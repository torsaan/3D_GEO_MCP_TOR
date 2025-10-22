# Topology Mathematics for FKB Point Cloud Extraction

## Overview

This document covers the mathematical foundations of topology operations required for FKB-compliant spatial data extraction. Topics include graph theory, spatial relationships, network algorithms, and geometric topology validation.

---

## 1. Graph Theory Fundamentals

### Basic Definitions

**Graph G = (V, E)**
- V: Set of vertices (nodes)
- E: Set of edges connecting vertices
- |V| = n (number of vertices)
- |E| = m (number of edges)

**Graph Types:**
```
Undirected Graph: edges have no direction
  (x, y) = (y, x)

Directed Graph (Digraph): edges have direction
  (x, y) ≠ (y, x)

Weighted Graph: edges have associated weights w(e)
  w: E → ℝ

Planar Graph: can be drawn on plane without edge crossings
  (Important for FKB topology - road networks, parcel boundaries)
```

### Degree of a Vertex

```
deg(v) = number of edges incident to v

For directed graphs:
  in-degree(v) = edges pointing to v
  out-degree(v) = edges pointing from v

Handshaking Lemma:
  Σ deg(v) = 2|E|
  v∈V
```

**FKB Application**: 
- Road intersections: deg(v) = 3 for T-junction, deg(v) = 4 for crossroads
- Dangling nodes: deg(v) = 1 (error in topology unless endpoint)

### Paths and Connectivity

```
Path: sequence of vertices v₁, v₂, ..., vₖ where (vᵢ, vᵢ₊₁) ∈ E

Simple Path: no repeated vertices

Cycle: path where v₁ = vₖ

Connected Graph: path exists between any two vertices

Connected Component: maximal connected subgraph
```

**Distance Metrics:**
```
d(u, v) = length of shortest path from u to v

Euclidean Distance (for spatial graphs):
  d(p₁, p₂) = √[(x₂-x₁)² + (y₂-y₁)²]

Manhattan Distance:
  d(p₁, p₂) = |x₂-x₁| + |y₂-y₁|

Geodesic Distance (network distance):
  d(u, v) = shortest path in graph
```

### Trees and Spanning Trees

```
Tree: connected graph with no cycles
  Property: |E| = |V| - 1

Forest: disjoint set of trees

Spanning Tree: tree containing all vertices of G
  Any connected graph has at least one spanning tree
```

**Minimum Spanning Tree (MST)**

**Problem**: Given weighted graph G = (V, E, w), find spanning tree T with minimum total weight:
```
min Σ w(e)
    e∈T
```

**Kruskal's Algorithm:**
```python
def kruskal_mst(vertices, edges):
    """
    Time: O(m log m) where m = |E|
    Space: O(n) for disjoint-set
    """
    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda e: e.weight)
    
    # Initialize disjoint-set (Union-Find)
    parent = {v: v for v in vertices}
    rank = {v: 0 for v in vertices}
    
    def find(v):
        if parent[v] != v:
            parent[v] = find(parent[v])  # Path compression
        return parent[v]
    
    def union(u, v):
        root_u, root_v = find(u), find(v)
        if root_u == root_v:
            return False
        
        # Union by rank
        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        elif rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        else:
            parent[root_v] = root_u
            rank[root_u] += 1
        return True
    
    mst = []
    for edge in sorted_edges:
        if union(edge.u, edge.v):
            mst.append(edge)
            if len(mst) == len(vertices) - 1:
                break
    
    return mst
```

**FKB Application**:
- Point cloud connectivity: connect scattered points into linear features
- Road network simplification: find main routes
- Skeleton extraction: compute medial axis of polygons

---

## 2. Spatial Topology Relationships

### 9-Intersection Model (DE-9IM)

**Definition**: Two geometries A and B have interior (°), boundary (∂), and exterior (⁻):

```
        B°    ∂B    B⁻
A°   [  I₁   I₂    I₃  ]
∂A   [  I₄   I₅    I₆  ]
A⁻   [  I₇   I₈    I₉  ]

Where Iᵢ ∈ {∅, 0, 1, 2} (dimension of intersection)
```

**Common Relationships:**

```
Equals:        T*F**FFF*
Disjoint:      FF*FF****
Touches:       FT******* or F**T***** or F***T****
Within:        T*F**F***
Contains:      T*****FF*
Overlaps:      T*T***T** (for areas)
Crosses:       T*T***T** (for lines)
```

**FKB Topology Rules:**
```
Adjacent Polygons: must TOUCH (share boundary)
  → T1 = ∂A ∩ ∂B ≠ ∅
  → T2 = A° ∩ B° = ∅

Road Network: segments must TOUCH at intersections
  → Endpoints must snap to within tolerance ε

Building Footprints: must be DISJOINT or TOUCH
  → Cannot OVERLAP (A° ∩ B° = ∅)
```

### Topological Invariants

**Euler Characteristic (χ)**

For planar graph embedded in 2D:
```
χ = V - E + F

V = number of vertices
E = number of edges
F = number of faces (including outer face)

For connected planar graph: χ = 2
```

**Genus (g)** - number of "holes" in surface:
```
χ = 2 - 2g

g = 0 → sphere/plane (χ = 2)
g = 1 → torus (χ = 0)
g = 2 → double torus (χ = -2)
```

**Betti Numbers** - topological features:
```
β₀ = number of connected components
β₁ = number of holes (1-cycles)
β₂ = number of voids (2-cycles)
```

---

## 3. Network Topology Algorithms

### Shortest Path Algorithms

**Dijkstra's Algorithm** (single-source shortest path, non-negative weights):

```
Time: O((|V| + |E|) log |V|) with binary heap
Space: O(|V|)

Pseudocode:
1. dist[s] = 0, dist[v] = ∞ for v ≠ s
2. Q = priority queue with all vertices
3. While Q not empty:
     u = extract_min(Q)
     For each neighbor v of u:
       alt = dist[u] + w(u, v)
       If alt < dist[v]:
         dist[v] = alt
         prev[v] = u
```

**A* Algorithm** (heuristic-guided shortest path):

```
f(n) = g(n) + h(n)

g(n) = actual cost from start to n
h(n) = estimated cost from n to goal (heuristic)

For spatial networks:
  h(n) = Euclidean distance to goal

Admissibility: h(n) ≤ true cost
  → guarantees optimal solution
```

**Floyd-Warshall** (all-pairs shortest paths):

```
Time: O(|V|³)
Space: O(|V|²)

dist[i][j] = { 0           if i = j
              { w(i,j)     if (i,j) ∈ E
              { ∞          otherwise

For k = 1 to |V|:
  For i = 1 to |V|:
    For j = 1 to |V|:
      dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

### Network Flow

**Maximum Flow Problem**: Find maximum flow from source s to sink t

```
Capacity: c(u,v) ≥ 0
Flow: f(u,v) with constraints:
  1. Capacity: f(u,v) ≤ c(u,v)
  2. Conservation: Σ f(u,v) = Σ f(v,w) for v ≠ s,t
                   u          w
  3. Skew symmetry: f(u,v) = -f(v,u)
```

**Ford-Fulkerson Method**:
```
Max-flow = value of maximum flow
Min-cut = minimum capacity cut separating s and t

Max-Flow Min-Cut Theorem:
  maximum flow value = minimum cut capacity
```

**FKB Application**:
- Water flow networks (FKB-Vann)
- Traffic capacity analysis
- Utility network optimization

---

## 4. Geometric Topology

### Simplicial Complexes

**k-Simplex**: convex hull of k+1 affinely independent points

```
0-simplex: point (vertex)
1-simplex: line segment (edge)
2-simplex: triangle (face)
3-simplex: tetrahedron
```

**Simplicial Complex K**: collection of simplices where:
1. Every face of simplex in K is in K
2. Intersection of any two simplices is a face of both

**Chain Complex** (for homology computation):
```
C₀ ←∂₁ C₁ ←∂₂ C₂ ←∂₃ ...

∂ₖ: boundary operator mapping k-chains to (k-1)-chains

Example for triangle [v₀, v₁, v₂]:
  ∂₂([v₀,v₁,v₂]) = [v₁,v₂] - [v₀,v₂] + [v₀,v₁]
```

### Delaunay Triangulation

**Definition**: Triangulation where no point is inside circumcircle of any triangle

**Properties**:
```
1. Unique (for points in general position)
2. Maximizes minimum angle (avoids sliver triangles)
3. Dual of Voronoi diagram
4. Any MST is subgraph of Delaunay triangulation
```

**Circumcircle Test** (for point d with triangle abc):
```
| xₐ  yₐ  xₐ²+yₐ²  1 |
| xᵦ  yᵦ  xᵦ²+yᵦ²  1 | > 0  ⟺  d inside circumcircle
| xᵨ  yᵨ  xᵨ²+yᵨ²  1 |
| xᵢ  yᵢ  xᵢ²+yᵢ²  1 |
```

**Bowyer-Watson Algorithm** (incremental insertion):
```
Time: O(n log n) average, O(n²) worst
Space: O(n)

For each point p:
  1. Find triangles whose circumcircle contains p
  2. Remove these triangles (creates polygon hole)
  3. Triangulate hole by connecting p to polygon vertices
```

**FKB Application**:
- TIN (Triangulated Irregular Network) for terrain
- Interpolation for DTM generation
- Spatial proximity queries

### Voronoi Diagrams

**Definition**: Partition of plane into regions, each containing points closest to a site

```
Voronoi cell for site pᵢ:
  V(pᵢ) = {x ∈ ℝ² : ||x - pᵢ|| ≤ ||x - pⱼ|| for all j}
```

**Properties**:
```
1. Dual of Delaunay triangulation
2. Each edge is perpendicular bisector of Delaunay edge
3. Voronoi vertices = circumcenters of Delaunay triangles
```

**Fortune's Algorithm** (sweep line):
```
Time: O(n log n)
Space: O(n)

Uses beach line (parabolic wavefront) and event queue
Events: site events and circle events
```

**FKB Application**:
- Road centerline extraction (medial axis = Voronoi skeleton)
- Service area computation (nearest facility)
- Natural neighbor interpolation

---

## 5. Topological Validation Rules

### Point Topology

```
1. Duplicate Points:
   ∀i,j: i≠j ⟹ ||pᵢ - pⱼ|| > ε

2. Coincident Points (within tolerance):
   If ||pᵢ - pⱼ|| < ε ⟹ snap to average position
```

### Line Topology

```
1. No Self-Intersection:
   For line L with segments sᵢ, sⱼ:
   i ≠ j ⟹ sᵢ ∩ sⱼ = ∅ or {endpoint}

2. Simple Polyline:
   vertices v₁, v₂, ..., vₙ with vᵢ ≠ vⱼ for i ≠ j (except v₁ = vₙ for closed)

3. Minimum Segment Length:
   ||vᵢ₊₁ - vᵢ|| ≥ εₘᵢₙ

4. Angle Tolerance:
   For consecutive segments sᵢ, sᵢ₊₁:
   angle(sᵢ, sᵢ₊₁) > θₘᵢₙ (typically 5-10°)
```

### Polygon Topology

```
1. Simple Polygon:
   Boundary = simple closed curve (Jordan curve)
   No self-intersections except at endpoints

2. Clockwise Orientation (exterior ring):
   Shoelace formula for signed area:
   A = ½ Σ (xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
      i=0
   A > 0 ⟹ counter-clockwise
   A < 0 ⟹ clockwise

3. Holes (interior rings):
   Opposite orientation to exterior
   Must be fully contained: hole ⊂ exterior

4. No Gaps/Overlaps (adjacent polygons):
   For adjacent P₁, P₂:
   ∂P₁ ∩ ∂P₂ = shared boundary (1D)
   P₁° ∩ P₂° = ∅
```

### Network Topology

```
1. Planar Embedding:
   Graph can be drawn without edge crossings
   (Road networks must be planar)

2. Connectivity:
   Every vertex reachable from every other
   (Or identify disconnected components)

3. Node Snapping:
   Endpoints within ε must be merged:
   ||p₁ - p₂|| < ε ⟹ p = (p₁ + p₂)/2

4. Dangles (hanging edges):
   Allowed only for dead-ends
   deg(v) = 1 ⟹ mark as terminal node

5. Pseudo-Nodes (degree-2 nodes):
   Unnecessary nodes on straight segments
   If deg(v) = 2 and angle ≈ 180° ⟹ remove v
```

---

## 6. Spatial Indexing Mathematics

### R-Tree Bounds

**Minimum Bounding Rectangle (MBR)**:
```
MBR = [xₘᵢₙ, xₘₐₓ] × [yₘᵢₙ, yₘₐₓ]

For point set P:
  xₘᵢₙ = min{pₓ : p ∈ P}
  xₘₐₓ = max{pₓ : p ∈ P}
  yₘᵢₙ = min{pᵧ : p ∈ P}
  yₘₐₓ = max{pᵧ : p ∈ P}

Area(MBR) = (xₘₐₓ - xₘᵢₙ) × (yₘₐₓ - yₘᵢₙ)
```

**Overlap**:
```
MBR₁ ∩ MBR₂ ≠ ∅ ⟺
  (x₁ₘᵢₙ ≤ x₂ₘₐₓ) ∧ (x₁ₘₐₓ ≥ x₂ₘᵢₙ) ∧
  (y₁ₘᵢₙ ≤ y₂ₘₐₓ) ∧ (y₁ₘₐₓ ≥ y₂ₘᵢₙ)
```

**Enlargement** (for insertion):
```
enlargement(MBR, p) = Area(MBR') - Area(MBR)

where MBR' = MBR ∪ {p}
```

### KD-Tree Partitioning

**Binary Space Partitioning**:
```
For dimension d, level l:
  Split dimension: l mod d

Split at median:
  left  = {p : pₓ ≤ median}
  right = {p : pₓ > median}

Balanced tree: height = O(log n)
```

**Nearest Neighbor Search**:
```
Best-First Search with priority queue:

1. Start at root, traverse to leaf containing query
2. Add leaf's points to candidates
3. Backtrack, checking if sibling could contain closer point:
   
   Distance to splitting plane: |q[d] - split_value|
   
   If |q[d] - split_value| < current_best:
     Explore sibling subtree
```

**Ball-Tree (Vantage Point Tree)**:
```
Instead of axis-aligned splits, use hyperspheres:

Split by distance to vantage point:
  Ball center: c ∈ ℝᵈ
  Ball radius: r = median({||p - c|| : p ∈ S})
  
  inner = {p : ||p - c|| ≤ r}
  outer = {p : ||p - c|| > r}
```

### Octree (3D Space Partitioning)

**Recursive Subdivision**:
```
Cube [xₘᵢₙ, xₘₐₓ] × [yₘᵢₙ, yₘₐₓ] × [zₘᵢₙ, zₘₐₓ]

Split at midpoint:
  xₘᵢₐ = (xₘᵢₙ + xₘₐₓ)/2
  yₘᵢₐ = (yₘᵢₙ + yₘₐₓ)/2
  zₘᵢₐ = (zₘᵢₙ + zₘₐₓ)/2

8 child octants:
  [xₘᵢₙ,xₘᵢₐ] × [yₘᵢₙ,yₘᵢₐ] × [zₘᵢₙ,zₘᵢₐ]  (000)
  [xₘᵢₐ,xₘₐₓ] × [yₘᵢₙ,yₘᵢₐ] × [zₘᵢₙ,zₘᵢₐ]  (100)
  ...
  [xₘᵢₐ,xₘₐₓ] × [yₘᵢₐ,yₘₐₓ] × [zₘᵢₐ,zₘₐₓ]  (111)
```

**Range Query** (points in bounding box):
```
1. If node.bbox ∩ query.bbox = ∅:
     return []

2. If node.bbox ⊂ query.bbox:
     return all points in subtree

3. If leaf node:
     return points where p ∈ query.bbox

4. Else:
     return ∪ range_query(child, query.bbox)
            child
```

---

## 7. Computational Geometry Predicates

### Orientation Test

**Problem**: Determine if point c is left/right of line ab

```
orientation(a, b, c) = sign(det|xₐ yₐ 1|)
                              |xᵦ yᵦ 1|
                              |xᵨ yᵨ 1|

Expanded form:
  = (xᵦ - xₐ)(yᵨ - yₐ) - (yᵦ - yₐ)(xᵨ - xₐ)

Result:
  > 0 ⟹ c is left of ab (counter-clockwise)
  < 0 ⟹ c is right of ab (clockwise)
  = 0 ⟹ collinear
```

### Line Segment Intersection

**Problem**: Do segments s₁ = (p₁, p₂) and s₂ = (p₃, p₄) intersect?

```
Parametric form:
  s₁(t) = p₁ + t(p₂ - p₁),  t ∈ [0,1]
  s₂(u) = p₃ + u(p₄ - p₃),  u ∈ [0,1]

Intersection ⟺
  s₁(t) = s₂(u) for some t,u ∈ [0,1]

Solve:
  t = det|p₃-p₁, p₄-p₃| / det|p₂-p₁, p₄-p₃|
  u = det|p₃-p₁, p₂-p₁| / det|p₂-p₁, p₄-p₃|

Check:
  0 ≤ t ≤ 1  and  0 ≤ u ≤ 1

Special cases:
  det = 0 ⟹ parallel segments
```

### Point in Polygon Test

**Ray Casting Algorithm**:
```
Cast ray from point p to infinity (usually along +x axis)
Count intersections with polygon edges

odd number of intersections ⟹ p inside
even number of intersections ⟹ p outside

Handle edge cases:
- Ray passes through vertex: count once
- Ray overlaps edge: doesn't count
- Point exactly on edge: consider inside
```

**Winding Number Algorithm**:
```
winding_number = Σ angle(p, vᵢ, vᵢ₊₁) / (2π)
                 i

For closed curve:
  wn = 0 ⟹ p outside
  wn ≠ 0 ⟹ p inside (handles holes correctly)
```

---

## 8. Tolerance and Precision

### Floating Point Considerations

**Machine Epsilon**:
```
ε_machine ≈ 2.22 × 10⁻¹⁶ for double precision

Relative error in arithmetic:
  fl(x ⊙ y) = (x ⊙ y)(1 + δ),  |δ| ≤ ε_machine
```

**Geometric Tolerance**:
```
Spatial tolerance: εₛₚₐₜᵢₐₗ (typically 0.001 - 0.01 for FKB)

Comparison:
  |x - y| < εₛₚₐₜᵢₐₗ ⟹ x ≈ y

For FKB-A: εₛₚₐₜᵢₐₗ = 0.10 m (10 cm)
For FKB-B: εₛₚₐₜᵢₐₗ = 0.20 m (20 cm)
```

### Snap Rounding

**Problem**: Convert floating-point coordinates to integer grid

```
Grid resolution: g (e.g., 0.001 for millimeter precision)

Snap function:
  snap(x) = round(x / g) × g

For point p = (x, y):
  p' = (snap(x), snap(y))

Preserves topology if g < ε_spatial / 2
```

### Robust Predicates

**Shewchuk's Exact Arithmetic**:
```
For orientation test, use adaptive precision:

1. Fast filter: compute with double precision
   If |result| > ε_bound ⟹ return sign(result)

2. Exact filter: compute with exact arithmetic
   (using expansion arithmetic, no rounding errors)
   Return exact sign

Guarantees correct topology decisions
```

---

## 9. FKB-Specific Topology Rules

### Shared Geometry (Delt Geometri)

**Mathematical Definition**:
```
For adjacent features F₁, F₂:

Shared boundary: B_shared = ∂F₁ ∩ ∂F₂

Requirements:
1. B_shared is 1-dimensional (curve)
2. B_shared stored once, referenced by both
3. Vertices must match exactly (within ε)

Topological consistency:
  orientation(B in F₁) = -orientation(B in F₂)
```

### Node Matching

**Snap Tolerance**:
```
For FKB-A: ε_snap = 3 × σ ≈ 3 × 0.10 = 0.30 m

Node matching:
  If ||n₁ - n₂|| < ε_snap ⟹ merge to n̄
  
  n̄ = (n₁ + n₂) / 2  (average position)

Update all incident edges to reference n̄
```

### Polygon Closure

**Closure Tolerance**:
```
For closed polygon P with vertices v₁, ..., vₙ:

Closure check:
  ||v₁ - vₙ|| < ε_closure

If fails:
  1. Force closure: vₙ = v₁
  2. Adjust midpoint if error large:
     vₙ₋₁, vₙ = adjust_to_close(vₙ₋₁, vₙ, v₁)
```

### Gap and Overlap Detection

**Gap Detection** (for adjacent polygons):
```
P₁ and P₂ should share boundary

Gap exists if:
  dist(∂P₁, ∂P₂) > ε_gap

Quantify gap:
  gap_area = area(convex_hull(∂P₁ ∪ ∂P₂)) - area(P₁) - area(P₂)
```

**Overlap Detection**:
```
Overlap = P₁ ∩ P₂

Should have:
  dim(P₁ ∩ P₂) ≤ 1  (intersection is at most a curve)

If dim(P₁ ∩ P₂) = 2:
  overlap_area = area(P₁ ∩ P₂)
  Flag as error if overlap_area > ε_area
```

---

## 10. Implementation Formulas

### Douglas-Peucker Simplification

**Recursive polyline simplification**:
```
function simplify(points, ε):
  if len(points) ≤ 2:
    return points
  
  # Find point farthest from line(first, last)
  d_max = 0
  index = 0
  for i = 2 to len(points)-1:
    d = perpendicular_distance(points[i], line(points[1], points[n]))
    if d > d_max:
      d_max = d
      index = i
  
  # If max distance > ε, split and recurse
  if d_max > ε:
    left = simplify(points[1:index+1], ε)
    right = simplify(points[index:n], ε)
    return left[:-1] + right
  else:
    return [points[1], points[n]]

Perpendicular distance formula:
  d(p, line(a,b)) = |det|xᵦ-xₐ yᵦ-yₐ|| / ||b-a||
                        |xₐ-xₚ yₐ-yₚ|
```

### Polygon Area (Shoelace Formula)

```
For polygon with vertices (x₁,y₁), ..., (xₙ,yₙ):

A = ½|Σ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)|
     i=1

Vectorized form:
  A = ½|det|x₁ x₂ ... xₙ||
           |y₁ y₂ ... yₙ|
  
Signed area (orientation):
  A_signed = ½ Σ(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
  
  A_signed > 0 ⟹ counter-clockwise
  A_signed < 0 ⟹ clockwise
```

### Polygon Centroid

```
For simple polygon:

Cₓ = (1/6A) Σ(xᵢ + xᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
            i=1

Cᵧ = (1/6A) Σ(yᵢ + yᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
            i=1

where A = signed area from shoelace formula
```

### Line-Line Distance

```
For line segments s₁ = (p₁, p₂) and s₂ = (p₃, p₄):

Closest points:
  s₁(t*) = p₁ + t*(p₂ - p₁)
  s₂(u*) = p₃ + u*(p₄ - p₃)

Solve:
  t* = det|p₃-p₁, d₂| / det|d₁, d₂|
  u* = det|p₃-p₁, d₁| / det|d₁, d₂|

where d₁ = p₂ - p₁, d₂ = p₄ - p₃

Clamp to [0,1] for segment distance:
  t* = max(0, min(1, t*))
  u* = max(0, min(1, u*))

Distance:
  d = ||s₁(t*) - s₂(u*)||
```

---

## References & Further Reading

### Graph Theory
- Diestel, R. (2017). *Graph Theory* (5th ed.)
- Bondy, J. A., & Murty, U. S. R. (2008). *Graph Theory*

### Computational Geometry
- de Berg, M., et al. (2008). *Computational Geometry: Algorithms and Applications* (3rd ed.)
- O'Rourke, J. (1998). *Computational Geometry in C* (2nd ed.)

### Spatial Topology
- Egenhofer, M. J., & Herring, J. (1990). *Categorizing Binary Topological Relations*
- ISO 19107:2019 *Geographic Information — Spatial Schema*

### Algorithms
- Cormen, T. H., et al. (2009). *Introduction to Algorithms* (3rd ed.)
- Preparata, F. P., & Shamos, M. I. (1985). *Computational Geometry*

### FKB Standards
- Kartverket (2023). *FKB 5.0 Specification*
- SOSI Standard Documentation: https://www.kartverket.no/standard/sosi/

---

## Quick Reference


**Time Complexities:**
```
Kruskal MST:        O(m log m)
Dijkstra:           O((n+m) log n)
Delaunay:           O(n log n)
Voronoi:            O(n log n)
KD-Tree build:      O(n log n)
KD-Tree query:      O(log n) average
R-Tree query:       O(log n) average
Point-in-polygon:   O(n)
Line intersection:  O(1)
```

**Spatial Predicates:**
```
Equals:      A = B
Disjoint:    A ∩ B = ∅
Touches:     ∂A ∩ ∂B ≠ ∅, A° ∩ B° = ∅
Within:      A ⊂ B
Contains:    B ⊂ A
Overlaps:    A° ∩ B° ≠ ∅, A ⊄ B, B ⊄ A
Crosses:     dim(A ∩ B) < max(dim(A), dim(B))
```
