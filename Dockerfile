# Day05 — Docker 镜像构建
# 启动：docker build -t ai-chat:v1 . && docker run -p 8000:8000 ai-chat:v1
#
# 功能：将 FastAPI 服务容器化
# 逻辑：复制代码 → pip install → uvicorn 监听 0.0.0.0:8000

FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

# Day08 重构后入口为 app.main:app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
