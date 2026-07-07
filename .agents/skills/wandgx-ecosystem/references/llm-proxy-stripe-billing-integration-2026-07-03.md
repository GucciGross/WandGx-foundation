# LLM Proxy Stripe/Billing Integration Inspection (2026-07-03)

Use this when asked to inspect or verify the WandGx LLM app (`llm.wandgx.com`, VM300 `/opt/apps/LLM`) billing/Stripe integration without modifying files/services or exposing secrets.

## Scope and source of truth

- Runtime: VM300 `/opt/apps/LLM`, container `llm-proxy` on host port `9090`, public `https://llm.wandgx.com`.
- App DB: SQLite analytics DB (`/app/data/analytics.db` in container, `/opt/apps/LLM/data/analytics.db` on host).
- Stripe config is DB-backed in the `settings` table, not direct `STRIPE_*` env vars.
- Do not print secret values. Report empty/set status only, or lengths if needed.

## Exact DB-backed settings keys

Billing settings seeded by `src/llm_proxy/settings_store.py`:

- `billing.enabled` — `true` enforces credit checks and exposes billing/card UI paths.
- `billing.stripe_secret_key` — Stripe API key used for customer and Checkout Session creation.
- `billing.stripe_webhook_secret` — Stripe webhook signing secret used to verify `Stripe-Signature`.
- `billing.stripe_publishable_key` — stored/displayed but not critical to server-side checkout flow.
- `billing.min_topup_usd` — minimum credit top-up amount.

Pricing settings:

- `pricing.<model>` — JSON object: `{ "input": USD_per_1M_tokens, "output": USD_per_1M_tokens }`.

Relevant schema fields:

- `users.credit_balance`
- `users.total_spend`
- `users.stripe_customer_id`
- `transactions.type` (`credit`, `debit`, `refund`)
- `transactions.amount_usd`
- `transactions.description`
- `transactions.stripe_ref`
- `request_logs.cost_usd`

## Routes and behavior

Admin/user routes in `src/llm_proxy/routes_web.py`:

- `GET /admin/settings` — admin settings form.
- `POST /admin/settings` — saves billing settings. Blank Stripe key fields keep existing values.
- `POST /admin/settings/pricing/{model}` — updates `pricing.<model>`.
- `POST /admin/users/{user_id}/quota` — sets RPM, daily token quota, and credit balance.
- `GET /admin/billing` — revenue/spend/transactions dashboard.
- `GET /portal/billing` — user balance, transactions, top-up form.
- `POST /portal/billing/topup` — creates Stripe Checkout Session and redirects.
- `POST /webhook/stripe` — unauthenticated Stripe webhook; security relies on signature verification.
- `GET /portal/payments` — payment-method options page.

Checkout behavior in `src/llm_proxy/billing.py`:

- `create_checkout_session(user, amount_usd, success_url, cancel_url)` requires `billing.stripe_secret_key`.
- Creates/reuses Stripe customer; stores `users.stripe_customer_id`.
- Creates one-time USD Checkout Session with metadata:
  - `metadata[user_id]`
  - `metadata[amount_usd]`
- Success/cancel URLs are based on runtime `PUBLIC_BASE_URL`, so production should use `https://llm.wandgx.com`.

Webhook behavior in `src/llm_proxy/billing.py`:

- Requires both `billing.stripe_secret_key` and `billing.stripe_webhook_secret`.
- Verifies `Stripe-Signature` using HMAC-SHA256 over `t.payload`.
- Enforces a 5-minute freshness window.
- Handles `checkout.session.completed` only.
- Extracts `metadata.user_id` and `metadata.amount_usd`.
- Credits the user via `credit_user`, which increments `users.credit_balance` and inserts a `transactions` credit row.
- Uses event id (or checkout session id fallback) as `transactions.stripe_ref`.
- Duplicate delivery is skipped if a transaction already exists with the same `stripe_ref`.
- Bad/missing signatures or missing webhook secret return HTTP 400 and must not credit the account.

API billing behavior in `src/llm_proxy/routes.py` and `billing.py`:

- `check_quota()` blocks DB users with `429 quota_exceeded` when `billing.enabled=true` and `credit_balance <= 0`.
- Non-stream chat completions calculate cost from public model pricing and debit via `debit_user()` after a successful request.
- Debit inserts a negative `transactions` row and increments `users.total_spend`.

## Important pitfall discovered

If `billing.enabled=true` but the Stripe settings are empty, user billing/card UI can appear available because templates check `billing.enabled`; however, `/portal/billing/topup` will fail Checkout creation and redirect to `/portal/billing?status=error`. When reporting readiness, distinguish:

- billing enforcement enabled, versus
- Stripe checkout fully configured.

## Safe inspection snippets

Use redacted/status-only DB inspection. Never select raw secret values in output.

```bash
ssh root@192.168.1.248 'cd /opt/apps/LLM && python3 - <<"PY"
import sqlite3
con = sqlite3.connect("data/analytics.db")
con.row_factory = sqlite3.Row
sensitive = {"billing.stripe_secret_key", "billing.stripe_webhook_secret", "billing.stripe_publishable_key"}
for r in con.execute("select key,value from settings where key like 'billing.%' order by key"):
    k, v = r["key"], r["value"] or ""
    if k in sensitive:
        status = "<empty>" if not v.strip() else f"<set length={len(v)}>"
    else:
        status = v
    print(f"{k}={status}")
PY'
```

Check selected non-secret runtime env from the container:

```bash
ssh root@192.168.1.248 'python3 - <<"PY"
import json, subprocess
inspect = json.loads(subprocess.check_output(["docker", "inspect", "llm-proxy"], text=True))[0]
want = {"PUBLIC_BASE_URL", "ANALYTICS_DB", "PROXY_HOST", "PROXY_PORT", "CENTRAL_AUTH_ENABLED", "COMPANY_IDENTITY_URL", "BETTER_AUTH_URL"}
for e in inspect.get("Config", {}).get("Env", []):
    if "=" in e:
        k, v = e.split("=", 1)
        if k in want:
            print(f"{k}={v}")
print(inspect.get("NetworkSettings", {}).get("Ports", {}))
PY'
```

## Verification checklist

1. Confirm runtime `PUBLIC_BASE_URL=https://llm.wandgx.com` and DB path points at `/app/data/analytics.db`.
2. Confirm `billing.enabled=true` only means credit enforcement is on; separately confirm Stripe keys/secrets are set without printing them.
3. In Stripe Dashboard configure webhook URL `https://llm.wandgx.com/webhook/stripe` for `checkout.session.completed` and store the webhook signing secret in `billing.stripe_webhook_secret`.
4. Login as test user and post `amount >= billing.min_topup_usd` to `/portal/billing/topup`; expect `303` to Stripe Checkout.
5. Complete a test payment; webhook should return `{ "received": true, "handled": true }`.
6. Verify DB state without secrets:
   - `users.credit_balance` increased by paid amount.
   - `users.stripe_customer_id` set.
   - `transactions` has a `credit` row with positive `amount_usd` and `stripe_ref` set.
7. Replay same event; expect duplicate skipped and no second credit.
8. Negative checks: bad/missing `Stripe-Signature` returns 400; zero-credit user with billing enabled gets API `429 quota_exceeded`; after credit, a successful non-stream completion creates a debit transaction.
