# Day05 — Docker 镜像构建（v0.2.0）
# 启动：docker build -t ai-assistant:v0.2.0 . && docker run -p 8000:8000 ai-assistant:v0.2.0
#
# 功能：将 FastAPI 服务容器化
# 逻辑：复制代码 → pip install → uvicorn 监听 0.0.0.0:8000
# 注意：需挂载 data/、uploads/，并通过 host.docker.internal 连接宿主机 Ollama

FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

# Day08 重构后入口为 app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
