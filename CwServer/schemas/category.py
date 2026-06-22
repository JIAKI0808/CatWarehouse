from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "FolderOutline"


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str = "FolderOutline"

    model_config = {"from_attributes": True}
