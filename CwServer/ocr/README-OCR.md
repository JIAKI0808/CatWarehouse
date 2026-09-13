# CwServer/ocr — 票据视觉识别模块

用 `opencv-python` 做通用票据（发票 / 收据 / 购物小票 / 送货单）的**图像后处理 + 版面分析**，
再经 OCR 引擎抽文本、规则化解析成结构化字段。

```
image bytes
  → preprocess.py   灰度 / 去噪 / 倾斜校正 / 透视矫正 / 去阴影 / 二值化
  → engine_*.py     OCR 取文本行（带 bbox 时直接给坐标）
  → layout.py       表格线检测、文本行检测、行/列聚类、区域切分
  → parser.py       正则 + 关键词 + 表格列 → Receipt
  → Receipt.to_dict() → 可直接 JSON 返回
```

## 依赖安装

```bash
pip install -r CwServer/ocr/requirements-ocr.txt
```

- `opencv-python` / `numpy`：预处理与版面分析必需，已在 OpenCV 5.0.0 上验证。
- `paddleocr` / `paddlepaddle`：**仅 `OCR_ENGINE=local`（本地自部署模型）时必需**，且为**惰性导入** ——
  未安装时 ocr 包其余模块照常 import，只有调用识别方法才报错。
  注意 `paddlepaddle` 对 **Python 3.13 暂无 wheel**，装依赖请用 3.11 / 3.12 环境；
  `requirements-ocr.txt` 已用环境标记自动跳过 3.13。
- **`OCR_ENGINE=http`（调远程 serving）不需要上面两项依赖**，只用 Python 标准库。

> 根目录 `requirements.txt` 未纳入本次改动范围，OCR 依赖独立记录于 `requirements-ocr.txt`。

## 用法

```python
from ocr.pipeline import create_recognizer

recognizer = create_recognizer()            # 默认 PaddleOcrEngine
receipt = recognizer.recognize(image_bytes)  # image_bytes = 上传图片的原始字节
payload = receipt.to_dict()                 # 可直接 json.dumps
```

输出结构：

```json
{
  "doc_type": "delivery",
  "merchant": "星辰调料批发部",
  "date": "2026-09-13",
  "order_no": "SH20260913001",
  "items": [{"name": "花椒", "quantity": 2.0, "unit_price": 12.5, "amount": 25.0}],
  "total": 33.0,
  "raw_text": "...",
  "extra": {"line_count": 8, "row_count": 8, "skew_angle": 0.0, "perspective": false}
}
```

`doc_type` ∈ `invoice | receipt | delivery | unknown`。
`quantity` / `unit_price` / `amount` 允许为 `null`（该列没解析出来）。

### 换引擎 / 挂观察者

```python
from ocr.base import OcrObserver
from ocr.engine_paddle import PaddleOcrEngine
from ocr.pipeline import ReceiptRecognizer

class Log(OcrObserver):
    def on_recognition_complete(self, event):
        print("done:", event.data)

recognizer = ReceiptRecognizer(PaddleOcrEngine(lang="ch"), [Log()])
```

事件顺序与既有 `OcrManager` 一致：`start → progress… → complete | error`。

## 两种引擎（可切换）

两套实现共用同一 `OcrEngine` / `LineOcrEngine` 接口，所以 `create_recognizer()` 与整条流水线都不用改。

| 方式 | 类 | 说明 |
| --- | --- | --- |
| **本地自部署模型** | `PaddleOcrEngine` | 本机直接跑 `paddleocr`；需装 paddlepaddle（Python < 3.13） |
| **调远程接口** | `HttpOcrEngine` | 调 PaddleX / PaddleOCR serving；**不需要装任何 OCR 依赖**，只用标准库 `urllib` |

> `HttpOcrEngine` 因此在 Python 3.13 这类装不上 paddlepaddle 的环境里也能用 —— 只要有一台
> 跑着 serving 的机器（可以是同一台，把服务跑在 3.12 环境里）。

自动选择：`create_recognizer()` 读环境变量，`OCR_ENGINE=http` 且配了 `OCR_API_BASE` 时走 HTTP，
否则走本地。只给了 `OCR_ENGINE=http` 却没给 `OCR_API_BASE` 会**自动退回本地**，
避免配置写一半就把识别整个打死。

### 环境变量（`ocr/settings.py`，不污染 `core/config.py`）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `OCR_ENGINE` | `local` | `local` = 本地自部署模型 / `http` = 调远程 serving |
| `OCR_LANG` | `ch` | 本地模型的语言 |
| `OCR_API_BASE` | 空 | serving 地址，如 `http://127.0.0.1:8080` |
| `OCR_API_PATH` | `/ocr` | serving 路径 |
| `OCR_API_KEY` | 空 | 可选，会以 `Authorization: Bearer` 发送 |
| `OCR_API_TIMEOUT` | `30` | 请求超时秒数 |

```bash
# 本地自部署模型（默认）
python catWarehouse_server.py
# 改调远程 serving
OCR_ENGINE=http OCR_API_BASE=http://127.0.0.1:8080 python catWarehouse_server.py
```

### 远程接口约定（PaddleX / PaddleOCR serving）

```
POST {OCR_API_BASE}{OCR_API_PATH}
  body: {"file": "<base64 图片>", "fileType": 1}
  resp: {"result": {"ocrResults": [{"prunedResult": {
           "rec_texts": [...], "rec_scores": [...], "rec_polys": [...]}}]}}
```

解析**不写死嵌套层数**：按结构递归找带 `rec_texts` 的节点，
serving 换版本改了包装层也不用动代码；找不到时退化为按 2.x 的列表形状解析。

显式指定引擎（绕过环境变量）：

```python
from ocr.engine_http import HttpOcrEngine
from ocr.engine_paddle import PaddleOcrEngine
from ocr.pipeline import create_recognizer
from ocr.settings import OcrSettings

create_recognizer(PaddleOcrEngine(lang="ch"))
create_recognizer(HttpOcrEngine(OcrSettings(api_base="http://127.0.0.1:8080")))
```

## 两条取文本行的路径

| 引擎能力 | 路径 | bbox 来源 |
| --- | --- | --- |
| 实现 `LineOcrEngine.recognize_lines()`（两个引擎都是） | 整图一次识别 | OCR 引擎 |
| 只实现 `OcrEngine.recognize()` | opencv 检测文本行 → 逐行裁剪 → 逐行识别 | opencv |

两条路径产出的 bbox 都以**预处理后的图像**为坐标空间，因此版面分析与字段解析不需要坐标换算。

## 各文件职责

| 文件 | 职责 |
| --- | --- |
| `types.py` | `TextLine` / `ReceiptItem` / `Receipt` / `LineOcrEngine` 协议（不依赖 numpy/cv2） |
| `preprocess.py` | 预处理算子与 `preprocess()`，返回 `image` + `binary`（二者尺寸严格一致） |
| `layout.py` | `detect_table_lines` / `detect_text_lines` / `group_rows` / `group_columns` / `split_regions` / `group_lines_into_rows` |
| `engine_paddle.py` | `PaddleOcrEngine` —— 本地自部署模型（惰性导入 paddleocr） |
| `engine_http.py` | `HttpOcrEngine` —— 调远程 PaddleX / PaddleOCR serving |
| `response.py` | 两个引擎共用的响应解析（rec_texts 结构 / 2.x 列表结构，嵌套层数自适应） |
| `settings.py` | `OcrSettings` —— 环境变量配置（引擎选择、serving 地址与鉴权） |
| `parser.py` | 日期 / 单号 / 总额 / 商户 / 明细的规则抽取 |
| `pipeline.py` | `ReceiptRecognizer` / `create_recognizer()`（按环境变量选引擎） |

## HTTP 接口

已接入后端（`api/ocr_router.py`，注册于 `api/router.py`）。**识别与落库是两个接口**：

```
POST /api/ocr/receipt          multipart/form-data, 字段名 file
  → 200  {"receipt": {...}, "draft": {...}}     # 只读，不写库
  → 400  文件为空、图片无法解码，或远程 OCR 服务判定图片无效（上游 4xx）
  → 503  OCR 引擎不可用（例如未安装 paddleocr、服务未启动、上游 5xx）

POST /api/ocr/receipt/apply    application/json, body = draft
  → 200  {"created_items": [1,2], "updated_sub_categories": [3],
          "created_ledger_id": 7, "skipped": ["无分类: 未指定或找不到分类"],
          "clamped": ["花椒: 库存不足已归零（原 2，需扣 99）"]}
```

**上游 HTTP 状态码会被翻译成对调用方有意义的语义**：4xx（图片格式不认等）→ **400**，
5xx / 连不上 / 非 JSON → **503**。两者按「素材无效」与「服务故障」分开，
前端据此决定是「换张图」还是「稍后重试」。

```bash
# 1) 识别，拿回可编辑的草稿
curl -F "file=@receipt.jpg" http://localhost:11222/api/ocr/receipt
# 2) 前端确认/修改草稿（选分类、勾选、改数量）后提交落库
curl -X POST -H "Content-Type: application/json" \
     -d '{"sub_category_id":3,"items":[{"name":"花椒","quantity":2,"amount":25.0}],
          "create_ledger":true}' \
     http://localhost:11222/api/ocr/receipt/apply
```

`POST /api/upload` 保持原样（只存盘返回 `{path, filename}`），未做改动。

> 引擎实例在 `ocr_router` 内做了**懒加载单例**：PaddleOCR 模型初始化是秒级开销，不能每请求重建。

### 草稿（draft）与落库语义

识别结果不直接落库，而是先映射成一份**客户端可编辑**的草稿，这是刻意的解耦：

```json
{
  "sub_category_id": null,      "recorder": "星辰调料批发部",
  "image_path": null,           "update_stock": true,
  "create_ledger": false,
  "ledger": {"amount": 33.0, "date": "2026-09-13", "platform": "星辰调料批发部",
             "type": "expense", "description": "票据入库: 花椒、酱油"},
  "meta": {"source": "ocr_receipt", "doc_type": "delivery", "order_no": "SH001", "total": 33.0},
  "items": [{"name": "花椒", "quantity": 2, "unit_price": 12.5, "amount": 25.0,
             "selected": true, "sub_category_id": null}]
}
```

落库语义（集中在 `receipts/sink.py`，改这里即可，不动 `ocr/` 与 API）：

| 草稿字段 | 行为 |
| --- | --- |
| `sub_category_id` / item 级 `sub_category_id` | 落库目标分类。**必须显式给**——识别层不猜分类。item 级覆盖顶层 |
| `selected` | 只有 `true` 的明细入库 |
| `update_stock` | 为真时把数量**按 `direction` 的方向**加到 `SubCategory.quantity`（库存数量只存在子分类上）；**出库扣不足时归零**，并在 `clamped` 里说明 |
| `direction` | 票据路径恒为 `in`（入库）；语音路径可为 `out`，见 `voice/README-VOICE.md` |
| `image_path` | 写进 `SpecificItem.image_path`，可把上传的票据图和明细关联起来 |
| `create_ledger` | 为真时额外记一条 `Ledger`（默认 expense）；金额为 0 则跳过 |
| `ledger` | 覆盖账目字段；只接受 `amount/date/platform/description/notes/person/type`，其它键被丢弃 |
| `meta` | 存进 `SpecificItem.extra`（JSON），保留票据溯源信息 |

- 找不到/未指定的分类 → 该明细跳过并在 `skipped` 里说明原因，其余照常写入。
- 全程**单事务**提交，失败不留半截数据。
- 想换落库目标：实现 `receipts.sink.ReceiptSink` 协议，在 `api/ocr_router.py` 换一行构造即可。


## 已知边界

1. **需要装 OCR 引擎才有识别结果**：接口默认用 `PaddleOcrEngine`，
   未安装 paddleocr/paddlepaddle 时返回 503 并附安装指引（本机 Python 3.13 即此情况）。
2. **字段解析是规则式的**：针对中文票据的常见写法（`合计` / `单号` / `日期` 等关键词、数字位序）。
   票据版式差异大时可能需要按实际样例补充关键词与正则，改 `parser.py` 顶部的常量表即可。
3. **无表头时的数字位序约定**：3 个数字按 `数量/单价/金额`；2 个数字按 `数量/金额`
   （本应用库存要数量、账本要金额）；1 个数字视为金额。
   若票据恰好缺列（如只有「单价 金额」而无数量），可能误判——有表头时会按表头映射，不受此影响。
4. **真实识别准确率仍未实测**（两种引擎都一样）：本机装不上 paddlepaddle，
   而 `HttpOcrEngine` 虽然**代码路径已用本地起真实 HTTP 服务完整验证过**
   （请求体 base64/fileType/鉴权头、响应解析、500/连接失败/非 JSON 三类错误），
   但真实 serving 是否按上表约定返回、识别准不准，仍要接上真实服务才能确认。
   若真实 serving 的字段名与约定不同，只需改 `response.py` 一处。
