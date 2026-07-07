# WandGx ops watchdog + Telegram-safe triage loop — 2026-07-04

Use this reference when the user asks for launch ops, log watching, incident alerts, self-healing, agent triage, or auto-redeploy controls across WandGx vNext, LLM, identity, SET, and Appwrite.

## Durable lesson

Do not claim the ecosystem has hands-off self-healing just because autorepair scripts exist in source. Prove the watcher is installed/running and that it actually checks production surfaces. If not present, install a script-only cron watchdog that stays silent when healthy and alerts only on incidents.

## Recommended shape

Create a script-only Hermes cron job, not a chatty LLM-driven recurring job:

- `no_agent=true`
- schedule: `every 5m` for launch week
- script under `~/.hermes/scripts/`
- stdout empty when healthy
- non-empty stdout only for incident alerts

The script should check:

- public URLs: WandGx home/register/signup/app, API, worker, Chat/Oracle, LLM health, identity/JWKS, Appwrite health, SET home/API/docs
- remote Docker container health on VM300, VM301, VM302 via SSH
- VM301 SET containers must include `set-auth-1`; otherwise SET auth/JWKS failures can be invisible while SET frontend/backend health stays green
- filtered recent Docker logs for: 5xx, checkout/Stripe, webhook/signature, auth/signup/register, JWKS, zero-credit/insufficient-credit/429, fatal/error/traceback/unhandled, connection refused, timeout
- direct auth/JWKS probes for SET when auth is in scope: `https://auth.trainwithset.com/api/auth/jwks`, not only `/api/auth/ok`

## Incident record requirements

For each new/deduped incident, write redacted JSONL with:

- `incident_id`
- `fingerprint`
- `recorded_at`
- `source`
- `component`
- `incident_class`
- `severity`
- safe `message`
- `evidence`
- `triage.status = queued_for_triage`
- `triage.sla_minutes = 20`
- `triage.human_deploy_approval_required = true` by default
- `triage.auto_redeploy_enabled = false` by default

Redact secrets by both value pattern and key name. Always redact Stripe keys/secrets, OAuth codes/tokens, webhook secrets, cookies, Authorization headers, API keys, passwords, JWTs, private keys, and GitHub tokens.

## Agent triage loop

On incident, generate a read-only triage prompt and optionally run Hermes/Codex in read-only mode. The prompt must say:

- inspect evidence first
- do not edit files
- do not restart services
- do not deploy
- do not print secrets
- identify owner repo/service
- propose minimal fix and verification commands
- human approval required before deploy

This gives the user a fix draft quickly while preserving a safe launch posture.

## Human approval gate and later auto-redeploy

Initial launch posture:

- no automatic deploys
- alerts + read-only triage drafts only
- human approval required for restarts/deploys

After a clean week, auto-redeploy may be enabled only for narrow safe classes and only with explicit env flags, e.g.:

- `WANDGX_OPS_AUTO_REDEPLOY_ENABLED=true`
- `WANDGX_OPS_CLEAN_DAYS_REQUIRED=7`
- safe classes: container health / simple 5xx-style restartable cases

Never enable broad code-editing auto-deploy without separate explicit approval.

## Verification pattern

After installing the watchdog:

1. Run the script manually with autotriage disabled; expect empty stdout when healthy.
2. Create/confirm cron job and run it once.
3. `cronjob list` should show the watchdog enabled and last status `ok`.
4. Confirm `~/.hermes/state/wandgx_ops/state.json` exists and updates `clean_since` / `last_clean_at` on healthy runs.
5. Report that the watcher is active, but distinguish it from fully autonomous code-fix/redeploy until the deploy gate is intentionally enabled.

## Pitfalls

- Do not use `watch_patterns` on noisy log substrings for long-running processes; it rate-limits and spams. Use script-only cron with deduped incidents.
- Do not treat existing source scripts like `wandgx-vnext-autorepair.mjs` or `set-codex-autorepair.mjs` as production automation unless a service/cron/process is actually running them.
- Do not create generic Stripe Payment Links for credit packs when account/session-specific crediting depends on authenticated server-side Checkout.
- In Telegram/mobile workflows, keep alerts compact and include MEDIA links to triage reports/incident JSONL when needed.
- Tune log filters so access-log noise does not hide incidents: ignore normal `2xx/3xx` access logs, expected auth probes like unauthenticated `401`, stack-continuation lines after the headline error, generic `authenticated: true/false` messages, benign SET startup/config notices (`[CONFIG] All critical configuration keys present`, `[OK] Rate limiting enabled`, optional `auth_provider`/`webhook_delivery` not configured), and OAuth debug connection lines. Keep headline errors such as `ERROR [Better Auth]: relation "jwks" does not exist`.
- Cap automatic LLM triage per watchdog run (for example one new triage report per tick) and still write prompts for the rest. A noisy incident burst should not spawn many long-running LLM jobs that make the watchdog exceed its cron window.
- Safer default after the July 2026 watchdog timeout: keep `WANDGX_OPS_AUTOTRIAGE=false` unless the user explicitly wants live read-only LLM triage drafts. The watchdog should still write triage prompt files, but it should not launch Hermes by default from inside the cron loop because that can exceed the schedule window and look like a watchdog failure.
- When the user asks to reduce watchdog noise/frequency, list cron jobs first and update exact job IDs; recurring hourly should be `every 1h` / `every 60m`, not a one-shot timestamp. Verify with `cronjob list` after updates.
