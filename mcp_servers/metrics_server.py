from mcp.server.fastmcp import FastMCP

from mcp_servers.tool_logic import query_metrics


mcp = FastMCP("metrics-server")


@mcp.tool()
def query_service_metrics(service: str) -> dict:
    """
    Query service metrics summary and time series points.
    """
    return query_metrics(service=service)


if __name__ == "__main__":
    mcp.run()
