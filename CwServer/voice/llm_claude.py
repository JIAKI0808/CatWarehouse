from __future__ import annotations

import json
import logging

from voice.http_util import post_bytes, preview
from voice.settings import LlmSettings, load_llm_settings

logger = logging.getLogger(__name__)

SERVICE_NAME = "Claude 接口"
BASE_KEY = "VOICE_LLM_BASE"
ANTHROPIC_VERSION = "2023-06-01"


class ClaudeMessagesClient:
    """调用 Anthropic Claude 原生 Messages 接口。

    **不需要安装任何依赖**，只用标准库 `urllib`。
    未配 `VOICE_LLM_BASE` 时用官方地址与路径（见 `voice/settings.py`）。

    刻意**不用 `tool_use` 做结构化抽取**：那会让两个 LLM 实现的返回形态不一致、
    解析层要按 provider 分叉。代价是 schema 约束弱一些，由
    `prompt.extract_json()` 的容错解析兜住（见 plan.md §15.4）。

    与 `OpenAiChatClient` 互为替代，都只按结构满足 `voice.types.LlmClient` 协议。
    """

    def __init__(self, settings: LlmSettings | None = None) -> None:
        self._settings = settings or load_llm_settings()

    def _payload(self, system: str, user: str) -> bytes:
        """构造请求体；system 是顶层字段，不是 messages 里的一条。"""
        body = {
            "model": self._settings.resolved_model(),
            "max_tokens": self._settings.max_tokens,
            "temperature": 0,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        return json.dumps(body, ensure_ascii=False).encode("utf-8")

    def _headers(self) -> dict:
        """构造请求头；Claude 用 `x-api-key`（不是 Bearer）并必须带版本头。"""
        headers = {"Content-Type": "application/json", "anthropic-version": ANTHROPIC_VERSION}
        if self._settings.api_key:
            headers["x-api-key"] = self._settings.api_key
        return headers

    def _text_of(self, payload: dict) -> str:
        """把 content 块列表里的文本拼起来（除文本块外还可能有别的类型）。"""
        blocks = payload.get("content")
        if not isinstance(blocks, list):
            raise RuntimeError(f"{SERVICE_NAME}返回里没有 content: {preview(payload)}")
        text = "".join(block.get("text", "") for block in blocks if isinstance(block, dict))
        if not text.strip():
            raise RuntimeError(f"{SERVICE_NAME}返回里没有文本块: {preview(payload)}")
        return text

    def complete(self, system: str, user: str) -> str:
        """返回模型生成的原始文本（应为 JSON，但不在这里解析，见 `voice/prompt.py`）。

        Raises:
            RuntimeError: 未配置地址、连接失败、服务报错，或返回里取不到文本。
        """
        payload = post_bytes(self._settings.api_url, self._payload(system, user),
                             self._headers(), self._settings.timeout, SERVICE_NAME, BASE_KEY)
        return self._text_of(payload)
