# Phone-first Stripe setup fallback for WandGx LLM credits

Use when Stripe MCP OAuth or CLI OAuth cannot complete from a Telegram/headless Hermes runtime and the user can only act from a phone.

## Trigger

- User needs Stripe setup for WandGx/LLM credits.
- `hermes mcp login stripe` or `mcporter auth` loops on `127.0.0.1` callbacks, times out, or rejects with client/state mismatch.
- User says they need a flow that works from their phone.

## Pattern

1. Stop retrying OAuth links. Explain that the callback is local to the browser/device and headless OAuth is the wrong path for this context.
2. Use a short-lived HTTPS secret drop page on an existing WandGx-controlled host. Requirements:
   - high-entropy token in URL
   - HTTPS via existing NPM wildcard cert
   - no logging of submitted values
   - writes secrets to a root-only temp file with `0600`
   - remove route/process/file after setup
3. Ask for only the minimum Stripe values:
   - Stripe server API key, preferably restricted (`rk_`) with Customers read/write and Checkout Sessions read/write; Webhook Endpoints write only if Hermes will auto-create the webhook.
   - Webhook signing secret (`whsec_...`) if webhook is created manually.
   - Publishable key (`pk_...`) optional.
4. Configure LLM DB-backed settings, not env vars:
   - `billing.stripe_secret_key`
   - `billing.stripe_webhook_secret`
   - `billing.stripe_publishable_key`
   - confirm `billing.enabled=true` and `billing.min_topup_usd`.
5. Webhook endpoint for Stripe Dashboard:
   - URL: `https://llm.wandgx.com/webhook/stripe`
   - Event: `checkout.session.completed`
6. Verify without printing secrets:
   - settings are non-empty by length/hash only
   - `/portal/billing/topup` returns 303 to Stripe Checkout for a logged-in user
   - webhook signature rejects bad/missing signatures with 400
   - completed checkout credits `users.credit_balance` and inserts a positive `transactions` row with `stripe_ref`
   - after credit, `/v1/chat/completions` succeeds and records a debit
   - duplicate webhook event does not double-credit
7. Clean up:
   - delete temporary NPM proxy host
   - kill drop-page process
   - remove temp files containing secrets

## Safety rules

- Never ask for Stripe passwords, 2FA codes, recovery codes, dashboard cookies, or OAuth browser session data.
- Do not paste API keys or webhook secrets into Telegram. Use the secure drop page or user-managed server-side secret placement.
- Prefer restricted keys over full secret keys.
- Do not store transient OAuth URLs or callback codes in memory.
