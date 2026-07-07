---
name: wandgx-ecosystem
description: Use when building, debugging, deploying, or handing off work for WandGx, WandGx vNext, Oracle/WandGx Chat, SET, central identity/Appwrite/ops, Paint Quote, or ZCode. Loads the live VM topology, production/dev URLs, source/repo rules, auth architecture, product ownership, and verification gates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [wandgx, set, oracle, zcode, proxmox, deployment, topology]
    related_skills: [wandgx-adaptive-business-os, better-auth-platform-identity, ai-coding-agents]
---

# WandGx Ecosystem

## Overview

Use this skill before doing any WandGx ecosystem work in ZCode or Hermes. It captures the current production topology, live URLs, product ownership, source/deploy boundaries, auth rules, and proof requirements.

Current direction: public production traffic no longer belongs on the old 138 workstation. Public traffic flows through Cloudflare to Nginx Proxy Manager, then to Proxmox VMs/LXC.

138 status update (2026-07-06): 138 is active again for source/dev/build/ComfyUI workflows when appropriate. Verified host is Linux Mint at `gucci@192.168.1.138` (hostname `gucci`). Do not assume old Windows paths such as `C:\\Users\\gucci`; verify current Linux repo/tool paths over SSH before using it. Do not default to the Mac mini solely because an older memory/skill said 138 was excluded.

Do not expose internal workflow names, provider names, agent names, model names, or tool names in customer UI. Use normal product language: build, repair, account, app, preview, proof, training, workspace.

## When to Use

- User asks ZCode to build on WandGx, Oracle, SET, central identity, Appwrite, Paint Quote, or shared ecosystem infrastructure.
- You need to decide which repo/service owns a change.
- You need production URLs, LAN ports, VM placement, or NPM routing.
- You need to verify whether a deployed change is live.
- You are wiring cross-app flows: Oracle -> WandGx vNext, WandGx -> SET, or apps -> central identity/Appwrite.

## Non-Negotiable Product Rules

- All customer auth surfaces must show both Sign In and Register/Create account. No guest mode.
- Do not weaken auth guards. Unauthenticated protected API/product-session routes must remain 401.
- Do not replace central Better Auth/Appwrite with local one-off auth/storage.
- Do not claim working/latest/good-to-go without scoped runtime proof.
- Committed is not deployed. Deployed is not verified. Say exactly which boundary is proven.
- Changes made on 138 or any dev/source box are not finished until they are pushed/reconciled into the production VM/runtime, deployed there, and live-verified on the public/LAN production route. Dev-box success alone is not completion.
- For non-trivial WandGx ecosystem implementation, multi-repo setup, research, deploy, or verification work, default to background agents/tracked background jobs so the user can keep talking. Foreground commands are acceptable for quick targeted checks, but long-running work should not block the main chat.
- Public UI/copy must hide internal tool/workflow/agent names.
- Design rules: no gradients, no indigo/purple primary accent, no chat bubbles, no flashing/strobing, no shadcn/card-stack slop.
- WandGx brand-board UI rule: when the user asks to match the supplied black technical WANDGX board, use black/near-black, white linework, gray dividers, and cyan/electric-blue accent only. Do **not** introduce orange/coral/flame accents into post-login WandGx UI unless the user explicitly asks for that palette.
- Favicons/app icons from the WandGx logo board must preserve the mark and avoid ugly white square backgrounds; prefer transparent outer background or solid black app-icon background with white/cyan line mark.
- Use short plain product copy. Focus on intent-first building and proof.
- For WandGx/SET marketing-page critique or GTM landing-page diagnosis, use `references/wandgx-set-landing-page-clarity-teardown-2026-07-06.md`: inspect live pages first, then diagnose customer comprehension, buyer targeting, proof, CTA friction, and overuse of internal ecosystem metaphors before suggesting code changes.
- For WandGx/SET "smoke and mirrors" repair, real-product hardening, or safe feature addition, use `references/wandgx-set-no-smoke-working-path-guardrails-2026-07-06.md`: avoid timeline/phase/slice framing, preserve a live working path, gate public claims behind verified capabilities, label demo data honestly, add feature flags/contracts/smokes, and personally verify background-agent claims with live browser/API proof before saying done.
- QA-only requests mean observe and report. Do not patch/deploy unless the user explicitly asks for fixes.

## Product Ownership

### WandGx vNext

Owns the public AI app builder/app factory:

- public landing/workspace/build UI
- app/project/build APIs
- managed build/worker runtime
- preview URLs
- app factory / repair / proof loops

### Oracle / WandGx Chat

Owns the chat/product assistant surface:

- Oracle chat UI
- user conversation flow
- bridge calls into WandGx vNext for app/project/build actions
- bridge calls into SET for training handoffs

Oracle/WandGx Chat model-route support pattern: production chat lives in VM300 `/opt/apps/WandGx-chat`, container `wandgx-chat-web-1`, public host `chat.wandgx.com` / `oracle.wandgx.com`. The active CopilotKit runtime is `apps/web/src/app/api/copilotkit/route.ts`; user-visible model cards live in `apps/web/src/app/lib/models.ts`; public model artwork belongs under `apps/web/public/models/`. As of 2026-07-06, public Oracle wording/model selection must be **Oracle-1 only**: do not reintroduce `oracle-diffusion`, diffusiongemma, diffusion copy, provider names, `oracle-tool-proxy` / tool-proxy labels, or second public model cards. If internal proxy/tool routes exist, keep them completely hidden from customer dashboards, selectors, model lists, rendered chat UI, and public/API model metadata. `oracle-1` in the LLM proxy must use the local high-context Qwen/Ollama model (`oracle-1-proxy:latest` on the LLM host) for final responses; GLM-5.2/Z.ai may exist only as hidden support/council, not as the final answer backend. A warm Ollama model is not enough proof: inspect the LLM proxy DB-backed `virtual_models.backends` and provider logs to prove final routing. If only one public model exists, render the chat header model area as static identity rather than a clickable selector. Use `references/oracle-1-local-qwen-final-routing-and-selector-cleanup-2026-07-06.md` for the exact repair and verification sequence. Run `docker compose build web`, a focused route/model test or build, `docker compose up -d web`, then verify `https://chat.wandgx.com/`, `/api/oracle/agui-status`, model assets, no public diffusion strings, and endpoint reachability from both VM300 and the chat container. If a local model endpoint is a LAN/Tailscale address, VM300 must be able to reach it; code deployment alone will not make calls work.

Logged-in dashboard Oracle-only model rule: when the user asks to remove all other models from user dashboards, this spans both WandGx Chat and WandGx vNext. Use `references/oracle-1-only-user-dashboard-models-2026-07-06.md`. Durable pitfall: public `/v1/models` and `apps/web/src/app/lib/models.ts` being Oracle-only is not enough; vNext authenticated `/v1/model-routes` is backed by persisted Postgres runtime records and chat server tools can still fetch/expose those rows. Patch Chat client model metadata, Chat CopilotKit `wandgxListModels`/`wandgxUserModels`, vNext source defaults, vNext dashboard label sources, and the `control_plane_runtime_records` rows for `modelRoutes`/`modelRouteVersions`. Prove with an authenticated beta/admin session, Postgres row check, rebuild/restart of chat/vNext services, and forbidden-string scans of dashboard/client bundles.

Prompt inventory/alignment rule: when the user asks for SET AI, LLM API/proxy, or WandGx Chat/Oracle system prompts, use `references/wandgx-set-oracle-system-prompt-inventory-2026-07-04.md`. It maps the live production prompt sources across VM301 `/opt/apps/SET`, VM300 `/opt/apps/LLM`, and VM300 `/opt/apps/WandGx-chat`, including DB-backed LLM proxy overrides and dynamic prompt composition.

Prompt rename/alignment modification rule: when aligning system prompts across Oracle/WandGx Chat, the LLM API, and SET AI surfaces, use `references/oracle-prompt-alignment-2026-07-04.md`. Durable pattern: preserve existing role/task instructions, add the requested Oracle by WandGx identity without deleting prompt behavior, keep technical slugs like `oracle-1` unchanged unless explicitly requested, update DB-backed LLM settings/virtual-model overrides as well as source defaults, rebuild affected Docker services, and verify prompt text inside the running containers.

Oracle Diffusion prompt/asset split rule: when working on Oracle-1 vs Oracle Diffusion, use `references/oracle-diffusion-prompt-split-and-brand-assets-2026-07-05.md`. Durable pitfall: do not apply the same public diffusion persona to both `oracle-1` and `oracle-diffusion`, and do not make the LLM proxy global prompt a public model persona. Split Chat personas, LLM DB virtual-model overrides, hidden council prompts, and model-card assets. If the user supplies Oracle Diffusion artwork, actually deploy the public model assets and update `apps/web/src/app/lib/models.ts`, then rebuild and verify the deployed bundle references the new image.

Oracle internal tools/RAGFlow direction rule: when adding Council, web search, memory, or document RAG to Oracle Diffusion, use `references/oracle-diffusion-internal-tools-ragflow-plan-2026-07-06.md`. Durable pitfall: GLM-5.2 is hosted by Z.ai, not vLLM; vLLM hosts only the diffusion/orchestrator model. Do not send CopilotKit/OpenAI tool schemas to the vLLM diffusion endpoint just because Oracle needs Council/web/RAG/memory. The server-side proxy should execute hidden internal tools automatically with no user toggles or exposed provider/tool names. User likes RAGFlow as the long-term SET/Oracle document RAG engine; SET currently has a custom Postgres/pgvector/Ollama pipeline.

CopilotKit/AG-UI/A2UI repair rule: when `chat.wandgx.com` advertises AG-UI/A2UI but frontend surfaces/tool calls do not render, use `references/oracle-copilotkit-agui-a2ui-toolcall-repair-2026-07-06.md`. Durable pitfall: endpoint health can be green while the tool-call path is broken. Distinguish hidden Oracle internal tools from frontend AG-UI/A2UI render tools. Only pass OpenAI `tools` to vLLM when intentionally using vLLM-native diffusion tool calling; otherwise keep internal Council/web/RAG/memory orchestration in the proxy.

LLM proxy repair rule: `llm.wandgx.com` runs on VM300 `/opt/apps/LLM` as container `llm-proxy` on host port `9090`. If `/v1/chat/completions` fails while `/health` works, inspect DB-backed `providers`, `virtual_models`, and `settings` in `/opt/apps/LLM/data/analytics.db` before guessing. Historical known-good production shape after 2026-07-03 repair: public `oracle-1` mapped to provider slug `zai-main` (`https://api.z.ai/api/coding/paas/v4`, model `glm-5.2`) with local fallback provider `ollama` pointed at `http://192.168.1.247:8080/v1` model `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf`; billing is enabled and credits are enforced/debited for DB user API keys. Current Oracle diffusion-primary routing needs `oracle-1` to resolve to a diffusion provider first, with Z.AI only as hidden council/support and never as a raw final answer; use `references/oracle-diffusion-primary-llm-proxy-routing-2026-07-05.md` before changing Chat/LLM routing. If CopilotKit logs show request start but no assistant message reaches the UI, use `references/chat-copilotkit-auth-diffusion-live-repair-2026-07-05.md`: check the cron watchdog report, verify the diffusion provider is LAN-reachable (not stale `100.100.x.x` tailnet-only), convert streaming gateway failures into honest assistant deltas when needed, and repair central-session bootstrap/Google redirects without weakening the 401 auth guard. When auditing credits, test both non-streaming and streaming requests: streaming can return `200` while missing `request_logs`/debit rows unless final usage chunks are captured and metered. Stale placeholder OpenAI/Anthropic/Mercury providers should stay disabled unless real credentials/services are restored; stale diffusion placeholders should be replaced with the real reachable diffusion endpoint before enabling. Rebuild/restart only `llm-proxy` after source seed changes, then prove `/v1/models`, authenticated `/v1/chat/completions` in both stream and non-stream modes, positive-credit debit, zero-credit 429, and that diffusion-first routing does not silently fall back to raw Z.AI when diffusion final is required.

Stripe credit setup: when finishing paid credit top-ups for this LLM proxy, use `references/llm-stripe-credit-setup.md` and `references/llm-stripe-billing-checkout.md`. Do not claim Stripe is complete from credit enforcement alone; prove Checkout/session creation, signature-verified webhook handling, balance crediting, and replay idempotency. Stripe MCP/OAuth callbacks can fail from Telegram/headless phone approval loops; if retries fail or the user needs a phone-only flow, stop looping and use the secure secret-drop fallback in `references/stripe-phone-setup-fallback.md`.

LLM billing GA-safe fallback: if no approved Stripe secret + webhook secret exists after sweeping VM300 LLM/vNext/chat envs, VM302 platform secrets, and local Hermes auth/env without printing values, do not leave GA blocked by an unproven public self-serve top-up promise. Hide/disable self-serve card/Stripe UI and copy, keep `billing.enabled=true` credit enforcement fail-closed, prove admin/manual credit provisioning, prove zero-credit `429`, prove credited Oracle `200` with debit, and state GTM billing as admin/support-provisioned launch credits until Stripe authorization arrives. Example report: `/home/claw/reports/llm-platform-ga-unblock-iteration2-2026-07-03.md`.

LLM proxy Stripe/billing inspection rule: for read-only billing audits, do not print secret values and do not modify files/services. Stripe configuration is stored in the `settings` table (`billing.enabled`, `billing.stripe_secret_key`, `billing.stripe_webhook_secret`, `billing.stripe_publishable_key`, `billing.min_topup_usd`), while runtime `PUBLIC_BASE_URL` controls checkout return URLs. `billing.enabled=true` means credit enforcement/UI gating, not necessarily usable Stripe checkout; checkout also needs non-empty Stripe secret + webhook signing secret. See `references/llm-proxy-stripe-billing-integration-2026-07-03.md` for exact routes, DB keys, webhook behavior, safe redacted inspection snippets, and verification steps.

### SET

Owns the adaptive training layer:

- training packet ingestion
- SOP/quiz/lesson/checklist generation
- approval/publish flows
- adaptive-training UI
- training workspace continuity

For SET core-flow reliability work, check `references/set-core-flow-persistence-repair-2026-07-03.md`. It captures the proven pattern for repairing metadata Postgres drift across migrations, repository allow-lists, JSONB handling, production boot checks, contract tests, VM301 deploy, and live proof. Use it when stabilizing workspace -> documents -> AI understanding -> generated learning assets -> learner assignment -> readiness insight.

For SET auth/JWKS incidents where public pages and `/api/system/health` pass but users see auth/session errors, use `references/set-auth-jwks-self-healing-triage-2026-07-04.md`. Durable pitfall: a normal public browser QA pass can miss `set-auth-1` Better Auth JWT/JWKS failures; directly probe `https://auth.trainwithset.com/api/auth/jwks`, inspect `set-auth-1` logs, and verify the `public.jwks` table/migration before proposing a fix. The ops watchdog must include `set-auth-1` and filter noisy 2xx/401 access-log auth probes so the real `relation "jwks" does not exist` incident is visible.

For SET staff designation and Google Drive OAuth blank-page incidents, use `references/set-staff-and-google-drive-oauth-redirect-2026-07-04.md`. Durable pattern: staff may need both SET `platform_staff` and central Better Auth `public."user".role` updates; Google Drive OAuth callbacks must redirect to the SET frontend (`SET_PUBLIC_URL` / `APP_PUBLIC_URL`) rather than central `identity.wandgx.com`, or mobile users can see a blank identity page after Drive connect.

### Central Platform

Owns shared platform services:

- Better Auth/company identity
- JWKS/shared auth
- Appwrite projects/API/console
- ops dashboard
- app access checks

### Paint Quote

Owns the painting quote vertical app. Keep it separate from WandGx app-builder changes unless the task is about shared identity, central access, or route health.

Production auth should run in company-identity mode on LXC123. Paint Quote uses its own proxy route `/api/company-identity/auth`; registration action `register` forwards to central Better Auth `/api/auth/sign-up/email`. Central identity may return no JWT on sign-up when email verification is required, so the UI should show/check-email-and-sign-in behavior instead of pretending the user is authenticated. For later session checks, the client must send the stored company identity JWT as `Authorization: Bearer <token>` to the same proxy route. Do not show “Central Identity unavailable” or internal central-account-management copy in customer-facing Paint Quote auth screens.

Paint Quote has a local Better Auth/Postgres history in `painterquote-postgres`. If users appear “lost” after company-identity cutover, do not assume deletion: compare central VM302 `user`/`account` counts with Paint Quote local `user`/`account` counts and email overlap. Migrate legitimate local `user` + `account` rows into central identity, preserving IDs where app-owned Paint Quote tables depend on them, rather than wiping or restoring central blindly.

Paint Quote PWA install UX rule: do not use a global/browser install banner that covers workspace content or looks like a half-loaded page. Capture `beforeinstallprompt` silently and put installation behind a user-opened Settings option (`Settings -> Install App`, optionally linked from General). See `references/paint-quote-pwa-install-settings-2026-07-02.md` for the proven implementation and verification pattern.

Paint Quote auth UX rule: even in `company-identity` mode, keep customer-facing email/password screens visible for login, registration, and password reset. Do not replace them with a sole `Continue with Company Identity` button or company-only blocker; that creates an unusable support path if the identity landing page is not a real auth screen. The UI stays ordinary PainterQuote email/password, while the backend uses the `/api/company-identity/auth` proxy for central identity. See `references/paint-quote-company-identity-email-password-auth-2026-07-02.md` for the regression pattern and live verification gates.

Paint Quote core-flow repair rule: when Stripe plans, full quote save, property search, or packet creation breaks, verify both frontend company-identity gating and production connector env. Billing UI must allow first-party routes in `company-identity` mode, not just `useBetterAuth`; property packet research requires Firecrawl/Searx env on LXC123 even though VM300 already hosts those services. See `references/paint-quote-core-flow-repair-2026-07-02.md` for focused probes and known-good response shapes.

Paint Quote Agent Mode product rule: do not default to making users fill longer forms. Treat forms as fallback/edit surfaces; paid Agent Mode should ingest lead text/webhook/email/provider data, extract or ask for the address, build the property packet, draft the quote, and stop for human approval when confidence is low. Gate Agent Mode to paid plans at both frontend and backend, and prove packet creation/research with a live smoke. When Google Street View is not configured, attach SearxNG researched exterior image candidates as unconfirmed `agent_found_images` and require human review rather than blocking the packet or pretending they are verified Street View. Firecrawl on LXC123 should point to the VM300 LAN URL (`http://192.168.1.248:3002`) when available. See `references/paint-quote-agent-mode-paid-intake-2026-07-02.md` for the shipped pattern, SearxNG connector pitfall, Firecrawl/image fallback, Stripe metadata alignment, and measurement proof.

Paint Quote prod freshness proof rule: `/health` may report `deployment.commit: null`, so do not claim newest code from health alone. For “commit/push/merge to main and make sure prod VMs host newest code,” prove source `main == origin/main`, clean worktree, LXC123 `painterquote-web` health/image identity, public+LAN health, live hashed bundle parity between public origins, LAN origin, and the running container, plus expected string presence/removed-string absence in the live bundle. See `references/paint-quote-prod-freshness-proof-2026-07-02.md` for the concise verification pattern.

Paint Quote GA/GTM Agent Mode rule: when the user asks to get PainterQuote Pro ready for GA/GTM, do not stop at “pilot/beta/controlled launch” framing. Move through a visible ship loop: source fix, full tests/build, commit/push, LXC123 deploy, public browser proof, service-token Agent Mode smoke, AG-UI state proof, and tool-registry proof. The customer-facing architecture is Agent-as-a-Service: intake creates structured JSON packets, proposed diffs, pending approvals, and tool events; forms remain review/edit fallback. See `references/paint-quote-agent-first-ga-copilotkit-agui-2026-07-02.md` for the shipped CopilotKit/AG-UI and LXC deployment proof pattern. When the user pastes a Codex/other-agent handoff with a Mac mini path, do not assume Hermes should code on the Mac; treat it as context unless explicitly directed. Use `references/paint-quote-external-agent-handoff-closeout-2026-07-04.md` to verify GitHub main, LXC123 freshness, provider env/preflight, live Agent/Packet smoke, and mobile safe-area proof without faking QuickBooks/Stripe results.

## Public Production URLs

### WandGx vNext

- `https://wandgx.com`
- `https://wandgx.com/app`
- `https://wandgx.com/build`
- `https://wandgx.com/register`
- `https://wandgx.com/signup`
- `https://wandgx.com/sign-up`
- `https://vnext.wandgx.com`
- `https://preview.wandgx.com`
- API: `https://api.wandgx.com`
- Admin: `https://admin.wandgx.com`
- Worker: `https://worker.wandgx.com`

### Oracle / WandGx Chat

- `https://chat.wandgx.com`
- `https://oracle.wandgx.com`

### SET

- `https://trainwithset.com`
- `https://www.trainwithset.com`
- `https://set.wandgx.com`
- API: `https://api.trainwithset.com`
- Auth: `https://auth.trainwithset.com`

### Central Platform

- Identity: `https://auth.wandgx.com`
- Identity alias/JWKS: `https://identity.wandgx.com`
- Appwrite API: `https://appwrite.wandgx.com`
- Appwrite console: `https://cloud.wandgx.com`
- Ops dashboard: `https://ops.wandgx.com`

### Paint Quote

- `https://paint.wandgx.com`
- `https://painter.wandgx.com`

### Tooling / Support Services

- LLM proxy: `https://llm.wandgx.com`
- Firecrawl: `https://firecrawl.wandgx.com`
- Searx: `https://searx.wandgx.com`
- Sourcebot: `http://192.168.1.119:3377`
- Voicebox: `http://192.168.1.119:17493`
- Nginx Proxy Manager: `http://192.168.1.125:81`

## VM / Host Topology

### Nginx Proxy Manager

- Host: `192.168.1.125:81`
- Role: public reverse proxy after Cloudflare.
- Use NPM API/UI for public route cutovers.

### VM300 — WandGx vNext, Oracle, LLM/tool services

- IP: `192.168.1.248`
- Role: WandGx vNext, Oracle/WandGx Chat, LLM proxy, Firecrawl, Searx.
- Deploy dirs:
  - `/opt/apps/WandGx-vNext`
  - `/opt/apps/WandGx-chat`
  - `/opt/apps/LLM`
- Main containers/ports:
  - `wandgx-vnext-web-1` -> `31381`
  - `wandgx-vnext-api-1` -> `31380`
  - `wandgx-vnext-admin-1` -> `31382`
  - `wandgx-vnext-worker-1` -> `31383`
  - `wandgx-vnext-postgres-1` -> host `25432`
  - `wandgx-chat-web-1` -> `3200`
  - `llm-proxy` -> `9090`
  - Firecrawl API -> `3002`
  - Searx -> `8080`
- LAN URLs:
  - `http://192.168.1.248:31381`
  - `http://192.168.1.248:31380/health`
  - `http://192.168.1.248:31382`
  - `http://192.168.1.248:31383/health`
  - `http://192.168.1.248:3200`
  - `http://192.168.1.248:9090/health`
  - `http://192.168.1.248:3002`
  - `http://192.168.1.248:8080`

### VM301 — SET

- IP: `192.168.1.249`
- Role: SET frontend/backend/auth/runtime.
- Deploy dirs:
  - `/opt/apps/SET`
  - `/opt/apps/SET/SET-backend`
  - `/opt/apps/SET/SET-frontend`
- Main containers/ports:
  - `set-frontend-1` -> `8085`
  - `set-backend-1` -> `8000`
  - `set-auth-1` -> `8787`
  - `set-copilotkit-runtime-1` -> `4100`
  - `set-postgres-1`
  - `set-redis-1`
  - `set-celery-worker-1`
- LAN URLs:
  - `http://192.168.1.249:8085`
  - `http://192.168.1.249:8000`
  - `http://192.168.1.249:8787`
  - `http://192.168.1.249:4100`

### VM302 — Central Platform

- IP: `192.168.1.250`
- Role: central Better Auth/company identity, Appwrite, ops dashboard.
- Deploy dirs:
  - `/srv/platform/identity`
  - `/srv/platform/appwrite/appwrite`
  - `/srv/platform`
- Main containers/ports:
  - `platform-company-identity` -> `8787`
  - `platform-identity-postgres`
  - `appwrite-traefik` -> `80/443`
  - Appwrite stack
  - `company-platform-ops-api` -> `31480`
  - `company-platform-ops-web` -> `31481`
  - `company-platform-ops-postgres` -> localhost `31432`
- LAN URLs:
  - `http://192.168.1.250:8787/api/auth/ok`
  - `http://192.168.1.250:8787/api/auth/jwks`
  - `http://192.168.1.250:31480/health`
  - `http://192.168.1.250:31481`
  - `http://192.168.1.250:80/v1/health/version`

### LXC123 — Paint Quote

- IP: `192.168.1.183`
- Hostname: `painter-quote`
- Role: Paint Quote app.
- Deploy dir: `/opt/apps/paint-quote`
- Containers/ports:
  - `painterquote-web` -> `3010`
  - `painterquote-postgres`
- LAN URL: `http://192.168.1.183:3010`

### Sandbox / Tooling

- IP: `192.168.1.119`
- Role: Sourcebot, Voicebox, miscellaneous tooling.
- Sourcebot v5: `http://192.168.1.119:3377`
- Voicebox: `http://192.168.1.119:17493`
- Do not treat as production app hosting.

### Linux Dev/Build Box 138

- IP: `192.168.1.138`
- Host/user: `gucci@192.168.1.138`
- OS verified 2026-07-06: Linux Mint 22.3, hostname `gucci`
- Role: source/dev/build workstation and ComfyUI when reachable/requested. Not public production hosting.
- Do not assume historical Windows paths or `droid.exe` paths on this host. Discover current repo/tool paths over SSH before running build or source work.
- Expected dev stack, if running, may expose:
  - `http://192.168.1.138:31381`
  - `http://192.168.1.138:31380/health`
  - `http://192.168.1.138:31382`
  - `http://192.168.1.138:31383/health`
- ComfyUI remains on 138 when the host is reachable.

### Mac mini / ZCode Host

- IP: `192.168.1.241`
- Hostname observed: `zs-Mac-mini.local`
- Role: ZCode machine and historical repo workspaces.
- ZCode app: `/Applications/ZCode.app`
- ZCode project: `/Users/gucci/ZCodeProject`
- ZCode config roots:
  - `/Users/gucci/.zcode`
  - `/Users/gucci/Library/Application Support/ZCode`
- ZCode skill discovery paths include:
  - `<project>/.zcode/skills/<name>/SKILL.md`
  - `<project>/.agents/skills/<name>/SKILL.md`
  - `~/.zcode/skills/<name>/SKILL.md`
  - `~/.agents/skills/<name>/SKILL.md`

## NPM Route Map

- `wandgx.com`, `www.wandgx.com` -> `192.168.1.248:31381`
- `vnext.wandgx.com` -> `192.168.1.248:31381`
- `preview.wandgx.com` -> `192.168.1.248:31381`
- `api.wandgx.com` -> `192.168.1.248:31380`
- `admin.wandgx.com` -> `192.168.1.248:31382`
- `worker.wandgx.com` -> `192.168.1.248:31383`
- `chat.wandgx.com` -> `192.168.1.248:3200`
- `oracle.wandgx.com` -> `192.168.1.248:3200`
- `*.wandgx.com` wildcard -> `192.168.1.248:3200`, but specific hosts above are canonical.
- `llm.wandgx.com` -> `192.168.1.248:9090`
- `firecrawl.wandgx.com` -> `192.168.1.248:3002`
- `searx.wandgx.com` -> `192.168.1.248:8080`
- `trainwithset.com`, `www.trainwithset.com` -> `192.168.1.249:8085`
- `set.wandgx.com` -> `192.168.1.249:8085`
- `api.trainwithset.com` -> `192.168.1.249:8000`
- `auth.trainwithset.com` -> `192.168.1.249:8787`
- `auth.wandgx.com`, `identity.wandgx.com` -> `192.168.1.250:8787`
- `appwrite.wandgx.com` -> `192.168.1.250:80`
- `cloud.wandgx.com` -> `192.168.1.250:80`
- `ops.wandgx.com` -> `192.168.1.250:31481`
- `paint.wandgx.com`, `painter.wandgx.com` -> `192.168.1.183:3010`
- `dev.wandgx.com` and `droid.wandgx.com` are disabled old-138 hosts.

## Source / Repo Rules

Sourcebot currently indexes:

- `github.com/GucciGross/WandGx`
- `github.com/GucciGross/SET`
- `github.com/GucciGross/WandGx-Enterprise`
- `github.com/GucciGross/WandGx-vNext`
- `github.com/sourcebot-dev/sourcebot`

When WandGx-vNext is needed in Sourcebot and GitHub clone/pull is blocked, use `references/sourcebot-vnext-live-snapshot-indexing-2026-07-05.md` for the sanitized VM300 live-snapshot indexing pattern.

Important caveat: current Proxmox deployed dirs are archive-style/no-git:

- `/opt/apps/WandGx-vNext`
- `/opt/apps/WandGx-chat`
- `/opt/apps/LLM`
- `/opt/apps/SET`
- `/opt/apps/paint-quote`
- `/srv/platform/identity`

For durable development, use the GitHub/worktree repos. Do not treat deployed archive dirs as the long-term source of truth.

Repo-local handoff skill install on 138: when preparing 138 for Codex/Droid/Hermes handoffs, use `references/138-github-repo-local-skill-install-2026-07-06.md`. Install the full `wandgx-ecosystem` skill into each repo under `/home/gucci/Documents/GitHub/<repo>/.agents/skills/wandgx-ecosystem/`, patch/add `AGENTS.md` with a pointer, keep Git remotes token-free, and verify every repo has the skill before claiming handoff readiness.

WandGx-Cloud minimal Droid handoff rule: when preparing `/home/gucci/Documents/GitHub/WandGx-Cloud` as the clean new WandGx iteration, use `references/wandgx-cloud-droid-handoff-minimal-repo-config-2026-07-06.md`. Do not copy legacy rule-file clutter or broad `.factory` state. Add only repo-local skills, `AGENTS.md`, minimal `.factory/droids/`, minimal `.factory/mcp.json`, and minimal `.factory/settings.json`; verify no `*.rules`, `.cursorrules`, `.codex/rules`, secrets, caches, or logs were committed. If 138 cannot push to GitHub, use local authenticated patch/bundle transfer and realign 138 to the pushed head before claiming done.

Emergency live patches may exist in `/opt/apps`. If a live patch exists, reconcile it back into the source repo before larger work.

Recent live patch to preserve: WandGx vNext gained visible Register buttons on `/app` and `/build`, plus `/register`, `/signup`, and `/sign-up` aliases that open the create-account modal. The live patch touched:

- `/opt/apps/WandGx-vNext/apps/web/workspace-shell.html`
- `/opt/apps/WandGx-vNext/apps/web/src/shell/wandgx-real-build.mjs`
- `/opt/apps/WandGx-vNext/apps/web/src/shell/wandgx-real-build.css`
- `/opt/apps/WandGx-vNext/scripts/local-dev-138.mjs`

Mirror that patch into the canonical source worktree before doing larger auth/workspace work.

## Auth Architecture

Central identity is Better Auth on VM302. Apps should consume central identity or a product-owned proxy to it. Do not fork one-off auth.

- Central identity public URLs: `auth.wandgx.com`, `identity.wandgx.com`
- JWKS proof URL: `https://identity.wandgx.com/api/auth/jwks`
- Health proof URL: `https://auth.wandgx.com/api/auth/ok`
- Appwrite API: `https://appwrite.wandgx.com`
- Appwrite console: `https://cloud.wandgx.com`

Customer-facing login order:

1. Email/password visible first.
2. Create account and forgot password near the form.
3. Google/GitHub/passkey/email-code/magic-link as secondary options when configured.
4. Staff/enterprise/company identity only as secondary unless the surface is truly internal/admin-only.

WandGx vNext Google/OAuth pitfall: distinguish Google callback authorization from Better Auth state continuity. If the OAuth URL uses an app-host callback (`https://wandgx.com/api/auth/callback/google`) and Google returns `redirect_uri_mismatch`, either add that exact URI to the Google OAuth client or use the already-registered central callback. If using the central callback (`https://identity.wandgx.com/api/auth/callback/google`), Better Auth state cookies must be shared across subdomains (`Domain=.wandgx.com`) and product proxies must preserve the domain cookie; otherwise the callback fails with `state_mismatch`. Verification: generate the live OAuth URL, redact cookie values but inspect cookie attributes, and run a fake callback with the same cookie jar; success boundary is `invalid_code`, not `state_mismatch`. Important: fake callback proof is not real Google-login proof; if the user reports real Google still fails, do not repeat “fixed” from fake-code probes. Reproduce the real browser path or split into auth/central-identity lanes before claiming resolution. See `better-auth-platform-identity/references/app-host-oauth-state-cookie-loop.md`, `better-auth-platform-identity/references/central-identity-oauth-shared-cookie-callback-2026-07-05.md`, and `references/vnext-live-app-auth-ui-closeout-2026-07-05.md`.

## Verification Gates

Before claiming a change is done:

1. Load this skill first for any WandGx/SET/Enterprise deploy or hosting request; do not ask the user where to host when the target is already in this topology.
2. Identify product owner and source/deploy target from the topology above.
3. Inspect current code/route before editing.
4. Make the smallest safe change.
5. Run syntax/focused test/build proof.
6. Restart or redeploy only the affected service.
7. Verify live public URL or LAN route.
8. Verify auth/security guard still behaves correctly.
9. Report exactly what was changed and exactly what was proven.

### Hosting/deploy pitfall

For “merge to main and host” in the WandGx ecosystem, deploy to the already-hosted app locations unless the user explicitly asks for a new host:

- WandGx public production runs from `GucciGross/WandGx-vNext` on VM300 (`/opt/apps/WandGx-vNext`), not from the older `GucciGross/WandGx` repo tree. If self-healing/logging changes land in `GucciGross/WandGx`, confirm whether an equivalent vNext live patch is needed before claiming WandGx production is hosted.
- SET production runs from VM301 (`/opt/apps/SET`) and should be rebuilt/restarted there for backend/frontend changes.
- Central platform/identity/Appwrite/ops run on VM302.
- Windows/138 is a dev/build/ComfyUI workstation, not public production hosting. Current 138 state is Linux Mint; verify paths over SSH before using it.
- `WandGx-Enterprise` is source/contract work unless a concrete deployed Enterprise runtime exists in the topology. Do not overwrite wildcard Oracle/Chat routes like `suite.wandgx.com` or `enterprise.wandgx.com` without confirming a real Enterprise deploy target.

## Cross-Repo Incident Logging and Background Autorepair

When the user asks for self-healing, logging, user-reported error handling, repair loops, or incident triage across WandGx ecosystem repos, use `references/cross-repo-incident-autorepair.md` before editing. The class pattern is: redacted structured incident records, 20-minute default triage SLA, easy but low-emphasis user reporting, background-only autorepair watchers, and explicit env gates before any agent repair/deploy action.

For WandGx vNext source-level ops watcher/autorepair scaffolds, also use `references/vnext-source-ops-autorepair-scaffold-2026-07-04.md`. Key durable pattern: default to record-only/dry-run prompt drafting, redact route/query secrets as well as object/string secrets, generate focused triage prompts under `.codex/runtime`, and require both a deploy-request env flag and a separate human-approval env flag before any deploy command can run.

For the combined SET + vNext ops/autorepair hardening and competitive app-builder feature pattern from the 2026-07-04 launch session, use `references/set-vnext-ops-autorepair-and-competitive-feature-slice-2026-07-04.md`. Durable pitfalls: subagent success is not final proof; parent must re-read summaries, fix timed-out/failed lanes, rerun focused tests/builds/smokes, scan changed files for excluded product and secret-like strings, and commit coherent slices. Classify Stripe webhooks before broad checkout/Stripe classes; keep autoredeploy disabled behind human approval until a clean-week window is explicitly enabled.

For the 2026-07-04 multi-lane SET/vNext/LLM closeout lessons, use `references/multilane-set-vnext-llm-live-proof-2026-07-04.md`. Durable pitfalls: broad mobile QA can miss a sheet/modal substate, so reproduce the exact user screenshot flow; SET Drive `connected=true` needs a real OAuth grant and must not be faked; logged-in landing/root redirects are part of login persistence; VM archive fixes must be back-committed to GitHub main; user-facing LLM API keys/copy must not expose `proxy`; and WandGx status reports should use rich Telegram Markdown with compact tables, bullets, and code blocks rather than dense prose.

Do not turn this into visible customer workflow copy. Public UI should say normal product things like “report issue,” “we’re looking into it,” or “repair queued,” not internal watcher/agent/model names.

Useful live smoke URLs:

- `https://wandgx.com/`
- `https://wandgx.com/app`
- `https://wandgx.com/build`
- `https://vnext.wandgx.com/`
- `https://api.wandgx.com/health`
- `https://worker.wandgx.com/health`
- `https://chat.wandgx.com/`
- `https://oracle.wandgx.com/`
- `https://llm.wandgx.com/health`
- `https://firecrawl.wandgx.com/`
- `https://searx.wandgx.com/`
- `https://trainwithset.com/`
- `https://trainwithset.com/login`
- `https://set.wandgx.com/`
- `https://auth.wandgx.com/api/auth/ok`
- `https://identity.wandgx.com/api/auth/jwks`
- `https://ops.wandgx.com/`
- `https://appwrite.wandgx.com/v1/health/version`
- `https://paint.wandgx.com/login`
- `https://painter.wandgx.com/login`

Known caveat: `https://walkie.wandgx.com/` was returning 502 during the 2026-07-02 check and is not part of the active build lane unless the user names it.

## GA/GTM ecosystem readiness audits

When the user asks whether the WandGx ecosystem is “good to go” for GA/GTM, use `references/ecosystem-ga-gtm-readiness-audit-2026-07-03.md` before answering. Route health is only pipe evidence; GA needs authenticated product-flow proof, public URL correctness, OAuth/integration proof, and packet-ready evidence. If parallel/background audits time out, recover with focused deployed-source sweeps, redacted container env checks, and DB-backed findings instead of stopping.

If the user corrects scope mid-audit — for example “PaintQuote is being worked on; switch to WandGx-vNext” — treat that as authoritative immediately: exclude the active product from verdicts, remove it from packet synthesis, and add the named product lane instead. For long project-specific audits that exceed `delegate_task` child limits, use the Codex GPT-5.5 background-Hermes pattern in `references/ecosystem-ga-gtm-codex-background-agents-2026-07-03.md` rather than re-dispatching capped subagents.

When the user says to keep going until the ecosystem is complete, use `references/ecosystem-completion-agents-10m-updates-2026-07-03.md`: split long work into explicit Codex GPT-5.5 Hermes CLI background lanes, keep any user-excluded product out of every prompt, and install a script-only `every 10m` progress cron that reports compact status until the final packet/evidence bundle exists. For ad-hoc multi-lane work across WandGx/SET/LLM/Paint Quote where the user wants background agents plus visible progress, use `references/multilane-background-agents-watchdog-2026-07-04.md`: create a durable run folder with prompts/logs/reports/CONTINUATION.md, launch explicit Hermes CLI background workers, salvage partial work after worker context failures, and run a no-agent watchdog cron from a real script file. For the concrete 2026-07-04 WandGx-vNext/PaintQuote handoff pattern, use `references/multilane-watchdog-vnext-paintquote-2026-07-04.md`: it captures watchdog/autoresume semantics, VM300 vNext static deploy/back-commit caveats, packet extraction, and the rule that a Mac mini Codex path in a Paint Quote handoff is context only unless the user explicitly says to code on that machine.

When the user asks for GTM approval plus marketing/media materials, use `references/wandgx-gtm-media-packet-workflow-2026-07-03.md`: run GTM blockers first, preserve explicit product exclusions, report excluded-product leakage on in-scope campaign pages, then create a safe-claim media packet with the correct evidence label (`blocked`, `controlled GTM approved`, or `full clean self-serve conditional`). If only a specific campaign path is proven, list the allowed links and forbidden raw/deep links explicitly.

When the user escalates from controlled GTM to **fully unguarded self-service launch**, **real users**, or **real payday**, use `references/unguarded-self-service-launch-readiness-2026-07-03.md`. Do not stamp “fully ready” from route health, visible forms, or controlled campaign proof. Require real-inbox email/code verification or an explicit no-verification launch decision, authenticated build/artifact proof, and Stripe/payment checkout + webhook proof before claiming automated self-serve revenue readiness.

For the proven launch-finishing pattern with no-verification launch policy, live Stripe Checkout redirect proof, signed Stripe-format webhook smoke without charging a live card, duplicate endpoint cleanup, zero/credited API proof, and packet regeneration steps, use `references/self-service-launch-stripe-checkout-proof-2026-07-03.md`. Key pitfall: editing env files plus `docker restart` is not enough to apply compose env changes; recreate with `docker compose up -d <service>` and verify env inside the container.

For post-launch quick fixes after the launch proof passes — source reconciliation, SET API root polish, Stripe restricted-key hardening, and packet refresh — use `references/post-launch-quickfix-source-reconcile-set-root-stripe-rak-2026-07-04.md`. Important pitfall: do not blindly copy live VM archive files back into source when source has moved forward; preserve the newer source architecture and reapply only the compatible launch behavior fix. Stripe restricted API keys are Dashboard/2FA and one-time-copy; treat them as a hardening follow-up unless the user is actively completing the Dashboard step.

When the user asks to “do everything needed in Stripe,” create Products/Prices, research pricing, or add upsells for WandGx launch billing, use `references/stripe-mcp-research-pricing-catalog-2026-07-04.md`. Key pitfalls: phone-only Telegram OAuth works via `hermes mcp login stripe` paste-back; product/price setup is not the same as app wiring; do not create generic Payment Links when user/account crediting depends on an authenticated server-side Checkout session; verify active Price objects with `stripe_api_read`, not only human-friendly search/fetch summaries.

When the user asks for a read-only WandGx vNext auth/conversion or self-service signup/register launch audit, use `references/vnext-auth-conversion-readonly-audit-2026-07-03.md`: scope to VM300 `/opt/apps/WandGx-vNext`, exclude Paint Quote/PainterQuote when requested, identify exact deployed route/auth owner files, prove rendered `/register`, `/signup`, `/sign-up`, top-nav Sign in/Register, and `/app?intent=signup` behavior, and return only findings plus minimal patch recommendations unless fixes are explicitly requested.

When WandGx vNext API login/session routes succeed but the browser UI only flickers/stutters and does not enter the authenticated workspace, use `references/vnext-browser-auth-state-flow-debug-2026-07-05.md`: first prove whether production serves the legacy static `workspace-shell.html` or the newer React mount, then trace the active client `setSession`/product-session token path. Durable pitfall: API auth success is not enough; the active browser shell must also set the workspace gate attributes/events (`data-beta-session-state`, `data-auth-shell-state`, command gate, and `wandgx:account-session-ready`) or React must mint/store the beta product-session token before rendering signed-in workspace.

When the user asks to audit WandGx vNext against app-builder competitors and implement one low-risk missing feature, use `references/vnext-competitor-gap-low-risk-feature-pattern-2026-07-04.md`: ground Lovable/Bolt/v0/Replit feature claims in current docs, compare against the actual vNext workspace source, prefer backend-free user-visible parity such as starter templates/examples, run focused web typecheck/build, and explicitly separate your changed files from pre-existing unrelated diffs.

## Best First ZCode Build Lane

Continue the WandGx vNext + Oracle + SET integration:

- Oracle can create/open a WandGx project/build.
- WandGx can produce a preview/app artifact.
- SET can receive and publish a training packet from that app.
- Central identity is used for auth.
- VM300 owns WandGx/Oracle runtime, VM301 owns SET, VM302 owns identity/Appwrite/ops.

Keep public UX simple and customer-safe. Use proof-first reporting.

## ZCode Host Setup

When installing this ecosystem context into ZCode or preparing the Mac mini for long-running ZCode work, read `references/zcode-mac-mini-operational-setup.md`. It captures ZCode skill discovery paths, the dual install target for the `wandgx-ecosystem` skill, and the verified LaunchAgent-based `caffeinate` setup that prevents sleep/screensaver interruption.

## Quick Completion Checklist

- [ ] Product owner identified.
- [ ] Correct repo/worktree/deploy archive chosen.
- [ ] Central identity/Appwrite boundary preserved.
- [ ] Sign In and Register/Create account visible on customer auth surfaces.
- [ ] Tests/syntax/build ran for changed files.
- [ ] Live route/API verified.
- [ ] Auth guard still blocks unauthenticated protected actions.
- [ ] Any live archive patch reconciled back into source or explicitly reported as not reconciled.
