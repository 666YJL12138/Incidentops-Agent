from fastapi.testclient import TestClient

from apps.api.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_alerts_endpoint():
    response = client.get("/api/alerts")

    assert response.status_code == 200

    alerts = response.json()

    assert len(alerts) >= 2
    assert alerts[0]["id"] == "alert-001"


def test_start_incident():
    response = client.post(
        "/api/incidents/start",
        json={
            "alert_id": "alert-001",
        },
    )

    assert response.status_code == 200

    incident = response.json()

    assert incident["incident_id"] == "inc-alert-001"
    assert incident["timeline"]
    assert incident["hypotheses"]
    assert incident["recommended_actions"]


def test_get_unknown_incident():
    response = client.get(
        "/api/incidents/unknown-incident"
    )

    assert response.status_code == 200
    assert response.json()["error"] == "incident_not_found"


def test_approve_action():
    client.post(
        "/api/incidents/start",
        json={
            "alert_id": "alert-001",
        },
    )

    response = client.post(
        "/api/incidents/inc-alert-001/approve",
        json={
            "action_id": "act-002",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
