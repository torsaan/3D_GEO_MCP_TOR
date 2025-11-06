"""
RANSAC implementations for robust geometric fitting.
Supports plane, line, and cylinder fitting with various RANSAC variants.
"""

import numpy as np
import open3d as o3d
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class RANSACFitter:
    """RANSAC-based geometric primitive fitting."""
    
    def __init__(self, points: np.ndarray):
        """
        Initialize fitter with pointcloud.
        
        Args:
            points: numpy array of shape (N, 3)
        """
        self.points = points
        self.n_points = len(points)
        
    def fit_plane(
        self,
        distance_threshold: float = 0.01,
        ransac_n: int = 3,
        num_iterations: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit plane using RANSAC.
        
        Args:
            distance_threshold: Max distance for inlier (meters)
                - FKB-A: 0.01-0.03m
                - FKB-B: 0.03-0.05m  
                - FKB-C: 0.05-0.15m
            ransac_n: Minimum points for plane (3)
            num_iterations: RANSAC iterations
            
        Returns:
            Tuple of (plane_model [a,b,c,d], inlier_indices)
            Plane equation: ax + by + cz + d = 0
        """
        # Convert to Open3D
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(self.points)
        
        # RANSAC plane segmentation
        plane_model, inliers = pcd.segment_plane(
            distance_threshold=distance_threshold,
            ransac_n=ransac_n,
            num_iterations=num_iterations
        )
        
        a, b, c, d = plane_model
        logger.info(f"Plane equation: {a:.3f}x + {b:.3f}y + {c:.3f}z + {d:.3f} = 0")
        logger.info(f"Inliers: {len(inliers)}/{self.n_points} ({100*len(inliers)/self.n_points:.1f}%)")
        
        return plane_model, np.array(inliers)
    
    def fit_multiple_planes(
        self,
        max_planes: int = 5,
        distance_threshold: float = 0.02,
        min_inliers: int = 100
    ) -> list:
        """
        Fit multiple planes sequentially.
        Useful for building roofs with multiple sections.
        
        Args:
            max_planes: Maximum number of planes to detect
            distance_threshold: Inlier distance threshold
            min_inliers: Minimum inliers to accept plane
            
        Returns:
            List of dicts with 'model' and 'inliers' keys
        """
        remaining_points = self.points.copy()
        planes = []
        
        for i in range(max_planes):
            if len(remaining_points) < min_inliers:
                break
                
            # Fit plane to remaining points
            fitter = RANSACFitter(remaining_points)
            plane_model, inlier_indices = fitter.fit_plane(
                distance_threshold=distance_threshold,
                num_iterations=500
            )
            
            inliers = remaining_points[inlier_indices]
            
            if len(inliers) < min_inliers:
                break
            
            planes.append({
                'model': plane_model,
                'inliers': inliers,
                'n_inliers': len(inliers)
            })
            
            # Remove inliers from remaining points
            mask = np.ones(len(remaining_points), dtype=bool)
            mask[inlier_indices] = False
            remaining_points = remaining_points[mask]
            
            logger.info(f"Plane {i+1}: {len(inliers)} inliers, {len(remaining_points)} remaining")
        
        return planes
    
    def fit_line_3d(
        self,
        distance_threshold: float = 0.05,
        num_iterations: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Fit 3D line using RANSAC.
        
        Args:
            distance_threshold: Max distance for inlier
            num_iterations: RANSAC iterations
            
        Returns:
            Tuple of (point_on_line, direction_vector, inlier_indices)
        """
        best_inliers = []
        best_point = None
        best_direction = None
        
        for _ in range(num_iterations):
            # Sample 2 random points
            idx = np.random.choice(self.n_points, 2, replace=False)
            p1, p2 = self.points[idx]
            
            # Line direction
            direction = p2 - p1
            direction = direction / np.linalg.norm(direction)
            
            # Compute point-to-line distances
            v = self.points - p1
            distances = np.linalg.norm(
                v - np.outer(np.dot(v, direction), direction),
                axis=1
            )
            
            # Count inliers
            inliers = np.where(distances < distance_threshold)[0]
            
            if len(inliers) > len(best_inliers):
                best_inliers = inliers
                best_point = p1
                best_direction = direction
        
        logger.info(f"Line fit: {len(best_inliers)}/{self.n_points} inliers")
        
        return best_point, best_direction, np.array(best_inliers)
    
    def compute_plane_residuals(self, plane_model: np.ndarray) -> np.ndarray:
        """
        Compute point-to-plane distances.
        
        Args:
            plane_model: [a, b, c, d] plane coefficients
            
        Returns:
            Array of signed distances
        """
        a, b, c, d = plane_model
        
        # Distance = |ax + by + cz + d| / sqrt(a² + b² + c²)
        numerator = np.abs(
            a * self.points[:, 0] + 
            b * self.points[:, 1] + 
            c * self.points[:, 2] + 
            d
        )
        denominator = np.sqrt(a**2 + b**2 + c**2)
        
        return numerator / denominator
    
    def refine_plane_least_squares(self, inliers: np.ndarray) -> np.ndarray:
        """
        Refine plane using least squares on inliers.
        
        Args:
            inliers: Indices of inlier points
            
        Returns:
            Refined plane model [a, b, c, d]
        """
        inlier_points = self.points[inliers]
        
        # Center points
        centroid = inlier_points.mean(axis=0)
        centered = inlier_points - centroid
        
        # SVD for plane fitting
        _, _, vh = np.linalg.svd(centered)
        normal = vh[2, :]  # Last singular vector
        
        # Normalize normal
        normal = normal / np.linalg.norm(normal)
        
        # Compute d
        d = -np.dot(normal, centroid)
        
        return np.array([normal[0], normal[1], normal[2], d])


class MSACFitter(RANSACFitter):
    """MSAC (M-estimator SAC) variant with squared error cost."""
    
    def fit_plane_msac(
        self,
        distance_threshold: float = 0.01,
        num_iterations: int = 1000
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit plane using MSAC.
        Uses squared error cost instead of inlier counting.
        
        Args:
            distance_threshold: Max distance threshold
            num_iterations: RANSAC iterations
            
        Returns:
            Tuple of (plane_model, inlier_indices)
        """
        best_cost = float('inf')
        best_model = None
        best_inliers = []
        
        threshold_sq = distance_threshold ** 2
        
        for _ in range(num_iterations):
            # Sample 3 random points
            idx = np.random.choice(self.n_points, 3, replace=False)
            sample = self.points[idx]
            
            # Fit plane to sample
            v1 = sample[1] - sample[0]
            v2 = sample[2] - sample[0]
            normal = np.cross(v1, v2)
            
            if np.linalg.norm(normal) < 1e-6:
                continue
                
            normal = normal / np.linalg.norm(normal)
            d = -np.dot(normal, sample[0])
            
            model = np.array([normal[0], normal[1], normal[2], d])
            
            # Compute residuals
            residuals = self.compute_plane_residuals(model)
            
            # MSAC cost: min(r², threshold²)
            cost = np.sum(np.minimum(residuals**2, threshold_sq))
            
            if cost < best_cost:
                best_cost = cost
                best_model = model
                best_inliers = np.where(residuals < distance_threshold)[0]
        
        logger.info(f"MSAC plane fit: {len(best_inliers)}/{self.n_points} inliers, cost={best_cost:.3f}")
        
        return best_model, best_inliers


def extract_building_planes(points: np.ndarray, fkb_standard: str = 'B') -> list:
    """
    Extract building roof planes with FKB-appropriate parameters.
    
    Args:
        points: Building point array
        fkb_standard: 'A', 'B', 'C', or 'D'
        
    Returns:
        List of plane dictionaries
    """
    # Set threshold based on FKB standard
    thresholds = {
        'A': 0.02,  # 2cm for urban areas
        'B': 0.04,  # 4cm for dense areas
        'C': 0.10,  # 10cm for sparse areas
        'D': 0.15   # 15cm for wilderness
    }
    
    threshold = thresholds.get(fkb_standard, 0.04)
    
    fitter = RANSACFitter(points)
    planes = fitter.fit_multiple_planes(
        max_planes=10,
        distance_threshold=threshold,
        min_inliers=50
    )
    
    return planes


if __name__ == "__main__":
    # Example: Generate synthetic building roof
    np.random.seed(42)
    
    # Create two intersecting roof planes
    n_points = 1000
    
    # Plane 1: z = 0.3x + 10
    x1 = np.random.uniform(-5, 5, n_points//2)
    y1 = np.random.uniform(0, 10, n_points//2)
    z1 = 0.3 * x1 + 10 + np.random.normal(0, 0.01, n_points//2)
    plane1 = np.column_stack([x1, y1, z1])
    
    # Plane 2: z = -0.3x + 10
    x2 = np.random.uniform(-5, 5, n_points//2)
    y2 = np.random.uniform(0, 10, n_points//2)
    z2 = -0.3 * x2 + 10 + np.random.normal(0, 0.01, n_points//2)
    plane2 = np.column_stack([x2, y2, z2])
    
    # Combine
    roof_points = np.vstack([plane1, plane2])
    
    # Detect planes
    planes = extract_building_planes(roof_points, fkb_standard='A')
    print(f"\nDetected {len(planes)} roof planes:")
    for i, plane in enumerate(planes):
        print(f"  Plane {i+1}: {plane['n_inliers']} points")
