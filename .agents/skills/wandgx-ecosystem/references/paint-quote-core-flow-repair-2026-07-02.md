# Paint Quote core-flow repair notes — 2026-07-02

Use this when Paint Quote complaints mention Stripe plans, quote flow disappearing, property search/research, or packet creation.

## Durable findings

- Production Paint Quote is on LXC123 (`192.168.1.183`) in `/opt/apps/paint-quote`; the deployed directory is an archive-style app directory and may not be a git worktree. Do source edits in the GitHub repo/worktree, then deploy/reconcile into the archive.
- Production auth runs `company-identity`. Frontend first-party actions must not gate solely on `runtimeFlags.useBetterAuth`; they should use `runtimeFlags.useFirstPartyAppData` or explicitly include `runtimeFlags.useCompanyIdentity` when calling same-origin `/api/...` routes.
- Stripe billing routes can work in company-identity mode because server `isBetterAuthRequested()` covers protected app providers. If plan buttons show “temporarily unavailable” before hitting `/api/billing/checkout`, inspect frontend gating first.
- Property packets are allowed to return `success: true` while still showing zero research/street-view/3D assets if connectors are absent. That is not a packet route crash, but it is an unusable packet for the product promise. Verify connector env before assuming code failure.
- Available research services are on VM300:
  - Firecrawl API: `http://192.168.1.248:3002` or public `https://firecrawl.wandgx.com`
  - Searx: `http://192.168.1.248:8080` or public `https://searx.wandgx.com`
  - Firecrawl `/v1/scrape` was verified with `POST /v1/scrape` and no API key on the LAN endpoint.
- In the container, inspect env without printing secrets:

```bash
ssh root@192.168.1.183 'docker inspect painterquote-web --format "{{range .Config.Env}}{{println .}}{{end}}" \
  | sed -E "s/(SECRET|KEY|TOKEN|PASS|PASSWORD)=.*/\\1=REDACTED/g" \
  | grep -E "FIRECRAWL|SEARXNG|PROPERTY_PACKET|BILLING|STRIPE|AUTH_PROVIDER|COMPANY"'
```

## Verification probes

After logging in with a test central account, same-origin API proof can validate core backends faster than the browser when UI is flaky:

```js
// Authenticate through /api/company-identity/auth, then send Authorization: Bearer <token>
POST /api/customers
POST /api/quotes
POST /api/property-packet/prepare
POST /api/billing/checkout
POST /api/billing/portal
```

Expected proof shapes:

- Quote flow: `/api/customers` returns 201 with customer id, `/api/quotes` returns 201 with quote id and positive total.
- Billing: checkout response has `{ success: true, kind: 'checkout', plan: 'PRO', id: 'cs_...', url host checkout.stripe.com }`; portal response has `{ success: true, kind: 'portal', id: 'bps_...', url host billing.stripe.com }` after a Stripe customer exists.
- Packet: response has `{ success: true, packet.persisted: true }`. Asset counts and `source_statuses` determine whether the packet is actually useful.

## Common fix pattern

For frontend billing buttons in company-identity deployments:

```ts
const supportsFirstPartyBilling = (): boolean => Boolean(
  (runtimeFlags as any).useFirstPartyAppData ||
  runtimeFlags.useBetterAuth ||
  (runtimeFlags as any).useCompanyIdentity
);
```

Use this guard instead of `runtimeFlags.useBetterAuth` before calling `/api/billing/checkout` or `/api/billing/portal`.
