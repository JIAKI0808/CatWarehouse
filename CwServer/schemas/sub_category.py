from pydantic import BaseModel


class SubCategoryCreate(BaseModel):
    category_id: int
    name: str
    unit: str = "个"
    description: str = ""
    notes: str = ""


class SubCategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str
    quantity: int
    unit: str
    description: str
    notes: str

    model_config = {"from_attributes": True}
