from app import mcp  # <-- Import the mcp object
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