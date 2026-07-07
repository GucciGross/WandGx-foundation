# WandGx / SET / Oracle System Prompt Inventory Pattern

Use when the user asks to compare, align, audit, or retrieve system prompts across SET AI, the LLM API/proxy, and WandGx Chat/Oracle.

## Scope and live sources

- SET production: VM301 `192.168.1.249`, deploy root `/opt/apps/SET`.
- LLM API/proxy production: VM300 `192.168.1.248`, deploy root `/opt/apps/LLM`.
- WandGx Chat / Oracle production: VM300 `192.168.1.248`, deploy root `/opt/apps/WandGx-chat`.

## Prompt source map

### SET

Primary prompt paths:

- `SET-frontend/src/components/chat/ChatPanel.jsx`
  - Builds `effectiveSystemPrompt` from the UI/systemPrompt state, user preferences, and pinned context.
  - Sends it as `system_prompt` in the chat request body.
- `SET-frontend/src/pages/Chat.jsx`
  - Initializes `systemPrompt` UI state to an empty string.
- `SET-backend/app/api/routes/ai.py`
  - RAG default prompt: `You are a helpful AI assistant with access to a knowledge base...`
  - Connection test prompt: `You are a connection test.`
- `SET-backend/app/services/rag_service.py`
  - Same RAG-aware default prompt and context injection.
- `SET-backend/app/api/routes/tutor.py`
  - Tutor persona prompts: encouraging, Socratic, challenging, casual.
  - Main tutor prompt: `You are an AI tutor specializing in ...`
  - Quiz generator prompt: `You are an expert quiz creator...`
- `SET-backend/app/services/h5p_service.py`
  - H5P generation/system prompt: `You are an expert educational content creator specializing in interactive learning materials.`
- `SET-backend/app/api/routes/staff.py`
  - Staff support prompt: `You are an expert support assistant for the SET Backend platform.`

Avoid treating generated coverage (`htmlcov/`) or `node_modules/` matches as source of truth.

### LLM API / proxy

Primary prompt paths:

- SQLite: `/opt/apps/LLM/data/analytics.db`
  - `settings.system_prompt.text` is the live global prompt. Current observed shape: `You are a helpful, concise assistant.`
  - `virtual_models.system_prompt_override` may override the global prompt per virtual model. Current observed `oracle-1` override: `You are Oracle.`
- `.env`
  - `SYSTEM_PROMPT_TEXT=...` may seed/configure prompt text but DB settings are the runtime admin source.
- `src/llm_proxy/routes.py`
  - `_system_prompt_for_model()` applies virtual-model override first, then falls back to `settings.system_prompt.text`.
- `src/llm_proxy/config.py`
  - Default config prompt: `You are a helpful, concise assistant.`
- `src/llm_proxy/router.py`
  - Internal router prompts: routing-layer user prompt and `You are a JSON-emitting router. Output JSON only.`
- `src/llm_proxy/execute.py`
  - Adds stage-specific prompts for `oracle_draft`, `oracle_council`, `oracle_final`, `oracle_local_fallback`, and generic deliberation stages.
- `src/llm_proxy/diffusion_cli_server.py`
  - Default diffusion prompt: `You are Oracle-1. Answer the user directly...`

### WandGx Chat / Oracle

Primary prompt path:

- `apps/web/src/app/api/copilotkit/route.ts`
  - `getModelPersona()` contains model-specific personas for `glm-5-turbo`, `glm-5v-turbo`, `oracle-1`/null, and default.
  - `SHARED_SYSTEM_BODY` contains tool, delivery, formatting, context-awareness, SET/WandGx integration, build-flow, and follow-up rules.
  - `buildSystemPrompt(modelHeader)` returns `getModelPersona(modelHeader) + SHARED_SYSTEM_BODY`.
  - Runtime appends skill context and AG-UI runtime context: `[baseSystem, skillContext, agUiContext].filter(Boolean).join("\n\n")`.

## Practical audit workflow

1. Inspect live deployed roots, not only source repos, when the user asks what prompts are currently in production.
2. Search narrowly and exclude generated/vendor dirs:
   - Exclude `node_modules`, `htmlcov`, `.venv`, `venv`, `dist`, `build`, `__pycache__`, `.git`.
   - Search for `system_prompt`, `system prompt`, `MessageRole.SYSTEM`, `role: "system"`, and `You are`.
3. For the LLM proxy, query `analytics.db` directly for live settings and virtual model overrides.
4. Return only the prompt text and source paths if the user asks for just prompts; do not add alignment recommendations unless requested.
5. Call out dynamic prompt composition separately from static prompt literals: SET preferences/pinned context, WandGx skill/AG-UI context, LLM virtual-model overrides.

## Alignment pitfall

These systems currently use different identities:

- SET defaults are generic education/RAG/tutor prompts.
- LLM proxy global prompt is generic concise assistant; `oracle-1` override is only `You are Oracle.`
- WandGx Chat has the richest Oracle-1 identity and product workflow rules.

When aligning, preserve product roles: SET should stay training/education-first, WandGx Chat should stay Oracle/build-workspace-first, and LLM proxy should provide a shared Oracle-safe base without exposing internal routing/providers/councils.