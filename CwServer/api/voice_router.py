import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.sub_category import SubCategory
from receipts.draft import ApplyResult, ReceiptDraft
from receipts.sink import InventoryReceiptSink
from voice.pipeline import VoiceRecognizer, command_to_draft, create_recognizer
from voice.types import LlmReplyError, UpstreamRejectedError, VoiceCommand

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])

_recognizer: VoiceRecognizer | None = None


def _get_recognizer() -> VoiceRecognizer:
    """懒加载单例。

    本地 whisper 的模型加载与首次下载都是秒级以上的开销，不能每请求重建；
    `create_recognizer()` 本身只构造对象、不加载模型，所以这里也是惰性的。
    与 `api/ocr_router.py` 同样的取舍。引擎由 `voice/settings.py` 的环境变量决定。
    """
    global _recognizer
    if _recognizer is None:
        _recognizer = create_recognizer()
    return _recognizer


def _matches(probe: str, subs: list[SubCategory], exact: bool) -> list[SubCategory]:
    """按精确或子串方式找出名称匹配的子分类。"""
    if exact:
        return [sub for sub in subs if sub.name == probe]
    return [sub for sub in subs if probe in sub.name or sub.name in probe]


def _resolve(hint: str | None, name: str, subs: list[SubCategory]) -> tuple[SubCategory | None, str]:
    """定位落库分类：先精确（分类名词 → 品名）再子串，**只认唯一命中**。

    命中多个时返回 `None` —— 分不清就留空让用户在草稿里自己选，不替他赌
    （与票据路径「识别层不猜分类」是同一条原则，这里只是多给一个建议）。
    第二个返回值是原因，会如实写进响应，便于前端解释为什么没预填。
    """
    probes = [probe for probe in (hint, name) if probe]
    for exact in (True, False):
        for probe in probes:
            hits = _matches(probe, subs, exact)
            if len(hits) == 1:
                return hits[0], f"{'exact' if exact else 'partial'}:{probe}"
            if hits:
                return None, f"ambiguous:{probe}"
    return None, "not_found"


async def suggest_categories(db: AsyncSession, command: VoiceCommand,
                             draft: ReceiptDraft) -> None:
    """按口述里的分类线索给草稿预填 `sub_category_id`。

    这是**端点层的职责**：`voice/` 完全不认识数据库，只输出口语里说到的分类名词
    （`category_hint`）。这里把名词拿去和 `SubCategory.name` 匹配，命中就填上。
    结果逐项记进 `draft.meta["category_match"]`，与 `draft.items` **按下标对齐**。
    """
    subs = list((await db.execute(select(SubCategory))).scalars().all())
    report: list[dict] = []
    for item, drafted in zip(command.items, draft.items):
        found, reason = _resolve(item.category_hint, item.name, subs)
        if found is not None:
            drafted.sub_category_id = found.id
        report.append({
            "name": item.name,
            "hint": item.category_hint,
            "matched_id": found.id if found else None,
            "matched_name": found.name if found else None,
            "reason": reason,
        })
    draft.meta["category_match"] = report


@router.post("/record")
async def recognize_voice(file: UploadFile = File(...),
                          db: AsyncSession = Depends(get_db)):
    """上传语音，返回结构化指令 + 可直接提交的落库草稿。

    **本接口只读不写**：返回的 `draft` 供前端核对/修改（选分类、勾选、改数量）后
    再 POST 到 `/record/apply` 落库，识别与落库因此完全解耦。

    响应里的 `command` 同时携带识别原文（`raw_text`）与语音信息
    （`extra.asr_language` / `extra.asr_duration`），故不再单独返回一份 transcript。

    400：文件为空、音频无法解码、没识别出内容，或语音/大模型服务判定素材无效（上游 4xx）。
    502：大模型返回无法解析成结构化指令（上游返回不可用）。
    503：语音引擎或大模型不可用（如未装 faster-whisper、服务未启动、上游 5xx）。

    异常的 `except` 顺序有讲究：两个子类必须排在自己的父类前面，
    否则会被父类先接走，状态码就分不开了。
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="empty file")

    try:
        command = _get_recognizer().recognize(contents, file.filename or "")
    except LlmReplyError as exc:
        logger.error("LLM reply unusable: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UpstreamRejectedError as exc:
        logger.warning("Upstream rejected the material: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("Voice engine unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    draft = command_to_draft(command)
    await suggest_categories(db, command, draft)
    logger.info(
        "Recognized voice command: direction=%s items=%d total=%s matched=%d",
        command.direction, len(command.items), command.total,
        sum(1 for row in draft.meta["category_match"] if row["matched_id"]),
    )
    return {"command": command.to_dict(), "draft": draft.model_dump()}


@router.post("/record/apply", response_model=ApplyResult)
async def apply_voice(draft: ReceiptDraft, db: AsyncSession = Depends(get_db)) -> ApplyResult:
    """把（客户端可编辑的）草稿写入库存与账本。

    与 `/api/ocr/receipt/apply` 共用同一个落库出口 `InventoryReceiptSink`；
    草稿的 `direction` 决定库存是**累加**（`in`）还是**扣减**（`out`）、
    账目默认是支出还是收入。未指定/找不到分类的明细会被跳过并在 `skipped` 里说明原因。
    """
    sink = InventoryReceiptSink(db)
    result = await sink.write(draft)
    logger.info(
        "Applied voice draft: direction=%s items=%d ledger=%s skipped=%d",
        draft.direction, len(result.created_items), result.created_ledger_id, len(result.skipped),
    )
    return result
