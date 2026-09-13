"""dataManager.crud —— 通用 CRUD 层。

本包把「一个资源的标准增删改查」抽成可复用的三层，供 `api/` 的路由声明式使用：

    spec.py        CrudSpec / CrudNames        声明式资源规格（创建型）
    repository.py  SqlAlchemyRepository        AsyncSession → 统一仓储接口（结构型：适配器）
    registry.py    资源名 → CrudSpec 注册表     （创建型：抽象工厂的注册表）
    router.py      build_crud_router(spec)      五步骨架 + 钩子（行为型：模板方法）

刻意**不在这里 import 子模块**，保持 `import dataManager.crud` 轻量
（与 `voice/__init__.py`、`receipts/__init__.py` 同样的取舍）。
"""
