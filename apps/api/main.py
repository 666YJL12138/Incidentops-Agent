from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from rag.retrieve import search_knowledge


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


app.mount("/", StaticFiles(directory="apps/web", html=True), name="web")
