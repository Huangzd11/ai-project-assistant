# Day08 — 项目重构 + PDF 上传

> 版本：**v0.2.0-alpha** | Commit：`feat(upload)`

## 学习目标

- [x] 重构为 `app/` 分层目录结构
- [x] 实现 `POST /upload` PDF 上传接口
- [x] 文件保存至 `uploads/` 并返回文件名与大小

## 项目重构

将根目录扁平结构迁移为：

```
app/
├── api/       # HTTP 路由
├── core/      # 配置、LLM、日志、文件工具
├── models/    # Pydantic 模型
├── rag/       # RAG 模块（后续扩展）
└── main.py    # FastAPI 入口
```

## PDF 上传流程

```
浏览器 → 选择 PDF → POST /upload → 保存 uploads/ → 返回 JSON
```

**接口：** `POST /upload`

**请求：** `multipart/form-data`，字段 `file`

**响应示例：**

```json
{
  "filename": "linux.pdf",
  "size": "8MB"
}
```

## 核心实现

| 模块 | 说明 |
|------|------|
| `app/api/upload.py` | 接收文件、校验 PDF、写入磁盘 |
| `app/core/files.py` | 目录创建、文件大小格式化 |
| `app/models/schemas.py` | `UploadResponse` 响应模型 |

## 启动与测试

```powershell
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

1. 打开 http://127.0.0.1:8000/docs
2. 展开 `POST /upload`，选择 PDF 文件
3. 执行后检查 `uploads/` 目录与返回 JSON

## 收获

- 掌握 FastAPI 文件上传（`UploadFile` + `python-multipart`）
- 为 Sprint 2 RAG 流水线建立文档摄入入口

## 下一步

Day09 — PDF 解析（`feat(pdf-loader)`，v0.2.0-alpha2）
