from pydantic import BaseModel


class BudgetCreate(BaseModel):
    category_id: int
    month: str
    amount: float


class BudgetUpdate(BaseModel):
    category_id: int | None = None
    month: str | None = None
    amount: float | None = None


class BudgetResponse(BaseModel):
    id: int
    category_id: int
    category_name: str
    month: str
    amount: float
    spent: float

    model_config = {"from_attributes": True}
