# Payment Provider Timeout Postmortem

## Summary

Payment API latency increased because the third-party payment provider became unstable. Checkout requests depending on payment confirmation started timing out.

## Impact

- Payment creation success rate dropped.
- Checkout flow became slow for some users.
- Customer support received payment pending reports.
- Incident duration was about 52 minutes.

## Timeline

- 14:08: Payment provider latency started increasing.
- 14:13: payment-api p95 latency alert triggered.
- 14:18: Logs showed external provider timeout errors.
- 14:26: Checkout errors increased after payment latency spike.
- 14:35: Fallback payment status page was enabled.
- 15:00: Provider latency recovered.

## Root Cause

The external payment provider had elevated latency. The internal payment-api did not fail fast, causing requests to wait until timeout.

## Resolution

The team enabled a fallback payment status page and reduced unnecessary retries.

## Follow-up Actions

- Add circuit breaker for payment provider calls.
- Add provider-specific latency dashboard.
- Add alert for payment timeout ratio.
- Document fallback activation steps in the payment timeout runbook.
