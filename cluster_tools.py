from app import mcp
import numpy as np

# --- Smart Import: Try to get GPU, fall back to CPU ---
try:
    import cuml
    import cupy as cp
    GPU_ENABLED = True
    print("✅ GPU (cuML, cuPy) found. Clustering will be accelerated.")
except ImportError:
    # If GPU fails, import the CPU versions
    from hdbscan import HDBSCAN as CPU_HDBSCAN
    from sklearn.cluster import DBSCAN as CPU_DBSCAN
    GPU_ENABLED = False
    print("⚠️ GPU (cuML) not found. Falling back to CPU (HDBSCAN/DBSCAN).")
# ---

@mcp.tool
def cluster_points(points: np.ndarray, method: str, eps: float = 0.5, min_cluster_size: int = 50) -> np.ndarray:
    """
    Performs density-based clustering on [X, Y] points.
    AUTOMATICALLY uses GPU (cuML) if available, otherwise falls back to CPU. 
    
    :param points: [N, 3] or [N, 2] NumPy array of points.
    :param method: The algorithm to use. 'hdbscan' or 'dbscan'.
    :param eps: (DBSCAN only) The max distance between points.
    :param min_cluster_size: (HDBSCAN/DBSCAN) Min points to form a cluster.
    :return: NumPy array of cluster labels. -1 is noise.
    """
    # We only cluster on 2D (XY) for FKB objects
    points_2d = points[:, :2]

    if GPU_ENABLED:
        print(f"Clustering {len(points_2d)} points on GPU...")
        # Move data to GPU memory
        points_gpu = cp.asarray(points_2d)
        
        if method == 'hdbscan':
            clusterer = cuml.HDBSCAN(min_cluster_size=min_cluster_size)
        else: # dbscan
            clusterer = cuml.DBSCAN(eps=eps, min_samples=min_cluster_size)
        
        # Run on GPU
        labels_gpu = clusterer.fit_predict(points_gpu)
        
        # Return data to CPU memory
        return cp.asnumpy(labels_gpu)
        
    else:
        print(f"Clustering {len(points_2d)} points on CPU...")
        if method == 'hdbscan':
            clusterer = CPU_HDBSCAN(min_cluster_size=min_cluster_size, core_dist_n_jobs=-1) # Use all CPU cores
        else: # dbscan
            clusterer = CPU_DBSCAN(eps=eps, min_samples=min_cluster_size, n_jobs=-1) # Use all CPU cores
            
        # Run on CPU
        labels_cpu = clusterer.fit_predict(points_2d)
        return labels_cpu
    
@mcp.tool
def ground_segmentation_ransac(points: np.ndarray, distance_threshold: float = 0.1, num_iterations: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """
    Separates ground vs non-ground using RANSAC plane fitting.
    Assumes the largest plane found is the ground.

    :param points: [N, 3] NumPy array.
    :param distance_threshold: Max distance a point can be from the plane to be an inlier.
    :param num_iterations: Number of RANSAC iterations.
    :return: Tuple: (ground_points, non_ground_points)
    """
    if len(points) < 3:
        return np.array([]), points # Not enough points

    best_inliers_idx = []
    
    # RANSAC implementation (simplified from geo_tools version)
    for _ in range(num_iterations):
        # Sample 3 points
        sample_idx = np.random.choice(len(points), 3, replace=False)
        sample = points[sample_idx]

        # Compute plane normal
        v1 = sample[1] - sample[0]
        v2 = sample[2] - sample[0]
        normal = np.cross(v1, v2)
        norm_mag = np.linalg.norm(normal)
        if norm_mag < 1e-6: continue # Avoid degenerate plane
        normal /= norm_mag

        # Plane equation: ax + by + cz + d = 0 => normal . (x - p0) = 0
        d = -normal.dot(sample[0])

        # Calculate distances of all points to the plane
        distances = np.abs(points.dot(normal) + d)

        # Find inliers within the threshold
        inliers_idx = np.where(distances <= distance_threshold)[0]

        # Keep track of the largest set of inliers found
        if len(inliers_idx) > len(best_inliers_idx):
            best_inliers_idx = inliers_idx

    if len(best_inliers_idx) == 0:
        print("Warning: RANSAC failed to find a ground plane.")
        return np.array([]), points # Return all as non-ground

    # Create mask
    ground_mask = np.zeros(len(points), dtype=bool)
    ground_mask[best_inliers_idx] = True

    print(f"Ground segmentation complete. Ground points: {len(best_inliers_idx)}")
    return points[ground_mask], points[~ground_mask]