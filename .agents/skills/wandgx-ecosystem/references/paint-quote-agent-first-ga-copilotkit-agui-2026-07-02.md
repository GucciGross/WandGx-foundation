# Paint Quote agent-first GA/GTM proof pattern — 2026-07-02

## Trigger
Use when the user asks to make PainterQuote/Paint Quote GA/GTM ready, Agent-as-a-Service, CopilotKit/AG-UI-backed, or production deployable.

## Durable lessons
- Do not answer with another readiness caveat when the user asks to ship. Pick the smallest customer-visible blocker and move through source fix → tests/build → commit/push → LXC deploy → live public proof.
- Forms are review/edit fallback surfaces. The primary creation path is Agent Mode intake producing structured JSON: customer draft, quote draft, assumptions, warnings, missing info, confidence, asset summary, integration plan, pending approvals, proposed diffs, and tool events.
- Agent Mode is paid-only. Gate it on frontend and backend; allow only service-token automation to bypass human session gating for server-side ingestion/smoke.
- External mutations must remain approval-gated. It is OK for the agent to research, calculate, draft, summarize, and prepare. Email sends, external sync, invoices, charges, deletes, quote publication, and public sharing require human approval.
- CopilotKit is not a marketing checkbox: wire a real bridge/runtime and prove the browser route renders without JS errors. If using AG-UI state, expose state with events, pending approvals, proposed diffs, and packet JSON instead of chat-only text.
- For Paint Quote LXC123, `/opt/apps/paint-quote` is often an archive-style deployment dir, not a git checkout. Reconcile source to GitHub first, then rsync safe files to the LXC excluding `.env*`, `.git`, `node_modules`, and `dist`, then rebuild with Docker Compose.
- Health alone is not freshness. Verify public routes, live hashed JS bundle, browser console on `/agent`, container health, and a live service-token Agent Mode smoke.

## Known-good verification shape
- Local: `npm test -- --run`, `npm run typecheck`, `npm run build`, `node --check server/index.mjs`.
- Browser: unauthenticated `/agent` redirects to `/login`, renders the CopilotKit bridge marker, and has zero console JS errors.
- Production HTTP: `https://paint.wandgx.com/`, `https://painter.wandgx.com/`, and both `/health` endpoints return 200/healthy with a current hashed JS asset.
- Agent smoke inside `painterquote-web`: POST `/api/agent/intake` with `x-painterquote-agent-token`, verify 201, `ready_for_review`, quote created, packet created, then archive the request.
- AG-UI smoke: GET `/api/agent/requests/:id/ag-ui-state`, verify `agent_packet`, `events`, `pending_approvals`, and `proposed_diffs` exist.
- Tool registry smoke: GET `/api/agent/tool-registry`, verify version, tool count, and approval-required count.

## Deployment command pattern
```bash
rsync -az \
  --exclude='.git/' --exclude='node_modules/' --exclude='dist/' \
  --exclude='.env' --exclude='.env.*' --exclude='.env.local' --exclude='.env.local.*' \
  /path/to/paint-quote/ paintquote-lxc:/opt/apps/paint-quote/
ssh paintquote-lxc 'cd /opt/apps/paint-quote && docker compose up -d --build'
```

Do not print or copy secrets while doing this. Keep Stripe/OAuth/API credentials redacted and use existing deployment env or approved OAuth tooling only.
