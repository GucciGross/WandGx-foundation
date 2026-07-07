# Unguarded self-service launch gates — 2026-07-03

Use this when the user asks if WandGx is ready for **fully unguarded self-service launch**, **real users**, or **real payday**. This is stricter than controlled/concierge GTM.

## Decision labels

- **Controlled real-user onboarding ready**: public routes and a verified campaign path work; humans can onboard/close customers manually.
- **Fully unguarded self-service ready**: a cold user can discover, sign up, verify, sign in, create a product session, build, receive a usable artifact/preview, and pay/top up without staff help.
- **Real automatic payday ready**: a public user can complete checkout/payment, a signature-verified webhook credits the account, replay is idempotent, bad signatures fail, and paid/credited usage succeeds while zero-credit usage fails closed.

Do not collapse these into one “ready” verdict.

## WandGx vNext auth/conversion ownership

Production deploy root on VM300:

- `/opt/apps/WandGx-vNext`
- public web container: `wandgx-vnext-web-1`
- web command serves `apps/web` through `scripts/local-dev-138.mjs`
- deployed archive is not the canonical git source; reconcile live patches back to source later.

Primary files:

- Route aliases: `/opt/apps/WandGx-vNext/scripts/local-dev-138.mjs`
- Landing CTAs: `/opt/apps/WandGx-vNext/apps/web/index.html`
- Landing CSS: `/opt/apps/WandGx-vNext/apps/web/src/landing/home.css`
- Workspace top-nav/auth prompt: `/opt/apps/WandGx-vNext/apps/web/workspace-shell.html`
- Visible modal auth behavior: `/opt/apps/WandGx-vNext/apps/web/src/shell/wandgx-real-build.mjs`
- Workspace auth CSS: `/opt/apps/WandGx-vNext/apps/web/src/shell/wandgx-real-build.css`
- Legacy/static account-tab code may exist but is not the active modal path unless imported by the shell.

## Auth/conversion hardening pattern

For unguarded launch, prove all of these:

1. `/register`, `/signup`, and `/sign-up` return 200 and auto-open visible Create account.
2. `/login`, `/signin`, and `/sign-in` return 200 and auto-open visible Sign in, or redirect cleanly to an equivalent sign-in path.
3. Homepage has both Sign in and Create account, not only Create account.
4. Public create-account CTAs use canonical `/register`, not old `#account-auth-tab-signup` hash links to hidden/static tabs.
5. Workspace Sign in/Register controls are href-capable fallbacks (`/app?intent=signin`, `/register`) with JS intercept for modal behavior.
6. Header Register opens Create account; header Sign in opens Sign in.
7. Browser console has no JS errors on checked auth routes.
8. Unauthenticated protected actions still return 401.

Minimal implementation pattern used live:

- Add route aliases for login/signin/sign-in in `PUBLIC_WORKSPACE_ROUTE_ALIASES`.
- Replace `signupRequestedByLocation()` with a function that returns requested auth step for both signup and signin intents/paths.
- Intercept Sign in/Register anchor clicks with `event.preventDefault(); showAuth(...)`.
- Keep anchor `href` fallbacks for no-JS/crawler/basic browser behavior.

## Email verification proof gate

SMTP config status is not enough. For full unguarded launch, prove one of:

- owned real inbox receives verification email/code, then verify -> sign in -> product session -> build; or
- owner explicitly approves disabling email verification for launch, and the no-verification sign-up path creates an immediate session.

Disposable inbox failures are not definitive deliverability proof, but they also do not clear the gate. If disposable inboxes fail, request/obtain an owned real inbox or change verification policy intentionally.

For central identity, inspect without printing secrets:

- `COMPANY_IDENTITY_EMAIL_VERIFICATION_ENABLED`
- `COMPANY_IDENTITY_MAIL_DELIVERY_VERIFIED`
- SMTP host/port present
- SMTP user/pass set status only
- SMTP auth verify can be checked inside `platform-company-identity`, but inbox delivery still needs proof.

## Account/build proof gate

After account verification is satisfied, prove the product chain:

1. sign-up endpoint 200
2. sign-in 200
3. `/api/account/product-session` 201
4. unauthenticated `/v1/projects` returns 401
5. authenticated project create 201
6. authenticated content save 201
7. authenticated app build 201 with `status=completed`
8. hosted generated app URL fetches 200

If using an operator-side DB verification shim to test downstream behavior, label it clearly: it proves post-verification product flow, **not** real-user email delivery.

## Payment/payday proof gate

For real automatic payday, inspect VM300 `/opt/apps/LLM/data/analytics.db` settings without printing values:

- `billing.enabled`
- `billing.min_topup_usd`
- `billing.stripe_secret_key`
- `billing.stripe_webhook_secret`
- `billing.stripe_publishable_key`

`billing.enabled=true` only proves credit enforcement/gating, not usable checkout. Full Stripe proof requires:

1. Stripe secret/publishable/webhook secrets installed.
2. Webhook endpoint configured: `https://llm.wandgx.com/webhook/stripe`.
3. logged-in test user posts top-up amount >= min and gets 303 to Stripe Checkout.
4. test payment completes.
5. webhook credits `users.credit_balance`, sets/uses customer id, and creates positive transaction with Stripe ref.
6. replay of same event does not double-credit.
7. missing/bad `Stripe-Signature` returns 400 and does not credit.
8. zero-credit API user gets 429; credited user succeeds and debits.

## Reporting rule

If either email verification delivery or Stripe checkout is unproven, say:

> Controlled real-user onboarding: yes. Fully unguarded self-service + real automatic payday: no.

Then list exact P0 blockers and what proof clears each one. Do not let a working public route or a successful post-verification build smoke become a full self-service launch stamp.
