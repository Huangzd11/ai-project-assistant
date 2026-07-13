# Day08 — PDF 上传接口（Sprint 2 · v0.2.0-alpha）
# Day14 — Swagger 描述完善
#
# 功能：浏览器选择 PDF → 上传 → 保存到 uploads/ → 自动 RAG 入库
# 逻辑：
#   1. 校验文件扩展名与 content-type 必须为 PDF
#   2. 读取上传二进制内容，写入 UPLOAD_DIR 目录
#   3. 后台线程执行 parse → chunk → embed → index
#   4. 返回文件名、大小与入库结果
#
# 接口：POST /upload（multipart/form-data，字段名 file）

import asyncio
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import UPLOAD_DIR
from app.core.files import ensure_dir, format_file_size
from app.core.logger import logger
from app.models import UploadResponse
from app.rag.ingest import ingest_pdf

router = APIRouter(prefix="/upload", tags=["upload"])


# @brief: 上传 PDF 并保存至 uploads/
# @param: file: multipart 上传文件
# @return: UploadResponse（filename、size）
@router.post(
    "",
    response_model=UploadResponse,
    summary="上传 PDF",
    description=(
        "上传 PDF 至 uploads/ 并自动执行 RAG 入库（解析 → 切分 → 向量化 → Chroma）。"
        "仅支持 .pdf 格式，非 PDF 返回 400。"
    ),
)
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

    indexed = False
    indexed_chunks = 0
    index_error: str | None = None
    try:
        result = await asyncio.to_thread(ingest_pdf, dest)
        indexed = True
        indexed_chunks = result["indexed_chunks"]
    except Exception as exc:
        index_error = str(exc)
        logger.exception("Index failed for %s", filename)

    return UploadResponse(
        filename=filename,
        size=size,
        indexed=indexed,
        indexed_chunks=indexed_chunks,
        index_error=index_error,
    )
