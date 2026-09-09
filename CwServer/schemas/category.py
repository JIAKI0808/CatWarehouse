from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "FolderOutline"
    icon_color: str = "#f59e0b"


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    icon: str | None = None
    icon_color: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str
    icon: str = "FolderOutline"
    icon_color: str = "#f59e0b"

    model_config = {"from_attributes": True}
