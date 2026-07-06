# Day11 — Embedding（文本向量化）
#
# 功能：chunks JSON → 逐块 Embedding → vectors JSON
# 逻辑：
#   embed_text         — 单条文本 → list[float]（local / dashscope）
#   embed_chunks_list  — 遍历 chunks，组装 vectors
#   save_vectors_json  — 写入 data/vectors/*.json
#   embed_chunks       — 读文件 → 向量化 → 写盘
#
# 详见 docs/Day11.md

import json
from pathlib import Path

from openai import OpenAI

from app.core.config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    EMBEDDING_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    REQUEST_TIMEOUT,
    VECTORS_DIR,
)
from app.core.files import ensure_dir

_local_model = None


# @brief: 懒加载本地 SentenceTransformer 模型
# @return: SentenceTransformer 实例
def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer(EMBEDDING_MODEL)
    return _local_model


# @brief: 单条文本 → 向量，按 EMBEDDING_PROVIDER 分支
# @param: text: 输入文本
# @return: 浮点向量列表，空文本返回 []
def embed_text(text: str) -> list[float]:
    if not text or not text.strip():
        return []

    if EMBEDDING_PROVIDER == "local":
        model = _get_local_model()
        return model.encode(text).tolist()

    if EMBEDDING_PROVIDER == "dashscope":
        client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
            timeout=REQUEST_TIMEOUT,
        )
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            dimensions=EMBEDDING_DIMENSION,
        )
        return resp.data[0].embedding

    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")


# @brief: 遍历 chunks，批量生成 vectors 列表
# @param: chunks: chunks 列表（含 chunk_id、page、content）
# @return: [{chunk, page, embedding}, ...]
def embed_chunks_list(chunks: list[dict]) -> list[dict]:
    vectors = []
    for item in chunks:
        embedding = embed_text(item["content"])
        if not embedding:
            continue
        vectors.append({
            "chunk": item["chunk_id"],
            "page": item["page"],
            "embedding": embedding,
        })
    return vectors


# @brief: 将 vectors 列表保存为 JSON 文件
# @param: source: 源 PDF 文件名
# @param: chunks_json_path: chunks JSON 路径（用于输出文件名）
# @param: vectors: vectors 列表
# @param: vectors_dir: 输出目录
# @param: provider: Embedding 提供方
# @param: model: Embedding 模型名
# @return: 输出 JSON 路径
def save_vectors_json(
    source: str,
    chunks_json_path: str | Path,
    vectors: list[dict],
    vectors_dir: str | Path = VECTORS_DIR,
    provider: str = EMBEDDING_PROVIDER,
    model: str = EMBEDDING_MODEL,
) -> Path:
    chunks_json_path = Path(chunks_json_path)
    out_dir = ensure_dir(vectors_dir)
    out_path = out_dir / f"{chunks_json_path.stem}.json"

    dimension = len(vectors[0]["embedding"]) if vectors else 0

    payload = {
        "source": source,
        "provider": provider,
        "model": model,
        "dimension": dimension,
        "total_vectors": len(vectors),
        "vectors": vectors,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return out_path


# @brief: 读 chunks JSON → 向量化 → 写入 vectors JSON
# @param: chunks_json_path: chunks JSON 路径
# @param: vectors_dir: 输出目录，默认 VECTORS_DIR
# @return: 输出 JSON 路径
def embed_chunks(
    chunks_json_path: str | Path,
    vectors_dir: str | Path = VECTORS_DIR,
) -> Path:
    chunks_json_path = Path(chunks_json_path)
    if not chunks_json_path.is_file():
        raise FileNotFoundError(f"Chunks JSON not found: {chunks_json_path}")

    with open(chunks_json_path, encoding="utf-8") as f:
        data = json.load(f)

    vectors = embed_chunks_list(data["chunks"])
    return save_vectors_json(
        source=data.get("source", chunks_json_path.stem + ".pdf"),
        chunks_json_path=chunks_json_path,
        vectors=vectors,
        vectors_dir=vectors_dir,
    )
