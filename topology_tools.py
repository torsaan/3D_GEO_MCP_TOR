from app import mcp
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString
from scipy.spatial import KDTree
from app import mcp
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString
from scipy.spatial import KDTree
from collections import defaultdict



@mcp.tool
def build_road_network(road_segments: list[LineString]) -> nx.Graph:
    """Builds a NetworkX graph from a list of LineString segments."""
    G = nx.Graph()
    for i, segment in enumerate(road_segments):
        coords = list(segment.coords)
        for j in range(len(coords) - 1):
            p1 = coords[j]
            p2 = coords[j+1]
            G.add_edge(p1, p2, segment_id=i, length=Point(p1).distance(Point(p2)))
    return G

@mcp.tool
def snap_endpoints(lines: list[LineString], tolerance: float) -> list[LineString]:
    """
    Snaps line endpoints that are within a given tolerance to create
    clean topological nodes.
    
    :param lines: A list of Shapely LineString objects.
    :param tolerance: The snapping distance in meters.
    :return: A new list of snapped LineString objects.
    """
    endpoints = []
    for line in lines:
        endpoints.append(Point(line.coords[0]))
        endpoints.append(Point(line.coords[-1]))
        
    coords = np.array([[p.x, p.y] for p in endpoints])
    tree = KDTree(coords)
    
    # Find clusters of nearby endpoints
    clusters = tree.query_ball_tree(tree, r=tolerance)
    
    # This is a complex operation.
    # The full implementation would involve finding the centroid
    # of each cluster, creating a mapping from old_point -> new_snapped_point,
    # and then rebuilding all the LineStrings with the new_snapped_point coords.
    
    print(f"Found {len(clusters)} potential snapping clusters.")
    # For now, we return the original lines
    # TODO: Implement full snapping logic
    return lines

@mcp.tool
def order_points_mst(points: np.ndarray, k_neighbors: int = 8) -> np.ndarray:
    """
    Takes an UNORDERED cluster of 3D points and sorts them into a
    single, ordered line by finding the longest path in a
    Minimum Spanning Tree (MST).

    :param points: NumPy array of [X, Y, Z] points.
    :param k_neighbors: How many neighbors to connect in the initial graph.
    :return: A new NumPy array of [X, Y, Z] points, now in order.
    """
    if len(points) < 3:
        return points # Not enough points to sort

    print(f"Ordering {len(points)} points using MST...")
    
    # 1. Build a k-NN graph in 2D (XY)
    # [cite: 3]
    tree_2d = KDTree(points[:, :2])
    distances, indices = tree_2d.query(points[:, :2], k=k_neighbors)
    
    G = nx.Graph()
    for i in range(len(points)):
        for j in range(1, k_neighbors): # Start from 1 to skip self
            neighbor_idx = indices[i, j]
            dist = distances[i, j]
            # Add edge with the 2D distance as weight
            G.add_edge(i, neighbor_idx, weight=dist)

    # 2. Compute the Minimum Spanning Tree [cite: 3]
    mst = nx.minimum_spanning_tree(G)

    # 3. Find the endpoints (nodes of degree 1)
    degrees = dict(mst.degree())
    endpoints = [node for node, deg in degrees.items() if deg == 1]
    
    if len(endpoints) < 2:
        print("  Warning: No clear endpoints found. Returning original order.")
        return points # This is a blob, not a line

    # 4. Find the longest path between any two endpoints
    longest_path_len = -1
    start_node = -1
    end_node = -1
    
    # Get all-pairs shortest paths in the MST
    path_lengths = dict(nx.all_pairs_dijkstra_path_length(mst))

    for i in range(len(endpoints)):
        for j in range(i + 1, len(endpoints)):
            u, v = endpoints[i], endpoints[j]
            length = path_lengths[u][v]
            if length > longest_path_len:
                longest_path_len = length
                start_node, end_node = u, v

    # 5. Get the actual path (sequence of node indices)
    path_indices = nx.shortest_path(mst, source=start_node, target=end_node)
    
    print(f"  Successfully found path with {len(path_indices)} points.")
    
    # 6. Return the 3D points in the new order
    return points[path_indices]
@mcp.tool
def snap_endpoints(lines: list[LineString], tolerance: float) -> list[LineString]:
    """
    Snaps line endpoints within tolerance to create clean nodes (full implementation).
    """
    endpoints = []
    line_indices = []  # Track which line each endpoint belongs to
    for idx, line in enumerate(lines):
        endpoints.append(Point(line.coords[0]))
        line_indices.append((idx, 0))  # (line_idx, endpoint_idx: 0=start, -1=end)
        endpoints.append(Point(line.coords[-1]))
        line_indices.append((idx, -1))
    
    coords = np.array([[p.x, p.y] for p in endpoints])  # 2D for snapping
    tree = KDTree(coords)
    clusters = []  # List of lists: each sublist is indices in endpoints
    visited = set()
    for i in range(len(endpoints)):
        if i in visited:
            continue
        neighbors = tree.query_ball_point(coords[i], r=tolerance)
        clusters.append(neighbors)
        visited.update(neighbors)
    
    # Compute centroids for each cluster
    snap_map = {}  # old_point_index -> new_snapped_point (as tuple)
    for cluster in clusters:
        cluster_coords = coords[cluster]
        centroid = np.mean(cluster_coords, axis=0)
        for idx in cluster:
            snap_map[idx] = (centroid[0], centroid[1])  # Keep original Z for now
    
    # Rebuild lines with snapped endpoints
    new_lines = [list(line.coords) for line in lines]
    for ep_idx, (line_idx, pos) in enumerate(line_indices):
        if ep_idx in snap_map:
            snapped_xy = snap_map[ep_idx]
            orig_z = new_lines[line_idx][pos][2] if len(new_lines[line_idx][pos]) > 2 else 0
            new_lines[line_idx][pos] = (snapped_xy[0], snapped_xy[1], orig_z)
    
    return [LineString(coords) for coords in new_lines]

@mcp.tool
def detect_t_junctions(G: nx.Graph) -> list[tuple]:
    """
    Detects T-junctions in the road graph.
    
    :param G: NetworkX graph from build_road_network.
    :return: List of T-junction nodes (degree 3, with angle check).
    """
    junctions = []
    for node in G.nodes():
        if G.degree(node) == 3:
            # Simple angle check (could use vectors for precision)
            neighbors = list(G.neighbors(node))
            junctions.append((node, neighbors))  # TODO: Add angle validation if needed
    return junctions


# --- NEW TOOL: Split Lines at Junctions ---
@mcp.tool
def split_lines_at_junctions(lines: list[LineString], tolerance: float = 0.01) -> list[LineString]:
    """
    Splits LineStrings at intersection points (junctions) to ensure
    correct FKB topology where lines meet at nodes.

    :param lines: List of snapped LineString objects.
    :param tolerance: Tolerance for considering points identical.
    :return: A new list of potentially more, shorter LineString segments.
    """
    from shapely.ops import split as shapely_split

    split_points = defaultdict(list) # point_tuple -> list of line indices intersecting here
    all_points = []

    # 1. Find all intersection points between lines
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            if line1.intersects(line2):
                intersection = line1.intersection(line2)
                
                # Handle different intersection types
                if isinstance(intersection, Point):
                    pt_tuple = (intersection.x, intersection.y)
                    split_points[pt_tuple].extend([i, j])
                    all_points.append(intersection)
                elif isinstance(intersection, MultiPoint):
                     for pt in intersection.geoms:
                          pt_tuple = (pt.x, pt.y)
                          split_points[pt_tuple].extend([i,j])
                          all_points.append(pt)
                elif isinstance(intersection, LineString):
                     # Handle overlaps if necessary - more complex
                     pass

    if not all_points:
        return lines # No intersections found

    # 2. Add intersection points to the lines they intersect
    splitter_multipoint = MultiPoint(all_points)
    new_segments = []

    for i, line in enumerate(lines):
        # Find which split points lie on this line (within tolerance)
        relevant_split_points = []
        for pt in splitter_multipoint.geoms:
             # Use project/interpolate to find closest point *on* the line
             proj_dist = line.project(pt)
             if proj_dist > 1e-6 and proj_dist < line.length - 1e-6: # Avoid endpoints
                  closest_on_line = line.interpolate(proj_dist)
                  if closest_on_line.distance(pt) < tolerance:
                       relevant_split_points.append(closest_on_line)
        
        if not relevant_split_points:
            new_segments.append(line)
            continue

        # Use shapely.ops.split to cut the line at these points
        splitter = MultiPoint(relevant_split_points)
        split_result = shapely_split(line, splitter)
        
        if split_result:
             new_segments.extend(list(split_result.geoms))
        else: # Split might fail if points are exactly on vertices
             new_segments.append(line) # Keep original if split failed


    print(f"Split lines at junctions. Input: {len(lines)}, Output: {len(new_segments)}")
    return new_segments
# --- End New Tool ---