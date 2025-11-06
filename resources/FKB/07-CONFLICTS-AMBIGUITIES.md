# FKB Conflicts and Ambiguities

*Analysis Date: 2025-11-04*
*Purpose: Document unclear rules requiring clarification or official guidance*

## Methodology

This document catalogs:
1. **Conflicts:** Contradictory rules across specifications (if found)
2. **Ambiguities:** Unclear or insufficiently specified requirements
3. **Gaps:** Missing information needed for complete implementation

All analyzed specifications: FKB 5.0/5.1 versions (15 documents total)

---

## 1. Conflicts Across Specifications

### Assessment: NO DIRECT CONFLICTS FOUND

After thorough analysis of all FKB 5.1 specifications, **no direct contradictions** were identified between specifications.

**Findings:**
- ✅ FKB-Generell del 5.1 provides consistent foundation
- ✅ Individual specifications reference common rules consistently
- ✅ Terminology is consistent across specifications
- ✅ No cases of "Specification A says X, Specification B says NOT X"

**Note:** FKB_LEdningVA.md at version 4.6 may have minor inconsistencies with 5.1 specifications, but this is a version mismatch, not a conflict within the 5.1 family.

**Conclusion:** FKB 5.1 specifications are **internally consistent**.

---

## 2. Ambiguities Requiring Clarification

Despite overall consistency, several areas lack precise specification and require interpretation or assumptions for implementation.

---

### A2.1: Snap Tolerance Undefined

**Issue:** Specifications state objects should "connect" or "snap" but don't define numerical tolerance

**Context:** Network features (roads, utilities, water networks)

**What specifications say:**
- "Veglenker skal knytte seg sammen i endepunkter" (Road links should connect at endpoints)
- "Ledningssegmenter danner sammenhengende nettverk" (Utility segments form connected network)
- Quality measure: "Antall ulovlige løse ender" (Number of illegal dangling ends)

**What is NOT specified:**
- Exact distance threshold for "connected" vs "nearby but not connected"
- Whether threshold varies by FKB standard (A/B/C/D)
- Whether threshold varies by accuracy class (1/2/3/4)

**Impact:**
- Unclear when two endpoints are "connected" vs "close but disconnected"
- Different validation tools may use different tolerances
- Inconsistent validation results between implementations

**Recommended interpretation:**
- Use **2 × standardavvik** as snap tolerance
- For FKB-A Class 1: 20 cm
- For FKB-B Class 2: 40 cm
- For FKB-C/D Class 2: 110 cm

**Rationale:**
- 2σ covers ~95% of positioning variation
- Allows for normal measurement uncertainty
- Prevents false positive connections

**Status:** ⚠️ AMBIGUOUS - needs official clarification or specification update

**Priority:** HIGH - affects all network validation

**Source:** FKB-Generell del 5.1 (quality measures), individual specifications (network rules)

---

### A2.2: "Ulovlig løs ende" Definition

**Issue:** "Illegal dangling end" (ulovlig løs ende) mentioned but not precisely defined

**Context:** Network features - roads, utilities, trails

**What specifications say:**
- Quality measure exists: "Antall ulovlige løse ender"
- Implies some dangling ends are legal, others illegal
- No explicit definition of when dangling is legal vs illegal

**What is NOT specified:**
- Exact criteria for "illegal" vs "legal" dangling end
- Whether dangling at dataset boundary is legal
- Whether cul-de-sac is legal dangling end
- Whether disconnected network fragment is allowed

**Reasonable interpretations:**

**Legal dangling ends:**
- Network ends at dataset boundary
- Cul-de-sac (dead end street)
- Ferry terminal (network continues by ferry)
- Explicitly marked incomplete feature
- Network terminator (hydrant, transformer, etc.)

**Illegal dangling ends:**
- Network segment disconnected due to data error
- Missing connection where physical connection exists
- Endpoint that should connect to another segment within snap tolerance

**Status:** ⚠️ AMBIGUOUS - needs case-by-case or contextual interpretation

**Priority:** MEDIUM - affects network quality control

**Recommendation:**
- Consult detailed registration instructions (registreringsinstruks) for each object type
- Use spatial context (is endpoint near dataset boundary?)
- Check for nearby endpoints within snap tolerance (likely connection error)

**Source:** FKB-Generell del 5.1 section 8.2 (Quality measures)

---

### A2.3: Minimum Polygon Size Thresholds

**Issue:** "Små polygoner skal ikke registreres" (small polygons should not be registered) - but threshold not specified

**Context:** Various area features across FKB specifications

**What specifications say:**
- General principle that very small polygons should be omitted
- Some object-specific guidance (e.g., Bru minimum 10 m²)
- No systematic thresholds for most object types

**What is NOT specified:**
- Minimum area for most polygon object types
- Whether threshold varies by FKB standard (A/B/C/D)
- Whether threshold is strict or guideline

**Known thresholds:**
- Bru (Bridge): 10 m² minimum (FKB-Punktsky classification rules)
- Other objects: Unspecified

**Impact:**
- Unclear when small polygon should be point representation instead
- Inconsistent between data producers
- May lead to overly detailed data in some areas, generalized in others

**Reasonable approach:**
- Threshold should depend on FKB standard and map scale
- FKB-A: Smaller thresholds (capture more detail)
- FKB-D: Larger thresholds (generalize more)
- Should be consistent within dataset

**Status:** ⚠️ AMBIGUOUS - needs per-object or per-standard specification

**Priority:** MEDIUM - affects level of detail and data volume

**Recommendation:**
- Project/producer should document thresholds used
- Consult registreringsinstruks for guidance
- Consider: Can feature be meaningfully shown at map scale?

**Source:** Multiple specifications, FKB-Punktsky (bridge classification), general principles

---

### A2.4: Pilhøyde Exact Application Method

**Issue:** Pilhøyde rule (max deviation ≤ NØYAKTIGHET) is clear, but application method has ambiguities

**Rule:** "Pilhøyde (maksimal tverrfeilavvik) ved linjeforenkling skal ikke overstige nøyaktighetskravet"

**Context:** Line simplification for all KURVE objects

**What IS specified:**
- Maximum perpendicular deviation must be ≤ NØYAKTIGHET value
- Applies to line simplification operations

**What is NOT fully specified:**

1. **Measurement method:**
   - 2D perpendicular distance (plan view)?
   - 3D perpendicular distance?
   - Vertical component separate?

2. **Application:**
   - Every vertex checked?
   - Sampled points?
   - Only at simplified-away vertices?

3. **Reference:**
   - Perpendicular to simplified line?
   - Perpendicular to original line?
   - Shortest distance to line?

**Reasonable interpretation:**
- **2D perpendicular distance** in horizontal plane (most common)
- **Applied to removed vertices** - checking deviation of original points from simplified line
- **Perpendicular distance** to simplified line segment

**Mathematical approach:**
- Use Douglas-Peucker algorithm with epsilon = NØYAKTIGHET value
- Ensure topology preservation (shared boundaries simplified identically)

**Status:** ⚠️ PARTIALLY AMBIGUOUS - core concept clear but implementation details vary

**Priority:** MEDIUM - affects line quality and data volume

**Recommendation:**
- Use standard GIS simplification tools (preserve topology = TRUE)
- Douglas-Peucker with tolerance = NØYAKTIGHET is acceptable
- Always preserve critical points (corners, endpoints, high curvature)

**Source:** FKB-Generell del 5.1, photogrammetric registration guidelines

---

### A2.5: Association Validation Timing

**Issue:** When should association references be validated and enforced?

**Context:** Object associations and references (.REF in SOSI, associations in UML)

**What is NOT specified:**
- Must associations be valid during editing?
- Can objects temporarily have broken references?
- When is final validation required?
- Are there intermediate validation checkpoints?

**Scenarios:**

**During data capture/editing:**
- New object created, not yet linked to neighbors
- Object deleted, references from other objects not yet updated
- Partial dataset extracted for editing

**Before delivery:**
- All references should resolve
- All mandatory associations should be populated
- Multiplicities should be satisfied

**Practical implications:**
- Editing tools: May allow temporary broken references
- Validation tools: Should distinguish "in-progress" vs "delivery" mode
- Quality reports: Should flag unresolved references as errors for delivery

**Status:** ⚠️ AMBIGUOUS - lifecycle state not explicitly defined

**Priority:** MEDIUM - affects validation workflow design

**Recommendation:**
- **During editing:** Allow incomplete associations (with warnings)
- **Before delivery:** Mandatory validation - all references must resolve
- **Distinguish validation modes:** "real-time editing" vs "final QC"

**Source:** General practice, not explicitly in specifications

---

## 3. Information Gaps

These are areas where information exists elsewhere but is not included in core FKB specifications.

---

### G3.1: Code List Versioning

**Gap:** Code lists (Datafangstmetode, Bygningstype, etc.) may evolve over time

**Issue:**
- Code lists hosted at register.geonorge.no
- No clear versioning scheme visible in FKB specifications
- Old code values may become invalid
- New code values may be added

**Impact:**
- Validation against code lists may fail if using old list
- Historical data may have codes no longer in current list
- Unclear which code list version to use for which FKB version

**Current practice:**
- Code lists referenced by URL: https://register.geonorge.no/sosi-kodelister/fkb/...
- Presumably latest version served
- No explicit version in URL or specification

**Status:** ⚠️ PROCESS GAP - versioning methodology not documented

**Priority:** LOW - rare practical issue but important for long-term data management

**Recommendation:**
- Check register.geonorge.no for current code lists
- Historical data: Validate against code list valid at DATAFANGSTDATO
- Future improvement: Version code lists explicitly

**Source:** FKB specifications reference code lists by URL

---

### G3.2: Coordinate Transformation Parameters

**Gap:** SOSI file specifies CRS (.KOORDSYS) but not transformation parameters

**Issue:**
- Multiple transformations may exist between coordinate systems
- Transformation choice affects accuracy (sub-meter to centimeter level)
- Important for FKB data with millimeter precision

**Example:**
- EUREF89 UTM → WGS84: Multiple transformation methods
- NN2000 → NN1954: Specific transformation grid needed
- Geoid model for ellipsoid height → orthometric height

**Current specification:**
- .KOORDSYS specifies system (22/23/25 for UTM32/33/35)
- .VERT-DATUM specifies vertical datum (NN2000/NN1954)
- Transformation parameters not in SOSI file

**Status:** ⚠️ DOCUMENTATION GAP - transformations defined elsewhere (Kartverket standards)

**Priority:** MEDIUM - important for coordinate operations

**Recommendation:**
- Use official transformations from Kartverket
- NMA transformation services (NMATRANS)
- Document transformation used in processing metadata

**Source:** SOSI format specification, Kartverket transformation standards

---

### G3.3: Detailed Registration Instructions

**Gap:** Specifications give rules, but detailed capture procedures are in separate documents

**Issue:**
- FKB specifications: What to capture and quality requirements
- Registreringsinstruks: How to capture and interpret features
- Fotogrammetrisk registreringsinstruks: Photogrammetric capture procedures

**These are separate document series:**
- "Produktspesifikasjon" (product specification) - this analysis
- "Registreringsinstruks" (registration instruction) - separate documents
- "Fotogrammetrisk veiledning" (photogrammetric guidance) - appendices

**Status:** ✅ EXPECTED - not a true gap, just division of documentation

**Priority:** N/A - by design

**Recommendation:**
- Consult registreringsinstruks for detailed capture rules
- Use photogrammetric appendices for aerial mapping
- Specifications define "what" and "quality", instructions define "how"

**Source:** FKB documentation structure

---

## 4. Version-Specific Issues

---

### V4.1: FKB 5.0 vs 5.1 - Systematic Deviation Requirements

**Change:** FKB 5.1 introduces explicit systematic deviation requirements

**FKB 5.0:**
- "Standardavvik" defined similar to RMS
- No separate systematic deviation requirement
- Did not fully conform to Geodatakvalitet standard

**FKB 5.1:**
- True standard deviation per Geodatakvalitet
- Systematic deviation explicitly: ≤ 1/3 × standardavvik
- Separate validation of systematic and random deviations

**Impact on legacy data:**
- FKB 5.0 data lacks systematic deviation information
- Cannot validate systematic deviation requirement on old data
- NØYAKTIGHET values not directly comparable between versions

**Handling:**
- Check REGISTRERINGSVERSJON attribute
- Apply version-appropriate validation rules
- Legacy data remains valid under FKB 5.0 rules

**Status:** ✅ EXPECTED VERSION DIFFERENCE - documented in specifications

**Priority:** HIGH - affects validation of mixed-version datasets

**Recommendation:**
- Document which FKB version data was captured under
- Apply appropriate quality model for version
- When updating, bring to FKB 5.1 quality model

**Source:** FKB-Generell del 5.1, Section 2 (Changelog), Section 8.3 (Quality requirements)

---

### V4.2: FKB-LedningVA Still at Version 4.6

**Issue:** FKB_LEdningVA.md specification at version 4.6 while most others are 5.x

**Differences from FKB 5.1:**
- May use older quality model (målemetode instead of datafangstmetode)
- May have different attribute structure
- Possibly different coordinate system handling
- Different code lists

**Impact:**
- Integration with FKB 5.1 datasets requires careful mapping
- Validation tools need to handle version 4.6 structure
- May have attribute name conflicts or incompatibilities

**Status:** ⚠️ KNOWN ISSUE - specification needs updating

**Priority:** MEDIUM - affects VA utility integration

**Recommendation:**
- Update FKB-LedningVA to version 5.1
- Until updated: treat as special case in multi-dataset projects
- Document version in integration/validation procedures

**Source:** Document index analysis (00-DOCUMENT-INDEX.md)

---

## 5. Implementation Challenges

These are not specification problems but areas where implementation is complex or difficult.

---

### I5.1: Type 2 Flate Validation Complexity

**Challenge:** Validating "område = sum(boundaries)" is geometrically complex

**Technical issues:**

1. **Union operation may fail:**
   - Boundaries with small gaps or overlaps
   - Floating-point precision issues
   - Self-intersections in union result

2. **Equals comparison sensitive:**
   - Coordinate precision (1 cm in FKB)
   - Tolerance handling
   - Different geometry representations (WKT, WKB)

3. **Topology errors in boundaries:**
   - Gaps between boundary segments
   - Overlapping boundary segments
   - Boundary direction (positive/negative references)

4. **Performance:**
   - Union is expensive operation (O(n log n) or worse)
   - Large datasets require optimization
   - Spatial indexing essential

**Recommended approach:**

1. **Use robust geometry libraries:**
   - PostGIS (database)
   - Shapely (Python)
   - JTS (Java)
   - GEOS (C++)

2. **Apply tolerance:**
   - Use accuracy class standard deviation as tolerance
   - ST_Equals(geom1, geom2, tolerance)
   - Buffer-and-intersect method as alternative

3. **Validate incrementally:**
   - Check boundary closure first
   - Then check union validity
   - Finally check equals with tolerance

4. **Optimize for large datasets:**
   - Spatial index (R-tree)
   - Parallel processing (tile/chunk)
   - Cache union results

**Status:** ⚠️ IMPLEMENTATION COMPLEXITY: HIGH

**Priority:** CRITICAL - most important FKB topology rule

**Recommendation:**
- Use mature GIS database (PostGIS) for validation
- Implement tolerance carefully
- Test with real-world FKB data
- Have fallback for edge cases

**Source:** FKB-Generell del 5.1 Type 2 geometry, practical experience

---

### I5.2: Large Dataset Performance

**Challenge:** Full topology validation on large datasets (millions of objects)

**Issues:**

1. **Spatial queries without indexing:**
   - O(n²) complexity for finding neighbors
   - Point-in-polygon tests on many features
   - Network connectivity validation

2. **Cross-tile references:**
   - Dataset split into tiles for processing
   - Objects reference objects in other tiles
   - Requires global ID lookup

3. **Memory constraints:**
   - Loading entire dataset into memory may not be possible
   - Geometry operations memory-intensive
   - Union of millions of polygons

**Recommended approach:**

1. **Use spatial database:**
   - PostGIS with spatial index
   - R-tree or similar indexing
   - Query optimization

2. **Tile-based processing:**
   - Split dataset into manageable tiles
   - Process tiles in parallel
   - Handle cross-tile references carefully

3. **Incremental validation:**
   - Validate as data is created (editing tools)
   - Final validation checks only critical rules
   - Cache validation results

4. **Selective validation:**
   - Full validation on changed objects only
   - Topology validation on connected neighbors
   - Statistical sampling for quality assessment

**Status:** ⚠️ IMPLEMENTATION COMPLEXITY: HIGH

**Priority:** MEDIUM - important for production systems

**Recommendation:**
- Invest in proper database infrastructure
- Use spatial database, not flat files
- Implement tiling/chunking strategy
- Design for incremental validation

**Source:** Practical experience with large geodatasets

---

## 6. Recommendations for Clarification

Prioritized list of items that would benefit from official clarification or specification updates.

---

### Priority: HIGH

1. **Define snap tolerance explicitly**
   - **Recommendation:** Snap tolerance = 2 × standardavvik
   - **Why:** Critical for all network validation
   - **Impact:** Ensures consistent validation across implementations

2. **Define småpolygon thresholds**
   - **Recommendation:** Per FKB standard and object type
   - **Example:** FKB-A buildings: 4 m², FKB-C buildings: 25 m²
   - **Why:** Affects data detail level and consistency

3. **Clarify legal vs illegal dangling ends**
   - **Recommendation:** Explicit list of legitimate dangling cases
   - **Why:** Affects network quality assessment
   - **Impact:** Reduces false positives in validation

---

### Priority: MEDIUM

4. **Pilhøyde application method**
   - **Recommendation:** 2D perpendicular distance to simplified line
   - **Why:** Ensures consistent simplification quality
   - **Impact:** Minor - most implementations already use this

5. **Association validation timing**
   - **Recommendation:** Distinguish editing vs delivery validation modes
   - **Why:** Improves user experience in editing tools
   - **Impact:** Moderate - affects workflow design

6. **Coordinate transformation specification**
   - **Recommendation:** Reference Kartverket transformation services explicitly
   - **Why:** Ensures accuracy preservation
   - **Impact:** Important for multi-CRS workflows

---

### Priority: LOW

7. **Code list versioning**
   - **Recommendation:** Add version/date to code list URIs
   - **Why:** Improves long-term data management
   - **Impact:** Low - current system works adequately

8. **Update FKB-LedningVA to version 5.1**
   - **Recommendation:** Migrate specification to 5.1 structure
   - **Why:** Consistency with other FKB datasets
   - **Impact:** Moderate - affects VA utility integration

---

## 7. Questions for Standards Body

If consulting with Kartverket or Geovekst standardization committee, these questions would be valuable:

---

### Q1: Snap Tolerance

**Question:** What is the official snap tolerance for determining network connectivity?

**Context:** Validation of "Antall ulovlige løse ender" quality measure

**Options:**
- A) 2 × standardavvik for accuracy class
- B) 3 × standardavvik
- C) Fixed value (e.g., 50 cm)
- D) Implementation-dependent

**Our recommendation:** Option A (2 × standardavvik)

**Status:** ⏳ Awaiting official guidance

---

### Q2: Pilhøyde Calculation

**Question:** Should pilhøyde be calculated in 2D (horizontal) or 3D (including vertical component)?

**Context:** Line simplification quality control

**Options:**
- A) 2D perpendicular distance (horizontal plane only)
- B) 3D perpendicular distance (full spatial distance)
- C) Separate horizontal and vertical thresholds

**Our recommendation:** Option A (2D) for most features, Option C for elevation-critical features

**Status:** ⏳ Awaiting official guidance

---

### Q3: Småpolygon Thresholds

**Question:** Are there recommended minimum area thresholds for polygon features by FKB standard?

**Context:** Deciding when to represent feature as point vs polygon

**Request:** Table of thresholds per object type and FKB standard

**Status:** ⏳ Awaiting official guidance

---

### Q4: Fictional Boundary Metadata

**Question:** Should fictional boundaries have special metadata or flag to indicate they are not surveyed?

**Context:** Distinguishing surveyed boundaries from fictional/estimated ones

**Options:**
- A) Use separate OBJTYPE (current approach - FiktivBygningsavgrensning, VegFiktivGrense)
- B) Add boolean attribute "fiktiv" to boundary objects
- C) Use specific DATAFANGSTMETODE code
- D) Document in INFORMASJON attribute

**Current approach:** Option A (separate OBJTYPE)

**Status:** ✅ Already handled, but could be more systematic

---

## 8. Summary

---

### Conflict Assessment: ✅ NO CONFLICTS

FKB 5.1 specifications are **internally consistent** with no contradictory rules identified.

---

### Ambiguity Assessment: ⚠️ MODERATE AMBIGUITY

**Total ambiguities identified:** 5 significant

**Breakdown:**
- Snap tolerance: HIGH priority
- Illegal dangling ends: MEDIUM priority
- Småpolygon thresholds: MEDIUM priority
- Pilhøyde application: MEDIUM priority
- Association validation timing: MEDIUM priority

---

### Information Gap Assessment: ⚠️ MINOR GAPS

**Total gaps identified:** 3

**Breakdown:**
- Code list versioning: LOW priority
- Transformation parameters: MEDIUM priority
- Detailed registration instructions: N/A (by design)

---

### Implementation Complexity: ⚠️ MODERATE TO HIGH

**Major challenges:**
- Type 2 flate validation: HIGH complexity
- Large dataset performance: HIGH complexity

**Both are solvable with proper tools and infrastructure.**

---

### Version Issues: ⚠️ MINOR

**Issues identified:** 2

**Breakdown:**
- FKB 5.0 vs 5.1 differences: Expected, well-documented
- FKB-LedningVA version 4.6: Should be updated

---

## 9. Overall Assessment

**FKB 5.1 specifications are generally clear and well-defined.**

**Strengths:**
- ✅ Object types and attributes clearly specified
- ✅ Geometry types and validity rules well-defined
- ✅ Accuracy requirements explicit and detailed
- ✅ Metadata requirements comprehensive
- ✅ File format (SOSI) thoroughly documented
- ✅ No internal conflicts or contradictions

**Areas needing improvement:**
- ⚠️ Numeric thresholds (snap tolerance, minimum sizes) - need explicit values
- ⚠️ Validation procedures (timing, methods) - need process clarification
- ⚠️ Implementation guidance (complex topology checks) - need technical guidance

**Production readiness:**
- ✅ Suitable for production implementation
- ✅ Ambiguities can be resolved with documented assumptions
- ✅ Most implementation challenges are technical, not specification issues

**Recommendations:**
1. Document project-specific decisions for ambiguous areas
2. Use 2 × standardavvik as snap tolerance (awaiting official confirmation)
3. Use mature GIS tools (PostGIS, QGIS, FME) for topology validation
4. Implement tolerance handling carefully for Type 2 flate validation
5. Consider requesting specification updates for high-priority ambiguities

---

**Conclusion:** FKB 5.1 is a **mature, well-designed specification** suitable for production use. The identified ambiguities are manageable and mostly relate to implementation details rather than fundamental specification problems.

---

*Document created: 2025-11-04*
*Analysis basis: 15 FKB specification documents*
*Assessment: Internal consistency CONFIRMED, ambiguities DOCUMENTED*
