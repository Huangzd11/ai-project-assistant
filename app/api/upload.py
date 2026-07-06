# Day08 — PDF 上传接口（Sprint 2 · v0.2.0-alpha）
#
# 功能：浏览器选择 PDF → 上传 → 保存到 uploads/ → 返回文件名和大小
# 逻辑：
#   1. 校验文件扩展名与 content-type 必须为 PDF
#   2. 读取上传二进制内容，写入 UPLOAD_DIR 目录
#   3. 格式化文件大小（如 8MB），记录日志并返回 JSON
#
# 接口：POST /upload（multipart/form-data，字段名 file）

from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import UPLOAD_DIR
from app.core.files import ensure_dir, format_file_size
from app.core.logger import logger
from app.models import UploadResponse

router = APIRouter(prefix="/upload", tags=["upload"])


# @brief: 上传 PDF 并保存至 uploads/
# @param: file: multipart 上传文件
# @return: UploadResponse（filename、size）
@router.post("", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(..., description="PDF 文件")):
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
