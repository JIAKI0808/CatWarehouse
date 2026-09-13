from __future__ import annotations

import json
import logging

from voice.http_util import post_bytes, preview
from voice.settings import LlmSettings, load_llm_settings

logger = logging.getLogger(__name__)

SERVICE_NAME = "大模型接口"
BASE_KEY = "VOICE_LLM_BASE"


class OpenAiChatClient:
    """调用 OpenAI 兼容的 `/chat/completions`。

    通吃 DeepSeek / 通义 / Kimi / 智谱 / 本地 vLLM / Ollama 等 —— 只要它们提供
    OpenAI 兼容端点，换供应商只需改 `VOICE_LLM_BASE` + `VOICE_LLM_MODEL`，代码不动。
    **不需要安装任何依赖**，只用标准库 `urllib`。

    `VOICE_LLM_JSON_MODE`（默认开）会带上 `response_format={"type":"json_object"}`；
    部分自建服务不认这个参数会直接 400，此时把它设为 `0` 即可关掉。

    与 `ClaudeMessagesClient` 互为替代，都只按结构满足 `voice.types.LlmClient` 协议。
    """

    def __init__(self, settings: LlmSettings | None = None) -> None:
        self._settings = settings or load_llm_settings()

    def _payload(self, system: str, user: str) -> bytes:
        """构造请求体（温度固定 0：录入场景要的是稳定复现，不是发挥）。"""
        body: dict = {
            "model": self._settings.resolved_model(),
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        }
        if self._settings.json_mode:
            body["response_format"] = {"type": "json_object"}
        return json.dumps(body, ensure_ascii=False).encode("utf-8")

    def _headers(self) -> dict:
        """构造请求头；本地 Ollama 这类无需鉴权的服务可留空 key。"""
        headers = {"Content-Type": "application/json"}
        if self._settings.api_key:
            headers["Authorization"] = f"Bearer {self._settings.api_key}"
        return headers

    def _content_of(self, payload: dict) -> str:
        """从 `choices[0].message.content` 取文本。"""
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError(f"{SERVICE_NAME}返回里没有 choices: {preview(payload)}")
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str):
            raise RuntimeError(f"{SERVICE_NAME}返回里取不到 message.content: {preview(payload)}")
        return content

    def complete(self, system: str, user: str) -> str:
        """返回模型生成的原始文本（应为 JSON，但不在这里解析，见 `voice/prompt.py`）。

        Raises:
            RuntimeError: 未配置地址/模型、连接失败、服务报错，或返回里取不到文本。
        """
        if not self._settings.resolved_model():
            raise RuntimeError("未配置 VOICE_LLM_MODEL，无法调用大模型接口")
        payload = post_bytes(self._settings.api_url, self._payload(system, user),
                             self._headers(), self._settings.timeout, SERVICE_NAME, BASE_KEY)
        return self._content_of(payload)
