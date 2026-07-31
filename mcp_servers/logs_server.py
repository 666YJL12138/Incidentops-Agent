from mcp.server.fastmcp import FastMCP

from mcp_servers.tool_logic import search_logs


mcp = FastMCP("logs-server")


@mcp.tool()
def search_service_logs(service: str, keyword: str = "", limit: int = 20) -> list[dict]:
    """
    Search service logs by keyword.
    """
    return search_logs(service=service, keyword=keyword, limit=limit)


if __name__ == "__main__":
    mcp.run()
