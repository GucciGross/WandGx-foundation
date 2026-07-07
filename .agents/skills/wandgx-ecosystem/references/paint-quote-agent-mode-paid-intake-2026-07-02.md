# Paint Quote Agent Mode paid intake pattern — 2026-07-02

Use this reference when Paint Quote work drifts toward overbuilt manual forms, broken packet creation, or unproven billing/agent gates.

## Product lesson

The user explicitly rejected form-first quote flow for Paint Quote. The durable product direction is **Agent as a Service**:

- Agent Mode is a paid feature, not free/manual mode.
- Manual forms remain fallback/edit surfaces, not the primary workflow.
- The user/painter should paste or forward lead data: text, email, call notes, webhook payload, QuickBooks/customer-provider data.
- Agent creates or reuses customer data, resolves/cross-references the address, builds a property packet, drafts the quote, and asks the human only when it cannot confidently resolve something.
- Human-in-loop prompts should be specific: “Which address is correct?”, “I found two property matches”, “Upload/confirm photos or dimensions”, “Approve this quote before sending?”
- Do not expose internal workflow/provider/model names in customer UI. Use product language: Agent Mode, needs review, approve, packet, quote.

## Shipped implementation shape

Files touched in the successful pass:

- `src/pages/AgentInbox.tsx`
  - Reframed `/agent` from `Agent Inbox` into `Agent Mode`.
  - Free users see a paid Agent Mode upgrade panel and no inbox load.
  - Paid users get a lead-intake textarea, optional address correction, and `Run agent` action.
  - Request payload asks for `address_cross_reference`, `property_packet`, `draft_quote`, and `human_approval`.

- `src/contexts/SubscriptionContext.tsx`
  - Added `agent_mode` feature to `PRO` and `BUSINESS`, not `FREE`.

- `src/lib/stripe.ts`
  - Added Agent Mode/product copy into Pro/Business feature lists.

- `src/components/common/Sidebar.tsx`
  - Renamed navigation label to `Agent Mode`.

- `src/services/agentModeApi.ts`
  - Added `AgentModeApiError` so paid-plan and human-review errors surface useful messages/codes.
  - Supports `request_text`, `message`, `prompt`, and `human_in_loop` in the client request type.

- `server/index.mjs`
  - Added backend paid gate for `/api/agent/*`: active/trialing `pro` or `business` subscription with current period, except service-token automation.
  - Added lead text address extraction before packet creation.
  - If no usable address is found, returns `409` with `code: address_needs_human_review` instead of fabricating.
  - Persists `intake_text`, `human_in_loop`, and `address_resolution` in request data.
  - Creates/reuses customer, creates draft quote, builds and persists property packet, and stores packet summary.
  - SearxNG calls need bot-detection-safe headers (`User-Agent`, `X-Real-IP`, `X-Forwarded-For`).

Regression tests added/updated:

- `src/test/pages/AgentInbox.test.tsx`
- `src/test/services/agentModeApi.test.ts`
- `src/test/unit/SubscriptionContext.test.tsx`
- `src/test/server/propertyPacketRoute.test.ts`

## Verification commands used

Local source proof:

```bash
node --check server/index.mjs
npm test -- --run src/test/services/agentModeApi.test.ts src/test/pages/AgentInbox.test.tsx src/test/unit/SubscriptionContext.test.tsx src/test/server/propertyPacketRoute.test.ts
npm run typecheck
npm run build
npm test -- --run
```

Observed full-suite proof from the successful session:

- `161` test files passed.
- `1789` tests passed.
- `npm run typecheck` passed.
- `npm run build` passed.

## Deploy pattern for LXC123

Paint Quote LXC target:

- SSH alias: `paintquote-lxc`
- IP: `192.168.1.183`
- Deploy dir: `/opt/apps/paint-quote`
- App container: `painterquote-web`
- Postgres: `painterquote-postgres`
- Optional local SearxNG: `painterquote-searxng`

The deployed dir is an archive-style/no-git directory, so use source repo + rsync, excluding secrets and build artifacts:

```bash
rsync -az --delete \
  --exclude=.git/ \
  --exclude=.env --exclude='.env.*' \
  --exclude=.env.local --exclude='.env.local.*' \
  --exclude=node_modules/ --exclude=dist/ --exclude=data/ \
  /path/to/source/ paintquote-lxc:/opt/apps/paint-quote/

ssh paintquote-lxc 'cd /opt/apps/paint-quote && docker compose --profile research up -d --build painterquote searxng'
```

Before rsyncing, create a tar backup on the LXC that excludes secrets:

```bash
ssh paintquote-lxc 'set -e; stamp=$(date +%Y%m%d%H%M%S); mkdir -p /opt/apps/paint-quote-releases; cd /opt/apps/paint-quote; tar --exclude=.env --exclude=.env.* --exclude=.env.local --exclude=.env.local.* --exclude=node_modules --exclude=dist --exclude=data -czf /opt/apps/paint-quote-releases/pre-agentmode-$stamp.tgz .'
```

## SearxNG connector pitfall and fix

The app can use the compose `searxng` profile, but default SearxNG may reject JSON requests with `403 Forbidden` because JSON format is not enabled and/or bot detection complains.

Fix in the SearxNG container config:

- Ensure `/etc/searxng/settings.yml` has a non-default `server.secret_key`.
- Ensure JSON format is allowed:

```yaml
search:
  formats:
    - html
    - json
```

Restart SearxNG after editing:

```bash
docker restart painterquote-searxng
```

App env on LXC should include:

```text
SEARXNG_URL=http://searxng:8080
SEARXNG_BASE_URL=http://localhost:8888/
```

Do not store or print Firecrawl/Stripe/Google/agent tokens in skill docs or replies.

## Firecrawl + researched exterior image fallback

If Google Street View is not configured on LXC123, do not fake it and do not keep reporting `street_view_not_configured` as if the whole packet failed. The production-safe fallback is:

1. Configure Firecrawl against the VM300 LAN service, not the Cloudflare/NPM public host when running inside LXC123:

```text
FIRECRAWL_URL=http://192.168.1.248:3002
```

2. Keep local SearxNG enabled for text and image research:

```text
SEARXNG_URL=http://searxng:8080
```

3. Attach public image-search candidates as `agent_found_images` with `source: searxng_image_search` and `requires_human_confirmation: true`.
4. Emit `exterior_image_candidates_need_review` instead of claiming a confirmed Street View image. The user reviews the exterior candidate before customer-facing use.

This turns packets from blocked/no-photo into reviewable packets while preserving truthfulness and human-in-loop safety.

Expected live smoke with Firecrawl + SearxNG + image fallback:

```json
{
  "status": 201,
  "success": true,
  "request_status": "ready_for_review",
  "quote_created": true,
  "packet_created": true,
  "address": "123 Main St, Austin, TX",
  "packet_status": "ready_for_review",
  "agent_found_images": 3,
  "searxng_image_sources": 3,
  "research_count": 5,
  "firecrawl_sources": 5,
  "firecrawl_status": "ready",
  "searxng_status": "ready"
}
```

## Measurement accuracy proof

Measurement-accurate packet status does not require licensed property data if the human/contractor provides explicit dimensions. For live smoke, include property fields such as:

```json
{
  "footprint_width_ft": 42,
  "footprint_depth_ft": 31,
  "stories": 2,
  "wall_height": 10
}
```

Expected proof shape:

```json
{
  "packet_status": "ready_for_review",
  "measurement_source": "manual_dimensions",
  "requires_contractor_review": false,
  "measurement_accuracy": "measurement_accurate",
  "measurement_3d_status": "measurement_accurate"
}
```

If dimensions are absent, keep the warning and ask the human for dimensions/photos. That is correct human-in-loop behavior.

## Stripe product/plan alignment

Production already has Stripe secrets and product/price IDs in the LXC env. Before creating new products, first inspect existing IDs through the server-side Stripe secret from inside the container, and update metadata/copy when possible.

Known desired Stripe product metadata shape:

- Free: `agent_mode=false`, quote limit metadata, no paid Agent Mode.
- Pro: `agent_mode=true`, `agent_workflow=intake_packet_quote_review`, approval-required metadata.
- Business: `agent_mode=true`, `team_agent_inbox=true`, `api_webhook_intake=true`, approval-required metadata.

Do not print Stripe secrets. It is okay to print product IDs, price IDs, nicknames, amounts, recurring interval, and metadata values that are not secret.

## Automatic webhook delivery

The app already has outbound webhook tables, event types, and a delivery loop, but Docker Compose must pass the worker env into `painterquote-web`. If production says webhook delivery is still manual, check both `.env` and `docker-compose.yml`.

Source compose should include under `painterquote.environment`:

```yaml
- PAINTERQUOTE_WEBHOOK_DELIVERY_ENABLED=${PAINTERQUOTE_WEBHOOK_DELIVERY_ENABLED:-false}
- PAINTERQUOTE_WEBHOOK_DELIVERY_TIMEOUT_MS=${PAINTERQUOTE_WEBHOOK_DELIVERY_TIMEOUT_MS:-10000}
```

LXC `.env` production target:

```text
PAINTERQUOTE_WEBHOOK_DELIVERY_ENABLED=true
PAINTERQUOTE_WEBHOOK_DELIVERY_TIMEOUT_MS=10000
```

Verification inside the running container should show the envs, and `painterquote-web` health must be healthy after recreate.

## Live smoke shape

Use service-token automation inside the container to avoid browser credential handling. Do not print the token.

Expected successful summary after hitting `POST /api/agent/intake` with an intake string like `Casey needs exterior repaint at 123 Main St, Austin, TX`:

```json
{
  "status": 201,
  "success": true,
  "request_status": "ready_for_review",
  "quote_created": true,
  "packet_created": true,
  "address": "123 Main St, Austin, TX",
  "research_count": 5,
  "searxng_status": "ready"
}
```

Archive/delete the smoke request after proof if it lands in the app inbox.

Public proof to report:

- `https://paint.wandgx.com/health` -> `healthy`
- `https://painter.wandgx.com/health` -> `healthy`
- Public HTML references the newly built hashed bundle.
- Live container contains expected server/UI strings such as `canUsePaidAgentMode` and `Run agent`.
