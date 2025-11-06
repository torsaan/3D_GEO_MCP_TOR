"""
Quick test script to verify the MCP server is working
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_server():
    """Test the GEO-MCP server by listing available tools"""
    server_params = StdioServerParameters(
        command="conda",
        args=["run", "-n", "geo-mcp-env", "--no-capture-output", "python", "app.py"],
    )

    print("🚀 Starting GEO-MCP server test...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            print("✅ Server connection established")

            # List available tools
            tools_result = await session.list_tools()
            print(f"\n📦 Found {len(tools_result.tools)} tools:")

            for tool in tools_result.tools:
                print(f"\n  🔧 {tool.name}")
                print(f"     {tool.description}")

            print("\n✅ Server test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_server())
