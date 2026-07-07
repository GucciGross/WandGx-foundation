# WandGx vNext browser auth-state flow debug — 2026-07-05

Use this when vNext API login/session routes succeed but the browser UI only flickers/stutters and does not enter the authenticated workspace.

## Durable lesson

Do not stop at API auth success. For vNext, prove which browser shell is actually deployed and which client code owns the auth state. The deployed VM archive can contain both a legacy static shell and a newer React shell, and checks/comments may claim one is source-of-truth while production serves the other.

## Read-only investigation path

On VM300 deployed archive:

```bash
cd /opt/apps/WandGx-vNext
# Identify deployed serving mode and root.
docker compose ps
docker inspect wandgx-vnext-web-1 --format 'Cmd={{json .Config.Cmd}} Entrypoint={{json .Config.Entrypoint}} Image={{.Config.Image}}'

# Compare source and dist shells.
python3 - <<'PY'
from pathlib import Path
for fp in ['apps/web/workspace-shell.html','apps/web/dist/workspace-shell.html']:
    txt = Path(fp).read_text(errors='replace')
    print(fp)
    for marker in ['<div id="wandgx-app"','/src/react/main.tsx','data-testid="wandgx-real-build-app"','workspaceShell-', 'data-testid="auth-modal"']:
        print(' ', marker, marker in txt)
PY

# Check live public route without mutating auth state.
tmp=$(mktemp)
curl -sS -A 'Mozilla/5.0' https://wandgx.com/app -o "$tmp"
python3 - "$tmp" <<'PY'
import sys
html=open(sys.argv[1],encoding='utf-8',errors='replace').read()
for marker in ['<div id="wandgx-app"','/src/react/main.tsx','data-testid="wandgx-real-build-app"','workspaceShell-', 'data-testid="auth-modal"']:
    print(marker, marker in html)
print('bytes', len(html))
PY
rm -f "$tmp"
```

Browser-side confirmation without credentials:

- Navigate to `https://wandgx.com/app?intent=signin`.
- Inspect DOM state after bootstrap: `data-testid="wandgx-real-build-app"`, legacy modal, and legacy workspace composer indicate the old static shell is live.
- If the page contains `<div id="wandgx-app"></div>` and a React bundle, use the React flow checks below instead.

## Legacy static shell root cause pattern

Files/functions to inspect:

- `apps/web/workspace-shell.html`
  - If it includes `src="./src/shell/wandgx-real-build.mjs"` and static `data-testid="wandgx-real-build-app"`, production is using the legacy static shell.
  - If it lacks `<div id="wandgx-app"></div>` and `/src/react/main.tsx`, the React auth shell is not actually active even if checks/comments say it is.
- `apps/web/src/shell/wandgx-real-build.mjs`
  - `passwordSignIn()` calls `POST /api/auth/sign-in/email`, then `createProductSession()`.
  - `createProductSession()` calls `POST /api/account/product-session` and stores the beta token.
  - `setSession(account, betaSession)` only updates `state.account`, `state.betaSession`, `app.dataset.sessionState`, labels, and status text.
  - It does **not** set `data-beta-session-state`, `data-auth-shell-state`, `data-auth-scroll-lock`, `data-auth-app-surface`, command gate state, or dispatch `wandgx:account-session-ready`.
- `apps/web/src/shell/account-auth-flow.mjs`
  - Has the correct gate logic in `renderAuthenticated()`, `setWorkspaceSurfaceGate()`, `setWorkspaceCommandGate()`, and `createProductSession()` dispatches `wandgx:account-session-ready`.
  - This module may be dormant if not imported by `workspace-shell.html`.

Smallest safe patch for live legacy shell:

1. Extend `setSession(account, betaSession)` in `apps/web/src/shell/wandgx-real-build.mjs` to mirror the gate updates from `account-auth-flow.mjs`:
   - app/root `data-session-state` authenticated/signed-out
   - compatibility shell `data-beta-session-state` authenticated/signed-out
   - `data-auth-shell-state` unlocked/locked
   - `data-auth-scroll-lock` false/true
   - `data-auth-app-surface` available/hidden
   - command palette `data-command-auth-state` authenticated/locked and enable/disable command input/sign-out controls
   - hide Sign in/Register and show Sign out/account label when signed in
2. In legacy `createProductSession()`, after successful `setSession()`, dispatch `wandgx:account-session-ready` with the product-session payload so dormant compatibility controllers can hydrate.
3. Add a focused check that signs in through the legacy modal and asserts these DOM gates remain authenticated after the product-session response.

## React shell latent patch pattern

If production is switched to the React shell:

- `apps/web/src/react/App.tsx` currently can mark signed-in after `GET /api/account/session` without minting a product session.
- `packages/product-auth/src/product-auth.mjs` authenticates product API calls from the `x-wandgx-account-session` / `x-wandgx-beta-identity-session` headers, not from the browser cookie directly.
- `apps/web/src/react/api/client.ts` should read beta token from localStorage, sessionStorage, and then the `wandgx_vnext_beta_session_token` cookie fallback.

Small React-safe patch:

1. In `App.tsx resolveSession()`, when `/api/account/session` returns an account, call `createProductSession(false)`, store the returned session, then set `sessionState='signed-in'`.
2. In `api/client.ts sessionToken()`, fallback order should match `beta-api-origin.mjs`: localStorage -> sessionStorage -> cookie.
3. For social sign-in in `AuthModal.tsx`, if `/api/auth/sign-in/social` returns a URL, redirect the browser; do not merely call `onAuthenticated()`.

## Reporting guidance

For read-only auth-flow investigations, report:

- exact deployed shell (legacy static vs React) proved from live HTML/dist/container command
- exact files/functions that own the current auth state
- why API success is insufficient for UI unlock
- smallest safe patch only; do not edit/deploy unless explicitly requested
