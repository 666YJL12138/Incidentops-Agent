from mcp.server.fastmcp import FastMCP

from mcp_servers.tool_logic import get_recent_deployments


mcp = FastMCP("deploy-server")


@mcp.tool()
def get_service_deployments(service: str) -> list[dict]:
    """
    Get recent deployments for a service.
    """
    return get_recent_deployments(service=service)


if __name__ == "__main__":
    mcp.run()
