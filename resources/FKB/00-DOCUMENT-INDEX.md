# FKB Specification Document Index
*Analysis Date: 2025-11-04*
*Total Documents: 15*
*Total Size: ~1.4MB*

## Document Summary Table

| # | Filename | Spec Name | Version | Date | Size | Main Topics |
|---|----------|-----------|---------|------|------|-------------|
| 1 | FKB_BYGNING_5.1.md | FKB-Bygning | 5.1.1 | 2025-01 | 124KB | Buildings, facades, roofs, building details |
| 2 | FKB_BygningAnlegg.md | FKB-BygnAnlegg | 5.1 | 2024-07 | 171KB | Bridges, tunnels, walls, technical facilities |
| 3 | FKB_GENRELL_DEL_5.md | FKB Generell Del | 5.1 | 2024-07 | 119KB | Common/Core FKB specification - base standard |
| 4 | FKB_HOYDE.md | FKB-Høydekurve | 5.0.3 | 2022-01 | 68KB | Contour lines, terrain points, elevation |
| 5 | FKB_LEDNIGN.md | FKB-Ledning | 5.1 | (version 5.1) | 108KB | Utility networks, cables, masts, stations |
| 6 | FKB_LEdningVA.md | FKB-LedningVA | 4.6 | (version 4.6) | 64KB | Water/sewage utilities, hydrants, manholes |
| 7 | FKB_LUFThavn_5.md | FKB-Lufthavn | 5.0.2 | 2022-01 | 59KB | Airport runways, taxiways, heliports, lights |
| 8 | FKB_NATUR_INFO_5.md | FKB-Naturinfo | 5.0.1 | 2022-01 | 59KB | Hedges, trees, stones, natural features |
| 9 | FKB_ORTO.md | Ortofoto | 5.0 | (version 5.0) | 74KB | Orthophoto imagery, raster products |
| 10 | FKB-Punkysky.md | Punktsky | 1.0.3 | 2022-01 | 42KB | Point clouds, LiDAR, laser scanning |
| 11 | FKB_Traktorvegsti_5.md | FKB-TraktorvegSti | 5.1 | 2024-07 | 68KB | Agricultural roads, trails, paths |
| 12 | FKB_VANN_5.md | FKB-Vann | 5.1 | 2024-07 | 94KB | Water features, coastlines, rivers, lakes |
| 13 | FKB_VEG_5.md | FKB-Veg | 5.1 | 2024-07 | 109KB | Roads, traffic areas, road markings |
| 14 | NVDB_Vegnett_pluss_1.md | NVDB Vegnett Pluss | 1.1 | 2025-09 | 133KB | Road network, traffic regulations, restrictions |
| 15 | Produksjon_av_basis_geodata_2.md | Produksjon av basis geodata | 2.0 | (version 2) | 167KB | Production standard for geodata acquisition |

**Total Size:** 1,459 KB (~1.4 MB)

---

## Detailed Document Descriptions

### 1. FKB_BYGNING_5.1.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-Bygning 5.1
**Version:** 5.1.1
**Date:** Geovekst 2025-01
**Size:** 124KB
**Status:** Approved by Geovekst

**Scope:** Specification for buildings and building structures in FKB. Covers building footprints, facades, roofs, building details and 3D building representation.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1: General elements
  - 5.2.2: Buildings (Bygning, AnnenBygning)
  - 5.2.3: Building boundaries
  - 5.2.4: Descriptive building lines
  - 5.2.5: Building appendages
  - 5.2.6: Roof overhangs
- Section 6: Reference systems
- Section 7: Quality
- Section 8: Data capture
- Section 9: Data maintenance

**Object Types Defined:** ~40+ feature types including:
- Bygning (Building)
- AnnenBygning (Other building)
- BygningsavgrensningTiltak (Building boundary)
- Bygningsdelelinje (Building division line)
- Fasadeliv (Facade line)
- FiktivBygningsavgrensning (Fictive building boundary)
- Grunnmur (Foundation wall)
- Takkant (Roof edge)
- Arkade (Arcade)
- Bygningslinje (Building line)
- Hjelpelinje3D (3D helper line)
- Hjelpepunkt3D (3D helper point)
- Mønelinje (Ridge line)
- Portrom (Portal)
- TakMur (Roof wall)
- Takplatå (Roof plateau)
- TakplatåTopp (Roof plateau top)
- Taksprang (Roof overhang)
- TaksprangBunn (Roof overhang bottom)
- BygningBru (Building bridge)
- Låvebru (Barn bridge)
- TrappBygg (Stair building)
- Veranda (Veranda)
- VeggFrittstående (Freestanding wall)
- Takoverbygg (Roof structure)
- TakoverbyggKant (Roof structure edge)

**Dependencies:**
- FKB Generell del 5.x
- SOSI del 1 versjon 5.1
- Matrikkelen (building registry)

---

### 2. FKB_BygningAnlegg.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-BygnAnlegg 5.1
**Version:** 5.1
**Date:** Geovekst 2024-07
**Size:** 171KB
**Status:** Approved by Geovekst

**Scope:** Specification for built structures and facilities that are not buildings. Includes bridges, tunnels, walls, fences, technical facilities, cultural and recreational facilities.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1: General elements (common properties)
  - 5.2.2: Bridges and tunnels
  - 5.2.3: Built facilities
  - 5.2.4: Walls and fences
  - 5.2.5: Technical facilities for culture and recreation
  - 5.2.6: Technical facilities for water/watercourse/coast
  - 5.2.7: Technical energy facilities
  - 5.2.8: Transportation facilities
- Section 6: Reference systems
- Section 7: Quality
- Section 8: Data capture

**Object Types Defined:** ~70+ feature types including:
- **Bridges/Tunnels:** Bru (Bridge), Brudetalj (Bridge detail), Kulvert (Culvert), Stikkrenne (Box culvert), Tunnelportal (Tunnel portal)
- **Built facilities:** Avfallsbeholder (Waste container), Brønn (Well), Flaggstang (Flagpole), Fundament (Foundation), Pipe (Chimney), Tank (Tank), Trapp (Stairs), Tårn (Tower)
- **Walls/Fences:** Gjerde (Fence), MurFrittstående (Freestanding wall), MurLoddrett (Vertical wall), Portstolpe (Gate post), Ruin (Ruin), Skjerm (Screen), SkråForstøtningsmur (Sloping retaining wall), Voll (Embankment)
- **Recreation:** Hoppbakke (Ski jump), Idrettsanlegg (Sports facility), Parkdetalj (Park detail), Skytebaneinnretning (Shooting range), Svømmebasseng (Swimming pool), Taubane (Cable car), Taubanemast (Cable car mast), Tribune (Grandstand)
- **Water/Coast facilities:** Demning (Dam), Elveforbygning (River revetment), Elveterskel (River threshold)

**Dependencies:**
- FKB Generell del 5.x
- Integration with NRL (National road database)
- Integration with NVDB (National road database)

---

### 3. FKB_GENRELL_DEL_5.md
**Full Title:** SOSI abstrakte spesifikasjoner: FKB generell del 5.1
**Version:** 5.1
**Date:** Geovekst 2024-07
**Size:** 119KB
**Status:** Core specification - Foundation for all FKB datasets

**Scope:** **This is the CORE/GENERAL specification** that defines common concepts, rules, and elements used by ALL FKB product specifications. It establishes the foundation for the entire FKB system.

**Main Sections:**
- Section 1: Orientation and introduction
  - 1.2: Definition of FKB (Felles KartdataBase)
  - 1.3: Purpose of FKB
  - 1.4: Responsibility for FKB
  - 1.5: Criteria for FKB
  - 1.6: Geovekst data - completeness, quality and legal validity
- Section 2: History and status
  - 2.1: Changelog (5.0 to 5.1 updates)
- Section 3: Scope
- Section 4: Normative references
- Section 5: Definitions and abbreviations
- Section 6: General about FKB
  - 6.1: FKB datasets
  - 6.2: Level of detail and data content
    - 6.2.1: Area types and FKB mapping standards (FKB-A, FKB-B, FKB-C, FKB-D)
    - 6.2.2: Height foundation in FKB
  - 6.3: Independent primary datasets
  - 6.4: Identification of objects in FKB
  - 6.5: Use of date properties
  - 6.6: Code lists
  - 6.7: Maintenance
  - 6.8: Upgrading
  - 6.9: Seamless data
- Section 7: Modeling of FKB product specifications
  - 7.1: Geometry model in FKB
  - 7.2: UML common elements for use in ApplicationSchema
    - 7.2.1.1: Fellesegenskaper (Common properties) - abstract
    - 7.2.1.2: KvalitetPåkrevd (Quality required) - abstract
    - 7.2.1.3: KvalitetOpsjonell (Quality optional) - abstract
    - 7.2.1.4: Identifikasjon (Identification) - dataType
    - 7.2.1.5: Posisjonskvalitet (Position quality) - dataType
    - 7.2.1.6-10: Common CodeLists (Synbarhet, Datafangstmetode, Registreringsversjon, Høydereferanse, Medium)
- Section 8: Quality
  - 8.1: Quality of FKB data
  - 8.2: Quality elements used to set requirements
  - 8.3: Requirements for positional accuracy - classification
  - 8.4: Deviations found during control
- Appendices:
  - Appendix A: Exchange formats for FKB data
  - Appendix B: Spatial reference systems
  - Appendix C: Associations and surface geometry in SOSI and GML format
  - Appendix D: General guidelines for photogrammetric registration of FKB (Normative)

**Object Types Defined:**
This document defines the **abstract base classes and common elements** used by all other FKB specifications:
- Fellesegenskaper (abstract feature type - common properties)
- KvalitetPåkrevd (abstract - required quality)
- KvalitetOpsjonell (abstract - optional quality)
- Identifikasjon (identification data type)
- Posisjonskvalitet (position quality data type)
- Common code lists: Synbarhet, Datafangstmetode, Registreringsversjon, Høydereferanse, Medium

**Dependencies:**
- SOSI del 1 versjon 5.1
- ISO 19107 (Spatial schema)
- ISO 19115 (Metadata)
- This specification is referenced by ALL other FKB specifications

**Special Notes:**
- **FKB Standards hierarchy:** FKB-A (most detailed), FKB-B, FKB-C, FKB-D (least detailed)
- Defines quality classes and positional accuracy requirements
- Establishes guidelines for photogrammetric registration
- Core document for understanding the entire FKB system

---

### 4. FKB_HOYDE.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-Høydekurve 5.0.3
**Version:** 5.0.3
**Date:** 2022-01-01, Published 2022-12
**Size:** 68KB
**Status:** Approved by Geovekst and Kartverket

**Scope:** Specification for describing terrain form and elevation above a given reference level. Includes contour lines, depression curves, terrain points and terrain lines. Primarily generated from terrain models based on laser scanning point clouds.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - Høydekurve (Contour line)
  - Forsenkningskurve (Depression curve)
  - Toppunkt (Peak point)
  - Forsenkningspunkt (Depression point)
  - Terrengpunkt (Terrain point)
  - Terrenglinje (Terrain line)
- Section 6: Reference systems
- Section 7: Quality
- Section 8: Data capture

**Object Types Defined:** 6 main feature types:
- Høydekurve (Contour line)
- Forsenkningskurve (Depression curve)
- Toppunkt (Peak point)
- Forsenkningspunkt (Depression point)
- Terrengpunkt (Terrain point)
- Terrenglinje (Terrain line)

**Removed from previous versions (4.6 to 5.0):**
- Hjelpekurve (Helper curve)
- TerrenglinjeBygg (Terrain line building)
- TerrenglinjeVeg (Terrain line road)
- DTMPunkt (DTM point)
- Bruddlinje (Break line)
- FyllingKant (Fill edge)
- SkjæringKant (Cut edge)

**Dependencies:**
- FKB Generell del 5.0
- SOSI del 1 versjon 5.1
- SOSI del 2 Terreng versjon 4.0
- Punktsky registration instructions

**Special Notes:**
- New contours are mainly generated from terrain models based on laser scanning point clouds
- Contour lines are a visualization of terrain models - best information comes from direct use of terrain model
- Reference to Punktsky registration instructions for FKB-Høydekurve 5.0

---

### 5. FKB_LEDNIGN.md
**Full Title:** FKB-Ledning 5.1 (filename has typo: LEDNIGN)
**Version:** 5.1
**Date:** Version 5.1 (latest)
**Size:** 108KB
**Status:** Current version

**Scope:** Specification for utility networks and cables. Covers power lines, telecommunications, cable networks, masts, stations and network infrastructure.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1: Abstract object types (KoplingGrense, KoplingSenterlinje, KoplingPunkt, Ledning, Nettverkskomponent)
  - 5.2.2: Instantiable object types (18 types)
  - 5.2.3: Code lists (7 types)
  - 5.2.4: General elements
- Section 6: Reference systems

**Object Types Defined:** 18 instantiable feature types + 5 abstract types:
- **Abstract base types:** KoplingGrense, KoplingSenterlinje, KoplingPunkt, Ledning, Nettverkskomponent
- **Network components:** Bardun (Guy wire), Flymarkør (Aviation marker), Jordingsledning (Grounding wire), Kabelkanal (Cable duct), Kum (Manhole), LedningVertikalAvstand (Vertical distance), Kumlokk (Manhole cover), Luftledning (Overhead line), Lysarmatur (Light fixture), Mast (Mast), Masteomriss (Mast outline), Nettverkstasjon (Network station), Nettverkstasjonomriss (Network station outline), Skap (Cabinet), Trase (Route/trench), Vindturbin (Wind turbine), Vindturbinomriss (Wind turbine outline), Åk (Yoke)

**Code Lists:**
- Fase (Phase)
- Kumlokkform (Manhole cover shape)
- Ledningsnettverkstype (Network type)
- Mastekonstruksjon (Mast construction)
- Punktplassering (Point placement)
- VertikalAvstandType (Vertical distance type)
- Stasjonsplassering (Station placement)

**Dependencies:**
- FKB Generell del 5.x
- SOSI standards

**Special Notes:**
- Covers power, telecom, fiber networks
- Includes wind turbine infrastructure
- Vertical distance measurements for clearance

---

### 6. FKB_LEdningVA.md
**Full Title:** SOSI Produktspesifikasjon: FKB-LedningVA 4.6
**Version:** 4.6
**Date:** Version 4.6 (older version than other specs)
**Size:** 64KB
**Status:** Version 4.6 (Note: Most other specs are at version 5.x)

**Scope:** Specification for water and sewage (VA = Vann og Avløp) utility networks. Covers hydrants, manholes, connections and VA network components visible at ground level.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.1.2: UML application schema
    - Kopling (Connection)
    - Kumlokk (Manhole cover)
    - Nettverkskomponent (Network component)
    - VA_Hydrant (Hydrant)
    - VA_Kopling (VA connection)
    - VA_Kum (VA manhole)
    - VA_Sluk (Storm drain)
  - 5.1.2.9: General concepts (common properties)
- Section 6: Reference systems
- Section 7: Quality
- Section 8: Data capture
- Section 9: Data maintenance
- Section 10: Presentation
- Section 11: Delivery
- Section 12: Additional information
- Section 13: Metadata
- Appendix A: SOSI format realization

**Object Types Defined:** 7 main feature types:
- Kopling (Connection)
- Kumlokk (Manhole cover)
- Nettverkskomponent (Network component - base type)
- VA_Hydrant (Fire hydrant)
- VA_Kopling (VA connection)
- VA_Kum (VA manhole)
- VA_Sluk (Storm drain/catch basin)

**Dependencies:**
- FKB Generell del (older version 4.x)
- SOSI standards version 4.x
- Municipal VA network systems

**Special Notes:**
- **Version mismatch:** This specification is at version 4.6 while most others are 5.x - may need updating
- Focuses on visible/surface elements of VA networks
- Important for emergency services (hydrant locations)
- Typically maintained through FDV agreements and municipal updates

---

### 7. FKB_LUFThavn_5.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-Lufthavn 5.0.2
**Version:** 5.0.2
**Date:** 2022-01-01, Published 2022-12
**Size:** 59KB
**Status:** Approved by Geovekst and Kartverket

**Scope:** Specification for airports and aviation facilities. Covers runways, taxiways, heliports, and airport lighting systems.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure (Package: ApplicationSchema FKB-Lufthavn-5.0.2)
  - 5.1.1: Rullebane (Runway)
  - 5.1.2: Taksebanegrense (Taxiway boundary)
  - 5.1.3: Helikopterlandingsplass (Heliport)
  - 5.1.4: Lufthavnlys (Airport light)
  - 5.1.5: CodeList Lufthavnlystype (Airport light type)
  - 5.1.6: Package: General elements
- Section 6: Reference systems
- Section 7: Quality
- Section 8: Data capture

**Object Types Defined:** 4 main feature types + 1 code list:
- Rullebane (Runway)
- Taksebanegrense (Taxiway boundary)
- Helikopterlandingsplass (Heliport/helicopter landing site)
- Lufthavnlys (Airport light)
- Lufthavnlystype (Airport light type - code list)

**Dependencies:**
- FKB Generell del 5.x
- SOSI del 1 versjon 5.1
- Aviation authorities' requirements

**Special Notes:**
- Small, focused specification for aviation infrastructure
- Critical for aviation safety and navigation
- Includes both fixed-wing and helicopter facilities
- Airport lighting is essential for night operations

---

### 8. FKB_NATUR_INFO_5.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-Naturinfo 5.0.1
**Version:** 5.0.1
**Date:** 2022-01-01, Published 2022-12
**Size:** 59KB
**Status:** Approved by Geovekst and Kartverket

**Scope:** Specification for natural information that doesn't fall under other natural resource chapters. Specifically covers hedges, surveyed trees and stones. Small, focused dataset for discrete natural features.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - Hekk (Hedge)
  - InnmåltTre (Surveyed tree)
  - Stein (Stone)
- Section 6: Reference systems
- Section 7: Quality
- Section 8: Data capture

**Object Types Defined:** 3 main feature types:
- Hekk (Hedge) - with tree type property
- InnmåltTre (Surveyed tree) - individual mapped trees with tree type property
- Stein (Stone) - modeled with wholly-owned surface geometry

**Removed from previous version (4.6 to 5.0):**
- SteinOmriss (Stone outline - merged into Stein as wholly-owned geometry)
- Allé (Avenue/tree-lined path - removed as not actively mapped/maintained)

**Dependencies:**
- FKB Generell del 5.0
- SOSI del 1 versjon 5.1
- Fotogrammetrisk registreringsinstruks (Photogrammetric registration instructions) for FKB-Naturinfo 5.0

**Special Notes:**
- Small, focused specification
- Tree type (tretype) and height reference (høydereferanse) are required properties
- Objects are typically mapped photogrammetrically
- Individual features of landscape/cultural significance

---

### 9. FKB_ORTO.md
**Full Title:** Produktspesifikasjon for ortofoto
**Version:** 5.0
**Date:** Version 5.0
**Size:** 74KB
**Status:** Current version

**Scope:** Specification for orthophoto products - geometrically corrected aerial/satellite imagery. Covers orthophoto production, quality requirements, and metadata for raster image products.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.1.1: Ortofoto v. 5.0
    - 5.1.1.1: Ortofotoprosjekt (Orthophoto project)
    - 5.1.1.2: Ortofotobilde (Orthophoto image)
    - 5.1.1.3: Ortofotoavgrensning (Orthophoto boundary)
    - 5.1.1.4: Ortofotoprosjektavgrensning (Orthophoto project boundary)
    - 5.1.1.5: Raster (Raster)
    - 5.1.1.6-8: Data types (Bilde, Datautstrekning, Utstrekning)
    - 5.1.1.9-12: Code lists (Bildekategori, Opptaksmetode, Orienteringsmetode, Ortofototype)
- Section 6: Reference systems
- Section 7: Quality
  - 7.1.1: Requirements for visual orthophoto quality
  - 7.1.2: Requirements for positional accuracy
- Section 8: Data capture and special production requirements
  - 8.1: Geodetic foundation
  - 8.2: Aerial photography
  - 8.3: Image orientation
  - 8.4: Terrain model
  - 8.5: Production of orthophoto products
  - 8.6: Delivery to management solution
- Section 9: Data maintenance
- Section 10: Presentation
- Section 11: Delivery
- Section 12: Appendices
  - Appendix A: SOSI format realization
  - Appendix B: Examples of visual quality
  - Appendix C: Example of raster object

**Object Types Defined:** 5 feature types + 4 code lists:
- **Feature types:** Ortofotoprosjekt, Ortofotobilde, Ortofotoavgrensning, Ortofotoprosjektavgrensning, Raster
- **Data types:** Bilde (Image), Datautstrekning (Data extent), Utstrekning (Extent)
- **Code lists:** Bildekategori (Image category), Opptaksmetode (Capture method), Orienteringsmetode (Orientation method), Ortofototype (Orthophoto type)

**Dependencies:**
- Aerial photography specifications
- Terrain models (DTM/DSM)
- Image processing standards
- SOSI raster specifications

**Special Notes:**
- **Raster product specification** - different from vector FKB data
- Defines true orthophoto vs. simple rectified images
- Includes quality requirements for visual appearance and positional accuracy
- Critical for base mapping and visual interpretation
- Requires terrain model for production
- Delivery includes metadata, project files, and reports

---

### 10. FKB-Punkysky.md
**Full Title:** Produktspesifikasjon: Punktsky 1.0.3
**Version:** 1.0.3
**Date:** 2022-01-01, Published 2023-02
**Size:** 42KB
**Status:** Approved by Geovekst and Kartverket

**Scope:** Specification for point cloud data from various acquisition methods (LiDAR, photogrammetry, sonar). This is the raw/processed point cloud data that forms the basis for many other FKB products.

**Main Sections:**
- Section 1: Introduction, history and changelog
  - 1.3.3: Replaces FKB-Laser 3.0
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.1: Common components
  - 5.2: Airborne Topographic LiDAR
  - 5.3: Airborne Bathymetric LiDAR
  - 5.4: Terrestrial Topographic LiDAR
  - 5.5: Multibeam Echo Sounder
  - 5.6: Image matching (photogrammetry)
- Section 6: Reference systems
- Section 7: Quality
  - 7.1: Requirements for point density
  - 7.2: Accuracy
- Section 8: Data capture
- Section 9: Data maintenance
- Section 10: Presentation
- Section 11: Delivery
  - 11.1: Point cloud delivery
  - 11.2: Metadata delivery
  - 11.3: Report
  - 11.4: Delivery structure
- Section 12: Additional information
- Section 13: Metadata
- Section 14: Appendix A - Point cloud classification
  - 14.1: Precision for Class 17 - Bridge
  - 14.2: Precision for Class 13, 14, 15 - Utility line classes

**Acquisition Methods Covered:**
1. **Airborne Topographic LiDAR** - aerial laser scanning
2. **Airborne Bathymetric LiDAR** - underwater laser scanning
3. **Terrestrial Topographic LiDAR** - ground-based laser scanning
4. **Multibeam Echo Sounder** - underwater acoustic scanning
5. **Image Matching** - point clouds from photogrammetry

**Dependencies:**
- Replaces FKB-Laser 3.0
- Used as source data for: FKB-Høydekurve, terrain models, building models
- ASPRS LAS format standards
- Point cloud classification standards

**Special Notes:**
- **Foundation dataset** for many other FKB products
- Includes classification scheme for point clouds (Appendix A)
- Different requirements for different acquisition methods
- Point density requirements vary by application
- Accuracy requirements for different classes
- Special attention to bridges (Class 17) and utility lines (Classes 13-15)
- Delivery includes homogeneity plots, control surfaces, flight strips

---

### 11. FKB_Traktorvegsti_5.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-TraktorvegSti 5.1
**Version:** 5.1
**Date:** Geovekst 2024-07
**Size:** 68KB
**Status:** Approved by Geovekst

**Scope:** Specification for agricultural roads, tractor roads, trails and paths not included in the main road network (FKB-Veg). Covers rural access roads, farm roads, forest roads, and recreational trails.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1: Veglenke (Road link)
  - 5.2.2: Vegsperring (Road barrier)
  - 5.2.3-6: Data types (Vegsystemreferanse, Vegsystem, Vegstrekning, Veglenkeadresse)
  - 5.2.7-15: Code lists (Vegkategori, Vegfase, FunksjonVegsperring, TypeVegsperring, Typeveg, KlasseLandbruksveg, Rutemerking, Kommunenummer, EierVegsperring)
  - 5.2.16: Package: General elements
- Section 6: Reference systems

**Object Types Defined:** 2 main feature types + 9 code lists:
- **Feature types:**
  - Veglenke (Road link)
  - Vegsperring (Road barrier)
- **Data types:**
  - Vegsystemreferanse (Road system reference)
  - Vegsystem (Road system)
  - Vegstrekning (Road section)
  - Veglenkeadresse (Road link address)
- **Code lists:**
  - Vegkategori (Road category)
  - Vegfase (Road phase)
  - FunksjonVegsperring (Barrier function)
  - TypeVegsperring (Barrier type)
  - Typeveg (Road type)
  - KlasseLandbruksveg (Agricultural road class)
  - Rutemerking (Route marking)
  - Kommunenummer (Municipality number)
  - EierVegsperring (Barrier owner)

**Dependencies:**
- FKB Generell del 5.1
- SOSI road network model
- Integration with NVDB for road system references
- Related to FKB-Veg (main roads)

**Special Notes:**
- Focuses on roads NOT in main road network
- Important for agriculture, forestry, and recreation
- Includes hiking trails, forest roads, farm access
- Road barriers (gates, booms) to control access
- Agricultural road classification system
- Route marking for recreational trails

---

### 12. FKB_VANN_5.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-Vann 5.1
**Version:** 5.1
**Date:** Geovekst 2024-07
**Size:** 94KB
**Status:** Approved by Geovekst

**Scope:** Specification for water features - coastlines, seas, rivers, streams, canals, lakes, glaciers, and water boundaries. Comprehensive water feature dataset.

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1-18: Feature types (water boundaries and areas)
  - 5.2.19: Package: General elements
  - 5.2.20: Package: Data types and code lists
- Section 6: Reference systems

**Object Types Defined:** 18 feature types + 4 code lists:
- **Coastal features:**
  - Kystkontur (Coastline)
  - KystkonturTekniskeAnlegg (Coastline technical facilities)
  - Skjær (Skerry/reef)
  - Havflate (Sea surface)
- **Rivers and streams:**
  - Elvekant (River edge)
  - Elv (River - area)
  - ElvBekk (River/stream - centerline)
- **Canals:**
  - Kanalkant (Canal edge)
  - Kanal (Canal - area)
  - KanalGrøft (Canal/ditch - centerline)
- **Lakes:**
  - Innsjøkant (Lake edge)
  - Innsjø (Lake - area)
- **Other water features:**
  - VeggrøftÅpen (Open road ditch)
  - SnøIsbreKant (Snow/glacier edge)
  - SnøIsbre (Snow/glacier - area)
  - Flomløpkant (Flood channel edge)
  - VannFiktivGrense (Water fictive boundary)
  - KonnekteringVann (Water connection)
- **Code lists:**
  - Kystkonstruksjonstype (Coastal construction type)
  - Kystreferanse (Coast reference)
  - VannBredde (Water width)
  - VannSperretype (Water barrier type)

**Dependencies:**
- FKB Generell del 5.1
- SOSI del 1 versjon 5.1
- Integration with N50 Kartdata (national mapping)
- Hydrological databases

**Special Notes:**
- Dual representation: edges (boundaries) and areas (surfaces)
- Centerline representation for narrow features (ElvBekk, KanalGrøft)
- Coastal features include technical constructions (piers, breakwaters)
- Glaciers and permanent snow included
- Water width classification
- Important for flood management and hydrological analysis

---

### 13. FKB_VEG_5.md
**Full Title:** SOSI-standardisert produktspesifikasjon: FKB-Veg 5.1
**Version:** 5.1
**Date:** Geovekst 2024-07
**Size:** 109KB
**Status:** Approved by Geovekst

**Scope:** Specification for road surfaces, road boundaries, traffic areas, road markings, and road furniture. Covers the physical/visible road infrastructure. Complements NVDB Vegnett Pluss (road network).

**Main Sections:**
- Section 1: Introduction, history and changelog
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1: Package: General elements
  - 5.2.2: Package: Surface objects (flateobjekter)
  - 5.2.3: Package: Surface boundaries (flateavgrensninger)
  - 5.2.4: Package: Other objects
  - 5.2.5: Package: Data types and code lists
- Section 6: Reference systems

**Object Types Defined:** ~25 feature types:
- **Surface objects (areas):**
  - Parkeringsområde (Parking area)
  - Trafikkøy (Traffic island)
  - VegGåendeOgSyklende (Road for pedestrians and cyclists)
  - VegKjørende (Road for vehicles)
- **Surface boundaries (lines):**
  - VegAnnenAvgrensning (Road other boundary)
  - Vegdekkekant (Road surface edge)
  - VegFiktivGrense (Road fictive boundary)
- **Other road objects:**
  - AnnetVegarealAvgrensning (Other road area boundary)
  - FartsdemperAvgrensning (Speed bump boundary)
  - FeristAvgrensning (Cattle guard boundary)
  - GangfeltAvgrensning (Crosswalk boundary)
  - Kantstein (Curb)
  - Kjørebanekant (Carriageway edge)
  - OverkjørbartArealAvgrensning (Drivable area boundary)
  - Skiltportal (Sign portal)
  - Trafikksignalpunkt (Traffic signal point)
  - Vegbom (Road boom/gate)
  - Vegoppmerking (Road marking)
  - Vegrekkverk (Road barrier/guardrail)
  - Vegskulderkant (Road shoulder edge)
- **Data types:**
  - Vegsystemreferanse (Road system reference)
  - Vegsystem (Road system)
- **Code lists:**
  - Vegkategori, Vegfase, FunksjonVegsperring, TypeVegbom, TypevegGåendeOgSyklende, TypevegKjørende, BruksområdeVegoppmerking, TypeVegrekkverk

**Dependencies:**
- FKB Generell del 5.1
- SOSI del 1 versjon 5.1
- **Strong integration with NVDB** (National Road Database)
- **Relationship with NVDB Vegnett Pluss** - FKB-Veg covers physical features, NVDB covers network/topology
- Related to FKB-TraktorvegSti (minor roads)

**Special Notes:**
- Focuses on **physical/visible road features** (surfaces, edges, markings)
- NVDB objects included (abstract types NVDBobjekter)
- Separates pedestrian/cyclist areas from vehicle areas
- Road furniture (signs, signals, barriers)
- Important for navigation, mapping, and road management
- Dual model: FKB-Veg (physical) + NVDB Vegnett Pluss (network)

---

### 14. NVDB_Vegnett_pluss_1.md
**Full Title:** SOSI-standardisert produktspesifikasjon: NVDB Vegnett Pluss 1.1
**Version:** 1.1
**Date:** Kartverket 2025-09
**Size:** 133KB
**Status:** Approved by Kartverket (newest document in collection)

**Scope:** National Road Database (NVDB) road network specification. Focuses on road network topology, routing, traffic regulations, and restrictions. Complements FKB-Veg (physical roads). Replaces Elveg 2.0.

**Main Sections:**
- Section 1: Introduction, history and changelog
  - 1.3.2: Changes from Elveg 2.0 to NVDB Vegnett Pluss 1.0
- Section 2: Definitions and abbreviations
- Section 3: General about the specification
- Section 4: Specification scope
- Section 5: Content and structure
  - 5.2.1: Package: Veglenke (road link)
  - 5.2.2: Package: NVDB object types (18 types)
  - 5.2.3: Package: Common properties
  - 5.2.4: Package: Data types and code lists
- Section 6: Reference systems

**Object Types Defined:** 19 feature types (1 base + 18 NVDB objects):
- **Base network:**
  - Veglenke (Road link - the base network segment)
- **NVDB regulation/restriction objects:**
  - Beredskapsveg (Emergency road)
  - Fartsgrense (Speed limit)
  - FartsgrenseVariabel (Variable speed limit)
  - Ferjesamband (Ferry connection)
  - FunksjonellVegklasse (Functional road class)
  - GjennomkjøringForbudt (Through traffic prohibited)
  - GjennomkjøringForbudtTil (Through traffic prohibited to)
  - Gågatereguleringer (Pedestrian street regulations)
  - Høydebegrensning (Height restriction)
  - Jernbanekryssing (Railway crossing)
  - Landbruksvegklasse (Agricultural road class)
  - Motorveg (Motorway)
  - Serviceveg (Service road)
  - Svingerestriksjon (Turn restriction)
  - TillattKjøreretning (Permitted driving direction)
  - Trafikkreguleringer (Traffic regulations)
  - Vegsperring (Road barrier)
  - VærutsattVeg (Weather-exposed road)

**Data types and code lists:** Extensive set including:
- **Veglenke types:** Veglenkeadresse, Kryssystem, Sideanlegg, Vegstrekning, Vegsystem, Vegsystemreferanse
- **Code lists:** Referanseretning, TypeVeg, Vegdetaljnivå, Vegkategori, AdskilteLøp, Vegfase
- **NVDB code lists:** BruksområdeBeredskapsveg, Funksjon, særskiltFare, AnsvarligVTS, DriftsstatusFerjesamband, EierVegsperring, etc.

**Dependencies:**
- FKB Generell del
- SOSI road network standards
- **Replaces Elveg 2.0**
- **Complements FKB-Veg 5.1** (physical roads)
- NVDB (National Road Database) - Statens vegvesen

**Special Notes:**
- **Network/topology focused** - not physical features
- Veglenke (road link) is the base network element
- Rich attribute model with 18 NVDB object types
- Traffic regulations and restrictions for routing
- Variable speed limits
- Ferry connections as part of road network
- Turn restrictions for navigation
- Weather-exposed roads for winter maintenance
- Railway crossings for safety
- **Newest specification** (2025-09) in the collection
- Critical for GPS navigation, routing applications
- Maintained by Statens vegvesen (Norwegian Public Roads Administration)

---

### 15. Produksjon_av_basis_geodata_2.md
**Full Title:** Standard for geografisk informasjon: Produksjon av basis geodata 2.0
**Version:** 2.0
**Date:** Version 2.0
**Size:** 167KB (largest document)
**Status:** Production standard - methodological guide

**Scope:** **PRODUCTION STANDARD** for acquiring basis geodata. This is NOT a product specification but a **methodological standard** covering HOW to produce geodata using geodetic methods, photogrammetry, laser scanning. The "cookbook" for FKB data acquisition.

**Main Sections:**
- Section 1: Orientation and introduction
  - 1.1: Use of requirements in the standard
  - 1.2: History and status
  - 1.3: Changelog (version 1 to version 2)
- Section 2: Scope
- Section 3: Normative references
- Section 4: Terms and abbreviations
- Section 5: **Mapping with geodetic methods**
  - 5.1: Introduction
  - 5.2: Measurement methods
    - 5.2.1: Satellite-based methods (GNSS)
      - 5.2.1.1: Real-time measurement
      - 5.2.1.2: Transformations
    - 5.2.2: Use of total station
  - 5.3: Measurement instruments
  - 5.4: Calculation
  - 5.5: Self-control and reporting (geodetic mapping)
- Section 6: **Mapping with photogrammetry**
  - 6.1: Flight and signal planning
    - 6.1.1: Flight photography planning (flight plan)
    - 6.1.2: Ground control point and signaling planning
    - 6.1.3: Requirements for content and presentation of flight and signal plan
  - 6.2: Signaling
    - 6.2.1: Legal authority for field work (Matrikkellova)
    - 6.2.2: Execution of signaling
    - 6.2.3: Self-control and reporting (signaling report)
  - 6.3: Aerial photography
    - 6.3.1: Requirements for camera system
    - 6.3.2: Execution of photography
    - 6.3.3: Calculation of GNSS/INS data
    - 6.3.4: Production of images
    - 6.3.5: Self-control and reporting (photo report)
  - 6.4: Aerotriangulation
    - 6.4.1: Requirements for measurement work
    - 6.4.2: Requirements for calculation work
    - 6.4.3: Self-control and reporting (AT report)
  - 6.5: Map construction
    - 6.5.1: Preparation
    - 6.5.2: Construction
    - 6.5.3: Finalization
    - 6.5.4: Self-control and reporting (construction)
  - 6.6: Image matching for elevation modeling
  - 6.7: Orthophoto production
    - 6.7.1: Foundation (signaling, photography, AT, height model)
    - 6.7.2: Orthophoto types (true orthophoto vs. simple orthophoto)
    - 6.7.3: Orthophoto resolution
    - 6.7.4: Production of orthophoto
    - 6.7.5: Orthophoto mosaic
    - 6.7.6: Self-control and reporting (orthophoto report)
  - 6.8: **Photography with drone**
    - 6.8.1: Prequalification of drone system and supplier
    - 6.8.2: Camera
    - 6.8.3: GNSS/INS
    - 6.8.4: Signaling
    - 6.8.5: Flight plan
    - 6.8.6: Requirements for photography
    - 6.8.7: Photogrammetric construction
- Section 7: **Mapping with airborne laser scanning**
  - 7.1: Introduction
    - 7.1.1: Operating principle (laser scanner, position/rotation system)
    - 7.1.2: Products and applications
    - 7.1.3: Expected accuracy
  - 7.2: Execution of laser scanning
    - 7.2.1: Calibration of laser scanner (vendor, installation, daily)
    - 7.2.2: Planning of laser scanning (flight plan, cross strips, control surfaces, control profiles)

**Methodology Areas Covered:**
1. **Geodetic surveying:** GNSS (RTK, PPK), total station
2. **Photogrammetry:** Aerial photography, aerotriangulation, stereo compilation
3. **Drone mapping:** UAV/drone requirements and workflows
4. **Laser scanning:** Airborne LiDAR acquisition and processing
5. **Orthophoto production:** True ortho and simple rectified products
6. **Image matching:** Dense matching for terrain models

**Dependencies:**
- All FKB product specifications (5.x versions)
- Punktsky specification
- Geodatakvalitet standard
- ISO metadata standards
- Equipment calibration standards

**Special Notes:**
- **NOT a product specification** - it's a **production methodology standard**
- Defines HOW to acquire data, not WHAT data to acquire
- Extensive quality control and reporting requirements
- Each section includes self-control and reporting subsections
- Covers traditional and modern methods (total station to drones)
- Legal framework (Matrikkellova) for field access
- Calibration requirements for instruments
- **Largest specification** (167KB) - comprehensive methodology guide
- Essential reference for contractors and data producers
- Used by Geovekst partners for quality assurance

---

## Cross-Reference Notes

### Core/General Specification
**FKB_GENRELL_DEL_5.md (FKB Generell del 5.1)** is the CORE specification that defines:
- Common abstract base classes used by all FKB specs
- FKB system architecture and principles
- Quality classes and accuracy requirements
- Data model conventions (UML modeling rules)
- Exchange formats (SOSI, GML)
- All other FKB specifications reference this document

### Version Alignment
**Version 5.1 (Latest - 2024/2025):**
- FKB_BYGNING_5.1.md (5.1.1, 2025-01) - **NEWEST**
- FKB_BygningAnlegg.md (5.1, 2024-07)
- FKB_GENRELL_DEL_5.md (5.1, 2024-07)
- FKB_LEDNIGN.md (5.1)
- FKB_Traktorvegsti_5.md (5.1, 2024-07)
- FKB_VANN_5.md (5.1, 2024-07)
- FKB_VEG_5.md (5.1, 2024-07)
- NVDB_Vegnett_pluss_1.md (1.1, 2025-09) - **NEWEST, different numbering**

**Version 5.0 (2022):**
- FKB_HOYDE.md (5.0.3, 2022-01)
- FKB_LUFThavn_5.md (5.0.2, 2022-01)
- FKB_NATUR_INFO_5.md (5.0.1, 2022-01)
- FKB_ORTO.md (5.0)

**Version 4.6 (Older - needs update?):**
- FKB_LEdningVA.md (4.6) - **VERSION MISMATCH - older than others**

**Version 1.0 (Point cloud - different series):**
- FKB-Punkysky.md (1.0.3, 2022-01) - Replaces FKB-Laser 3.0

**Version 2.0 (Production standard):**
- Produksjon_av_basis_geodata_2.md (2.0) - Methodology, not product spec

### Specification Relationships and Overlaps

**Building/Structure Hierarchy:**
- **FKB_BYGNING_5.1.md** - Buildings proper (residential, commercial)
- **FKB_BygningAnlegg.md** - Built structures (bridges, walls, technical facilities)
- Overlap: Some structure types could fit both (e.g., tårn/tower, tank)

**Road Network - Dual Model:**
- **FKB_VEG_5.md** - Physical road surfaces, markings, furniture (WHAT you see)
- **NVDB_Vegnett_pluss_1.md** - Road network topology, regulations, routing (HOW you navigate)
- **FKB_Traktorvegsti_5.md** - Minor roads/trails not in main network
- These three specifications work together to provide complete road coverage

**Utility Networks:**
- **FKB_LEDNIGN.md** - General utility networks (power, telecom, fiber)
- **FKB_LEdningVA.md** - Water/sewage networks specifically
- Overlap: Kumlokk (manhole cover) appears in both

**Water Features:**
- **FKB_VANN_5.md** - Natural water features (rivers, lakes, coast)
- **FKB_BygningAnlegg.md** - Technical water/coast facilities (dams, revetments)
- Overlap: Water-related structures may reference both specs

**Natural Features:**
- **FKB_NATUR_INFO_5.md** - Discrete features (trees, stones, hedges)
- **FKB_VANN_5.md** - Water and glaciers
- **FKB_HOYDE.md** - Terrain/elevation

**Base Data Acquisition:**
- **FKB-Punkysky.md** - Point cloud acquisition (foundation data)
- **FKB_HOYDE.md** - Products derived from point clouds (contours, terrain points)
- **FKB_ORTO.md** - Orthophoto products from aerial imagery
- **Produksjon_av_basis_geodata_2.md** - HOW to acquire all of the above

### Integration Points

**NVDB Integration (National Road Database):**
- NVDB_Vegnett_pluss_1.md explicitly integrates with NVDB
- FKB_VEG_5.md has abstract types for NVDB objects (NVDBobjekter)
- FKB_BygningAnlegg.md references NRL and NVDB

**Matrikkelen Integration (Building Registry):**
- FKB_BYGNING_5.1.md links to official building registry
- Kommunenummer (municipality number) used across multiple specs

**SOSI Standards:**
- All FKB specs reference SOSI del 1 versjon 5.1
- All use SOSI UML modeling rules
- FKB_GENRELL_DEL_5.md defines SOSI implementation for FKB

### Quality Levels (FKB-A/B/C/D)
Defined in FKB_GENRELL_DEL_5.md:
- **FKB-A:** Most detailed (urban areas, high precision)
- **FKB-B:** Detailed (built-up areas)
- **FKB-C:** Standard (rural areas)
- **FKB-D:** Basic (remote areas)

All product specifications must specify content for each level.

### Temporal Coverage
- **2025 updates:** FKB_BYGNING_5.1.md (5.1.1, Jan 2025), NVDB_Vegnett_pluss_1.md (1.1, Sep 2025)
- **2024 updates:** 7 specifications updated to version 5.1 (July 2024)
- **2022 baseline:** Version 5.0 series established (Jan 2022)
- **Version 4.6:** One legacy spec remains (FKB_LEdningVA.md)

---

## Usage Recommendations

### For Understanding FKB System:
1. **Start with:** FKB_GENRELL_DEL_5.md - Understand the foundation
2. **Then review:** Produksjon_av_basis_geodata_2.md - Understand acquisition methods
3. **Then explore:** Individual product specs based on your domain

### For Data Production:
1. **Methodology:** Produksjon_av_basis_geodata_2.md
2. **Base data:** FKB-Punkysky.md, FKB_ORTO.md
3. **Product specs:** Relevant FKB_*.md files for your domain
4. **Quality:** FKB_GENRELL_DEL_5.md Section 8

### For Application Development:
1. **Data model:** FKB_GENRELL_DEL_5.md Section 7
2. **Exchange formats:** FKB_GENRELL_DEL_5.md Appendix A
3. **Product specs:** Relevant domain specifications
4. **Code lists:** Each specification defines domain-specific code lists

### For Navigation/Routing Applications:
- **Primary:** NVDB_Vegnett_pluss_1.md (network topology, regulations)
- **Secondary:** FKB_VEG_5.md (physical road features), FKB_Traktorvegsti_5.md (trails)

### For Building/Facility Management:
- **Buildings:** FKB_BYGNING_5.1.md
- **Infrastructure:** FKB_BygningAnlegg.md
- **Utilities:** FKB_LEDNIGN.md, FKB_LEdningVA.md

### For Environmental/Natural Resource Management:
- **Water:** FKB_VANN_5.md
- **Terrain:** FKB_HOYDE.md, FKB-Punkysky.md
- **Natural features:** FKB_NATUR_INFO_5.md

---

## Document Metadata Summary

**Responsible Organizations:**
- **Geovekst:** Main responsibility for FKB specifications
- **Kartverket:** Formal approval authority
- **Statens vegvesen:** NVDB Vegnett Pluss maintenance
- **Standardiseringskomiteen for Geomatikk:** Standards approval

**File Formats:**
- All specifications available in: HTML, PDF, GML schema
- UML models available online
- SOSI format realization included

**Status as of Analysis (2025-11-04):**
- 7 specifications at version 5.1 (2024-2025)
- 4 specifications at version 5.0.x (2022)
- 1 specification at version 4.6 (legacy - **recommend updating FKB_LEdningVA.md**)
- 1 specification at version 1.0.3 (point cloud - different series)
- 1 specification at version 1.1 (NVDB - different series)
- 1 production standard at version 2.0 (methodology)

**Total Object Types:** Approximately 300+ feature types across all specifications
**Total Size:** 1,459 KB (1.4 MB) of documentation

---

*Document Index created: 2025-11-04*
*Analysis tool: FKB Specification Document Analyzer*
*Source directory: /home/torsaan/Documents/Githubproj/GEO_MCP/FKB/Spesifications/*
