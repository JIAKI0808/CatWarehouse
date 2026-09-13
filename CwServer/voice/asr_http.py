from __future__ import annotations

import logging
import uuid

from voice.http_util import post_bytes, preview
from voice.settings import AsrSettings, load_asr_settings
from voice.types import Transcript

logger = logging.getLogger(__name__)

FIELD_NAME = "file"                  # OpenAI 兼容 /audio/transcriptions 的音频字段名
BOUNDARY_PREFIX = "----CwVoiceForm"
DEFAULT_FILENAME = "audio.wav"
SERVICE_NAME = "语音服务"
BASE_KEY = "VOICE_ASR_BASE"


def _boundary() -> str:
    """每次请求用不同的分隔串，避免音频字节里恰好含分隔串而截断表单。"""
    return f"{BOUNDARY_PREFIX}{uuid.uuid4().hex}"


def _field_part(boundary: str, name: str, value: str) -> bytes:
    """一个普通表单字段的 multipart 片段。"""
    return (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
        f"{value}\r\n"
    ).encode("utf-8")


def _file_part(boundary: str, filename: str, audio: bytes) -> bytes:
    """音频文件的 multipart 片段（音频流统一标 octet-stream，由服务端按内容嗅探）。"""
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{FIELD_NAME}"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    return head + audio + b"\r\n"


def build_multipart(fields: dict[str, str], filename: str, audio: bytes) -> tuple[bytes, str]:
    """构造 multipart/form-data 请求体，返回 `(body, content_type)`。

    手写而不用 `requests`：本模块刻意**只依赖标准库**，这样在没装任何
    第三方包的机器上也能调远程语音接口。
    """
    boundary = _boundary()
    chunks = [_field_part(boundary, key, value) for key, value in fields.items()]
    chunks.append(_file_part(boundary, filename, audio))
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _optional_str(value: object) -> str | None:
    """非空字符串才返回，其余返回 None。"""
    return value.strip() if isinstance(value, str) and value.strip() else None


def _optional_float(value: object) -> float | None:
    """能转成正浮点数才返回，其余返回 None。"""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


class HttpAsrEngine:
    """调用远程语音识别接口（OpenAI 兼容 `POST /audio/transcriptions`）。

    与 `LocalWhisperEngine`（本地自部署）互为替代，接口完全一致。
    **不需要安装任何依赖**，只用标准库 `urllib`（multipart 请求体手写）。

    请求：`POST {VOICE_ASR_BASE}{VOICE_ASR_PATH}`，multipart/form-data，
          字段 `file`（音频）+ `model` + `language`（可选，见 `voice/settings.py`）。
    响应：`{"text": "..."}`；带 `duration` / `language` 时一并取用。

    配置见 `voice/settings.py`（全部来自环境变量）。
    """

    def __init__(self, settings: AsrSettings | None = None) -> None:
        self._settings = settings or load_asr_settings()

    def _send(self, audio: bytes, filename: str) -> dict:
        """发请求取回 JSON。

        网络 / HTTP / JSON 三类错误由 `http_util.post_bytes` 统一转成 `RuntimeError`，
        与两个大模型客户端共用同一套报错口径。
        """
        fields: dict[str, str] = {}
        if self._settings.api_model:
            fields["model"] = self._settings.api_model
        if self._settings.lang:
            fields["language"] = self._settings.lang
        body, content_type = build_multipart(fields, filename or DEFAULT_FILENAME, audio)
        headers = {"Content-Type": content_type}
        if self._settings.api_key:
            headers["Authorization"] = f"Bearer {self._settings.api_key}"
        return post_bytes(self._settings.api_url, body, headers, self._settings.api_timeout,
                          SERVICE_NAME, BASE_KEY)

    def transcribe(self, audio: bytes, filename: str = "") -> Transcript:
        """调用远程接口，返回识别文本。

        `filename` 会作为 multipart 的文件名发出，服务端常据此推断音频格式，
        故调用方应尽量带上真实扩展名（如 `voice.m4a`）。

        Raises:
            ValueError: 音频为空。
            RuntimeError: 未配置地址、连接失败、服务报错，或返回内容无法解析。
        """
        if not audio:
            raise ValueError("音频内容为空")
        payload = self._send(audio, filename)
        text = payload.get("text")
        if not isinstance(text, str):
            raise RuntimeError(f"{SERVICE_NAME}返回里没有 text 字段: {preview(payload)}")
        return Transcript(
            text=text.strip(),
            language=_optional_str(payload.get("language")) or self._settings.lang or None,
            duration=_optional_float(payload.get("duration")),
        )
