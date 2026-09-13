"""语音录入层：把一段口述音频变成可落库的结构化草稿。

- `asr_*.py` 只负责「音频 → 文本」（本地 whisper / 远程语音接口）。
- `llm_*.py` 只负责「提示词 → 大模型文本」（OpenAI 兼容 / Claude 原生）。
- `prompt.py` 把大模型返回的 JSON 容错解析成 `VoiceCommand`。
- `pipeline.py` 串起上述步骤，并把 `VoiceCommand` 映射成 `receipts` 的 `ReceiptDraft`。
- 落库复用 `receipts/sink.py` 的既有出口，本包**不认识任何数据库模型**。

本文件刻意不 import 任何子模块，保持 `import voice` 轻量无副作用。
"""
