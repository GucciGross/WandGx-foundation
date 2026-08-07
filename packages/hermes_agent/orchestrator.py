from __future__ import annotations

from pathlib import Path
from typing import Any

from .crew_factory import CrewFactory, slugify
from .registry import JsonRegistry
from .schemas import (
    AppManifest,
    CrewManifest,
    EntityManifest,
    HermesAction,
    HermesMode,
    HermesResponse,
)
from .self_healing import FeedbackTriage


class HermesControlPlane:
    """The builder/supervisor brain for the starter.

    This first implementation is deterministic on purpose. Wire model calls behind this
    interface later, but keep manifests and guardrails as the contract.
    """

    def __init__(self, repo_root: Path | None = None, mode: HermesMode | str = HermesMode.dormant):
        self.repo_root = repo_root or Path.cwd()
        self.mode = HermesMode(mode)
        self.crew_factory = CrewFactory(self.repo_root)
        self.crew_registry = JsonRegistry(self.repo_root / "crews" / "registry" / "crews.json")

    def handle_chat(self, message: str, context: dict[str, Any] | None = None) -> HermesResponse:
        context = context or {}
        normalized = message.lower()

        if "crew" in normalized and any(word in normalized for word in ["create", "make", "generate"]):
            manifest = self.create_crew_blueprint(message)
            return HermesResponse(
                mode=self.mode,
                message=(
                    f"I drafted a CrewAI crew blueprint for `{manifest.id}`. "
                    "Approve scaffolding to write it under `crews/generated`."
                ),
                actions=[
                    HermesAction(
                        type="scaffold_crew",
                        title=f"Scaffold {manifest.name}",
                        description="Writes crew.py, agents.yaml, tasks.yaml, schemas, tests, and evals.",
                        payload=manifest.model_dump(),
                        requires_approval=True,
                    )
                ],
                artifacts={"crew_manifest": manifest.model_dump()},
            )

        if any(word in normalized for word in ["app", "saas", "dashboard", "crm", "quote"]):
            manifest = self.plan_app(message)
            return HermesResponse(
                mode=self.mode,
                message=(
                    f"I drafted `{manifest.app_name}` as an agent-first app. "
                    "Next I would generate DB tables, API routes, UI pages, and runtime crews."
                ),
                actions=[
                    HermesAction(
                        type="generate_app_modules",
                        title="Generate app modules",
                        description="Create DB/API/UI/CrewAI module plan from the app manifest.",
                        payload=manifest.model_dump(),
                        requires_approval=True,
                    )
                ],
                artifacts={"app_manifest": manifest.model_dump()},
            )

        if any(word in normalized for word in ["heal", "fix", "observe", "logs", "feedback"]):
            triage = FeedbackTriage().summarize([])
            return HermesResponse(
                mode=self.mode,
                message="I am in observation mode. Feed me failed runs or user feedback and I will propose evals and patches.",
                actions=[
                    HermesAction(
                        type="maintenance_report",
                        title="Create maintenance report",
                        description="Summarize logs, feedback, and failed runs into improvement candidates.",
                        payload={"findings": [f.model_dump() for f in triage]},
                    )
                ],
            )

        return HermesResponse(
            mode=self.mode,
            message=(
                "Tell me what app you want to build, or ask me to create a crew. "
                "Example: `Build a quote app for painting contractors` or "
                "`Create a lead intake crew`."
            ),
        )

    def plan_app(self, idea: str, app_name: str | None = None) -> AppManifest:
        slug = slugify(app_name or idea)[:48]
        title = app_name or self._title_from_idea(idea)
        entities = self._entities_from_idea(idea)
        crews = self._crews_from_idea(idea)
        return AppManifest(
            app_name=title,
            slug=slug,
            description=idea.strip(),
            users=["admin", "operator", "customer"],
            entities=entities,
            crews=crews,
            interfaces=["web_dashboard", "admin_hermes", "product_copilot", "api"],
        )

    def create_crew_blueprint(self, goal: str) -> CrewManifest:
        return self.crew_factory.blueprint_from_goal(goal)

    def scaffold_crew(self, manifest: CrewManifest) -> list[str]:
        paths = self.crew_factory.scaffold(manifest)
        self.crew_registry.upsert(manifest.id, manifest.model_dump())
        return [str(path.relative_to(self.repo_root)) for path in paths]

    def _title_from_idea(self, idea: str) -> str:
        idea = idea.strip().strip(".")
        if "painting" in idea.lower() or "quote" in idea.lower():
            return "PainterQuote Pro"
        if len(idea) <= 42:
            return idea.title()
        return "Hermes Generated App"

    def _entities_from_idea(self, idea: str) -> list[EntityManifest]:
        base = [
            EntityManifest(name="User", description="Authenticated app user", fields={"email": "string", "role": "string"}),
            EntityManifest(name="AgentRun", description="Logged agent execution", fields={"agent_id": "string", "status": "string", "payload": "json"}),
            EntityManifest(name="Feedback", description="User feedback on agent output", fields={"rating": "string", "comment": "text", "snapshot": "json"}),
        ]
        lower = idea.lower()
        if "quote" in lower or "painting" in lower:
            base.extend([
                EntityManifest(name="Lead", description="Potential customer request", fields={"name": "string", "status": "string", "source": "string"}),
                EntityManifest(name="Property", description="Job site/property details", fields={"address": "string", "notes": "text"}),
                EntityManifest(name="Estimate", description="Quote/estimate generated by agents", fields={"total": "decimal", "status": "string"}),
            ])
        else:
            base.extend([
                EntityManifest(name="Project", description="Workspace for generated app data", fields={"name": "string", "status": "string"}),
                EntityManifest(name="Task", description="Work item handled by agents", fields={"title": "string", "status": "string"}),
            ])
        return base

    def _crews_from_idea(self, idea: str) -> list[CrewManifest]:
        lower = idea.lower()
        goals = ["support crew", "feedback triage crew"]
        if "quote" in lower or "painting" in lower:
            goals = ["lead intake crew", "quote builder crew", "follow up crew", *goals]
        return [self.create_crew_blueprint(goal) for goal in goals]
