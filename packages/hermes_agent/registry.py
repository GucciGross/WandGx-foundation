from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonRegistry:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save({"items": []})

    def load(self) -> dict[str, Any]:
        return json.loads(self.path.read_text())

    def save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")

    def upsert(self, key: str, value: dict[str, Any]) -> None:
        data = self.load()
        items = data.setdefault("items", [])
        for idx, item in enumerate(items):
            if item.get("id") == key:
                items[idx] = value
                self.save(data)
                return
        items.append(value)
        self.save(data)
