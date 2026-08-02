# Safe Remediation Skill

## Goal

Recommend safe remediation actions during an incident.

## Procedure

1. Low-risk actions can be suggested directly.
2. High-risk actions must require human approval.
3. Rollback, production config changes, and database operations are high-risk.
4. Creating an incident ticket is low-risk.

## Output

Each action should include:

- title
- risk
- reason
- requires_approval
