"""
Clustering algorithms for pointcloud segmentation.
HDBSCAN for density-based clustering, DBSCAN for fixed-epsilon clustering.
"""

import numpy as np
import hdbscan
from sklearn.cluster import DBSCAN
from scipy.spatial import KDTree
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PointCloudClusterer:
    """Clustering operations for pointcloud segmentation."""
    
    def __init__(self, points: np.ndarray):
        """
        Initialize with pointcloud.
        
        Args:
            points: numpy array of shape (N, 3) or (N, 2) for 2D
        """
        self.points = points
        self.n_points = len(points)
        self.labels = None
        self.probabilities = None
        
    def cluster_hdbscan(
        self,
        min_cluster_size: int = 50,
        min_samples: int = 10,
        cluster_selection_method: str = 'eom',
        metric: str = 'euclidean'
    ) -> np.ndarray:
        """
        Cluster using HDBSCAN.
        
        Args:
            min_cluster_size: Minimum points for valid cluster
                - Buildings: 50-200 (depends on point density)
                - Trees: 30-100
                - Small objects: 10-30
            min_samples: Neighborhood size for core points
                - Higher = more robust to noise
                - Lower = more sensitive clusters
            cluster_selection_method: 'eom' or 'leaf'
                - 'eom': Maximally stable clusters (default)
                - 'leaf': Leaf nodes, more fine-grained
            metric: Distance metric
                
        Returns:
            Cluster labels (-1 for noise)
        """
        logger.info(f"Running HDBSCAN on {self.n_points} points...")
        
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            cluster_selection_method=cluster_selection_method,
            metric=metric,
            core_dist_n_jobs=-1  # Use all CPU cores
        )
        
        self.labels = clusterer.fit_predict(self.points)
        self.probabilities = clusterer.probabilities_
        
        n_clusters = len(set(self.labels)) - (1 if -1 in self.labels else 0)
        n_noise = list(self.labels).count(-1)
        
        logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")
        
        return self.labels
    
    def cluster_dbscan(
        self,
        eps: float = 0.5,
        min_samples: int = 10
    ) -> np.ndarray:
        """
        Cluster using DBSCAN with fixed epsilon.
        
        Args:
            eps: Maximum distance between neighbors
                - Dense urban: 0.02-0.05m
                - Sparse areas: 0.1-0.5m
                - Calculate from data: eps = 1.5 * avg_nearest_neighbor_dist
            min_samples: Minimum points for core point
            
        Returns:
            Cluster labels (-1 for noise)
        """
        logger.info(f"Running DBSCAN (eps={eps}, min_samples={min_samples})...")
        
        clusterer = DBSCAN(
            eps=eps,
            min_samples=min_samples,
            n_jobs=-1
        )
        
        self.labels = clusterer.fit_predict(self.points)
        
        n_clusters = len(set(self.labels)) - (1 if -1 in self.labels else 0)
        n_noise = list(self.labels).count(-1)
        
        logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")
        
        return self.labels
    
    def estimate_optimal_eps(self, k: int = 4) -> float:
        """
        Estimate optimal eps for DBSCAN using k-distance graph.
        
        Args:
            k: Number of nearest neighbors to consider
            
        Returns:
            Suggested eps value
        """
        tree = KDTree(self.points)
        distances, _ = tree.query(self.points, k=k+1)  # k+1 because includes self
        
        # Sort k-distances
        k_distances = np.sort(distances[:, k])
        
        # Find "elbow" - use 90th percentile as heuristic
        suggested_eps = np.percentile(k_distances, 90)
        
        logger.info(f"Suggested eps: {suggested_eps:.4f} (based on {k}-NN distances)")
        
        return suggested_eps
    
    def get_cluster_stats(self) -> dict:
        """
        Get statistics about clustering results.
        
        Returns:
            Dictionary with cluster statistics
        """
        if self.labels is None:
            raise ValueError("Must run clustering first")
        
        unique_labels = set(self.labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        
        stats = {
            'n_clusters': n_clusters,
            'n_noise': list(self.labels).count(-1),
            'cluster_sizes': []
        }
        
        for label in unique_labels:
            if label == -1:
                continue
            cluster_size = list(self.labels).count(label)
            stats['cluster_sizes'].append(cluster_size)
        
        if stats['cluster_sizes']:
            stats['mean_cluster_size'] = np.mean(stats['cluster_sizes'])
            stats['median_cluster_size'] = np.median(stats['cluster_sizes'])
            stats['min_cluster_size'] = np.min(stats['cluster_sizes'])
            stats['max_cluster_size'] = np.max(stats['cluster_sizes'])
        
        return stats
    
    def extract_clusters(self, min_size: Optional[int] = None) -> list:
        """
        Extract individual clusters as point arrays.
        
        Args:
            min_size: Optional minimum cluster size filter
            
        Returns:
            List of numpy arrays, one per cluster
        """
        if self.labels is None:
            raise ValueError("Must run clustering first")
        
        clusters = []
        unique_labels = set(self.labels) - {-1}  # Exclude noise
        
        for label in unique_labels:
            mask = self.labels == label
            cluster_points = self.points[mask]
            
            if min_size is None or len(cluster_points) >= min_size:
                clusters.append({
                    'label': label,
                    'points': cluster_points,
                    'size': len(cluster_points),
                    'centroid': cluster_points.mean(axis=0)
                })
        
        # Sort by size
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        return clusters
    
    def filter_by_height(
        self,
        min_height: Optional[float] = None,
        max_height: Optional[float] = None
    ) -> np.ndarray:
        """
        Filter clusters by height (Z) range.
        Useful for separating ground/buildings/trees.
        
        Args:
            min_height: Minimum Z coordinate
            max_height: Maximum Z coordinate
            
        Returns:
            Boolean mask for filtering
        """
        mask = np.ones(self.n_points, dtype=bool)
        
        if min_height is not None:
            mask &= (self.points[:, 2] >= min_height)
        
        if max_height is not None:
            mask &= (self.points[:, 2] <= max_height)
        
        n_filtered = mask.sum()
        logger.info(f"Height filter: {n_filtered}/{self.n_points} points retained")
        
        return mask


def segment_buildings_from_ground(
    points: np.ndarray,
    ground_height: float,
    height_threshold: float = 2.0,
    min_cluster_size: int = 100
) -> Tuple[list, np.ndarray]:
    """
    Segment buildings from pointcloud above ground.
    
    Args:
        points: Full pointcloud (N, 3)
        ground_height: Estimated ground elevation
        height_threshold: Minimum height above ground for buildings
        min_cluster_size: Minimum points for valid building
        
    Returns:
        Tuple of (building_clusters, non_building_mask)
    """
    # Filter points above ground
    above_ground = points[points[:, 2] > (ground_height + height_threshold)]
    
    logger.info(f"Found {len(above_ground)} points above ground+{height_threshold}m")
    
    # Cluster in 2D (X, Y only)
    clusterer = PointCloudClusterer(above_ground[:, :2])
    
    # Auto-estimate eps
    eps = clusterer.estimate_optimal_eps(k=4)
    
    # Cluster
    clusterer.cluster_dbscan(eps=eps * 1.5, min_samples=10)
    
    # Extract building clusters
    buildings = clusterer.extract_clusters(min_size=min_cluster_size)
    
    # Map back to 3D
    for building in buildings:
        # Get original 3D points
        labels_2d = clusterer.labels
        mask = labels_2d == building['label']
        building['points_3d'] = above_ground[mask]
    
    return buildings, clusterer.labels


def adaptive_clustering_for_fkb(
    points: np.ndarray,
    point_density: float,
    fkb_standard: str = 'B'
) -> list:
    """
    Adaptive clustering with parameters based on point density and FKB standard.
    
    Args:
        points: Pointcloud (N, 3)
        point_density: Points per square meter
        fkb_standard: 'A', 'B', 'C', or 'D'
        
    Returns:
        List of clusters
    """
    # Calculate adaptive parameters
    # min_cluster_size ~ minimum building area * point_density
    min_building_area = {
        'A': 10,   # 10 m² minimum in urban
        'B': 15,   # 15 m²
        'C': 25,   # 25 m²
        'D': 50    # 50 m² in wilderness
    }
    
    area = min_building_area.get(fkb_standard, 15)
    min_cluster_size = int(area * point_density)
    min_cluster_size = max(20, min_cluster_size)  # At least 20 points
    
    logger.info(f"Adaptive parameters for FKB-{fkb_standard}:")
    logger.info(f"  Point density: {point_density:.1f} pts/m²")
    logger.info(f"  Min cluster size: {min_cluster_size}")
    
    clusterer = PointCloudClusterer(points)
    clusterer.cluster_hdbscan(
        min_cluster_size=min_cluster_size,
        min_samples=max(5, min_cluster_size // 10),
        cluster_selection_method='eom'
    )
    
    clusters = clusterer.extract_clusters()
    
    return clusters


if __name__ == "__main__":
    # Example: Cluster synthetic building footprints
    np.random.seed(42)
    
    # Create 3 building footprints
    building1 = np.random.normal(loc=[0, 0, 10], scale=[2, 2, 0.5], size=(200, 3))
    building2 = np.random.normal(loc=[10, 0, 10], scale=[3, 3, 0.5], size=(300, 3))
    building3 = np.random.normal(loc=[5, 10, 12], scale=[1.5, 1.5, 0.5], size=(150, 3))
    
    # Add some noise points
    noise = np.random.uniform(low=[-5, -5, 0], high=[15, 15, 15], size=(50, 3))
    
    # Combine
    all_points = np.vstack([building1, building2, building3, noise])
    
    print("Testing HDBSCAN clustering:")
    clusterer = PointCloudClusterer(all_points)
    labels = clusterer.cluster_hdbscan(min_cluster_size=50, min_samples=10)
    
    stats = clusterer.get_cluster_stats()
    print(f"\nClustering statistics:")
    print(f"  Clusters: {stats['n_clusters']}")
    print(f"  Noise points: {stats['n_noise']}")
    print(f"  Mean cluster size: {stats['mean_cluster_size']:.1f}")
    
    clusters = clusterer.extract_clusters()
    print(f"\nExtracted {len(clusters)} clusters:")
    for i, cluster in enumerate(clusters):
        print(f"  Cluster {i+1}: {cluster['size']} points at {cluster['centroid']}")
