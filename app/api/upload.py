from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import UPLOAD_DIR
from app.core.files import ensure_dir, format_file_size
from app.core.logger import logger
from app.models import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(..., description="PDF 文件")):
    """上传 PDF 文件，保存至 uploads/ 目录。"""
    filename = Path(file.filename or "").name
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    content_type = file.content_type or ""
    if content_type and content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    upload_dir = ensure_dir(UPLOAD_DIR)
    dest = upload_dir / filename

    data = await file.read()
    dest.write_bytes(data)

    size = format_file_size(len(data))
    logger.info("Uploaded %s (%s) -> %s", filename, size, dest)

    return UploadResponse(filename=filename, size=size)
