"""
Core pointcloud processing utilities for FKB data extraction.
Handles loading, filtering, and basic geometric operations.
"""

import numpy as np
import laspy
import open3d as o3d
from scipy.spatial import KDTree
from typing import Tuple, Optional, List, Dict
from pathlib import Path
import logging
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FKB accuracy standards (loaded from extracted rules if available)
FKB_ACCURACY_STANDARDS = {
    'A': {'class_1': 0.10, 'class_2': 0.20, 'class_3': 0.30, 'class_4': 0.60},
    'B': {'class_1': 0.20, 'class_2': 0.40, 'class_3': 0.60, 'class_4': 1.20},
    'C': {'class_1': 0.50, 'class_2': 1.00, 'class_3': 1.50, 'class_4': 3.00},
    'D': {'class_1': 1.00, 'class_2': 2.00, 'class_3': 3.00, 'class_4': 6.00}
}


class PointCloudProcessor:
    """Main class for pointcloud operations with FKB-aware processing."""

    def __init__(self, las_path: str, fkb_standard: str = 'B', accuracy_class: int = 2):
        """
        Initialize with LAS/LAZ file and FKB parameters.

        Args:
            las_path: Path to LAS or LAZ file
            fkb_standard: FKB standard ('A', 'B', 'C', or 'D')
            accuracy_class: Accuracy class (1-4)
        """
        self.las_path = las_path
        self.las = None
        self.points = None
        self.o3d_cloud = None
        self.fkb_standard = fkb_standard.upper()
        self.accuracy_class = accuracy_class
        self._load_fkb_parameters()

    def _load_fkb_parameters(self):
        """Load FKB accuracy parameters and set processing thresholds."""
        # Get accuracy from standards
        standard_key = f'class_{self.accuracy_class}'
        self.accuracy_standard = FKB_ACCURACY_STANDARDS.get(self.fkb_standard, {}).get(standard_key, 0.50)

        # Set processing parameters based on FKB standard
        self.ransac_distance_threshold = self.accuracy_standard * 2.0  # For plane fitting
        self.simplification_tolerance = self.accuracy_standard  # Douglas-Peucker tolerance
        self.voxel_size = self.accuracy_standard / 2.0  # Voxel downsampling
        self.clustering_eps = self.accuracy_standard * 3.0  # DBSCAN epsilon

        logger.info(f"FKB-{self.fkb_standard} Class {self.accuracy_class} parameters loaded")
        logger.info(f"  Accuracy standard: {self.accuracy_standard:.3f}m")
        logger.info(f"  RANSAC threshold: {self.ransac_distance_threshold:.3f}m")
        logger.info(f"  Simplification tolerance: {self.simplification_tolerance:.3f}m")

    def set_fkb_standard(self, standard: str, accuracy_class: int = None):
        """
        Update FKB standard and recalculate processing parameters.

        Args:
            standard: FKB standard ('A', 'B', 'C', or 'D')
            accuracy_class: Optional accuracy class (1-4), keeps current if None

        Example:
            >>> processor.set_fkb_standard('A', 1)  # High precision
            >>> processor.set_fkb_standard('D', 4)  # Lower precision
        """
        self.fkb_standard = standard.upper()
        if accuracy_class is not None:
            self.accuracy_class = accuracy_class
        self._load_fkb_parameters()

    def get_fkb_metadata(self) -> Dict[str, any]:
        """
        Get FKB metadata for KVALITET block.

        Returns:
            Dictionary with FKB metadata fields
        """
        from datetime import datetime

        metadata = {
            'NØYAKTIGHET': self.accuracy_standard,
            'H-NØYAKTIGHET': self.accuracy_standard,  # Same for horizontal/vertical
            'MÅLEMETODE': 'lan',  # Laser scanning
            'SYNBARHET': 0,  # Good visibility
            'DATAFANGSTDATO': datetime.now().strftime('%Y%m%d'),
            'VERIFISERINGSDATO': datetime.now().strftime('%Y%m%d')
        }

        return metadata

    def get_recommended_parameters(self) -> Dict[str, float]:
        """
        Get recommended processing parameters for current FKB standard.

        Returns:
            Dictionary with parameter recommendations
        """
        return {
            'voxel_size': self.voxel_size,
            'ransac_threshold': self.ransac_distance_threshold,
            'simplification_tolerance': self.simplification_tolerance,
            'clustering_eps': self.clustering_eps,
            'min_cluster_size': int(100 / (self.accuracy_class)),  # Smaller for higher accuracy
            'alpha_shape_alpha': self.accuracy_standard * 2.0
        }

    def load(self) -> np.ndarray:
        """
        Load pointcloud from LAS file.
        
        Returns:
            numpy array of shape (N, 3) with XYZ coordinates
        """
        logger.info(f"Loading pointcloud from {self.las_path}")
        self.las = laspy.read(self.las_path)
        
        # Extract XYZ coordinates
        self.points = np.vstack([
            self.las.x,
            self.las.y,
            self.las.z
        ]).T
        
        logger.info(f"Loaded {len(self.points)} points")
        return self.points
    
    def filter_by_classification(self, classes: List[int]) -> np.ndarray:
        """
        Filter points by LAS classification codes.
        
        Args:
            classes: List of classification codes
                    2 = Ground
                    6 = Building
                    9 = Water
                    etc.
        
        Returns:
            Filtered point array
        """
        if self.las is None:
            self.load()
            
        mask = np.isin(self.las.classification, classes)
        filtered_points = self.points[mask]
        
        logger.info(f"Filtered to {len(filtered_points)} points from classes {classes}")
        return filtered_points
    
    def to_open3d(self, points: Optional[np.ndarray] = None) -> o3d.geometry.PointCloud:
        """
        Convert to Open3D pointcloud format.
        
        Args:
            points: Optional numpy array, uses self.points if None
            
        Returns:
            Open3D PointCloud object
        """
        if points is None:
            points = self.points
            
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points)
        
        self.o3d_cloud = pcd
        return pcd
    
    def remove_outliers_statistical(
        self, 
        nb_neighbors: int = 20, 
        std_ratio: float = 2.0
    ) -> Tuple[o3d.geometry.PointCloud, np.ndarray]:
        """
        Remove statistical outliers using Open3D.
        
        Args:
            nb_neighbors: Number of neighbors for analysis
            std_ratio: Standard deviation threshold
            
        Returns:
            Tuple of (cleaned pointcloud, inlier indices)
        """
        if self.o3d_cloud is None:
            self.to_open3d()
            
        clean_cloud, inlier_indices = self.o3d_cloud.remove_statistical_outlier(
            nb_neighbors=nb_neighbors,
            std_ratio=std_ratio
        )
        
        logger.info(f"Removed {len(self.o3d_cloud.points) - len(clean_cloud.points)} outliers")
        return clean_cloud, inlier_indices
    
    def estimate_normals(
        self, 
        radius: float = 0.1, 
        max_nn: int = 30
    ) -> o3d.geometry.PointCloud:
        """
        Estimate point normals for geometric analysis.
        
        Args:
            radius: Search radius in meters
            max_nn: Maximum nearest neighbors
            
        Returns:
            PointCloud with normals estimated
        """
        if self.o3d_cloud is None:
            self.to_open3d()
            
        self.o3d_cloud.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(
                radius=radius,
                max_nn=max_nn
            )
        )
        
        logger.info(f"Estimated normals for {len(self.o3d_cloud.points)} points")
        return self.o3d_cloud
    
    def compute_local_features(self, k: int = 20) -> dict:
        """
        Compute local geometric features using PCA.
        
        Args:
            k: Number of neighbors for feature computation
            
        Returns:
            Dictionary with eigenvalue-based features
        """
        if self.points is None:
            self.load()
            
        tree = KDTree(self.points)
        n_points = len(self.points)
        
        # Initialize feature arrays
        linearity = np.zeros(n_points)
        planarity = np.zeros(n_points)
        scattering = np.zeros(n_points)
        
        logger.info(f"Computing local features for {n_points} points...")
        
        for i in range(n_points):
            # Find k nearest neighbors
            distances, indices = tree.query(self.points[i], k=k)
            neighbors = self.points[indices]
            
            # Compute covariance matrix
            centered = neighbors - neighbors.mean(axis=0)
            cov = np.cov(centered.T)
            
            # Eigenvalue decomposition
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = np.sort(eigenvalues)[::-1]  # Descending order
            
            # Normalize eigenvalues
            sum_eigs = eigenvalues.sum()
            if sum_eigs > 0:
                e1, e2, e3 = eigenvalues / sum_eigs
                
                # Compute features
                linearity[i] = (e1 - e2) / e1 if e1 > 0 else 0
                planarity[i] = (e2 - e3) / e1 if e1 > 0 else 0
                scattering[i] = e3 / e1 if e1 > 0 else 0
        
        features = {
            'linearity': linearity,
            'planarity': planarity,
            'scattering': scattering
        }
        
        logger.info("Feature computation complete")
        return features
    
    def downsample_voxel(self, voxel_size: float = 0.05) -> o3d.geometry.PointCloud:
        """
        Downsample using voxel grid.
        
        Args:
            voxel_size: Size of voxel in meters
            
        Returns:
            Downsampled pointcloud
        """
        if self.o3d_cloud is None:
            self.to_open3d()
            
        downsampled = self.o3d_cloud.voxel_down_sample(voxel_size=voxel_size)
        
        logger.info(f"Downsampled from {len(self.o3d_cloud.points)} to {len(downsampled.points)} points")
        return downsampled
    
    def save_las(self, output_path: str, points: np.ndarray, classification: Optional[np.ndarray] = None):
        """
        Save pointcloud to LAS format.
        
        Args:
            output_path: Output file path
            points: Point array (N, 3)
            classification: Optional classification array
        """
        # Create new LAS file
        header = laspy.LasHeader(point_format=3, version="1.2")
        header.offsets = np.min(points, axis=0)
        header.scales = [0.01, 0.01, 0.01]
        
        las_out = laspy.LasData(header)
        las_out.x = points[:, 0]
        las_out.y = points[:, 1]
        las_out.z = points[:, 2]
        
        if classification is not None:
            las_out.classification = classification
        
        las_out.write(output_path)
        logger.info(f"Saved {len(points)} points to {output_path}")


# Example usage functions
def load_and_filter_buildings(las_path: str) -> np.ndarray:
    """Quick function to load and filter building points."""
    processor = PointCloudProcessor(las_path)
    processor.load()
    buildings = processor.filter_by_classification([6])  # Class 6 = Buildings
    return buildings


def load_and_clean(las_path: str, voxel_size: float = 0.05) -> o3d.geometry.PointCloud:
    """Load, clean outliers, and downsample."""
    processor = PointCloudProcessor(las_path)
    processor.load()
    processor.to_open3d()
    clean_cloud, _ = processor.remove_outliers_statistical()
    downsampled = clean_cloud.voxel_down_sample(voxel_size=voxel_size)
    return downsampled


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pointcloud_core.py <path_to_las_file>")
        sys.exit(1)
    
    las_file = sys.argv[1]
    
    # Load and process
    processor = PointCloudProcessor(las_file)
    processor.load()
    
    # Filter buildings
    buildings = processor.filter_by_classification([6])
    print(f"Building points: {len(buildings)}")
    
    # Compute features
    features = processor.compute_local_features(k=20)
    print(f"Mean planarity: {features['planarity'].mean():.3f}")
