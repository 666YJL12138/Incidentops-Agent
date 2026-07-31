from mcp_servers.tool_logic import (
    create_ticket,
    get_recent_deployments,
    query_metrics,
    search_logs,
)


def main():
    service = "checkout-api"

    print("=== Logs ===")
    logs = search_logs(service=service, keyword="timeout", limit=10)
    for item in logs:
        print(item["line"])

    print("\n=== Metrics ===")
    metrics = query_metrics(service=service)
    print(metrics["summary"])

    print("\n=== Deployments ===")
    deployments = get_recent_deployments(service=service)
    for deployment in deployments:
        print(
            f'{deployment["service"]} {deployment["version"]} '
            f'deployed at {deployment["time"]}: {deployment["summary"]}'
        )

    print("\n=== Ticket ===")
    ticket = create_ticket(
        title="Checkout API 5xx spike",
        severity="P1",
        summary="checkout-api has increased 5xx rate and payment timeout logs.",
    )
    print(ticket)


if __name__ == "__main__":
    main()
