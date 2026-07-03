from fastapi import FastAPI

from app.api import chat, health, upload

app = FastAPI(title="AI Project Assistant", version="0.2.0-alpha")

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(upload.router)
