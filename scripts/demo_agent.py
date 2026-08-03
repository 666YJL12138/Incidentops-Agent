import json

from agent.graph import run_investigation


def main():
    alert = {
        "id": "alert-001",
        "service": "checkout-api",
        "severity": "P1",
        "message": "5xx rate jumped to 12% and p95 latency is 2.8s after deployment",
        "status": "open",
    }

    state = run_investigation(alert)

    print(json.dumps(state.model_dump(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
