# SET authenticated browser-console watchdog triage — 2026-07-04

Use when the user reports SET browser-console errors or says the self-healing/watchdog should catch what they see in DevTools.

## Durable lesson

Server/container watchdogs do not see browser console errors. Public route QA can also miss authenticated-only frontend runtime failures. For SET, run an authenticated Playwright browser watchdog in addition to server log/HTTP checks.

Proven script path:

- `~/.hermes/scripts/set_browser_console_watchdog.py`
- state: `~/.hermes/state/set_browser_console/`
- evidence: `~/.hermes/qa/set-browser-console-watchdog/`
- cron: `SET authenticated browser-console watchdog`, every 10m, `no_agent=true`

The script logs every browser console warning/error, page error, request failure, and HTTP >=400 response from an authenticated disposable QA session. It emits compact Telegram alerts only for new/deduped incidents.

Coverage pitfall found on 2026-07-04: authenticated route watchdogs must include direct workspace aliases, not only the main app pages. Add/keep `/home`, `/welcome`, `/workspace`, and `/workspaces` in the authenticated route list so nginx allow-list misses and onboarding redirect regressions are caught.

## Current SET browser errors observed

Authenticated `/welcome` produced:

```text
GET https://trainwithset.com/api/copilotkit -> 404
Failed to load resource: the server responded with a status of 404 ()
Failed to load runtime info (/api/copilotkit/info): Runtime info request failed with status 404
[CopilotKit] Error (runtime_info_fetch_failed): Error: Runtime info request failed with status 404 ... {runtimeUrl: /api/copilotkit}
Agent default not found
```

Unauthenticated/invalid login produced expected-but-still-logged browser events:

```text
POST https://trainwithset.com/api/auth/sign-in/email -> 401
Failed to load resource: the server responded with a status of 401 ()
```

Auth JWKS direct route produced:

```text
GET https://auth.trainwithset.com/api/auth/jwks -> 500
Failed to load resource: the server responded with a status of 500 ()
```

## Likely ownership

- `/api/copilotkit` 404 / `runtime_info_fetch_failed`: SET frontend runtime/proxy wiring. Check whether NPM/frontend should proxy `/api/copilotkit` to `set-copilotkit-runtime-1:4100`, or whether frontend env should point at the correct runtime URL.
- `auth.trainwithset.com/api/auth/jwks` 500 + `relation "jwks" does not exist`: SET auth Better Auth JWT/JWKS schema/migration. Check `set-auth-1` and `public.jwks` table.

## Proven production fixes applied

- `/api/copilotkit` 404: the runtime was serving CopilotKit in multi-route mode while the browser client was POSTing to the single base endpoint. In `/opt/apps/SET/copilotkit-runtime/server.js`, keep the safe `GET /api/copilotkit` metadata response and create the CopilotKit Express handler with `mode: 'single-route'` for POST. Rebuild/recreate only `copilotkit-runtime`.
- After the fix, expected probes are:
  - `GET https://trainwithset.com/api/copilotkit` -> 200 metadata
  - `POST https://trainwithset.com/api/copilotkit` with an invalid empty body -> 400 `Missing method field`, not 404
  - authenticated browser-console watchdog event count -> 0

## Guardrails

- QA/triage only unless user explicitly asks to fix/deploy.
- Do not restart `set-auth-1`, rebuild SET, apply migrations, or change NPM routes during QA-only requests.
- Store disposable QA credentials only under local Hermes state; do not print real credentials or tokens.
- Human approval remains required before production repair/deploy.
