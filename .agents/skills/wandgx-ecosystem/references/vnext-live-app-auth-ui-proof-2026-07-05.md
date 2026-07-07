# WandGx vNext live `/app` auth/UI proof pattern — 2026-07-05

Use this when WandGx vNext login appears to work at the API level but the user says the phone/browser UI still loops, stutters, or looks logged out.

## Durable lesson

Do **not** claim login is fixed from API-only proof. The live `/app` surface can be served by the static workspace shell, not the React shell you may inspect first.

For the current VM300 deploy, the real public `/app` route is primarily:

- `apps/web/workspace-shell.html`
- `apps/web/src/shell/wandgx-real-build.mjs`
- `apps/web/src/shell/wandgx-real-build.css`
- built/served as `dist/workspace-shell.html` and `assets/workspaceShell-*.{js,css}`

The React files under `apps/web/src/react/*` can typecheck/build while not being the behavior the user is testing on the phone.

## Failure shape seen

- API checks passed:
  - `/api/auth/sign-up/email` `200`
  - `/api/auth/sign-in/email` `200`
  - `/api/account/session` `200`
  - `/api/account/product-session` `201`
- The browser UI still looked broken:
  - regular login opened an email-only `Continue` step first, hiding password login behind a second step
  - UI could briefly stutter into signed-in state but still show `Sign in` / `Register`
  - `Sign out` / `Sign in` / `Register` state could be ambiguous if controls were not hidden mutually exclusively

## Root-cause checks

1. Fetch the live `/app` HTML and identify the actual bundle:

```bash
curl -ksS 'https://wandgx.com/app?verify=...' -o /tmp/wgx_live_app.html
grep -o '/assets/workspaceShell-[^" ]*\.js' /tmp/wgx_live_app.html | head -1
grep -o '/assets/workspaceShell-[^" ]*\.css' /tmp/wgx_live_app.html | head -1
```

2. Inspect the served JS/CSS bundle for real behavior, not just source guesses:

```bash
curl -ksS "https://wandgx.com$JS" -o /tmp/wgx_live_workspace.js
curl -ksS "https://wandgx.com$CSS" -o /tmp/wgx_live_workspace.css
```

3. Required live-bundle assertions:

- sign-in defaults to password/email-password, not email-only `Continue`
- the sign-in form contains both `account-auth-email` and `account-auth-password`
- after signed in, code hides Sign in/Register and shows Sign out
- header/theme CSS matches the current reference direction
- Google fake callback still returns `invalid_code`, not `state_mismatch`

Example string checks:

```python
checks = {
  'signin_default_password': "function showAuth(step = 'password')" in js or 'authStep:`password`' in js,
  'signin_form_has_email_password': 'data-auth-form="password"' in js and 'account-auth-email' in js and 'account-auth-password' in js,
  'nav_hides_signin_when_signed_in': 'dataset.sessionState' in js and 'hidden=r' in js,
  'view_switch_hidden': '.wgx-view-switch{' in css and 'display:none' in css,
  'black_topbar': 'background:#000' in css.replace(' ', ''),
  'coral_primary': '#ff5432' in css.lower(),
}
```

## Fix pattern

Patch the actual workspace shell first:

- In `wandgx-real-build.mjs`:
  - default `authStep` and `showAuth()` to `password`
  - render email + password fields together in `data-auth-form="password"`
  - on password submit, validate/read email before `passwordSignIn()`
  - on `setSession(account, betaSession)`, hide all `[data-action="open-auth"]` and `[data-action="open-register"]` when `signedIn`, and show `real-sign-out` only when signed in
  - after account cookie exists, ensure `/api/account/product-session` runs and token is stored before unlocking workspace/build calls

- In `wandgx-real-build.css`:
  - style the live header, not only React CSS
  - black background, larger app icon/wordmark, coral primary Sign in, dark slate Register/Sign out
  - hide the Chat/IDE mode switch from the mobile/header reference when it conflicts with the product packet

## Verification commands

Run all of these before telling the user it works:

```bash
# In container so the same toolchain/build path is used.
docker exec wandgx-vnext-web-1 sh -lc 'cd /workspace && node --check apps/web/src/shell/wandgx-real-build.mjs && pnpm --filter @wandgx/web build'
docker restart wandgx-vnext-web-1
curl -fsS http://127.0.0.1:31381/health
```

Then public proof:

```bash
# Live bundle proof: fetch /app HTML, then workspaceShell JS/CSS and assert strings.
# Live login proof: create throwaway email, sign out, sign in, product-session -> 201 with token/accessAllowed.
# OAuth proof: /api/auth/sign-in/social returns redirect_uri=https://wandgx.com/api/auth/callback/google; fake callback returns invalid_code not state_mismatch.
```

## Reporting rule

If the user says “it still doesn’t work,” treat prior API-only proof as insufficient. Say you are verifying the exact browser/UI flow, not that it is fixed. The final report must distinguish:

- API auth proof
- actual served `/app` bundle proof
- browser/DOM/UI proof
- public OAuth callback proof
