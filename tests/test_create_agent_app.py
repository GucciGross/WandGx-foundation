from __future__ import annotations

import importlib.util
from pathlib import Path


def load_script():
    path = Path(__file__).resolve().parents[1] / "scripts" / "create-agent-app.py"
    spec = importlib.util.spec_from_file_location("create_agent_app", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_slugify():
    mod = load_script()
    assert mod.slugify("My Agent App!") == "my-agent-app"


def test_copy_foundation_writes_oracle_defaults(tmp_path):
    mod = load_script()
    src = Path(__file__).resolve().parents[1]
    target = tmp_path / "demo"
    mod.copy_foundation(src, target)
    mod.write_app_overrides(target, "Demo Agent", "demo_agent", "https://llm.wandgx.com")
    assert (target / "FOUNDATION.md").exists()
    assert "oracle-1" in (target / "FOUNDATION.md").read_text()
    assert "APP_NAME=Demo Agent" in (target / ".env").read_text()
    assert 'name = "demo_agent"' in (target / "pyproject.toml").read_text()
    assert not (target / ".git").exists()
