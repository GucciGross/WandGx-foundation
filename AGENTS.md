# Agent Operating Guide: WandGx Foundation

This repo is **WandGx Foundation**, the reusable base for agent-first apps. Treat it as infrastructure for many products, not as a single throwaway demo.

## Mission

Build and maintain a cloneable foundation where Hermes can plan and scaffold apps, CrewAI crews can perform domain work, the frontend can expose agent UX, and local research tools are ready from day one.

```txt
Hermes = control plane, app builder, crew factory, guardian
CrewAI = runtime workforce for product workflows
AG-UI = user/app frontend to agent backend event stream
CopilotKit = production agent UI option
A2A = agent-to-agent discovery/interoperability
SearXNG = local web search
Firecrawl = optional richer search/scrape/crawl provider
```

## Required reading before coding

Read these files before making structural changes:

```txt
AGENTS.md
.hermes/rules.md
.hermes/skills/app-builder.md
.hermes/skills/crewai.md
.hermes/skills/research-tools.md
.hermes/skills/security.md
.hermes/agent-template/system.md
```

## Non-negotiable rules

1. Keep generated app code manifest-first.
2. Generated CrewAI crews must have manifests, schemas, evals, tests, and permissions.
3. Do not write secrets into source files, manifests, docs, tests, examples, or generated crews.
4. Do not let agents directly change production code or data. Use proposals, patches, PRs, or approval records.
5. Dangerous actions require human approval: email, SMS, payments, deletes, exports, shell commands, auth/billing changes, and production deploys.
6. Keep the repo cloneable and local-first. Docker Compose should remain the main quick-start path.
7. Prefer SearXNG for no-key local search. Use Firecrawl only when explicitly enabled or when a deployment provides it.
8. If adding new app templates, keep them generic and useful outside WandGx while still supporting WandGx products.

## Coding style

- Python lives under `packages/`, `apps/api/`, `apps/worker/`, and `crews/`.
- Frontend lives under `apps/web/`.
- Agent instructions live under `.hermes/`.
- Infrastructure lives under `infra/` and root Compose files.
- Generated crews live under `crews/generated/<crew_id>/`.
- Do not place generated code outside allowed paths.

## Before finishing a change

Run the fastest relevant checks:

```bash
PYTHONPATH=packages:. pytest -q
ruff check .
cd apps/web && pnpm lint
```

If a check cannot run because dependencies or services are missing, document the blocker clearly.

## WandGx ecosystem context

This repo was previously missing from the 138 WandGx repo handoff set. Before ecosystem-facing work, also read:

```txt
.agents/skills/wandgx-ecosystem/SKILL.md
```

That skill carries the current WandGx/SET/Oracle topology, VM routing, production URLs, source/deploy boundaries, central identity rules, and proof gates. Keep this repo as foundation/source infrastructure; dev-box success is not production success unless the relevant production runtime is rebuilt/restarted and live-verified.
