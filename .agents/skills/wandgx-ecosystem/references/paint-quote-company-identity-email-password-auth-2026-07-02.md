# Paint Quote company-identity email/password auth pitfall — 2026-07-02

## Trigger

Use this reference when Paint Quote is in `company-identity` mode and the auth UI, login/register flow, or password reset flow is being changed.

## Lesson

Do not replace Paint Quote's customer-facing auth screens with a company-identity-only button. In production, the prior `Continue with Company Identity` screen redirected to the central identity root/status page and left users without a usable support/login path. The correct product surface is still ordinary email/password auth, even though the backend proxies those calls through central identity.

## Correct shape

- `/login` shows the normal PainterQuote email/password form:
  - Email Address
  - Password
  - Remember me
  - Forgot password
  - Sign In
  - Sign up here
- `/register` shows the normal account form:
  - Full Name
  - Email Address
  - Password
  - Confirm Password
  - Create Account
- `/reset-password` shows the normal password reset form:
  - Email Address
  - Send Reset Link
- No customer-facing auth screen should show a sole `Continue with Company Identity` button or a `Company Sign In` / `Company Account` blocker.

## Backend boundary

In `company-identity` mode, keep the UI normal but route the operations through the app-owned proxy:

- Login: `POST /api/company-identity/auth` with `action: "password"`
- Register: `POST /api/company-identity/auth` with `action: "register"`
- Reset request: `POST /api/company-identity/auth` with `action: "request-password-reset"`
- Reset completion: `POST /api/company-identity/auth` with `action: "reset-password"`

The proxy forwards to central Better Auth endpoints and exchanges the session cookie for a JWT when needed. Do not initialize local Better Auth routes in production company-identity mode, but also do not remove email/password UX.

## Regression tests to add/keep

- Login component renders email/password fields and does not render `Continue with Company Identity`.
- Register component renders email/password account creation and does not render `Continue with Company Identity`.
- ResetPassword component renders email reset form and does not render `Continue with Company Identity`.
- Auth store in company-identity mode calls `/api/company-identity/auth` for register/login/reset actions.
- Server proxy forwards password reset requests to central identity with the PainterQuote `/reset-password` return URL.

## Live verification pattern

After deploy, verify all three public auth routes in browser snapshots or DOM checks:

- `https://painter.wandgx.com/login`
- `https://painter.wandgx.com/register`
- `https://painter.wandgx.com/reset-password`

Also verify the public bundle no longer contains the dead company-only strings:

- `Company Sign In`
- `Continue with Company Identity`
- `Company Account`

Then verify health remains:

- `status=healthy`
- `authProvider=company-identity`
- `billingEnabled=true`
