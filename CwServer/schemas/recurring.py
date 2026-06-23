from pydantic import BaseModel
from datetime import datetime


class RecurringBillCreate(BaseModel):
    amount: float
    description: str = ""
    platform: str = ""
    person: str = ""
    type: str = "expense"
    frequency: str = "monthly"
    next_date: datetime


class RecurringBillUpdate(BaseModel):
    amount: float | None = None
    description: str | None = None
    platform: str | None = None
    person: str | None = None
    type: str | None = None
    frequency: str | None = None
    next_date: datetime | None = None
    is_active: bool | None = None


class RecurringBillResponse(BaseModel):
    id: int
    amount: float
    description: str
    platform: str
    person: str
    type: str
    frequency: str
    next_date: datetime
    is_active: bool

    model_config = {"from_attributes": True}
