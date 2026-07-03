from __future__ import annotations

from fastapi import APIRouter, Request

from a2a_adapter import build_agent_card

router = APIRouter(tags=["a2a"])


@router.get("/.well-known/agent-card.json")
def agent_card(request: Request) -> dict:
    base_url = str(request.base_url).rstrip("/")
    return build_agent_card(base_url)
