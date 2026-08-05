from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from agent.state import IncidentState
from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, Field
from rag.retrieve import search_knowledge
from mcp_servers.tool_logic import (
    create_ticket,
    get_recent_deployments,
    query_metrics,
    search_logs,
)

from agent.graph import run_investigation
from apps.api.incident_store import (
    get_events,
    get_incident,
    init_db,
    save_incident,
)


app = FastAPI(
    title="IncidentOps Agent",
    description="An SRE incident commander agent for alert triage, investigation, and postmortem generation.",
    version="0.1.0",
)

init_db()


class StartIncidentRequest(BaseModel):
    alert_id: str


class CustomAlertRequest(BaseModel):
    service: str = Field(min_length=1, max_length=100)
    severity: Literal["P1", "P2", "P3"]
    message: str = Field(min_length=1, max_length=1000)
    status: str = "open"


class ApproveActionRequest(BaseModel):
    action_id: str


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


@app.post("/api/incidents/start")
def start_incident(request: StartIncidentRequest):
    alerts = list_alerts()

    alert = next(
        (
            item
            for item in alerts
            if item["id"] == request.alert_id
        ),
        None,
    )

    if alert is None:
        return {
            "error": "alert_not_found",
            "message": f"Alert {request.alert_id} does not exist.",
        }

    state = run_investigation(alert)
    save_incident(state)

    return state.model_dump()


@app.post("/api/incidents/start-from-alert")
def start_incident_from_alert(request: CustomAlertRequest):
    alert = {
        "id": f"manual-{uuid4().hex[:8]}",
        "service": request.service.strip(),
        "severity": request.severity,
        "message": request.message.strip(),
        "status": request.status,
    }

    state = run_investigation(alert)
    save_incident(state)

    return state.model_dump()


@app.get("/api/incidents/{incident_id}")
def incident_detail(incident_id: str):
    incident = get_incident(incident_id)

    if incident is None:
        return {
            "error": "incident_not_found",
            "incident_id": incident_id,
        }

    return incident


@app.get("/api/incidents/{incident_id}/events")
def incident_events(incident_id: str):
    return {
        "incident_id": incident_id,
        "events": get_events(incident_id),
    }


@app.post("/api/incidents/{incident_id}/approve")
def approve_action(
    incident_id: str,
    request: ApproveActionRequest,
):
    incident = get_incident(incident_id)

    if incident is None:
        return {
            "error": "incident_not_found",
            "incident_id": incident_id,
        }

    action = next(
        (
            item
            for item in incident["recommended_actions"]
            if item["id"] == request.action_id
        ),
        None,
    )

    if action is None:
        return {
            "error": "action_not_found",
            "action_id": request.action_id,
        }

    action["approved"] = True
    action["approval_message"] = (
        "Action approved by human operator. "
        "Production execution is simulated."
    )

    for item in incident["timeline"]:
        if item["step"] == "actions":
            item["message"] += f" Action {request.action_id} approved."

    incident["status"] = "action_approved"

    updated_state = IncidentState(**incident)
    save_incident(updated_state)

    return {
        "incident_id": incident_id,
        "action_id": request.action_id,
        "status": "approved",
        "message": "Action approval recorded.",
    }


app.mount("/", StaticFiles(directory="apps/web", html=True), name="web")
