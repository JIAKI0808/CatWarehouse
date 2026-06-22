from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str = ""


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}
