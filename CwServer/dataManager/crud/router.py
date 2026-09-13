"""按资源规格生成一组标准 CRUD 端点。

**行为型：模板方法** —— 增删改查五步骨架在这里固定下来，资源之间的差异
全部通过 `CrudSpec` 的字段与钩子（`list_filter` / `list_query` / `to_response`）
表达；**结构型：门面** —— 调用方一次 `build_crud_router(spec)` 就拿到五个端点。

两个必须遵守的实现约束（都踩过坑，见 plan.md §28.6）：
1. **端点函数不能有返回类型注解**。FastAPI 在 `response_model` 缺省时用返回注解
   推导响应 schema，补一个 `-> Any` 会让 `/openapi.json` 从 `"schema": {}`
   变成带 title 的 schema，接口就变了。
2. **handler 闭包不能写 docstring**。FastAPI 会把 `__doc__` 填进 OpenAPI 的
   `description`，而改造前的端点都没有 docstring，写了同样是漂移。

端点函数名由 `CrudNames` 逐字给出，因为它决定 `operationId` 与 `summary`。
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.repository import SqlAlchemyRepository
from dataManager.crud.spec import CrudSpec

EMPTY = inspect.Parameter.empty
_ITEM_ACTIONS = ("get", "update", "delete")


def _param(name: str, annotation: Any, default: Any = EMPTY) -> inspect.Parameter:
    """造一个位置或关键字参数。"""
    return inspect.Parameter(
        name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation, default=default
    )


def _signature(spec: CrudSpec, action: str) -> inspect.Signature:
    """按动作造端点签名：路径参数名、请求体类型、数据库依赖全部取自 spec。

    路径参数名必须是 `spec.id_param`（如 `cat_id`），FastAPI 靠它把 URL 里的
    `{cat_id}` 绑到函数参数上，改了名字接口就变了。
    """
    params: list[inspect.Parameter] = []
    if action in _ITEM_ACTIONS:
        params.append(_param(spec.id_param, int))
    if action == "create":
        params.append(_param("data", spec.create))
    elif action == "update":
        params.append(_param("data", spec.update))
    elif action == "list" and spec.list_filter:
        params.append(_param(spec.list_filter, int | None, default=None))
    params.append(_param("db", AsyncSession, default=Depends(get_db)))
    return inspect.Signature(params)


def _mint(handler: Any, name: str, signature: inspect.Signature) -> Any:
    """给闭包改名并装上签名 —— FastAPI 通过 `__signature__` 读取参数。"""
    handler.__name__ = name
    handler.__qualname__ = name
    handler.__signature__ = signature
    return handler


def _repo(spec: CrudSpec, db: AsyncSession) -> SqlAlchemyRepository:
    """本资源对应的仓储。"""
    return SqlAlchemyRepository(db, spec.model)


def _respond(spec: CrudSpec, obj: Any) -> Any:
    """响应钩子：联表等场景由 `spec.to_response` 覆盖，默认原样返回。"""
    return spec.to_response(obj) if spec.to_response else obj


def _handler_list(spec: CrudSpec) -> Callable[..., Any]:
    async def _list(**kwargs):
        db = kwargs["db"]
        field = spec.list_filter
        value = kwargs.get(field) if field else None
        if field and value is not None:
            return await _repo(spec, db).find(field, value)
        return await _repo(spec, db).get_all()

    return _list


def _handler_get(spec: CrudSpec) -> Callable[..., Any]:
    async def _get(**kwargs):
        obj = await _repo(spec, kwargs["db"]).get(kwargs[spec.id_param])
        if obj is None:
            raise HTTPException(404, spec.not_found)
        return _respond(spec, obj)

    return _get


def _handler_create(spec: CrudSpec) -> Callable[..., Any]:
    async def _create(**kwargs):
        created = await _repo(spec, kwargs["db"]).create(kwargs["data"].model_dump())
        return _respond(spec, created)

    return _create


def _handler_update(spec: CrudSpec) -> Callable[..., Any]:
    async def _update(**kwargs):
        payload = kwargs["data"].model_dump(exclude_unset=True)
        updated = await _repo(spec, kwargs["db"]).update(kwargs[spec.id_param], payload)
        if updated is None:
            raise HTTPException(404, spec.not_found)
        return _respond(spec, updated)

    return _update


def _handler_delete(spec: CrudSpec) -> Callable[..., Any]:
    async def _delete(**kwargs):
        if not await _repo(spec, kwargs["db"]).delete(kwargs[spec.id_param]):
            raise HTTPException(404, spec.not_found)
        return {"ok": True}

    return _delete


_HANDLERS: dict[str, Callable[[CrudSpec], Any]] = {
    "list": _handler_list,
    "get": _handler_get,
    "create": _handler_create,
    "update": _handler_update,
    "delete": _handler_delete,
}


def _register(router: APIRouter, spec: CrudSpec, action: str) -> None:
    """注册一个端点。五个动作在路径、方法、响应模型上的差异只写在这里。"""
    item_path = f"{spec.path}/{{{spec.id_param}}}"
    handler = _mint(_HANDLERS[action](spec), getattr(spec.names, action), _signature(spec, action))
    if action == "list":
        router.add_api_route(spec.path, handler, methods=["GET"], response_model=list[spec.response])
    elif action == "create":
        router.add_api_route(spec.path, handler, methods=["POST"], response_model=spec.response)
    elif action == "delete":
        router.add_api_route(item_path, handler, methods=["DELETE"])
    else:
        method = "GET" if action == "get" else "PUT"
        router.add_api_route(item_path, handler, methods=[method], response_model=spec.response)


def add_crud_routes(router: APIRouter, spec: CrudSpec) -> None:
    """把一组标准端点挂到已有 router 上。

    一个文件里有多套 CRUD 时（如 pricing_category_router）用它共用同一个 router，
    避免 `include_router` 的包装在路径或 operationId 上引入差异。
    """
    for action in spec.actions():
        _register(router, spec, action)


def build_crud_router(spec: CrudSpec) -> APIRouter:
    """按规格产出一组标准 CRUD 端点。要生成哪些动作由 `spec.names` 里的非 None 决定。"""
    router = APIRouter()
    add_crud_routes(router, spec)
    return router
