from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

ENGINE_LOCAL = "local"
ENGINE_HTTP = "http"
DEFAULT_ENGINE = ENGINE_LOCAL
DEFAULT_LANG = "ch"
DEFAULT_API_PATH = "/ocr"
DEFAULT_TIMEOUT = 30.0


@dataclass(frozen=True)
class OcrSettings:
    """OCR 运行配置，全部来自环境变量。

    刻意不放进 `core/config.py`：OCR 模块保持自包含，接不接、怎么接都不影响主配置。

    环境变量：
        OCR_ENGINE      local | http，默认 local（本地自部署 PaddleOCR 模型）
        OCR_LANG        识别语言，默认 ch
        OCR_API_BASE    http 模式的 serving 地址，如 http://127.0.0.1:8080
        OCR_API_PATH    serving 路径，默认 /ocr
        OCR_API_KEY     可选，会以 Authorization: Bearer 发送
        OCR_API_TIMEOUT 请求超时秒数，默认 30
    """

    engine: str = DEFAULT_ENGINE
    lang: str = DEFAULT_LANG
    api_base: str = ""
    api_path: str = DEFAULT_API_PATH
    api_key: str = ""
    api_timeout: float = DEFAULT_TIMEOUT

    @property
    def api_url(self) -> str:
        """拼好的 serving 请求地址（容忍两侧多余斜杠）。"""
        if not self.api_base:
            return ""
        return f"{self.api_base.rstrip('/')}/{self.api_path.lstrip('/')}"

    def use_http(self) -> bool:
        """是否走远程接口。

        `OCR_ENGINE=http` 但没配 `OCR_API_BASE` 时**自动退回本地**，
        避免配置写一半就把识别全打死。
        """
        return self.engine == ENGINE_HTTP and bool(self.api_base)


def _to_float(value: str | None, fallback: float) -> float:
    """安全转 float；空值或非法值回退默认。"""
    try:
        return float(value) if value else fallback
    except ValueError:
        return fallback


def load_settings(env: Mapping[str, str] | None = None) -> OcrSettings:
    """从环境变量读取配置（可传 env 便于测试）。"""
    source = os.environ if env is None else env
    return OcrSettings(
        engine=(source.get("OCR_ENGINE") or DEFAULT_ENGINE).strip().lower(),
        lang=(source.get("OCR_LANG") or DEFAULT_LANG).strip() or DEFAULT_LANG,
        api_base=(source.get("OCR_API_BASE") or "").strip(),
        api_path=(source.get("OCR_API_PATH") or DEFAULT_API_PATH).strip() or DEFAULT_API_PATH,
        api_key=(source.get("OCR_API_KEY") or "").strip(),
        api_timeout=_to_float(source.get("OCR_API_TIMEOUT"), DEFAULT_TIMEOUT),
    )
