from __future__ import annotations

from typing import Any


def build_agent_card(base_url: str = "http://localhost:8000") -> dict[str, Any]:
    """Return a simple A2A-style agent card for Hermes.

    The official SDK can be layered in later; this endpoint keeps discovery
    available from day one.
    """
    return {
        "name": "Hermes Control Plane",
        "description": "Builder, supervisor, crew factory, and maintenance agent for agent-first apps.",
        "url": base_url.rstrip("/"),
        "provider": {"organization": "Hermes Agent Starter", "url": base_url.rstrip("/")},
        "version": "0.1.0",
        "capabilities": {
            "streaming": True,
            "pushNotifications": False,
            "stateTransitionHistory": True,
        },
        "skills": [
            {
                "id": "app_builder",
                "name": "App Builder",
                "description": "Turns an app idea into manifests, crews, UI/API/DB plans, and tests.",
                "tags": ["builder", "saas", "app-generation"],
                "examples": ["Build a quote app for painting contractors"],
            },
            {
                "id": "crew_factory",
                "name": "Crew Factory",
                "description": "Creates CrewAI crew blueprints and scaffolded crew modules.",
                "tags": ["crewai", "agents", "factory"],
                "examples": ["Create a lead intake crew"],
            },
            {
                "id": "guardian",
                "name": "Guardian",
                "description": "Observes feedback/logs and proposes evals plus safe patches.",
                "tags": ["self-healing", "feedback", "evals"],
                "examples": ["Summarize failed agent runs"],
            },
        ],
    }
