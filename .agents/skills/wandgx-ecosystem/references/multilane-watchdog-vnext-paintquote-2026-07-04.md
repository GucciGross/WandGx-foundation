# WandGx multi-lane watchdog + vNext/PaintQuote handoff lessons — 2026-07-04

Use when the user asks Hermes to kick off multiple WandGx ecosystem workstreams, keep them running through context compression/new conversations, or continue from handoff packets.

## Multi-lane execution pattern

- Create one durable run folder under `~/.hermes/project-runs/<date>-<scope>/` with:
  - `CONTINUATION.md`
  - `prompts/`
  - `logs/`
  - `reports/`
  - `handoffs/`
  - `artifacts/`
- Write each lane prompt to disk before spawning the agent.
- Spawn explicit background Hermes CLI agents for long lanes, not native `delegate_task`, when lanes need different models or may outlive a context window.
- Use `notify_on_complete=true` for bounded background processes.
- Reports are the source of truth, not the truncated background completion message.

## Watchdog/autoresume semantics

A script-only cron watchdog survives context compression and `/new` because it is scheduler-level, not chat-context-level.

Known-good shape:

```text
script: wandgx_multilane_watchdog.py
schedule: every 10m
no_agent: true
deliver: origin
attach_to_session: true
```

The watchdog should read lane logs/reports and print compact status. It should not use an LLM. It monitors/reporting automatically across new conversations, but does not automatically relaunch crashed lanes unless a separate controller is built. Be explicit with the user:

- background processes + cron watchdog keep running across conversation reset;
- reports/logs persist in the run folder;
- a new session can resume by reading `CONTINUATION.md`;
- relaunching stale/dead lanes requires a stronger auto-resume controller.

## WandGx-vNext handoff packet pattern

If user uploads a zip packet:

1. Extract to `handoffs/<packet-name>/`.
2. Summarize files.
3. Inspect any reference image with vision if available, but do not block on vision failures.
4. Write a controller brief in `reports/` before spawning the UI lane.
5. For UI work, prefer GLM-5.2 if available.
6. Preserve the user’s direction: terminal/operator like `llm.wandgx.com` plus functional space/constellation map, not decorative galaxy wallpaper.

VM300 WandGx-vNext static deploy notes from this session:

- Live/deploy tree: `/opt/apps/WandGx-vNext/apps/web` on VM300 `192.168.1.248`.
- Container: `wandgx-vnext-web-1`, port `31381`.
- Static files are bind-mounted/hot-served via `scripts/local-dev-138.mjs`; no build step for this web slice.
- If 138 is unreachable, VM300 changes can be shipped live, but must be back-committed to `GucciGross/WandGx-vNext` once 138 returns.
- Always report that live != canonical repo until back-committed.

## Paint Quote handoff pattern

If the user pastes a Codex handoff that mentions a Mac path, do not assume the Mac is the target. In this session the user explicitly corrected:

- `/Users/gucci/Documents/GitHub/paint-quote` was only where Codex ran.
- Do not code on the Mac mini for that handoff.
- Use GitHub `origin/main` and/or LXC123 production deploy instead.

Production target:

- LXC123 `192.168.1.183`
- deploy dir `/opt/apps/paint-quote`
- containers `painterquote-web`, `painterquote-postgres`
- public routes `https://paint.wandgx.com`, `https://painter.wandgx.com`

For QuickBooks/Stripe provider proof:

- Redacted-inspect env first.
- Do not fake live provider proof when env is missing.
- Continue with non-provider smoke and list missing variable names only.
- Human approval remains required before external QuickBooks/Stripe mutation.
