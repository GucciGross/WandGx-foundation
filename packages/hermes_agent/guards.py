from __future__ import annotations

import os
from pathlib import Path

DEFAULT_ALLOWED_WRITE_PATHS = [
    "apps",
    "packages",
    "crews/generated",
    "docs",
    "examples",
    "infra",
    "tests",
]

DANGEROUS_ACTIONS = {
    "send_email",
    "send_sms",
    "charge_customer",
    "delete_data",
    "export_customer_data",
    "run_shell_command",
    "deploy_production",
    "modify_auth",
    "modify_billing",
}


def allowed_write_paths() -> list[str]:
    raw = os.getenv("HERMES_ALLOWED_WRITE_PATHS")
    if not raw:
        return DEFAULT_ALLOWED_WRITE_PATHS
    return [item.strip() for item in raw.split(",") if item.strip()]


def assert_safe_repo_path(repo_root: Path, target: Path, allowed: list[str] | None = None) -> Path:
    """Ensure a generated file is inside a configured safe path."""
    repo_root = repo_root.resolve()
    target = target.resolve()
    allowed = allowed or allowed_write_paths()

    if repo_root not in target.parents and target != repo_root:
        raise ValueError(f"Refusing to write outside repo root: {target}")

    rel = target.relative_to(repo_root)
    rel_text = rel.as_posix()
    if not any(rel_text == prefix or rel_text.startswith(prefix.rstrip("/") + "/") for prefix in allowed):
        raise ValueError(f"Refusing to write outside allowed paths: {rel_text}")
    return target


def action_requires_approval(action_name: str) -> bool:
    return action_name in DANGEROUS_ACTIONS
