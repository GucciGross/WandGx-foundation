from __future__ import annotations

from typing import Any

CREW_ID = "research_crew"


def kickoff(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("query") or payload.get("message") or ""
    return {
        "crew_id": CREW_ID,
        "status": "needs_provider",
        "query": query,
        "summary": "Connect the local search provider before running this research crew.",
        "sources": [],
        "needs_human": False,
    }
