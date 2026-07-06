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
from app.core.files import ensure_dir   # 确保目录存在

# 本地模型懒加载（避免 import 时下载）
_local_model = None

def _get_local_model():
    global _local_model   # 全局变量
    if _local_model is None:   # 如果模型实例不存在，则创建
        from sentence_transformers import SentenceTransformer   # 本地模型
        _local_model = SentenceTransformer(EMBEDDING_MODEL)   # 创建模型实例
    return _local_model   # 返回模型实例

# 步骤 A：单条文本 → 向量。根据 EMBEDDING_PROVIDER 选择实现。
def embed_text(text: str) -> list[float]:
    if not text or not text.strip():
        return []

    if EMBEDDING_PROVIDER == "local":
        model = _get_local_model()
        return model.encode(text).tolist()

    if EMBEDDING_PROVIDER == "dashscope":
        client = OpenAI(
            api_key=OPENAI_API_KEY,   # 设置 API 密钥
            base_url=OPENAI_BASE_URL,   # 设置 API 基础 URL
            timeout=REQUEST_TIMEOUT   # 设置请求超时时间
        )
        resp = client.embeddings.create(
            model=EMBEDDING_MODEL,   # 设置模型
            input=text,   # 设置输入文本
            dimensions=EMBEDDING_DIMENSION,   # 设置维度
        )
        return resp.data[0].embedding
    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER}")   # 抛出错误

# 步骤 B：遍历 chunks，组装 vectors。
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


# 步骤 C：读 chunks JSON → 向量化 → 写入 vectors JSON。
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
        vectors_dir=vectors_dir
    )