import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 三个 parent：本文件 → api/intake → api → CwServer。
    # ⚠️ 2026-09-14 的接口分区重构把本文件从 `api/` 移到了 `api/intake/`，
    # 而这里当时仍是 `parent.parent`（只到 `api/`），上传目录会从
    # `CwServer/uploads` 悄悄漂到 `CwServer/api/uploads` —— 已修正为 `parents[2]`。
    # 这类 bug 是「纯 rename」推不出来的：文件内容没变，但 `__file__` 变了。
    upload_dir = Path(__file__).parents[2] / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = upload_dir / file_name

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return {"path": str(file_path), "filename": file_name}
