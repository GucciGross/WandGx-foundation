# WandGx vNext source-level ops watcher/autorepair scaffold (2026-07-04)

Use this when adding or extending WandGx vNext production ops/self-healing from source while keeping production deploys behind a human approval gate.

## Durable source shape

Canonical vNext files used for the scaffold:

- `apps/api/src/incidents.mjs`
  - Redacted JSONL incident recorder.
  - Required incident metadata: `incident_id`, `recorded_at`, `source`, `severity`, safe message, route/build/app/user identifiers, `fingerprint`, 20-minute triage window, `autorepair` metadata, redacted `context`.
  - Redact secrets in string values, object keys, and route/query strings. In this session a regression check caught an unredacted `?token=` in `route`; route values must pass through the same redactor.
- `apps/worker/src/incidents.mjs`
  - Worker helper that forwards failures to the API incident recorder.
- `apps/worker/src/worker.mjs`
  - Worker health capabilities should include ops watcher/autorepair handoff and the human-approval deploy gate when present.
- `scripts/wandgx-vnext-autorepair.mjs`
  - Source-level watcher scaffold.
  - Processes structured incident JSONL.
  - Optionally scans generic logs from `WANDGX_OPS_LOG_PATHS` for `fatal|critical|error|exception|unhandled rejection|uncaught`.
  - Optionally checks URLs from `WANDGX_OPS_HEALTH_URLS` and records incidents on non-2xx/timeout.
  - Writes state and prompt drafts under `.codex/runtime/wandgx-vnext-autorepair` unless overridden.
- `scripts/check-vnext-ops-autorepair.mjs`
  - Focused regression check for redaction, 20-minute triage metadata, dry-run prompt drafting, generic log incident capture, and deploy gate blocking.
- `package.json`
  - Keep script entries such as `ops:incidents:once`, `ops:incidents:watch`, `ops:incidents:dry-run`, and `ops:autorepair:check`.

## Human approval deploy gate

Default behavior must be record-only / dry-run prompt drafting. Do not deploy from the watcher by default.

Recommended env shape:

- Autorepair/agent execution enabled only when one of these is true:
  - `WANDGX_VNEXT_AUTOREPAIR_ENABLED=true`
  - `WANDGX_CODEX_AUTOREPAIR_ENABLED=true`
- Deploy is only requested when one of these is true:
  - `WANDGX_VNEXT_AUTOREPAIR_DEPLOY=true`
  - `WANDGX_CODEX_AUTOREPAIR_DEPLOY=true`
- Deploy is only allowed when a separate human approval flag is also true:
  - `WANDGX_VNEXT_AUTOREPAIR_DEPLOY_APPROVED=true`
  - `WANDGX_CODEX_AUTOREPAIR_DEPLOY_APPROVED=true`
  - `WANDGX_AUTOREPAIR_HUMAN_APPROVED=true`
- A deploy command must be configured separately, e.g. `WANDGX_VNEXT_AUTOREPAIR_DEPLOY_COMMAND`.

A deploy request without the approval flag should produce `deploy_blocked_reason: human_approval_required` and no deploy command should run.

## Triage prompt requirements

Prompt drafts should be redacted and include:

- Hard scope: WandGx vNext only; do not touch Paint Quote/PainterQuote/paint.wandgx unless explicitly asked.
- Inspect evidence and current source before fixes.
- Do not print secrets.
- Add/update focused regression checks for behavior changes.
- If the same error repeats twice, research 3-5 credible fixes before another local attempt.
- State whether deployment remains blocked by the human approval gate.

## Verification pattern

Run focused checks before broader build/test suites:

```bash
node --check scripts/wandgx-vnext-autorepair.mjs
node --check scripts/check-vnext-ops-autorepair.mjs
node --check apps/api/src/incidents.mjs
node --check apps/worker/src/worker.mjs
pnpm ops:autorepair:check
git diff --check
```

Also confirm scope before reporting:

```bash
git status --short | grep -Ei 'paint|painter' || true
```

The verification is source-level only unless a live deploy is explicitly requested and the human approval deploy gate is satisfied. Do not claim deployed or live-verified from these checks alone.
