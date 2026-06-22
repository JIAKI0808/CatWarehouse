from datetime import datetime

from pydantic import BaseModel


class SpecificItemCreate(BaseModel):
    sub_category_id: int
    name: str
    recorder: str = ""
    price: float = 0.0
    description: str = ""


class SpecificItemUpdate(BaseModel):
    name: str | None = None
    recorder: str | None = None
    price: float | None = None
    description: str | None = None


class SpecificItemResponse(BaseModel):
    id: int
    sub_category_id: int
    name: str
    entry_date: datetime | None = None
    update_date: datetime | None = None
    recorder: str
    price: float
    description: str

    model_config = {"from_attributes": True}
