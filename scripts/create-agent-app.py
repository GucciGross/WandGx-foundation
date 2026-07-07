#!/usr/bin/env python3
"""Create a new agent-native app from WandGx Foundation.

This is intentionally local and deterministic: it copies the foundation repo,
excludes build/cache/git artifacts, writes a starter .env, and records the
WandGx/Oracle defaults needed for an agent-native app.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", ".venv", "node_modules", ".next", "dist", "build", "coverage",
    ".pytest_cache", ".ruff_cache", ".mypy_cache", "__pycache__", ".local",
}
EXCLUDED_FILES = {".DS_Store"}


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return slug or "agent-app"


def should_skip(path: Path) -> bool:
    if path.name in EXCLUDED_FILES:
        return True
    return any(part in EXCLUDED_DIRS for part in path.parts)


def copy_foundation(src: Path, dst: Path) -> None:
    if dst.exists() and any(dst.iterdir()):
        raise SystemExit(f"target exists and is not empty: {dst}")
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if should_skip(item.relative_to(src)):
            continue
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=lambda _d, names: [n for n in names if n in EXCLUDED_DIRS or n in EXCLUDED_FILES])
        else:
            shutil.copy2(item, target)


def write_app_overrides(dst: Path, app_name: str, package_name: str, oracle_base_url: str) -> None:
    env_example = dst / ".env.example"
    env = dst / ".env"
    if env_example.exists() and not env.exists():
        text = env_example.read_text()
        text = re.sub(r"^APP_NAME=.*$", f"APP_NAME={app_name}", text, flags=re.M)
        text = re.sub(r"^MODEL_PROVIDER=.*$", "MODEL_PROVIDER=wandgx", text, flags=re.M)
        text = re.sub(r"^MODEL_NAME=.*$", "MODEL_NAME=oracle-1", text, flags=re.M)
        text += f"\n# WandGx Oracle-1\nWANDGX_LLM_BASE_URL={oracle_base_url.rstrip('/')}/v1\nWANDGX_MODEL=oracle-1\n"
        env.write_text(text)
    marker = dst / "FOUNDATION.md"
    marker.write_text(f"""# {app_name}

Generated from WandGx Foundation.

## Agent-native defaults

- Public model contract: `oracle-1`
- LLM base URL: `{oracle_base_url.rstrip('/')}/v1`
- AG-UI event surface: `apps/api/routes/agui.py`
- Agent control plane: `packages/hermes_agent/`
- Human approvals remain required for dangerous actions.

## First proof commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
PYTHONPATH=packages:. pytest -q
```

Then start Docker Compose or the API/web dev servers from the README.
""")
    # Keep package names safe without doing a broad destructive rewrite.
    pyproject = dst / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text()
        text = re.sub(r'^name = "[^"]+"', f'name = "{package_name}"', text, count=1, flags=re.M)
        text = re.sub(r'^description = "[^"]+"', f'description = "{app_name} built on WandGx Foundation."', text, count=1, flags=re.M)
        pyproject.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new app from WandGx Foundation")
    parser.add_argument("name", help="Human app name, e.g. 'Painter CRM'")
    parser.add_argument("--target", "-t", help="Output directory. Defaults to ./<slug>")
    parser.add_argument("--package-name", help="Python package/project name. Defaults to slug with dashes converted to underscores")
    parser.add_argument("--oracle-base-url", default="https://llm.wandgx.com", help="WandGx Oracle base URL")
    args = parser.parse_args()

    src = Path(__file__).resolve().parents[1]
    slug = slugify(args.name)
    target = Path(args.target or slug).expanduser().resolve()
    package_name = args.package_name or slug.replace("-", "_")

    copy_foundation(src, target)
    write_app_overrides(target, args.name, package_name, args.oracle_base_url)
    print(f"created={target}")
    print(f"app_name={args.name}")
    print(f"model=oracle-1")
    print(f"next=cd {target} && PYTHONPATH=packages:. pytest -q")


if __name__ == "__main__":
    main()
