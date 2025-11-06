# FKB Data Validation Checklist

*Version: 1.0*
*Date: 2025-11-04*
*Based on: FKB 5.1 Specifications*

## Purpose

This checklist provides systematic validation steps for FKB data before delivery. Each check references specific rules from the extracted FKB specifications.

## How to Use This Checklist

1. **Work through sections sequentially** - Each section builds on previous validations
2. **Check all boxes** - Even if automated, verify results
3. **Document failures** - Record rule ID and object ID for each failure
4. **Priority levels:**
   - CRITICAL (must pass)
   - HIGH (should pass)
   - MEDIUM (recommended)
   - LOW (nice to have)

---

## Validation Workflow

```
File Format → Geometry → Attributes → Topology → Quality → References → Report
```

**Estimated time:**
- Small dataset (<1K objects): 30 min
- Medium (1K-10K): 2-4 hours
- Large (>10K): Use automated tools + sampling

---

## Section 1: File Format Validation (SOSI)

**Priority: CRITICAL**
**Reference:** `08-SOSI-FORMAT-RULES.yaml`

### 1.1 Header Validation

- [ ] `.HODE` section present and at nesting level 0
- [ ] `.HODE` contains all mandatory elements:
  - [ ] `.TEGNSETT UTF-8`
  - [ ] `.KOORDSYS [22|23|25]` (valid SOSI coordinate system code)
    - 22 = EUREF89 UTM32 (Trøndelag and south)
    - 23 = EUREF89 UTM33 (Nordland and Troms)
    - 25 = EUREF89 UTM35 (Finnmark)
  - [ ] `.VERT-DATUM [NN2000|NN1954|"ikke angitt"]`
  - [ ] `.SOSI-VERSJON 5.0`
  - [ ] `.OBJEKTKATALOG [catalog name and version]` (e.g., "FKBBygning 5.0.1")

**Validation commands:**
```bash
# Check header
head -20 file.sos | grep "^\.HODE\|^\.\.TEGNSETT\|^\.\.KOORDSYS"

# Validate encoding
file -i file.sos | grep "utf-8"
```

**Rule References:** SOSI-FORMAT-001 to SOSI-FORMAT-004

### 1.2 File Structure

- [ ] Proper nesting: Number of dots indicates hierarchy level
  - Level 0: `.HODE`, `.PUNKT`, `.KURVE`, `.FLATE`
  - Level 1: Header elements (`.TEGNSETT`, `.KOORDSYS`)
  - Level 2: Object attributes (`..OBJTYPE`, `..KVALITET`)
  - Level 3: Nested attributes (`...DATAFANGSTMETODE`, `...LOKALID`)
- [ ] All objects start with `.[GEOMETRY_TYPE] [seq]:` at level 0
- [ ] All objects have `..OBJTYPE [value]` attribute
- [ ] No illegal characters in text fields
- [ ] File ends properly (no truncation)
- [ ] UTF-8 encoding throughout

**Rule References:** SOSI-FORMAT-001, SOSI-FORMAT-002, SOSI-FORMAT-004

### 1.3 Coordinate Format

- [ ] Coordinates are integers (centimeters)
- [ ] Format: `X Y [Z]` (space-separated)
- [ ] Values reasonable for declared CRS:
  - X (Easting): ~-200000 to 1100000 (in cm, convert by ×100)
  - Y (Northing): ~6400000 to 7900000 (in cm)
  - Z (Height): Reasonable for Norway (-500m to 3000m typical)
- [ ] No missing or malformed coordinates
- [ ] All coordinates in geometry have same dimension (2D or 3D)

**Validation:**
```python
# Coordinates should be 6-7 digits for Norwegian CRS
# Example: 7034127981 567190174 (in cm)
# = 70341.27981 m East, 5671.90174 m North
```

**Rule References:** SOSI-FORMAT-003, SOSI-FORMAT-008, SOSI-FORMAT-009

---

## Section 2: Geometry Validation

**Priority: CRITICAL**
**Reference:** `02-GEOMETRIC-RULES.yaml` sections GR-001 to GR-006

### 2.1 Basic Geometry Validity

**For ALL geometries:**
- [ ] Coordinates within valid CRS bounds
- [ ] No NaN or Inf values
- [ ] Coordinate precision appropriate (integer cm)
- [ ] Geometry type matches `..OBJTYPE` specification

**For PUNKT:**
- [ ] Single coordinate pair/triple (`..NØ` or `..NØH`)
- [ ] X, Y (and Z if 3D) all present

**For KURVE:**
- [ ] At least 2 points
- [ ] No consecutive duplicate points (except closure)
- [ ] Line segments not zero-length
- [ ] No degenerate lines (all points collinear with length ~0)
- [ ] No self-intersections (line crossing itself)
- [ ] No self-overlaps (line segments overlapping)

**For FLATE:**
- [ ] At least 3 unique points (4 with closure)
- [ ] Closed: First point == Last point
- [ ] No self-intersections
- [ ] No self-overlaps
- [ ] Area > 0 (non-degenerate)
- [ ] Vertices ordered correctly (CCW for exterior, CW for holes in GML)

**Validation tools:**
```python
# Using Shapely
from shapely.geometry import Point, LineString, Polygon

# Check validity
assert polygon.is_valid  # False if self-intersecting
assert polygon.is_simple  # False if self-overlapping

# Check closure
coords = list(polygon.exterior.coords)
assert coords[0] == coords[-1]

# Check area
assert polygon.area > 0
```

**Rule References:** GR-001, GR-004, GR-005, GR-006

### 2.2 Geometry Type Compliance

- [ ] Each object has correct geometry type per specification
- [ ] PUNKT objects use `..NØ` or `..NØH`
- [ ] KURVE objects use `..NØH` (or `..NØ` for 2D)
- [ ] FLATE objects use `..REF` + representative point
- [ ] No multi-geometries - ILLEGAL in FKB:
  - NO GM_MultiPoint
  - NO GM_MultiCurve
  - NO GM_MultiSurface
  - NO GM_CompositeCurve
  - NO circular arcs (must be densified)

**Reference:** `01-MANDATORY-ATTRIBUTES.yaml` / geometry_type field for each object

**Rule:** GR-001 - Only simple geometries allowed

### 2.3 Coordinate System Consistency

- [ ] `.KOORDSYS` matches regional assignment:
  - Trøndelag and south: UTM32 (code 22)
  - Nordland and Troms: UTM33 (code 23)
  - Finnmark: UTM35 (code 25)
- [ ] Coordinates within expected range for specified zone
- [ ] Vertical datum appropriate (NN2000 preferred)

**Rule References:** META-010, SOSI header requirements

---

## Section 3: Attribute Validation

**Priority: CRITICAL for mandatory, HIGH for optional**
**Reference:** `01-MANDATORY-ATTRIBUTES.yaml`, `05-METADATA-RULES.yaml`

### 3.1 Common Mandatory Attributes (ALL Objects)

- [ ] `OPPDATERINGSDATO` present, format: YYYYMMDDHHMMSS
  - Example: 20210929133801
  - Must be >= DATAFANGSTDATO
- [ ] `DATAFANGSTDATO` present, format: YYYYMMDD
  - Example: 20210924
  - Should be date when feature was observed
- [ ] `..IDENT` block present with:
  - [ ] `...LOKALID` - valid UUID v4 format
    - Example: "5e1d42bb-fd1c-4a58-92dc-aa0b3fadf57d"
  - [ ] `...NAVNEROM` - valid URI format
    - Example: "http://data.geonorge.no/SOSI/FKB-Bygning/5.0"
- [ ] `..KVALITET` block present (see Section 3.2)

**Validation:**
```python
import re
import uuid
from datetime import datetime

# UUID validation
try:
    uuid.UUID(lokalid)
except ValueError:
    # Invalid UUID

# Date validation
datafangst = datetime.strptime(datafangstdato, '%Y%m%d')
oppdatering = datetime.strptime(oppdateringsdato, '%Y%m%d%H%M%S')
assert datafangst.date() <= oppdatering.date()

# URI validation
assert navnerom.startswith('http://data.geonorge.no/')
```

**Rule References:** META-001, META-003, META-004

### 3.2 KVALITET Block Validation

**Always required:**
- [ ] `..KVALITET` block exists (2-dot level)
- [ ] `...DATAFANGSTMETODE` present with valid code (3-dot level)

**Valid DATAFANGSTMETODE codes:**
- `byg` - Som bygget (as-built from plans + verification)
- `ukj` - Ukjent (unknown)
- `pla` - Plandata (plan data, not verified)
- `sat` - Satellittmålt (GNSS measured)
- `gen` - Generert (generated from point cloud)
- `fot` - Fotogrammetri (photogrammetry)
- `dig` - Digitalisert (digitized from orthophoto/map)
- `lan` - Landmålt (surveyed)

**Conditional requirements (Reference: `06-SPECIAL-CASES.md`):**

If `DATAFANGSTMETODE = 'fot'` (photogrammetry):
- [ ] `...NØYAKTIGHET` present (integer, cm)
  - Should match standard deviation requirement for accuracy class
  - Example: 120 (= 1.20 m)
- [ ] `...SYNBARHET` present (0/1/2/3)
  - 0 = Fullt ut synlig (fully visible)
  - 1 = Dårlig gjenfinnbar (poorly recognizable)
  - 2 = Middels synlig (moderately visible)
  - 3 = Ikke synlig (not visible)

If object has Z coordinates (3D geometry):
- [ ] Consider `...DATAFANGSTMETODEHØYDE` (if different from horizontal)
- [ ] Consider `...H-NØYAKTIGHET` (vertical accuracy in cm)

**Constraint:**
- [ ] `DATAFANGSTMETODEHØYDE` cannot be 'dig' (META-007)

**Rule References:** META-001, META-002, META-005, META-007

### 3.3 Object-Specific Mandatory Attributes

For **each object type**, verify ALL mandatory attributes are present.

**Example validation for Bygning:**
- [ ] `posisjon` (PUNKT geometry) - mandatory
- [ ] `bygningsnummer` (integer or UUID per municipality)
- [ ] `bygningstype` (code from register.geonorge.no)
- [ ] `bygningsstatus` (code list value)
- [ ] `kommunenummer` (4-digit code)
- [ ] `medium` (T=på terreng, usually) - varies by context

**Approach:**
```python
# Get mandatory attributes for object type from specification
mandatory_attrs = spec['object_types'][obj_type]['mandatory_attributes']

# Check each one present
for attr in mandatory_attrs:
    if attr['name'] not in object_attributes:
        raise ValidationError(f"Missing mandatory attribute: {attr['name']}")
```

**Reference:** `01-MANDATORY-ATTRIBUTES.yaml` - Search for specific object type

### 3.4 Attribute Value Validation

- [ ] Code list values valid (check register.geonorge.no)
- [ ] Numeric values within specified ranges
- [ ] Text fields not exceeding length limits (SOSI datatype lengths)
- [ ] Date/DateTime formats correct
- [ ] UUIDs properly formatted (with hyphens)
- [ ] URIs follow pattern: `http://data.geonorge.no/[S]FKB/...`

### 3.5 Date Logic Validation

- [ ] `DATAFANGSTDATO ≤ OPPDATERINGSDATO` (META-003)
- [ ] If `VERIFISERINGSDATO` present: reasonable relationship with other dates
- [ ] If `SLUTTDATO` present: `SLUTTDATO ≥ DATAFANGSTDATO`
- [ ] Dates not in future (unless explicitly for planning)
- [ ] Dates not unreasonably old (data should be current for FKB)

**Rule:** META-003, META-006

---

## Section 4: Topology Validation

**Priority: CRITICAL for shared geometry, HIGH for others**
**Reference:** `02-GEOMETRIC-RULES.yaml`, `04-TOPOLOGY-RULES.yaml`

### 4.1 Shared Geometry (Type 2 Flater) - MOST CRITICAL

**This is the most important topology rule in FKB!**

For objects with "delt geometri" (shared boundaries):
- Bygning (with område)
- Kjørebane
- Elv (when FLATE)
- Innsjø
- HavEllerHavarm
- VegKjørende
- Fortau
- KaiBrygge
- [see `04-TOPOLOGY-RULES.yaml` for full list]

**Validation steps:**
1. [ ] Object has association to `avgrensningsobjekter`
2. [ ] Association role name starts with `avgrensesAv*`
3. [ ] All boundary objects exist (references resolve via `..REF`)
4. [ ] **CRITICAL:** `område = union(all boundary objects)`
   - Tolerance: Use 2 × NØYAKTIGHET (2 × standard deviation)
   - Must be topologically equal
   - No gaps between boundaries
   - No overlaps of boundaries

**Validation code:**
```python
# Pseudo-code for most critical check
area_geom = object.get_geometry('område')
boundary_refs = object.get_refs()  # Parse ..REF :1 :2 :-3
boundary_geoms = [get_geometry(ref) for ref in boundary_refs]

# Handle direction (negative refs = reverse)
for i, ref in enumerate(boundary_refs):
    if ref < 0:  # Negative reference
        boundary_geoms[i] = reverse_coords(boundary_geoms[i])

union_boundaries = unary_union(boundary_geoms)
tolerance = object.KVALITET.NØYAKTIGHET * 2 / 100  # cm to m, × 2

# Check topological equality
assert area_geom.buffer(0).equals_exact(union_boundaries.buffer(0), tolerance)
```

**Rule:** TOPO-CRITICAL-001 (Most important rule in FKB!)

**Failure examples:**
- Gap between Grunnmur segments
- Bygning område doesn't match union of Grunnmur + Fasadelinje
- Overlap between boundary objects

### 4.2 Point-in-Polygon Containment

For objects with both PUNKT and FLATE geometry:
- [ ] `posisjon` (point) is inside `område` (polygon)
- [ ] OR `senterpunkt` inside `område`
- [ ] Representative point in `.FLATE` structure inside surface

**Validation:**
```python
# Allow small tolerance for points on boundary
tolerance = NØYAKTIGHET / 100  # cm to m
assert point_geom.within(area_geom.buffer(tolerance))
```

**Rule:** TOPO-CONTAIN-001, TOPO-CONTAIN-003

**Applies to:** Bygning, Kjørebane, and others with dual geometry

### 4.3 Network Connectivity (if applicable)

For road/utility networks:
- [ ] Veglenker connect at Knutepunkt (nodes)
- [ ] Endpoints snap within tolerance (recommend 2 × standardavvik)
- [ ] No illegal dangling ends:
  - OK: Dataset boundary
  - OK: Cul-de-sac (marked appropriately)
  - OK: Ferry terminal
  - NOT OK: Random endpoint in middle of network
- [ ] Network forms connected graph (if expected)
- [ ] No illegal crossings except:
  - At nodes (knutepunkt)
  - Different MEDIUM values (over/under)

**Reference:** `04-TOPOLOGY-RULES.yaml` / network_topology

**Validation tools:**
```python
# Using NetworkX for connectivity analysis
import networkx as nx

G = nx.Graph()
# Add edges from Veglenker
for link in veglenker:
    G.add_edge(link.start_node, link.end_node)

# Find connected components
components = list(nx.connected_components(G))
# Should be 1 component (or justify multiple)

# Find dangling ends
for node in G.nodes():
    if G.degree(node) == 1:
        # Check if legitimate terminator
        pass
```

**Rule References:** TOPO-NETWORK-001 to TOPO-NETWORK-005

### 4.4 Coverage Validation (if applicable)

For full-coverage datasets (Arealbruk, Arealressurs):
- [ ] No gaps between adjacent polygons
  - Tolerance: Gap <= accuracy class standard deviation
- [ ] No overlaps between polygons (same OBJTYPE, same MEDIUM)
- [ ] Complete coverage of defined area
- [ ] Shared boundaries between adjacent polygons are identical

**Validation:**
```sql
-- Using PostGIS
-- Check for gaps
SELECT ST_Union(geom) FROM polygons;
-- Should cover entire area with no holes

-- Check for overlaps
SELECT a.lokalid, b.lokalid
FROM polygons a, polygons b
WHERE a.lokalid < b.lokalid
  AND a.medium = b.medium
  AND ST_Overlaps(a.geom, b.geom);
-- Should return no rows
```

**Rule References:** TOPO-COVERAGE-001, TOPO-COVERAGE-002, TOPO-COVERAGE-003

---

## Section 5: Quality/Accuracy Validation

**Priority: HIGH**
**Reference:** `03-ACCURACY-STANDARDS.yaml`

### 5.1 Accuracy Class Validation

- [ ] `NØYAKTIGHET` value matches specification requirements
- [ ] Accuracy appropriate for FKB standard (A/B/C/D)
- [ ] Accuracy appropriate for nøyaktighetsklasse (1/2/3/4)

**Reference table (FKB-B example):**

| Klasse | Object Type | Grunnriss (sys/std) | Høyde (sys/std) |
|--------|-------------|---------------------|-----------------|
| 1 | Svært veldefinerte | 5/15 cm | 5/15 cm |
| 2 | Veldefinerte | 6/20 cm | 6/20 cm |
| 3 | Uskarpe | 10/35 cm | 10/35 cm |
| 4 | Diffuse | 15/55 cm | 15/50 cm |

**Check:**
```python
# NØYAKTIGHET should match or be better than standardavvik requirement
# Example: FKB-B Klasse 2 should have NØYAKTIGHET ≤ 20 cm
if nøyaktighet > required_standard_deviation:
    warn(f"Accuracy {nøyaktighet} exceeds requirement {required_standard_deviation}")
```

**Rule Reference:** META-002

### 5.2 FKB 5.1 Quality Rules

- [ ] **ACC-001:** Systematisk avvik ≤ 1/3 × standardavvik
  - NOTE: Cannot validate on data without control points
  - FKB 5.0 data not subject to this rule (version-specific)
- [ ] **ACC-002:** Grove feil (>3σ) < 1% of points
  - Requires comparison to reference data
- [ ] **ACC-003:** `NØYAKTIGHET` represents standard deviation
  - FKB 5.1: True standard deviation
  - FKB 5.0: Similar to RMS (check REGISTRERINGSVERSJON)

**Validation:** Requires ground control points or independent check measurements

**Reference:** `03-ACCURACY-STANDARDS.yaml`, `07-CONFLICTS-AMBIGUITIES.md` (version differences)

### 5.3 Line Simplification (Pilhøyde)

- [ ] Maximum perpendicular deviation from original ≤ `NØYAKTIGHET` value
- [ ] Critical points preserved:
  - Building corners
  - Sharp angles
  - Network connection points
  - High curvature points
- [ ] Smooth curves not over-simplified

**Validation:**
```python
from shapely.geometry import LineString

# Douglas-Peucker or similar
simplified = original_line.simplify(tolerance=NØYAKTIGHET/100)

# Check max deviation
max_deviation = hausdorff_distance(original_line, simplified)
assert max_deviation <= NØYAKTIGHET / 100  # cm to m
```

**Rule:** GR-003 (Pilhøyde constraint)

---

## Section 6: Association/Reference Validation

**Priority: CRITICAL**
**Reference:** `04-TOPOLOGY-RULES.yaml` / association_constraints

### 6.1 Reference Integrity

- [ ] All `.REF` references resolve to existing objects in file
- [ ] Reference format correct: `:[sequence_number]`
  - Positive: `:1`, `:2`, etc. (follow direction)
  - Negative: `:-1`, `:-2`, etc. (reverse direction)
- [ ] Referenced objects have correct OBJTYPE
- [ ] Bidirectional associations consistent (if applicable)

**Validation:**
```python
# Build object index by sequence number
objects_by_seq = {}
for obj in parse_sosi_file(filename):
    objects_by_seq[obj.sequence_number] = obj

# Check each reference
for obj in all_objects:
    for ref in obj.references:
        seq = abs(ref)  # Remove sign
        assert seq in objects_by_seq, f"Dangling reference: {ref}"

        target = objects_by_seq[seq]
        assert target.OBJTYPE in allowed_types_for_association
```

**Rule:** TOPO-ASSOC-001

### 6.2 Association Multiplicity

- [ ] Multiplicities satisfied per UML model
- [ ] Example: Bygning → avgrensesAvGrunnmur (1..*)
  - Must have at least 1 Grunnmur or Bygningsavgrensning
- [ ] Example: Mast → Bardun (0..*)
  - May have zero or more guy wires

**Reference:** `01-MANDATORY-ATTRIBUTES.yaml` / association definitions

### 6.3 Concrete Types Only

- [ ] No references to abstract types
- [ ] NO: Fellesegenskaper, KvalitetPåkrevd, KvalitetOpsjonell, Identifikasjon, Posisjonskvalitet
- [ ] YES: Bygning, Grunnmur, Mast, Veglenke, etc. (concrete object types)

**Rule:** TOPO-ASSOC-004 (references GR-COMMON-010)

---

## Section 7: Specification Compliance

**Priority: HIGH**

### 7.1 Version Compliance

- [ ] If `REGISTRERINGSVERSJON` present, matches specification version
  - Format: YYYY-MM-DD (e.g., "2022-01-01")
- [ ] Check version-specific rules:
  - FKB 5.0 data: Don't enforce FKB 5.1 systematic deviation rule (ACC-001)
  - FKB 5.1 data: All FKB 5.1 rules apply
- [ ] `NØYAKTIGHET` interpretation depends on version:
  - FKB 5.0: Similar to RMS
  - FKB 5.1: True standard deviation

**Reference:** `07-CONFLICTS-AMBIGUITIES.md` / Version-Specific Issues (V4.1)

### 7.2 Object Type Validity

- [ ] `OBJTYPE` value exists in specification
- [ ] Spelling/capitalization exactly matches specification
- [ ] OBJTYPE is concrete (not abstract supertype)
- [ ] Geometry type matches object type requirements

**Validation:** Check against `01-MANDATORY-ATTRIBUTES.yaml` object list

### 7.3 Namespace Compliance

- [ ] `NAVNEROM` URI points to correct specification
- [ ] Format: `http://data.geonorge.no/[S]FKB[/municipality]/FKB-{Dataset}/{Version}`
- [ ] Examples:
  - `http://data.geonorge.no/SOSI/FKB-Bygning/5.0`
  - `http://data.geonorge.no/SFKB/50/FKB-Ledning/so`

**Rule:** META-008

---

## Section 8: Special Cases & Exceptions

**Priority: MEDIUM**
**Reference:** `06-SPECIAL-CASES.md`

### 8.1 Fictional Boundaries

- [ ] Used only when appropriate:
  - Dataset boundary crossings
  - Obscured/incomplete features (trees covering building)
  - Temporary gaps pending completion
  - Unclear physical boundary (gravel road merging with terrain)
- [ ] Correct OBJTYPE used:
  - FiktivBygningsavgrensning
  - VegFiktivGrense
  - VannFiktivGrense
  - FiktivAvgrensningForAnlegg
- [ ] Clearly distinguishable from real boundaries
- [ ] Documented in `INFORMASJON` if needed

### 8.2 MEDIUM Attribute Handling

- [ ] MEDIUM attribute present when required
- [ ] Correct values:
  - `T` = På terrenget (on terrain) - default
  - `U` = Under terrenget (underground)
  - `B` = På bygning (on building/roof)
  - `L` = I lufta (in air/elevated)
- [ ] Objects with different MEDIUM can overlap in plan view (not an error)
- [ ] Network connectivity only within same MEDIUM level
- [ ] Validation accounts for MEDIUM before flagging topology errors

**Important:** Always check MEDIUM before reporting overlaps or crossing networks as errors!

### 8.3 Historical/Legacy Data

- [ ] Legacy data retains `REGISTRERINGSVERSJON` from original spec
- [ ] Lower accuracy documented if not meeting current standards
- [ ] NØYAKTIGHET reflects actual quality, not target quality
- [ ] Migration plan documented if needed

### 8.4 Incomplete Features at Boundary

- [ ] Features extending beyond dataset boundary properly handled
- [ ] Fictional boundaries used appropriately at edges
- [ ] Incomplete network ends documented
- [ ] Temporary state noted in `INFORMASJON` attribute

---

## Section 9: Final Checks

**Priority: MEDIUM**

### 9.1 Uniqueness

- [ ] `LOKALID` unique within dataset/namespace
  - Each UUID appears only once per NAVNEROM
- [ ] No duplicate objects (same location and attributes)
- [ ] Object sequence numbers unique (SOSI internal)

**Rule:** META-004

### 9.2 Completeness

- [ ] All expected object types present (if full coverage)
- [ ] Dataset boundary clearly defined
- [ ] README or metadata file describes dataset scope
- [ ] Known limitations documented
- [ ] Quality report generated

### 9.3 Consistency

- [ ] Attribute values consistent across related objects
- [ ] Coordinate system used consistently throughout file
- [ ] Accuracy class consistent within object types
- [ ] Naming conventions followed
- [ ] Code list values from same version/date

---

## Section 10: Validation Report

### 10.1 Generate Report

**Template:**

```
FKB Data Validation Report
==========================
Dataset: [name]
File: [filename]
Validation Date: [date]
Specification: FKB [version]
FKB Standard: [A/B/C/D]
Validator: [person/tool]
Tool version: [if automated]

Summary
-------
Total Objects: [count]
Object Types: [count unique types]
  - Bygning: [count]
  - Veglenke: [count]
  - [etc.]

Results by Section:
-------------------
1. File Format:      PASS  [X checks]
2. Geometry:         PASS  [X checks]
3. Attributes:       WARN  [X checks, Y warnings]
4. Topology:         PASS  [X checks]
5. Quality:          PASS  [X checks]
6. References:       PASS  [X checks]
7. Specification:    PASS  [X checks]
8. Special Cases:    PASS  [X checks]
9. Final Checks:     PASS  [X checks]

Issue Summary
-------------
CRITICAL: [count]
HIGH:     [count]
MEDIUM:   [count]
LOW:      [count]

Critical Issues
---------------
[If any, list with rule IDs and object IDs]

High Priority Issues
--------------------
[List]

Detailed Issue List
-------------------
[For each issue:]
- Issue ID: [sequential]
- Priority: [CRITICAL/HIGH/MEDIUM/LOW]
- Rule: [Rule ID from specifications]
- Object: LOKALID=[uuid] or Sequence=[number]
- OBJTYPE: [object type]
- Description: [what's wrong]
- Location: [coordinates or reference]
- Recommendation: [how to fix]

Overall Assessment
------------------
Status: APPROVED / CONDITIONAL / REJECTED

Decision:
[If APPROVED: Ready for delivery]
[If CONDITIONAL: Can be delivered with documented limitations]
[If REJECTED: Must be corrected before delivery]

Conditions (if CONDITIONAL):
- [List limitations/caveats]

Required Corrections (if REJECTED):
- [Prioritized list of fixes]

Dataset Statistics:
-------------------
- Total objects: [count]
- Average NØYAKTIGHET: [value] cm
- Coordinate system: EUREF89 UTM[zone] + [vertical datum]
- Date range: [earliest] to [latest] DATAFANGSTDATO
- Primary capture method: [most common DATAFANGSTMETODE]

Validator Signature: ___________________
Date: ___________________
```

### 10.2 Report Interpretation

**APPROVED:** All CRITICAL and HIGH checks pass, < 5% MEDIUM issues
**CONDITIONAL:** All CRITICAL pass, some HIGH issues but documented
**REJECTED:** Any CRITICAL failures or >10% HIGH issues

---

## Automated Validation Tools

### Recommended Tool Chain:

1. **SOSI Validator**
   - Purpose: File format validation
   - Source: Kartverket/Statens Kartverk
   - URL: https://www.kartverket.no/geodataarbeid/standardisering/veiledere-og-verktoy/sosi-kontroll

2. **GDAL/OGR**
   ```bash
   # Geometry validity
   ogrinfo -al file.sos

   # Format conversion (tests validity)
   ogr2ogr -f GeoJSON output.geojson input.sos

   # Check CRS
   ogrinfo -so file.sos
   ```

3. **PostGIS**
   ```sql
   -- Import to PostGIS
   -- Run topology checks
   SELECT lokalid, ST_IsValid(geom), ST_IsSimple(geom)
   FROM features
   WHERE NOT ST_IsValid(geom);

   -- Type 2 flate validation
   SELECT f.lokalid,
          ST_Equals(
            f.område_geom,
            ST_Union(ARRAY(
              SELECT b.geom
              FROM boundaries b
              WHERE b.lokalid = ANY(f.boundary_refs)
            ))
          ) AS topology_valid
   FROM flater f
   WHERE f.has_shared_geometry = true;
   ```

4. **QGIS with Topology Checker Plugin**
   - Visual validation
   - Interactive error correction
   - Built-in topology rules

5. **Custom Python Scripts**
   - Type 2 flate validation (most critical)
   - Association checking
   - FKB-specific rules

### Automation Strategy:

**Level 1 (Fast, ~90% of checks):**
- File format validation
- Basic geometry validity
- Attribute presence
- Format compliance
- Time: Minutes

**Level 2 (Moderate, requires GIS):**
- Topology checks
- Spatial relationships
- Coverage analysis
- Point-in-polygon
- Time: 15-60 minutes

**Level 3 (Slow, requires manual review or specialized tools):**
- Accuracy verification (needs ground control)
- Complex network analysis
- Quality assessment
- Special cases evaluation
- Time: Hours to days

**Recommended:** Automate Level 1 & 2, sample Level 3

---

## Priority Validation Matrix

| Check Category | Priority | Automated | Time | Fail Impact |
|----------------|----------|-----------|------|-------------|
| File format | CRITICAL | Yes | 1 min | Cannot read file |
| Basic geometry | CRITICAL | Yes | 5 min | Invalid geometry |
| Mandatory attrs | CRITICAL | Yes | 2 min | Incomplete data |
| Shared geometry | CRITICAL | Partial | 30 min | Topology invalid |
| Point-in-polygon | HIGH | Yes | 5 min | Inconsistent |
| Accuracy check | HIGH | Needs GCP | Hours | Quality issue |
| Network connect | HIGH | Yes | 15 min | Broken network |
| References | CRITICAL | Yes | 5 min | Dangling refs |
| Code lists | MEDIUM | Needs API | 10 min | Invalid values |
| Special cases | MEDIUM | Manual | Variable | Edge cases |

---

## Quick Reference: Most Critical Checks

**Top 5 checks that catch 80% of issues:**

1. **Område = union(avgrensningsobjekter)** for Type 2 flater (TOPO-CRITICAL-001)
2. **All mandatory attributes present** per object type (META-001)
3. **Geometry valid** (closed, no self-intersection) (GR-004, GR-005)
4. **References resolve** (no dangling pointers) (TOPO-ASSOC-001)
5. **KVALITET complete** with valid DATAFANGSTMETODE (META-001)

**Focus on these first!**

---

## Appendix A: Rule ID Quick Reference

See full details in respective specification files:

**Geometric Rules:** (02-GEOMETRIC-RULES.yaml)
- GR-001: Simple geometries only (no multi-geometries)
- GR-002: Coordinate transformation precision < 5mm
- GR-003: Pilhøyde ≤ NØYAKTIGHET
- GR-004: Polygons must be closed
- GR-005: No self-intersections
- GR-006: No self-overlaps

**Accuracy Rules:** (03-ACCURACY-STANDARDS.yaml)
- ACC-001: Systematic deviation ≤ 1/3 × standardavvik (FKB 5.1)
- ACC-002: Gross errors (>3σ) < 1%
- ACC-003: NØYAKTIGHET = standard deviation
- ACC-004: FKB 5.1 change from previous versions
- ACC-005: Must control all three measures (std dev, sys dev, gross errors)

**Metadata Rules:** (05-METADATA-RULES.yaml)
- META-001: Mandatory KVALITET attributes
- META-002: NØYAKTIGHET matches requirements
- META-003: DATAFANGSTDATO ≤ OPPDATERINGSDATO
- META-004: LOKALID unique within dataset
- META-005: H-NØYAKTIGHET for 3D objects
- META-006: VERIFISERINGSDATO ≤ OPPDATERINGSDATO
- META-007: DATAFANGSTMETODEHØYDE cannot be 'dig'
- META-008: NAVNEROM URI pattern
- META-009: REGISTRERINGSVERSJON format
- META-010: Coordinate system regional match

**Topology Rules:** (04-TOPOLOGY-RULES.yaml)
- TOPO-CRITICAL-001: Område = union(boundaries)
- TOPO-CONTAIN-001: Posisjon inside område
- TOPO-NETWORK-001 to 005: Network connectivity
- TOPO-COVERAGE-001 to 003: Full coverage requirements
- TOPO-ASSOC-001 to 005: Association integrity

**SOSI Format Rules:** (08-SOSI-FORMAT-RULES.yaml)
- SOSI-FORMAT-001 to 010: File structure and encoding

---

## Appendix B: Validation Workflow Diagram

```
START
  ↓
[1. File Format Check] → FAIL → REJECT (cannot proceed)
  ↓ PASS
[2. Geometry Validity] → FAIL → REJECT (invalid data)
  ↓ PASS
[3. Attribute Check] → FAIL → REJECT (incomplete)
  ↓ PASS
[4. Topology Check] → FAIL → FIX or DOCUMENT → CONDITIONAL
  ↓ PASS
[5. Quality Check] → FAIL → FIX or DOCUMENT → CONDITIONAL
  ↓ PASS
[6. Special Cases] → ISSUES → DOCUMENT → CONDITIONAL
  ↓ CLEAN
[7. Final Review] → MINOR ISSUES → DOCUMENT → CONDITIONAL
  ↓ CLEAN
APPROVED
```

---

## Appendix C: Common Validation Errors and Fixes

### Error 1: "Område does not match union of boundaries"
- **Cause:** Gap or overlap in boundary objects
- **Fix:** Rebuild område from boundaries or fix boundary coordinates
- **Rule:** TOPO-CRITICAL-001
- **Priority:** CRITICAL

### Error 2: "Posisjon outside område"
- **Cause:** Point placed incorrectly or område boundary wrong
- **Fix:** Move point inside or correct område
- **Rule:** TOPO-CONTAIN-001
- **Priority:** HIGH

### Error 3: "Missing NØYAKTIGHET for photogrammetric data"
- **Cause:** DATAFANGSTMETODE='fot' but NØYAKTIGHET not specified
- **Fix:** Add NØYAKTIGHET value matching accuracy class
- **Rule:** META-001, META-002
- **Priority:** CRITICAL

### Error 4: "Dangling network edge"
- **Cause:** Endpoint not connected within snap tolerance
- **Fix:** Snap to nearby endpoint or mark as legitimate terminator
- **Rule:** TOPO-NETWORK-004
- **Priority:** MEDIUM

### Error 5: "Self-intersecting polygon"
- **Cause:** Boundary crosses itself
- **Fix:** Rebuild geometry without crossing
- **Rule:** GR-005
- **Priority:** CRITICAL

### Error 6: "Invalid UUID format"
- **Cause:** LOKALID not formatted as valid UUID v4
- **Fix:** Generate proper UUID
- **Rule:** META-004
- **Priority:** HIGH

### Error 7: "Coordinate out of range"
- **Cause:** Wrong units (meters instead of cm) or wrong CRS
- **Fix:** Multiply by 100 if meters, or transform to correct CRS
- **Rule:** SOSI-FORMAT-003
- **Priority:** CRITICAL

### Error 8: "Missing .KVALITET block"
- **Cause:** Required metadata not present
- **Fix:** Add complete KVALITET block with DATAFANGSTMETODE
- **Rule:** META-001
- **Priority:** CRITICAL

---

## Appendix D: Contact & Resources

**Specifications:**
- FKB Documentation: https://www.kartverket.no/geodataarbeid/geovekst/fkb
- SOSI Format: https://www.kartverket.no/geodataarbeid/teknologi/standarder/sosi
- Code Lists: https://register.geonorge.no
- FKB Product Specifications: https://sosi.geonorge.no/standarder/

**Tools:**
- GDAL: https://gdal.org
- PostGIS: https://postgis.net
- QGIS: https://qgis.org
- SOSI Tools: https://www.kartverket.no/geodataarbeid/standardisering/veiledere-og-verktoy/sosi-kontroll

**Support:**
- Kartverket Contact: https://www.kartverket.no/om-kartverket/kontakt-oss
- Geovekst: https://www.kartverket.no/geodataarbeid/geovekst

**Standards:**
- Geodatakvalitet: https://register.geonorge.no/standarder/sosi/standarder-geografisk-informasjon/geodatakvalitet
- SOSI UML Modeling: https://register.geonorge.no/standarder/sosi/del-1-generell-del/regler-for-uml-modellering

---

## Appendix E: Validation Tool Comparison

| Tool | Format | Geometry | Attributes | Topology | Performance | Cost |
|------|--------|----------|------------|----------|-------------|------|
| SOSI-kontroll | Excellent | Good | Excellent | Basic | Fast | Free |
| PostGIS | N/A | Excellent | Good | Excellent | Fast | Free |
| QGIS | Good | Excellent | Good | Good | Medium | Free |
| FME | Excellent | Excellent | Excellent | Excellent | Fast | Commercial |
| Custom Python | Fair | Good | Good | Good | Slow | Free |

**Recommendation:** Use combination of SOSI-kontroll + PostGIS + QGIS for comprehensive validation.

---

## Document Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-04 | Initial release based on FKB 5.1 specifications |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-04
**Next Review:** Annually or with specification updates
**Status:** Ready for production use

---

*END OF CHECKLIST*
