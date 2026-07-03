from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class FirecrawlLocalClient:
    """Small client for a self-hosted Firecrawl endpoint.

    This intentionally avoids storing provider credentials in source. For hosted
    Firecrawl, add authentication in your deployment layer or wrap the official SDK.
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or os.getenv("FIRECRAWL_URL") or "http://localhost:3002").rstrip("/")

    def enabled(self) -> bool:
        return os.getenv("FIRECRAWL_ENABLED", "false").lower() in {"1", "true", "yes"}

    def search(self, query: str, limit: int = 5) -> dict[str, Any]:
        return self._post("/v2/search", {"query": query, "limit": limit, "sources": ["web"]})

    def page_read(self, url: str) -> dict[str, Any]:
        return self._post("/v2/scrape", {"url": url, "formats": ["markdown"], "onlyMainContent": True})

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "WandGxFoundation/0.1"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            return json.loads(response.read().decode("utf-8"))
