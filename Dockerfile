# Day05 — Docker 镜像构建（v0.4.0-alpha）
# 单容器：docker build -t ai-assistant . && docker run -p 8000:8000 ...
# Compose：docker compose up -d --build
#
# 功能：将 FastAPI + Agent 服务容器化
# 逻辑：复制代码 → pip install → uvicorn 监听 0.0.0.0:8000
# 注意：
#   - 默认 compose up：api + chroma，LLM 读 .env（通义等）
#   - --profile local-llm：额外启动 ollama，entrypoint 自动切换本地模型
#   - MCP 默认关闭（容器内无 Node.js）

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' scripts/docker-entrypoint.sh && chmod +x scripts/docker-entrypoint.sh

EXPOSE 8000

ENV MCP_ENABLED=false

ENTRYPOINT ["sh", "/app/scripts/docker-entrypoint.sh"]
