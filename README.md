# Practice Exercise: Usage Billing Engine

This is an original practice repository inspired by practical Python debugging interviews. It is not an actual Zenskar assessment.

## Scenario
A SaaS product bills customers based on usage events. Each event has an event ID, customer ID, timestamp, and quantity. Customers have a plan with an included monthly allowance and a per-unit price after the allowance. Events may be delivered more than once, and invalid events must not affect invoices.

## Your task (45–60 minutes)
1. Run `python -m pytest -q` and inspect failures.
2. Fix the implementation with minimal, safe changes.
3. Add tests for edge cases you discover.
4. Be ready to explain your assumptions and complexity.

## Rules
- Do not change the public method signatures unless you can justify it.
- Duplicate event IDs must be idempotent: count an event at most once per customer.
- Reject events with blank IDs/customer IDs, negative quantities, or malformed timestamps.
- Bill events in the requested UTC month only.
- Apply the included allowance once per customer per month, across all that customer's events.
- Round the final amount to 2 decimal places, not each event's charge.
- A customer with no billable usage should still receive a zero-amount invoice.

## Run
```bash
pip install -r requirements.txt
python -m pytest -q
```
