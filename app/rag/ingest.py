# RAG 入库编排：PDF → parse → chunk → embed → Chroma
#
# 功能：上传后一键入库，供 POST /upload 调用
# 逻辑：串联 Day09~12 各模块，返回入库摘要

import time
from pathlib import Path

from app.core.logger import logger
from app.rag.chunker import chunk_pdf
from app.rag.embedder import embed_chunks
from app.rag.pdf_loader import parse_pdf
from app.rag.vector_store import index_chunks


# @brief: PDF 完整入库流水线
# @param: pdf_path: uploads/ 下的 PDF 路径
# @return: { source, indexed_chunks, duration_ms }
def ingest_pdf(pdf_path: str | Path) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF 不存在: {pdf_path}")

    start = time.perf_counter()
    source = pdf_path.name

    parsed = parse_pdf(pdf_path)
    chunks_path = chunk_pdf(parsed)
    embed_chunks(chunks_path)
    count = index_chunks(chunks_path)

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    logger.info(
        "Ingested %s -> %d chunks in %dms",
        source,
        count,
        elapsed_ms,
    )

    return {
        "source": source,
        "indexed_chunks": count,
        "duration_ms": elapsed_ms,
    }
