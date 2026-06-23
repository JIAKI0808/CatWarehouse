from pydantic import BaseModel


class PricingCategoryCreate(BaseModel):
    name: str
    description: str = ""


class PricingCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class PricingCategoryResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = {"from_attributes": True}


class PricingSubCategoryCreate(BaseModel):
    category_id: int
    name: str
    description: str = ""


class PricingSubCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class PricingSubCategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: str

    model_config = {"from_attributes": True}
