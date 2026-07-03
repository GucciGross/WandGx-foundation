from __future__ import annotations

from fastapi import APIRouter

from apps.api.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "mode": settings.hermes_mode}
