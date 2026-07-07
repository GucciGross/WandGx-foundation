# LLM Stripe billing and credit top-up integration

Session-derived reference from the VM300 `/opt/apps/LLM` billing inspection.

## Runtime shape

- App: VM300 `/opt/apps/LLM`
- Container: `llm-proxy`
- Public URL: `https://llm.wandgx.com`
- Host port: `9090` -> container `8000`
- DB: `/opt/apps/LLM/data/analytics.db` mounted as `sqlite:////app/data/analytics.db`

## DB-backed settings

Stripe is configured through the `settings` table, not direct `STRIPE_*` env vars:

- `billing.enabled`
- `billing.stripe_secret_key`
- `billing.stripe_webhook_secret`
- `billing.stripe_publishable_key`
- `billing.min_topup_usd`
- `pricing.<model>` as JSON: `{"input": USD_per_1M, "output": USD_per_1M}`

Important pitfall: `billing.enabled=true` alone makes card top-up UI appear possible, but Checkout still fails unless `billing.stripe_secret_key` and webhook settings are present.

## Routes

- Admin settings: `GET /admin/settings`
- Save billing settings: `POST /admin/settings`
- User billing page: `GET /portal/billing`
- User top-up: `POST /portal/billing/topup`
- Stripe webhook: `POST /webhook/stripe`

## Checkout behavior

`POST /portal/billing/topup` requires:

- logged-in user
- `billing.enabled=true`
- amount >= `billing.min_topup_usd`
- non-empty `billing.stripe_secret_key`

Checkout uses `PUBLIC_BASE_URL` for returns:

- success: `/portal/billing?status=success`
- cancel: `/portal/billing?status=cancel`

Checkout metadata includes:

- `user_id`
- `amount_usd`

The app creates/reuses a Stripe customer and stores `users.stripe_customer_id`.

## Webhook behavior

Configure Stripe webhook URL:

- `https://llm.wandgx.com/webhook/stripe`

Required event:

- `checkout.session.completed`

The handler requires:

- `billing.stripe_secret_key`
- `billing.stripe_webhook_secret`

It verifies the Stripe signature, applies a 5-minute timestamp tolerance, uses event/session id as `transactions.stripe_ref`, skips duplicate refs, then credits `users.credit_balance` and inserts a positive `transactions` row.

## Verification checklist

1. Confirm `billing.stripe_secret_key` and `billing.stripe_webhook_secret` are non-empty without printing values.
2. Login as a test user.
3. Post `/portal/billing/topup` with amount >= min; expect 303 redirect to Stripe Checkout.
4. Complete a test-mode payment.
5. Confirm user balance increased, `stripe_customer_id` is set, and a positive `transactions` credit row exists.
6. Replay the same event; confirm no second credit is applied.
7. Confirm bad or missing `Stripe-Signature` returns 400 and no credit.
8. Confirm zero-credit user still gets API `429 quota_exceeded` before top-up and can call `/v1/chat/completions` after credit.
