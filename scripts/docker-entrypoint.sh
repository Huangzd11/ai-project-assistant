#!/bin/sh
# Day22 — 容器启动：若 Ollama 服务在 Compose 网络内可达则优先本地 LLM，否则沿用 .env（通义等）
set -e

if getent hosts ollama >/dev/null 2>&1; then
  i=0
  while [ "$i" -lt 30 ]; do
    if python -c "import urllib.request; urllib.request.urlopen('http://ollama:11434/', timeout=3)" 2>/dev/null; then
      export OPENAI_BASE_URL=http://ollama:11434/v1
      export OPENAI_API_KEY=ollama
      export MODEL_NAME="${MODEL_NAME:-qwen3:4b}"
      export PROVIDER=ollama
      echo "[entrypoint] LLM: Ollama (local-llm profile)"
      break
    fi
    i=$((i + 1))
    sleep 2
  done
fi

if [ "$OPENAI_BASE_URL" = "http://ollama:11434/v1" ]; then
  :
else
  echo "[entrypoint] LLM: ${OPENAI_BASE_URL:-（未设置）} model=${MODEL_NAME:-（未设置）}"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
