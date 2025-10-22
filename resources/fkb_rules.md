# FKB Data Extraction Rules

**Purpose:** Core rules, metadata requirements, and geometric logic for automatically extracting FKB-compliant data from point clouds.

**Source:** Based on Statens vegvesen v5.2 specifications

---

## 1. Required Dataset Files

All extracted FKB data must be delivered in separate files for each of these datasets:

- `FKB-BygnAnlegg` (Buildings and structures)
- `FKB-Bygning` (Buildings)
- `FKB-Ledning` (Utilities and infrastructure)
- `FKB-Vann` (Water bodies and features)
- `FKB-Veg` (Roads)
- `FKB-TraktorvegSti` (Tractor roads and paths)
- `Elveg 2.0` (Road network)

---

## 2. Mandatory Metadata (Per Object)

Every FKB object must include these attributes in the SOSI file:

### 2.1 OBJTYPE
**Required:** Yes  
**Type:** String  
**Description:** The official FKB object name  
**Examples:**
- `Vegdekkekant` (Road edge)
- `Fasadelinje` (Facade line)
- `SkråForstøtningsmur` (Sloped retaining wall)
- `Høydekurve` (Contour line)
- `Bygning` (Building)

### 2.2 DATAFANGSTDATO
**Required:** Yes  
**Type:** Date  
**Format:** `ååååmmdd` (YYYYMMDD)  
**Description:** Date of data capture (survey/scan)  
**Example:** `20230502`

### 2.3 REGISTRERINGSVERSJON
**Required:** Yes  
**Type:** Date  
**Format:** `yyyy-mm-dd`  
**Description:** FKB version used for registration  
**Value:** For FKB 5.0, always use `2022-01-01`

### 2.4 KVALITET (Quality Block)

**Required:** Yes  
**Type:** Block with 5 mandatory child attributes

```sosi
..KVALITET
...DATAFANGSTMETODE byg
...NØYAKTIGHET 10
...SYNBARHET O
...DATAFANGSTMETODEHØYDE byg
...H-NØYAKTIGHET 10
```

#### DATAFANGSTMETODE (Capture Method)
**Required:** Yes  
**Type:** String code  
**Description:** How the data was captured  

**Allowed values for point cloud extraction:**
- `byg` - "Som bygget" (As-built, verified from plan/model)
- `sat` - "Satellittmålt" (GNSS surveyed)
- `lan` - "Landmålt" (Surveyed with total station)

**Forbidden values:**
- `pla` - From plan only (not allowed unless specifically agreed)
- `gen` - Generated (not allowed unless specifically agreed)

#### NØYAKTIGHET (Horizontal Accuracy)
**Required:** Yes  
**Type:** Integer  
**Unit:** Centimeters  
**Description:** Positional accuracy of XY coordinates  
**Values, Horistontal and Vertical:**
- `15,15` - 15cm accuracy (FKB-A standard)
- `20,20` - 20cm accuracy (FKB-B standard)
- `40,40` - 40cm accuracy (FKB-C standard)
- `40,40` - 40cm accuracy (FKB-D standard)

#### SYNBARHET (Visibility)
**Required:** Yes  
**Type:** String code  
**Description:** Object visibility at time of capture  

**Values:**
- `O` - Fully visible (required for new construction)
- `T` - Partially covered
- `H` - Completely covered/hidden

#### DATAFANGSTMETODEHØYDE (Height Capture Method)
**Required:** Yes  
**Type:** String code  
**Description:** Same code values as DATAFANGSTMETODE  
**Typical value:** `byg` (same as horizontal method)

#### H-NØYAKTIGHET (Vertical Accuracy)
**Required:** Yes  
**Type:** Integer  
**Unit:** Centimeters  
**Description:** Height (Z) accuracy  
**Typical values:** Same as NØYAKTIGHET (10, 20, 50 cm)

---

## 3. Geometric and Topological Logic

### 3.1 Polygon (FLATE) Creation Methods

FKB uses two different methods for creating surface geometries:

#### Method 1: Wholly-Owned Geometry (heleid geometri)

**Used for:**
- `Bru` (Bridge)
- `SkråForstøtningsmur` (Retaining wall)
- Standalone structures

**Implementation:**
1. Create a separate `.KURVE` object with `..OBJTYPE Flateavgrensning`
2. The `.FLATE` object (e.g., `..OBJTYPE Bru`) references this boundary curve
3. The boundary curve is "owned" by this surface only

**SOSI Structure:**
```sosi
.KURVE 1001:
..OBJTYPE Flateavgrensning
..NØ
123456.78 7891011.23
123456.89 7891011.45
...

.FLATE 2001:
..OBJTYPE Bru
..REF :1001
...other attributes
```

#### Method 2: Shared Geometry (delt geometri)

**Used for:**
- `VegKjørende` (Road surface for vehicles)
- `Fortau` (Sidewalk)
- `Parkeringsområde` (Parking area)
- `VegGåendeOgSyklende` (Pedestrian/cycling surface)

**Implementation:**
1. Create separate FKB line objects that form the boundary (e.g., `Vegdekkekant`, `Kjørebanekant`)
2. The `.FLATE` object references these existing line objects
3. Multiple surfaces can share the same boundary lines (topology preserved)

**SOSI Structure:**
```sosi
.KURVE 3001:
..OBJTYPE Vegdekkekant
..NØ
...coordinates

.KURVE 3002:
..OBJTYPE Vegdekkekant
..NØ
...coordinates

.FLATE 4001:
..OBJTYPE VegKjørende
..REF :3001 :3002
...other attributes
```

#### Line Capping with Fictional Boundaries

**Rule:** Road surfaces must have closed boundaries. Use `VegFiktivGrense` to cap open ends.

**Required for:**
- `VegKjørende`
- `VegGåendeOgSyklende`

**Implementation:**
Create a `VegFiktivGrense` line to close the polygon where no physical edge exists (e.g., at project boundaries).

```sosi
.KURVE 5001:
..OBJTYPE VegFiktivGrense
..NØ
...coordinates connecting the open ends
```

### 3.2 Height Reference (HREF)

**Rule:** Specifies where on an object the Z-coordinate was measured  
**Required for:** Objects with vertical extent (walls, buildings, etc.)

**Values:**
- `fot` - Bottom/foot of object
- `topp` - Top of object

**Example:**
- `Fasadelinje` (Facade line) - measured at `fot` (bottom of wall)
- `Bygning` (Building) - typically measured at ground level (`fot`)

**NVDB Override Rule:**
For objects that exist in both FKB and NVDB (National Road Database), use the NVDB standard:
- `Vegrekkverk` (Road barrier) - always `topp`

```sosi
..OBJTYPE Fasadelinje
..HREF fot
..NØ
...coordinates at bottom of wall
```

### 3.3 Object Location (MEDIUM)

**Rule:** Required for all objects NOT on ground-level terrain surface  
**Type:** String code

**Values:**
- `L` - "I luft" (In air, e.g., on a bridge deck)
- `U` - "Under terrenget" (Underground, e.g., in tunnel)
- `B` - "I Bygning" (Inside a building)
- (No MEDIUM attribute) - Object is on ground terrain

**Example for tunnel:**
```sosi
..OBJTYPE VegKjørende
..MEDIUM U
```

**Example for bridge:**
```sosi
..OBJTYPE Vegdekkekant
..MEDIUM L
```

### 3.4 Curve Precision (Pilhøyde Constraint)

**Critical Rule:** Mathematical constraint for line simplification/densification

**Definition:**
The maximum perpendicular distance from a straight line segment (between two vertices) to the true curved shape must not exceed the accuracy tolerance.

**Formula:**
```
max_deviation ≤ NØYAKTIGHET
```

**Implementation:**
- For 10cm accuracy: deviation between simplified line and original curve ≤ 10cm
- For 20cm accuracy: deviation ≤ 20cm
- Use Douglas-Peucker algorithm with epsilon = NØYAKTIGHET

**Example:**
```python
from shapely.geometry import LineString

# Original dense line from point cloud
original_line = LineString(dense_points)

# Simplify with tolerance matching accuracy
simplified = original_line.simplify(
    tolerance=0.10,  # 10cm for FKB-A
    preserve_topology=True
)
```

---

## 4. Object-Specific Rules and Exceptions

### 4.1 General Deviations from Standard FKB

**IDENT attribute:**
- NOT required for automated extraction
- Can be omitted

### 4.2 Tunnel Objects

**Rule:** Road surfaces inside tunnels must be delivered

**Required objects:**
- `VegKjørende` (with `..MEDIUM U`)
- `Vegdekkekant` (with `..MEDIUM U`)
- All other relevant road features

**Critical:** The `..MEDIUM U` attribute is mandatory

### 4.3 Road Edge Requirements

**Kjørebanekant** (Lane edge) and **Vegskulderkant** (Shoulder edge):

**Required for:**
- Europaveger (European routes)
- Riksveger (National roads)
- Fylkesveger (County roads)

**Not required for:**
- Kommunale veger (Municipal roads)
- Private roads

### 4.4 Elveg Objects (Simplified Attributes)

For `Elveg 2.0` network dataset, only these attributes are required:

1. `Objekttype` (must be `Veglenke`)
2. `Typeveg` (Road type)
3. `Datafangstdato`
4. `Kvalitet` (standard quality block)
5. `Medium` (if not on ground)

**All other attributes can be omitted.**

### 4.5 Lighting (Lysarmatur)

**Required:** Register light fixtures that hang on wires over the road

**Object type:** `Lysarmatur`

**Implementation:** Detect overhead light fixtures from point cloud intensity/classification

---

## 5. SOSI File Header Requirements

Every `.sos` file must include this header structure:

### 5.1 Required Header Attributes

```sosi
.HODE
..TEGNSETT UTF-8
..KOORDSYS [zone_code]
..VERT-DATUM NN2000
..SOSI-VERSJON 5.0
..OBJEKTKATALOG [dataset_name]
..OMRÅDE
...MIN-NØ [min_east] [min_north]
...MAX-NØ [max_east] [max_north]
..DATAFANGSTDATO [yyyymmdd]
```

### 5.2 Coordinate Systems (KOORDSYS)

Norway uses **ETRS89 / UTM zones 31-36** (plus zone 37 for far eastern Svalbard). Different zones are used based on location:

#### Primary Zones for Mainland FKB Data

##### UTM Zone 32N (EPSG:25832)
**SOSI code:** `22`  
**Coverage:** Southern Norway municipalities
- Innlandet, Oslo, Viken
- Vestfold og Telemark, Agder, Rogaland
- Vestland, Møre og Romsdal, Trøndelag

**Central meridian:** 9°E  
**Longitude range:** 6°E to 12°E

##### UTM Zone 33N (EPSG:25833)
**SOSI code:** `23`  
**Coverage:** 
- **Nationwide data** (default for country-wide datasets)
- Nordland, Troms (part of Troms og Finnmark)

**Central meridian:** 15°E  
**Longitude range:** 12°E to 18°E

##### UTM Zone 35N (EPSG:25835)
**SOSI code:** `25`  
**Coverage:** Finnmark (part of Troms og Finnmark)

**Central meridian:** 27°E  
**Longitude range:** 24°E to 30°E

#### Additional Zones (Offshore & Special Cases)

##### UTM Zone 31N (EPSG:25831)
**SOSI code:** `21`  
**Coverage:** Far western coast, Jan Mayen, western Svalbard, offshore

**Central meridian:** 3°E  
**Longitude range:** 0°E to 6°E

##### UTM Zone 34N (EPSG:25834)
**SOSI code:** `24`  
**Coverage:** Offshore areas, large sea areas, Svalbard (eliminated 72°-84°N)

**Central meridian:** 21°E  
**Longitude range:** 18°E to 24°E

##### UTM Zone 36N (EPSG:25836)
**SOSI code:** `26`  
**Coverage:** Eastern offshore areas, eastern Svalbard, maritime data

**Central meridian:** 33°E  
**Longitude range:** 30°E to 36°E

**Note:** In Svalbard region (72°-84°N), standard zones 32, 34, 36 are eliminated. Zones 31, 33, 35, 37 are widened to cover the gaps.

### 5.3 Vertical Datum

**Always use:** `..VERT-DATUM NN2000`

**NN2000** = Norway Normal Null 2000 (national height system)

**Note:** Older datasets may use NN1954, but all new FKB data must use NN2000.

### 5.4 OBJEKTKATALOG Values

Specify the exact FKB dataset and version:

```sosi
..OBJEKTKATALOG FKBVeg 5.0.1
..OBJEKTKATALOG FKBBygning 5.0.1
..OBJEKTKATALOG FKBVann 5.0.1
..OBJEKTKATALOG FKBLedning 5.0.1
..OBJEKTKATALOG Elveg 2.0
```

### 5.5 Complete Header Example

```sosi
.HODE
..TEGNSETT UTF-8
..KOORDSYS 23
..ORIGO-NØ 0 0
..ENHET 0.01
..VERT-DATUM NN2000
..SOSI-VERSJON 5.0
..OBJEKTKATALOG FKBVeg 5.0.1
..OMRÅDE
...MIN-NØ 598234.56 6643210.12
...MAX-NØ 599456.78 6644532.34
..TRANSPAR
...KOORDSYS 23
...ORIGO-NØ 0 0
...ENHET 0.01
...VERT-DATUM NN2000
..DATAFANGSTDATO 20230502
..SOSI-NIVÅ 4
```

---

## 6. Implementation Checklist

### Point Cloud Processing
- [ ] Load and classify point cloud (ground, building, vegetation, etc.)
- [ ] Extract ground surface for terrain features
- [ ] Identify non-ground objects (buildings, roads, structures)
- [ ] Apply accuracy standards (10cm, 20cm, 50cm)

### Geometry Extraction
- [ ] Extract building footprints (polygons)
- [ ] Extract road edges (lines)
- [ ] Extract centerlines
- [ ] Extract contour lines from terrain
- [ ] Apply Douglas-Peucker simplification (tolerance = accuracy)
- [ ] Validate topology (no self-intersections, closed polygons)

### Metadata Assignment
- [ ] Assign correct OBJTYPE for each feature
- [ ] Set DATAFANGSTDATO (scan date)
- [ ] Set REGISTRERINGSVERSJON to `2022-01-01`
- [ ] Create KVALITET block with all 5 attributes
- [ ] Set DATAFANGSTMETODE (typically `byg`)
- [ ] Set NØYAKTIGHET based on FKB class
- [ ] Set SYNBARHET to `O` for new construction
- [ ] Add HREF where applicable (fot/topp)
- [ ] Add MEDIUM for non-ground objects (L/U/B)

### Topology Building
- [ ] Create wholly-owned geometry for bridges/structures
- [ ] Create shared geometry for road surfaces
- [ ] Add VegFiktivGrense to cap open road surfaces
- [ ] Ensure adjacent polygons share boundaries correctly
- [ ] Validate no gaps or overlaps

### SOSI File Generation
- [ ] Determine correct UTM zone (22/23/25)
- [ ] Create proper HODE section
- [ ] Set correct KOORDSYS code
- [ ] Set VERT-DATUM NN2000
- [ ] Set OBJEKTKATALOG to correct dataset
- [ ] Calculate MIN-NØ and MAX-NØ bounds
- [ ] Output features in correct format (.PUNKT, .KURVE, .FLATE)
- [ ] Validate with SOSI-kontroll tool

### Quality Control
- [ ] Verify geometric accuracy meets FKB class requirements
- [ ] Check completeness (all required objects captured)
- [ ] Validate topology (SOSI-kontroll)
- [ ] Check for missing mandatory attributes
- [ ] Review special cases (tunnels, bridges)

---

## 7. Common Validation Errors

### Missing Mandatory Attributes
**Error:** Object missing KVALITET block or child attributes  
**Fix:** Ensure all 5 KVALITET attributes are present

### Wrong Coordinate System
**Error:** Using EPSG code instead of SOSI KOORDSYS code  
**Fix:** Use 22 (not 25832), 23 (not 25833), 25 (not 25835)

### Open Polygons
**Error:** Road surface polygon not closed  
**Fix:** Add VegFiktivGrense to cap the ends

### Accuracy Exceeds Tolerance
**Error:** Geometry simplified too much, exceeds pilhøyde constraint  
**Fix:** Reduce simplification tolerance to match NØYAKTIGHET

### Missing MEDIUM for Non-Ground Objects
**Error:** Tunnel or bridge objects without MEDIUM attribute  
**Fix:** Add `..MEDIUM U` for tunnels, `..MEDIUM L` for bridges

### Wrong Height Reference
**Error:** Using `topp` when NVDB specifies different standard  
**Fix:** Check if object exists in NVDB, use their standard

---

## 8. References

**Official FKB Documentation:**
- https://www.kartverket.no/geodataarbeid/geovekst/fkb-produktspesifikasjoner
- https://register.geonorge.no/produktspesifikasjoner

**SOSI Standard:**
- https://www.kartverket.no/standard/sosi/

**Coordinate Systems:**
- https://www.geonorge.no/en/references/references/coordiante-systems/

**Validation Tools:**
- SOSI-kontroll: https://www.kartverket.no/geodataarbeid/standardisering/veiledere-og-verktoy/sosi-kontroll

---

## Quick Reference Card

| Attribute | Required | Type | Example Value |
|-----------|----------|------|---------------|
| OBJTYPE | Yes | String | `Vegdekkekant` |
| DATAFANGSTDATO | Yes | yyyymmdd | `20230502` |
| REGISTRERINGSVERSJON | Yes | yyyy-mm-dd | `2022-01-01` |
| DATAFANGSTMETODE | Yes | Code | `byg` |
| NØYAKTIGHET | Yes | Integer (cm) | `10` |
| SYNBARHET | Yes | Code | `O` |
| DATAFANGSTMETODEHØYDE | Yes | Code | `byg` |
| H-NØYAKTIGHET | Yes | Integer (cm) | `10` |
| HREF | Conditional | fot/topp | `fot` |
| MEDIUM | Conditional | L/U/B | `U` |

**Coordinate Systems (ETRS89 / UTM):**
- Zone 31: SOSI `21` → EPSG:25831 (Far west coast, Jan Mayen, offshore)
- Zone 32: SOSI `22` → EPSG:25832 (Southern Norway - primary FKB)
- Zone 33: SOSI `23` → EPSG:25833 (Nationwide, Nordland, Troms - primary FKB)
- Zone 34: SOSI `24` → EPSG:25834 (Offshore, maritime data)
- Zone 35: SOSI `25` → EPSG:25835 (Finnmark - primary FKB)
- Zone 36: SOSI `26` → EPSG:25836 (Eastern offshore, eastern Svalbard)

**Vertical Datum:** Always `NN2000`

**FKB Version:** `2022-01-01` for FKB 5.0
