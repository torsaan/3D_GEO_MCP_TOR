from app import mcp  
from pathlib import Path

# Helper function to read a file
def _read_file(filepath):
    try:
        return Path(filepath).read_text()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"

@mcp.resource("file://fkb_rules")
def get_fkb_rules() -> str:
    """Returns the FKB object and geometry rules."""
    return _read_file("resources/fkb_rules.md")

@mcp.resource("file://topology_math")
def get_topology_math() -> str:
    """Returns the advanced math for topology and junctions."""
    return _read_file("resources/topology_math.md")

@mcp.resource("file://surveying_rules")
def get_surveying_rules() -> str:
    """Returns key geomatics principles for Norwegian land surveying (coordinate systems, projections, accuracy)."""
    return _read_file("resources/surveying_rules.md")

@mcp.resource("file://accuracy_metrics")
def get_accuracy_metrics() -> str:
    """Returns explanations of accuracy metrics used in surveying adjustments."""
    return _read_file("resources/accuracy_metrics.md")

@mcp.resource("file://adjustment_procedures")
def get_adjustment_procedures() -> str:
    """Returns an overview of least squares adjustment procedures in surveying."""
    return _read_file("resources/adjustment_procedures.md")

@mcp.resource("file://ransac_guide")
def get_ransac_guide() -> str:
    """Returns detailed RANSAC guide for robust geometric fitting in point clouds."""
    return _read_file("resources/RANSAC_GUIDE.md")

@mcp.resource("file://clustering_guide")
def get_clustering_guide() -> str:
    """Returns comprehensive clustering guide for HDBSCAN and DBSCAN segmentation."""
    return _read_file("resources/CLUSTERING_GUIDE.md")

@mcp.resource("file://geometric_extraction_guide")
def get_geometric_extraction_guide() -> str:
    """Returns guide for boundary detection, footprints, and spline fitting."""
    return _read_file("resources/GEOMETRIC_EXTRACTION_GUIDE.md")

# ============================================================================
# FKB-SPECIFIC RESOURCES (from FKB subfolder)
# ============================================================================

@mcp.resource("file://fkb_rules_consolidated")
def get_fkb_rules_consolidated() -> str:
    """Returns the master FKB rules document consolidating all 400+ rules from 15 FKB 5.1 specifications."""
    return _read_file("resources/FKB/FKB-RULES-CONSOLIDATED.md")

@mcp.resource("file://fkb_validation_checklist")
def get_fkb_validation_checklist() -> str:
    """Returns production-ready FKB validation checklist with priority-based workflow and code examples."""
    return _read_file("resources/FKB/09-VALIDATION-CHECKLIST.md")

@mcp.resource("file://fkb_document_index")
def get_fkb_document_index() -> str:
    """Returns complete inventory of all 15 FKB 5.1 specification documents with metadata."""
    return _read_file("resources/FKB/00-DOCUMENT-INDEX.md")

@mcp.resource("file://fkb_special_cases")
def get_fkb_special_cases() -> str:
    """Returns FKB special cases and conditional rules (fictional boundaries, legacy data, edge cases)."""
    return _read_file("resources/FKB/06-SPECIAL-CASES.md")

@mcp.resource("file://fkb_conflicts")
def get_fkb_conflicts() -> str:
    """Returns known conflicts, ambiguities, and clarifications needed in FKB specifications."""
    return _read_file("resources/FKB/07-CONFLICTS-AMBIGUITIES.md")

@mcp.resource("file://fkb_quick_reference")
def get_fkb_quick_reference() -> str:
    """Returns quick reference tables for FKB code values (DATAFANGSTMETODE, SYNBARHET, etc.)."""
    return _read_file("resources/FKB/QUICK_REFERENCE.md")

@mcp.resource("file://fkb_rules_legacy")
def get_fkb_rules_legacy() -> str:
    """Returns original FKB rules summary (legacy document for quick introduction)."""
    return _read_file("resources/FKB/fkb_rules.md")
