from mcp_servers.tool_logic import (
    get_recent_deployments,
    query_metrics,
    search_logs,
)


def test_search_checkout_timeout_logs():
    results = search_logs(
        service="checkout-api",
        keyword="timeout",
        limit=10,
    )

    assert results
    assert all(
        "timeout" in item["line"].lower()
        for item in results
    )


def test_query_checkout_metrics():
    result = query_metrics("checkout-api")

    assert result["service"] == "checkout-api"
    assert "summary" in result
    assert result["summary"]["max_error_rate"] > 0
    assert result["summary"]["max_p95_latency"] > 0


def test_get_checkout_deployments():
    deployments = get_recent_deployments("checkout-api")

    assert deployments
    assert all(
        item["service"] == "checkout-api"
        for item in deployments
    )


def test_unknown_service_metrics():
    result = query_metrics("unknown-service")

    assert result["error"] == "metrics_not_found"
