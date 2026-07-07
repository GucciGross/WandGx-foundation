# WandGx Stripe MCP research-pricing catalog pattern — 2026-07-04

Use when the user asks to finish Stripe-side pricing/products for WandGx, especially from Telegram/mobile.

## Durable lesson

Stripe-side catalog work can be completed from Hermes on Telegram if Stripe MCP OAuth is already configured as `auth: oauth`. Use the headless MCP paste-back flow: run `hermes mcp login stripe`, send the authorization URL to the user, have them approve on their phone, and let Hermes finish the login. Verify with `hermes mcp test stripe`. Token cache should exist under `~/.hermes/mcp-tokens/stripe.json` with `0600` permissions. Never preserve OAuth codes/tokens in evidence.

## Research-driven WandGx launch ladder

Benchmark from current AI app-builder pricing:

- Lovable: Free, Pro ~$25/mo, Business ~$50/mo, credits/top-ups.
- Bolt: Free, Pro ~$25/mo, Teams ~$30/user/mo, token limits/rollover.
- v0: Free, Team ~$30/user/mo, Business ~$100/user/mo, included and purchased credits.
- Replit: Core ~$20/mo with credits, Pro ~$100/mo with credits.

A good WandGx launch catalog is:

| Offer | Amount | Type | Purpose |
|---|---:|---|---|
| Starter Credit Pack | $5 | one-time | low-friction first purchase |
| Builder Credit Pack | $25 | one-time | market-matched core top-up |
| Scale Credit Pack | $100 | one-time | serious build-day pack |
| Pro Membership | $29/mo | subscription | paid builder tier, just above $25 market anchor |
| Pro Annual | $290/yr | subscription | two-months-free annual upsell |
| Team Membership | $99/mo | subscription | team/pro revenue anchor |
| Team Annual | $990/yr | subscription | team annual upsell |
| Launch Concierge | $499 | one-time | high-ticket founder/help-me-launch upsell |

## Implementation pattern

1. First inspect current app billing behavior. If current launch path credits users via authenticated server-side amount/top-up Checkout, do **not** create generic Payment Links that can bypass account/session association.
2. Use Stripe MCP `stripe_api_search` + `stripe_api_details` before `stripe_api_write`; Product/Price IDs are non-secret, API keys/webhook secrets/OAuth codes are secrets.
3. Create products and prices with stable `lookup_key` values and metadata such as `wandgx_catalog`, `wandgx_sku`, `wandgx_surface`, and `wandgx_position`.
4. For memberships, put monthly and annual prices on the same product. If an annual-only duplicate product is created during an initial pass, create the annual price on the canonical product with `transfer_lookup_key: true`, then deactivate the superseded price/product.
5. Verify active prices with `stripe_api_read GetPricesPrice`; `fetch_stripe_resources` is useful for human-friendly summaries but may omit fields like `active`, `recurring`, and metadata.
6. Update packet evidence with only non-secret product/price IDs, lookup keys, amounts, and verification status.

## Verification checklist

- Stripe MCP connected and tools discovered.
- Each intended lookup key resolves to an active live Price.
- Amount, currency, interval, product, and metadata match expectation.
- Superseded duplicate prices/products are inactive/deactivated.
- No real card charged.
- No secrets or OAuth values stored in evidence.
- Excluded product lane terms scan clean if user excluded that lane.
- Packet manifest/checksums/zip regenerated and zip opens cleanly.

## Known pitfall

Do not overstate the app wiring. Creating Stripe Products/Prices is Stripe-side catalog completion. If the current app still uses amount-based Checkout, say the catalog is ready and the current payment path still works; a later optional code pass can switch checkout line items to these `price_...` IDs.