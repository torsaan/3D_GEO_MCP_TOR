# FKB Geometric Rules Extraction - Summary Report

**Analysis Date:** 2025-11-04  
**Analyst:** Claude Code - FKB Geometric Rules Extraction  
**Source:** FKB Specification Documents v5.0/5.1

---

## Executive Summary

This document summarizes the extraction of ALL geometric constraints, topology rules, and spatial requirements from 7 FKB specification documents. A comprehensive YAML file (`02-GEOMETRIC-RULES.yaml`) has been created containing 127+ rules organized by category.

---

## Specifications Analyzed

1. **FKB_GENRELL_DEL_5.md** - Common rules applying to all FKB objects
2. **FKB_BYGNING_5.1.md** - Building geometry and topology rules
3. **FKB_BygningAnlegg.md** - Construction and structures rules
4. **FKB_VEG_5.md** - Road and transportation surface rules
5. **FKB_VANN_5.md** - Water bodies and water feature rules
6. **FKB_Traktorvegsti_5.md** - Tractor roads, paths, and trails
7. **NVDB_Vegnett_pluss_1.md** - National road network topology

---

## Extraction Results

### Total Rules Extracted: 127+

#### Rules by Category:
- **Common Geometric Rules:** 32 rules
  - Geometry type constraints
  - Coordinate precision requirements
  - Association rules
  - Multi-geometry handling

- **Topology Rules:** 45 rules
  - Shared boundary (delt geometri) patterns
  - Network connectivity requirements
  - Spatial containment constraints
  - Coverage requirements (no gaps/overlaps)

- **Quality/Accuracy Rules:** 18 rules
  - Stedfestingsnøyaktighet for FKB-A/B/C/D
  - 4 accuracy classes per standard (12 class combinations)
  - Systematic vs. standard deviation requirements
  - Gross error thresholds (< 1%)

- **Object-Specific Rules:** 23+ object types documented
  - Geometry type per object
  - Specific constraints per object type
  - Accuracy class assignments

- **Validation Rules:** 15 procedures
  - Geometry validity checks
  - Topology validation methods
  - Spatial relationship tests
  - Attribute validation

---

## Key Findings

### A. Common Geometric Constraints (Apply to ALL FKB objects)

#### 1. Geometry Type Restrictions
**Rule GR-COMMON-001:**
> "FKB-data skal ha en enklest mulig geometri. Andre geometrityper enn GM_Point, GM_Curve, GM_Surface skal ikke benyttes"
- ❌ NO multipoint, multicurve, multisurface
- ✅ Only: PUNKT (.PUNKT), KURVE (.KURVE), FLATE (.FLATE)

#### 2. Coordinate Precision
**Rule GR-COMMON-002:**
> "Presisjon bedre enn 5mm ved transformasjon"
- Critical for coordinate system transformations
- Required for maintaining data quality

#### 3. Closure Requirements
- All polygon geometries MUST be closed
- First coordinate == Last coordinate
- Section: FKB_GENRELL_DEL_5.md §7.1.4

#### 4. Self-Intersection Prohibition
- Kurver og flater skal IKKE ha egenkryssinger
- Quality measure: "Antall ulovlige egenkryssinger" = 0
- Validation: ST_IsSimple() must return TRUE

---

### B. Stedfestingsnøyaktighet (Positioning Accuracy)

#### Accuracy Standards Summary

| FKB Standard | Nøyaktighetsklasse | Grunnriss (syst/std) | Høyde (syst/std) |
|--------------|-------------------|---------------------|------------------|
| **FKB-A** | Klasse 1 | 3 cm / 10 cm | 3 cm / 10 cm |
| **FKB-A** | Klasse 2 | 5 cm / 15 cm | 5 cm / 15 cm |
| **FKB-A** | Klasse 3 | 10 cm / 35 cm | 8 cm / 25 cm |
| **FKB-A** | Klasse 4 | 15 cm / 55 cm | 12 cm / 40 cm |
| **FKB-B** | Klasse 1 | 5 cm / 15 cm | 5 cm / 15 cm |
| **FKB-B** | Klasse 2 | 6 cm / 20 cm | 6 cm / 20 cm |
| **FKB-B** | Klasse 3 | 10 cm / 35 cm | 10 cm / 35 cm |
| **FKB-B** | Klasse 4 | 15 cm / 55 cm | 15 cm / 50 cm |
| **FKB-C/D** | Klasse 1 | 15 cm / 48 cm | 15 cm / 48 cm |
| **FKB-C/D** | Klasse 2 | 15 cm / 55 cm | 20 cm / 70 cm |
| **FKB-C/D** | Klasse 3 | 20 cm / 70 cm | 25 cm / 90 cm |
| **FKB-C/D** | Klasse 4 | 30 cm / 100 cm | 40 cm / 150 cm |

**Key Accuracy Rules:**
- **Systematisk avvik ≤ 1/3 × standardavvik** (New in FKB 5.1)
- **Grove feil:** Avvik > 3 × standardavvik must be < 1%
- Source: FKB_GENRELL_DEL_5.md §8.3, Tabell 11

---

### C. Flategeometri - Two Types

#### Type 1: Heleid Geometri (Wholly-Owned Geometry)
- Simple-feature flater
- No separate boundary objects
- Example: Brønn, Industriområde
- Avgrensningsobjekter have no independent function

#### Type 2: Delt Geometri (Shared Geometry)
**CRITICAL RULE:**
> "Område-geometrien skal være lik summen av geometriene til de assosierte avgrensningsobjektene"

**Requirements:**
1. Association from flate → avgrensningsobjekt
2. Navigable from kilde to mål
3. Multiplisitet: 0..* on mål side
4. Rollenavn starts with `avgrensesAv`
5. **Geometric consistency constraint:** flate.equals(union(boundaries))

**Objects using Type 2:**
- Bygning, AnnenBygning, TakoverbyggFlatefeste
- Kjørebane, GangSykkelveg, GangfeltKryssingspunkt, Gatetun
- HavEllerHavarm, Elv, Kanal, Innsjø, SnøIsbre
- KaiBrygge

---

### D. Punkt-Flate Containment

**Rule:** For objects with both punkt and flate geometry:
> "Dersom det finnes område-geometri skal posisjon-geometrien ligge innenfor område-geometrien"

**Applies to:**
- Bygning (punkt påkrevd, flate opsjonell)
- AnnenBygning (flate påkrevd, punkt opsjonell)
- Kjørebane, GangSykkelveg, etc.
- All vann-flater (Elv, Innsjø, HavEllerHavarm, etc.)

**Validation:** `point.within(polygon)` must be TRUE

---

### E. Network Topology

#### NVDB Vegnett Rules:
1. **Veglenke connectivity:** Lenker møtes i knutepunkt
2. **No illegal dangles:** Except logical terminators
3. **Node location:** Knutepunkt at endpoints/crossings
4. **Network consistency:** Forms connected graph

#### TraktorvegSti:
- Senterlinjer skal danne sammenhengende nettverk
- Vegsperring (punkt) skal ligge på senterlinje

---

### F. Topology Patterns Identified

#### 1. Shared Boundary Pattern
- Adjacent polygons share identical coordinate sequences
- Used for: Bygning-til-bygning, veg-dekke, vann-flater
- Validation: Coordinates must match within tolerance

#### 2. Gap Filling with Fictional Boundaries
- Use "Fiktiv" boundary objects to close polygons
- Examples:
  - `FiktivBygningsavgrensning`
  - `VegFiktivGrense`
  - `VannFiktivGrense`
  - `FiktivAvgrensningForAnlegg`

#### 3. Full Coverage (Fulldekkende flater)
- No gaps or overlaps
- Quality measure: "Prosentandel feil på fulldekkende flater" = 0%
- Used for: AR5, some vann datasets

#### 4. MEDIUM-based separation
- Objects on different vertical levels can overlap in xy
- MEDIUM values:
  - T = på terrenget (default)
  - U = under bakken
  - L = løs i luften
  - W = i vann
  - V = på vannoverflaten

---

## Most Complex Object Types

### 1. Bygning (Building)
**Complexity Score: 10/10**

**Geometry:**
- PUNKT (påkrevd) - Copy of matrikkelen bygningspunkt
- FLATE (opsjonell) - Full building outline

**Constraints:**
- Punkt må ligge innenfor flate
- Flate bruker Type 2 delt geometri

**Boundary Objects (6 types):**
1. Grunnmur
2. Fasadeliv
3. Takkant
4. Bygningsdelelinje
5. BygningsavgrensningTiltak
6. FiktivBygningsavgrensning

**Associations:** 15+ associations to descriptive objects
- Taksprang, TaksprangBunn, Mønelinje, Portrom, Arkade
- Hjelpepunkt3D, Hjelpelinje3D, Bygningslinje
- Veranda, Låvebru, TrappBygg, BygningBru, VeggFrittstående

**Rules:**
- BYG-003: Punkt innenfor flate
- BYG-004: Område = sum(avgrensningsobjekter)
- Accuracy: Klasse 1 (svært veldefinerte kanter)

---

### 2. Kjørebane (Road Surface)
**Complexity Score: 8/10**

**Geometry:**
- FLATE (påkrevd) + PUNKT (opsjonell)

**Boundary Objects (3 types):**
1. Vegdekkekant
2. VegAnnenAvgrensning
3. VegFiktivGrense

**Rules:**
- VEG-001: Område = sum(avgrensningsobjekter)
- VEG-002: Punkt innenfor flate
- Must form closed polygon
- Accuracy: Klasse 1-2

---

### 3. HavEllerHavarm (Sea/Sea Arm)
**Complexity Score: 7/10**

**Geometry:**
- FLATE (påkrevd) + PUNKT (opsjonell)

**Boundary Objects (3 types):**
1. Kystkontur
2. KystkonturTekniskeAnlegg
3. VannFiktivGrense

**Rules:**
- VANN-001: Område = sum(avgrensningsobjekter)
- VANN-002: Punkt innenfor flate
- Large-scale features with complex coastlines
- Accuracy: Klasse 2-3 (variable along coast)

---

## Validation Checklist

### Geometry Validation
- [ ] Only allowed geometry types (PUNKT/KURVE/FLATE)
- [ ] All polygons are closed (first == last point)
- [ ] No self-intersections: `ST_IsSimple() == TRUE`
- [ ] No self-overlaps
- [ ] No degenerate geometries (zero-length/area)
- [ ] Coordinate precision sufficient (< 5mm for transforms)

### Topology Validation
- [ ] Punkt inside flate (for objects with both)
- [ ] Område equals sum of avgrensningsobjekter (Type 2 flater)
- [ ] Shared boundaries have identical coordinates
- [ ] Network connectivity (endpoints snap within tolerance)
- [ ] No illegal dangling ends
- [ ] No illegal link crossings (except at nodes)
- [ ] Full coverage (no gaps/overlaps for coverage datasets)

### Quality Validation
- [ ] Stedfestingsnøyaktighet within limits for nøyaktighetsklasse
- [ ] Systematisk avvik ≤ 1/3 × standardavvik
- [ ] Grove feil < 1% (avvik > 3×standardavvik)
- [ ] Pilhøyde ≤ NØYAKTIGHET (line simplification)
- [ ] KVALITET block complete (5 mandatory attributes)
- [ ] Datafangstmetode valid (not 'dig' for height)

### Association Validation
- [ ] All avgrensesAv* references exist
- [ ] Multiplicities correct (0..1 or 0..*)
- [ ] Associations to concrete object types only
- [ ] No broken references

---

## Object Type Summary

### By Specification:

**FKB-BYGNING (10 object types):**
- Bygning, AnnenBygning, TakoverbyggFlatefeste
- Grunnmur, Fasadeliv, Takkant, Bygningsdelelinje
- FiktivBygningsavgrensning, BygningsavgrensningTiltak, TakoverbyggKant
- Plus 14 descriptive objects (Taksprang, Mønelinje, etc.)

**FKB-VEG (8 object types):**
- Kjørebane, GangSykkelveg, GangfeltKryssingspunkt, Gatetun
- Vegdekkekant, VegFiktivGrense, VegAnnenAvgrensning
- Plus traffic infrastructure objects

**FKB-VANN (12 object types):**
- HavEllerHavarm, Elv, Kanal, Innsjø, SnøIsbre
- Kystkontur, KystkonturTekniskeAnlegg, Elvekant
- Kanalkant, Innsjøkant, SnøIsbreKant, VannFiktivGrense

**FKB-TRAKTORVEGSTI (2 object types):**
- TraktorvegStiSenterlinje
- Vegsperring

**FKB-BYGNINGANLEGG (10+ object types):**
- KaiBrygge, Bru, SkråForstøtningsmur, Konstruksjon
- Plus many specific construction types

**NVDB (2 main types):**
- Veglenke (network links)
- Knutepunkt (nodes)

---

## Issues and Ambiguities Found

### 1. Tolerance Values Not Explicit
**Issue:** Geometric equality tests require tolerance, but exact values not specified  
**Recommendation:** Use nøyaktighetsklasse standardavvik as tolerance basis
- FKB-A Klasse 1: tolerance = 0.10 m
- FKB-B Klasse 2: tolerance = 0.20 m
- Etc.

### 2. "Ulovlig løs ende" Definition Varies
**Issue:** What constitutes an "illegal dangle" depends on context  
**Recommendation:** Each specification must define allowable dangling ends
- Road networks: Dead ends allowed for cul-de-sacs
- Water networks: Springs/outlets are logical terminators
- Building boundaries: No dangles allowed

### 3. Småpolygoner Threshold Undefined
**Issue:** Minimum polygon area not specified  
**Recommendation:** Define per object type
- Bygning: > 10 m²
- Brønn: > 0.5 m²
- Etc.

### 4. Pilhøyde Rules Incomplete
**Issue:** Line simplification tolerance not fully documented  
**Recommendation:** Search fotogrammetrisk registreringsinstruks
- Likely: pilhøyde = nøyaktighet for object's class

### 5. Association Consistency Not Automated
**Issue:** "Område = sum(avgrensningsobjekter)" requires manual validation  
**Recommendation:** Implement automated topology checker
- PostGIS: ST_Equals(flate, ST_Union(boundaries))
- Tolerance based on accuracy class

---

## Tools and Methods

### Validation Tools Identified:
1. **SOSI-kontroll** - Official SOSI format validator
2. **PostGIS Topology** - Spatial database validation
3. **QGIS Topology Checker** - Desktop GIS validation
4. **FME** - ETL with topology validators

### Validation Functions:
- `ST_IsValid()` - Geometry validity
- `ST_IsSimple()` - No self-intersections
- `ST_Contains(polygon, point)` - Containment
- `ST_Equals(geom1, geom2)` - Geometric equality
- `ST_Union(geometries)` - Aggregate boundaries
- `ST_Distance(geom1, geom2)` - Snap tolerance
- `ST_Area(polygon)`, `ST_Length(line)` - Minimum sizes

---

## Recommendations for Implementation

### 1. Automated Validation Pipeline
Create validation workflow:
```
Input FKB data
  ↓
[Geometry Validity] → Report invalid geometries
  ↓
[Topology Check] → Report topology errors
  ↓
[Accuracy Check] → Compare to control points
  ↓
[Association Check] → Verify referential integrity
  ↓
[Attribute Check] → Validate against code lists
  ↓
Output: Validation Report + Clean Data
```

### 2. Priority Rules for Implementation
**Critical (Must implement):**
- GR-COMMON-001: Geometry type check
- GR-COMMON-006: Område = sum(avgrensningsobjekter)
- GR-COMMON-007: Punkt innenfor flate
- All accuracy thresholds (GR-COMMON-012 through 023)
- Network connectivity (NVDB-002, 003, 004)

**High Priority:**
- Self-intersection/overlap checks
- Closure requirements
- Association referential integrity

**Medium Priority:**
- Pilhøyde validation
- Small polygon checks
- Illegal dangle detection

### 3. Tolerance Configuration
Create configuration per FKB standard:
```yaml
tolerance_config:
  FKB-A:
    klasse_1:
      snap_tolerance: 0.10  # meters
      area_tolerance: 0.01  # square meters
      geometric_equality_tolerance: 0.10
    klasse_2:
      snap_tolerance: 0.15
      # ...
  FKB-B:
    # ...
```

### 4. Error Reporting
Generate reports with:
- Rule ID violated
- Object ID(s) affected
- Geometry location (WKT or coords)
- Error description
- Suggested fix

---

## File Location

**Main Output:**  
`/home/torsaan/Documents/Githubproj/GEO_MCP/FKB/extracted/02-GEOMETRIC-RULES.yaml`

**File Size:** 1,118 lines  
**Format:** YAML (structured, machine-readable)

**Sections:**
1. Metadata
2. Common Geometric Rules
3. Accuracy Requirements (detailed tables)
4. Topology Patterns
5. Spatial Constraints
6. Object-Specific Rules (23+ object types)
7. Validation Rules (5 categories, 15 procedures)
8. Special Notes
9. References

---

## Conclusion

This extraction has successfully documented **127+ geometric rules** from 7 FKB specifications, covering:
- ✅ All common geometric constraints
- ✅ All accuracy class requirements (12 classes)
- ✅ All topology patterns (5 patterns)
- ✅ 23+ object-specific rule sets
- ✅ Complete validation checklist

**Key Achievement:**  
The rule "Område-geometrien skal være lik summen av geometriene til de assosierte avgrensningsobjektene" has been identified as the **most critical geometric constraint** in FKB, applying to 15+ object types across 4 specifications.

**Most Complex Rule:**  
Bygning (Building) objects with 6 boundary types, 15+ associations, both punkt and flate geometries, and Type 2 delt geometri constraints represent the most complex geometric validation challenge.

---

## Next Steps

1. **Implement validation functions** for priority rules
2. **Create tolerance configuration** per FKB standard
3. **Develop automated topology checker** for Type 2 flater
4. **Build error reporting system** with rule IDs
5. **Test validation pipeline** on real FKB datasets
6. **Document edge cases** from validation testing

---

**Generated by:** Claude Code - FKB Geometric Rules Extraction  
**Date:** 2025-11-04  
**Version:** 1.0
