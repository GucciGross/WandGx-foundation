# Oracle Diffusion prompt split + brand asset deployment (2026-07-05)

Use this when working on `chat.wandgx.com`, `llm.wandgx.com`, Oracle-1, Oracle Diffusion, hidden Z.AI/council routing, or model-card artwork.

## What went wrong in the session

- The same heavy-handed Oracle Diffusion identity prompt was applied to both `oracle-1` and `oracle-diffusion`.
- The LLM proxy global `system_prompt.text` also carried user-facing diffusion persona text, so the neutral runtime/proxy layer could bleed product identity into multiple models.
- The identity guard over-corrected base-model leaks by replacing identity-ish prompts with a canned one-liner, causing the user to see only: `I am Oracle Diffusion by WandGx...` instead of a useful full answer.
- Chat routing treated both `oracle-1` and `oracle-diffusion` as the same proxy model (`ORACLE_PROXY_MODEL`), so the two UI models collided in the backend virtual-model layer.
- The user supplied Oracle-1 Diffusion artwork, but the chat model config still pointed to `/models/oracle-diffusion.svg`, a tiny placeholder. Asset deployment must be completed, not just acknowledged.

## Durable architecture rule

Separate identity at every layer:

```text
chat.wandgx.com
├─ oracle-1 selected
│  └─ chat persona: Oracle-1 by WandGx
├─ oracle-diffusion selected
│  └─ chat persona: Oracle Diffusion by WandGx

llm.wandgx.com
├─ global settings.system_prompt.text
│  └─ neutral runtime/proxy prompt, no public persona
├─ virtual_models.oracle-1.system_prompt_override
│  └─ Oracle-1 contract
├─ virtual_models.oracle-diffusion.system_prompt_override
│  └─ Oracle Diffusion contract
└─ oracle-council-* prompts
   └─ private support only; never user-facing
```

Do **not** use one shared public persona prompt for both Oracle-1 and Oracle Diffusion.

## Correct prompt behavior

Oracle Diffusion text streaming is transport, not the model identity. The user expects the **whole answer** to be generated/refined through the diffusion route, then streamed as text chunks.

Bad behavior:

```text
normal task prompt -> canned identity sentence
```

Correct behavior:

```text
normal task prompt -> task-specific full answer
identity prompt -> brief identity answer, then continue work if requested
base-model leak -> sanitize Gemma/Google/DeepMind/open-weights leak only when it appears
```

Guard rule: do not replace every identity-ish prompt with the canonical identity. Only sanitize actual upstream identity leaks. Preserve the model's full generated answer for normal work.

## Files and DB locations

### Chat app on VM300

- Root: `/opt/apps/WandGx-chat`
- Container: `wandgx-chat-web-1`
- Active CopilotKit route: `apps/web/src/app/api/copilotkit/route.ts`
- Model cards/config: `apps/web/src/app/lib/models.ts`
- Public model assets: `apps/web/public/models/`

Implementation pattern:

- Add separate chat persona branches for `oracle-1` and `oracle-diffusion` in `getModelPersona`.
- Keep `oracle-1` as Oracle-1, not Oracle Diffusion.
- Add `ORACLE_PROXY_DIFFUSION_MODEL = process.env.ORACLE_PROXY_DIFFUSION_MODEL || "oracle-diffusion"`.
- Route `x-oracle-model: oracle-diffusion` to proxy model `oracle-diffusion`, not `oracle-1`.
- Keep `x-oracle-model: oracle-1` / no header routed to `oracle-1`.

### LLM proxy on VM300

- Root: `/opt/apps/LLM`
- Container: `llm-proxy`
- DB: `/opt/apps/LLM/data/analytics.db`
- Source defaults:
  - `src/llm_proxy/config.py`
  - `src/llm_proxy/routes.py`
  - `src/llm_proxy/router.py`
  - `src/llm_proxy/app.py`
  - `src/llm_proxy/execute.py`

DB-backed updates matter more than source defaults for live runtime:

- `settings.system_prompt.text` must be neutral runtime/proxy text.
- `virtual_models.oracle-1.name` should be `Oracle-1`.
- `virtual_models.oracle-1.system_prompt_override` should describe Oracle-1 only.
- `virtual_models.oracle-diffusion` should exist/enabled with Oracle Diffusion prompt override.
- `oracle-council-*` models should remain private/internal, not public persona prompts.

## Brand artwork deployment pattern

When the user supplies a model/logo image for Oracle Diffusion, actually deploy the assets:

1. Generate web-ready variants from the supplied source image:
   - `oracle-diffusion.jpg` — square/card image, 512x512.
   - `oracle-diffusion.webp` — square/card webp.
   - `oracle-diffusion-avatar.jpg` / `.webp` — tight central-figure/avatar crop.
   - `oracle-diffusion-poster.jpg` / `.webp` — full poster/banner image.
2. Copy them into `/opt/apps/WandGx-chat/apps/web/public/models/`.
3. Backup old assets first under `/opt/apps/WandGx-chat/backups/oracle-diffusion-image-<timestamp>/`.
4. Update `apps/web/src/app/lib/models.ts` from placeholder SVG to the real image:

```ts
image: "/models/oracle-diffusion.jpg"
```

5. Rebuild and restart `wandgx-chat-web-1`.
6. Verify public URLs return `200` and correct content types:
   - `https://chat.wandgx.com/models/oracle-diffusion.jpg`
   - `https://chat.wandgx.com/models/oracle-diffusion.webp`
   - `https://chat.wandgx.com/models/oracle-diffusion-avatar.jpg`
   - `https://chat.wandgx.com/models/oracle-diffusion-poster.jpg`
7. Grep the deployed Next bundle/container for `/models/oracle-diffusion.jpg`; public asset `200` alone does not prove the UI points at it.

## Verification gates

After prompt/routing/asset changes, prove all of these before saying done:

```text
python3 -m py_compile src/llm_proxy/config.py src/llm_proxy/routes.py src/llm_proxy/router.py src/llm_proxy/app.py src/llm_proxy/execute.py
cd /opt/apps/WandGx-chat && docker compose config --quiet
docker compose up -d --build proxy   # in /opt/apps/LLM when LLM changed
docker compose up -d --build web     # in /opt/apps/WandGx-chat when chat/assets changed
```

Public checks:

- `https://chat.wandgx.com/ -> 200`
- `https://chat.wandgx.com/api/oracle/agui-status -> 200`
- `https://llm.wandgx.com/health -> 200`
- no-JWT `POST /api/copilotkit -> 401` still protected
- `llm-proxy` and `wandgx-chat-web-1` healthy
- recent logs have no warning/error lines

Model behavior checks through the internal LLM proxy with the chat proxy key, without printing the key:

- `oracle-1` normal prompt -> task-specific answer, not Oracle Diffusion identity.
- `oracle-diffusion` normal prompt -> task-specific answer, not canned identity.
- `oracle-1` identity prompt -> `I am Oracle-1 by WandGx...` plus requested work if any.
- `oracle-diffusion` identity prompt -> `I am Oracle Diffusion by WandGx...` plus requested work if any.
- No `Gemma`, `Google`, `DeepMind`, or `open weights` leaks.

## Reporting preference learned

For this user, when they are upset about production behavior, do not explain first or stop at intent. Be active:

- Acknowledge the concrete mistake.
- Inspect the live source/DB/runtime.
- Patch the actual persisted source of truth (source plus DB overrides when DB-backed).
- Rebuild/restart.
- Verify with public URLs and live behavior.
- Then summarize concisely with exact proof.

If they ask for a wiring graph “once complete,” complete/verify deployment first, then provide the graph. Do not give speculative architecture as final proof.