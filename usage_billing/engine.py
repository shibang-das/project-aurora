from datetime import datetime
from .models import Invoice, Plan, UsageEvent
from threading import Lock


class UsageBillingEngine:
    def __init__(self):
        self._events = {}
        self._plans = {}
        self._lock = Lock()

    def set_plan(self, customer_id: str, plan: Plan) -> None:
        with self._lock:
            self._plans[customer_id] = plan

    def add_event(self, event: UsageEvent) -> bool:

        
        with self._lock:
            if not event.event_id or not event.customer_id or event.quantity < 0:
                return False
            if event.event_id in self._events:
                return False
            
            if not event.customer_id.strip():
                return False
            
            try:
                datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
            except (TypeError, ValueError):
                return False
            self._events[event.event_id] = event
            return True

    def invoice(self, customer_id: str, month: str) -> Invoice:
        start = datetime.fromisoformat(month + "-01T00:00:00+00:00")
        end = datetime(start.year + (start.month == 12), 1 if start.month == 12 else start.month + 1, 1, tzinfo=start.tzinfo)

        with self._lock:
            events = [e for e in self._events.values() if e.customer_id == customer_id and start <= datetime.fromisoformat(e.timestamp.replace("Z", "+00:00")) < end]
            plan = self._plans.get(customer_id)

        if plan is None:
            raise ValueError("No plan configured for customer")

        total_units = sum(e.quantity for e in events)
        billable_units = max(0, total_units - plan.included_units)
        amount = round(max(0,billable_units) * plan.price_per_unit, 2)

        return Invoice(customer_id, month, total_units, billable_units, amount)
