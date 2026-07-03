from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    provider: str = "searxng"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SearxngSearchClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("SEARXNG_URL") or "http://localhost:8888").rstrip("/")

    def search(self, query: str, limit: int = 5, language: str = "en") -> list[SearchResult]:
        params = urllib.parse.urlencode({"q": query, "format": "json", "language": language})
        request = urllib.request.Request(
            f"{self.base_url}/search?{params}",
            headers={"User-Agent": "WandGxFoundation/0.1"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
        results: list[SearchResult] = []
        for item in data.get("results", [])[:limit]:
            url = item.get("url") or ""
            if not url:
                continue
            results.append(
                SearchResult(
                    title=item.get("title") or url,
                    url=url,
                    snippet=item.get("content") or item.get("snippet") or "",
                )
            )
        return results
