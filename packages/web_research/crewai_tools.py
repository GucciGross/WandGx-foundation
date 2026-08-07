from __future__ import annotations

import json

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .searxng import SearxngSearchClient


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Web search query")
    limit: int = Field(default=5, ge=1, le=10, description="Maximum results to return")


class LocalWebSearchTool(BaseTool):
    name: str = "local_web_search"
    description: str = "Search the web through the local SearXNG service configured for WandGx Foundation."
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str, limit: int = 5) -> str:
        results = SearxngSearchClient().search(query=query, limit=limit)
        return json.dumps([result.to_dict() for result in results], indent=2)
