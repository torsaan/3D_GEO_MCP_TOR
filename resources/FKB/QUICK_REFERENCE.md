# FKB Attribute Extraction - Quick Reference

## Files Generated

### Main Output
**`/home/torsaan/Documents/Githubproj/GEO_MCP/FKB/extracted/01-MANDATORY-ATTRIBUTES.yaml`**
- Size: 191 KB (5,143 lines)
- Format: Structured YAML
- Contains: 164 object types with 485 total attributes

### Documentation
**`/home/torsaan/Documents/Githubproj/GEO_MCP/FKB/extracted/EXTRACTION_SUMMARY.md`**
- Complete analysis and recommendations
- Statistics and patterns
- Known limitations

**`/home/torsaan/Documents/Githubproj/GEO_MCP/FKB/extracted/QUICK_REFERENCE.md`**
- This file - quick lookup reference

## Quick Stats

```
Total Object Types:        164
Total Mandatory Attributes: 264
Total Optional Attributes:  221
Specifications Processed:   7 of 15
Most Complex Object:        GjennomkjøringForbudt (19 attributes)
```

## Specifications Successfully Extracted

| # | Specification | Objects | Notes |
|---|---------------|---------|-------|
| 1 | FKB_BYGNING_5.1 | 26 | Buildings |
| 2 | FKB_BygningAnlegg | 54 | Building facilities (largest) |
| 3 | FKB_VEG_5 | 25 | Roads |
| 4 | FKB_VANN_5 | 18 | Water features |
| 5 | FKB_Traktorvegsti_5 | 2 | Tractor roads |
| 6 | FKB_LEDNIGN | 18 | Utility lines |
| 7 | NVDB_Vegnett_pluss_1 | 21 | Road network |

## Common Attributes (Apply to ALL Objects)

### Mandatory (5)
- `OPPDATERINGSDATO` - Last update timestamp
- `DATAFANGSTDATO` - Data capture date
- `KVALITET` - Position quality
- `LOKALID` - Local identifier (UUID)
- `NAVNEROM` - Namespace URI

### Optional (5)
- `SLUTTDATO` - End date
- `VERIFISERINGSDATO` - Verification date
- `REGISTRERINGSVERSJON` - Specification version
- `INFORMASJON` - General info
- `VERSJONID` - Version ID

## Geometry Types

| SOSI Type | Description | Example Objects |
|-----------|-------------|-----------------|
| PUNKT | Point | Bygning (posisjon), Trafikksignalpunkt |
| KURVE | Line | Vegdekkekant, ElveBekk, Grunnmur |
| FLATE | Polygon | Bygning (område), Parkeringsområde |
| TEKST | Text | (Not found in current extraction) |
| UNKNOWN | Not detected | Requires manual review |

## Most Common Attribute Names

### Geometry Attributes
- `posisjon` - Point location (GM_Point)
- `senterlinje` - Center line (GM_Curve)
- `grense` - Boundary line (GM_Curve)
- `område` - Area (GM_Surface)

### Classification Attributes
- `medium` - Position relative to ground (T=Terrenget, U=Underground, etc.)
- `høydereferanse` - Height reference (Topp=Top, Bunn=Bottom)
- `type` - Type classification (varies by object)

### Quality Attributes (under ..KVALITET)
- `datafangstmetode` - Data capture method
- `nøyaktighet` - Accuracy in cm
- `synbarhet` - Visibility in source data

## Sample Object Lookups

### Buildings (FKB_BYGNING_5.1)
```yaml
Bygning:                  # Building (in cadastre)
  - Mandatory: 6
  - Optional: 1
  - Key: bygningsnummer, bygningstype, bygningsstatus

AnnenBygning:            # Other building (not in cadastre)
  - Mandatory: 2
  - Optional: 1

Grunnmur:                # Foundation wall
  - Mandatory: 3
  - Optional: 1
```

### Roads (FKB_VEG_5)
```yaml
Vegdekkekant:            # Road surface edge
  - Mandatory: 3
  - Optional: 0
  - Geometry: KURVE

Parkeringsområde:        # Parking area
  - Mandatory: 1
  - Optional: 1
  - Geometry: FLATE

Kjørebanekant:           # Carriageway edge
  - Mandatory: 3
  - Optional: 1
```

### Water (FKB_VANN_5)
```yaml
ElveBekk:                # River/stream
  - Mandatory: 2
  - Optional: 2
  - Key: vanntype, vannbredde

Innsjø:                  # Lake
  - Mandatory: 2
  - Optional: 1
  - Geometry: FLATE
```

## Code List References

Most enumerated attributes reference code lists at:
`https://register.geonorge.no/sosi-kodelister/fkb/[domain]/5.0/[codelist]`

### Common Code Lists
- `medium` - Object position relative to surface
- `hoydereferanse` - Height reference point
- `datafangstmetode` - Data capture method
- `synbarhet` - Visibility in imagery
- `registreringsversjon` - FKB version

## Inheritance Patterns

Most objects inherit from one of these abstract types:

```
Fellesegenskaper (Common properties)
├── KvalitetPåkrevd (Required quality)
│   └── [Most objects with mandatory quality attributes]
└── KvalitetOpsjonell (Optional quality)
    └── [Objects with optional quality attributes]
```

## How to Use the YAML File

### Python Example
```python
import yaml

with open('01-MANDATORY-ATTRIBUTES.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Get all object types from a specification
bygning_spec = next(s for s in data['specifications']
                    if s['specification'] == 'FKB_BYGNING_5.1')

print(f"Objects: {bygning_spec['object_count']}")

# Get mandatory attributes for Bygning
bygning = next(o for o in bygning_spec['object_types']
               if o['object_type'] == 'Bygning')

for attr in bygning['mandatory_attributes']:
    print(f"- {attr['name']}: {attr['description']}")
```

### Command Line Examples
```bash
# Count object types
grep "object_type:" 01-MANDATORY-ATTRIBUTES.yaml | wc -l

# Find all objects with specific attribute
grep -B 5 "attribute_name: medium" 01-MANDATORY-ATTRIBUTES.yaml

# List all specifications
grep "^- specification:" 01-MANDATORY-ATTRIBUTES.yaml

# Get object types from one specification
sed -n '/specification: FKB_BYGNING/,/specification:/p' 01-MANDATORY-ATTRIBUTES.yaml | grep "object_type:"
```

## Common Tasks

### Validate FKB Data
1. Load YAML file
2. For each feature in your data:
   - Find object type definition
   - Check all mandatory attributes are present
   - Validate attribute types
   - Check multiplicity constraints

### Generate Documentation
1. Parse YAML structure
2. Group by specification
3. Format as tables or lists
4. Include inherited attributes from common_attributes

### Create Database Schema
1. Map SOSI types to database types:
   - GM_Point → POINT
   - GM_Curve → LINESTRING
   - GM_Surface → POLYGON
   - Integer → INT
   - Real → DOUBLE
   - CharacterString → VARCHAR
   - Date → DATE
   - DateTime → TIMESTAMP

### Build Validation Schema
1. Create JSON Schema or XSD
2. Required fields = mandatory attributes
3. Optional fields = optional attributes
4. Add enum constraints from code lists

## Next Steps

1. **Fetch code list values** from register.geonorge.no
2. **Process remaining 8 specifications** with different formats
3. **Extract relationship definitions** (Roller sections)
4. **Generate validation schemas** (JSON Schema/XSD)
5. **Cross-reference inherited attributes** from supertypes

## Support Files

- `extract_attributes.py` - Python extraction script (reusable)
- `test_extraction.py` - Test/debug script
- Source specifications in `../Spesifications/`

---

**Last Updated:** 2025-11-04
**Version:** 1.0
**Status:** Initial extraction complete, 7 of 15 specifications processed
