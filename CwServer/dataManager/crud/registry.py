"""资源注册表：资源名 → `CrudSpec`。

这是「创建型」这一类的落点：调用方按**名字**要资源，而不是到处 import 具体模型与
schema；要换实现只改注册处。`dataManager/factory.py` 的抽象工厂按同一思路工作，
本表让 CRUD 资源也能被按名取用。
"""

from __future__ import annotations

from dataManager.crud.spec import CrudSpec

_specs: dict[str, CrudSpec] = {}


def register_crud(spec: CrudSpec) -> CrudSpec:
    """登记一个资源，返回原 spec 以便链式使用。重名会覆盖。"""
    _specs[spec.name] = spec
    return spec


def get_crud(name: str) -> CrudSpec:
    """按名取资源，未注册时报明确错误（而不是给一个空壳）。"""
    spec = _specs.get(name)
    if spec is None:
        raise KeyError(f"未注册的 CRUD 资源: {name}")
    return spec


def registered() -> list[str]:
    """已登记的资源名（排序后），便于自检与排查。"""
    return sorted(_specs)
