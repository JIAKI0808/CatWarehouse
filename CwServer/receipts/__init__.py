"""票据落库层：在 `ocr`（纯识别）与数据库之间做解耦。

- `ocr/` 只产出 `Receipt`，不认识任何数据库模型。
- 本包把 `Receipt` 映射成**可编辑草稿**（`draft.py`，纯函数），
  再由 `sink.py` 的落库出口写进库存/账本。
- 想换落库目标或语义，只需替换 `ReceiptSink` 的实现，`ocr/` 与 API 均不受影响。

本文件刻意不 import 任何子模块，保持 `import receipts` 轻量无副作用。
"""
