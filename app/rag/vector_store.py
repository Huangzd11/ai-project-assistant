# Day12 — Chroma 向量库（Insert + Search，不接 LLM）
#
# 功能：chunks + vectors → Chroma 入库；Question → Search → Top-K
# 逻辑：
#   build_records      — 合并 chunks JSON + vectors JSON
#   insert_documents   — 写入 Chroma Collection
#   search             — embed_text → query → Top-K（无 LLM）
#   index_chunks       — 入库门面
#
# 详见 docs/Day12.md

import json
from pathlib import Path

import chromadb

from app.core.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DIR,
    CHROMA_HOST,
    CHROMA_MODE,
    CHROMA_PORT,
    SEARCH_TOP_K,
    VECTORS_DIR,
)
from app.core.files import ensure_dir
from app.core.logger import logger
from app.rag.embedder import embed_text


# @brief: 获取 Chroma 客户端（embedded 本地 / server Compose）
# @return: PersistentClient 或 HttpClient 实例
def get_chroma_client():
    if CHROMA_MODE == "server":
        logger.info("chroma client  mode=server  host=%s  port=%s", CHROMA_HOST, CHROMA_PORT)
        return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    ensure_dir(CHROMA_DIR)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


# @brief: 获取或创建 Chroma Collection（cosine 相似度）
# @return: Collection 实例
def get_or_create_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


# @brief: 合并 chunks JSON 与 vectors JSON 为 Chroma 入库记录
# @param: chunks_data: chunks JSON 数据（含 chunk_id、content、page）
# @param: vectors_data: vectors JSON 数据（含 chunk、embedding）
# @return: ids / embeddings / documents / metadatas / source / count
def build_records(chunks_data: dict, vectors_data: dict) -> dict:
    source = chunks_data.get("source", "unknown.pdf")
    stem = Path(source).stem

    content_map = {item["chunk_id"]: item for item in chunks_data["chunks"]}

    ids, embeddings, documents, metadatas = [], [], [], []

    for vector in vectors_data["vectors"]:
        chunk_id = vector["chunk"]
        chunk = content_map.get(chunk_id)
        if chunk is None:
            continue

        ids.append(f"{stem}_chunk_{chunk_id}")
        embeddings.append(vector["embedding"])
        documents.append(chunk["content"])
        metadatas.append({
            "source": source,
            "chunk": chunk_id,
            "page": chunk["page"],
        })

    return {
        "ids": ids,
        "embeddings": embeddings,
        "documents": documents,
        "metadatas": metadatas,
        "source": source,
        "count": len(ids),
    }


# @brief: 将 chunks + vectors 写入 Chroma（同 source 先删后插）
# @param: chunks_json_path: chunks JSON 路径
# @param: vectors_json_path: vectors JSON 路径
# @return: 入库条数
def insert_documents(chunks_json_path: str | Path, vectors_json_path: str | Path) -> int:
    chunks_json_path = Path(chunks_json_path)
    vectors_json_path = Path(vectors_json_path)

    with open(chunks_json_path, encoding="utf-8") as f:
        chunks_data = json.load(f)
    with open(vectors_json_path, encoding="utf-8") as f:
        vectors_data = json.load(f)

    records = build_records(chunks_data, vectors_data)
    if records["count"] == 0:
        return 0

    collection = get_or_create_collection()
    collection.delete(where={"source": records["source"]})
    collection.add(
        ids=records["ids"],
        embeddings=records["embeddings"],
        documents=records["documents"],
        metadatas=records["metadatas"],
    )
    return records["count"]


# @brief: 问题向量化后检索 Top-K（无 LLM）
# @param: question: 用户问题
# @param: top_k: 返回条数，默认 SEARCH_TOP_K
# @return: { query, top_k, results[] }
def search(question: str, top_k: int = SEARCH_TOP_K) -> dict:
    query_vector = embed_text(question)
    if not query_vector:
        return {"query": question, "top_k": top_k, "results": []}

    collection = get_or_create_collection()
    raw = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    for rank, (doc, meta, dist) in enumerate(
        zip(raw["documents"][0], raw["metadatas"][0], raw["distances"][0]),
        start=1,
    ):
        results.append({
            "rank": rank,
            "score": round(1 - dist, 4),
            "chunk": meta["chunk"],
            "page": meta["page"],
            "source": meta["source"],
            "content": doc,
        })

    return {"query": question, "top_k": top_k, "results": results}


# @brief: 入库门面
# @param: chunks_json_path: chunks JSON 路径
# @param: vectors_json_path: vectors JSON 路径，默认 data/vectors/{同名}.json
# @return: 入库条数
def index_chunks(
    chunks_json_path: str | Path,
    vectors_json_path: str | Path | None = None,
) -> int:
    chunks_json_path = Path(chunks_json_path)
    if not chunks_json_path.is_file():
        raise FileNotFoundError(f"Chunks JSON not found: {chunks_json_path}")

    if vectors_json_path is None:
        vectors_json_path = Path(VECTORS_DIR) / f"{chunks_json_path.stem}.json"
    else:
        vectors_json_path = Path(vectors_json_path)

    if not vectors_json_path.is_file():
        raise FileNotFoundError(f"Vectors JSON not found: {vectors_json_path}")

    return insert_documents(chunks_json_path, vectors_json_path)
