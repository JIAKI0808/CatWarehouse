from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    quantity: int = 0


class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: int

    model_config = {"from_attributes": True}
