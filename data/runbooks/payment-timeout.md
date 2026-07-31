# Payment Timeout Runbook

## Symptoms

- Payment API latency increases.
- Logs contain payment provider timeout.
- Checkout requests fail or stay pending.

## Common Causes

- Third-party payment provider degraded.
- Retry policy is too aggressive.
- Network latency increased.
- Payment client timeout configuration changed.

## Investigation Steps

1. Search logs for payment timeout and retry.
2. Check deployment history for payment client changes.
3. Query payment-api p95 latency and error rate.
4. Check whether checkout-api errors increased after payment errors.

## Safe Actions

- Create an incident ticket.
- Reduce retry pressure if retry storm is suspected.
- Enable fallback payment status page.
- Notify customer support.

## Risk Notes

- Do not disable payment verification.
- Do not change retry policy without approval.
