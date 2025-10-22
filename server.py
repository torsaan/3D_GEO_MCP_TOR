# 1. Import the app. This creates the 'mcp' object.
from app import mcp
from fastmcp import FastMCP
# 2. Import all your tool and resource files.
#    This is CRITICAL: just importing them registers all
#    the @mcp.tool decorators with the 'mcp' object.
try:
    import geo_tools
    import topology_tools
    import fkb_exporter
    import validation_tools
    import resource_tools # From our previous example
    import cluster_tools
    
    print("Successfully imported all tool modules.")
    
except ImportError as e:
    print(f"!!! FAILED TO IMPORT A MODULE: {e}")
    print("!!! Please check your environment.yml and file names.")
    

# 3. Run the server
if __name__ == "__main__":
    print(f"🚀 GEO-MCP Server starting...")
    print("   Listening on: http://localhost:6278")
    mcp.run(transport="http", host="127.0.0.1", port=6278)