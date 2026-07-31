# API 5xx Spike Runbook

## Symptoms

- HTTP 5xx rate increases above 5%.
- p95 latency increases quickly.
- User checkout or payment flow may fail.

## Common Causes

- Recent deployment introduced a bug.
- Upstream dependency timeout.
- Database connection pool exhausted.
- Application pods are overloaded.

## Investigation Steps

1. Check whether there was a deployment in the last 2 hours.
2. Query error rate and p95 latency metrics.
3. Search logs for timeout, exception, refused, and 5xx.
4. Compare affected service with upstream dependency status.
5. Check CPU, memory, and pod restart count.

## Safe Actions

- Create an incident ticket.
- Notify service owner.
- Scale application pods if CPU is saturated.
- Prepare rollback if the issue started after deployment.

## Risk Notes

- Do not restart database before confirming database saturation.
- Rollback should require human approval.
