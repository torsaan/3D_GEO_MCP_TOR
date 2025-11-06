# FKB Pointcloud Processing - Quick Reference

All files ready to use in your MCP server!

## 📁 Python Implementation Files

### Core Processing
- **`pointcloud_core.py`** - Load LAS, filter, compute features, normals
  - Class: `PointCloudProcessor`
  - Key methods: `load()`, `filter_by_classification()`, `compute_local_features()`

### Geometric Fitting  
- **`ransac_fitting.py`** - Robust plane/line fitting with RANSAC
  - Classes: `RANSACFitter`, `MSACFitter`
  - Key functions: `fit_plane()`, `fit_multiple_planes()`, `extract_building_planes()`

### Clustering
- **`clustering.py`** - HDBSCAN and DBSCAN segmentation
  - Class: `PointCloudClusterer`
  - Key functions: `cluster_hdbscan()`, `segment_buildings_from_ground()`, `adaptive_clustering_for_fkb()`

### Geometric Extraction
- **`geometric_extraction.py`** - Boundaries, footprints, centerlines
  - Classes: `BoundaryExtractor`, `SplineFitter`, `CenterlineExtractor`
  - Key functions: `compute_alpha_shape()`, `extract_building_footprint()`, `fit_parametric_spline()`

### GPU Acceleration (Optional)
- **`gpu_utils.py`** - CuPy/cuML GPU acceleration
  - Classes: `GPUPointCloudProcessor`, `HybridProcessor`
  - 10-50x speedup for large datasets

## 📚 Documentation Files

### Guides
- **`README.md`** - Complete overview, quick start, workflows
- **`RANSAC_GUIDE.md`** - Detailed RANSAC tutorial with examples
- **`CLUSTERING_GUIDE.md`** - Complete clustering guide (HDBSCAN/DBSCAN)
- **`GEOMETRIC_EXTRACTION_GUIDE.md`** - Boundaries, footprints, splines

## 🚀 Quick Start Examples

### Extract Building Footprints
```python
from pointcloud_core import PointCloudProcessor
from clustering import PointCloudClusterer
from geometric_extraction import extract_building_footprint

# Load
processor = PointCloudProcessor('building.las')
processor.load()
buildings = processor.filter_by_classification([6])

# Cluster
clusterer = PointCloudClusterer(buildings[:, :2])
clusterer.cluster_hdbscan(min_cluster_size=100)

# Extract footprints
for cluster in clusterer.extract_clusters():
    points_3d = buildings[clusterer.labels == cluster['label']]
    footprint = extract_building_footprint(points_3d, fkb_standard='B')
    print(f"Area: {footprint.area:.2f} m²")
```

### Detect Roof Planes
```python
from ransac_fitting import extract_building_planes

planes = extract_building_planes(building_points, fkb_standard='B')
print(f"Found {len(planes)} roof sections")

for i, plane in enumerate(planes):
    print(f"Plane {i+1}: {plane['n_inliers']} points")
```

### GPU Acceleration
```python
from gpu_utils import GPUPointCloudProcessor

# Transfer to GPU
processor = GPUPointCloudProcessor(large_pointcloud)

# 10-40x faster clustering
labels = processor.cluster_dbscan_gpu(eps=0.5, min_samples=10)
```

## 📊 FKB Standards Quick Reference

| Standard | Area | H Acc | V Acc | RANSAC threshold | Simplify tolerance |
|----------|------|-------|-------|------------------|-------------------|
| FKB-A | Urban | ±3cm | ±10cm | 0.01-0.02m | 0.03m |
| FKB-B | Dense | ±5cm | ±15cm | 0.02-0.04m | 0.05m |
| FKB-C | Rural | ±15cm | ±48cm | 0.05-0.10m | 0.15m |
| FKB-D | Wilderness | - | - | 0.10-0.15m | 0.30m |

## 🔧 Parameter Cheat Sheet

### RANSAC
```python
distance_threshold = {
    'A': 0.02,  # 2cm
    'B': 0.04,  # 4cm
    'C': 0.10,  # 10cm
    'D': 0.15   # 15cm
}[fkb_standard]

num_iterations = 1000  # Usually sufficient
```

### Clustering
```python
# HDBSCAN
min_cluster_size = min_building_area_m2 * point_density
min_samples = max(5, min_cluster_size // 10)

# DBSCAN  
eps = avg_point_spacing * 1.5  # Or use estimate_optimal_eps()
min_samples = 10-20
```

### Alpha Shapes
```python
spacing = extractor.estimate_point_spacing()
alpha = spacing * 1.5  # Tight fit for buildings
```

### Splines
```python
smoothing = len(points) * 0.3  # Medium smoothing
degree = 3  # Cubic (smooth curves)
```

## 💡 Common Workflows

### 1. Building Extraction Pipeline
```
Load LAS → Filter [class=6] → Cluster (HDBSCAN) → 
Extract planes (RANSAC) → Compute footprints (alpha shape) → 
Simplify & regularize → Export shapefile
```

### 2. Road Centerline Pipeline  
```
Load LAS → Filter [class=2] → Filter by intensity → 
Cluster segments (DBSCAN) → Extract skeleton → 
Smooth with splines → Export shapefile
```

### 3. Quality Control Pipeline
```
Load reference → Extract features → Compare geometries →
Compute IoU/RMSE → Flag issues → Manual review
```

## 🐛 Troubleshooting

### "No inliers found" (RANSAC)
- Increase `distance_threshold`
- Check data is actually planar
- Pre-filter outliers

### "Too many small clusters" (Clustering)
- Increase `min_cluster_size`
- Adjust `eps` (DBSCAN)
- Filter after clustering

### "Alpha shape too complex"
- Increase `alpha` parameter
- Simplify with Douglas-Peucker
- Use convex hull for simple shapes

### "Out of memory" (GPU)
- Process in tiles
- Downsample first
- Use CPU for very large datasets

## 📦 Dependencies

Core (all included in your conda env):
- numpy, scipy, scikit-learn
- laspy, open3d, hdbscan
- alphashape, shapely, geopandas
- networkx

Optional (for GPU):
- cupy, cuml (install via: `conda install -c rapidsai`)

## 📖 Where to Learn More

1. **Start with README.md** for overview
2. **Read specific guides** for detailed tutorials:
   - RANSAC_GUIDE.md for plane fitting
   - CLUSTERING_GUIDE.md for segmentation
   - GEOMETRIC_EXTRACTION_GUIDE.md for boundaries
3. **Look at code examples** in each `.py` file (`if __name__ == "__main__"`)
4. **Check FKB docs** at geonorge.no

## 🎯 Next Steps

1. Test each module with your data
2. Adjust parameters for your use case
3. Build your MCP server tools using these as building blocks
4. Validate against FKB quality requirements
5. Scale up with GPU acceleration if needed

---

All files are in `/mnt/user-data/outputs/` and ready to integrate into your MCP server!

Questions? Check the guides or examine the code - everything is documented with examples.
