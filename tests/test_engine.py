from usage_billing.engine import UsageBillingEngine
from usage_billing.models import Plan, UsageEvent


def event(event_id, customer="c1", timestamp="2026-04-15T12:00:00Z", quantity=1):
    return UsageEvent(event_id, customer, timestamp, quantity)


def test_duplicate_event_is_idempotent():
    engine = UsageBillingEngine()
    engine.set_plan("c1", Plan(0, 2.0))
    assert engine.add_event(event("evt1", quantity=3)) is True
    assert engine.add_event(event("evt1", quantity=3)) is False
    invoice = engine.invoice("c1", "2026-04")
    assert invoice.total_units == 3
    assert invoice.amount == 6.0


def test_allowance_applies_across_month_not_per_event():
    engine = UsageBillingEngine()
    engine.set_plan("c1", Plan(5, 2.0))
    engine.add_event(event("evt1", quantity=4))
    engine.add_event(event("evt2", quantity=4))
    invoice = engine.invoice("c1", "2026-04")
    assert invoice.total_units == 8
    assert invoice.billable_units == 3
    assert invoice.amount == 6.0


def test_only_events_in_requested_utc_month_count():
    engine = UsageBillingEngine()
    engine.set_plan("c1", Plan(0, 1.5))
    engine.add_event(event("before", timestamp="2026-03-31T23:59:59Z", quantity=10))
    engine.add_event(event("inside", timestamp="2026-04-01T00:00:00Z", quantity=2))
    engine.add_event(event("after", timestamp="2026-05-01T00:00:00Z", quantity=10))
    invoice = engine.invoice("c1", "2026-04")
    assert invoice.total_units == 2
    assert invoice.amount == 3.0


def test_invalid_events_are_rejected():
    engine = UsageBillingEngine()
    assert engine.add_event(event("", quantity=1)) is False
    assert engine.add_event(event("negative", quantity=-1)) is False
    assert engine.add_event(event("bad-time", timestamp="not-a-time")) is False
    assert engine.add_event(event("blank-customer", customer=" ", quantity=1)) is False


def test_round_only_final_amount():
    engine = UsageBillingEngine()
    engine.set_plan("c1", Plan(0, 0.335))
    engine.add_event(event("a", quantity=1))
    engine.add_event(event("b", quantity=1))
    engine.add_event(event("c", quantity=1))
    assert engine.invoice("c1", "2026-04").amount == 1.01


def test_zero_usage_invoice():
    engine = UsageBillingEngine()
    engine.set_plan("c1", Plan(10, 2.0))
    invoice = engine.invoice("c1", "2026-04")
    assert invoice.total_units == 0
    assert invoice.billable_units == 0
    assert invoice.amount == 0.0
