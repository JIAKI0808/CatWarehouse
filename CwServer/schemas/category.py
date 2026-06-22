from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "FolderOutline"


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str = "FolderOutline"

    model_config = {"from_attributes": True}
