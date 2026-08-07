from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from hermes_agent.runtime import run_python_crew
from hermes_agent.schemas import FeedbackRecord
from pydantic import BaseModel

from apps.api.db import store_feedback

router = APIRouter(tags=["agents"])


class AgentChatRequest(BaseModel):
    message: str
    thread_id: str | None = None
    context: dict[str, Any] = {}


@router.post("/agents/product/chat")
def product_chat(request: AgentChatRequest) -> dict[str, Any]:
    run_id = f"run_{uuid.uuid4().hex[:10]}"
    entrypoint = Path.cwd() / "crews" / "templates" / "support_crew" / "crew.py"
    result = run_python_crew(entrypoint, {"message": request.message, "context": request.context, "run_id": run_id})
    return {"run_id": run_id, "thread_id": request.thread_id, "result": result}


@router.post("/feedback")
def feedback(record: FeedbackRecord) -> dict[str, str]:
    store_feedback(record.model_dump())
    return {"status": "received"}
