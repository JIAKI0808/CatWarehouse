from __future__ import annotations

import io
import logging
from typing import Any

from voice.settings import (
    DEFAULT_WHISPER_COMPUTE,
    DEFAULT_WHISPER_DEVICE,
    DEFAULT_WHISPER_MODEL,
    AsrSettings,
    load_asr_settings,
)
from voice.types import Transcript

logger = logging.getLogger(__name__)

_INSTALL_HINT = (
    "faster-whisper 未安装，无法本地识别。请先安装："
    "pip install -r CwServer/voice/requirements-voice.txt"
    "（或改用 VOICE_ASR_ENGINE=http 调远程语音接口，那条路径不需要任何依赖）"
)


class LocalWhisperEngine:
    """本地自部署语音识别：用 faster-whisper 在本机推理。

    与 `HttpAsrEngine`（调远程语音接口）互为替代，接口完全一致，
    因此 `create_recognizer()` 与整条流水线都不用改。
    只按结构满足 `voice.types.AsrEngine` 协议（鸭子类型），不继承任何基类。

    `faster_whisper` 采用**惰性导入**：未安装时本模块仍可正常 import 与实例化，
    只有真正调用 `transcribe()` 时才报错并给出安装提示。
    模型实例**首次调用时创建并缓存** —— 加载权重是秒级开销，不能每请求重建。

    Usage:
        engine = LocalWhisperEngine()          # 读环境变量
        transcript = engine.transcribe(audio_bytes, "voice.wav")
    """

    def __init__(self, settings: AsrSettings | None = None) -> None:
        self._settings = settings or load_asr_settings()
        self._model: Any | None = None

    def _ensure_model(self) -> Any:
        """惰性创建 WhisperModel（首次调用时才 import faster_whisper）。"""
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(_INSTALL_HINT) from exc
        conf = self._settings
        logger.info("Loading local whisper model: %s (%s/%s)",
                    conf.model, conf.device, conf.compute)
        self._model = WhisperModel(
            conf.model or DEFAULT_WHISPER_MODEL,
            device=conf.device or DEFAULT_WHISPER_DEVICE,
            compute_type=conf.compute or DEFAULT_WHISPER_COMPUTE,
        )
        return self._model

    def _collect(self, model: Any, audio: bytes) -> tuple[list[dict], Any]:
        """跑一次识别，把 segments 取成普通字典（避免把生成器留在返回值里）。"""
        segments, info = model.transcribe(io.BytesIO(audio), language=self._settings.lang or None,
                                          vad_filter=True)
        collected = [
            {"start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text}
            for seg in segments
        ]
        return collected, info

    def transcribe(self, audio: bytes, filename: str = "") -> Transcript:
        """把音频字节转成文本。

        `filename` 在本引擎里用不到（whisper 直接解码字节流），保留是为了与
        `HttpAsrEngine` 保持同一签名。

        Raises:
            ValueError: 音频为空，或解码/识别失败。
            RuntimeError: 未安装 faster-whisper。
        """
        if not audio:
            raise ValueError("音频内容为空")
        model = self._ensure_model()
        try:
            collected, info = self._collect(model, audio)
        except Exception as exc:
            raise ValueError(f"音频解码或识别失败: {exc}") from exc
        return Transcript(
            text="".join(seg["text"] for seg in collected).strip(),
            language=getattr(info, "language", None) or self._settings.lang or None,
            duration=_optional_float(getattr(info, "duration", None)),
            segments=collected,
        )


def _optional_float(value: object) -> float | None:
    """能转成正浮点数才返回，其余返回 None。"""
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None
