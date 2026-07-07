# SET + vNext ops/autorepair and competitive feature slice (2026-07-04)

Use this reference when the user asks whether WandGx is launch-ready, asks for self-healing/log-watching, or asks agents to add missing competitive app-builder features.

## Durable lessons

- **Do not equate source scaffolds with deployed self-healing.** State the boundary precisely: cron/script watchdog live vs source-level watcher committed vs production service deployed.
- **Human approval gate first.** Autorepair should draft triage/fixes and stay dry-run by default. Deployment requires both a deploy-request flag and a separate human-approval flag. Only after a clean week should narrow safe auto-redeploy classes be considered.
- **Subagent output is not final proof.** When background agents return or time out, the parent must re-read summaries, inspect diffs, rerun focused checks, fix obvious test failures, run smoke checks, scan changed files for excluded product/secret-like strings, then commit coherent slices.
- **Classify webhook before checkout.** Stripe webhook errors include the word `stripe`, which can accidentally classify as checkout. In SET/vNext incident classifiers, route family and priority should put `webhook` before broad `stripe/checkout/payment` matching.
- **Launch copy gates matter.** If a public copy checker requires visible fallback copy in an HTML shell, add a safe no-JS fallback rather than weakening the checker.
- **Legacy route compatibility matters for GTM.** SET legacy `/training?...` links should route through the Adaptive Training auth/returnTo path instead of 404ing.
- **Handoff URLs must be public and encoded.** WandGx -> SET training links should use a public frontend URL such as `https://trainwithset.com` (configurable via env), not a LAN/dev host, and app names/query values must be URL-encoded.
- **Launch-safe SET copy:** replace pilot-only CTAs with `Talk to us`, `workspace setup`, or `guided evaluation` unless the user explicitly wants pilot framing.

## Proven vNext slice

Committed source slice: `ab686d5 Add launch ops guardrails and builder starters`.

Changed class areas:
- `scripts/wandgx-vnext-autorepair.mjs`: incident JSONL/log/health processing, redacted prompt drafts under `.codex/runtime/wandgx-vnext-autorepair`, dry-run default, optional agent command, deploy blocked without explicit human approval env.
- `apps/api/src/incidents.mjs`: strengthened redaction including route/query secrets and added autorepair metadata.
- `apps/worker/src/worker.mjs`: advertises watcher + human approval gate in worker health.
- `scripts/check-vnext-ops-autorepair.mjs` and `package.json`: focused regression check.
- `apps/web/src/react/shell/starterTemplates.ts`, `HomeView.tsx`, `BuildView.tsx`, `styles.css`: starter template/prompt-example cards for app-builder competitiveness.
- `apps/web/index.html`, `apps/web/src/landing/home.css`: public pricing/upsell ladder.
- `apps/web/workspace-shell.html`: safe public no-JS fallback copy required by GA checker.

Verification that passed:
- `pnpm ops:autorepair:check`
- `pnpm --filter @wandgx/web typecheck`
- `pnpm --filter @wandgx/web build`
- `pnpm ga-public-copy:check`
- `git diff --check`
- changed-file excluded product scan: 0 hits for `Paint Quote|PainterQuote|paint.wandgx`
- changed-file secret-like scan: 0 actionable hits

## Proven SET slice

Committed source slice: `efd4148 Add SET ops triage gate and launch-safe handoff`.

Changed class areas:
- `scripts/set-codex-autorepair.mjs`: health checks, log extraction, incident classification, redaction, dry-run prompt drafting, deploy gate.
- `scripts/__tests__/set-codex-autorepair.test.mjs`: regression coverage for redaction, classification, deploy gate, health and docker-log extraction.
- `SET-backend/app/services/incidents.py` + `SET-backend/app/api/routes/system.py`: classification and deploy-gate metadata in incident records/responses.
- `SET-backend/app/api/routes/wandgx_build_handoff.py`: public configurable `SET_FRONTEND_URL`, URL-encoded app query value.
- `SET-backend/tests/test_api/test_system.py`: webhook-over-checkout classification regression.
- `SET-backend/tests/test_api/test_wandgx_build_handoff.py`: public/encoded handoff URL proof.
- `SET-frontend/src/AppShell.jsx`: legacy `/training` route uses Adaptive Training auth path.
- SET public frontend files/tests: pilot language replaced with launch-safe `Talk to us` / setup / guided evaluation language.

Issues caught and fixed by parent after subagents:
- SET watcher test initially failed because webhook incidents were classified as checkout. Fix: move webhook above checkout in priority and route-family matching, add backend endpoint regression.
- SET frontend tests initially failed because `/training?...` rendered 404 and terms expected copy did not match current copy. Fix: add `/training` route to AdaptiveTrainingRoute and align test to exact `guided evaluation` heading.

Verification that passed:
- `npm run ops:incidents:test` -> 7/7 passed
- `python -m pytest SET-backend/tests/test_api/test_system.py SET-backend/tests/test_api/test_wandgx_build_handoff.py -q` -> 29 passed
- `npm run check:public-set`
- `pnpm test --run src/__tests__/AppShell.test.jsx src/components/public/__tests__/PublicChrome.test.jsx src/pages/__tests__/PublicCtaClickthrough.test.jsx` -> 40 passed
- `pnpm build` in `SET-frontend`
- `git diff --check`
- changed-file excluded product scan: 0 hits
- changed-file secret-like scan: 0 actionable hits

## Reporting pattern

When reporting to the user, use the launch boundary language:

- `Apps live health: green` only if public smoke is current.
- `Payments launch-ready` only if Checkout/webhook/credit proof exists; say whether a real card was charged.
- `Ops watchdog active` only if cron/process is actually scheduled/running.
- `Source improvements verified + committed, not deployed yet` if changes are only in canonical source.
- `Autoredeploy disabled by design; human gate first` unless the approval/clean-week enablement is actually in production.
