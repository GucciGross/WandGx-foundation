from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def run_python_crew(entrypoint: Path, payload: dict[str, Any]) -> dict[str, Any]:
    if not entrypoint.exists():
        raise FileNotFoundError(f"Crew entrypoint not found: {entrypoint}")
    spec = importlib.util.spec_from_file_location(f"crew_{entrypoint.stem}", entrypoint)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load crew module: {entrypoint}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "kickoff"):
        raise AttributeError(f"Crew module has no kickoff(payload) function: {entrypoint}")
    result = module.kickoff(payload)
    if isinstance(result, dict):
        return result
    return {"status": "completed", "summary": str(result), "needs_human": False}
