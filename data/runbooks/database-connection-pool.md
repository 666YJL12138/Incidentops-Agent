# Database Connection Pool Runbook

## Symptoms

- API latency increases.
- Logs contain database connection timeout or pool exhausted.
- Error rate increases during traffic spikes.
- Database CPU may look normal, but application requests fail.

## Common Causes

- Application connection pool size is too small.
- Connections are leaked and not released.
- Slow SQL queries occupy connections for too long.
- A recent deployment changed database access behavior.

## Investigation Steps

1. Search logs for `connection timeout`, `pool exhausted`, `too many connections`, and `SQL timeout`.
2. Check whether the affected service had a recent deployment.
3. Query p95 latency, error rate, and request rate.
4. Check database active connections and slow query count.
5. Compare the issue start time with traffic changes.

## Safe Actions

- Create an incident ticket.
- Notify the database owner and service owner.
- Temporarily scale application pods if CPU is saturated.
- Reduce non-critical traffic if the service is overloaded.
- Prepare rollback if the issue started after deployment.

## Risk Notes

- Do not restart the database before confirming the root cause.
- Increasing connection pool size without analysis may make the database worse.
- Rollback and database configuration changes require human approval.
