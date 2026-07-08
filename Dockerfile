# Day05 — Docker 镜像构建（v0.3.0）
# 启动：docker build -t ai-assistant:v0.3.0 . && docker run -p 8000:8000 ai-assistant:v0.3.0
#
# 功能：将 FastAPI + Agent 服务容器化
# 逻辑：复制代码 → pip install → uvicorn 监听 0.0.0.0:8000
# 注意：
#   - 挂载 data/、uploads/；通过 host.docker.internal 连接宿主机 Ollama
#   - MCP 默认关闭（容器内无 Node.js）；需 MCP 时在宿主机运行或自定义镜像装 Node

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV MCP_ENABLED=false

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
