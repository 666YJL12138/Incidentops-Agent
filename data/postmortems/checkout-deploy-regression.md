# Checkout Deployment Regression Postmortem

## Summary

Checkout API experienced a 5xx spike shortly after version v1.18.3 was deployed. The incident affected checkout submission and payment creation.

## Impact

- Users could not complete checkout reliably.
- 5xx rate increased from 0.3% to 12%.
- p95 latency increased from 450ms to 2.8s.
- Incident duration was about 38 minutes.

## Timeline

- 10:05: v1.18.3 deployed to production.
- 10:12: 5xx alert triggered for checkout-api.
- 10:16: On-call engineer started investigation.
- 10:23: Logs showed payment client timeout and retry errors.
- 10:31: Rollback was approved.
- 10:43: Error rate returned to normal.

## Root Cause

The new deployment changed payment client retry behavior. Failed payment requests were retried too aggressively, increasing upstream pressure and causing checkout requests to timeout.

## Resolution

The team rolled back checkout-api to v1.18.2 and disabled the new retry policy.

## Follow-up Actions

- Add load test coverage for payment retry behavior.
- Add deployment annotation to incident dashboard.
- Require approval for retry policy changes.
- Add runbook entry for retry storm investigation.
