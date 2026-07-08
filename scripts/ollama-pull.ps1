# Day22 — 在 Compose 栈中拉取 Ollama 模型（Windows）
# 用法：.\scripts\ollama-pull.ps1
#       .\scripts\ollama-pull.ps1 -Model qwen3:4b

param(
    [string]$Model = "qwen3:4b"
)

docker compose exec ollama ollama pull $Model
Write-Host "Model pulled: $Model"
