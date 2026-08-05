from agent.graph import run_investigation


def build_test_alert():
    return {
        "id": "alert-test-001",
        "service": "checkout-api",
        "severity": "P1",
        "message": (
            "5xx rate increased after deployment "
            "with payment timeout errors"
        ),
        "status": "open",
    }


def test_agent_completes_investigation():
    state = run_investigation(build_test_alert())

    assert state.status == "investigation_completed"
    assert state.timeline
    assert state.evidence
    assert state.hypotheses
    assert state.recommended_actions
    assert state.postmortem


def test_agent_collects_required_evidence():
    state = run_investigation(build_test_alert())

    assert "triage" in state.evidence
    assert "knowledge" in state.evidence
    assert "metrics" in state.evidence
    assert "logs" in state.evidence
    assert "deployments" in state.evidence


def test_agent_requires_approval_for_risky_action():
    state = run_investigation(build_test_alert())

    risky_actions = [
        action
        for action in state.recommended_actions
        if action["risk"] == "high"
    ]

    assert risky_actions
    assert all(
        action["requires_approval"]
        for action in risky_actions
    )


def test_agent_timeline_contains_core_steps():
    state = run_investigation(build_test_alert())

    steps = {
        event["step"]
        for event in state.timeline
    }

    expected_steps = {
        "load_skills",
        "triage",
        "rag_search",
        "metrics",
        "logs",
        "deployments",
        "hypotheses",
        "actions",
        "postmortem",
        "complete",
    }

    assert expected_steps.issubset(steps)
