# --- app.py ---
from fastmcp import FastMCP
# Removed pydantic import as we're not using ConfigDict here for now

# Initialize FastMCP with just the server name
mcp = FastMCP(
    "GEO-MCP Server" # Server name is the first positional argument
)