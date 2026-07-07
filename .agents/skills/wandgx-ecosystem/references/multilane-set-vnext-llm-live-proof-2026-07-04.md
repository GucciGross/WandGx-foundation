# Multi-lane SET/vNext/LLM live-proof lessons — 2026-07-04

Use this reference for WandGx ecosystem background-lane work where GitHub source, VM/LXC archive deploys, and public mobile/browser proof all have to agree.

## User-facing status format

The user corrected status readability during this run. For WandGx multi-lane updates, use rich Telegram Markdown:

- clear headings
- short sections
- compact tables for lane/status/proof
- bullets over dense paragraphs
- fenced code blocks for paths, commits, process IDs, and commands
- no long unstructured wall-of-text

## SET: proof must target the exact mobile state

A broad mobile nav QA pass can falsely pass while a modal/sheet subflow is still blocked.

Durable pattern:

1. Treat a user screenshot as authoritative live evidence, even if a previous report said `0 blocked actions`.
2. Reproduce the exact UI state from the screenshot, not just the route:
   - Documents/Vault mobile
   - Add Document sheet
   - New/Upload/Cloud/Local document selector modes
   - queued/progress/Cancel action area
   - Training copilot launcher
   - fixed bottom nav active on Vault
3. Measure action/control rectangles against bottom-nav top and safe area.
4. Verify the scroll container reaches the true bottom; do not rely only on horizontal overflow or route health.
5. Save before/after screenshots and JSON probes.

Shipped pattern from this run:

- Add explicit modal/sheet/action markers/classes in `Documents.jsx`.
- Add mobile bottom clearance in global CSS for the Add Document dialog/sheet/actions.
- Hide `.set-copilot-launch` while `html[data-set-document-sheet-open]` is set, so the launcher cannot cover Cancel/Upload/Create.
- Verify both `trainwithset.com` and `set.wandgx.com` at `390x844` and `393x852`.

Known-good commit after this fix:

```text
GucciGross/SET main: 59abada7215d6b1023dc7e2b098a10d8c61ed37b
```

## SET: Drive and login persistence proof

Login persistence is not only “session cookie survives reload.” Also verify:

- logged-in users who visit the public landing/root are routed into the app/dashboard when appropriate
- `/home` reload stays authenticated
- direct `/documents` after reload stays authenticated
- protected APIs still return `401` unauthenticated

For Google Drive:

- Do not fake `connected=true` with a synthetic token.
- Prove callback routing returns to SET frontend over HTTPS, not `identity.wandgx.com`.
- Prove `GET /api/integrations/google/status` works after auth hydration.
- Prove connect returns a real Google OAuth URL with backend-created state.
- Final `connected=true` persistence requires a real user Google OAuth grant; report that honestly if not available.

## vNext: live archive fixes must be back-committed

VM300 `/opt/apps/WandGx-vNext` is an archive-style deploy tree. A live CSS fix is not durable until it is back-committed to canonical source.

Shipped pattern:

- Fix/prove live VM300 first when production is broken.
- Reconcile minimal changed files back to `GucciGross/WandGx-vNext main`.
- Prove source files are byte-identical to live fixed copies.
- Run `pnpm --filter @wandgx/web typecheck` and `pnpm --filter @wandgx/web build` before push.

Known-good mobile CSS source commit:

```text
GucciGross/WandGx-vNext main: 0a583e46172c791d9c2aa6e8f6ba43138e98b5e0
```

Caveat: mobile CSS was reconciled; a separate full landing parity pass is needed if the task is to guarantee every live landing HTML/asset file matches source.

## LLM API: hide proxy branding from users

The LLM service may still have internal module/container names containing `proxy`, but user-facing product/API/key copy should not reveal proxy branding.

Pattern:

- New user-facing API keys should use a product prefix such as `wgx_[REDACTED]`, not `sk-proxy` or anything containing `proxy`.
- Existing legacy keys must keep validating.
- Legacy prefixes displayed in the portal can be masked as `legacy-key...`.
- Public OpenAPI and AG-UI status should say `WandGx LLM API` / `wandgx-llm-api` and contain no user-facing `proxy` wording.
- Always rerun billing smokes after this change: positive-credit request debits balance; zero-credit request returns `429 quota_exceeded`.

Known-good live result from this run:

```text
New key shape: wgx_[REDACTED]
Full tests: 138 passed
Public health: https://llm.wandgx.com/health -> 200
```
