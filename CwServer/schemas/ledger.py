from pydantic import BaseModel
from datetime import datetime


class LedgerCreate(BaseModel):
    amount: float
    date: datetime
    platform: str = ""
    description: str = ""
    notes: str = ""
    person: str = ""
    type: str = "expense"


class LedgerUpdate(BaseModel):
    amount: float | None = None
    date: datetime | None = None
    platform: str | None = None
    description: str | None = None
    notes: str | None = None
    person: str | None = None
    type: str | None = None


class LedgerResponse(BaseModel):
    id: int
    amount: float
    date: datetime
    platform: str
    description: str
    notes: str
    person: str
    type: str

    model_config = {"from_attributes": True}


class LedgerStats(BaseModel):
    period: str
    income: float
    expense: float
