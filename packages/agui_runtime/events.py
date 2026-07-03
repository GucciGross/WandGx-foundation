from __future__ import annotations

import json
import time
import uuid
from collections.abc import Iterable
from typing import Any


def now_ms() -> int:
    return int(time.time() * 1000)


def event(type_: str, **payload: Any) -> dict[str, Any]:
    return {"type": type_, "timestamp": now_ms(), **payload}


def make_text_stream_events(text: str, thread_id: str | None = None, run_id: str | None = None) -> list[dict[str, Any]]:
    """Create AG-UI compatible event dictionaries for a text response.

    Uses the event names documented by the Python SDK while keeping this helper
    dependency-light and easy to inspect.
    """
    thread_id = thread_id or f"thread_{uuid.uuid4().hex[:10]}"
    run_id = run_id or f"run_{uuid.uuid4().hex[:10]}"
    message_id = f"msg_{uuid.uuid4().hex[:10]}"
    chunks = _chunk_text(text)
    events = [
        event("RUN_STARTED", thread_id=thread_id, run_id=run_id),
        event("TEXT_MESSAGE_START", message_id=message_id, role="assistant"),
    ]
    events.extend(event("TEXT_MESSAGE_CONTENT", message_id=message_id, delta=chunk) for chunk in chunks)
    events.extend([
        event("TEXT_MESSAGE_END", message_id=message_id),
        event("RUN_FINISHED", thread_id=thread_id, run_id=run_id, result={"message_id": message_id}),
    ])
    return events


def sse_encode(events: Iterable[dict[str, Any]]) -> Iterable[str]:
    for item in events:
        yield f"event: {item['type']}\n"
        yield "data: " + json.dumps(item, separators=(",", ":")) + "\n\n"


def _chunk_text(text: str, size: int = 28) -> list[str]:
    if not text:
        return [" "]
    return [text[i : i + size] for i in range(0, len(text), size)]
