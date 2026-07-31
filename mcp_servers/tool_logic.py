import csv
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
LOG_DIR = DATA_DIR / "logs"
METRIC_DIR = DATA_DIR / "metrics"
DEPLOYMENTS_PATH = DATA_DIR / "deployments.json"
TICKETS_PATH = DATA_DIR / "tickets.json"


def search_logs(service: str, keyword: str = "", limit: int = 20) -> list[dict]:
    log_path = LOG_DIR / f"{service}.log"

    if not log_path.exists():
        return []

    results = []

    for line in log_path.read_text(encoding="utf-8").splitlines():
        if keyword.lower() in line.lower():
            results.append(
                {
                    "service": service,
                    "source": str(log_path),
                    "line": line,
                }
            )

    return results[-limit:]


def query_metrics(service: str) -> dict:
    metric_path = METRIC_DIR / f"{service}.csv"

    if not metric_path.exists():
        return {
            "service": service,
            "error": "metrics_not_found",
        }

    rows = []

    with metric_path.open("r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(
                {
                    "time": row["time"],
                    "error_rate": float(row["error_rate"]),
                    "p95_latency": float(row["p95_latency"]),
                    "cpu": float(row["cpu"]),
                    "memory": float(row["memory"]),
                }
            )

    if not rows:
        return {
            "service": service,
            "error": "metrics_empty",
        }

    max_error_rate = max(row["error_rate"] for row in rows)
    max_p95_latency = max(row["p95_latency"] for row in rows)
    max_cpu = max(row["cpu"] for row in rows)
    max_memory = max(row["memory"] for row in rows)

    return {
        "service": service,
        "points": rows,
        "summary": {
            "max_error_rate": max_error_rate,
            "max_p95_latency": max_p95_latency,
            "max_cpu": max_cpu,
            "max_memory": max_memory,
        },
    }


def get_recent_deployments(service: str) -> list[dict]:
    if not DEPLOYMENTS_PATH.exists():
        return []

    deployments = json.loads(DEPLOYMENTS_PATH.read_text(encoding="utf-8"))

    return [
        deployment
        for deployment in deployments
        if deployment["service"] == service
    ]


def create_ticket(title: str, severity: str, summary: str) -> dict:
    if TICKETS_PATH.exists():
        tickets = json.loads(TICKETS_PATH.read_text(encoding="utf-8"))
    else:
        tickets = []

    ticket = {
        "id": f"INC-{len(tickets) + 1:03d}",
        "title": title,
        "severity": severity,
        "summary": summary,
        "status": "open",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    tickets.append(ticket)

    TICKETS_PATH.write_text(
        json.dumps(tickets, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return ticket
