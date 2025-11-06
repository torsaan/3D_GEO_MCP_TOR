# FKB Validation Module

Comprehensive validation tools for FKB (Felles Kartgrunnlag) datasets based on FKB 5.1 specifications.

## Features

✅ **Attribute Validation** - Verify all mandatory attributes are present and correctly typed
✅ **Geometry Validation** - Check geometry validity, topology, and type compliance
✅ **Accuracy Validation** - Validate NØYAKTIGHET against FKB-A/B/C/D standards
✅ **Metadata Validation** - Verify KVALITET block completeness and code validity
✅ **SOSI Format Validation** - Check SOSI header and encoding correctness
✅ **Topology Validation** - Validate Type 2 flater, networks, and shared boundaries
✅ **HTML Reports** - Generate beautiful, detailed validation reports

## Installation

```bash
# Required dependencies
pip install pyyaml shapely numpy

# Optional: for running tests
pip install pytest
```

## Quick Start

### Validate a Single Feature

```python
from FKB.validation import validate_feature

feature = {
    'OBJTYPE': 'Bygning',
    'posisjon': [100, 200, 50],
    'bygningsnummer': 12345,
    'DATAFANGSTDATO': '20231104',
    'KVALITET': {
        'MÅLEMETODE': 'fot',
        'NØYAKTIGHET': 0.10,
        'SYNBARHET': 0,
        'DATAFANGSTDATO': '20231104',
        'VERIFISERINGSDATO': '20231104'
    },
    'geometry': {...}
}

results = validate_feature(feature, fkb_standard='B')

# Check results
for validator_name, errors in results.items():
    if errors:
        print(f"{validator_name}: {len(errors)} errors")
        for error in errors:
            print(f"  - {error}")
```

### Validate Complete Dataset

```python
from FKB.validation import validate_dataset, generate_html_report

# Your parsed SOSI data
features = [...]  # List of feature dicts
header = {...}    # Parsed .HODE section

# Run validation
report = validate_dataset(features, header, fkb_standard='B')

# Print summary
print(f"Total features: {report['summary']['total_features']}")
print(f"Total errors: {report['summary']['total_errors']}")

# Generate HTML report
html_path = generate_html_report(
    report,
    dataset_name="My FKB Dataset",
    output_path="validation_report.html"
)
print(f"Report saved to: {html_path}")
```

### Generate Reports

```python
from FKB.validation import (
    generate_html_report,
    generate_json_report,
    generate_summary_report
)

# Beautiful HTML report (for humans)
html_path = generate_html_report(report, "My Dataset")

# Machine-readable JSON (for automation)
json_path = generate_json_report(report, "report.json")

# Quick CLI summary (for terminals)
summary = generate_summary_report(report)
print(summary)
```

## Validation Rules

The module validates against **400+ rules** extracted from FKB 5.1 specifications:

### Attribute Rules (ATTR-xxx)
- `ATTR-001`: Unknown OBJTYPE
- `ATTR-002`: Missing mandatory attribute
- `ATTR-003`: Missing inherited attribute

### Geometry Rules (GEOM-xxx)
- `GEOM-001`: Missing geometry
- `GEOM-003`: Invalid geometry (self-intersections, etc.)
- `GEOM-004`: Geometry type mismatch
- `GEOM-010`: Segment too short (violates accuracy)

### Accuracy Rules (ACC-xxx)
- `ACC-001`: Missing KVALITET block
- `ACC-002`: Missing NØYAKTIGHET
- `ACC-004`: NØYAKTIGHET exceeds standard limits
- `ACC-005`: H-NØYAKTIGHET exceeds vertical limits

### Metadata Rules (META-xxx)
- `META-001`: Missing KVALITET block
- `META-002`: Missing mandatory KVALITET attribute
- `META-003`: Invalid MÅLEMETODE code
- `META-004`: Invalid SYNBARHET code
- `META-005`: Invalid date format

### SOSI Format Rules (SOSI-xxx)
- `SOSI-001`: Missing mandatory header attribute
- `SOSI-002`: Invalid TEGNSETT
- `SOSI-006`: Missing coordinate system
- `SOSI-008`: Coordinate not encoded as integer

### Topology Rules (TOPO-xxx)
- **`TOPO-CRITICAL-001`**: Type 2 flate område ≠ union(avgrensning) ⚠️ **MOST CRITICAL**
- `TOPO-008`: Dangling network endpoint
- `TOPO-010`: Polygon overlap

## Validation Workflow

```
┌─────────────────┐
│  Load Dataset   │
│   (SOSI file)   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Parse Features  │
│   & Header      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│   Validate      │
│   - Attributes  │
│   - Geometry    │
│   - Accuracy    │
│   - Metadata    │
│   - Topology    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Generate Report │
│ (HTML/JSON)     │
└─────────────────┘
```

## FKB Standards

The module supports all four FKB accuracy standards:

| Standard | Horizontal Accuracy | Vertical Accuracy | Use Case |
|----------|--------------------:|------------------:|----------|
| **FKB-A** | 3-30 cm | 3-30 cm | High-precision engineering |
| **FKB-B** | 6-60 cm | 6-60 cm | Standard mapping |
| **FKB-C** | 15-150 cm | 15-150 cm | Overview mapping |
| **FKB-D** | 30-300 cm | 30-300 cm | Background data |

## Most Critical Validation

The **single most important** FKB rule is **TOPO-CRITICAL-001**:

> **Type 2 flate:** `område` geometry **MUST** equal the union of all `avgrensningsobjekter`

This applies to:
- Bygning (buildings)
- Kjørebane (roads)
- ElvBekk (rivers)
- Innsjø (lakes)
- ...and 10+ other object types

**Example validation:**

```python
from FKB.validation import validate_type2_flate_topology

# The polygon (område)
bygning = {
    'OBJTYPE': 'Bygning',
    'område': Polygon([...]),  # The area
    'KVALITET': {'NØYAKTIGHET': 0.10}
}

# The boundary lines (avgrensning)
boundaries = [
    {'geometry': LineString([...])},  # North wall
    {'geometry': LineString([...])},  # East wall
    {'geometry': LineString([...])},  # South wall
    {'geometry': LineString([...])},  # West wall
]

# Validate
errors = validate_type2_flate_topology(bygning, boundaries)

if not errors:
    print("✅ Type 2 flate validation passed!")
else:
    for error in errors:
        print(f"❌ {error}")
```

## Rule Database

The validators are **data-driven** and load rules from:

```
FKB/extracted/
├── 01-MANDATORY-ATTRIBUTES.yaml  # 164 object types, 5,143 lines
├── 02-GEOMETRIC-RULES.yaml       # 127+ rules, 1,118 lines
├── 03-ACCURACY-STANDARDS.yaml    # 16 accuracy classes, 352 lines
├── 04-TOPOLOGY-RULES.yaml        # Topology patterns
├── 05-METADATA-RULES.yaml        # KVALITET rules, 556 lines
└── 08-SOSI-FORMAT-RULES.yaml     # SOSI format spec, 535 lines
```

This means:
- ✅ Easy to update rules without changing code
- ✅ Rules traced to source specifications
- ✅ Consistent validation across tools

## Testing

Run unit tests:

```bash
# Run all tests
pytest test_validators.py -v

# Run specific test
pytest test_validators.py::test_validate_mandatory_attributes_valid -v

# Run with coverage
pytest test_validators.py --cov=fkb_validators --cov-report=html
```

## HTML Report Features

The generated HTML reports include:

- 📊 **Visual Status Dashboard** - Overall pass/fail with color coding
- 📈 **Metrics Cards** - Feature counts, error counts, critical issues
- 🔍 **Detailed Error Lists** - Every error with context and error codes
- 💡 **Recommendations** - Actionable advice for fixing issues
- 🎨 **Beautiful Design** - Professional, printable layout

Example output:
```
✅ FKB VALIDATION REPORT
Status: PASS
Features: 1,234
Errors: 0

🔴 Critical Errors: 0
🟠 High Priority: 0
🟡 Medium Priority: 0
```

## Error Codes Reference

### Critical Errors (Fix First)
- `ATTR-002`: Missing mandatory attribute
- `GEOM-001`: Missing geometry
- `TOPO-001`: Type 2 flate missing område
- `TOPO-005`: Type 2 flate geometry mismatch
- `SOSI-001`: Missing mandatory header attribute
- `SOSI-006`: Missing coordinate system

### High Priority
- `GEOM-003`: Invalid geometry
- `ACC-004`: Accuracy exceeds standards
- `META-001`: Missing KVALITET block
- `TOPO-008`: Dangling network endpoint

### Medium Priority
- `ATTR-WARN-001`: Unknown attribute
- `GEOM-010`: Short segment (could be simplified)
- `META-003`: Invalid MÅLEMETODE

## API Reference

### Core Functions

#### `validate_feature(feature, fkb_standard='B', strict=False)`
Validate a single feature against all rules.

**Parameters:**
- `feature` (dict): Parsed SOSI feature
- `fkb_standard` (str): 'A', 'B', 'C', or 'D'
- `strict` (bool): Enable optional validators

**Returns:** dict mapping validator names to error lists

#### `validate_dataset(features, header, fkb_standard='B')`
Validate complete dataset including topology.

**Parameters:**
- `features` (list): All features in dataset
- `header` (dict): Parsed .HODE section
- `fkb_standard` (str): 'A', 'B', 'C', or 'D'

**Returns:** Comprehensive validation report dict

#### `generate_html_report(results, dataset_name, output_path)`
Generate beautiful HTML validation report.

**Parameters:**
- `results` (dict): Output from `validate_dataset()`
- `dataset_name` (str): Name for report header
- `output_path` (str): Where to save HTML

**Returns:** Path to generated HTML file

## Integration Example

### As MCP Tool

```python
from app import mcp
from FKB.validation import validate_dataset, generate_html_report

@mcp.tool
def validate_fkb_dataset(
    sosi_file_path: str,
    fkb_standard: str = 'B',
    generate_report: bool = True
) -> dict:
    """
    Validate FKB dataset from SOSI file.

    Args:
        sosi_file_path: Path to SOSI file
        fkb_standard: FKB standard ('A', 'B', 'C', 'D')
        generate_report: Generate HTML report

    Returns:
        Validation results with optional report path
    """
    # Parse SOSI file (use your parser)
    features, header = parse_sosi_file(sosi_file_path)

    # Validate
    results = validate_dataset(features, header, fkb_standard)

    # Generate report
    if generate_report:
        report_path = generate_html_report(
            results,
            dataset_name=Path(sosi_file_path).stem,
            output_path=sosi_file_path.replace('.sos', '_validation.html')
        )
        results['report_path'] = report_path

    return results
```

### As CLI Tool

```python
#!/usr/bin/env python
"""
FKB Validator CLI
Usage: python validate_fkb.py dataset.sos --standard B --report
"""

import sys
from FKB.validation import validate_dataset, generate_summary_report

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate FKB dataset')
    parser.add_argument('sosi_file', help='Path to SOSI file')
    parser.add_argument('--standard', default='B', choices=['A', 'B', 'C', 'D'])
    parser.add_argument('--report', action='store_true', help='Generate HTML report')

    args = parser.parse_args()

    # Parse and validate
    features, header = parse_sosi_file(args.sosi_file)
    results = validate_dataset(features, header, args.standard)

    # Print summary
    print(generate_summary_report(results))

    # Generate report if requested
    if args.report:
        from FKB.validation import generate_html_report
        path = generate_html_report(results, args.sosi_file)
        print(f"\n📄 Full report: {path}")

    # Exit code based on validation
    sys.exit(0 if results['summary']['total_errors'] == 0 else 1)

if __name__ == '__main__':
    main()
```

## Troubleshooting

### Rules Not Loading

```
⚠️  Warning: Could not load all FKB rules: ...
```

**Solution:** Ensure the extracted rule files exist:
```bash
ls -la FKB/extracted/
# Should see 01-MANDATORY-ATTRIBUTES.yaml, etc.
```

### Import Errors

```python
ImportError: No module named 'yaml'
```

**Solution:** Install dependencies:
```bash
pip install pyyaml shapely numpy
```

### Test Failures

Some tests may fail if rule databases are not loaded. This is expected behavior - validators will return appropriate warnings.

## Contributing

To add new validators:

1. Add validation function to `fkb_validators.py`
2. Use error code format: `CATEGORY-###: Description`
3. Add tests to `test_validators.py`
4. Update `__init__.py` exports
5. Update this README

## License

Part of GEO-MCP Server - Norwegian geomatics MCP server

## References

- **FKB 5.1 Specifications:** Source of all validation rules
- **SOSI Format 4.5:** Norwegian GIS file format standard
- **Kartverket:** Norwegian Mapping Authority

---

**Generated:** 2025-11-04
**Version:** 1.0.0
**Status:** Production Ready ✅
