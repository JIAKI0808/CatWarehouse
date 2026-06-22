from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: str
    quantity: int
    price: float


class TrendResponse(BaseModel):
    sub_category_id: int
    sub_category_name: str
    unit: str
    data: list[TrendPoint]
