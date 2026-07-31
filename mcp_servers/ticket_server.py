from mcp.server.fastmcp import FastMCP

from mcp_servers.tool_logic import create_ticket


mcp = FastMCP("ticket-server")


@mcp.tool()
def create_incident_ticket(title: str, severity: str, summary: str) -> dict:
    """
    Create an incident ticket.
    """
    return create_ticket(title=title, severity=severity, summary=summary)


if __name__ == "__main__":
    mcp.run()
