# GEO-MCP Server

**A Model Context Protocol (MCP) server for Norwegian geomatics and surveying workflows**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

GEO-MCP Server provides AI assistants (Claude, Cursor, etc.) with specialized capabilities for:
-  **Point cloud processing** (LAS/LAZ files)
-  **FKB GUIDELINES** (Norwegian mapping standards)
-  **SOSI file generation** (Norwegian GIS format)
-  **Surveying calculations** (adjustments, topology, accuracy)
-  **Format conversion** (SOSI ↔ GeoJSON, LAS → SOSI)
-  **GPU ACCELERATION**
---

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/GEO-MCP.git
cd GEO-MCP
```

2. **Create conda environment:**
```bash
conda env create -f environment.yml
conda activate geo-mcp-env
```

3. **Test the server:**
```bash
python app.py
# Should start without errors
```

### Usage with Claude Code

1. **Configure MCP server** in your Claude Code settings:

```json
{
  "mcpServers": {
    "geo-mcp": {
      "command": "conda",
      "args": [
        "run",
        "-n",
        "geo-mcp-env",
        "python",
        "/absolute/path/to/GEO_MCP/app.py"
      ]
    }
  }
}
```

2. **Restart Claude Code** to load the server

3. **Use MCP tools in your conversations:**
   - "Validate this SOSI file against FKB-B standards"
   - "Extract buildings from this LAS file and generate SOSI output"
   - "Convert this SOSI file to GeoJSON"
   - "Analyze the point cloud and tell me about building density"

---

##  Features

### Point Cloud Processing

**Extract features from LAS/LAZ files:**
- Load and filter by classification codes
- HDBSCAN/DBSCAN clustering
- RANSAC plane fitting
- Building footprint extraction
- Alpha shapes and boundaries
- B-spline curve fitting
- GPU acceleration (optional)

**Available Tools:**
- `load_and_filter_pointcloud` - Load LAS/LAZ with classification filtering
- `cluster_pointcloud_advanced` - Advanced HDBSCAN/DBSCAN clustering
- `fit_plane_ransac_advanced` - RANSAC plane fitting
- `extract_building_footprint_advanced` - Alpha shape footprint extraction
- `analyze_point_cloud_file` - Get point cloud statistics

### FKB Validation

**Validate against Norwegian FKB 5.1 standards:**
- 400+ validation rules implemented
- Attribute validation (mandatory/optional)
- Geometry validation (validity, topology)
- Accuracy validation (FKB-A/B/C/D standards)
- Metadata validation (KVALITET blocks)
- SOSI format validation
- Topology validation (Type 2 flater, networks)

**Available Tools:**
- `validate_fkb_sosi_file` - Complete FKB validation with HTML report
- `validate_fkb_object` - Validate single feature
- `get_fkb_accuracy_recommendations` - Get processing parameters for FKB standard

### SOSI Generation

**Generate FKB-compliant SOSI files:**
- Automatic .HODE section generation
- Integer coordinate encoding
- KVALITET block generation
- Feature validation before export
- Dual output (SOSI + GeoJSON)

**Available Tools:**
- `extract_buildings_to_sosi` - LAS → Buildings → SOSI pipeline
- `export_to_sosi` - Export features to SOSI format
- `convert_sosi_to_geojson` - Convert SOSI to GeoJSON

### Surveying Tools

**Professional surveying calculations:**
- Least squares adjustment
- Network analysis
- Coordinate transformations
- Accuracy metrics
- Statistical testing

---

## Available Tools

**Total: 39 MCP tools, 15 resources**

### Core Point Cloud Tools (10)
| Tool | Description |
|------|-------------|
| `load_and_filter_pointcloud` | Load LAS/LAZ with classification filtering |
| `cluster_pointcloud_advanced` | HDBSCAN/DBSCAN clustering with stats |
| `fit_plane_ransac_advanced` | RANSAC plane fitting with refinement |
| `detect_multiple_planes` | Sequential multi-plane detection |
| `extract_building_footprint_advanced` | Alpha shape footprint extraction |
| `compute_alpha_shape` | Concave hull computation |
| `fit_spline_to_points` | B-spline curve fitting |
| `segment_buildings_from_ground_advanced` | Building segmentation |
| `estimate_point_cloud_spacing` | Point spacing analysis |
| `check_gpu_availability` | GPU capability detection |

### FKB Tools (8)
| Tool | Description |
|------|-------------|
| `validate_fkb_sosi_file` | ⭐ Validate SOSI file with HTML report |
| `convert_sosi_to_geojson` | Convert SOSI to GeoJSON |
| `analyze_point_cloud_file` | Point cloud statistics |
| `extract_buildings_to_sosi` | ⭐ Complete LAS → SOSI pipeline |
| `get_fkb_accuracy_recommendations` | FKB processing parameters |
| `validate_fkb_object` | Validate single feature |
| `lookup_fkb_code` | FKB code lookup |
| `export_to_sosi` | Export to SOSI format |

### Surveying Tools (12)
- Network adjustment
- Coordinate transformations
- Topology analysis
- Validation checks
- And more...

### Geometry Tools (9)
- Point clustering
- Geometric primitives
- Distance calculations
- Topology operations
- And more...

---

## 📚 Documentation

### Comprehensive Guides

**Point Cloud Processing:**
- [RANSAC Guide](resources/RANSAC_GUIDE.md) - Robust geometric fitting
- [Clustering Guide](resources/CLUSTERING_GUIDE.md) - HDBSCAN/DBSCAN segmentation
- [Geometric Extraction Guide](resources/GEOMETRIC_EXTRACTION_GUIDE.md) - Boundaries & splines
- [Point Cloud Index](resources/POINTCLOUD_INDEX.md) - Complete overview

**FKB Standards:**
- [FKB Rules Consolidated](resources/FKB/FKB-RULES-CONSOLIDATED.md) - ⭐ Master reference (400+ rules)
- [FKB Validation Checklist](resources/FKB/09-VALIDATION-CHECKLIST.md) - Production workflow
- [FKB Document Index](resources/FKB/00-DOCUMENT-INDEX.md) - Specification inventory
- [FKB Special Cases](resources/FKB/06-SPECIAL-CASES.md) - Edge cases & exceptions
- [FKB Quick Reference](resources/FKB/QUICK_REFERENCE.md) - Code lookup tables

**Validation:**
- [FKB Validation Module](FKB/validation/README.md) - Validator API reference
- [FKB Validation Complete](FKB_VALIDATION_COMPLETE.md) - Implementation details

**Extraction Pipeline:**
- [FKB Extraction Pipeline](FKB_EXTRACTION_PIPELINE.md) - LAS → SOSI workflow

**Integration:**
- [Integration Summary](INTEGRATION_SUMMARY.md) - Point cloud modules overview

### MCP Resources

All documentation is accessible as MCP resources:

```
file://fkb_rules_consolidated        - Master FKB rules (33KB)
file://fkb_validation_checklist      - Validation workflow (32KB)
file://ransac_guide                  - RANSAC tutorial (10KB)
file://clustering_guide              - Clustering guide (12KB)
file://geometric_extraction_guide    - Extraction guide (15KB)
... and 10 more
```

---

## 🎯 Use Cases

### 1. Validate Existing FKB Data

```
User: "Validate buildings.sos against FKB-B standards and show me the report"

Claude uses:
  validate_fkb_sosi_file('buildings.sos', 'B', generate_html_report=True)

Result:
  - Validation report with error details
  - HTML report for visual inspection
  - Pass/fail status with error counts
```

### 2. Extract Buildings from Point Cloud

```
User: "Extract all buildings from scan.las and generate FKB-compliant SOSI output"

Claude uses:
  extract_buildings_to_sosi(
    'scan.las',
    'buildings.sos',
    fkb_standard='B',
    coordinate_system=25,
    origo_ne=[6500000, 100000]
  )

Result:
  - SOSI file with building footprints
  - GeoJSON for visualization
  - Validation report
  - Statistics (building count, areas, etc.)
```

### 3. Convert Between Formats

```
User: "Convert this SOSI file to GeoJSON for use in QGIS"

Claude uses:
  convert_sosi_to_geojson('data.sos', 'data.geojson')

Result:
  - GeoJSON file ready for QGIS/web maps
  - Feature count and CRS info
```

### 4. Analyze Point Cloud Quality

```
User: "Analyze this LAS file and tell me about the building points"

Claude uses:
  analyze_point_cloud_file('scan.las', classification_codes=[6])

Result:
  - Total points and building points
  - Spatial extent (bounds)
  - Point density
  - Height statistics
```

---

## 🏗️ Architecture

```
GEO-MCP Server
├── MCP Interface (FastMCP)
│   ├── 39 Tools (exposed to AI assistants)
│   └── 15 Resources (documentation)
│
├── Point Cloud Processing
│   ├── pointcloud_core.py (FKB-aware processing)
│   ├── clustering.py (HDBSCAN/DBSCAN)
│   ├── ransac_fitting.py (geometric fitting)
│   ├── geometric_extraction.py (footprints, boundaries)
│   └── gpu_utils.py (GPU acceleration)
│
├── FKB Validation
│   ├── FKB/validation/
│   │   ├── fkb_validators.py (20 validators)
│   │   ├── validation_report.py (HTML reports)
│   │   └── test_validators.py (30+ tests)
│   └── FKB/extracted/ (400+ rules from specs)
│
├── SOSI Processing
│   ├── FKB/sosi_parser.py (parse SOSI files)
│   ├── sosi_generator.py (generate SOSI files)
│   └── geometric_extraction.py (SOSI output)
│
└── Surveying Tools
    ├── adjustment_tools.py
    ├── surveying_tools.py
    ├── topology_tools.py
    └── validation_tools.py
```

---

## 📊 Statistics

- **Lines of Code:** 10,000+ (Python)
- **Documentation:** 2,000+ lines (Markdown, YAML)
- **FKB Rules:** 400+ validation rules implemented
- **Object Types:** 164 FKB object types supported
- **Test Coverage:** 30+ unit tests
- **MCP Tools:** 39
- **MCP Resources:** 15

---

## 🔧 Requirements

### Python Dependencies

```
python >= 3.10
fastmcp
numpy
scipy
shapely
laspy
open3d
hdbscan
scikit-learn
pyyaml
alphashape
```

### Optional Dependencies

```
cupy            # GPU acceleration
cuml            # GPU clustering
pytest          # Running tests
pytest-cov      # Test coverage
```

---
## 📖 FKB Standards

GEO-MCP Server supports all four FKB accuracy standards:

| Standard | Horizontal Accuracy | Vertical Accuracy | Use Case |
|----------|--------------------:|------------------:|----------|
| **FKB-A** | 3-30 cm | 3-30 cm | High-precision engineering, cadastral |
| **FKB-B** | 6-60 cm | 6-60 cm | Standard municipal mapping |
| **FKB-C** | 15-150 cm | 15-150 cm | Overview mapping, planning |
| **FKB-D** | 30-300 cm | 30-300 cm | Background data, large-scale |

Each standard has 4 accuracy classes for fine-grained control.

---

## 🧪 Testing

### Run Unit Tests

```bash
# All tests
pytest

# Specific module
pytest FKB/validation/test_validators.py -v

# With coverage
pytest --cov=FKB.validation --cov-report=html
```

### Test Server

```bash
# Start server (stdio transport)
python app.py

# In another terminal, test with MCP client
python test_server.py
```

### Test Example Workflow

```bash
# Generate test SOSI file
python sosi_generator.py

# Parse it back
python FKB/sosi_parser.py output/bygninger.sos

# Validate it
python -c "
from FKB.sosi_parser import parse_sosi_file
from FKB.validation import validate_dataset
features, header = parse_sosi_file('output/bygninger.sos')
report = validate_dataset(features, header, 'B')
print(f'Errors: {report[\"summary\"][\"total_errors\"]}')
"
```

---

## 🤝 Contributing

This is currently a personal project, but contributions are welcome!

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to all public functions
- Include examples in docstrings

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Kartverket** - Norwegian Mapping Authority (FKB specifications)
- **FastMCP** - MCP server framework
- **Open3D** - Point cloud processing
- **Shapely** - Geometric operations

---

## 📞 Support

### Documentation
- [FKB Rules Consolidated](resources/FKB/FKB-RULES-CONSOLIDATED.md) - Complete FKB reference
- [Validation README](FKB/validation/README.md) - Validation guide
- [Extraction Pipeline](FKB_EXTRACTION_PIPELINE.md) - Workflow documentation

### Issues
- Report bugs on GitHub Issues
- Feature requests welcome
- Questions? Open a discussion

---

## 🗺️ Roadmap

### Completed ✅
- ✅ Point cloud processing pipeline
- ✅ FKB validation (400+ rules)
- ✅ SOSI parser and generator
- ✅ MCP server with 39 tools
- ✅ Comprehensive documentation

### Future Enhancements
- [ ] Type 2 flater generation (separate boundary features)
- [ ] Multi-dataset SOSI support
- [ ] Web UI for validation reports
- [ ] Batch processing CLI
- [ ] PostGIS integration
- [ ] Real-time validation in QGIS plugin
- [ ] More object types (roads, water, vegetation)
- [ ] INSPIRE compliance checking

---

## 📊 Project Status

**Version:** 0.1.0
**Status:** ✅ Production Ready
**Last Updated:** 2025-11-05
**Python:** 3.10+
**License:** MIT

---

**Made with ❤️ for Norwegian geomatics workflows**

*GEO-MCP Server - Bringing AI assistance to professional surveying and mapping*
