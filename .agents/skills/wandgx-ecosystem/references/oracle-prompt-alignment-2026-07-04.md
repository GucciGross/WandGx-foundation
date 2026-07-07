# Oracle prompt alignment across SET, LLM API, and WandGx Chat

Use this reference when the user asks to align, rename, or audit the system prompts for Oracle/WandGx Chat, the LLM API, and SET AI surfaces.

## Durable pattern

0. If the user asks to list prompts only, respond with the prompt text and source locations only; do not add alignment recommendations or commentary unless explicitly asked.
1. Treat prompts as deployed-runtime state, not just source text.
   - WandGx Chat prompt owner: VM300 `/opt/apps/WandGx-chat/apps/web/src/app/api/copilotkit/route.ts`.
   - LLM API prompt owner: VM300 `/opt/apps/LLM/src/llm_proxy/*`, `.env`, and DB-backed `data/analytics.db` settings/virtual model overrides.
   - SET prompt owners: VM301 `/opt/apps/SET/SET-backend/app/api/routes/*`, `/opt/apps/SET/SET-backend/app/services/*`, and SET frontend `SET-frontend/src/components/chat/ChatPanel.jsx`.
2. Preserve existing prompt instructions. If the user asks to add an identity, prepend or inline the identity; do not replace the rest of the prompt.
3. Separate prompt copy from technical slugs. Example: replacing user-facing prompt text `Oracle-1` with `Oracle by WandGx` should not automatically rename stable API/model slugs such as `oracle-1` unless explicitly requested.
4. For DB-backed LLM API prompts, update both source defaults and the live DB:
   - `settings.system_prompt.text`
   - `virtual_models.system_prompt_override` where non-empty
5. Rebuild/recreate affected services after source/env changes; container restarts alone may keep old built assets or installed Python packages.
   - WandGx Chat: `docker compose up -d --build web`
   - LLM API: `docker compose up -d --build proxy`
   - SET: `docker compose up -d --build backend frontend`
6. Verify inside the running containers, not only in the host archive dir.
   - Chat: grep `/app/apps/web/src/app/api/copilotkit/route.ts` inside `wandgx-chat-web-1`.
   - LLM: inspect `/app/data/analytics.db` inside `llm-proxy` and grep installed package files under site-packages.
   - SET backend: grep `/app/app/...` inside `set-backend-1`.
   - SET frontend: grep built assets under `/usr/share/nginx/html/assets` inside `set-frontend-1`.
7. Run focused validation:
   - Python compile for changed backend files.
   - YAML parse for changed YAML prompt configs.
   - Next/Vite build proof from compose build output.
   - Public health checks for `chat.wandgx.com`, `llm.wandgx.com/health`, `trainwithset.com`, and `api.trainwithset.com/api/system/health`.

## Pitfalls

- The deploy directories are archive-style/no-git; do not claim source reconciliation unless you actually mirror changes to canonical repos.
- Host source files can be newer than a running container. Always verify prompt text inside the container after rebuild.
- The LLM settings store needs app/database initialization for helper imports. Direct SQLite inspection is safer for verification in a bare `docker exec` context.
- Do not collapse product-specific prompt behavior. SET tutor, quiz, RAG, H5P, and staff prompts can all identify as Oracle by WandGx while preserving their original learning/support roles.

## Quick active prompt locations from the 2026-07-04 alignment

- SET:
  - `SET-backend/app/api/routes/ai.py`
  - `SET-backend/app/services/rag_service.py`
  - `SET-backend/app/api/routes/tutor.py`
  - `SET-backend/app/services/h5p_service.py`
  - `SET-backend/app/api/routes/staff.py`
  - `SET-backend/app/services/chat_service.py`
  - `SET-backend/app/services/deepresearch/config/agents.yaml`
  - `SET-frontend/src/components/chat/ChatPanel.jsx`
- LLM API:
  - `src/llm_proxy/config.py`
  - `src/llm_proxy/routes.py`
  - `src/llm_proxy/router.py`
  - `src/llm_proxy/execute.py`
  - `src/llm_proxy/diffusion_cli_server.py`
  - `.env`
  - `data/analytics.db`
- WandGx Chat:
  - `apps/web/src/app/api/copilotkit/route.ts`
