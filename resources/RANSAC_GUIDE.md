# RANSAC: Practical Guide for Pointcloud Fitting

## What is RANSAC?

RANSAC (Random Sample Consensus) is the go-to algorithm for robust geometric fitting when your data contains outliers. It's essential for FKB pointcloud processing because real-world LiDAR data always has noise, vegetation, and other outliers.

## How RANSAC Works

1. **Sample**: Randomly pick minimum points needed (3 for plane, 2 for line)
2. **Fit**: Compute model from these points
3. **Score**: Count how many points fit the model (inliers)
4. **Repeat**: Do steps 1-3 many times
5. **Best**: Keep the model with most inliers
6. **Refine**: Optionally refit using all inliers

## When to Use RANSAC

✅ **Use RANSAC when:**
- Data has outliers (20-50% outliers is fine)
- You need robust plane/line detection
- Building roof segmentation
- Ground plane removal
- Facade detection

❌ **Don't use RANSAC when:**
- Data is clean (<5% outliers) → Use least squares instead
- Need all geometries at once → Use region growing
- Real-time processing → Consider simpler methods first

## Plane Fitting

### Basic Usage

```python
from ransac_fitting import RANSACFitter

# Your pointcloud (N, 3)
points = load_building_points()

# Create fitter
fitter = RANSACFitter(points)

# Fit plane
plane_model, inliers = fitter.fit_plane(
    distance_threshold=0.02,  # 2cm tolerance
    ransac_n=3,               # 3 points define plane
    num_iterations=1000       # Usually enough
)

# plane_model = [a, b, c, d]
# Plane equation: ax + by + cz + d = 0
# Normal vector: [a, b, c]

print(f"Found plane with {len(inliers)} inliers")
print(f"Normal: [{plane_model[0]:.3f}, {plane_model[1]:.3f}, {plane_model[2]:.3f}]")
```

### Choosing Distance Threshold

The distance threshold is **the most important parameter**. Match it to your FKB standard:

```python
# FKB Standard → Distance Threshold
fkb_thresholds = {
    'A': 0.01,  # 1-2cm for precise urban mapping
    'B': 0.02,  # 2-4cm for standard urban  
    'C': 0.05,  # 5-10cm for rural
    'D': 0.10   # 10-15cm for wilderness
}

# Too small → Not enough inliers, unstable
# Too large → Accepts outliers, poor fit

# Rule of thumb: 2-3× expected noise level
threshold = 2.5 * noise_std_dev
```

### How Many Iterations?

The formula: `k = log(1-p) / log(1-w^n)`

Where:
- `p` = success probability (usually 0.99)
- `w` = inlier ratio (estimate: 0.3-0.7)
- `n` = minimum sample size (3 for plane)

```python
import math

def compute_iterations(inlier_ratio, success_prob=0.99, min_sample=3):
    """Calculate required RANSAC iterations."""
    w = inlier_ratio
    p = success_prob
    n = min_sample
    
    k = math.log(1 - p) / math.log(1 - w**n)
    return int(k) + 1

# Examples:
# 50% inliers → 35 iterations
# 30% inliers → 227 iterations  
# 70% inliers → 11 iterations

# In practice: 500-1000 iterations is safe default
```

## Multiple Plane Detection

Buildings often have multiple roof sections. Detect them sequentially:

```python
from ransac_fitting import RANSACFitter

fitter = RANSACFitter(building_points)

# Detect up to 5 planes
planes = fitter.fit_multiple_planes(
    max_planes=5,
    distance_threshold=0.03,
    min_inliers=100  # Skip small planes
)

for i, plane in enumerate(planes):
    print(f"Plane {i+1}:")
    print(f"  Points: {plane['n_inliers']}")
    print(f"  Model: {plane['model']}")
    
    # Get the actual points
    inlier_points = plane['inliers']
```

## MSAC: Better than RANSAC

MSAC (M-estimator SAC) is an improved variant that uses **squared error** instead of counting inliers:

```python
from ransac_fitting import MSACFitter

fitter = MSACFitter(points)
plane_model, inliers = fitter.fit_plane_msac(
    distance_threshold=0.02,
    num_iterations=1000
)

# MSAC advantages:
# ✓ More accurate parameters
# ✓ Better in noise
# ✓ Same speed as RANSAC
# 
# Use MSAC when accuracy matters (FKB-A, FKB-B)
# Use RANSAC when speed matters
```

## Line Fitting in 3D

For edges, ridges, or linear features:

```python
fitter = RANSACFitter(edge_points)

point_on_line, direction, inliers = fitter.fit_line_3d(
    distance_threshold=0.05,
    num_iterations=1000
)

# Parameterize line: P(t) = point_on_line + t * direction
# direction is unit vector

# Example: Get points along line
t_values = np.linspace(0, 10, 100)
line_points = point_on_line + t_values[:, None] * direction
```

## Refinement: Least Squares After RANSAC

After RANSAC finds inliers, improve the fit:

```python
# 1. RANSAC to find inliers
plane_model, inliers = fitter.fit_plane(distance_threshold=0.02)

# 2. Refine using least squares on inliers only
refined_model = fitter.refine_plane_least_squares(inliers)

# This gives:
# ✓ More accurate parameters
# ✓ Better geometric properties
# ✓ Minimal extra cost
```

## Computing Quality Metrics

Check if your plane meets FKB standards:

```python
# Get residuals (distances to plane)
residuals = fitter.compute_plane_residuals(plane_model)

# Root Mean Square Error
rmse = np.sqrt(np.mean(residuals[inliers]**2))

# Standard deviation
std_dev = np.std(residuals[inliers])

# Max error
max_error = np.max(residuals[inliers])

print(f"RMSE: {rmse*100:.2f} cm")
print(f"Std Dev: {std_dev*100:.2f} cm")
print(f"Max Error: {max_error*100:.2f} cm")

# FKB-B requires std dev < 5cm
if std_dev < 0.05:
    print("✓ Meets FKB-B standard")
```

## Common Issues and Solutions

### Problem: No Inliers Found

```python
# Check 1: Is threshold too small?
threshold = fitter.compute_plane_residuals(plane_model).min()
print(f"Minimum residual: {threshold:.4f}")
# If < 1mm, threshold might be too tight

# Check 2: Is data planar?
from pointcloud_core import PointCloudProcessor
processor = PointCloudProcessor.from_points(points)
features = processor.compute_local_features(k=20)
print(f"Mean planarity: {features['planarity'].mean():.3f}")
# Should be > 0.5 for planar surfaces

# Solution: Increase threshold or check data
```

### Problem: Too Many Iterations, Still Bad Fit

```python
# This means inlier ratio is very low
# Solutions:

# 1. Pre-filter obvious outliers
from pointcloud_core import PointCloudProcessor
processor = PointCloudProcessor.from_points(points)
clean, _ = processor.remove_outliers_statistical(
    nb_neighbors=20,
    std_ratio=2.0
)

# 2. Use region growing instead
# Better for highly contaminated data (>70% outliers)
```

### Problem: Plane is Unstable/Jumping

```python
# Increase iterations for stability
plane_model, inliers = fitter.fit_plane(
    num_iterations=5000,  # More iterations = more stable
    distance_threshold=0.02
)

# Or use MSAC
fitter_msac = MSACFitter(points)
plane_model, inliers = fitter_msac.fit_plane_msac(...)
# MSAC is more stable than RANSAC
```

## Real-World Example: Building Roof Extraction

```python
from pointcloud_core import PointCloudProcessor
from ransac_fitting import extract_building_planes
import numpy as np

# Load building
processor = PointCloudProcessor('building.las')
processor.load()
building_points = processor.filter_by_classification([6])

# Extract planes with FKB-B parameters
planes = extract_building_planes(
    building_points,
    fkb_standard='B'  # Uses 4cm threshold
)

print(f"Detected {len(planes)} roof sections")

# Validate each plane
for i, plane in enumerate(planes):
    # Compute quality metrics
    fitter = RANSACFitter(plane['inliers'])
    residuals = fitter.compute_plane_residuals(plane['model'])
    
    rmse = np.sqrt(np.mean(residuals**2))
    
    print(f"\nRoof section {i+1}:")
    print(f"  Points: {len(plane['inliers'])}")
    print(f"  RMSE: {rmse*100:.2f} cm")
    print(f"  Normal: {plane['model'][:3]}")
    
    # Check if horizontal (flat roof) or sloped
    angle = np.degrees(np.arccos(abs(plane['model'][2])))
    if angle < 10:
        print(f"  Type: Flat roof ({angle:.1f}° from horizontal)")
    else:
        print(f"  Type: Sloped roof ({angle:.1f}° from horizontal)")
```

## Advanced: Custom Distance Functions

Sometimes you want different distance metrics:

```python
class CustomRANSAC(RANSACFitter):
    def point_to_plane_distance_weighted(self, plane_model, weights):
        """Custom weighted distance."""
        distances = self.compute_plane_residuals(plane_model)
        return distances * weights

# Use when:
# - Points have different confidence levels
# - Want to weight by intensity, return number, etc.
```

## Performance Tips

```python
# Tip 1: Downsample first for speed
from pointcloud_core import PointCloudProcessor
processor = PointCloudProcessor.from_points(points)
downsampled = processor.downsample_voxel(voxel_size=0.05)
# 10x fewer points = 10x faster RANSAC

# Tip 2: Use Open3D's optimized implementation
import open3d as o3d
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(points)
plane_model, inliers = pcd.segment_plane(
    distance_threshold=0.02,
    ransac_n=3,
    num_iterations=1000
)
# Open3D is C++ implementation = fast

# Tip 3: Reduce iterations if time-critical
# Even 100 iterations often works well
```

## Summary Checklist

- [ ] Choose threshold based on FKB standard
- [ ] Use 500-1000 iterations (or compute from inlier ratio)
- [ ] Validate RMSE and std dev meet accuracy requirements
- [ ] Refine with least squares for final parameters
- [ ] Use MSAC for high-accuracy applications (FKB-A, FKB-B)
- [ ] Pre-filter outliers if inlier ratio < 30%
- [ ] Downsample dense clouds for speed

## Further Reading

- Original RANSAC paper: Fischler & Bolles (1981)
- MSAC: Torr & Zisserman (2000)
- MLESAC: Torr & Zisserman (2000) - even better, probabilistic
- Open3D RANSAC docs: http://www.open3d.org/docs/latest/tutorial/geometry/pointcloud.html
