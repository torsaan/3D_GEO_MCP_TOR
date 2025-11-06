"""
GEO-MCP Server - Main Application
A FastMCP server for geomatics and surveying tools, focusing on point cloud processing.
"""
from fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("GEO-MCP Server", version="0.1.0")

# Import all tool modules to register their @mcp.tool decorators
# These imports must come AFTER mcp is initialized
import cluster_tools
import geo_tools
import topology_tools
import validation_tools
import resource_tools
import fkb_exporter
import fkb_tools
import surveying_tools
import adjustment_tools
import pointcloud_tools  # Advanced point cloud processing tools
import fkb_mcp_tools  # FKB validation, parsing, and extraction tools


# Server entry point
if __name__ == "__main__":
    # Run with stdio transport for local MCP clients (Claude Desktop, Cursor, etc.)
    mcp.run(transport="stdio")
