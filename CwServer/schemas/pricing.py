from datetime import datetime

from pydantic import BaseModel


class PricingCreate(BaseModel):
    sub_category_id: int
    name: str
    cost: float = 0.0
    suggested_price: float = 0.0
    discount: float = 1.0
    description: str = ""
    notes: str = ""


class PricingUpdate(BaseModel):
    name: str | None = None
    cost: float | None = None
    suggested_price: float | None = None
    discount: float | None = None
    description: str | None = None
    notes: str | None = None


class PricingResponse(BaseModel):
    id: int
    sub_category_id: int
    sub_category_name: str = ""
    name: str
    cost: float
    suggested_price: float
    discount: float
    description: str
    notes: str
    record_date: datetime | None = None

    model_config = {"from_attributes": True}
