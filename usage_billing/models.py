from dataclasses import dataclass


@dataclass(frozen=True)
class UsageEvent:
    event_id: str
    customer_id: str
    timestamp: str
    quantity: int


@dataclass(frozen=True)
class Plan:
    included_units: int
    price_per_unit: float


@dataclass(frozen=True)
class Invoice:
    customer_id: str
    month: str
    total_units: int
    billable_units: int
    amount: float
