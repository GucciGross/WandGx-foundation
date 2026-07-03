from __future__ import annotations

import json
import os
from pathlib import Path

import typer

from .orchestrator import HermesControlPlane
from .schemas import CrewManifest, HermesMode

app = typer.Typer(help="Hermes control-plane CLI")


def _control() -> HermesControlPlane:
    mode = HermesMode(os.getenv("HERMES_MODE", "dormant"))
    return HermesControlPlane(repo_root=Path.cwd(), mode=mode)


@app.command()
def doctor() -> None:
    """Check the local starter setup."""
    root = Path.cwd()
    checks = {
        "repo_root": str(root),
        "env_file": (root / ".env").exists(),
        "docker_compose": (root / "docker-compose.yml").exists(),
        "web_app": (root / "apps" / "web").exists(),
        "api_app": (root / "apps" / "api").exists(),
        "generated_crews": (root / "crews" / "generated").exists(),
        "hermes_mode": os.getenv("HERMES_MODE", "dormant"),
    }
    typer.echo(json.dumps(checks, indent=2))


@app.command()
def plan(idea: str) -> None:
    """Generate an app manifest from a product idea."""
    manifest = _control().plan_app(idea)
    typer.echo(manifest.model_dump_json(indent=2))


crew_app = typer.Typer(help="Crew factory commands")
app.add_typer(crew_app, name="crew")


@crew_app.command("create")
def crew_create(goal: str, write: bool = typer.Option(False, help="Write files to crews/generated.")) -> None:
    """Draft or write a CrewAI crew from a goal."""
    control = _control()
    manifest = control.create_crew_blueprint(goal)
    if not write:
        typer.echo(manifest.model_dump_json(indent=2))
        typer.echo("\nRun again with --write to scaffold files.")
        return
    paths = control.scaffold_crew(manifest)
    typer.echo(json.dumps({"crew": manifest.id, "written": paths}, indent=2))


@crew_app.command("register")
def crew_register(manifest_path: Path) -> None:
    """Register an existing generated crew manifest."""
    data = json.loads(manifest_path.read_text())
    manifest = CrewManifest.model_validate(data)
    control = _control()
    control.crew_registry.upsert(manifest.id, manifest.model_dump())
    typer.echo(f"Registered {manifest.id}")


@app.command()
def observe() -> None:
    """Run a deterministic maintenance summary."""
    response = _control().handle_chat("observe feedback and logs")
    typer.echo(response.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
