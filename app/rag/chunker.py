# Day10 — Chunk 切分（LangChain Text Splitter）
#
# 功能：parsed JSON → 按页切分 → chunks JSON
# 逻辑：
#   split_page_text  — 单页 → LangChain 切块
#   chunk_document   — 遍历 pages，分配 chunk_id
#   save_chunks_json — 写入 data/chunks/*.json
#   chunk_pdf        — 读文件 → 切分 → 写盘
#
# 详见 docs/Day10.md

import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNKS_DIR, CHUNK_OVERLAP, CHUNK_SIZE
from app.core.files import ensure_dir


# @brief: 单页文本 → LangChain 切块（不含 chunk_id）
# @param: page: 页码
# @param: text: 页文本内容
# @param: chunk_size: 块大小，默认 CHUNK_SIZE
# @param: chunk_overlap: 重叠大小，默认 CHUNK_OVERLAP
# @return: [{page, content}, ...]
def split_page_text(
    page: int,
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    pieces = splitter.split_text(text)
    return [{"page": page, "content": piece} for piece in pieces]


# @brief: 遍历 pages，汇总块并分配全局 chunk_id
# @param: parsed: parsed JSON 数据
# @param: chunk_size: 块大小
# @param: chunk_overlap: 重叠大小
# @return: [{chunk_id, page, content}, ...]
def chunk_document(
    parsed: dict,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    chunks: list[dict] = []
    chunk_id = 1

    for item in parsed["pages"]:
        page_num = item["page"]
        content = item["content"]
        page_chunks = split_page_text(page_num, content, chunk_size, chunk_overlap)

        for block in page_chunks:
            chunks.append({
                "chunk_id": chunk_id,
                "page": block["page"],
                "content": block["content"],
            })
            chunk_id += 1

    return chunks


# @brief: 将 chunks 列表保存为 JSON 文件
# @param: source: 源 PDF 文件名
# @param: parsed_json_path: parsed JSON 路径（用于输出文件名）
# @param: chunks: chunks 列表
# @param: chunks_dir: 输出目录
# @param: chunk_size: 块大小
# @param: chunk_overlap: 重叠大小
# @return: 输出 JSON 路径
def save_chunks_json(
    source: str,
    parsed_json_path: str | Path,
    chunks: list[dict],
    chunks_dir: str | Path = CHUNKS_DIR,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> Path:
    parsed_json_path = Path(parsed_json_path)
    out_dir = ensure_dir(chunks_dir)
    out_path = out_dir / f"{parsed_json_path.stem}.json"

    payload = {
        "source": source,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "total_chunks": len(chunks),
        "chunks": chunks,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return out_path


# @brief: 读 parsed JSON → 切分 → 写入 chunks JSON
# @param: parsed_json_path: parsed JSON 路径
# @param: chunks_dir: 输出目录，默认 CHUNKS_DIR
# @return: 输出 JSON 路径
def chunk_pdf(
    parsed_json_path: str | Path,
    chunks_dir: str | Path = CHUNKS_DIR,
) -> Path:
    parsed_json_path = Path(parsed_json_path)
    if not parsed_json_path.is_file():
        raise FileNotFoundError(f"Parsed JSON not found: {parsed_json_path}")

    with open(parsed_json_path, encoding="utf-8") as f:
        parsed = json.load(f)

    chunks = chunk_document(parsed)
    return save_chunks_json(
        source=parsed.get("source", parsed_json_path.stem + ".pdf"),
        parsed_json_path=parsed_json_path,
        chunks=chunks,
        chunks_dir=chunks_dir,
    )
