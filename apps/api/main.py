from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rag.retrieve import search_knowledge
from mcp_servers.tool_logic import (
    create_ticket,
    get_recent_deployments,
    query_metrics,
    search_logs,
)


app = FastAPI(
    title="IncidentOps Agent",
    description="An SRE incident commander agent for alert triage, investigation, and postmortem generation.",
    version="0.1.0",
)


class Alert(BaseModel):
    id: str
    service: str
    severity: str
    message: str
    status: str


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "incidentops-agent",
    }


@app.get("/api/alerts")
def list_alerts():
    return [
        {
            "id": "alert-001",
            "service": "checkout-api",
            "severity": "P1",
            "message": "5xx rate jumped to 12% and p95 latency is 2.8s",
            "status": "open",
        },
        {
            "id": "alert-002",
            "service": "payment-api",
            "severity": "P2",
            "message": "Payment dependency timeout increased in the last 10 minutes",
            "status": "open",
        },
    ]


@app.get("/api/alerts/{alert_id}")
def get_alert(alert_id: str):
    alerts = list_alerts()

    for alert in alerts:
        if alert["id"] == alert_id:
            return alert

    return {
        "error": "alert_not_found",
        "message": f"Alert {alert_id} does not exist.",
    }


@app.get("/api/rag/search")
def rag_search(query: str, top_k: int = 5):
    results = search_knowledge(query=query, top_k=top_k)

    return {
        "query": query,
        "top_k": top_k,
        "results": results,
    }


@app.get("/api/tools/logs")
def api_search_logs(service: str, keyword: str = "", limit: int = 20):
    return {
        "service": service,
        "keyword": keyword,
        "results": search_logs(service=service, keyword=keyword, limit=limit),
    }


@app.get("/api/tools/metrics")
def api_query_metrics(service: str):
    return query_metrics(service=service)


@app.get("/api/tools/deployments")
def api_get_deployments(service: str):
    return {
        "service": service,
        "deployments": get_recent_deployments(service=service),
    }


@app.post("/api/tools/tickets")
def api_create_ticket(title: str, severity: str, summary: str):
    return create_ticket(title=title, severity=severity, summary=summary)


app.mount("/", StaticFiles(directory="apps/web", html=True), name="web")
