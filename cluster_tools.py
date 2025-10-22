from app import mcp
import numpy as np

# --- Smart Import: Try to get GPU, fall back to CPU ---
try:
    import cuml
    import cupy as cp
    GPU_ENABLED = True
    print("✅ GPU (cuML, cuPy) found. Clustering will be accelerated.")
except (ImportError, RuntimeError) as e:
    # If GPU fails (missing module or CUDA runtime), import the CPU versions
    GPU_ENABLED = False
    print(f"⚠️ GPU (cuML) not available: {e}. Falling back to CPU (HDBSCAN/DBSCAN).")

# Import CPU versions if GPU is not available
if not GPU_ENABLED:
    try:
        from hdbscan import HDBSCAN as CPU_HDBSCAN
        from sklearn.cluster import DBSCAN as CPU_DBSCAN
    except ImportError:
        print("❌ ERROR: Neither GPU (cuML) nor CPU (HDBSCAN/DBSCAN) libraries found!")
        print("   Please install: pip install hdbscan scikit-learn")
# ---

@mcp.tool
def cluster_points(points: list[list[float]], method: str, eps: float = 0.5, min_cluster_size: int = 50) -> list[int]:
    """
    Performs density-based clustering on [X, Y] points.
    AUTOMATICALLY uses GPU (cuML) if available, otherwise falls back to CPU. 
    
    :param points: List of [X, Y, Z] or [X, Y] points (nested list of floats).
    :param method: The algorithm to use. 'hdbscan' or 'dbscan'.
    :param eps: (DBSCAN only) The max distance between points.
    :param min_cluster_size: (HDBSCAN/DBSCAN) Min points to form a cluster.
    :return: List of cluster labels. -1 is noise.
    """
    # Convert to NumPy array
    points_array = np.array(points)
    
    # We only cluster on 2D (XY) for FKB objects
    points_2d = points_array[:, :2]

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
        
        # Return data to CPU memory as list
        return cp.asnumpy(labels_gpu).tolist()
        
    else:
        print(f"Clustering {len(points_2d)} points on CPU...")
        if method == 'hdbscan':
            clusterer = CPU_HDBSCAN(min_cluster_size=min_cluster_size, core_dist_n_jobs=-1) # Use all CPU cores
        else: # dbscan
            clusterer = CPU_DBSCAN(eps=eps, min_samples=min_cluster_size, n_jobs=-1) # Use all CPU cores
            
        # Run on CPU
        labels_cpu = clusterer.fit_predict(points_2d)
        return labels_cpu.tolist()
    
@mcp.tool
def ground_segmentation_ransac(points: list[list[float]], distance_threshold: float = 0.1, num_iterations: int = 1000) -> dict:
    """
    Separates ground vs non-ground using RANSAC plane fitting.
    Assumes the largest plane found is the ground.

    :param points: List of [X, Y, Z] points (nested list of floats).
    :param distance_threshold: Max distance a point can be from the plane to be an inlier.
    :param num_iterations: Number of RANSAC iterations.
    :return: Dict with 'ground' and 'non_ground' point lists.
    """
    # Convert to NumPy array
    points_array = np.array(points)
    
    if len(points_array) < 3:
        return {"ground": [], "non_ground": points} # Not enough points

    best_inliers_idx = []
    
    # RANSAC implementation (simplified from geo_tools version)
    for _ in range(num_iterations):
        # Sample 3 points
        sample_idx = np.random.choice(len(points_array), 3, replace=False)
        sample = points_array[sample_idx]

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
        distances = np.abs(points_array.dot(normal) + d)

        # Find inliers within the threshold
        inliers_idx = np.where(distances <= distance_threshold)[0]

        # Keep track of the largest set of inliers found
        if len(inliers_idx) > len(best_inliers_idx):
            best_inliers_idx = inliers_idx

    if len(best_inliers_idx) == 0:
        print("Warning: RANSAC failed to find a ground plane.")
        return {"ground": [], "non_ground": points} # Return all as non-ground

    # Create mask
    ground_mask = np.zeros(len(points_array), dtype=bool)
    ground_mask[best_inliers_idx] = True

    print(f"Ground segmentation complete. Ground points: {len(best_inliers_idx)}")
    return {
        "ground": points_array[ground_mask].tolist(),
        "non_ground": points_array[~ground_mask].tolist()
    }