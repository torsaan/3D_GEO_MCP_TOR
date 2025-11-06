# Geometric Extraction: Boundaries, Footprints & Centerlines

## Alpha Shapes: The Swiss Army Knife of Boundaries

Alpha shapes are **concave hulls** - they fit tightly around point clouds, capturing detailed boundaries unlike convex hulls.

### Quick Start

```python
from geometric_extraction import BoundaryExtractor
import numpy as np

# Your 2D points (building footprint, road outline, etc.)
points_2d = building_points[:, :2]  # Just X, Y

# Create extractor
extractor = BoundaryExtractor(points_2d)

# Compute alpha shape
boundary = extractor.compute_alpha_shape(
    alpha=None,          # Auto-optimize
    optimize_alpha=True
)

print(f"Boundary area: {boundary.area:.2f} m²")
print(f"Boundary length: {boundary.length:.2f} m")
print(f"Vertices: {len(boundary.exterior.coords)}")
```

### Understanding Alpha Parameter

Alpha controls **how tight** the boundary fits:

```python
# Alpha = 0 → Super tight, follows every point
# Alpha = small (0.5-2.0 × spacing) → Tight fit, detailed
# Alpha = medium (2.0-5.0 × spacing) → Moderate fit
# Alpha = large (>10 × spacing) → Loose fit, approaches convex hull
# Alpha = ∞ → Convex hull

# Calculate point spacing
spacing = extractor.estimate_point_spacing()
print(f"Average spacing: {spacing:.3f} m")

# Try different alphas
alphas = [1.0 * spacing, 2.0 * spacing, 5.0 * spacing]
for alpha in alphas:
    boundary = extractor.compute_alpha_shape(alpha=alpha)
    print(f"Alpha={alpha:.3f}: {len(boundary.exterior.coords)} vertices")

# For FKB building footprints:
# Use alpha = 1.5-2.0 × spacing for good balance
```

### Visual Guide

```
Point spacing = 0.10m

Alpha = 0.10m (1.0× spacing)     Alpha = 0.20m (2.0× spacing)
┌─┐                                ┌──┐
│ │  ┌┐  Very detailed            │  │  Good detail
│ │  ││  Every bump               │  │  Main features
│ │  ││                            │  │
└─┴──┘│                            └──┘
    └─┘

Alpha = 0.50m (5.0× spacing)     Convex Hull
┌────┐  Simplified               ┌────┐  Maximum
│    │  Major features           │    │  simplification
│    │                            │    │
└────┘                            └────┘
```

## Complete Building Footprint Extraction

```python
from geometric_extraction import extract_building_footprint

# All-in-one function with FKB parameters
footprint = extract_building_footprint(
    building_points,      # (N, 3) array
    fkb_standard='B',    # 'A', 'B', 'C', or 'D'
    simplify=True        # Regularize to building orientations
)

# What it does:
# 1. Projects to 2D
# 2. Computes alpha shape with optimal parameter
# 3. Simplifies using Douglas-Peucker
# 4. Regularizes to dominant angles
# 5. Returns Shapely Polygon

# Use the footprint
print(f"Area: {footprint.area:.2f} m²")
print(f"Perimeter: {footprint.length:.2f} m")

# Export to GeoJSON
import json
geojson = {
    "type": "Feature",
    "geometry": footprint.__geo_interface__,
    "properties": {
        "area": footprint.area,
        "fkb_standard": "B"
    }
}
```

## Polygon Simplification

Reduce vertex count while preserving shape:

```python
# Douglas-Peucker algorithm
simplified = extractor.simplify_polygon(
    polygon,
    tolerance=0.10,      # 10cm tolerance
    regularize=True      # Align to building orientations
)

# Tolerance guide for FKB:
fkb_tolerances = {
    'A': 0.03,  # 3cm - keep details
    'B': 0.05,  # 5cm - standard
    'C': 0.15,  # 15cm - simplified
    'D': 0.30   # 30cm - very simplified
}

# Before: 243 vertices
# After:   18 vertices (90% reduction!)
```

## Building Regularization

Align edges to architectural orientations:

```python
# Buildings typically have:
# - Walls at right angles
# - Dominant orientations (0°, 90°, or other)

# Regularization does:
# 1. Compute edge angles
# 2. Find 2 dominant directions (usually perpendicular)
# 3. Snap each edge to nearest dominant angle

irregular = extractor.compute_alpha_shape(alpha=0.2)
regular = extractor.simplify_polygon(
    irregular,
    tolerance=0.10,
    regularize=True  # ← Magic happens here
)

# Result:
# ✓ Cleaner geometry
# ✓ Right angles preserved
# ✓ Smaller file size
# ✓ Better for FKB database
```

## Spline Fitting for Roads

Smooth curves through discrete points:

```python
from geometric_extraction import SplineFitter

# Ordered road centerline points
road_points = extract_centerline(...)  # (N, 2) or (N, 3)

# Create fitter
fitter = SplineFitter(road_points)

# Fit smooth spline
smooth_curve = fitter.fit_parametric_spline(
    smoothing=None,     # Auto: 0.2 × n_points
    degree=3,           # Cubic spline (smooth)
    num_samples=100     # Points in output
)

# Now smooth_curve is a smooth version of road_points
# Great for cartography!
```

### Smoothing Parameter Guide

```python
n_points = len(road_points)

# No smoothing (interpolation)
smoothing = 0
# Result: Passes through every point, may be wiggly

# Light smoothing (recommended for clean data)
smoothing = n_points * 0.1
# Result: Slight smoothing, preserves detail

# Medium smoothing (recommended for noisy data)
smoothing = n_points * 0.3
# Result: Good balance, removes noise

# Heavy smoothing (for very noisy data)
smoothing = n_points * 1.0
# Result: Very smooth, may lose details

# For FKB roads:
# GPS data → medium smoothing (0.3-0.5)
# LiDAR data → light smoothing (0.1-0.2)
```

### Spline Example

```python
import matplotlib.pyplot as plt

# Original noisy centerline
road_points = get_noisy_road_centerline()

# Fit with different smoothing
for s_factor in [0, 0.1, 0.3, 1.0]:
    fitter = SplineFitter(road_points)
    smooth = fitter.fit_parametric_spline(
        smoothing=len(road_points) * s_factor,
        degree=3,
        num_samples=200
    )
    
    plt.plot(smooth[:, 0], smooth[:, 1], 
             label=f's={s_factor}')

plt.plot(road_points[:, 0], road_points[:, 1], 
         'ko', ms=3, label='Original')
plt.legend()
plt.axis('equal')
plt.show()
```

## Road Centerline Extraction

Two methods: skeleton-based and medial axis:

```python
from geometric_extraction import CenterlineExtractor

# Your road points (2D)
road_points_2d = road_points[:, :2]

extractor = CenterlineExtractor(road_points_2d)

# Method 1: Skeleton (via minimum spanning tree)
centerline = extractor.extract_via_skeleton(
    grid_resolution=0.5  # Connect points within 0.5m
)

# Method 2: Medial axis (via Delaunay)
centerline = extractor.extract_via_medial_axis()

# Returns Shapely LineString
print(f"Centerline length: {centerline.length:.2f} m")

# Smooth the centerline
if len(centerline.coords) > 3:
    fitter = SplineFitter(np.array(centerline.coords))
    smooth_centerline = fitter.fit_parametric_spline(
        smoothing=len(centerline.coords) * 0.3
    )
```

## Complete Workflow Examples

### Building Footprint Pipeline

```python
from pointcloud_core import PointCloudProcessor
from clustering import PointCloudClusterer
from geometric_extraction import extract_building_footprint
import geopandas as gpd

# 1. Load and filter
processor = PointCloudProcessor('city.las')
processor.load()
buildings = processor.filter_by_classification([6])

# 2. Cluster individual buildings
clusterer = PointCloudClusterer(buildings[:, :2])
clusterer.cluster_hdbscan(min_cluster_size=100)
clusters = clusterer.extract_clusters()

# 3. Extract footprint for each
footprints = []
for cluster in clusters:
    # Get 3D points
    cluster_3d = buildings[clusterer.labels == cluster['label']]
    
    # Extract footprint
    try:
        footprint = extract_building_footprint(
            cluster_3d,
            fkb_standard='B',
            simplify=True
        )
        
        footprints.append({
            'geometry': footprint,
            'area': footprint.area,
            'n_points': len(cluster_3d)
        })
    except:
        print(f"Failed to extract cluster {cluster['label']}")

# 4. Save to file
gdf = gpd.GeoDataFrame(footprints, crs='EPSG:25833')  # EUREF89 UTM 33
gdf.to_file('buildings.shp')
print(f"Exported {len(footprints)} buildings")
```

### Road Centerline Pipeline

```python
from pointcloud_core import PointCloudProcessor
from clustering import PointCloudClusterer  
from geometric_extraction import CenterlineExtractor, SplineFitter

# 1. Load ground points
processor = PointCloudProcessor('roads.las')
processor.load()
ground = processor.filter_by_classification([2])

# 2. Filter by intensity (roads are usually higher)
if hasattr(processor.las, 'intensity'):
    intensity = processor.las.intensity[
        processor.las.classification == 2
    ]
    high_intensity = intensity > np.percentile(intensity, 70)
    road_points = ground[high_intensity]
else:
    road_points = ground

# 3. Cluster road segments
clusterer = PointCloudClusterer(road_points[:, :2])
eps = clusterer.estimate_optimal_eps(k=4)
clusterer.cluster_dbscan(eps=eps * 2, min_samples=20)

# 4. Extract centerline for each segment
centerlines = []
for cluster in clusterer.extract_clusters(min_size=100):
    extractor = CenterlineExtractor(cluster['points'])
    centerline = extractor.extract_via_skeleton(
        grid_resolution=0.5
    )
    
    if len(centerline.coords) > 3:
        # Smooth
        fitter = SplineFitter(np.array(centerline.coords))
        smooth = fitter.fit_parametric_spline(
            smoothing=len(centerline.coords) * 0.3,
            num_samples=100
        )
        
        from shapely.geometry import LineString
        centerlines.append({
            'geometry': LineString(smooth),
            'length': LineString(smooth).length
        })

# 5. Save
gdf = gpd.GeoDataFrame(centerlines, crs='EPSG:25833')
gdf.to_file('roads.shp')
```

## Quality Control

### Check Footprint Quality

```python
def validate_footprint(footprint, building_points):
    """Validate building footprint quality."""
    
    # 1. Check area is reasonable
    area = footprint.area
    if area < 10:
        return False, "Area too small (<10 m²)"
    if area > 10000:
        return False, "Area too large (>10000 m²)"
    
    # 2. Check convexity
    convex_hull = footprint.convex_hull
    convexity = footprint.area / convex_hull.area
    if convexity < 0.5:
        return False, f"Too concave (convexity={convexity:.2f})"
    
    # 3. Check point coverage
    from shapely.geometry import Point
    points_inside = sum(
        footprint.contains(Point(p[:2]))
        for p in building_points[:100]  # Sample
    )
    coverage = points_inside / min(100, len(building_points))
    if coverage < 0.7:
        return False, f"Poor coverage ({coverage:.1%})"
    
    # 4. Check aspect ratio
    bounds = footprint.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    aspect = max(width, height) / min(width, height)
    if aspect > 10:
        return False, f"Extreme aspect ratio ({aspect:.1f})"
    
    return True, "OK"

# Use it
footprint = extract_building_footprint(building_points)
valid, message = validate_footprint(footprint, building_points)
print(f"Validation: {message}")
```

### Check Centerline Quality

```python
def validate_centerline(centerline, expected_length_range):
    """Validate road centerline quality."""
    
    length = centerline.length
    min_len, max_len = expected_length_range
    
    if length < min_len:
        return False, f"Too short ({length:.1f}m < {min_len}m)"
    if length > max_len:
        return False, f"Too long ({length:.1f}m > {max_len}m)"
    
    # Check for loops (shouldn't have)
    if not centerline.is_simple:
        return False, "Self-intersecting"
    
    return True, "OK"
```

## Common Issues

### Issue: Alpha Shape Too Complex

```python
# Problem: 500+ vertices
footprint = extractor.compute_alpha_shape(alpha=0.05)
# len(footprint.exterior.coords) = 523

# Solution 1: Increase alpha
footprint = extractor.compute_alpha_shape(alpha=0.15)
# len(footprint.exterior.coords) = 89

# Solution 2: Simplify after
footprint = extractor.simplify_polygon(
    footprint, 
    tolerance=0.10
)
# len(footprint.exterior.coords) = 24
```

### Issue: Alpha Shape Has Holes

```python
# Alpha shapes can have interior holes
footprint = extractor.compute_alpha_shape(alpha=0.2)

if len(footprint.interiors) > 0:
    print(f"Warning: {len(footprint.interiors)} holes detected")
    
    # Option 1: Remove holes
    from shapely.geometry import Polygon
    footprint_no_holes = Polygon(footprint.exterior)
    
    # Option 2: Increase alpha (makes it more convex)
    footprint = extractor.compute_alpha_shape(alpha=0.5)
```

### Issue: Spline Too Wiggly

```python
# Increase smoothing
smooth = fitter.fit_parametric_spline(
    smoothing=len(points) * 0.5,  # Increase from 0.1
    degree=3
)
```

### Issue: Spline Too Smooth (Lost Details)

```python
# Decrease smoothing
smooth = fitter.fit_parametric_spline(
    smoothing=len(points) * 0.05,  # Decrease from 0.3
    degree=3
)

# Or use moving average instead
smooth = fitter.smooth_polyline(
    window_size=5,
    iterations=2
)
```

## Performance Tips

```python
# Tip 1: Downsample before alpha shape
if len(points_2d) > 1000:
    # Sample every Nth point
    step = len(points_2d) // 500
    sampled = points_2d[::step]
    boundary = BoundaryExtractor(sampled).compute_alpha_shape()

# Tip 2: Use convex hull for simple shapes
# Convex hull is O(n log n), alpha shape is O(n²)
if is_simple_rectangular_building:
    boundary = extractor.compute_convex_hull()
    boundary = extractor.simplify_polygon(boundary, regularize=True)

# Tip 3: Parallel process multiple buildings
from joblib import Parallel, delayed

footprints = Parallel(n_jobs=-1)(
    delayed(extract_building_footprint)(cluster['points'], 'B')
    for cluster in building_clusters
)
```

## Summary Checklist

- [ ] Use alpha = 1.5-2.0 × spacing for buildings
- [ ] Simplify with FKB-appropriate tolerance
- [ ] Regularize building footprints to dominant angles
- [ ] Smooth road centerlines with appropriate factor
- [ ] Validate area, coverage, and geometry
- [ ] Check for holes and self-intersections
- [ ] Export with proper CRS (EPSG:25833 for Norway)

## Further Reading

- Alpha shapes: Edelsbrunner et al. (1983)
- Douglas-Peucker: Douglas & Peucker (1973)
- Shapely documentation: https://shapely.readthedocs.io/
- B-splines: https://docs.scipy.org/doc/scipy/tutorial/interpolate.html
