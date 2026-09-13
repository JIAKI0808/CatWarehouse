from __future__ import annotations

from receipts.draft import (
    LEDGER_DEFAULT_TYPE,
    LEDGER_OUTBOUND_TYPE,
    ReceiptDraft,
    ReceiptItemDraft,
)
from voice.asr_http import HttpAsrEngine
from voice.asr_local import LocalWhisperEngine
from voice.llm_claude import ClaudeMessagesClient
from voice.llm_openai import OpenAiChatClient
from voice.prompt import build_system_prompt, build_user_prompt, command_from_text
from voice.settings import AsrSettings, LlmSettings, load_asr_settings, load_llm_settings
from voice.types import (
    DIRECTION_IN,
    DIRECTION_OUT,
    AsrEngine,
    LlmClient,
    LlmReplyError,
    Transcript,
    VoiceCommand,
    VoiceItem,
)

SOURCE = "voice"
_DIRECTION_TEXT = {DIRECTION_IN: "语音入库", DIRECTION_OUT: "语音出库"}


def _sum_amounts(items: list[VoiceItem]) -> float:
    """明细金额合计（忽略没有金额的行）。"""
    return round(sum(item.amount for item in items if item.amount is not None), 2)


def _describe(command: VoiceCommand) -> str:
    """账目描述：方向 + 前几个品名；没解析出品名时只留方向。"""
    prefix = _DIRECTION_TEXT.get(command.direction, "语音录入")
    names = "、".join(item.name for item in command.items[:3])
    return f"{prefix}: {names}" if names else prefix


def _draft_items(command: VoiceCommand) -> list[ReceiptItemDraft]:
    """把口述明细转成草稿明细。

    `category_hint` **不写进草稿**：`ReceiptItemDraft` 里没有这个字段，
    而且把分类名词翻成 `sub_category_id` 是端点层的职责（`voice/` 不认识数据库）。
    端点从同一个响应的 `command` 里逐项取 hint 做匹配，再回填 `sub_category_id`。
    """
    return [
        ReceiptItemDraft(name=item.name, quantity=item.quantity,
                         unit_price=item.unit_price, amount=item.amount)
        for item in command.items
    ]


class VoiceRecognizer:
    """语音录入流水线：音频 → 识别文本 → 结构化指令 → 落库草稿。

    与原 `ocr` 流水线的分层完全一致：识别与解析不认识任何数据库模型，
    映射成草稿是纯函数，写库由 `receipts/sink.py` 的出口负责。

    刻意**不注册观察者**：`ocr/` 有 observer 是因为既有 `OcrManager` 框架本来就有事件机制；
    语音这边从零起，为它造一套事件框架属于未被要求的抽象（见 plan.md §15.3）。

    Usage:
        recognizer = create_recognizer()
        command = recognizer.recognize(audio_bytes, "voice.m4a")
        draft = command_to_draft(command)
    """

    def __init__(self, asr: AsrEngine, llm: LlmClient) -> None:
        self._asr = asr
        self._llm = llm

    def _to_command(self, transcript: Transcript) -> VoiceCommand:
        """把识别文本交给大模型整理成结构化指令。"""
        reply = self._llm.complete(build_system_prompt(), build_user_prompt(transcript.text))
        try:
            command = command_from_text(reply, transcript.text)
        except ValueError as exc:
            # 转成子类：端点据此回 502（上游返回不可用），而不是回 400（客户端输入问题）
            raise LlmReplyError(str(exc)) from exc
        command.extra.update({
            "source": SOURCE,
            "asr_language": transcript.language,
            "asr_duration": transcript.duration,
        })
        return command

    def recognize(self, audio: bytes, filename: str = "") -> VoiceCommand:
        """把一段音频识别成结构化指令。

        Raises:
            ValueError: 音频为空、无法解码、没识别出内容，或大模型没有返回可解析的 JSON。
            RuntimeError: 语音引擎或大模型不可用（如未安装 faster-whisper、服务未启动）。
        """
        transcript = self._asr.transcribe(audio, filename)
        if not transcript.text.strip():
            raise ValueError("没有识别到语音内容，请确认录音是否有效")
        return self._to_command(transcript)


def command_to_draft(command: VoiceCommand) -> ReceiptDraft:
    """把语音指令映射成可编辑草稿（纯函数，不碰数据库）。

    刻意**不猜分类**：`sub_category_id` 留空由调用方决定（`voice/` 不认识数据库）。
    `create_ledger` 默认 False，与票据路径保持一致 —— 避免「随口说一句」就产生账目。
    票面总额优先作为账目默认金额，缺失时用明细金额合计。
    `direction` 一路带到草稿：由 `receipts/sink.py` 决定库存是累加还是扣减。
    """
    total = command.total if command.total is not None else _sum_amounts(command.items)
    return ReceiptDraft(
        recorder=command.merchant or "",
        direction=command.direction,
        items=_draft_items(command),
        ledger={
            "amount": total,
            "date": command.date,
            "platform": command.merchant or "",
            "type": LEDGER_OUTBOUND_TYPE if command.is_outbound() else LEDGER_DEFAULT_TYPE,
            "description": _describe(command),
            "notes": command.note or "",
        },
        meta={
            "source": SOURCE,
            "direction": command.direction,
            "merchant": command.merchant,
            "date": command.date,
            "total": command.total,
            "note": command.note,
            "raw_text": command.raw_text,
            "category_hints": [item.category_hint for item in command.items],
        },
    )


def create_recognizer(asr: AsrEngine | None = None, llm: LlmClient | None = None,
                      asr_settings: AsrSettings | None = None,
                      llm_settings: LlmSettings | None = None) -> VoiceRecognizer:
    """便捷构造识别器；不传引擎时按环境变量自动选择。

    - 语音：`VOICE_ASR_ENGINE=http` **且**配了 `VOICE_ASR_BASE` → `HttpAsrEngine`，
      否则 → `LocalWhisperEngine`（本地自部署 whisper）
    - 大模型：`VOICE_LLM_PROVIDER=claude` → `ClaudeMessagesClient`，
      否则 → `OpenAiChatClient`（OpenAI 兼容）

    四个引擎都是**惰性初始化**：未装 faster-whisper / 远程服务未起时本函数仍正常返回，
    只有真正调用 `recognize()` 才报错。配置见 `voice/settings.py`。
    """
    if asr is None:
        asr_conf = asr_settings or load_asr_settings()
        asr = HttpAsrEngine(asr_conf) if asr_conf.use_http() else LocalWhisperEngine(asr_conf)
    if llm is None:
        llm_conf = llm_settings or load_llm_settings()
        llm = ClaudeMessagesClient(llm_conf) if llm_conf.use_claude() else OpenAiChatClient(llm_conf)
    return VoiceRecognizer(asr, llm)
