# Database Pool Exhausted Postmortem

## Summary

Checkout API returned intermittent 5xx errors because application database connections were exhausted during a traffic spike.

## Impact

- Checkout requests failed intermittently.
- Error rate increased to 7%.
- p95 latency increased to 1.9s.
- Incident duration was about 44 minutes.

## Timeline

- 19:20: Traffic increased during promotion campaign.
- 19:27: checkout-api latency alert triggered.
- 19:31: Logs showed database connection pool exhausted.
- 19:38: Slow query count increased.
- 19:49: Non-critical traffic was reduced.
- 20:04: Error rate returned to normal.

## Root Cause

A slow query occupied database connections for too long. During the traffic spike, the application connection pool reached its limit and new requests failed.

## Resolution

The team reduced non-critical traffic and optimized the slow query.

## Follow-up Actions

- Add slow query alert.
- Add connection pool usage dashboard.
- Review database access pattern in checkout-api.
- Add load test for promotion traffic.
