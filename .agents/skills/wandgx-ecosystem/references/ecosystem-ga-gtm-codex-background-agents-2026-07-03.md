# Ecosystem GA/GTM audits with Codex background agents — 2026-07-03

Use when a WandGx ecosystem GA/GTM readiness pass needs project-specific parallel audits and normal Hermes `delegate_task` workers timed out or are model-capped.

## Durable lesson

If the user says a product is actively being worked on, **exclude it from the readiness verdict** and do not audit, fix, or report it except to mark it out of scope. In this session the correction was: PaintQuote is being worked on, so exclude PaintQuote and switch focus to WandGx-vNext plus Oracle/shared platform, SET, and packet synthesis.

## Background-agent pattern

1. Confirm Hermes delegation/model config if needed, but do not rely on `delegate_task` for long audits when the 600s child timeout is the blocker.
2. Use explicit background Hermes CLI sessions pinned to OpenAI Codex GPT-5.5:
   ```bash
   HERMES_MAX_ITERATIONS=200 hermes chat -Q \
     --provider openai-codex -m gpt-5.5 \
     --max-turns 200 --source tool \
     --skills wandgx-ecosystem,wandgx-adaptive-business-os,caveman,ponytail,ponytail-audit \
     --yolo -q "$(cat /tmp/<prompt>.txt)" 2>&1 | tee /home/claw/reports/codex-gpt55-logs/<lane>.log
   ```
3. Launch one process per independent lane:
   - WandGx-vNext readiness
   - Oracle/WandGx Chat + shared platform + LLM/identity/Appwrite
   - SET readiness and integrations
   - GA/GTM packet synthesis
4. Each prompt must be self-contained and include explicit scope exclusions, especially: `PAINT-QUOTE IS OUT OF SCOPE` when the user has corrected that.
5. Require each worker to write a report file under `/home/claw/reports/` and never modify production code, secrets, routes, containers, or git during an audit-only run.
6. Monitor with `process.poll`/`process.wait`, then verify the report files exist before consolidating. A completed process without a report is not evidence.

## Prompt requirements

Every background prompt should include:

- `You are a background Hermes agent running with provider openai-codex model gpt-5.5.`
- Exact product scope and exact exclusions.
- Loaded skills to follow.
- `Task type: readiness audit and evidence collection, not code fix/deploy.`
- `Never print secrets. Redact tokens, passwords, keys, OAuth codes, cookies, connection strings.`
- Required output path.
- Verdict labels: `GA approved`, `GA blocked`, `GA candidate pending evidence`.

## Pitfalls

- Do not keep re-dispatching `delegate_task` if all useful workers hit the child timeout. Switch to background Hermes processes with higher max-turns.
- Do not audit PaintQuote if the user says it is being worked on. That creates duplicate/conflicting work.
- Do not let packet synthesis include excluded products by inertia from earlier reports. The synthesis prompt must restate the current scope.
- Do not claim Codex CLI availability from Hermes `openai-codex` provider availability. Hermes background agents can use `openai-codex` even if standalone `codex` binary is absent.
