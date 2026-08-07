from __future__ import annotations

from agui_runtime import make_text_stream_events, sse_encode
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/agui", tags=["ag-ui"])


@router.get("/stream")
def stream(message: str = Query(..., min_length=1), thread_id: str | None = None) -> StreamingResponse:
    text = (
        "Hermes product copilot received your request. "
        "In this starter, the stream is deterministic until you attach a model and CrewAI tools. "
        f"User message: {message}"
    )
    events = make_text_stream_events(text, thread_id=thread_id)
    return StreamingResponse(sse_encode(events), media_type="text/event-stream")
