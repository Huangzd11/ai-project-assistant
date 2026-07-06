# Day10 — Chunk 切分（LangChain Text Splitter）
#
# 功能：parsed JSON → 按页切分 → chunks JSON
# 逻辑：
#   split_page_text  — 单页 → LangChain 切块
#   chunk_document   — 遍历 pages，分配 chunk_id
#   save_chunks_json — 写入 data/chunks/*.json
#   chunk_pdf        — 读文件 → 切分 → 写盘

import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import CHUNKS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.core.files import ensure_dir

# 步骤 A：单页文本 → LangChain 切块（不含 chunk_id）。
def split_page_text(
    page: int,
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(  # 创建切块器
        chunk_size=chunk_size,   # 切块大小
        chunk_overlap=chunk_overlap,   # 切块重叠大小
    )
    pieces = splitter.split_text(text)   # 切块

    return [{"page": page, "content": piece} for piece in pieces]   # 返回切块结果

# 步骤 B：遍历 pages，汇总块并分配全局 chunk_id。
def chunk_document(
    parsed: dict,   # 解析后的 JSON 数据
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
            chunks.append({   # 添加到 chunks 列表
                "chunk_id": chunk_id,
                "page": block["page"],
                "content": block["content"],
            })
            chunk_id += 1

    return chunks

# 步骤 C1：将 chunks 列表保存为 JSON 文件。
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

 # 步骤 C2：读 parsed JSON → 切分 → 写入 chunks JSON。
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
