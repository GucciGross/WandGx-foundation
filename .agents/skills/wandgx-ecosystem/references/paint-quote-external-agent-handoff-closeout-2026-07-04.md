# Paint Quote external-agent handoff closeout pattern — 2026-07-04

Use when the user pastes a Codex/Claude/other-agent handoff for Paint Quote after work was done somewhere else.

## Key user correction

If the handoff mentions a Mac mini path like `/Users/gucci/Documents/GitHub/paint-quote`, do **not** assume Hermes should code there. The path may only be where Codex was running. Ask/notice whether the user says it is only handoff context. For Paint Quote production work, default to:

- GitHub `origin/main` as source truth;
- LXC123 `192.168.1.183` `/opt/apps/paint-quote` as production deploy archive;
- public routes `https://paint.wandgx.com` and `https://painter.wandgx.com`.

## Closeout workflow from handoff

1. Convert the pasted handoff into a durable local brief under the current run folder. Include:
   - claimed commit/branch,
   - commands already run,
   - remaining blockers,
   - provider env names missing,
   - production target.
2. Clone/fetch GitHub source or use an existing non-Mac local clone. Verify:
   - `origin/main` contains the claimed commit;
   - local source is clean;
   - `AGENTS.md` has been read before editing.
3. Compare source vs LXC123 production freshness. `/health` may not include commit metadata, so prove freshness with:
   - container health/image identity;
   - public + LAN health;
   - live hashed bundle parity between public origins, LAN origin, and container;
   - expected string presence in live bundle.
4. Provider preflight:
   - Redacted-inspect env/container for missing QuickBooks/Stripe variables.
   - Run the repo's provider preflight honestly.
   - If env is missing, list exact variable names and continue non-provider smoke; do not fake QuickBooks/Stripe proof.
5. Live smoke:
   - app loads;
   - auth works with safe/disposable account or service-token smoke;
   - quote creation works;
   - Packet Mode works;
   - Agent Mode / Agent Inbox works;
   - AG-UI/tool/event/approval state is visible;
   - provider preflight status is honest in production.
6. Mobile QA:
   - use mobile viewport/Playwright when real iOS Safari/simulator is not available;
   - check bottom floating actions and top/bottom safe-area padding;
   - capture screenshots/artifact paths if possible.
7. Patch only small blockers that are safe and necessary. If patching, run focused tests/build/lint, deploy, then rerun live smoke.

## Product constraints

- Paint Quote is Agent-as-a-Service first.
- Forms are edit/review fallback surfaces.
- Agent Mode is paid-only and must be gated frontend + backend.
- Human approval is required before external mutations: QuickBooks customer/estimate, Stripe invoice/payment, email sends, quote publication, public sharing, deletes.
- Do not print secrets/tokens/cookies/hashes.
- Public UI must not expose internal tool/model/provider names.
