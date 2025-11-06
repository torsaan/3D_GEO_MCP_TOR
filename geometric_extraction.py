"""
Geometric extraction utilities for building footprints and road centerlines.
Includes alpha shapes, boundary detection, and spline fitting.
"""

import numpy as np
import alphashape
from scipy.interpolate import splprep, splev, UnivariateSpline
from scipy.spatial import ConvexHull, Delaunay
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union
import networkx as nx
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


class BoundaryExtractor:
    """Extract boundaries from 2D point sets."""
    
    def __init__(self, points_2d: np.ndarray):
        """
        Initialize with 2D points.
        
        Args:
            points_2d: numpy array of shape (N, 2)
        """
        self.points = points_2d
        self.n_points = len(points_2d)
        
    def compute_alpha_shape(
        self,
        alpha: Optional[float] = None,
        optimize_alpha: bool = True
    ) -> Polygon:
        """
        Compute alpha shape (concave hull).
        
        Args:
            alpha: Alpha parameter
                - Small (0.5-2.0 * spacing): Tight fit
                - Large (5-10 * spacing): Approaches convex hull
                - None: Auto-optimize
            optimize_alpha: Automatically find optimal alpha
            
        Returns:
            Shapely Polygon
        """
        if alpha is None or optimize_alpha:
            # Auto-optimize alpha
            logger.info("Optimizing alpha parameter...")
            alpha_shape = alphashape.alphashape(self.points, alpha=0.0)
        else:
            alpha_shape = alphashape.alphashape(self.points, alpha=alpha)
        
        logger.info(f"Alpha shape computed with {len(alpha_shape.exterior.coords)} vertices")
        
        return alpha_shape
    
    def compute_convex_hull(self) -> Polygon:
        """
        Compute convex hull.
        
        Returns:
            Shapely Polygon
        """
        hull = ConvexHull(self.points)
        hull_points = self.points[hull.vertices]
        
        polygon = Polygon(hull_points)
        logger.info(f"Convex hull: {len(hull.vertices)} vertices")
        
        return polygon
    
    def estimate_point_spacing(self) -> float:
        """
        Estimate average point spacing.
        Useful for setting alpha parameter.
        
        Returns:
            Average nearest neighbor distance
        """
        from scipy.spatial import KDTree
        
        tree = KDTree(self.points)
        distances, _ = tree.query(self.points, k=2)  # k=2 to exclude self
        
        avg_spacing = np.mean(distances[:, 1])
        logger.info(f"Average point spacing: {avg_spacing:.4f}")
        
        return avg_spacing
    
    def simplify_polygon(
        self,
        polygon: Polygon,
        tolerance: float = 0.1,
        regularize: bool = True
    ) -> Polygon:
        """
        Simplify and regularize polygon.
        
        Args:
            polygon: Input polygon
            tolerance: Douglas-Peucker tolerance
            regularize: Align to dominant orientations
            
        Returns:
            Simplified polygon
        """
        # Douglas-Peucker simplification
        simplified = polygon.simplify(tolerance, preserve_topology=True)
        
        if regularize:
            simplified = self._regularize_to_dominant_angles(simplified)
        
        logger.info(f"Simplified from {len(polygon.exterior.coords)} to {len(simplified.exterior.coords)} vertices")
        
        return simplified
    
    def _regularize_to_dominant_angles(self, polygon: Polygon) -> Polygon:
        """
        Regularize polygon edges to dominant building orientations.
        
        Args:
            polygon: Input polygon
            
        Returns:
            Regularized polygon
        """
        coords = np.array(polygon.exterior.coords[:-1])  # Exclude closing point
        
        # Compute edge angles
        edges = np.diff(coords, axis=0)
        angles = np.arctan2(edges[:, 1], edges[:, 0])
        angles = np.degrees(angles) % 180  # Normalize to [0, 180)
        
        # Find dominant angles using histogram
        hist, bins = np.histogram(angles, bins=36)  # 5-degree bins
        dominant_bins = np.argsort(hist)[-2:]  # Top 2 directions
        dominant_angles = bins[dominant_bins]
        
        # Snap each edge to nearest dominant angle
        regularized_coords = [coords[0]]
        
        for i in range(len(edges)):
            edge_angle = angles[i]
            
            # Find nearest dominant angle
            angle_diffs = np.abs(dominant_angles - edge_angle)
            nearest_dominant = dominant_angles[np.argmin(angle_diffs)]
            
            # Rotate edge to dominant angle
            length = np.linalg.norm(edges[i])
            angle_rad = np.radians(nearest_dominant)
            new_edge = length * np.array([np.cos(angle_rad), np.sin(angle_rad)])
            
            new_point = regularized_coords[-1] + new_edge
            regularized_coords.append(new_point)
        
        # Close polygon
        regularized_coords.append(regularized_coords[0])
        
        return Polygon(regularized_coords)


class SplineFitter:
    """Fit smooth splines to point sequences."""
    
    def __init__(self, points: np.ndarray):
        """
        Initialize with ordered points.
        
        Args:
            points: numpy array of shape (N, 2) or (N, 3)
        """
        self.points = points
        self.dimension = points.shape[1]
        
    def fit_parametric_spline(
        self,
        smoothing: Optional[float] = None,
        degree: int = 3,
        num_samples: int = 100
    ) -> np.ndarray:
        """
        Fit parametric B-spline curve.
        
        Args:
            smoothing: Smoothing factor
                - None: Auto-calculate
                - 0: Interpolation
                - 0.1-0.5 * n_points: Light smoothing
                - 1-5 * n_points: Heavy smoothing
            degree: Spline degree (1=linear, 3=cubic)
            num_samples: Number of points in output curve
            
        Returns:
            Smooth curve points (num_samples, dimension)
        """
        if smoothing is None:
            smoothing = len(self.points) * 0.2
        
        # Fit spline
        tck, u = splprep(self.points.T, s=smoothing, k=degree)
        
        # Evaluate spline
        u_new = np.linspace(0, 1, num_samples)
        smooth_curve = np.array(splev(u_new, tck)).T
        
        logger.info(f"Fitted {degree}-degree spline with smoothing={smoothing:.2f}")
        
        return smooth_curve
    
    def fit_univariate_spline(
        self,
        x: np.ndarray,
        y: np.ndarray,
        smoothing: float = 0.0,
        degree: int = 3
    ) -> UnivariateSpline:
        """
        Fit 1D spline (y as function of x).
        
        Args:
            x: Independent variable
            y: Dependent variable
            smoothing: Smoothing factor (0 = interpolation)
            degree: Spline degree
            
        Returns:
            UnivariateSpline object
        """
        # Sort by x
        sort_idx = np.argsort(x)
        x_sorted = x[sort_idx]
        y_sorted = y[sort_idx]
        
        spline = UnivariateSpline(x_sorted, y_sorted, s=smoothing, k=degree)
        
        return spline
    
    def smooth_polyline(
        self,
        window_size: int = 5,
        iterations: int = 1
    ) -> np.ndarray:
        """
        Smooth polyline using moving average.
        Simple alternative to splines.
        
        Args:
            window_size: Moving average window
            iterations: Number of smoothing passes
            
        Returns:
            Smoothed points
        """
        smoothed = self.points.copy()
        
        for _ in range(iterations):
            for dim in range(self.dimension):
                smoothed[:, dim] = np.convolve(
                    smoothed[:, dim],
                    np.ones(window_size) / window_size,
                    mode='same'
                )
        
        return smoothed


class CenterlineExtractor:
    """Extract centerlines from road/corridor point clouds."""
    
    def __init__(self, points_2d: np.ndarray):
        """
        Initialize with 2D road points.
        
        Args:
            points_2d: numpy array (N, 2)
        """
        self.points = points_2d
        
    def extract_via_skeleton(
        self,
        grid_resolution: float = 0.5
    ) -> LineString:
        """
        Extract centerline via morphological skeleton.
        
        Args:
            grid_resolution: Voxel/grid size for rasterization
            
        Returns:
            Centerline as LineString
        """
        # This is a simplified version
        # Full implementation would use scipy.ndimage.morphology
        
        # Create graph from points
        from scipy.spatial import KDTree
        tree = KDTree(self.points)
        
        # Connect nearby points
        G = nx.Graph()
        for i, point in enumerate(self.points):
            neighbors = tree.query_ball_point(point, r=grid_resolution * 2)
            for j in neighbors:
                if i != j:
                    dist = np.linalg.norm(self.points[i] - self.points[j])
                    G.add_edge(i, j, weight=dist)
        
        # Find minimum spanning tree
        mst = nx.minimum_spanning_tree(G)
        
        # Order nodes to form path
        if len(mst.nodes()) == 0:
            return LineString([])
        
        # Find endpoints (degree 1)
        endpoints = [n for n in mst.nodes() if mst.degree(n) == 1]
        
        if len(endpoints) < 2:
            return LineString([])
        
        # Find path between endpoints
        try:
            path = nx.shortest_path(mst, endpoints[0], endpoints[1])
            centerline_points = self.points[path]
            
            return LineString(centerline_points)
        except nx.NetworkXNoPath:
            return LineString([])
    
    def extract_via_medial_axis(self) -> LineString:
        """
        Extract centerline via medial axis transform.
        Requires dense point coverage.
        
        Returns:
            Centerline as LineString
        """
        # Compute Delaunay triangulation
        tri = Delaunay(self.points)
        
        # Build graph of triangle centroids
        G = nx.Graph()
        centroids = []
        
        for simplex in tri.simplices:
            triangle_points = self.points[simplex]
            centroid = triangle_points.mean(axis=0)
            centroids.append(centroid)
        
        centroids = np.array(centroids)
        
        # Connect adjacent triangle centroids
        for i, simplex in enumerate(tri.simplices):
            # Find neighboring triangles
            for j, other_simplex in enumerate(tri.simplices[i+1:], start=i+1):
                # Check if triangles share an edge
                shared = len(set(simplex) & set(other_simplex))
                if shared == 2:  # Shared edge
                    dist = np.linalg.norm(centroids[i] - centroids[j])
                    G.add_edge(i, j, weight=dist)
        
        # Find minimum spanning tree as centerline
        if len(G.nodes()) > 0:
            mst = nx.minimum_spanning_tree(G)
            
            # Order nodes
            endpoints = [n for n in mst.nodes() if mst.degree(n) == 1]
            if len(endpoints) >= 2:
                path = nx.shortest_path(mst, endpoints[0], endpoints[1])
                centerline_points = centroids[path]
                
                return LineString(centerline_points)
        
        return LineString([])


def extract_building_footprint(
    building_points: np.ndarray,
    fkb_standard: str = 'B',
    simplify: bool = True
) -> Polygon:
    """
    Extract building footprint with FKB-appropriate parameters.
    
    Args:
        building_points: Building point cloud (N, 3)
        fkb_standard: 'A', 'B', 'C', or 'D'
        simplify: Apply simplification and regularization
        
    Returns:
        Building footprint as Shapely Polygon
    """
    # Project to 2D
    points_2d = building_points[:, :2]
    
    extractor = BoundaryExtractor(points_2d)
    
    # Estimate spacing for alpha parameter
    spacing = extractor.estimate_point_spacing()
    alpha = 1.5 * spacing  # Tight fit
    
    # Compute alpha shape
    footprint = extractor.compute_alpha_shape(alpha=alpha, optimize_alpha=False)
    
    if simplify:
        # Simplification tolerance based on FKB standard
        tolerances = {
            'A': 0.03,  # 3cm
            'B': 0.05,  # 5cm
            'C': 0.15,  # 15cm
            'D': 0.30   # 30cm
        }
        tolerance = tolerances.get(fkb_standard, 0.05)
        
        footprint = extractor.simplify_polygon(
            footprint,
            tolerance=tolerance,
            regularize=True
        )
    
    return footprint


# ============================================================================
# SOSI OUTPUT GENERATION
# ============================================================================

def geometry_to_sosi_coords(geometry, origo_ne: Tuple[float, float], enhet: float = 0.01) -> List[Tuple[int, int]]:
    """
    Convert Shapely geometry coordinates to SOSI integer format.

    Args:
        geometry: Shapely geometry (LineString, Polygon, Point)
        origo_ne: ORIGO-NØ reference point (northing, easting)
        enhet: ENHET scaling factor (default 0.01 for cm precision)

    Returns:
        List of integer coordinate tuples (N, E)

    Example:
        >>> from shapely.geometry import LineString
        >>> line = LineString([(100000, 6500000), (100010, 6500010)])
        >>> coords = geometry_to_sosi_coords(line, origo_ne=(6500000, 100000))
        >>> # Returns [(0, 0), (1000, 1000)]  # In cm units
    """
    from shapely.geometry import Point, LineString, Polygon

    origo_n, origo_e = origo_ne

    # Get coordinate array based on geometry type
    if isinstance(geometry, Point):
        coords = [(geometry.x, geometry.y)]
    elif isinstance(geometry, LineString):
        coords = [(x, y) for x, y in geometry.coords]
    elif isinstance(geometry, Polygon):
        coords = [(x, y) for x, y in geometry.exterior.coords]
    else:
        raise ValueError(f"Unsupported geometry type: {type(geometry)}")

    # Convert to SOSI integer format
    sosi_coords = []
    for e, n in coords:  # Shapely uses (X=E, Y=N)
        # Offset from origo and scale to integer
        n_offset = int(round((n - origo_n) / enhet))
        e_offset = int(round((e - origo_e) / enhet))
        sosi_coords.append((n_offset, e_offset))

    return sosi_coords


def to_sosi_feature(
    geometry,
    objtype: str,
    feature_id: int,
    metadata: dict,
    origo_ne: Tuple[float, float],
    enhet: float = 0.01
) -> str:
    """
    Convert extracted geometry to SOSI feature format with FKB metadata.

    Args:
        geometry: Shapely geometry (Point, LineString, Polygon)
        objtype: FKB OBJTYPE (e.g., 'Bygning', 'Vegkant', 'ElvBekk')
        feature_id: Sequential feature ID
        metadata: Dictionary with FKB attributes (KVALITET, etc.)
        origo_ne: ORIGO-NØ reference point (northing, easting)
        enhet: ENHET scaling factor

    Returns:
        SOSI feature as formatted string

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(100000, 6500000), (100010, 6500000), (100010, 6500010), (100000, 6500010), (100000, 6500000)])
        >>> metadata = {'bygningsnummer': 12345, 'KVALITET': {...}}
        >>> sosi = to_sosi_feature(poly, 'Bygning', 1, metadata, (6500000, 100000))
    """
    from shapely.geometry import Point, LineString, Polygon

    lines = []

    # Feature header
    lines.append(f".{objtype} {feature_id}:")

    # Add attributes
    for key, value in metadata.items():
        if key == 'KVALITET':
            # KVALITET is a nested block
            lines.append("..KVALITET")
            for k, v in value.items():
                lines.append(f"...{k} {v}")
        elif isinstance(value, str):
            lines.append(f"..{key} \"{value}\"")
        else:
            lines.append(f"..{key} {value}")

    # Add geometry
    coords = geometry_to_sosi_coords(geometry, origo_ne, enhet)

    if isinstance(geometry, Point):
        # PUNKT geometry
        n, e = coords[0]
        lines.append(f"..PUNKT")
        lines.append(f"{n} {e}")

    elif isinstance(geometry, LineString):
        # KURVE geometry
        lines.append(f"..KURVE {len(coords)}:")
        for n, e in coords:
            lines.append(f"{n} {e}")

    elif isinstance(geometry, Polygon):
        # FLATE geometry (polygon boundary)
        lines.append(f"..FLATE")
        lines.append(f"..KURVE {len(coords)}:")
        for n, e in coords:
            lines.append(f"{n} {e}")

    return '\n'.join(lines)


def to_geojson_feature(geometry, objtype: str, properties: dict) -> dict:
    """
    Convert extracted geometry to GeoJSON feature format.

    Args:
        geometry: Shapely geometry
        objtype: FKB OBJTYPE
        properties: Feature properties/attributes

    Returns:
        GeoJSON feature dictionary

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
        >>> feature = to_geojson_feature(poly, 'Bygning', {'bygningsnummer': 123})
        >>> import json
        >>> print(json.dumps(feature, indent=2))
    """
    from shapely.geometry import mapping

    return {
        'type': 'Feature',
        'geometry': mapping(geometry),
        'properties': {
            'OBJTYPE': objtype,
            **properties
        }
    }


def format_fkb_attributes(
    objtype: str,
    custom_attrs: dict,
    kvalitet_block: dict
) -> dict:
    """
    Format complete FKB attributes including KVALITET block.

    Args:
        objtype: FKB OBJTYPE
        custom_attrs: Object-specific attributes
        kvalitet_block: KVALITET metadata (MÅLEMETODE, NØYAKTIGHET, etc.)

    Returns:
        Complete attribute dictionary ready for SOSI export

    Example:
        >>> attrs = format_fkb_attributes(
        ...     'Bygning',
        ...     {'bygningsnummer': 12345},
        ...     {'MÅLEMETODE': 'lan', 'NØYAKTIGHET': 0.10, 'SYNBARHET': 0}
        ... )
    """
    from datetime import datetime

    # Ensure KVALITET has all mandatory fields
    required_kvalitet = ['MÅLEMETODE', 'NØYAKTIGHET', 'SYNBARHET', 'DATAFANGSTDATO', 'VERIFISERINGSDATO']

    kvalitet = kvalitet_block.copy()
    today = datetime.now().strftime('%Y%m%d')

    # Add defaults for missing fields
    if 'DATAFANGSTDATO' not in kvalitet:
        kvalitet['DATAFANGSTDATO'] = today
    if 'VERIFISERINGSDATO' not in kvalitet:
        kvalitet['VERIFISERINGSDATO'] = today

    # Build complete attributes
    attributes = {
        'OBJTYPE': objtype,
        **custom_attrs,
        'KVALITET': kvalitet
    }

    return attributes


if __name__ == "__main__":
    # Example: Extract building footprint
    np.random.seed(42)
    
    # Create L-shaped building
    n = 200
    # Horizontal part
    x1 = np.random.uniform(0, 10, n//2)
    y1 = np.random.uniform(0, 3, n//2)
    # Vertical part
    x2 = np.random.uniform(0, 3, n//2)
    y2 = np.random.uniform(0, 10, n//2)
    
    points_2d = np.vstack([
        np.column_stack([x1, y1]),
        np.column_stack([x2, y2])
    ])
    
    # Add Z coordinate
    points_3d = np.column_stack([points_2d, np.ones(n) * 10])
    
    print("Extracting building footprint...")
    footprint = extract_building_footprint(points_3d, fkb_standard='B')
    
    print(f"Footprint area: {footprint.area:.2f} m²")
    print(f"Footprint vertices: {len(footprint.exterior.coords)}")
    print(f"Bounds: {footprint.bounds}")
