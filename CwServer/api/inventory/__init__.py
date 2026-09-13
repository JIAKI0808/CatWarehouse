"""库存分区 —— 大类 / 子分类 / 明细条目 / 标签。

分区规则见 `api/__init__.py`。本文件刻意不 import 子模块：`import api.inventory`
必须是轻量的，聚合入口是 `api.inventory.router`。
"""
