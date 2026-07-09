# Day23 — Nginx 反向代理设计

> 版本：**v0.4-alpha2** | 前置：**Day22 Docker Compose**、**Day21_1 Web 前端**  
> **定位：统一生产入口 — 用户只访问 Nginx，由 Nginx 分发静态页面与 API**

## 学习目标

- [ ] 理解 **Reverse Proxy（反向代理）**：客户端只连 Nginx，Nginx 再转发到内网服务
- [ ] 掌握 Nginx 托管 **前端静态资源**（`vite build` 产物）
- [ ] 了解 **HTTPS** 与证书在部署中的位置（本地自签 / 生产 Let's Encrypt）
- [ ] 理解 **域名访问** 与 `server_name`、DNS 的关系
- [ ] 能画出 `用户 → Nginx → FastAPI` 完整链路

---

## 今日边界（重要）

| 做 | 不做 |
|----|------|
| Nginx 反代 FastAPI（`/api` 或路径直通） | K8s Ingress |
| 托管 `frontend/dist` 静态资源 | 前端 SSR |
| SSE 流式代理配置（`proxy_buffering off`） | WAF / 限流（Day24+） |
| Compose 新增 `nginx` + `frontend` build | 云厂商 CDN 一键部署 |
| 本地 HTTP（`:80`）+ HTTPS 设计说明 | 正式域名备案与上线 |

**Day23 核心成果：** 浏览器只访问 **一个地址**（如 `http://localhost`），同时打开 Web UI 与调用 Agent API，不再分 `5173` + `8000`。

---

## 核心链路（必须理解）

```
用户浏览器
    │
    ▼
 Nginx (:80 / :443)          ← 唯一对外入口
    │
    ├─ /              → 静态文件（React build：index.html / assets）
    ├─ /agent         → proxy_pass → api:8000
    ├─ /agent/stream  → proxy_pass（SSE，关闭缓冲）
    ├─ /upload        → proxy_pass → api:8000
    ├─ /health        → proxy_pass → api:8000
    ├─ /docs          → proxy_pass → api:8000
    └─ /openapi.json  → proxy_pass → api:8000

api (FastAPI)              ← 仅 Compose 内网，不映射宿主机 8000
chroma / ollama ...        ← 仍仅内网（延续 Day22）
```

**反向代理 vs 正向代理：**

| 类型 | 谁不知道谁 | 本项目 |
|------|------------|--------|
| 正向代理 | 服务端不知道真实客户端（VPN、公司网关） | 不做 |
| **反向代理** | **客户端不知道后端有几台机器** | **Nginx → api** |

用户只认识 `http://your-domain.com`，不知道后面是 `api:8000` 还是将来多实例。

---

## 以前 vs 以后

### Day22（当前）

```
用户 → http://localhost:5173  (Vite dev + proxy)
         └─ proxy → http://127.0.0.1:8000  (api 暴露宿主机端口)

或

用户 → http://127.0.0.1:8000/docs  (直连 API)
```

问题：

- 前端、API **两个端口**，演示时要解释两遍
- 开发模式 Vite 不应作为生产部署
- `8000` 易与本机 `uvicorn` 冲突（Day22 已踩坑）
- 无 HTTPS / 域名，不像「可交付产品」

### Day23（目标）

```
用户 → http://localhost  (仅 Nginx :80)
         ├─ /           前端静态页
         └─ /agent ...  反代到 api:8000（容器内网）
```

api **不再** `ports: "8000:8000"` 映射到宿主机（或仅 `expose` 内网），统一由 Nginx 入口。

---

## 目标架构

```
                    ┌─────────────────────────────────────────┐
                    │           docker compose (app-net)       │
                    │                                          │
  Browser ──:80──►  │  nginx                                   │
                    │    ├─ static  → /usr/share/nginx/html   │
                    │    └─ proxy   → api:8000                 │
                    │              │                           │
                    │              ├──► chroma:8000            │
                    │              └──► 通义 API（外网）        │
                    │                                          │
                    │  [profile: local-llm] ollama:11434        │
                    └─────────────────────────────────────────┘
```

### 服务变更（相对 Day22）

| 服务 | Day22 | Day23 |
|------|-------|-------|
| `api` | `ports: 8000:8000` | 仅 `expose: 8000` 或内网访问，**不暴露宿主机** |
| `nginx` | 无 | **新增**，`ports: 80:80`（+ `443:443` 可选） |
| `frontend` | 宿主机 `npm run dev` | **构建阶段** `npm run build` → 挂载/复制到 nginx |
| `chroma` | 内网 | 不变 |

---

## 路由设计

### 方案 A：API 路径直通（推荐，改动小）

Nginx 按 **与现有一致的路径** 转发，前端 `API_BASE=""` 继续请求同源：

| 路径 | Nginx 动作 | 后端 |
|------|------------|------|
| `/` | `try_files` → `index.html` | 静态 |
| `/assets/*` | 静态文件 | `dist/assets/` |
| `/agent` | `proxy_pass http://api:8000` | FastAPI |
| `/agent/stream` | 反代 + SSE 配置 | FastAPI |
| `/upload` | 反代 | FastAPI |
| `/health` | 反代 | FastAPI |
| `/docs` | 反代 | FastAPI |
| `/openapi.json` | 反代 | FastAPI |
| `/chat` `/rag` | 反代（按需） | FastAPI |

**优点：** `frontend/src/api.js` 几乎不用改（`VITE_API_BASE` 为空即同源）。

### 方案 B：API 统一前缀 `/api`（可选，更「REST 网关」风格）

| 路径 | 动作 |
|------|------|
| `/api/agent` | → `api:8000/agent` |
| `/` | 静态 |

需改 FastAPI `root_path` 或 Nginx `rewrite`，**Day23 默认不采用**，降低改动面。

---

## Nginx 配置草案

文件：`nginx/nginx.conf` 或 `nginx/default.conf`

```nginx
upstream api_backend {
    server api:8000;
}

server {
    listen 80;
    server_name localhost;   # 生产改为 assistant.example.com

    root /usr/share/nginx/html;
    index index.html;

    # 前端 SPA：除 API 外回落到 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 健康检查 / API
    location ~ ^/(health|docs|openapi\.json|upload|chat|rag|agent) {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 上传 PDF 需较大 body
        client_max_body_size 50m;

        # SSE：/agent/stream
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
    }
}
```

**SSE 注意：** `proxy_buffering off` 否则流式输出会被 Nginx 攒包，前端看不到逐字效果。

---

## 静态资源（前端生产构建）

```powershell
cd frontend
npm run build    # 产出 frontend/dist/
```

**挂载方式（二选一）：**

| 方式 | 说明 |
|------|------|
| A. 多阶段 Dockerfile | `node build` → `COPY dist` 到 `nginx` 镜像（推荐） |
| B. Compose volume | `./frontend/dist:/usr/share/nginx/html:ro` |

生产推荐 **A**：镜像自包含，不依赖宿主机先手动 build。

---

## HTTPS 设计

### 本地演示（可选）

- 自签证书：`openssl` 生成 `cert.pem` / `key.pem`
- Nginx `listen 443 ssl`，挂载 `./nginx/certs`
- 浏览器会提示「不安全」— 演示可接受

### 生产（设计级，Day23 可只写文档）

```
用户 → https://assistant.example.com
         │
         ▼
      Nginx (:443, Let's Encrypt 证书)
         │
         └─ proxy → api:8000
```

| 项 | 说明 |
|----|------|
| 证书 | Certbot + Let's Encrypt，或云 LB 终结 TLS |
| 强制 HTTPS | `80` → `301` 跳转 `https` |
| `X-Forwarded-Proto` | 已在上游配置，FastAPI 可知原始协议 |

**Day23 实现优先级：** 先 **HTTP :80** 跑通；HTTPS 作为可选 profile `https` 或文档附录。

---

## 域名访问

1. **DNS**：`A` 记录 `assistant.example.com` → 服务器公网 IP  
2. **Nginx**：`server_name assistant.example.com;`  
3. **防火墙**：放行 `80` / `443`  
4. **本地 hosts 测试**（无域名时）：

   ```
   127.0.0.1  assistant.local
   ```

   访问 `http://assistant.local`，`server_name` 匹配该域名。

---

## Docker Compose 变更预览

```yaml
services:
  frontend-build:
    # 多阶段构建产物，或 profile 仅 build 时用
    ...

  nginx:
    build:
      context: .
      dockerfile: nginx/Dockerfile   # FROM nginx:alpine + dist + conf
    ports:
      - "80:80"
      # - "443:443"
    depends_on:
      api:
        condition: service_healthy
    networks:
      - app-net

  api:
    # 移除 ports: "8000:8000"，仅内网
    expose:
      - "8000"
    ...
```

**开发模式保留：** 开发者仍可用 `npm run dev` + `docker compose up api chroma` 直连调试；**生产演示**走 `docker compose --profile production up` 含 nginx。

---

## 与 FastAPI 的协作

| 项 | 是否需要改 |
|----|------------|
| CORS | 同源后 **可简化**；Nginx 统一域名时浏览器不再跨域 |
| `root_path` | 方案 A 不需要 |
| `TrustedHostMiddleware` | 生产可加 `assistant.example.com` |
| Swagger `/docs` | 经 Nginx 反代后应能直接打开 |

---

## 实现日文件清单（预览）

| 文件 | 职责 |
|------|------|
| `nginx/default.conf` | 反代 + 静态 + SSE |
| `nginx/Dockerfile` | nginx + frontend dist |
| `docker-compose.yml` | 新增 `nginx`，api 改内网 |
| `frontend/vite.config.js` | 生产 `base: '/'` 确认 |
| `docs/Day23.md` | 设计 + 使用指南（本文） |
| `README.md` | 增加「生产入口 http://localhost」 |

---

## 验收标准

- [ ] `docker compose up` 后仅访问 `http://localhost` 可打开 Web UI
- [ ] 同域下 `POST /agent/stream` SSE 流式正常
- [ ] `http://localhost/docs` 打开 Swagger
- [ ] `http://localhost/health` 返回版本号
- [ ] 宿主机 **无需** 映射 `8000`（避免与 uvicorn 冲突）
- [ ] `docker compose down` / `up` 后静态页与 API 均可用
- [ ] （可选）`https://localhost` 自签证书可访问

---

## 测试命令（实现后）

```powershell
# 启动（含 nginx + api + chroma）
docker compose up -d --build

# 探活（统一入口）
Invoke-RestMethod http://localhost/health

# 浏览器
# http://localhost/          → Web UI
# http://localhost/docs      → Swagger

# 流式
curl -N -X POST http://localhost/agent/stream `
  -H "Content-Type: application/json" `
  -d '{"message":"你好"}'
```

---

## 风险与对策

| 风险 | 对策 |
|------|------|
| SSE 被 Nginx 缓冲 | `proxy_buffering off` |
| 大 PDF 上传 413 | `client_max_body_size 50m` |
| SPA 刷新 404 | `try_files ... /index.html` |
| api 仍映射 8000 导致端口冲突 | Day23 去掉宿主机端口，仅 nginx 暴露 |
| 前端写死 `127.0.0.1:8000` | 保持 `VITE_API_BASE=""` 同源 |

---

## 小结

Day23 在 Day22 Compose 之上增加 **Nginx 作为唯一对外入口**：静态资源由 Nginx 直接返回，API 请求反向代理到内网 `api:8000`。用户链路变为 **用户 → Nginx → FastAPI**，为 HTTPS、域名与后续上线（Day27~30 作品集演示）打下基础。

---

## 使用指南（实现后）

### 一键启动

```powershell
docker compose up -d --build
docker compose ps
Invoke-RestMethod http://localhost/health
```

| 地址 | 说明 |
|------|------|
| http://localhost | Web UI（React 生产构建） |
| http://localhost/docs | Swagger |
| http://localhost/health | 健康检查 |

### 服务说明

| 服务 | 宿主机端口 | 说明 |
|------|------------|------|
| `nginx` | **80** | 唯一对外入口 |
| `api` | 无（仅内网 `api:8000`） | 避免与本机 uvicorn 冲突 |
| `chroma` | 无 | 向量库内网 |

### 开发模式

| 场景 | 命令 |
|------|------|
| 生产演示 | `docker compose up` → 访问 http://localhost |
| Vite 热更新 | `docker compose -f docker-compose.yml -f docker-compose.dev-api.yml up -d api chroma` + `npm run dev` |
| 纯本地 | `uvicorn` + `npm run dev`（与 Day21 相同） |

### 文件清单

| 文件 | 职责 |
|------|------|
| `nginx/default.conf` | 反代 + 静态 + SSE |
| `nginx/Dockerfile` | 多阶段：npm build → nginx |
| `docker-compose.yml` | 新增 `nginx`，`api` 改 `expose` |
| `docker-compose.dev-api.yml` | 可选暴露 `8000` 供 Vite 代理 |

### 验收清单

- [x] `http://localhost` 打开 Web UI
- [x] `http://localhost/health` 返回版本号
- [x] `http://localhost/docs` 打开 Swagger
- [x] `POST /agent/stream` SSE 经 Nginx 流式正常
- [x] 宿主机不映射 `8000`
