from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routes import a2a, agents, agui, health, hermes
from .settings import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(hermes.router)
app.include_router(agents.router)
app.include_router(agui.router)
app.include_router(a2a.router)


@app.on_event("startup")
def startup() -> None:
    init_db()


if __name__ == "__main__":
    uvicorn.run("apps.api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
