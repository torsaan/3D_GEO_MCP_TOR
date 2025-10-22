from app import mcp
import networkx as nx
import numpy as np
from shapely.geometry import Point, LineString, MultiPoint
from shapely.ops import split as shapely_split
from scipy.spatial import KDTree
from collections import defaultdict



@mcp.tool
def build_road_network(road_segments: list[dict]) -> dict:
    """Builds a NetworkX graph from a list of LineString segments.
    
    :param road_segments: List of GeoJSON-like LineString dicts.
    :return: Serialized graph data (not actual NetworkX object, since it's not JSON-serializable).
    """
    G = nx.Graph()
    for i, segment_dict in enumerate(road_segments):
        segment = LineString(segment_dict["coordinates"])
        coords = list(segment.coords)
        for j in range(len(coords) - 1):
            p1 = coords[j]
            p2 = coords[j+1]
            G.add_edge(p1, p2, segment_id=i, length=Point(p1).distance(Point(p2)))
    
    # Return serialized representation
    return {
        "nodes": list(G.nodes()),
        "edges": [(u, v, data) for u, v, data in G.edges(data=True)],
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges()
    }

@mcp.tool
def order_points_mst(points: list[list[float]], k_neighbors: int = 8) -> list[list[float]]:
    """
    Takes an UNORDERED cluster of 3D points and sorts them into a
    single, ordered line by finding the longest path in a
    Minimum Spanning Tree (MST).

    :param points: List of [X, Y, Z] points (nested list of floats).
    :param k_neighbors: How many neighbors to connect in the initial graph.
    :return: A new list of [X, Y, Z] points, now in order.
    """
    # Convert to NumPy array
    points_array = np.array(points)
    
    if len(points_array) < 3:
        return points # Not enough points to sort

    print(f"Ordering {len(points_array)} points using MST...")
    
    # 1. Build a k-NN graph in 2D (XY)
    # [cite: 3]
    tree_2d = KDTree(points_array[:, :2])
    distances, indices = tree_2d.query(points_array[:, :2], k=k_neighbors)
    
    G = nx.Graph()
    for i in range(len(points_array)):
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
    return points_array[path_indices].tolist()
@mcp.tool
def snap_endpoints(lines: list[dict], tolerance: float) -> list[dict]:
    """
    Snaps line endpoints within tolerance to create clean nodes (full implementation).
    
    :param lines: List of GeoJSON-like LineString dicts.
    :param tolerance: Snapping distance in meters.
    :return: List of snapped LineString dicts.
    """
    # Convert GeoJSON dicts to Shapely objects
    shapely_lines = [LineString(line["coordinates"]) for line in lines]
    
    endpoints = []
    line_indices = []  # Track which line each endpoint belongs to
    for idx, line in enumerate(shapely_lines):
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
    new_lines = [list(line.coords) for line in shapely_lines]
    for ep_idx, (line_idx, pos) in enumerate(line_indices):
        if ep_idx in snap_map:
            snapped_xy = snap_map[ep_idx]
            orig_z = new_lines[line_idx][pos][2] if len(new_lines[line_idx][pos]) > 2 else 0
            new_lines[line_idx][pos] = (snapped_xy[0], snapped_xy[1], orig_z)
    
    # Convert back to GeoJSON dicts
    return [{"type": "LineString", "coordinates": coords} for coords in new_lines]

@mcp.tool
def detect_t_junctions(graph_data: dict) -> list[dict]:
    """
    Detects T-junctions in the road graph.
    
    :param graph_data: Serialized graph data from build_road_network.
    :return: List of T-junction info dicts with node and neighbors.
    """
    # Reconstruct NetworkX graph from serialized data
    G = nx.Graph()
    for u, v, data in graph_data["edges"]:
        G.add_edge(u, v, **data)
    
    junctions = []
    for node in G.nodes():
        if G.degree(node) == 3:
            # Simple angle check (could use vectors for precision)
            neighbors = list(G.neighbors(node))
            junctions.append({"node": node, "neighbors": neighbors})
    
    return junctions


# --- NEW TOOL: Split Lines at Junctions ---
@mcp.tool
def split_lines_at_junctions(lines: list[dict], tolerance: float = 0.01) -> list[dict]:
    """
    Splits LineStrings at intersection points (junctions) to ensure
    correct FKB topology where lines meet at nodes.

    :param lines: List of snapped GeoJSON-like LineString dicts.
    :param tolerance: Tolerance for considering points identical.
    :return: A new list of potentially more, shorter LineString dicts.
    """
    # Convert GeoJSON dicts to Shapely objects
    shapely_lines = [LineString(line["coordinates"]) for line in lines]

    split_points = defaultdict(list) # point_tuple -> list of line indices intersecting here
    all_points = []

    # 1. Find all intersection points between lines
    for i in range(len(shapely_lines)):
        for j in range(i + 1, len(shapely_lines)):
            line1 = shapely_lines[i]
            line2 = shapely_lines[j]
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

    for i, line in enumerate(shapely_lines):
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


    print(f"Split lines at junctions. Input: {len(shapely_lines)}, Output: {len(new_segments)}")
    
    # Convert back to GeoJSON dicts
    return [{"type": "LineString", "coordinates": list(line.coords)} for line in new_segments]
# --- End New Tool ---