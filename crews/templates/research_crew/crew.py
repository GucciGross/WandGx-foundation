from __future__ import annotations

from typing import Any

from web_research.searxng import SearxngSearchClient

CREW_ID = "research_crew"


def kickoff(payload: dict[str, Any]) -> dict[str, Any]:
    query = payload.get("query") or payload.get("message") or "agent app foundation"
    limit = int(payload.get("limit", 5))
    results = SearxngSearchClient().search(query, limit=limit)
    return {
        "crew_id": CREW_ID,
        "status": "completed",
        "query": query,
        "summary": "Collected search results through the local WandGx research provider.",
        "sources": [result.to_dict() for result in results],
        "needs_human": False,
    }
