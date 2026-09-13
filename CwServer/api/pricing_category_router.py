"""定价分类与定价子分类 —— 一个文件里的两套纯 CRUD，共用同一个 `router`。

两套都走通用层；用 `add_crud_routes` 而不是各建一个 router 再 `include_router`，
是为了避免包装层在路径或 operationId 上引入差异。
"""

from fastapi import APIRouter
from dataManager.crud.registry import register_crud
from dataManager.crud.router import add_crud_routes
from dataManager.crud.spec import CrudNames, CrudSpec
from models.pricing_category import PricingCategory
from models.pricing_sub_category import PricingSubCategory
from schemas.pricing_category import (
    PricingCategoryCreate,
    PricingCategoryResponse,
    PricingCategoryUpdate,
    PricingSubCategoryCreate,
    PricingSubCategoryResponse,
    PricingSubCategoryUpdate,
)

PRICING_CATEGORY = register_crud(
    CrudSpec(
        name="pricing_category",
        model=PricingCategory,
        response=PricingCategoryResponse,
        path="/pricing-categories",
        id_param="cat_id",
        not_found="Pricing category not found",
        create=PricingCategoryCreate,
        update=PricingCategoryUpdate,
        names=CrudNames(
            list="list_pricing_categories",
            create="create_pricing_category",
            update="update_pricing_category",
            delete="delete_pricing_category",
        ),
    )
)

PRICING_SUB_CATEGORY = register_crud(
    CrudSpec(
        name="pricing_sub_category",
        model=PricingSubCategory,
        response=PricingSubCategoryResponse,
        path="/pricing-sub-categories",
        id_param="sub_id",
        not_found="Pricing sub-category not found",
        create=PricingSubCategoryCreate,
        update=PricingSubCategoryUpdate,
        list_filter="category_id",
        names=CrudNames(
            list="list_pricing_sub_categories",
            create="create_pricing_sub_category",
            update="update_pricing_sub_category",
            delete="delete_pricing_sub_category",
        ),
    )
)

router = APIRouter()
add_crud_routes(router, PRICING_CATEGORY)
add_crud_routes(router, PRICING_SUB_CATEGORY)
