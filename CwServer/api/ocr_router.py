import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from ocr.pipeline import ReceiptRecognizer, create_recognizer
from ocr.types import UpstreamRejectedError
from receipts.draft import ApplyResult, ReceiptDraft, draft_from_receipt
from receipts.sink import InventoryReceiptSink

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ocr", tags=["ocr"])

_recognizer: ReceiptRecognizer | None = None


def _get_recognizer() -> ReceiptRecognizer:
    """懒加载单例。

    OCR 引擎初始化（尤其 PaddleOCR 的模型加载）开销在秒级，不能每请求重建。
    create_recognizer() 本身只构造对象、不加载模型，所以这里也是惰性的：
    首次真正识别时才会付出初始化成本。
    """
    global _recognizer
    if _recognizer is None:
        _recognizer = create_recognizer()
    return _recognizer


@router.post("/receipt")
async def recognize_receipt(file: UploadFile = File(...)):
    """上传票据图片，返回识别结果 + 可直接提交的落库草稿。

    **本接口只读不写**：返回的 `draft` 供前端核对/修改（改分类、勾选、改数量）后
    再 POST 到 `/receipt/apply` 落库。识别与落库因此完全解耦。

    400：文件为空、图片无法解码，或远程 OCR 服务判定图片无效（上游 4xx）。
    503：OCR 引擎不可用（例如未安装 paddleocr、服务未启动、上游 5xx）。

    异常的 `except` 顺序有讲究：子类必须排在自己的父类前面，
    否则会被父类先接走，400 / 503 就分不开了。
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="empty file")

    try:
        receipt = _get_recognizer().recognize(contents)
    except UpstreamRejectedError as exc:
        logger.warning("Upstream rejected the image: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.error("OCR engine unavailable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    logger.info(
        "Recognized receipt: doc_type=%s items=%d total=%s",
        receipt.doc_type,
        len(receipt.items),
        receipt.total,
    )
    return {
        "receipt": receipt.to_dict(),
        "draft": draft_from_receipt(receipt).model_dump(),
    }


@router.post("/receipt/apply", response_model=ApplyResult)
async def apply_receipt(draft: ReceiptDraft, db: AsyncSession = Depends(get_db)) -> ApplyResult:
    """把（客户端可编辑的）草稿写入库存与账本。

    这是**唯一的写库入口**，写入语义集中在 `receipts/sink.py` 的
    `InventoryReceiptSink`；想换落库目标只需替换该处构造，本接口与 `ocr/` 都不受影响。
    未指定/找不到分类的明细会被跳过，并在 `skipped` 里说明原因。
    """
    sink = InventoryReceiptSink(db)
    result = await sink.write(draft)
    logger.info(
        "Applied receipt draft: items=%d ledger=%s skipped=%d",
        len(result.created_items), result.created_ledger_id, len(result.skipped),
    )
    return result
