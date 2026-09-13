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
#: 低于此置信度的文本行会被列进 `Receipt.low_confidence`（**不影响解析结果**）。
#: 取值与既有 `ocr/config.py::OcrConfig.confidence_threshold` 的默认一致（0.6）——
#: 那个旋钮配了却不生效，这里是它的「活」对照物。
DEFAULT_MIN_CONFIDENCE = 0.6


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
        OCR_MIN_CONFIDENCE 低置信度上报阈值（0~1），默认 0.6
    """

    engine: str = DEFAULT_ENGINE
    lang: str = DEFAULT_LANG
    api_base: str = ""
    api_path: str = DEFAULT_API_PATH
    api_key: str = ""
    api_timeout: float = DEFAULT_TIMEOUT
    min_confidence: float = DEFAULT_MIN_CONFIDENCE

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


def _clamp01(value: float) -> float:
    """把置信度阈值夹在 0.0 ~ 1.0。"""
    return max(0.0, min(1.0, value))


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
        # 阈值被夹在 0~1：写 -1 会让**所有**行都被当成低置信度（噪声），
        # 写 2 会让这个功能彻底失效 —— 两者都是「配置写错但看起来在工作」。
        min_confidence=_clamp01(
            _to_float(source.get("OCR_MIN_CONFIDENCE"), DEFAULT_MIN_CONFIDENCE)
        ),
    )
