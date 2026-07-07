# LLM Stripe credit setup notes

Use this when finishing Stripe payments for the WandGx LLM proxy / Oracle API credit top-ups.

## Current app shape

- LLM app: VM300 `/opt/apps/LLM`, container `llm-proxy`, public base `https://llm.wandgx.com/v1`, host port `9090`.
- Billing/credit enforcement is DB-backed in `/opt/apps/LLM/data/analytics.db` and was proven separately from Stripe checkout:
  - positive-balance API users get charged/debited after successful `/v1/chat/completions` calls
  - zero-balance API users receive `429` with insufficient-credit response
- Stripe checkout/top-up requires real Stripe API/webhook configuration; do not claim it is done until a checkout session and webhook credit path have been tested.

## Stripe MCP OAuth on headless Telegram sessions

The configured MCP entry can be present but unauthenticated. `hermes mcp test stripe` may say no cached tokens exist in non-interactive mode. The working handoff pattern is:

```bash
MCPORTER_OAUTH_TIMEOUT_MS=900000 \
  npx -y mcporter --log-level info --oauth-timeout 900000 \
  auth --reset --http-url https://mcp.stripe.com --name stripe --json
```

Then poll the background process, extract only the printed `https://access.stripe.com/mcp/oauth2/authorize?...` URL, and send it to the user. Never ask for passwords, 2FA codes, recovery codes, dashboard cookies, or secret keys.

Important pitfall: if Stripe says authorization succeeded in the user's browser but the headless process keeps waiting, the OAuth callback probably went to the user's local `127.0.0.1:<port>` instead of the Hermes host. Ask only for the final localhost callback URL from the browser address bar, or restart OAuth from a browser in the same network namespace as mcporter.

## Completion proof checklist

Before saying Stripe is finished:

1. Stripe MCP auth works and tool listing succeeds.
2. Required product/price/payment link or Checkout Session resources exist in Stripe; record IDs only, never secret keys.
3. LLM settings/env have Stripe secret/restricted key and webhook secret stored server-side with values redacted in all reports.
4. Webhook endpoint verifies Stripe signatures before crediting users.
5. A test-mode checkout session can be created for a known credit amount.
6. A completed checkout webhook credits the correct LLM user balance.
7. Duplicate webhook/event replay is idempotent and does not double-credit.
8. Public unauthenticated endpoints still reject protected LLM calls.

## Reporting

Report only resource IDs, endpoint URLs, test-mode vs live-mode, and proof statuses. Redact API keys, webhook signing secrets, OAuth tokens, customer PII, and checkout/session URLs unless the user explicitly needs to click a short-lived test checkout link.