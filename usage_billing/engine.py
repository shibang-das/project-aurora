from datetime import datetime
from .models import Invoice, Plan, UsageEvent


class UsageBillingEngine:
    def __init__(self):
        self._events = {}
        self._plans = {}

    def set_plan(self, customer_id: str, plan: Plan) -> None:
        self._plans[customer_id] = plan

    def add_event(self, event: UsageEvent) -> bool:
        if not event.event_id or not event.customer_id or event.quantity < 0:
            return False
        if event.event_id in self._events:
            return False
        
        # count only spaces in customer id edge case
        count_space=0
        for c in event.customer_id:
            if(c==' '):
                count_space+=1
        if(count_space == len(event.customer_id)):
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
        events = [e for e in self._events.values() if e.customer_id == customer_id and start <= datetime.fromisoformat(e.timestamp.replace("Z", "+00:00")) < end]
        total_units = sum(e.quantity for e in events)
        plan = self._plans.get(customer_id)
        billable_units = max(0, total_units - plan.included_units)
        for e in events:
            print(max(0, e.quantity - plan.included_units))
        amount = round(max(0,billable_units) * plan.price_per_unit, 2)
        return Invoice(customer_id, month, total_units, billable_units, amount)
