# Day09+ — RAG 模块
# Day09 — pdf_loader.py：PDF 按页解析为 JSON
# Day10 — chunker.py：按页切分为 Chunk JSON
# Day11 — embedder.py：Chunk 向量化 → Vector JSON
# Day12 — vector_store.py：Chroma 入库 + Top-K 检索
# Day13 — rag_pipeline.py：RAG 问答流水线
#
# 子模块按需导入，避免包初始化时拉起 chromadb 等重依赖。
# 示例：from app.rag.pdf_loader import parse_pdf
