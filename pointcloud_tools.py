"""
MCP tool wrappers for advanced point cloud processing modules.
Exposes class-based functionality as MCP tools.
"""

from app import mcp
import numpy as np
from typing import Optional, List
import tempfile
import os


@mcp.tool
def load_and_filter_pointcloud(
    las_path: str,
    classification_codes: Optional[List[int]] = None,
    compute_features: bool = False
) -> dict:
    """
    Load a LAS/LAZ file and optionally filter by classification.

    Args:
        las_path: Path to LAS or LAZ file
        classification_codes: Optional list of LAS classification codes to filter
                            (e.g., [2]=ground, [6]=building, [9]=water)
        compute_features: Whether to compute local geometric features (linearity, planarity)

    Returns:
        Dictionary with 'points' (list of [x,y,z]), 'n_points', and optional 'features'
    """
    from pointcloud_core import PointCloudProcessor

    processor = PointCloudProcessor(las_path)
    processor.load()

    if classification_codes:
        points = processor.filter_by_classification(classification_codes)
    else:
        points = processor.points

    result = {
        'points': points.tolist(),
        'n_points': len(points),
        'path': las_path
    }

    if compute_features:
        features = processor.compute_local_features(k=20)
        result['features'] = {
            'linearity': features['linearity'].tolist(),
            'planarity': features['planarity'].tolist(),
            'scattering': features['scattering'].tolist(),
            'mean_linearity': float(features['linearity'].mean()),
            'mean_planarity': float(features['planarity'].mean())
        }

    return result


@mcp.tool
def cluster_pointcloud_advanced(
    points: List[List[float]],
    method: str = 'hdbscan',
    min_cluster_size: int = 50,
    min_samples: Optional[int] = None,
    eps: float = 0.5,
    extract_clusters: bool = True
) -> dict:
    """
    Advanced clustering with HDBSCAN or DBSCAN using the PointCloudClusterer class.

    Args:
        points: List of [X, Y, Z] or [X, Y] points
        method: 'hdbscan' or 'dbscan'
        min_cluster_size: Minimum points for a valid cluster
        min_samples: Neighborhood size (auto-calculated if None)
        eps: DBSCAN epsilon parameter (ignored for HDBSCAN)
        extract_clusters: Return detailed cluster information

    Returns:
        Dictionary with labels, statistics, and optionally cluster details
    """
    from clustering import PointCloudClusterer

    points_array = np.array(points)
    clusterer = PointCloudClusterer(points_array)

    # Calculate min_samples if not provided
    if min_samples is None:
        min_samples = max(5, min_cluster_size // 10)

    # Perform clustering
    if method == 'hdbscan':
        labels = clusterer.cluster_hdbscan(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples
        )
    else:
        labels = clusterer.cluster_dbscan(
            eps=eps,
            min_samples=min_samples
        )

    # Get statistics
    stats = clusterer.get_cluster_stats()

    result = {
        'labels': labels.tolist(),
        'n_clusters': stats['n_clusters'],
        'n_noise': stats['n_noise'],
        'cluster_sizes': stats['cluster_sizes']
    }

    if 'mean_cluster_size' in stats:
        result['mean_cluster_size'] = float(stats['mean_cluster_size'])
        result['median_cluster_size'] = float(stats['median_cluster_size'])

    # Extract detailed cluster info
    if extract_clusters:
        clusters = clusterer.extract_clusters()
        result['clusters'] = [
            {
                'label': int(c['label']),
                'size': int(c['size']),
                'centroid': c['centroid'].tolist(),
                'points': c['points'].tolist()
            }
            for c in clusters
        ]

    return result


@mcp.tool
def fit_plane_ransac_advanced(
    points: List[List[float]],
    distance_threshold: float = 0.02,
    num_iterations: int = 1000,
    refine_with_least_squares: bool = True
) -> dict:
    """
    Fit a plane to points using RANSAC with the RANSACFitter class.

    Args:
        points: List of [X, Y, Z] points
        distance_threshold: Maximum distance for inlier (meters)
                          FKB-A: 0.01-0.02, FKB-B: 0.02-0.04, FKB-C: 0.05-0.10
        num_iterations: Number of RANSAC iterations
        refine_with_least_squares: Refine plane using least squares on inliers

    Returns:
        Dictionary with plane model [a,b,c,d], inlier points, and residual statistics
    """
    from ransac_fitting import RANSACFitter

    points_array = np.array(points)
    fitter = RANSACFitter(points_array)

    plane_model, inlier_indices = fitter.fit_plane(
        distance_threshold=distance_threshold,
        ransac_n=3,
        num_iterations=num_iterations
    )

    # Optionally refine
    if refine_with_least_squares:
        plane_model = fitter.refine_plane_least_squares(inlier_indices)

    # Compute residuals
    residuals = fitter.compute_plane_residuals(plane_model)
    inlier_residuals = residuals[inlier_indices]

    inlier_points = points_array[inlier_indices]

    return {
        'plane_model': plane_model.tolist(),
        'equation': f"{plane_model[0]:.4f}x + {plane_model[1]:.4f}y + {plane_model[2]:.4f}z + {plane_model[3]:.4f} = 0",
        'inlier_points': inlier_points.tolist(),
        'inlier_indices': inlier_indices.tolist(),
        'n_inliers': int(len(inlier_indices)),
        'inlier_percentage': float(len(inlier_indices) / len(points_array) * 100),
        'rmse': float(np.sqrt(np.mean(inlier_residuals**2))),
        'max_residual': float(inlier_residuals.max()),
        'mean_residual': float(inlier_residuals.mean())
    }


@mcp.tool
def detect_multiple_planes(
    points: List[List[float]],
    max_planes: int = 5,
    distance_threshold: float = 0.02,
    min_inliers: int = 100,
    fkb_standard: Optional[str] = None
) -> dict:
    """
    Detect multiple planes sequentially (useful for building roofs).

    Args:
        points: List of [X, Y, Z] points
        max_planes: Maximum number of planes to detect
        distance_threshold: Inlier distance threshold (overridden if fkb_standard is set)
        min_inliers: Minimum inliers to accept a plane
        fkb_standard: FKB standard ('A', 'B', 'C', 'D') - auto-sets threshold

    Returns:
        Dictionary with list of detected planes
    """
    from ransac_fitting import extract_building_planes

    points_array = np.array(points)

    if fkb_standard:
        planes = extract_building_planes(points_array, fkb_standard=fkb_standard)
    else:
        from ransac_fitting import RANSACFitter
        fitter = RANSACFitter(points_array)
        planes = fitter.fit_multiple_planes(
            max_planes=max_planes,
            distance_threshold=distance_threshold,
            min_inliers=min_inliers
        )

    return {
        'n_planes': len(planes),
        'planes': [
            {
                'model': p['model'].tolist(),
                'equation': f"{p['model'][0]:.4f}x + {p['model'][1]:.4f}y + {p['model'][2]:.4f}z + {p['model'][3]:.4f} = 0",
                'inliers': p['inliers'].tolist(),
                'n_inliers': p['n_inliers']
            }
            for p in planes
        ]
    }


@mcp.tool
def extract_building_footprint_advanced(
    building_points: List[List[float]],
    fkb_standard: str = 'B',
    alpha: Optional[float] = None,
    simplify: bool = True,
    regularize: bool = True
) -> dict:
    """
    Extract building footprint using alpha shapes with advanced options.

    Args:
        building_points: List of [X, Y, Z] building points
        fkb_standard: FKB standard ('A', 'B', 'C', 'D') - affects simplification
        alpha: Alpha parameter (auto-calculated if None)
        simplify: Apply Douglas-Peucker simplification
        regularize: Regularize edges to dominant orientations

    Returns:
        GeoJSON-like dict with polygon geometry and metadata
    """
    from geometric_extraction import extract_building_footprint

    points_array = np.array(building_points)

    footprint = extract_building_footprint(
        points_array,
        fkb_standard=fkb_standard,
        simplify=simplify
    )

    return {
        'type': 'Polygon',
        'coordinates': [list(footprint.exterior.coords)],
        'area': float(footprint.area),
        'perimeter': float(footprint.length),
        'bounds': footprint.bounds,
        'n_vertices': len(footprint.exterior.coords) - 1,
        'fkb_standard': fkb_standard
    }


@mcp.tool
def compute_alpha_shape(
    points: List[List[float]],
    alpha: Optional[float] = None,
    optimize_alpha: bool = True
) -> dict:
    """
    Compute alpha shape (concave hull) of 2D points.

    Args:
        points: List of [X, Y] or [X, Y, Z] points (Z ignored)
        alpha: Alpha parameter (None for auto-optimization)
        optimize_alpha: Automatically find optimal alpha

    Returns:
        GeoJSON-like dict with polygon geometry
    """
    from geometric_extraction import BoundaryExtractor

    points_array = np.array(points)
    points_2d = points_array[:, :2]

    extractor = BoundaryExtractor(points_2d)
    polygon = extractor.compute_alpha_shape(alpha=alpha, optimize_alpha=optimize_alpha)

    return {
        'type': 'Polygon',
        'coordinates': [list(polygon.exterior.coords)],
        'area': float(polygon.area),
        'perimeter': float(polygon.length),
        'n_vertices': len(polygon.exterior.coords) - 1
    }


@mcp.tool
def fit_spline_to_points(
    points: List[List[float]],
    smoothing: Optional[float] = None,
    degree: int = 3,
    num_samples: int = 100
) -> dict:
    """
    Fit a smooth B-spline curve to ordered points.

    Args:
        points: List of ordered [X, Y] or [X, Y, Z] points
        smoothing: Smoothing factor (None=auto, 0=interpolation, higher=smoother)
        degree: Spline degree (1=linear, 3=cubic)
        num_samples: Number of points in output curve

    Returns:
        Dictionary with smoothed curve points
    """
    from geometric_extraction import SplineFitter

    points_array = np.array(points)
    fitter = SplineFitter(points_array)

    smooth_curve = fitter.fit_parametric_spline(
        smoothing=smoothing,
        degree=degree,
        num_samples=num_samples
    )

    return {
        'type': 'LineString',
        'coordinates': smooth_curve.tolist(),
        'n_points': len(smooth_curve),
        'degree': degree,
        'smoothing': smoothing if smoothing else 'auto'
    }


@mcp.tool
def segment_buildings_from_ground_advanced(
    points: List[List[float]],
    ground_height: float,
    height_threshold: float = 2.0,
    min_cluster_size: int = 100,
    clustering_method: str = 'auto'
) -> dict:
    """
    Segment buildings from pointcloud above ground level.

    Args:
        points: List of [X, Y, Z] points
        ground_height: Estimated ground elevation (meters)
        height_threshold: Minimum height above ground for buildings (meters)
        min_cluster_size: Minimum points for valid building cluster
        clustering_method: 'auto', 'hdbscan', or 'dbscan'

    Returns:
        Dictionary with building clusters and non-building points
    """
    from clustering import segment_buildings_from_ground

    points_array = np.array(points)

    buildings, labels = segment_buildings_from_ground(
        points_array,
        ground_height=ground_height,
        height_threshold=height_threshold,
        min_cluster_size=min_cluster_size
    )

    return {
        'n_buildings': len(buildings),
        'buildings': [
            {
                'label': int(b['label']),
                'size': int(b['size']),
                'centroid_2d': b['centroid'].tolist(),
                'points_3d': b['points_3d'].tolist(),
                'height_range': [
                    float(b['points_3d'][:, 2].min()),
                    float(b['points_3d'][:, 2].max())
                ]
            }
            for b in buildings
        ],
        'labels': labels.tolist()
    }


@mcp.tool
def estimate_point_cloud_spacing(points: List[List[float]]) -> dict:
    """
    Estimate average point spacing in a point cloud.
    Useful for setting parameters like alpha or eps.

    Args:
        points: List of [X, Y] or [X, Y, Z] points

    Returns:
        Dictionary with spacing statistics
    """
    from geometric_extraction import BoundaryExtractor

    points_array = np.array(points)
    points_2d = points_array[:, :2]

    extractor = BoundaryExtractor(points_2d)
    avg_spacing = extractor.estimate_point_spacing()

    return {
        'average_spacing': float(avg_spacing),
        'suggested_alpha_tight': float(avg_spacing * 1.5),
        'suggested_alpha_moderate': float(avg_spacing * 3.0),
        'suggested_alpha_loose': float(avg_spacing * 5.0),
        'suggested_dbscan_eps': float(avg_spacing * 1.5),
        'n_points': len(points_array)
    }


@mcp.tool
def check_gpu_availability() -> dict:
    """
    Check if GPU acceleration (CuPy/cuML) is available.

    Returns:
        Dictionary with GPU availability status and info
    """
    from gpu_utils import GPU_AVAILABLE

    result = {
        'gpu_available': GPU_AVAILABLE,
        'backend': 'GPU (CuPy/cuML)' if GPU_AVAILABLE else 'CPU'
    }

    if GPU_AVAILABLE:
        import cupy as cp
        result['gpu_info'] = {
            'device_count': cp.cuda.runtime.getDeviceCount(),
            'device_name': cp.cuda.runtime.getDeviceProperties(0)['name'].decode()
        }
    else:
        result['message'] = 'GPU libraries not available. Install with: conda install -c rapidsai cuml cupy'

    return result
