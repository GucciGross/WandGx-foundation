# WandGx vNext live app auth/UI closeout pattern

## Why this exists

A prior session over-claimed login success from API proof while the user still saw Google OAuth failure and a weak mobile logged-in UI. This reference captures the durable closeout pattern for WandGx vNext `/app`.

## Active production areas

On VM300, live vNext runs from `/opt/apps/WandGx-vNext` with public routes served by the web container and auth proxied through the API container. The post-login app may be the static workspace shell, not React.

Inspect these before editing UI/auth state:

- `apps/web/workspace-shell.html`
- `apps/web/src/shell/wandgx-real-build.mjs`
- `apps/web/src/shell/wandgx-real-build.css`
- `apps/web/dist/workspace-shell.html`
- built hashed `dist/assets/workspaceShell-*.js/css`
- `apps/api/src/account-auth.mjs`
- central identity on VM302: `/srv/platform/identity/source/apps/company-identity/src/auth.ts` and `config.ts`

## Auth closeout proof

Do not report “login fixed” until these boundaries are separated:

1. **Regular email/password API:** sign-up/sign-in/session/product-session endpoints succeed.
2. **Rendered browser UI:** after UI sign-in, profile/account identity is visible, Sign in/Register are hidden, Sign out is visible, and workspace is not gated.
3. **Google social:** generated Google URL uses an authorized callback, state cookie scope matches callback host, and fake callback with same cookie jar returns `invalid_code` rather than `state_mismatch`.

## Google OAuth decision

If app-host callback (`https://wandgx.com/api/auth/callback/google`) causes `redirect_uri_mismatch`, do not keep asserting state is fixed. Either register that exact URI in Google Cloud or use the central registered callback and make Better Auth state cookies cross-subdomain (`Domain=.wandgx.com`).

## UX closeout proof

For mobile post-login, profile clarity is part of functional auth proof. The user expects to know which profile is logged in. Good vNext mobile state should include:

- profile chip/avatar/display name/email
- `Profile / Projects / Settings` or similar workspace/account affordances
- CLI/space build cockpit feel when that direction is requested
- no simultaneous logged-out and logged-in header controls

## Reporting

Use exact boundary language:

- `API auth works`
- `browser UI login works`
- `Google OAuth state/callback works`
- `source reconciled` vs `live archive patched only`

If source reconciliation has not happened, say so; deployed archive changes are not automatically durable source-of-truth changes.