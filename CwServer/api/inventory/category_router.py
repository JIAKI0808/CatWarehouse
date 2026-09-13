"""分类（Category）的 CRUD —— 端点由 `dataManager.crud` 的通用层生成。

原先是 59 行的五段样板（list/create/get/update/delete 各写一遍），现在只剩一份声明：
这个资源与其他纯 CRUD 资源的差异，全都在 `CrudSpec` 里。
"""

from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.category import Category
from schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

CATEGORY = register_crud(
    CrudSpec(
        name="category",
        model=Category,
        response=CategoryResponse,
        path="/categories",
        id_param="cat_id",
        not_found="Category not found",
        create=CategoryCreate,
        update=CategoryUpdate,
        names=CrudNames(
            list="list_categories",
            get="get_category",
            create="create_category",
            update="update_category",
            delete="delete_category",
        ),
    )
)

router = build_crud_router(CATEGORY)
