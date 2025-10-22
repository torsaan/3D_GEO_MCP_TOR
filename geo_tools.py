from app import mcp
import numpy as np
import alphashape
from shapely.geometry import Polygon, LineString
from scipy.interpolate import griddata, splprep, splev
import matplotlib.pyplot as plt
import math
from typing import Optional
from scipy.spatial import KDTree



# --- Helper function for Building Regularization ---
def _regularize_building(polygon: Polygon, angle_tolerance_deg: float = 10.0) -> Polygon:
    """
    Attempts to regularize a building footprint by snapping near-orthogonal
    angles to 90 degrees. Simple implementation.
    """
    coords = list(polygon.exterior.coords)
    if len(coords) < 4:
        return polygon # Need at least a triangle

    new_coords = [coords[0]] # Start with the first point

    for i in range(1, len(coords) - 1):
        p_prev = coords[i-1]
        p_curr = coords[i]
        p_next = coords[i+1]

        vec1 = (p_curr[0] - p_prev[0], p_curr[1] - p_prev[1])
        vec2 = (p_next[0] - p_curr[0], p_next[1] - p_curr[1])

        angle1 = math.atan2(vec1[1], vec1[0])
        angle2 = math.atan2(vec2[1], vec2[0])

        # Angle between the two segments (in degrees)
        angle_diff = math.degrees(angle2 - angle1)
        angle_diff = (angle_diff + 180) % 360 - 180 # Normalize to [-180, 180]

        snapped = False
        # Check if angle is close to 0, 90, 180, -90 degrees
        for target_angle in [0, 90, 180, -90]:
            if abs(angle_diff - target_angle) < angle_tolerance_deg:
                # Simple snap: Adjust p_next based on p_curr and vec1 direction
                # This is a basic approximation. Real regularization is complex.
                # For simplicity, we just keep the original point for now.
                # A full implementation would involve rotating vec2 or adjusting p_next.
                snapped = True
                break

        # For this simplified version, we just add the current point.
        # A more complex version would adjust p_curr's position.
        new_coords.append(p_curr)

    new_coords.append(coords[-1]) # Add the last point (same as first)

    # Try creating a polygon from potentially simplified coords
    try:
        regularized_poly = Polygon(new_coords)
        if regularized_poly.is_valid:
            return regularized_poly
    except Exception:
        pass # If regularization failed, return original

    return polygon
# --- End Helper ---

@mcp.tool
def extract_building_footprint(building_points: list[list[float]], alpha: Optional[float] = None) -> Optional[dict]:
    """
    Extracts a 2D building footprint polygon from a cluster of building points
    using alpha shapes.
    
    :param building_points: List of [X, Y, Z] points for one building (nested list of floats).
    :param alpha: The alpha value. If None, alphashape will auto-optimize.
    :return: A GeoJSON-like dict representing the polygon, or None if invalid.
    """
    # Convert list to NumPy array
    building_points_array = np.array(building_points)
    
    if len(building_points_array) < 3:
        return None
        
    # Project to 2D
    xy_points = building_points_array[:, :2]
    
    # Compute alpha shape
    polygon = alphashape.alphashape(xy_points, alpha)
    
    if not polygon.is_valid or polygon.is_empty:
        return None
        
    # TODO: Add logic from _regularize_building here
    
    # Return GeoJSON-like dict
    return {
        "type": "Polygon",
        "coordinates": [list(polygon.exterior.coords)]
    }

@mcp.tool
def generate_contours(ground_points: list[list[float]], interval: float = 1.0) -> list[dict]:
    """
    Generates contour lines (Høydekurve) from ground points.
    
    :param ground_points: List of [X, Y, Z] ground points (nested list of floats).
    :param interval: The contour interval in meters.
    :return: A list of GeoJSON-like LineString dicts.
    """
    # Convert list to NumPy array
    ground_points_array = np.array(ground_points)
    x, y, z = ground_points_array[:, 0], ground_points_array[:, 1], ground_points_array[:, 2]
    
    # Create a grid to interpolate onto
    grid_x = np.linspace(x.min(), x.max(), 500)
    grid_y = np.linspace(y.min(), y.max(), 500)
    grid_x, grid_y = np.meshgrid(grid_x, grid_y)
    
    # Interpolate Z values onto the grid
    grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
    
    # Generate contours using matplotlib
    contours = plt.contour(grid_x, grid_y, grid_z, 
                           levels=np.arange(z.min(), z.max(), interval))
    
    # Convert contour paths to GeoJSON-like dicts
    lines = []
    for collection in contours.collections:
        for path in collection.get_paths():
            if len(path.vertices) > 1:
                lines.append({
                    "type": "LineString",
                    "coordinates": path.vertices.tolist()
                })
                
    plt.close() # Close the plot to save memory
    return lines


@mcp.tool
def smooth_line_bspline(points: list[list[float]], smoothing: float = 0.5) -> list[list[float]]:
    """Smooths a 2D/3D line using a B-spline.
    
    :param points: List of [X, Y, Z] points (nested list of floats).
    :param smoothing: The smoothing factor.
    :return: List of smoothed [X, Y, Z] points.
    """
    points_array = np.array(points)
    tck, u = splprep([points_array[:, 0], points_array[:, 1], points_array[:, 2]], s=smoothing, k=3)
    u_new = np.linspace(u.min(), u.max(), len(points_array))
    x_new, y_new, z_new = splev(u_new, tck)
    return np.vstack([x_new, y_new, z_new]).T.tolist()

@mcp.tool
def simplify_line_douglas_peucker(line_points: list[list[float]], tolerance: float) -> list[list[float]]:
    """
    Simplifies a 3D line using the Douglas-Peucker algorithm.
    This reduces the number of vertices while preserving the shape.

    :param line_points: List of ORDERED [X, Y, Z] points (nested list of floats).
    :param tolerance: The simplification distance in meters.
    :return: A new, simplified list of [X, Y, Z] points.
    """
    # Convert to NumPy array
    line_points_array = np.array(line_points)
    
    if len(line_points_array) < 2:
        return line_points
        
    line = LineString(line_points_array)
    # preserve_topology=True is important!
    simplified_line = line.simplify(tolerance, preserve_topology=True)
    
    return np.array(simplified_line.coords).tolist()


@mcp.tool
def ransac_plane_detection(points: list[list[float]], threshold: float = 0.01, iterations: int = 1000) -> dict:
    """
    Detects plane in 3D points using RANSAC.
    
    :param points: List of [X, Y, Z] points (nested list of floats).
    :param threshold: Inlier distance threshold.
    :param iterations: Max RANSAC iterations.
    :return: Dict with 'inliers' and 'outliers' as lists of points.
    """
    points_array = np.array(points)
    best_inliers = []
    for _ in range(iterations):
        # Sample 3 points
        sample_idx = np.random.choice(len(points_array), 3, replace=False)
        sample = points_array[sample_idx]
        
        # Compute plane: ax + by + cz = d
        v1 = sample[1] - sample[0]
        v2 = sample[2] - sample[0]
        normal = np.cross(v1, v2)
        normal /= np.linalg.norm(normal)
        d = -normal.dot(sample[0])
        
        # Inliers
        dist = np.abs(points_array.dot(normal) + d) / np.linalg.norm(normal)
        inliers = np.where(dist <= threshold)[0]
        
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
    
    outliers_idx = np.setdiff1d(np.arange(len(points_array)), best_inliers)
    
    return {
        "inliers": points_array[best_inliers].tolist(),
        "outliers": points_array[outliers_idx].tolist()
    }


# --- NEW TOOL: Detect Linear Feature Points ---
@mcp.tool
def detect_linear_points(points: list[list[float]], classification: list[int], target_class: int, neighbor_radius: float = 0.5, min_linearity: float = 0.7) -> list[list[float]]:
    """
    Detects points belonging to linear features (like curbs, road edges)
    based on local neighborhood analysis (e.g., linearity). Requires classified points.

    :param points: List of [X, Y, Z] points (nested list of floats).
    :param classification: List of class labels for each point (list of ints).
    :param target_class: The integer class label for the linear feature (e.g., 6 for curb).
    :param neighbor_radius: Radius to search for neighbors.
    :param min_linearity: Minimum PCA linearity score (0=plane, 1=perfect line) to keep a point.
    :return: List of points belonging to the linear feature.
    """
    points_array = np.array(points)
    classification_array = np.array(classification)
    
    feature_points = points_array[classification_array == target_class]
    if len(feature_points) == 0:
        return []

    tree = KDTree(feature_points[:, :2]) # Use 2D for neighborhood search
    indices_list = tree.query_ball_point(feature_points[:, :2], r=neighbor_radius)

    linear_mask = np.zeros(len(feature_points), dtype=bool)

    for i, neighbors_idx in enumerate(indices_list):
        if len(neighbors_idx) < 5: # Need enough points for PCA
            continue

        local_points = feature_points[neighbors_idx]
        
        # PCA on local neighborhood
        centered_points = local_points - np.mean(local_points, axis=0)
        cov_matrix = np.cov(centered_points.T)
        eigenvalues, _ = np.linalg.eigh(cov_matrix)
        
        # Sort eigenvalues (smallest to largest for 3D)
        eigenvalues = np.sort(eigenvalues) 
        
        # Linearity score = (lambda1 - lambda2) / lambda1 
        # lambda1 is the largest eigenvalue (along the line)
        # lambda2 is the second largest (width)
        # lambda3 is the smallest (thickness)
        if eigenvalues[2] > 1e-6: # Avoid division by zero
            linearity = (eigenvalues[2] - eigenvalues[1]) / eigenvalues[2]
            if linearity >= min_linearity:
                linear_mask[i] = True

    print(f"Detected {np.sum(linear_mask)} linear points for class {target_class}")
    return feature_points[linear_mask].tolist()