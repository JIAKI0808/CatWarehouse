from pydantic import BaseModel


class ImportSubCategoryData(BaseModel):
    name: str
    unit: str = "个"
    description: str = ""
    notes: str = ""


class ImportCategoryData(BaseModel):
    name: str
    description: str = ""
    icon: str = "FolderOutline"
    icon_color: str = "#f59e0b"
    sub_categories: list[ImportSubCategoryData] = []


class ImportRequest(BaseModel):
    categories: list[ImportCategoryData]


class ConflictItem(BaseModel):
    type: str
    name: str
    existing_id: int
    imported_data: dict


class ConflictCheckResponse(BaseModel):
    has_conflicts: bool
    conflicts: list[ConflictItem]


class ImportExecuteRequest(BaseModel):
    categories: list[ImportCategoryData]
    skip_conflicts: list[str] = []


class ImportResult(BaseModel):
    categories_created: int
    sub_categories_created: int
    items_created: int
