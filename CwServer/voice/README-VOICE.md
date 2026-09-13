# CwServer/voice — 语音录入模块

口述一句「今天进货花椒两斤一共五十」→ 自动整理成结构化数据 → 落库（入库 / 出库）。

```
音频 bytes
  → asr_*.py       语音识别取文本（本地 faster-whisper / 调远程语音接口）
  → llm_*.py       大模型把口语整理成结构化指令（OpenAI 兼容 / Claude 原生）
  → prompt.py      容错取出 JSON → VoiceCommand
  → pipeline.py    VoiceCommand → ReceiptDraft（复用 receipts/ 的中间契约）
  → receipts/sink.py  落库：direction 决定库存累加还是扣减、账目默认支出还是收入
```

## 依赖安装

```bash
pip install -r CwServer/voice/requirements-voice.txt
```

- **只有「本地自部署 whisper」这一条路径需要装依赖**（`faster-whisper`）。
  它基于 CTranslate2，**不需要装 torch**；首次调用会下载模型权重（默认 `small` 约 500MB）。
- **调远程语音接口**（`VOICE_ASR_ENGINE=http`）与**大模型调用**（两种 provider）
  都**只用 Python 标准库 `urllib`**，不需要任何第三方包。
- 根目录 `requirements.txt` 未纳入本次改动范围，依赖独立记录于 `requirements-voice.txt`。

## 用法

```python
from voice.pipeline import command_to_draft, create_recognizer

recognizer = create_recognizer()                 # 按环境变量选引擎
command = recognizer.recognize(audio_bytes, "voice.m4a")
draft = command_to_draft(command)                # 可直接 model_dump() 交给前端确认

print(command.to_dict())
```

输出结构：

```json
{
  "direction": "in",
  "items": [{"name": "花椒", "quantity": 2, "unit": "斤",
             "unit_price": 15.0, "amount": 30.0, "category_hint": "调料"}],
  "merchant": "星辰调料批发部",
  "date": "2026-09-13",
  "total": 50.0,
  "note": "给了优惠",
  "raw_text": "今天进货花椒两斤一共五十",
  "extra": {"source": "voice", "asr_language": "zh", "asr_duration": 3.2}
}
```

`direction` ∈ `in`（入库）| `out`（出库）。

## 两套引擎，各自可切换

### 语音识别

| 方式 | 类 | 依赖 |
| --- | --- | --- |
| **本地自部署模型** | `LocalWhisperEngine` | 需 `faster-whisper` |
| **调远程接口** | `HttpAsrEngine` | **不需要任何依赖**（OpenAI 兼容 `/audio/transcriptions`，multipart 手写） |

### 大模型

| 方式 | 类 | 依赖 |
| --- | --- | --- |
| **OpenAI 兼容** | `OpenAiChatClient` | 无（标准库） |
| **Claude 原生** | `ClaudeMessagesClient` | 无（标准库） |

OpenAI 兼容这一路通吃 DeepSeek / 通义 / Kimi / 智谱 / 本地 vLLM / Ollama ——
换供应商只改 `VOICE_LLM_BASE` + `VOICE_LLM_MODEL`，**代码不动**。

两套引擎都只按结构满足 `voice/types.py` 里的 `AsrEngine` / `LlmClient` 协议（鸭子类型），
所以 `create_recognizer()` 与整条流水线都不用改。

### 环境变量（`voice/settings.py`，不污染 `core/config.py`）

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `VOICE_ASR_ENGINE` | `local` | `local` 本地 whisper / `http` 调远程语音接口 |
| `VOICE_WHISPER_MODEL` | `small` | 本地模型名或大小 |
| `VOICE_WHISPER_DEVICE` / `VOICE_WHISPER_COMPUTE` | `cpu` / `int8` | 本地推理设备与量化 |
| `VOICE_ASR_LANG` | `zh` | 语言提示；填 `auto` 交给引擎自动检测 |
| `VOICE_ASR_BASE` | 空 | 远程语音接口地址，如 `http://127.0.0.1:9000` |
| `VOICE_ASR_PATH` | `/audio/transcriptions` | 远程语音接口路径 |
| `VOICE_ASR_KEY` | 空 | 可选，以 `Authorization: Bearer` 发送 |
| `VOICE_ASR_MODEL` | `whisper-1` | 远程接口的模型名 |
| `VOICE_ASR_TIMEOUT` | `60` | 请求超时秒数 |
| `VOICE_LLM_PROVIDER` | `openai` | `openai` OpenAI 兼容 / `claude` Claude 原生 |
| `VOICE_LLM_BASE` | 空 | 接口地址；`claude` 未配时用 `https://api.anthropic.com` |
| `VOICE_LLM_PATH` | 按 provider | 留空则 `openai` 用 `/chat/completions`、`claude` 用 `/v1/messages` |
| `VOICE_LLM_KEY` | 空 | API Key（Ollama 这类无需鉴权的服务可留空） |
| `VOICE_LLM_MODEL` | 按 provider | `claude` 未配时用 `claude-sonnet-5`；OpenAI 兼容侧须显式配 |
| `VOICE_LLM_TIMEOUT` | `60` | 请求超时秒数 |
| `VOICE_LLM_MAX_TOKENS` | `1024` | 最大生成长度 |
| `VOICE_LLM_JSON_MODE` | `1` | 是否发 `response_format=json_object`；自建服务不认这个参数时设 `0` |

`VOICE_ASR_ENGINE=http` 但没配 `VOICE_ASR_BASE` 会**自动退回本地**，配置写一半不至于把功能打死。

```bash
# 本地 whisper + 默认 OpenAI 兼容大模型
python catWarehouse_server.py
# 语音走远程接口、大模型走 Claude
VOICE_ASR_ENGINE=http VOICE_ASR_BASE=http://127.0.0.1:9000 \
VOICE_LLM_PROVIDER=claude VOICE_LLM_KEY=sk-ant-xxx python catWarehouse_server.py
```

### 远程接口约定

**语音识别**（OpenAI 兼容）：

```
POST {VOICE_ASR_BASE}{VOICE_ASR_PATH}
  body: multipart/form-data
        file=<音频>  model=whisper-1  language=zh     # model / language 为空时不发送
  resp: {"text": "...", "language": "zh", "duration": 3.4}   # 后两个可缺
```

**大模型**（二选一，路径与鉴权头不同，请求体形状也不同）：

```
POST {VOICE_LLM_BASE}/chat/completions          Authorization: Bearer <key>
  {"model": "...", "messages": [{"role":"system",...},{"role":"user",...}],
   "temperature": 0, "response_format": {"type": "json_object"}}
  resp: {"choices": [{"message": {"content": "<JSON 文本>"}}]}

POST {VOICE_LLM_BASE}/v1/messages               x-api-key: <key>  anthropic-version: 2023-06-01
  {"model": "...", "max_tokens": 1024, "temperature": 0,
   "system": "<系统提示词>", "messages": [{"role": "user", "content": "..."}]}
  resp: {"content": [{"type": "text", "text": "<JSON 文本>"}]}
```

> Claude 侧刻意**没用 `tool_use`**：那会让两个实现的返回形态不一致、解析层要按 provider 分叉。
> 代价是 schema 约束弱一些，由 `prompt.extract_json()` 的容错解析兜住。

## 取 JSON 的三层容错

模型返回不可能总是干净的 JSON，`prompt.extract_json()` 依次尝试：

1. 直接解析整段文本；
2. 剥掉 ``` 围栏后解析（模型爱加 markdown 代码块）；
3. 从**首个 `{`** 起 `raw_decode` 一个完整对象，后面的内容一概忽略
   （模型在 JSON 后面又补一段话、甚至再给一个对象时用这条，规则是**取第一个完整对象**）。

三层全失败才抛 `LlmReplyError`，**绝不返回空壳** —— 猜出来的数据会静默污染库存，
宁可让调用方看到明确的失败。

## 各文件职责

| 文件 | 职责 |
| --- | --- |
| `types.py` | `Transcript` / `VoiceItem` / `VoiceCommand` / `AsrEngine` 协议 / `LlmClient` 协议 / `LlmReplyError`（不依赖第三方） |
| `settings.py` | `AsrSettings` / `LlmSettings` 与环境变量读取；provider 相关默认值集中在 `resolved_*()` |
| `asr_local.py` | `LocalWhisperEngine` —— 本地 faster-whisper（惰性导入） |
| `asr_http.py` | `HttpAsrEngine` —— 远程语音接口（multipart 手写，只用标准库） |
| `llm_openai.py` | `OpenAiChatClient` —— OpenAI 兼容 `/chat/completions` |
| `llm_claude.py` | `ClaudeMessagesClient` —— Claude 原生 Messages 接口 |
| `http_util.py` | 三处 HTTP 调用点**共用**的错误映射出口（`post_bytes` / `preview`） |
| `prompt.py` | 提示词构造 + JSON 容错解析 + 口语 → `VoiceCommand` |
| `pipeline.py` | `VoiceRecognizer` / `command_to_draft()` / `create_recognizer()` |

## HTTP 接口

已接入后端（`api/voice_router.py`，注册于 `api/router.py`）。**识别与落库是两个接口**：

```
POST /api/voice/record         multipart/form-data, 字段名 file（音频）
  → 200  {"command": {...}, "draft": {...}}     # 只读，不写库
  → 400  文件为空，/ 音频无法解码，/ 没识别出语音内容，
         / 语音或大模型服务判定素材无效（上游 4xx，例如音频格式它不认）
  → 502  大模型返回无法解析成结构化指令
  → 503  语音引擎或大模型不可用（如未装 faster-whisper、服务未启动、上游 5xx）

POST /api/voice/record/apply   application/json, body = draft
  → 200  {"created_items": [1,2], "updated_sub_categories": [3],
          "created_ledger_id": 7, "skipped": ["无分类: 未指定或找不到分类"],
          "clamped": ["酱油: 库存不足已归零（原 0，需扣 5）"]}
```

```bash
# 1) 识别，拿回可编辑的草稿（command 里同时带识别原文）
curl -F "file=@voice.m4a" http://localhost:11222/api/voice/record
# 2) 前端确认/修改草稿（选分类、勾选、改数量）后提交落库
curl -X POST -H "Content-Type: application/json" \
     -d '{"direction":"in","sub_category_id":3,
          "items":[{"name":"花椒","quantity":2,"amount":30.0}],
          "create_ledger":true}' \
     http://localhost:11222/api/voice/record/apply
```

> 引擎实例在 `voice_router` 内做了**懒加载单例**：whisper 模型初始化（含首次下载）是秒级开销。

**上游 HTTP 状态码会被翻译成对调用方有意义的语义**（见 `http_util.post_bytes`）：

| 上游返回 | 抛出的异常 | 端点回 | 含义 |
| --- | --- | --- | --- |
| 4xx | `UpstreamRejectedError(RuntimeError)` | **400** | 素材无效（音频格式不认等）——改输入就能解决 |
| 5xx | `RuntimeError` | **503** | 上游服务出问题——稍后重试 |
| 连不上 / 非 JSON | `RuntimeError` | **503** | 地址配错或服务没起 |

这个区分是端到端实测逼出来的：最初所有 HTTP 错误都被揉成一个 `RuntimeError`，
结果「音频格式不认」被回成了 503，前端会误以为服务挂了。

### 分类建议（与票据路径的关键差异）

票据上没有分类信息，所以 `ocr` 那条路「识别层不猜分类，客户端显式传 id」。
但语音里用户**会开口说出分类**（「进货调料花椒」），不给建议则体验不可用。

做法：`voice/` 仍然**完全不认识数据库**，大模型只输出 `category_hint`（口语里说到的分类名词）；
由**端点层**拿 hint（其次品名）去和 `SubCategory.name` 匹配：

1. 先精确匹配（分类名词 → 品名），再子串匹配；
2. **只认唯一命中**；命中多个就留空由用户在草稿里自己选 —— 不替用户赌；
3. 命中结果填入 `draft.items[i].sub_category_id`，并在
   `draft.meta["category_match"]` 里逐项记下 `reason`
   （`exact:调料` / `partial:花椒` / `ambiguous:花椒` / `not_found`），前端可据此解释为什么没预填。

### 草稿（draft）与落库语义

识别结果不直接落库，先映射成一份**客户端可编辑**的草稿（与票据路径共用同一契约）：

```json
{
  "direction": "in",            "sub_category_id": 3,
  "recorder": "星辰调料批发部",   "image_path": null,
  "update_stock": true,         "create_ledger": false,
  "ledger": {"amount": 50.0, "date": "2026-09-13", "platform": "星辰调料批发部",
             "type": "expense", "description": "语音入库: 花椒、酱油", "notes": "给了优惠"},
  "meta": {"source": "voice", "direction": "in", "raw_text": "今天进货花椒两斤一共五十",
           "category_hints": ["调料", null], "category_match": [...]},
  "items": [{"name": "花椒", "quantity": 2, "unit_price": 15.0, "amount": 30.0,
             "selected": true, "sub_category_id": 3}]
}
```

落库语义集中在 `receipts/sink.py`（改这里即可，不动 `voice/` 与 API）：

| 草稿字段 | 行为 |
| --- | --- |
| `direction` | `in` → 库存**累加**、账目默认 `expense`；`out` → 库存**扣减**、账目默认 `income` |
| 出库扣不足 | **归零**（不扣成负数），并在 `clamped` 里如实汇报「原多少、需扣多少」 |
| `sub_category_id` / item 级 | 落库目标分类。**必须显式给**（端点会先按口述线索预填建议）。item 级覆盖顶层 |
| `selected` | 只有 `true` 的明细入库 |
| `update_stock` | 为真时按 `direction` 的方向改 `SubCategory.quantity` |
| `create_ledger` | 为真时额外记一条 `Ledger`（类型默认取 `direction`，可被 `ledger` 覆盖）；金额为 0 则跳过 |
| `ledger` | 覆盖账目字段；只接受 `amount/date/platform/description/notes/person/type`，其它键被丢弃 |
| `meta` | 存进 `SpecificItem.extra`（JSON），保留口述原文与语音信息以便溯源 |

- **出库扣不足时归零**，不扣成负数：库存为负不是有效状态，用户多半只是先卖了货、
  还没来得及登记进货。但归零**必须说出来** —— 静默改数会让人以为库存是准的，
  所以差额记进 `ApplyResult.clamped`（`酱油: 库存不足已归零（原 0，需扣 5）`），
  同时打一条 `WARNING` 日志。想改回「允许负数」只动 `sink.py` 的 `_apply_stock()` 一处。
- 找不到/未指定的分类 → 该明细跳过并在 `skipped` 里说明原因，其余照常写入。
- 全程**单事务**提交，失败不留半截数据。

## 已知边界

1. **语音识别准确率未实测**：本机装不上 `faster-whisper`（未授权安装），
   故本地这条路径只验证了「未装依赖时的报错与替代指引」。
   `HttpAsrEngine` 的代码路径已用**本地真实 HTTP 服务**完整验证过（请求形状、字段、鉴权、错误路径）。
2. **大模型返回结构由提示词约束**：`prompt.py` 的 `SYSTEM_PROMPT` 声明输出结构，
   解析层只做结构容错、不做业务猜测。换模型或换供应商后若字段风格变化，改提示词即可。
3. **需要配好大模型才可用**：这是全链路里唯一必须有外部服务的一环 ——
   口语理解没法用规则兜底（票据那边至少还有正则）。
4. **一次请求一段音频、同步返回**：没有做流式识别、唤醒词、长音频分段。
5. `voice/` 与 `ocr/` 互不依赖，两者共用的只有 `receipts/` 这一层落库出口。
