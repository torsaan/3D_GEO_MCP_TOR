# Pointcloud Processing for FKB Surveying

Practical Python tools for extracting geometric features from LiDAR pointclouds for Norwegian FKB (Felles Kartgrunnlag) mapping standards.

## Overview

This library provides production-ready implementations for:
- **Building footprint extraction** with plane detection and boundary regularization
- **Road centerline extraction** via skeleton-based methods
- **Robust geometric fitting** using RANSAC variants
- **Density-based clustering** with HDBSCAN and DBSCAN
- **GPU acceleration** for large-scale processing

## Quick Start

```python
from pointcloud_core import PointCloudProcessor
from ransac_fitting import extract_building_planes
from clustering import segment_buildings_from_ground
from geometric_extraction import extract_building_footprint

# Load pointcloud
processor = PointCloudProcessor('data/building.las')
processor.load()

# Filter to building class
buildings = processor.filter_by_classification([6])

# Extract planes
planes = extract_building_planes(buildings, fkb_standard='B')
print(f"Found {len(planes)} roof planes")

# Extract footprint
footprint = extract_building_footprint(buildings, fkb_standard='B')
print(f"Building area: {footprint.area:.2f} m²")
```

## Modules

### `pointcloud_core.py`
Core pointcloud operations: loading LAS files, filtering, normal estimation, feature computation.

**Key Classes:**
- `PointCloudProcessor`: Main interface for pointcloud manipulation

**Key Functions:**
- `load()`: Load from LAS/LAZ
- `filter_by_classification()`: Extract specific LAS classes
- `compute_local_features()`: Eigenvalue-based geometric features
- `estimate_normals()`: Normal vector estimation

### `ransac_fitting.py`
Robust geometric primitive fitting using RANSAC and variants.

**Key Classes:**
- `RANSACFitter`: Standard RANSAC for planes and lines
- `MSACFitter`: M-estimator SAC with squared error cost

**Key Functions:**
- `fit_plane()`: Detect planar surfaces
- `fit_multiple_planes()`: Sequential multi-plane detection
- `fit_line_3d()`: 3D line fitting
- `extract_building_planes()`: FKB-compliant building roof detection

### `clustering.py`
Density-based segmentation for separating objects.

**Key Classes:**
- `PointCloudClusterer`: HDBSCAN and DBSCAN clustering

**Key Functions:**
- `cluster_hdbscan()`: Hierarchical density-based clustering
- `cluster_dbscan()`: Fixed-epsilon clustering
- `segment_buildings_from_ground()`: Separate buildings from terrain
- `adaptive_clustering_for_fkb()`: FKB-aware parameter selection

### `geometric_extraction.py`
Boundary detection, footprint extraction, and spline fitting.

**Key Classes:**
- `BoundaryExtractor`: Alpha shapes and polygon operations
- `SplineFitter`: Smooth curve fitting
- `CenterlineExtractor`: Road centerline detection

**Key Functions:**
- `compute_alpha_shape()`: Concave hull computation
- `extract_building_footprint()`: Complete footprint pipeline
- `fit_parametric_spline()`: B-spline curve fitting

## FKB Standards Reference

| Standard | Area Type | Horiz. Accuracy | Vert. Accuracy | Use Case |
|----------|-----------|-----------------|----------------|----------|
| FKB-A | Central urban | ±3 cm | ±10 cm | Dense cities |
| FKB-B | Dense development | ±5 cm | ±15 cm | Urban areas |
| FKB-C | Sparse areas | ±15 cm | ±48 cm | Rural |
| FKB-D | Wilderness | - | - | Remote areas |

## Parameter Guidelines

### RANSAC Distance Thresholds
```python
# Match to FKB standard accuracy requirements
fkb_thresholds = {
    'A': 0.02,  # 2cm for high-precision urban
    'B': 0.04,  # 4cm for standard urban
    'C': 0.10,  # 10cm for rural
    'D': 0.15   # 15cm for wilderness
}
```

### Clustering Parameters
```python
# HDBSCAN min_cluster_size
# = minimum_building_area * point_density
# Example: 15 m² building, 10 pts/m² → min_cluster_size = 150

# DBSCAN eps (epsilon)
# ≈ 1.5 × average_nearest_neighbor_distance
# Urban: 0.02-0.05m
# Rural: 0.1-0.5m
```

### Alpha Shape Parameters
```python
# alpha = multiplier × average_point_spacing
# Tight fit: 1.0-2.0 × spacing
# Moderate: 2.0-5.0 × spacing  
# Loose: 5.0-10.0 × spacing (approaches convex hull)
```

## Common Workflows

### Building Extraction Pipeline
```python
# 1. Load and filter
processor = PointCloudProcessor('input.las')
processor.load()
buildings = processor.filter_by_classification([6])

# 2. Cluster individual buildings
from clustering import PointCloudClusterer
clusterer = PointCloudClusterer(buildings[:, :2])  # 2D clustering
clusterer.cluster_hdbscan(min_cluster_size=100)
building_clusters = clusterer.extract_clusters()

# 3. Extract footprint for each
footprints = []
for cluster in building_clusters:
    footprint = extract_building_footprint(
        cluster['points'],
        fkb_standard='B',
        simplify=True
    )
    footprints.append(footprint)

# 4. Save to shapefile
import geopandas as gpd
gdf = gpd.GeoDataFrame(geometry=footprints)
gdf.to_file('buildings.shp')
```

### Road Centerline Extraction
```python
# 1. Load ground points
processor = PointCloudProcessor('roads.las')
processor.load()
ground = processor.filter_by_classification([2])

# 2. Filter by height and intensity (if available)
# Road points typically have higher intensity

# 3. Cluster road segments
from clustering import PointCloudClusterer
clusterer = PointCloudClusterer(ground[:, :2])
clusterer.cluster_dbscan(eps=0.5, min_samples=20)

# 4. Extract centerlines
from geometric_extraction import CenterlineExtractor
for cluster in clusterer.extract_clusters(min_size=50):
    extractor = CenterlineExtractor(cluster['points'][:, :2])
    centerline = extractor.extract_via_skeleton(grid_resolution=0.5)
    
    # Smooth centerline
    from geometric_extraction import SplineFitter
    if len(centerline.coords) > 3:
        fitter = SplineFitter(np.array(centerline.coords))
        smooth = fitter.fit_parametric_spline(
            smoothing=len(centerline.coords) * 0.3,
            degree=3,
            num_samples=100
        )
```

## Performance Tips

### Memory Management
```python
# Process large files in chunks
import laspy

with laspy.open('huge_file.las') as file:
    for chunk in file.chunk_iterator(2_000_000):
        points = np.vstack([chunk.x, chunk.y, chunk.z]).T
        # Process chunk...
```

### CPU Parallelization
```python
# HDBSCAN and DBSCAN use all cores by default
clusterer.cluster_hdbscan(...)  # Uses n_jobs=-1 internally

# For custom parallelization
from joblib import Parallel, delayed

results = Parallel(n_jobs=-1)(
    delayed(process_building)(cluster) 
    for cluster in building_clusters
)
```

### GPU Acceleration
```python
# Use cuML for GPU clustering on large datasets
# import cuml
# from cuml.cluster import HDBSCAN
# 
# # Convert to cupy array
# import cupy as cp
# points_gpu = cp.array(points)
# 
# # GPU clustering
# clusterer = HDBSCAN(min_cluster_size=100)
# labels = clusterer.fit_predict(points_gpu)
```

## Validation and Quality Control

### Geometric Accuracy Checks
```python
from ransac_fitting import RANSACFitter

fitter = RANSACFitter(building_points)
plane_model, inliers = fitter.fit_plane(distance_threshold=0.02)

# Compute residuals
residuals = fitter.compute_plane_residuals(plane_model)

# Check if meets FKB-B standard (±5cm)
rmse = np.sqrt(np.mean(residuals[inliers]**2))
print(f"RMSE: {rmse*100:.2f} cm")

if rmse < 0.05:
    print("✓ Meets FKB-B accuracy")
else:
    print("✗ Below FKB-B accuracy")
```

### Completeness Checks
```python
# Compare against reference data
from shapely.geometry import Polygon

extracted_footprint = extract_building_footprint(...)
reference_footprint = Polygon(...)  # From cadastre

iou = (extracted_footprint.intersection(reference_footprint).area / 
       extracted_footprint.union(reference_footprint).area)

print(f"IoU: {iou:.2%}")
# Target: >85% for FKB acceptance
```

## Dependencies

Core:
- `numpy`, `scipy` - Numerical operations
- `laspy` - LAS file I/O
- `open3d` - 3D geometry algorithms
- `hdbscan`, `scikit-learn` - Clustering
- `alphashape` - Concave hull computation
- `shapely`, `geopandas` - Vector geometry
- `networkx` - Graph algorithms

Optional (GPU acceleration):
- `cupy` - GPU arrays
- `cuml` - GPU machine learning
- `torch`, `torch-geometric` - Deep learning

## Installation

```bash
# Create conda environment
conda env create -f environment.yml
conda activate geo-mcp-env

# Or install manually
conda install -c conda-forge python=3.10 numpy scipy \
    laspy open3d hdbscan scikit-learn shapely geopandas \
    networkx gdal alphashape
```

## References

### FKB Documentation
- [FKB General Specification](https://dokument.geonorge.no/produktspesifikasjoner/fkb-generell-del/)
- [Punktsky Specification](https://dokument.geonorge.no/produktspesifikasjoner/punktsky/)
- [Kartverket FKB Info](https://www.kartverket.no/geodataarbeid/geovekst/fkb-produktspesifikasjoner)

### Key Papers
- PointNet++: Qi et al., "PointNet++: Deep Hierarchical Feature Learning on Point Sets" (2017)
- HDBSCAN: McInnes et al., "hdbscan: Hierarchical density based clustering" (2017)
- RANSAC: Fischler & Bolles, "Random sample consensus" (1981)
- Alpha Shapes: Edelsbrunner et al., "On the shape of a set of points" (1983)

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please open issues for bugs or feature requests.

Focus areas:
- Deep learning integration (PointNet++, DGCNN)
- Real-time processing optimizations
- Additional FKB dataset implementations
- Validation framework improvements
