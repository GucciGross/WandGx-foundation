# WandGx ecosystem GA/GTM readiness audit pattern — 2026-07-03

Use this reference when the user asks whether the rest of the WandGx ecosystem is “good to go,” especially while WandGx-vNext is still actively being worked.

## Key lesson

Do not treat public route health as GA readiness. A route-alive ecosystem can still be GA-blocked if product-flow proof, public URLs, OAuth callbacks, or integrations are missing.

## Proven audit shape

1. Start with a live SQLite evidence DB for route health, LAN health, and public endpoints.
2. If background audit agents time out, recover directly with focused checks instead of stopping:
   - deployed source keyword sweeps,
   - container env metadata checks with secrets redacted,
   - public-vs-private URL checks,
   - evidence rows inserted back into the DB.
3. Keep final statuses separate:
   - `route_alive`
   - `source_feature_present`
   - `runtime_env_configured`
   - `authenticated_flow_proven`
   - `GA_approved` / `GA_blocked` / `GA_candidate_pending_evidence`
4. Only produce final GA/GTM packets after P0 evidence gates pass; scaffolds/templates may be created earlier but must be marked not GA-stamped.

## Blockers found in the 2026-07-03 pass

These are examples of the kind of findings that should block GA claims until fixed and re-proven:

### Oracle / WandGx Chat

- Deployed Chat had `openInSET` deep-link affordance, but no proven real SET packet-creation tool in the active Chat source (`createSetTrainingPacket` style path not found in deployed source).
- `NEXT_PUBLIC_SET_URL` was absent in the Chat container, so the frontend defaulted to old/private `http://192.168.1.138:8085` SET links.
- Server-side `SET_API_URL` was correctly pointed at VM301 backend (`http://192.168.1.249:8000`), which proves pipe config, not user-visible flow completion.

### PainterQuote Pro

- Agent Mode scaffolding existed: `/api/agent/intake`, `painter_agent_requests`, AgentPacket summary/AG-UI state, paid-plan messaging, and a service token.
- Billing/Stripe env was present and billing enabled.
- Production QuickBooks callback was wrong: `QUICKBOOKS_REDIRECT_URI=http://localhost:3010/api/v1/integrations/quickbooks/oauth/callback`. This blocks QuickBooks Online GA proof until changed to a public callback such as `https://painter.wandgx.com/api/v1/integrations/quickbooks/oauth/callback` and re-smoked.

### SET

- JWT build handoff route existed and generated SOP/onboarding/quiz/readiness checklist material entries.
- `wandgx_build_handoff.py` hardcoded `SET_FRONTEND_URL = "http://192.168.1.138:8085"`, so returned training material URLs were not public-GA safe.
- Notion/Obsidian/ClickUp-level claims were not proven by deployed source: Notion appeared mostly in docs/comparison copy, Obsidian and ClickUp had no deployed-source evidence in the keyword sweep.

## Required proof gates before GA packet stamping

- Oracle visible UI completion for build/training actions, not just API route or page load.
- Oracle/WandGx -> SET real packet handoff with handoff/material IDs and public material URLs.
- PainterQuote AgentPacket -> quote lifecycle proof: draft, edit, approve, send, revise, accept/expire, audit trail.
- PainterQuote QuickBooks Online OAuth/sync/idempotency proof using public callback.
- PainterQuote Stripe/payment/deposit proof if payment deposits are in GA scope.
- SET normal linked user sees imported training context; unlinked/wrong user gets a safe blocked state with no data leak.
- SET ClickUp-like workspace/docs/tasks/automation primitives and Notion/Obsidian connector proof before GTM copy mentions them.

## Reporting language

Use: “route-alive but GA-blocked on product-flow proof.”

Avoid: “good to go” from health checks alone.
