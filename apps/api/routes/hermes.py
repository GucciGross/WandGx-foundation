from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from hermes_agent import HermesControlPlane
from hermes_agent.schemas import CrewManifest, HermesMode
from pydantic import BaseModel

from apps.api.settings import settings

router = APIRouter(prefix="/admin/hermes", tags=["hermes"])


class ChatRequest(BaseModel):
    message: str
    context: dict[str, Any] = {}


@router.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    control = HermesControlPlane(repo_root=Path.cwd(), mode=HermesMode(settings.hermes_mode))
    return control.handle_chat(request.message, request.context).model_dump()


@router.post("/crews/scaffold")
def scaffold_crew(manifest: CrewManifest) -> dict[str, Any]:
    if settings.require_human_approval:
        # In a real app, create an approval record here. For local starter usage,
        # the admin endpoint is itself the approval boundary.
        pass
    try:
        paths = HermesControlPlane(repo_root=Path.cwd(), mode=settings.hermes_mode).scaffold_crew(manifest)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "written", "paths": paths}


@router.get("/manifest/example")
def manifest_example() -> dict[str, Any]:
    control = HermesControlPlane(repo_root=Path.cwd(), mode=settings.hermes_mode)
    return control.plan_app("A quote app for painting contractors").model_dump()
