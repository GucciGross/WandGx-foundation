# WandGx post-launch quickfix pattern — source reconcile, SET root, Stripe RAK

Use this after a self-service launch pass when the product is already live but the remaining items are quick hardening tasks before media or broader promotion.

## Pattern from 2026-07-04 launch pass

### 1. Reconcile live archive patches without overwriting newer source

VM deploy archives can diverge from canonical source. Do **not** blindly copy the entire live file back into source when the source has moved forward.

Observed case:

- Live VM300 `workspace-shell.html` still used the older static shell.
- Canonical WandGx-vNext `origin/main` had advanced to the newer React workspace shell.
- Correct action: preserve the newer React shell and apply only the compatible launch auth conversion fixes.

Safe sequence:

1. Copy live files to `/tmp/...` for comparison.
2. Compare hashes and targeted diffs.
3. Pull/rebase the source repo before pushing.
4. If conflicts show source moved forward, keep the newer architecture and reapply only the minimal behavior fix.
5. Run syntax checks for changed JS/MJS files.
6. Commit a small source-reconcile patch and push.

Proof used:

- WandGx-vNext pushed commit: `1d95d62 Preserve launch auth conversion fixes`.
- Checks: `node --check apps/web/src/shell/wandgx-real-build.mjs` and `node --check scripts/local-dev-138.mjs`.

### 2. SET API root fix

If `https://api.trainwithset.com/` returns 404 while `/docs` and `/openapi.json` work, add a small JSON root to `SET-backend/app/main.py` rather than changing route/proxy topology.

Known-good root response:

```json
{
  "service": "SET Backend API",
  "status": "ok",
  "docs": "/docs",
  "openapi": "/openapi.json",
  "health": "/api/system/health"
}
```

Safe deploy sequence on VM301:

1. Back up `/opt/apps/SET/SET-backend/app/main.py` under `/opt/apps/SET/.hermes-backups/<utc>/`.
2. Copy patched file.
3. Run `python3 -m py_compile SET-backend/app/main.py`.
4. Rebuild/recreate only backend: `docker compose build backend && docker compose up -d backend`.
5. Wait for `set-backend-1` healthy.
6. Verify LAN root JSON and public root `200`.

Proof used:

- SET pushed commit: `e6041ea Add SET API root metadata response`.
- Public root: `https://api.trainwithset.com/` returned 200.

### 3. Stripe restricted API key hardening

Do not promise the agent can silently replace a live Stripe secret with a restricted API key.

Stripe’s RAK flow is Dashboard-driven:

- Create from Stripe Dashboard API keys page.
- Choose permissions interactively.
- Complete Dashboard/2FA verification.
- Key value is shown once and must be saved then.

There is no safe standard server-side Stripe API path to create and retrieve a live RAK without the interactive Dashboard/2FA step.

For WandGx LLM credit top-up, the current live checkout/webhook path can remain launch-valid if already proven. The RAK replacement is a security-hardening follow-up:

1. User creates `wandgx-llm-credit-topup-live` RAK in Dashboard.
2. Replace the current VM300 LLM billing server key with the RAK without printing it.
3. Rerun checkout redirect + signed webhook + duplicate + bad-signature + zero/credited API proof.
4. Rotate/expire the old broad secret.

### 4. Packet update after quick fixes

After these quick fixes, add a concise evidence file and regenerate:

- `MEDIA_PACKET.md`
- `gtm-readiness-and-blockers.md`
- `asset-manifest.json`
- `sha256sums.txt`
- packet zip

Run scans for secrets and explicitly excluded product-lane terms before delivery.
