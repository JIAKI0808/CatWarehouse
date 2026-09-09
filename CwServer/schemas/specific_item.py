from datetime import datetime

from pydantic import BaseModel


class SpecificItemCreate(BaseModel):
    sub_category_id: int
    name: str
    recorder: str = ""
    price: float = 0.0
    description: str = ""
    expire_date: datetime | None = None
    is_expired: bool = False


class SpecificItemUpdate(BaseModel):
    name: str | None = None
    recorder: str | None = None
    price: float | None = None
    description: str | None = None
    quantity: int | None = None
    unit: str | None = None
    expire_date: datetime | None = None
    is_expired: bool | None = None


class SpecificItemResponse(BaseModel):
    id: int
    sub_category_id: int
    sub_category_name: str = ""
    quantity: int = 0
    unit: str = ""
    name: str
    entry_date: datetime | None = None
    update_date: datetime | None = None
    expire_date: datetime | None = None
    is_expired: bool = False
    recorder: str
    price: float
    description: str

    model_config = {"from_attributes": True}
