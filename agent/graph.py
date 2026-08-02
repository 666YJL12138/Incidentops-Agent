from agent.skill_loader import load_incident_skills
from agent.state import IncidentState, add_timeline_event
from mcp_servers.tool_logic import (
    get_recent_deployments,
    query_metrics,
    search_logs,
)
from rag.retrieve import search_knowledge


def run_investigation(alert: dict) -> IncidentState:
    state = IncidentState(
        incident_id=f"inc-{alert['id']}",
        alert=alert,
    )

    state.skills = load_incident_skills()
    add_timeline_event(state, "load_skills", "Loaded incident operation skills.")

    triage_alert(state)
    retrieve_knowledge(state)
    collect_metrics(state)
    collect_logs(state)
    collect_deployments(state)
    build_hypotheses(state)
    build_recommended_actions(state)
    build_postmortem(state)

    state.status = "investigation_completed"
    add_timeline_event(state, "complete", "Investigation completed.")

    return state


def triage_alert(state: IncidentState) -> None:
    alert = state.alert

    state.evidence["triage"] = {
        "service": alert["service"],
        "severity": alert["severity"],
        "message": alert["message"],
        "initial_focus": ["recent deployment", "timeout logs", "error rate"],
    }

    add_timeline_event(
        state,
        "triage",
        f"Classified {alert['service']} alert as {alert['severity']}.",
    )


def retrieve_knowledge(state: IncidentState) -> None:
    query = f"{state.alert['service']} {state.alert['message']}"
    docs = search_knowledge(query=query, top_k=5)

    state.evidence["knowledge"] = docs

    add_timeline_event(
        state,
        "rag_search",
        f"Retrieved {len(docs)} related knowledge documents.",
    )


def collect_metrics(state: IncidentState) -> None:
    service = state.alert["service"]
    metrics = query_metrics(service=service)

    state.evidence["metrics"] = metrics

    add_timeline_event(
        state,
        "metrics",
        f"Collected metrics for {service}.",
    )


def collect_logs(state: IncidentState) -> None:
    service = state.alert["service"]
    logs = search_logs(service=service, keyword="timeout", limit=10)

    state.evidence["logs"] = logs

    add_timeline_event(
        state,
        "logs",
        f"Found {len(logs)} timeout-related log lines.",
    )


def collect_deployments(state: IncidentState) -> None:
    service = state.alert["service"]
    deployments = get_recent_deployments(service=service)

    state.evidence["deployments"] = deployments

    add_timeline_event(
        state,
        "deployments",
        f"Found {len(deployments)} recent deployments.",
    )


def build_hypotheses(state: IncidentState) -> None:
    evidence = state.evidence
    hypotheses = []

    metrics = evidence.get("metrics", {})
    metric_summary = metrics.get("summary", {})
    logs = evidence.get("logs", [])
    deployments = evidence.get("deployments", [])

    if deployments and logs:
        hypotheses.append(
            {
                "title": "Recent deployment may have introduced timeout regression",
                "confidence": 0.82,
                "evidence": [
                    "Recent deployment exists for the affected service.",
                    "Timeout-related logs were found.",
                ],
            }
        )

    if metric_summary.get("max_error_rate", 0) > 5:
        hypotheses.append(
            {
                "title": "Service is experiencing elevated error rate",
                "confidence": 0.74,
                "evidence": [
                    f"Max error rate reached {metric_summary['max_error_rate']}%.",
                ],
            }
        )

    if metric_summary.get("max_p95_latency", 0) > 1000:
        hypotheses.append(
            {
                "title": "High latency may be contributing to request failures",
                "confidence": 0.68,
                "evidence": [
                    f"Max p95 latency reached {metric_summary['max_p95_latency']} ms.",
                ],
            }
        )

    state.hypotheses = hypotheses

    add_timeline_event(
        state,
        "hypotheses",
        f"Generated {len(hypotheses)} root-cause hypotheses.",
    )


def build_recommended_actions(state: IncidentState) -> None:
    state.recommended_actions = [
        {
            "id": "act-001",
            "title": "Create incident ticket",
            "risk": "low",
            "requires_approval": False,
            "reason": "Creating a ticket is safe and helps track the incident.",
        },
        {
            "id": "act-002",
            "title": "Prepare rollback plan",
            "risk": "high",
            "requires_approval": True,
            "reason": "Rollback changes production behavior and requires human approval.",
        },
        {
            "id": "act-003",
            "title": "Notify service owner",
            "risk": "low",
            "requires_approval": False,
            "reason": "The affected service owner should review the evidence.",
        },
    ]

    add_timeline_event(
        state,
        "actions",
        f"Generated {len(state.recommended_actions)} recommended actions.",
    )


def build_postmortem(state: IncidentState) -> None:
    state.postmortem = {
        "summary": f"{state.alert['service']} triggered {state.alert['severity']} alert.",
        "impact": state.alert["message"],
        "timeline": state.timeline,
        "hypotheses": state.hypotheses,
        "follow_up_actions": [
            "Improve alert dashboard.",
            "Add regression test for timeout behavior.",
            "Review deployment risk checklist.",
        ],
    }

    add_timeline_event(
        state,
        "postmortem",
        "Generated postmortem draft.",
    )
