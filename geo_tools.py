from app import mcp
import numpy as np
import alphashape
from shapely.geometry import Polygon, LineString
from scipy.interpolate import griddata,splprep, splev
import matplotlib.pyplot as plt
from app import mcp
import numpy as np
import alphashape
from shapely.geometry import Polygon, LineString
from scipy.interpolate import griddata, splprep, splev # <-- Add splprep, splev
import matplotlib.pyplot as plt
import math



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
def extract_building_footprint(building_points: np.ndarray, alpha: float = None) -> (Polygon | None):
    """
    Extracts a 2D building footprint polygon from a cluster of building points
    using alpha shapes.
    
    :param building_points: NumPy array of [X, Y, Z] points for one building.
    :param alpha: The alpha value. If None, alphashape will auto-optimize.
    :return: A Shapely Polygon object, or None if invalid.
    """
    if len(building_points) < 3:
        return None
        
    # Project to 2D
    xy_points = building_points[:, :2]
    
    # Compute alpha shape
    polygon = alphashape.alphashape(xy_points, alpha)
    
    if not polygon.is_valid or polygon.is_empty:
        return None
        
    # TODO: Add logic from _regularize_building here
    
    return polygon

@mcp.tool
def generate_contours(ground_points: np.ndarray, interval: float = 1.0) -> list[LineString]:
    """
    Generates contour lines (Høydekurve) from ground points.
    
    :param ground_points: NumPy array of [X, Y, Z] ground points.
    :param interval: The contour interval in meters.
    :return: A list of Shapely LineString objects.
    """
    x, y, z = ground_points[:, 0], ground_points[:, 1], ground_points[:, 2]
    
    # Create a grid to interpolate onto
    grid_x = np.linspace(x.min(), x.max(), 500)
    grid_y = np.linspace(y.min(), y.max(), 500)
    grid_x, grid_y = np.meshgrid(grid_x, grid_y)
    
    # Interpolate Z values onto the grid
    grid_z = griddata((x, y), z, (grid_x, grid_y), method='linear')
    
    # Generate contours using matplotlib
    contours = plt.contour(grid_x, grid_y, grid_z, 
                           levels=np.arange(z.min(), z.max(), interval))
    
    # Convert contour paths to LineStrings
    lines = []
    for collection in contours.collections:
        for path in collection.get_paths():
            if len(path.vertices) > 1:
                lines.append(LineString(path.vertices))
                
    plt.close() # Close the plot to save memory
    return lines


@mcp.tool
def smooth_line_bspline(points: np.ndarray, smoothing: float = 0.5) -> np.ndarray:
    """Smooths a 2D/3D line using a B-spline."""
    tck, u = splprep([points[:, 0], points[:, 1], points[:, 2]], s=smoothing, k=3)
    u_new = np.linspace(u.min(), u.max(), len(points))
    x_new, y_new, z_new = splev(u_new, tck)
    return np.vstack([x_new, y_new, z_new]).T

@mcp.tool
def simplify_line_douglas_peucker(line_points: np.ndarray, tolerance: float) -> np.ndarray:
    """
    Simplifies a 3D line using the Douglas-Peucker algorithm.
    This reduces the number of vertices while preserving the shape.

    :param line_points: NumPy array of ORDERED [X, Y, Z] points.
    :param tolerance: The simplification distance in meters.
    :return: A new, simplified NumPy array of [X, Y, Z] points.
    """
    if len(line_points) < 2:
        return line_points
        
    line = LineString(line_points)
    # preserve_topology=True is important!
    simplified_line = line.simplify(tolerance, preserve_topology=True)
    
    return np.array(simplified_line.coords)


@mcp.tool
def smooth_line_bspline(line_points: np.ndarray, num_points: int, smoothing: float = 0.5) -> np.ndarray:
    """
    Smooths a jagged 3D line into a B-spline curve.
    This is excellent for creating clean, aesthetic contour lines. [cite: 3]

    :param line_points: NumPy array of ORDERED [X, Y, Z] points.
    :param num_points: How many points the final smooth line should have.
    :param smoothing: The smoothing factor. 0 = interpolates (passes through all points), > 0 = smoother.
    :return: A new, smooth NumPy array of [X, Y, Z] points.
    """
    if len(line_points) < 4: # splprep needs at least k+1 points (k=3 default)
        return line_points
        
    # Unpack the 3D points
    x, y, z = line_points.T
    
    # Find the B-spline representation
    tck, u = splprep([x, y, z], s=smoothing, k=3)
    
    # Evaluate the spline at 'num_points' new, evenly-spaced points
    u_new = np.linspace(u.min(), u.max(), num_points)
    x_new, y_new, z_new = splev(u_new, tck)
    
    # Re-pack into an [N, 3] array
    return np.column_stack([x_new, y_new, z_new])

@mcp.tool
def ransac_plane_detection(points: np.ndarray, threshold: float = 0.01, iterations: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """
    Detects plane in 3D points using RANSAC.
    
    :param points: [N, 3] NumPy array.
    :param threshold: Inlier distance threshold.
    :param iterations: Max RANSAC iterations.
    :return: (inliers, outliers)
    """
    best_inliers = []
    for _ in range(iterations):
        # Sample 3 points
        sample_idx = np.random.choice(len(points), 3, replace=False)
        sample = points[sample_idx]
        
        # Compute plane: ax + by + cz = d
        v1 = sample[1] - sample[0]
        v2 = sample[2] - sample[0]
        normal = np.cross(v1, v2)
        normal /= np.linalg.norm(normal)
        d = -normal.dot(sample[0])
        
        # Inliers
        dist = np.abs(points.dot(normal) + d) / np.linalg.norm(normal)
        inliers = np.where(dist <= threshold)[0]
        
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
    
    return points[best_inliers], points[np.setdiff1d(np.arange(len(points)), best_inliers)]


# --- NEW TOOL: Detect Linear Feature Points ---
@mcp.tool
def detect_linear_points(points: np.ndarray, classification: np.ndarray, target_class: int, neighbor_radius: float = 0.5, min_linearity: float = 0.7) -> np.ndarray:
    """
    Detects points belonging to linear features (like curbs, road edges)
    based on local neighborhood analysis (e.g., linearity). Requires classified points.

    :param points: [N, 3] NumPy array of points.
    :param classification: [N] NumPy array of class labels for each point.
    :param target_class: The integer class label for the linear feature (e.g., 6 for curb).
    :param neighbor_radius: Radius to search for neighbors.
    :param min_linearity: Minimum PCA linearity score (0=plane, 1=perfect line) to keep a point.
    :return: NumPy array of points belonging to the linear feature.
    """
    feature_points = points[classification == target_class]
    if len(feature_points) == 0:
        return np.array([])

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
    return feature_points[linear_mask]