# Cross-repo incident logging + background autorepair pattern

Use this reference when adding or maintaining self-healing/error triage across WandGx ecosystem repos.

## Product intent

- User-facing error reporting should be easy and accessible, but not the focus of the UI.
- Logging and self-healing should run in the background.
- Every user-reported/runtime incident should be triaged within 20 minutes unless it is a genuinely large emergency.
- Customer-facing UI/copy must not expose internal tool, model, provider, or agent names.

## Durable shape

### WandGx

There are two WandGx source shapes to distinguish:

- `GucciGross/WandGx` contains the older/larger worker/API implementation. Relevant files include `apps/api/src/routes/bugs.ts`, `frontend/src/api/types.ts`, `apps/worker/src/orchestrator/runBuild.ts`, and worker incident helpers.
- Public production currently runs `GucciGross/WandGx-vNext` on VM300 from `/opt/apps/WandGx-vNext`. For live production incident triage, add/verify the vNext shape too: `apps/api/src/incidents.mjs`, `apps/api/src/server.mjs`, `apps/worker/src/incidents.mjs`, `apps/worker/src/worker.mjs`, and `scripts/wandgx-vnext-autorepair.mjs`.

When the user asks to “host” or “deploy” WandGx incident/self-healing work, do not stop at `GucciGross/WandGx` if production is vNext. Either port the equivalent incident route/helper/watcher into `GucciGross/WandGx-vNext`, or explicitly report that only the non-production repo was changed.

Older/larger repo pattern:

- API user reports: `apps/api/src/routes/bugs.ts`.
- Frontend API types: `frontend/src/api/types.ts`.
- Worker build failures: `apps/worker/src/orchestrator/runBuild.ts`.
- Worker incident helper pattern: redacted JSONL records, structured log prefix, `incidentId`, `fingerprint`, `triage`, and background autorepair metadata.
- Background watcher script pattern: `scripts/wandgx-autorepair.mjs` tails docker compose logs, parses structured incident events plus generic ERROR/CRITICAL/FATAL lines, writes incident/run state under `.codex/runtime/*-autorepair`, and only invokes Codex when `*_CODEX_AUTOREPAIR_ENABLED=true`.

### SET

- Backend incident route: `SET-backend/app/api/routes/system.py` `/api/system/incidents`.
- Incident service: `SET-backend/app/services/incidents.py`.
- Frontend telemetry: `SET-frontend/src/services/errorTelemetry.js` and global install from `SET-frontend/src/main.jsx`.
- Background watcher script pattern: `scripts/set-codex-autorepair.mjs`.

### WandGx-Enterprise

- Gateway error handler and client incident route: `apps/gateway/src/server.ts`.
- Gateway incident helper pattern: `apps/gateway/src/ops/incidents.ts`.
- Browser global error/unhandled rejection reporter: `apps/web/src/opsIncidentClient.ts`, installed from `apps/web/src/main.tsx`.
- Background watcher script pattern: `scripts/enterprise-autorepair.mjs`.

## Required fields for incident records

- stable `incident_id`
- `recorded_at`
- `source`
- `severity`
- safe user/product `message`
- route/component/build/app/user identifiers when available
- `fingerprint` for dedupe/retry suppression
- `triage.status = queued_for_triage`
- `triage.sla_minutes = 20` by default
- `triage.due_at`
- `triage.emergency_override_allowed = true`
- `autorepair.handoff = background` or product-appropriate equivalent
- `autorepair.enabled` and `autorepair.deploy_enabled`
- redacted `context`

## Redaction expectations

Redact by key name and by value pattern. Always redact:

- authorization, bearer/basic tokens, cookies, JWTs
- API keys, secrets, passwords, private keys
- session IDs and refresh/access tokens

Tests should assert both that `[REDACTED]` appears and that sample secret values do not.

## Verification pattern

Run focused verification first, then broader checks if dependencies are ready.

Good focused checks:

- helper unit test for redaction + 20-minute triage metadata
- direct service invocation for Python incident recorder if full pytest deps are absent
- route-level test for client incident endpoint
- `node --check` for watcher scripts
- `python -m py_compile` for touched Python modules
- `tsc --noEmit` for touched TypeScript packages once workspace package builds/links are present
- `git diff --check` in every touched repo before commit

If workspace package links are stale after building a local package, rerun `npm ci --ignore-scripts` in the consumer package before repeating `tsc`. Capture the fix pattern, not the transient missing-package error.

## Autorepair watcher guardrails

- Default to dry-run/record-only unless the explicit `*_CODEX_AUTOREPAIR_ENABLED=true` env var is set.
- Do not push/deploy from the watcher unless a separate `*_CODEX_AUTOREPAIR_DEPLOY=true` env var is set.
- Block if the repo worktree is dirty.
- Persist prompts and process tails under `.codex/runtime/...` for audit.
- Include prompt rules: inspect evidence first, do not print secrets, add focused regression tests, commit coherent changes, and if the same error repeats twice, research 3-5 credible fixes before another local attempt.
