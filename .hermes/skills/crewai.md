# Skill: CrewAI coding in WandGx Foundation

Use this skill whenever creating, editing, or reviewing CrewAI code.

## Current baseline

- CrewAI requires Python `>=3.10` and `<3.14`.
- CrewAI recommends `uv` for project/dependency management.
- CrewAI project scaffolds commonly use `agents.yaml`, `tasks.yaml`, `crew.py`, `tools/`, and `knowledge/`.
- For maintainability, prefer YAML-backed crews using `CrewBase`, `@agent`, `@task`, and `@crew`.
- Direct code-only crews are allowed for small templates or deterministic fallbacks.

Reference docs:

```txt
https://docs.crewai.com/installation
https://docs.crewai.com/concepts/crews
https://docs.crewai.com/concepts/agents
https://docs.crewai.com/concepts/tasks
https://docs.crewai.com/concepts/tools
https://docs.crewai.com/learn/create-custom-tools
```

## WandGx crew contract

Every generated crew must include:

```txt
manifest.json
crew.py
agents.yaml
tasks.yaml
tools.py
schemas/input.schema.json
schemas/output.schema.json
evals/basic.yaml
tests/test_contract.py
```

The manifest is the source of truth. Do not let a crew access tools not listed in `manifest.json`.

## Recommended crew shape

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class ExampleCrew:
    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(config=self.agents_config["researcher"], verbose=True)

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
```

In this repo, each `crew.py` should expose:

```python
def kickoff(payload: dict) -> dict:
    ...
```

That keeps API routes, workers, evals, and generated crews using the same runtime interface.

## Tool creation pattern

Use `BaseTool` when the tool needs validation, retries, configuration, or reuse:

```python
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(..., description="Search query")

class LocalSearchTool(BaseTool):
    name: str = "local_web_search"
    description: str = "Search the web through the local SearXNG service."
    args_schema: Type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        return "search result markdown"
```

Use the `@tool` decorator only for small one-off functions.

## Generated crew coding rules

- Always include deterministic fallback behavior so local demos work without model credentials.
- Keep all model-provider setup outside generated crews; read from environment or central config.
- Always return JSON-compatible dictionaries from `kickoff`.
- Include `needs_human` in outputs whenever the crew can trigger risky actions.
- Attach SearXNG/Firecrawl tools only when the manifest includes `web.search` or `web.scrape`.
- Do not write files outside the generated crew directory unless Hermes created an approved plan.

## When to use Flows

Use CrewAI Flows for deterministic orchestration or app workflows that need routing, state, conditional branches, or human approval. Use Crews for multi-agent collaboration around a task.
