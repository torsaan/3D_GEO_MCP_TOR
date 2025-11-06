# Clustering: Practical Guide for Pointcloud Segmentation

## HDBSCAN vs DBSCAN: Which to Use?

### HDBSCAN (Recommended)
✅ **Use HDBSCAN when:**
- Point density varies (mixed aerial/terrestrial data)
- Don't know the right epsilon value
- Want automatic parameter selection
- Need soft clustering (probability scores)
- Building extraction from mixed urban scenes

### DBSCAN (Classic)
✅ **Use DBSCAN when:**
- Point density is uniform
- You know the right epsilon (from experience or calculation)
- Need deterministic results
- Simpler to explain/implement

## Quick Start

```python
from clustering import PointCloudClusterer
import numpy as np

# Your pointcloud (N, 3) or (N, 2)
points = load_your_points()

# Create clusterer
clusterer = PointCloudClusterer(points)

# Cluster with HDBSCAN (easy mode)
labels = clusterer.cluster_hdbscan(
    min_cluster_size=50,    # Minimum points for cluster
    min_samples=10          # Noise robustness
)

# Get cluster info
stats = clusterer.get_cluster_stats()
print(f"Found {stats['n_clusters']} clusters")
print(f"Mean size: {stats['mean_cluster_size']:.1f} points")

# Extract individual clusters
clusters = clusterer.extract_clusters(min_size=50)
for cluster in clusters:
    print(f"Cluster {cluster['label']}: {cluster['size']} points")
```

## HDBSCAN Parameters Explained

### `min_cluster_size`

**What it does:** Minimum points needed to form a cluster

**How to choose:**
```python
# Method 1: Based on expected object size
min_area = 15  # m² (minimum building size)
point_density = 10  # points/m² (from your data)
min_cluster_size = int(min_area * point_density)  # = 150

# Method 2: Based on percentile
min_cluster_size = int(len(points) * 0.01)  # 1% of points

# Method 3: FKB-aware (recommended)
fkb_min_sizes = {
    'A': 10 * point_density,   # 10 m² urban
    'B': 15 * point_density,   # 15 m²
    'C': 25 * point_density,   # 25 m²
    'D': 50 * point_density    # 50 m² wilderness
}
min_cluster_size = fkb_min_sizes['B']

# Typical values:
# Buildings: 50-200
# Trees: 30-100  
# Small objects: 10-30
```

### `min_samples`

**What it does:** Number of neighbors for a point to be "core"

**How to choose:**
```python
# Rule of thumb: 10-20% of min_cluster_size
min_samples = max(5, min_cluster_size // 10)

# High min_samples = more robust to noise
# Low min_samples = more sensitive clusters

# Typical values:
# Noisy data: 15-30
# Clean data: 5-15
# Very clean: 3-10
```

### `cluster_selection_method`

**'eom' (Excess of Mass) - Default**
- Selects stable clusters across hierarchy
- Good for buildings (clear density peaks)
- More conservative

**'leaf'**
- Selects leaf nodes
- More fine-grained clusters
- Good for detailed segmentation

```python
# Use 'eom' for:
# - Building footprints
# - Distinct objects

# Use 'leaf' for:
# - Detailed part segmentation
# - When objects touch/overlap
```

## DBSCAN Parameters

### `eps` (Epsilon)

**What it does:** Maximum distance between neighbors

**How to find optimal eps:**

```python
# Method 1: k-distance plot
clusterer = PointCloudClusterer(points)
suggested_eps = clusterer.estimate_optimal_eps(k=4)
print(f"Suggested eps: {suggested_eps:.4f}")

# Method 2: Manual calculation
from scipy.spatial import KDTree
tree = KDTree(points)
distances, _ = tree.query(points, k=5)
eps = np.median(distances[:, 4]) * 1.5

# Method 3: Based on point spacing
avg_spacing = 0.05  # 5cm from LiDAR specs
eps = avg_spacing * 2.0  # 2x spacing

# Typical values:
# Dense urban: 0.02-0.05 m
# Normal urban: 0.05-0.15 m
# Sparse/rural: 0.15-0.50 m
```

### `min_samples`

Same as HDBSCAN, typically 5-20.

## Complete Building Segmentation Example

```python
from pointcloud_core import PointCloudProcessor
from clustering import segment_buildings_from_ground

# Load data
processor = PointCloudProcessor('urban_area.las')
processor.load()

# Get all points
all_points = processor.points

# Estimate ground height (multiple methods)
ground_points = processor.filter_by_classification([2])  # LAS class 2
if len(ground_points) > 0:
    ground_height = np.median(ground_points[:, 2])
else:
    ground_height = np.percentile(all_points[:, 2], 5)  # 5th percentile

print(f"Ground height: {ground_height:.2f} m")

# Segment buildings
buildings, labels = segment_buildings_from_ground(
    points=all_points,
    ground_height=ground_height,
    height_threshold=2.0,      # Buildings > 2m above ground
    min_cluster_size=100       # Minimum 100 points
)

print(f"\nFound {len(buildings)} buildings:")
for i, building in enumerate(buildings):
    pts_3d = building['points_3d']
    
    # Compute building statistics
    width = pts_3d[:, 0].max() - pts_3d[:, 0].min()
    depth = pts_3d[:, 1].max() - pts_3d[:, 1].min()
    height = pts_3d[:, 2].max() - pts_3d[:, 2].min()
    
    print(f"Building {i+1}:")
    print(f"  Points: {len(pts_3d)}")
    print(f"  Dimensions: {width:.1f} × {depth:.1f} × {height:.1f} m")
```

## Adaptive FKB-Aware Clustering

Automatically adjust parameters based on FKB standard and point density:

```python
from clustering import adaptive_clustering_for_fkb

# Calculate point density
area = (points[:, 0].max() - points[:, 0].min()) * \
       (points[:, 1].max() - points[:, 1].min())
point_density = len(points) / area

print(f"Point density: {point_density:.1f} pts/m²")

# Cluster with adaptive parameters
clusters = adaptive_clustering_for_fkb(
    points=points,
    point_density=point_density,
    fkb_standard='B'  # or 'A', 'C', 'D'
)

# Parameters are automatically set:
# FKB-A: min_cluster_size = 10 m² × density
# FKB-B: min_cluster_size = 15 m² × density  
# FKB-C: min_cluster_size = 25 m² × density
# FKB-D: min_cluster_size = 50 m² × density
```

## Filtering and Post-Processing

### Filter by Height

```python
clusterer = PointCloudClusterer(points)

# Keep only points in height range
mask = clusterer.filter_by_height(
    min_height=2.0,   # Above 2m
    max_height=50.0   # Below 50m
)

filtered_points = points[mask]
```

### Filter by Cluster Size

```python
# Get clusters above minimum size
large_clusters = clusterer.extract_clusters(min_size=200)

# Or manually filter
all_clusters = clusterer.extract_clusters()
buildings = [c for c in all_clusters if c['size'] > 100]
small_features = [c for c in all_clusters if 20 < c['size'] < 100]
```

### Remove Isolated Points

```python
labels = clusterer.cluster_hdbscan(
    min_cluster_size=50,
    min_samples=10
)

# Remove noise (label = -1)
non_noise_mask = labels != -1
clean_points = points[non_noise_mask]

print(f"Removed {(labels == -1).sum()} noise points")
```

## Multi-Scale Clustering

For hierarchical object detection:

```python
# Level 1: Coarse clustering (building groups)
clusterer_coarse = PointCloudClusterer(points)
clusterer_coarse.cluster_hdbscan(
    min_cluster_size=500,   # Large groups
    min_samples=20
)
building_groups = clusterer_coarse.extract_clusters()

# Level 2: Fine clustering (individual buildings)
all_buildings = []
for group in building_groups:
    clusterer_fine = PointCloudClusterer(group['points'])
    clusterer_fine.cluster_hdbscan(
        min_cluster_size=100,  # Individual buildings
        min_samples=10
    )
    buildings = clusterer_fine.extract_clusters()
    all_buildings.extend(buildings)

print(f"Found {len(building_groups)} groups")
print(f"Found {len(all_buildings)} individual buildings")
```

## Soft Clustering with Probabilities

HDBSCAN provides probability scores:

```python
labels = clusterer.cluster_hdbscan(...)

# Get probability for each point
probabilities = clusterer.probabilities

# Find uncertain points (low probability)
uncertain = probabilities < 0.5
print(f"{uncertain.sum()} uncertain points")

# Use for quality control
for i, cluster in enumerate(clusterer.extract_clusters()):
    cluster_mask = labels == cluster['label']
    cluster_probs = probabilities[cluster_mask]
    
    mean_prob = cluster_probs.mean()
    print(f"Cluster {i+1} confidence: {mean_prob:.2%}")
    
    if mean_prob < 0.7:
        print("  ⚠ Low confidence - review manually")
```

## Common Issues and Solutions

### Problem: Too Many Small Clusters

```python
# Solution 1: Increase min_cluster_size
labels = clusterer.cluster_hdbscan(
    min_cluster_size=100,  # Increase from 50
    min_samples=15
)

# Solution 2: Filter after clustering
clusters = clusterer.extract_clusters(min_size=100)
```

### Problem: Buildings Merged Together

```python
# Solution 1: Reduce eps (DBSCAN)
labels = clusterer.cluster_dbscan(
    eps=0.05,  # Reduce from 0.1
    min_samples=10
)

# Solution 2: Use 2D clustering only
points_2d = points[:, :2]  # Just X, Y
clusterer = PointCloudClusterer(points_2d)
# Heights don't affect clustering
```

### Problem: Parts of Building Split

```python
# Solution 1: Increase eps (DBSCAN)
labels = clusterer.cluster_dbscan(
    eps=0.15,  # Increase from 0.1
    min_samples=10
)

# Solution 2: Reduce min_samples
labels = clusterer.cluster_hdbscan(
    min_cluster_size=50,
    min_samples=5  # Reduce from 10
)
```

### Problem: Vegetation Mixed with Buildings

```python
# Solution 1: Pre-filter by classification
buildings_only = processor.filter_by_classification([6])

# Solution 2: Use geometric features
features = processor.compute_local_features(k=20)

# Buildings have high planarity
planar_mask = features['planarity'] > 0.7
building_like = points[planar_mask]

# Vegetation has high scattering
vegetation_mask = features['scattering'] > 0.6
```

## Performance Optimization

```python
# Tip 1: Use 2D clustering when possible
# 2D is ~3x faster than 3D
points_2d = points[:, :2]
clusterer = PointCloudClusterer(points_2d)

# Tip 2: Downsample first
from pointcloud_core import PointCloudProcessor
processor = PointCloudProcessor.from_points(points)
downsampled = processor.downsample_voxel(voxel_size=0.1)
# Cluster on downsampled, map back to original

# Tip 3: Process in tiles for huge datasets
def cluster_by_tiles(points, tile_size=100):
    """Cluster large dataset in spatial tiles."""
    x_min, y_min = points[:, :2].min(axis=0)
    x_max, y_max = points[:, :2].max(axis=0)
    
    all_clusters = []
    cluster_id = 0
    
    for x in np.arange(x_min, x_max, tile_size):
        for y in np.arange(y_min, y_max, tile_size):
            # Extract tile
            mask = ((points[:, 0] >= x) & (points[:, 0] < x + tile_size) &
                    (points[:, 1] >= y) & (points[:, 1] < y + tile_size))
            tile_points = points[mask]
            
            if len(tile_points) < 50:
                continue
            
            # Cluster tile
            clusterer = PointCloudClusterer(tile_points)
            clusterer.cluster_hdbscan(min_cluster_size=50)
            
            # Extract and store
            for cluster in clusterer.extract_clusters():
                cluster['label'] = cluster_id
                all_clusters.append(cluster)
                cluster_id += 1
    
    return all_clusters
```

## Validation Checklist

- [ ] Check cluster count is reasonable for scene
- [ ] Verify mean cluster size matches expected object size
- [ ] Look at outlier percentage (should be 5-20% for urban)
- [ ] Validate largest clusters aren't merged buildings
- [ ] Check smallest clusters aren't building fragments
- [ ] Review probability scores for HDBSCAN
- [ ] Compare against reference data if available

## Summary: Parameter Selection Guide

| Data Type | Algorithm | min_cluster_size | eps | min_samples |
|-----------|-----------|------------------|-----|-------------|
| Dense urban buildings | HDBSCAN | 100-200 | - | 10-20 |
| Sparse rural buildings | HDBSCAN | 50-100 | - | 5-10 |
| Uniform density | DBSCAN | - | 0.05-0.10 | 10-20 |
| Mixed data | HDBSCAN | 50-150 | - | 10-15 |
| Very noisy | HDBSCAN | 100+ | - | 20-30 |

## Further Reading

- HDBSCAN documentation: https://hdbscan.readthedocs.io/
- Parameter selection guide: https://hdbscan.readthedocs.io/en/latest/parameter_selection.html
- Original DBSCAN paper: Ester et al. (1996)
- HDBSCAN paper: Campello et al. (2013)
