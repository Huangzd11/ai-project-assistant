# Day05 — Docker 容器化部署

## 目标

- 将 Day04 FastAPI 服务打包为 Docker 镜像
- 理解镜像构建与容器运行流程
- 处理容器访问宿主机 Ollama 的网络配置

## Dockerfile 说明

项目根目录的 `Dockerfile`：

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

| 指令 | 说明 |
|------|------|
| `FROM` | 基于 Python 3.13 精简镜像 |
| `WORKDIR` | 容器内工作目录设为 `/app` |
| `COPY` | 将项目文件复制进镜像 |
| `RUN` | 安装 Python 依赖 |
| `EXPOSE` | 声明服务监听 8000 端口 |
| `CMD` | 启动 Uvicorn，绑定 `0.0.0.0` 以接受外部请求 |

## 构建与运行

```powershell
docker build -t ai-chat:v1 .
docker run -p 8000:8000 ai-chat:v1
```

访问 http://127.0.0.1:8000/docs 验证服务是否正常。

## 连接宿主机 Ollama

容器内无法直接访问 `127.0.0.1:11434`（指向容器自身）。需通过环境变量指向宿主机：

```powershell
docker run -p 8000:8000 `
  -e OPENAI_BASE_URL=http://host.docker.internal:11434/v1 `
  ai-chat:v1
```

| 变量 | 值 | 说明 |
|------|-----|------|
| `OPENAI_BASE_URL` | `http://host.docker.internal:11434/v1` | Windows / macOS 访问宿主机 |
| `OPENAI_API_KEY` | `ollama` | Ollama 不校验密钥 |
| `MODEL_NAME` | `qwen3:4b` | 与本地已拉取模型一致 |

> Linux 环境下 `host.docker.internal` 可能不可用，可改用 `--add-host=host.docker.internal:host-gateway` 或宿主机实际 IP。

## 前置知识

- Day04 已完成 FastAPI HTTP 服务，本日在此基础上做容器化
- 接口说明见 [api.md](api.md)
