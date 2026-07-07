# Oracle-1 local Qwen final routing + public selector cleanup (2026-07-06)

## When to use

Use this reference when Oracle/WandGx Chat appears to load the local Ollama/Qwen model but answers still look like GLM/Z.AI, or when retired diffusion models still appear in the chat model selector or public model list.

## Durable lesson

A warm local model is not proof that it is the final response backend. The LLM proxy can load `oracle-1-proxy:latest` in Ollama while `oracle-1` still has GLM/Z.AI first in its DB-backed `virtual_models.backends`. Always inspect and prove the routed provider from LLM proxy logs, not just `ollama ps`.

## Correct production shape

- Public model list: `oracle-1` only.
- `oracle-1` final answer backend: `oracle-local-qwen` -> `http://192.168.1.247:11434/v1` -> `oracle-1-proxy:latest`.
- GLM/Z.AI: hidden support/council only, not final response backend for `oracle-1`.
- Diffusion model/card/routes/assets: retired and absent from source, built bundle, public HTML, and DB-backed public model rows.
- Chat header/model area: with one public model, render as static Oracle-1 identity, not as a clickable selector/deck.

## Focused repair sequence

1. On VM300 `/opt/apps/LLM`, inspect DB-backed routing first:
   ```bash
   python3 - <<'PY'
   import sqlite3,json
   con=sqlite3.connect('data/analytics.db'); con.row_factory=sqlite3.Row
   for r in con.execute("select slug,is_enabled,backends from virtual_models where slug like 'oracle%' order by slug"):
       print(json.dumps(dict(r), indent=2))
   PY
   ```
2. Set `oracle-1` to local-only final backend:
   ```json
   [{"provider_slug":"oracle-local-qwen","model":"oracle-1-proxy:latest","weight":100}]
   ```
3. Disable/delete retired DB rows for `oracle-diffusion`, `gemmadiffusion*`, `oracle-tool-proxy` if public `/v1/models` exposes them. Delete/disable retired diffusion providers if they are no longer wanted.
4. Patch LLM source seeding so a rebuild cannot resurrect GLM-first or diffusion rows. The built-in Oracle final backend helper should prefer `tool_proxy`, `oracle-local-qwen`, `oracle-1-proxy`, local Qwen/Ollama providers. Do not leave seed helpers that search for `diffusion`, `gemma`, or `mercury`.
5. Rebuild/restart `llm-proxy`:
   ```bash
   docker compose build proxy && docker compose up -d proxy
   ```
6. On VM300 `/opt/apps/WandGx-chat`, ensure `apps/web/src/app/lib/models.ts` contains only `oracle-1` and no `oracle-diffusion` entry/assets.
7. Patch `components/model-switcher.tsx` so `MODELS.length <= 1` returns a static identity wrapper and never opens the model deck. Also reset stale `localStorage['oracle-active-model']` to `DEFAULT_MODEL_ID` if it contains a retired id.
8. Rebuild/redeploy chat:
   ```bash
   docker compose build web && docker compose up -d web
   ```

## Required proof

- `/v1/models` returns exactly `oracle-1` with `backend_count: 1`.
- A direct `oracle-1` completion returns the requested sentinel and LLM proxy logs show:
  ```text
  provider_success provider=oracle-local-qwen model=oracle-1-proxy:latest
  ```
- A forced tool-call request through `oracle-1` returns OpenAI-style `tool_calls` for `webSearch`.
- Greps of LLM source/templates/config/data and Chat source/public/docker/env/built bundle have no `oracle-diffusion`, `diffusiongemma`, or `Oracle Diffusion` strings.
- Public `chat.wandgx.com` and `llm.wandgx.com` HTML greps pass with no retired diffusion strings.
- Browser console on `chat.wandgx.com` has no JS errors.

## Pitfall

Do not claim local-Qwen routing from `ollama ps` alone. `ollama ps` only proves the model is loaded; the LLM proxy DB and provider logs prove the final response path.