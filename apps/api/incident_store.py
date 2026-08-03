import json
import sqlite3
from pathlib import Path

from agent.state import IncidentState


DB_PATH = Path("data/incidents.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            service TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            state_json TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS incident_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT NOT NULL,
            step TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_incident(state: IncidentState):
    connection = get_connection()
    data = state.model_dump()

    connection.execute(
        """
        INSERT OR REPLACE INTO incidents
        (id, service, severity, status, state_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            state.incident_id,
            state.alert["service"],
            state.alert["severity"],
            state.status,
            json.dumps(data, ensure_ascii=False),
        ),
    )

    connection.execute(
        "DELETE FROM incident_events WHERE incident_id = ?",
        (state.incident_id,),
    )

    for event in state.timeline:
        connection.execute(
            """
            INSERT INTO incident_events
            (incident_id, step, message)
            VALUES (?, ?, ?)
            """,
            (
                state.incident_id,
                event["step"],
                event["message"],
            ),
        )

    connection.commit()
    connection.close()


def get_incident(incident_id: str):
    connection = get_connection()

    row = connection.execute(
        "SELECT state_json FROM incidents WHERE id = ?",
        (incident_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return json.loads(row["state_json"])


def get_events(incident_id: str):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT step, message, created_at
        FROM incident_events
        WHERE incident_id = ?
        ORDER BY id
        """,
        (incident_id,),
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]
