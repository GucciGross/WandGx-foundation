# Hermes Agent Starter

A batteries-included starter for building agent-first SaaS apps with a **Hermes control plane**, **CrewAI runtime crews**, **AG-UI streams**, **A2UI-style generative UI contracts**, **A2A agent cards**, Postgres, Redis, and Docker Compose.

This repo is designed to be cloned as the foundation for every new agent-powered app:

```txt
git clone <your-repo-url>
cd hermes-agent-starter
cp .env.example .env
docker compose up --build
```

Then open:

- Web app: <http://localhost:3000>
- API health: <http://localhost:8000/health>
- Hermes admin API: <http://localhost:8000/admin/hermes/chat>
- A2A card: <http://localhost:8000/.well-known/agent-card.json>

## What this gives you

```txt
Developer/Admin
  ↓
Hermes Control Plane
  - app interview
  - app manifest generation
  - DB/UI/API scaffolding plan
  - CrewAI crew factory
  - feedback triage
  - self-healing proposal loop
  ↓
CrewAI Runtime Plane
  - support crew template
  - generated crew registry
  - worker process
  ↓
AG-UI / CopilotKit-ready Frontend
  - streaming product copilot
  - admin Hermes console
  - approval/feedack surfaces
  ↓
Postgres / Redis / Logs / Feedback
```

## Repo layout

```txt
apps/
  api/                    FastAPI backend, AG-UI stream endpoint, A2A card, feedback API
  web/                    Next.js UI with Hermes admin console and product copilot
  worker/                 CrewAI/background worker skeleton
packages/
  hermes_agent/           Hermes control plane, crew factory, safe code generation helpers
  agui_runtime/           Minimal AG-UI event helpers and SSE encoder
  a2a_adapter/            A2A agent-card helpers
  contracts/              JSON schemas for app, crew, tool, feedback, and approval manifests
crews/
  templates/support_crew/ Example CrewAI-ready crew with deterministic fallback
  generated/              Versioned generated crews live here
infra/
  postgres/init.sql       Local database bootstrap
examples/
  painterquote-pro/       Example app manifest
```

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Local development without Docker:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m apps.api.main
```

In another terminal:

```bash
cd apps/web
corepack enable
pnpm install
pnpm dev
```

## CLI

After `pip install -e .`, use:

```bash
hermes doctor
hermes plan "A quote app for painting contractors"
hermes crew create "Lead intake crew for painting quotes"
hermes observe
```

## Hermes modes

```env
HERMES_MODE=dormant   # Only runs when explicitly called
HERMES_MODE=observe   # Reads logs/feedback and reports issues
HERMES_MODE=guardian  # Generates tests/patch proposals, approval required
```

Production default should be `observe` or `guardian` with `HERMES_AUTOFIX=pr_only`. Direct mutation of production code should stay off.

## Contracts first

Hermes generates manifests before code. Generated crews should always have:

- manifest
- input schema
- output schema
- tool permissions
- tests/evals
- human-approval settings

That is how this starter allows agents to create more agents without turning into chaos.

## Safety defaults

- Generated files are restricted to allowed repo paths.
- Dangerous actions require explicit approval.
- Secrets stay in `.env` and are never written into generated code.
- Feedback becomes evals before prompt or code changes are promoted.
- Self-healing produces proposals by default, not direct production edits.

## GitHub publish

Do **not** paste long-lived PATs into chat or commits. The safest flow is:

```bash
git init
git add -A
git commit -m "Initial Hermes agent starter"
gh repo create hermes-agent-starter --public --source=. --remote=origin --push
```

If you use a token, make it short-lived and fine-grained with only the repository permissions you need.
