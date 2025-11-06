# FKB Special Cases and Exceptions

*Analysis Date: 2025-11-04*
*Sources: All FKB 5.1 specifications*

## Overview

This document catalogs special cases, exceptions, and conditional requirements that deviate from standard FKB rules. These are the edge cases, special circumstances, and conditional logic that implementers must handle correctly.

---

## 1. Conditional Mandatory Attributes

### 1.1 Photogrammetric Registration

**Condition:** When `DATAFANGSTMETODE = 'fot'` (photogrammetry)

**Then mandatory:**
- `..KVALITET/NØYAKTIGHET` - Standard deviation of positioning
- `..KVALITET/SYNBARHET` - Visibility in aerial photos (0-3)

**Source:** FKB-Generell del 5.1, Vedlegg D (Photogrammetric registration guidelines)

**Rationale:** Photogrammetric data quality depends heavily on how well objects are visible in aerial imagery and the achieved accuracy. These attributes must be documented for photogrammetrically captured data.

---

### 1.2 3D Geometry

**Condition:** When object has Z coordinates (3D geometry)

**Then mandatory/recommended:**
- `..KVALITET/DATAFANGSTMETODEHØYDE` - If height capture method differs from horizontal
- `..KVALITET/H-NØYAKTIGHET` - Vertical accuracy (recommended)

**Source:** FKB-Generell del 5.1, Posisjonskvalitet datatype

**Rationale:** Height may be captured differently than horizontal position (e.g., horizontal from photogrammetry, height from LiDAR). Vertical accuracy requirements may differ from horizontal.

**Note:** H-NØYAKTIGHET is technically optional but strongly recommended for 3D data.

---

### 1.3 MEDIUM Attribute Variability

**Condition:** Varies by object type and context

**Rules:**
- Most objects: MEDIUM is optional, defaults to terrain level (T)
- Buildings: MEDIUM is mandatory (can be on building, in air, underground)
- Roads/utilities: MEDIUM mandatory when not at terrain level
- Network objects: MEDIUM used to separate vertical levels (tunnels vs. bridges)

**Common values:**
- `T` = På terrenget (on terrain) - default
- `U` = Under terrenget (underground) - tunnels, underground utilities, cellars
- `B` = På bygning (on building) - roof features
- `L` = I lufta (in air) - bridges, overhead lines, elevated structures

**Source:** FKB-Generell del 5.1, MEDIUM codelist

**Special topology rule:** Objects with different MEDIUM values can overlap in plan view without being considered a topology error.

---

### 1.4 HREF (Height Reference)

**Condition:** Object-specific requirements

**Rules:**
- Photogrammetry: Default is `topp` (top of object)
- Mast, flagpole, chimney: Use `fot` (foot/bottom)
- Terrain height required: Use `fot`
- Buildings: Usually `topp` for roof registration
- Walls: May use `fot` for foundation

**Source:** FKB-Generell del 5.1, Høydereferanse codelist

**Note:** Affects interpretation of Z coordinate - whether it represents top or bottom of object.

---

### 1.5 Geometry Type Variations

**Condition:** Scale and object size dependent

**Bygning (Building):**
- **Always:** PUNKT (posisjon) - mandatory
- **Optional:** FLATE (område) - for larger/important buildings
- **Decision:** Based on FKB standard (A/B/C/D) and building size
- **Small buildings:** May have only PUNKT representation

**Elv (River):**
- **Width < 2m:** KURVE (centerline) only
- **Width ≥ 2m:** FLATE (area) with Elvekant boundaries

**Roads:**
- **Main roads:** Full surface representation (VegKjørende FLATE)
- **Minor roads:** May have only centerline (Veglenke)

**Source:** Individual FKB specifications for each object type

---

## 2. Geometry Type Exceptions

### 2.1 Bygning Dual Representation

**Standard rule:** Bygning has PUNKT geometry (posisjon) - **mandatory**

**Exception:** Bygning may also have FLATE geometry (område) - **optional**

**Constraints when both present:**
- Posisjon must be inside område (TOPO-CONTAIN-001)
- Posisjon should be centrally located in område
- LOKALID is same for both representations (same object)

**Decision criteria:**
- FKB-A, FKB-B: Most buildings have both PUNKT and FLATE
- FKB-C, FKB-D: Smaller buildings may have only PUNKT
- Threshold varies by local practice (no strict standard)

**Source:** FKB-Bygning 5.1.1

---

### 2.2 Incomplete Linear Features at Dataset Boundary

**Standard rule:** Linear features should be complete

**Exception:** When feature continues beyond dataset boundary

**Handling:**
1. Feature extends to dataset edge
2. Feature is marked as incomplete (if attribute available)
3. Documentation in INFORMASJON attribute recommended

**Use of fictional boundaries:**
- For roads: Use `VegFiktivGrense` to close road surface polygons at boundary
- For water: Use `VannFiktivGrense` to close water body polygons
- For buildings: Use `FiktivBygningsavgrensning` if building extends beyond boundary

**Constraint:** Fictional boundaries should only be used at legitimate dataset edges, not to mask missing data or poor quality.

**Source:** Individual FKB specifications, general FKB practice

---

### 2.3 Network Objects at Different Levels

**Standard rule:** Network objects connect at endpoints

**Exception:** Networks at different vertical levels (MEDIUM attribute)

**Examples:**
- Road on bridge (MEDIUM=L) crosses road in tunnel (MEDIUM=U)
- Overhead power line (MEDIUM=L) crosses underground water pipe (MEDIUM=U)

**Topology handling:**
- Objects with different MEDIUM do NOT have topology connection
- No snap requirement between different MEDIUM levels
- Overlaps in plan view are permitted

**Validation:** Always check MEDIUM before flagging crossing networks as errors

**Source:** FKB-Generell del 5.1, network topology discussions

---

## 3. Accuracy Class Overrides

### 3.1 Higher Accuracy for Critical Objects

**General rule:** Objects follow accuracy class for FKB standard (A/B/C/D) and object class (1/2/3/4)

**Potential override:** Critical infrastructure may require higher accuracy than standard

**Examples:**
- Survey control points: Always highest accuracy
- Cadastral boundaries: May require accuracy exceeding general FKB standard
- Building footprints for property tax: May require Class 1 even in FKB-C areas

**Note:** FKB specifications generally do NOT mandate these overrides - they are implementation/project-specific decisions. Individual specifications define which accuracy class applies to each object type.

**Source:** Project requirements, not explicitly in FKB specifications

---

### 3.2 Lower Accuracy Acceptable for Historical Data

**General rule:** All data must meet FKB accuracy requirements

**Exception:** Legacy data and historical features

**Conditions:**
- Data captured under earlier FKB versions (4.6, 5.0)
- Historical features no longer accessible for resurvey
- Difficult terrain where standard accuracy cannot be achieved

**Documentation requirements:**
- REGISTRERINGSVERSJON indicates specification version used
- NØYAKTIGHET reflects actual achieved accuracy (not standard requirement)
- INFORMASJON attribute should note if accuracy is below standard

**Handling:**
- Data remains valid even if below current accuracy requirements
- Should be improved when opportunity arises (resurvey, update)
- Quality metadata must reflect actual quality, not desired quality

**Source:** FKB-Generell del 5.1, maintenance and update guidelines

---

## 4. Fictional Boundary Rules

### 4.1 When to Use FiktivBygningsavgrensning

**Legitimate uses:**
1. Building extends beyond dataset boundary
2. Building boundary partially obscured (e.g., under trees)
3. Building connects to another building without clear separation line
4. Temporary building or structure with unclear permanent boundary

**Constraints:**
- Should be minimized - prefer real boundaries
- Must be clearly distinguishable from real boundaries in data
- Should not cross real boundary objects

**SOSI encoding:** Same as regular Bygningsavgrensning but with specific OBJTYPE = FiktivBygningsavgrensning

**Source:** FKB-Bygning 5.1.1

---

### 4.2 VegFiktivGrense

**Legitimate uses:**
1. Road surface continues beyond data capture area
2. Road surface boundary unclear (e.g., gravel road merging with terrain)
3. Dataset boundary cuts through road
4. Need to close road polygon for Type 2 geometry

**Rules:**
- Use to connect open ends of Vegdekkekant or Kjørebanekant
- Should follow logical/natural line where real boundary would be
- Clearly marked as fictional in data

**Source:** FKB-Veg 5.1

---

### 4.3 VannFiktivGrense

**Legitimate uses:**
1. Water body extends beyond coverage area
2. Water boundary unclear (e.g., wetland transition)
3. Seasonal water level variation makes exact boundary uncertain

**Rules:**
- Must be clearly distinguished from natural shoreline (Kystkontur, Elvekant, etc.)
- Should represent best estimate of typical/average boundary
- Used to close water body polygons at dataset edges

**Source:** FKB-Vann 5.1

---

### 4.4 General Fictional Boundary Principles

**Key principle:** Fictional boundaries are a necessary compromise, not a preferred solution

**Best practices:**
1. Minimize use - capture real boundaries whenever possible
2. Document reason in metadata (INFORMASJON attribute)
3. Mark clearly so users know boundary is not surveyed
4. Place logically - don't create artificial geometric artifacts
5. Update to real boundaries when possible

**Validation:** Fictional boundaries are geometrically valid but semantically distinct from real boundaries

---

## 5. Historical Data and Version Compatibility

### 5.1 Legacy Data Migration

**Issue:** Older FKB data (versions 4.6, 5.0) may not meet FKB 5.1 requirements

**Handling:**
- REGISTRERINGSVERSJON attribute indicates specification version
- Data captured under older standard remains valid
- May have attributes or structure incompatible with 5.1
- May lack new mandatory attributes added in 5.1

**Specific changes:**

**FKB 5.0 → 5.1:**
- Explicit systematic deviation requirements added (≤ 1/3 × standardavvik)
- NØYAKTIGHET definition changed to true standard deviation
- Changes are minor, mostly compatible

**FKB 4.6 → 5.0:**
- Major structural changes
- New quality model (Posisjonskvalitet datatype)
- DATAFANGSTMETODE codelist replaced målemetode
- Requires migration, not just updating attributes

**Recommendation:**
- When updating dataset, bring to current specification version
- May require re-validation and metadata updates
- LOKALID should remain stable across versions (same object = same ID)

**Source:** FKB-Generell del 5.1, Section 2 (Changelog)

---

### 5.2 NØYAKTIGHET Definition Change (FKB 5.0 → 5.1)

**Critical change:** Meaning of NØYAKTIGHET attribute changed

**FKB 5.0 and earlier:**
- "Standardavvik" similar to RMS (root mean square)
- Did NOT subtract systematic deviation first
- Inconsistent with Geodatakvalitet standard

**FKB 5.1:**
- True standard deviation per Geodatakvalitet standard
- Systematic deviation explicitly defined (≤ 1/3 × standardavvik)
- Systematic and standard deviation are separate measures

**Impact:**
- FKB 5.0 NØYAKTIGHET values are NOT directly comparable to FKB 5.1
- Legacy data may need quality re-evaluation
- Cannot validate systematic deviation requirement on FKB 5.0 data

**Handling:**
- Check REGISTRERINGSVERSJON before interpreting NØYAKTIGHET
- Apply appropriate validation rules based on version
- Document version carefully in dataset metadata

**Source:** FKB-Generell del 5.1, Section 8.3

---

### 5.3 FKB-LedningVA Version 4.6

**Issue:** FKB-LedningVA specification still at version 4.6 while others are 5.x

**Implications:**
- Uses older specification structure
- May have different attribute names or codelists
- Quality model may be FKB 4.x style
- Integration with FKB 5.1 datasets requires careful handling

**Recommendation:**
- Specification should be updated to FKB 5.1
- Until updated, treat as special case in validation
- May require format/attribute mapping when integrating

**Source:** Document index analysis (FKB_LEdningVA.md version 4.6)

---

## 6. Multi-representation Objects

### 6.1 Objects with Multiple Geometry Types

**Pattern:** Same real-world object represented with different geometry types

**Example: Kjørebane (runway)**
- Primary: FLATE (area of runway surface)
- Optional: PUNKT (reference point for runway)

**Rules when multiple geometries present:**
- PUNKT must be inside FLATE
- Both representations have same LOKALID (same object)
- Attributes shared between representations

**Other examples:**
- Bygning: PUNKT (mandatory) + FLATE (optional)
- Mast: PUNKT (position) + may reference linear features (Bardun)

**Source:** Individual FKB specifications

---

### 6.2 Scale-dependent Representation

**Pattern:** Object represented differently depending on map scale / FKB standard

**Examples:**

**Small buildings:**
- FKB-A, FKB-B: PUNKT + FLATE
- FKB-C, FKB-D: PUNKT only (if building small)

**Rivers:**
- Width < 2m: KURVE (centerline)
- Width ≥ 2m: FLATE (area with boundaries)

**Roads:**
- Major roads: Full surface (VegKjørende FLATE)
- Minor roads: Centerline only (Veglenke KURVE)
- Farm roads: Simplified (TraktorvegSti)

**Decision criteria:**
- Object size relative to map scale
- Importance of object
- FKB standard (A/B/C/D)
- Local practice

**No strict thresholds:** Specifications give guidelines but exact cutoffs are implementation-specific

**Source:** Multiple FKB specifications, general principles

---

## 7. Association Multiplicity Special Cases

### 7.1 Optional vs Required Associations

**General rule:** Associations are optional unless explicitly stated as mandatory

**Exception: Type 2 flater (shared geometry)**
- Avgrensningsobjekter are **required** for Type 2 flate
- Multiplicity: [1..*] (at least one boundary object)
- Empty .REF is an error

**Other associations typically optional:**
- Mast → Bardun: [0..*] (mast may have zero or more guy wires)
- Veglenke → Fartsgrense: [0..*] (road link may have zero or more speed limits)

**Validation:** Check specification for each association's multiplicity

**Source:** UML models in FKB specifications

---

### 7.2 Zero Multiplicity Edge Cases

**Issue:** New objects not yet fully connected to network/neighbors

**Example:** New building added but neighboring buildings not yet updated to reference shared wall

**Temporary state:** Object may have 0 associated objects even if multiplicity suggests more

**Handling:**
- May be acceptable during data capture/editing
- Must be completed before final delivery
- Quality report should flag incomplete associations

**Recommendation:** Validation should distinguish between "in-progress" and "final delivery" states

**Source:** Data maintenance practice, not explicitly in specifications

---

## 8. Coordinate System Edge Cases

### 8.1 UTM Zone Boundaries

**Issue:** Norway spans multiple UTM zones (32, 33, 35)

**Assignment:**
- Trøndelag and south: UTM32 (SOSI code 22)
- Nordland and Troms: UTM33 (SOSI code 23)
- Finnmark: UTM35 (SOSI code 25)

**Edge case:** Municipality or feature spanning UTM zone boundary

**Handling:**
1. Choose primary zone based on municipality center or majority of area
2. May need dual representation in border areas (rare)
3. Document choice in dataset metadata
4. Geonorge distribution typically provides UTM33 + local zone

**Recommendation:** Stay in local UTM zone - avoid transformations if possible

**Source:** FKB-Generell del 5.1, Vedlegg B (Coordinate systems)

---

### 8.2 Svalbard Special Case

**Standard:** ETRS89 UTM zone 33 (SOSI code 25)

**Note:** Svalbard uses different UTM zone than mainland Norway despite being at similar latitude

**Reason:** Svalbard is far north where UTM zones are narrower; zone 33 provides best coverage

**Impact:** Data from Svalbard must be carefully distinguished from mainland data in same zone

**Source:** Norwegian coordinate system standards

---

## 9. MEDIUM Attribute Topology Implications

### 9.1 Under Water Features (MEDIUM = U)

**Objects:**
- Submarine cables
- Underwater pipelines
- River/lake bottom features

**Topology rules:**
- Do NOT connect to surface water features
- Can overlap with surface features (different vertical level)
- Network connectivity only within same MEDIUM level

**Special case:** Pipeline entering/exiting water
- Transition point where MEDIUM changes from T to U
- May need special network node object at transition

**Source:** FKB-Ledning, FKB-LedningVA specifications

---

### 9.2 In Building Features (MEDIUM = B)

**Objects:**
- Roof features (antennas, solar panels, etc.)
- Features on top of buildings

**Topology rules:**
- May have different accuracy than ground features
- Height reference (HREF) should be clear
- Typically not connected to ground network

**Special case:** Building entrance/exit
- Ground-level features vs. building features
- May need to distinguish access points

---

### 9.3 Above Ground Features (MEDIUM = L)

**Objects:**
- Power lines on poles
- Cable cars
- Roads on bridges
- Elevated structures

**Topology rules:**
- Do NOT connect to ground features unless explicitly at support point
- Can cross ground features without intersection
- Network connectivity only at support structures (masts, bridge piers)

**Special case:** Bridge approach
- Transition from ground level (T) to bridge (L)
- Requires careful handling at ramp/approach area

**Source:** FKB-Ledning, FKB-Veg, FKB-BygningAnlegg specifications

---

## 10. Unnamed Features

### 10.1 When NAVN is Optional

**Rule:** Most FKB objects have optional `navn` (name) attribute

**Exceptions where name is more important:**
- Roads: Road name often significant (Storgata, E6, etc.)
- Named natural features (mountains, lakes)
- Named buildings (official building names)

**Handling unnamed objects:**
- Leave `navn` attribute empty (not "Unknown" or "Unnamed")
- Do not create artificial names
- Name can be added later when known

**Source:** Individual FKB specifications, common practice

---

## 11. Data Quality Special Cases

### 11.1 Remote/Inaccessible Areas

**Issue:** Cannot achieve standard accuracy due to terrain, access restrictions, or danger

**Examples:**
- Steep cliffs
- Military restricted areas
- Dangerous industrial sites
- Islands without access

**Handling:**
1. Use lower NØYAKTIGHET value (actual achieved accuracy)
2. Document issue in INFORMASJON attribute
3. May use alternative capture method (satellite imagery, LiDAR from longer distance)
4. Flag in quality report as below standard

**Validation:** Should not fail validation if quality metadata accurately reflects actual quality (even if below requirement)

**Source:** FKB-Generell del 5.1, quality control guidelines

---

### 11.2 Temporal Features

**Issue:** Feature exists only part of year or changes seasonally

**Examples:**
- Seasonal roads (winter roads on ice)
- Temporary structures
- Seasonal water bodies
- Snow/ice features

**Handling:**
1. Use DATAFANGSTDATO to indicate when observed
2. May use SLUTTDATO if feature has known end date
3. Document temporal nature in INFORMASJON
4. May have multiple versions for different seasons

**Special object types:**
- SnøIsbre (snow/glacier) - explicitly for seasonal features
- Seasonal roads - may have specific attribute values

**Source:** FKB-Vann (for snow/ice), general FKB practice

---

## 12. Simplification and Generalization

### 12.1 Pilhøyde Variation by Object Type

**Standard rule:** Pilhøyde (max perpendicular deviation) ≤ NØYAKTIGHET

**May be looser:**
- Very smooth features (long straight roads, railway lines)
- Features where slight deviation is not significant
- Historical data captured with different standards

**Must be tighter:**
- Building corners (critical points must be preserved)
- Sharp terrain features
- Property boundaries
- Objects where accuracy is legally significant

**Recommendation:**
- Always preserve critical points (corners, endpoints, high curvature points)
- Use topology-preserving simplification
- Check pilhøyde after simplification

**Source:** FKB-Generell del 5.1, line simplification rules; Photogrammetric registration guidelines

---

### 12.2 Critical Points Must Be Preserved

**Rule:** Some vertices cannot be removed even if pilhøyde would allow

**Critical points:**
- Building corners
- Road intersection points
- Network connection points (nodes)
- Property boundary corners
- Sharp terrain features (ridge lines, drainage)

**Handling:**
- Tag critical points before simplification
- Ensure simplification algorithm preserves tagged points
- Verify after simplification that critical points remain

**Source:** General cartographic practice, FKB quality requirements

---

## Summary Statistics

- **Conditional mandatory attributes:** 5 main categories
- **Geometry type exceptions:** 3 major patterns
- **Accuracy overrides:** 2 types (higher and lower)
- **Fictional boundary types:** 4 main types
- **Version-specific issues:** 3 major compatibility concerns
- **Medium attribute levels:** 4 (T/U/B/L)
- **Coordinate system edge cases:** 2 (zone boundaries, Svalbard)

---

## Recommendations for Implementation

### High Priority (Must Handle)

1. **Check DATAFANGSTMETODE** - Apply conditional mandatory rules for photogrammetry
2. **Validate MEDIUM attribute** - Don't flag topology errors between different MEDIUM levels
3. **Handle fictional boundaries** - Recognize as special case, not error
4. **Check REGISTRERINGSVERSJON** - Apply version-appropriate validation rules
5. **Distinguish point-only vs. point+area** - Bygning and other dual-representation objects

### Medium Priority (Should Handle)

6. **UTM zone assignment** - Ensure correct zone for location
7. **Accuracy class context** - Some objects may legitimately have different accuracy
8. **Scale-dependent representation** - Don't require area geometry for small objects in FKB-C/D
9. **Network connectivity by MEDIUM** - Only validate connections within same MEDIUM level
10. **Temporal features** - Allow SLUTTDATO for removed features

### Low Priority (Nice to Handle)

11. **Historical data quality** - Accept lower accuracy with proper metadata
12. **Inaccessible areas** - Accept documented lower quality
13. **Seasonal features** - Handle temporal variations
14. **Critical point preservation** - Check after simplification
15. **Association multiplicity timing** - May be incomplete during editing

---

## Questions for Clarification (Unresolved)

While most special cases are well-documented, some areas could benefit from additional clarification:

1. **Exact thresholds for scale-dependent representation** - When exactly should small building be point-only?
2. **Fictional boundary documentation** - Should there be required metadata indicating fictional boundaries?
3. **MEDIUM transitions** - How should network nodes at MEDIUM transitions be handled?
4. **Version migration** - Are there official migration tools for FKB 4.6 → 5.1?

---

## Overall Assessment

**FKB specifications handle special cases well.** Most exceptions are clearly documented and logically justified. The main challenges are:

✅ **Clear:** Conditional mandatory attributes, fictional boundaries, MEDIUM attribute rules
✅ **Documented:** Version compatibility, coordinate systems, accuracy requirements
⚠️ **Implementation-dependent:** Scale thresholds, exact simplification rules, some multiplicity rules
⚠️ **Needs care:** MEDIUM attribute topology implications, version compatibility

**For production use:** These special cases are manageable. Document your project's decisions on implementation-dependent issues, and ensure validation tools correctly handle MEDIUM attribute and fictional boundaries.

---

*Document created: 2025-11-04*
*FKB Version: 5.1*
*Purpose: Comprehensive catalog of special cases for FKB implementation*
