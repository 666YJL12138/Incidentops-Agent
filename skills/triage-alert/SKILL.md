# Alert Triage Skill

## Goal

Classify an incoming production alert and decide the initial investigation focus.

## Procedure

1. Identify the service name, severity, symptom, and user impact.
2. If severity is P1, prioritize fast evidence collection.
3. Determine whether the alert is related to latency, 5xx errors, timeout, deployment, or resource saturation.
4. Produce a short triage summary.

## Output

- severity
- affected_service
- symptom_summary
- initial_focus
