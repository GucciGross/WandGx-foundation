# WandGx ecosystem completion agents + 10-minute updates — 2026-07-03

Use this when the user says to keep going until the WandGx ecosystem scope is complete, especially after a GA/GTM readiness audit finds blockers.

## Scope discipline

- If the user says a product is already being worked on, exclude it from the background fan-out unless they explicitly add it back.
- In the 2026-07-03 session, PaintQuote was excluded because the user said it was already being worked on; scope became WandGx-vNext + Oracle/Chat/shared platform + SET + ecosystem continuity.
- Keep the exclusion in every prompt and final packet so agents do not waste cycles or collide with another workstream.

## Agent pattern

Hermes `delegate_task` can hit a hard 600s child timeout on broad ecosystem audits. For long completion work, spawn explicit background Hermes CLI agents instead:

```bash
HERMES_MAX_ITERATIONS=300 hermes chat -Q \
  --provider openai-codex -m gpt-5.5 \
  --max-turns 300 --source tool \
  --skills wandgx-ecosystem,wandgx-adaptive-business-os,caveman,ponytail,ponytail-audit \
  --yolo -q "$(cat /tmp/wandgx-ecosystem-exec/prompts/<lane>.txt)" \
  2>&1 | tee /home/claw/reports/wandgx-complete-logs/<lane>.log
```

Recommended lanes:

1. `vnext_build_proof` — normal-user build + preview artifact proof, source/deploy freshness, public health leakage cleanup.
2. `oracle_set_handoff` — public Chat/Oracle URLs, no private 138 fallbacks, real Oracle -> SET handoff packet/material IDs.
3. `set_completion` — public SET URLs, `/training` material route, linked-user/wrong-user proof, Notion/Obsidian/ClickUp-like standards proof.
4. `llm_billing_platform` — LLM billing/top-up path or exact missing-account blocker, central platform guard proof.
5. `finalizer` — waits for lane reports, then packages final GA/GTM report and evidence zip.

Each lane should write a JSON status file under `/tmp/wandgx-ecosystem-exec/state/<lane>.json` plus a report under `/home/claw/reports/`.

## 10-minute update loop

When the user asks for updates every 10 minutes and nothing else until done:

1. Create a script-only cron job (`no_agent=true`) that reads lane JSON/log files and prints a compact status block.
2. Use `schedule="every 10m"` so it is recurring; avoid bare `10m` if a recurring cadence is intended.
3. Set `attach_to_session=true` so final output lands in the ongoing topic/thread.
4. Make the script quiet after final delivery by writing a sentinel such as `/tmp/wandgx-ecosystem-exec/FINAL_NOTICE_SENT`.
5. If `/tmp/wandgx-ecosystem-exec/DONE.json` exists, send the final report and evidence zip as `MEDIA:` and stop emitting regular ticks.

Example compact update style:

```text
╭─ WANDGX ECOSYSTEM FORGE / 10-MIN TICK ─╮
│ scope     vNext + Oracle + SET + platform
│ excluded  PaintQuote
├─────────────────────────────────────────┤
│ vNext        RUN   no-report  12m   │ fixing build proof
│ Oracle       DONE  report     3m    │ no private fallback strings
│ SET          RUN   no-report  12m   │ rebuilding backend
│ LLM/platform RUN   no-report  12m   │ Stripe top-up gate
│ Packets      WAIT  no-report        │ waiting for lanes
╰─────────────────────────────────────────╯
```

## Completion rules

- Do not stamp GA from route health alone.
- Finalizer may produce a `GA blocked` packet if non-code/account blockers remain, but it must be explicit and proof-backed.
- If Stripe MCP OAuth times out in headless Telegram, do not keep looping stale URLs. Use existing secret stores or the secure phone-friendly fallback pattern; otherwise classify as an account/secret blocker and continue other lanes.
- Secret scan generated reports and bundles before delivery.
