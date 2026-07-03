# Security and approval model

Hermes has powerful responsibilities, so the repo defaults to safe patterns.

## Approval-gated actions

- send email/SMS
- charge customer
- delete/export customer data
- run shell commands
- deploy production
- modify auth or billing

## File write scope

Generated code is restricted to configured paths via `HERMES_ALLOWED_WRITE_PATHS`.

## Secret handling

Secrets belong in `.env`, a secret manager, or CI secrets. Do not write secrets into manifests, generated crews, eval files, examples, or docs.
