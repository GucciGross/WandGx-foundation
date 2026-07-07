# WandGx self-service launch + Stripe Checkout proof pattern — 2026-07-03

Use this when finishing or re-verifying **fully unguarded WandGx launch**, especially where the question is “real users / real payday”.

## Launch verdict distinction

Do not call the ecosystem fully self-service-ready from route health alone. Require proof for:

1. public auth routes render correct Sign in/Create account surfaces,
2. new account can enter product without operator action,
3. signed-in user can submit a prompt and reach a hosted artifact,
4. unauthenticated protected APIs still return 401,
5. payment/top-up redirects to Stripe Checkout,
6. signed webhook credits exactly once,
7. zero-credit user is blocked and credited user succeeds.

## Email verification policy

If inbox delivery is not proven and the user wants unguarded launch now, the viable launch decision is: **disable mandatory email verification for initial entry**, document it explicitly, and verify immediate account/session behavior.

For the 2026-07-03 launch pass:

- Central identity env was set to `COMPANY_IDENTITY_EMAIL_VERIFICATION_ENABLED=false`.
- LLM central-login gate was set to `COMPANY_IDENTITY_REQUIRE_EMAIL_VERIFIED=false`.
- SMTP remained configured for future password/email support paths.

Pitfall: `docker restart` does not apply changed env files. After editing env used by Docker Compose, run `docker compose up -d <service>` or recreate the service, then verify inside the container with `docker exec ... printenv KEY`.

## Stripe payment proof without charging a live card

A safe smoke can prove the backend payday path without charging a real card:

1. Validate the Stripe server key without printing it.
2. Create a fresh webhook endpoint for `https://llm.wandgx.com/webhook/stripe` and capture the signing secret server-side only.
3. Disable duplicate webhook endpoints for the same URL created during failed/partial attempts, so Stripe does not deliver duplicate events.
4. Store these VM300 LLM billing settings without printing values:
   - `billing.enabled=true`
   - `billing.min_topup_usd=5`
   - `billing.stripe_secret_key=<set>`
   - `billing.stripe_webhook_secret=<set>`
   - optional `billing.stripe_webhook_endpoint_id=<we_...>`
5. Prove the portal top-up form returns a `303` redirect to `https://checkout.stripe.com/...` with a `cs_live_...` Checkout Session.
6. Generate a Stripe-format `checkout.session.completed` JSON event locally, sign it with the installed webhook signing secret (`t=<timestamp>,v1=<hmac_sha256(timestamp.payload)>`), and POST it to `/webhook/stripe`.
7. Re-post the same signed payload to prove replay/idempotency.
8. Post a bad signature to prove `400`.
9. Prove zero-credit user `429`; credited user `200` and debits.
10. Revoke temporary proof API keys.

Report clearly: this proves live Checkout creation and backend crediting, but **does not mean a real card was charged**. The first real buyer completing Checkout is the first actual charge event.

## Local proof pitfalls

- The LLM session cookie is `Secure`, so a raw `http://127.0.0.1:9090` urllib/local probe may receive a session cookie but not send it back automatically. Use public HTTPS for browser proof, or manually set the Cookie header in local LAN smoke scripts when probing from the host.
- If login appears to work but the next local request redirects to `/login`, inspect the cookie `secure` flag before assuming auth failed.
- If central Better Auth login returns “Email is not verified in central identity,” either prove inbox verification or intentionally turn off the verification gate for launch and record the product decision.

## Final packet update pattern

When the proof passes, update both:

- `evidence/self-service-launch-readiness-YYYY-MM-DD.md`
- `gtm-readiness-and-blockers.md`
- `MEDIA_PACKET.md`

Then regenerate:

- `asset-manifest.json`
- `sha256sums.txt`
- packet zip

Run a text scan for secrets and explicitly excluded product-lane terms before delivery.
