#!/usr/bin/env sh
# Day22 — 在 Compose 栈中拉取 Ollama 模型
# 用法：./scripts/ollama-pull.sh [model]
# 示例：./scripts/ollama-pull.sh qwen3:4b

set -e
MODEL="${1:-qwen3:4b}"
docker compose exec ollama ollama pull "$MODEL"
echo "Model pulled: $MODEL"
