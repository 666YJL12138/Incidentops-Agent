# Kubernetes CrashLoopBackOff Runbook

## Symptoms

- Pods repeatedly restart.
- Kubernetes status shows CrashLoopBackOff.
- Service availability decreases.
- Logs may contain startup failure, missing environment variable, or dependency error.

## Common Causes

- Recent deployment introduced a startup bug.
- Required environment variable is missing.
- Container image is broken.
- Application cannot connect to database, Redis, or another dependency.
- Memory limit is too low and the container is killed.

## Investigation Steps

1. Check pod restart count and last restart time.
2. Inspect container logs before the latest crash.
3. Check Kubernetes events for OOMKilled, image pull errors, or failed probes.
4. Compare the crash start time with recent deployments.
5. Verify configuration changes and environment variables.

## Safe Actions

- Create an incident ticket.
- Notify service owner.
- Scale healthy replicas if available.
- Prepare rollback to the previous stable image.
- Increase memory limit only after confirming OOMKilled.

## Risk Notes

- Do not delete all pods at once.
- Do not change production configuration without review.
- Rollback should require human approval.
