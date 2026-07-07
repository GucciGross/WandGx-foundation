# WandGx unguarded self-service launch readiness pattern — 2026-07-03

Use this when the user asks whether WandGx is ready for **fully unguarded self-service launch**, **real users**, or **real payday**. This is stricter than controlled GTM.

## Core distinction

Do not equate controlled GTM approval with unguarded self-service approval.

- **Controlled launch**: tested campaign path works, first users can be onboarded with human/concierge support.
- **Unguarded self-service launch**: unknown real users can sign up, verify, sign in, build, reach a hosted artifact, pay/top up if money is claimed, and recover from common auth/payment failures without operator action.

## Required gates before saying “fully ready”

1. **Public auth routes**
   - `/register`, `/signup`, `/sign-up`, `/app`, `/build`, and top-nav Sign in/Register show visible account surfaces with no console errors.
   - Header Register must open Create account; Header Sign in must open Sign in.

2. **New-user email/verification path**
   - Use an owned real inbox, not only disposable inboxes.
   - Prove: sign-up -> email/code received -> verify -> sign in after reload -> product session created.
   - If email verification is intentionally disabled for launch, document that as an explicit product decision and prove immediate session creation.
   - SMTP `verify()` success is not enough; inbox receipt is the proof.

3. **Authenticated product/build path**
   - Prove unauthenticated protected routes return 401.
   - Prove authenticated project create, content save, app build, and hosted artifact fetch.
   - A DB/manual verification shim can validate downstream build behavior, but it does **not** clear the real-user verification gate.

4. **Payment/payday path**
   - If claiming real automatic payday or self-serve paid credits, prove Stripe or equivalent checkout end-to-end.
   - Billing enforcement (`billing.enabled=true`) is not checkout readiness.
   - For VM300 LLM billing, inspect DB-backed settings in `/opt/apps/LLM/data/analytics.db` and require non-empty:
     - `billing.stripe_secret_key`
     - `billing.stripe_webhook_secret`
     - `billing.stripe_publishable_key`
   - Prove checkout session creation, successful payment, webhook signature validation, balance credit, replay idempotency, bad-signature 400, zero-credit 429, and credited-user success.

5. **Copy/media claim safety**
   - Until all above pass, label as controlled launch or conditional self-service, not full unguarded launch.
   - Do not claim self-serve card top-up, instant production delivery, or automated payday unless payment and build gates are proven.

## Useful smoke pattern

- Public route fetch: route status and source/copy leakage.
- Browser check: visible forms and console errors.
- API smoke:
  - `POST /api/auth/sign-up/email`
  - verify through real inbox or explicit launch policy
  - `POST /api/auth/sign-in/email`
  - `POST /api/account/product-session`
  - unauthenticated `POST /v1/projects` -> 401
  - authenticated `POST /v1/projects` -> 201
  - authenticated content save -> 201
  - authenticated app build -> 201 completed
  - hosted artifact URL -> 200

## Pitfalls from the session

- Disposable inboxes may fail to receive mail even when SMTP accepts delivery. Treat that as inconclusive for deliverability; use an owned inbox for launch proof.
- Operator-side DB verification can unblock downstream smoke tests, but must be clearly labeled as a shim.
- A UI that says “Account created. Sign in to continue” can still be launch-blocking if sign-in fails because verification is required. Prefer moving the user directly into the verification-code step.
- Live archive patches on VM300 should be reconciled back into canonical source after emergency launch fixes.
