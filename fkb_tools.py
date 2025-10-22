from app import mcp  # <-- Import the same mcp object

fkb_metadata = {
    "datasets": ["FKB-BygnAnlegg", "FKB-Bygning", "FKB-Ledning", "FKB-Vann", "FKB-Veg", "FKB-TraktorvegSti", "Elveg 2.0"],
    "mandatory_metadata": ["OBJTYPE", "DATAFANGSTDATO", "REGISTRERINGSVERSJON", "KVALITET"],
    # Add more from PDF, e.g., KVALITET subkeys, HREF values, etc.
}

@mcp.tool
def lookup_fkb_code(object_name: str) -> dict:
    """Enhanced: Returns FKB code, geometry, and rules."""
    # Placeholder lookup; expand with real data
    base = {"kode": 65, "geometri": "LineString"}
    base["rules"] = {"mandatory": fkb_metadata["mandatory_metadata"]}
    return base