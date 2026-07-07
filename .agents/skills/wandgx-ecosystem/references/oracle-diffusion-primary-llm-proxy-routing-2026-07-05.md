# Oracle diffusion-primary routing through LLM proxy

Use when wiring or debugging `chat.wandgx.com` / Oracle so diffusion is the user-facing model and Z.AI is only hidden support.

## Desired product contract

- The user talks to **Oracle Diffusion by WandGx** as a diffusion-first model.
- `llm.wandgx.com` is the gateway/proxy, not the public model.
- Diffusion is the primary backend and must produce the final user-facing answer.
- "Diffusion" here is **text-first diffusion language generation**, not image-only generation. The browser receives streamed text chunks because SSE/chat streaming is the delivery format; streaming text does not prove Z.AI or another autoregressive model wrote the answer.
- Public prompt/identity copy should call it `Oracle Diffusion by WandGx, the user-facing text-first diffusion language model for chat, builds, product work, code, and creative exploration`.
- Z.AI may be called only behind the scenes for private support/council context.
- Z.AI output must be fed back into the diffusion/finalization step; raw Z.AI must not be streamed as the final user answer.
- If diffusion is unreachable, fail honestly instead of silently returning a Z.AI answer while calling it diffusion.

## Live ownership

- Chat app: VM300 `/opt/apps/WandGx-chat`, container `wandgx-chat-web-1`, public `https://chat.wandgx.com`.
- LLM proxy: VM300 `/opt/apps/LLM`, container `llm-proxy`, public `https://llm.wandgx.com`, LAN `http://127.0.0.1:9090`.
- LLM proxy runtime config is DB-backed in `/opt/apps/LLM/data/analytics.db`:
  - `providers`
  - `virtual_models`
  - `settings`

## Known-good architecture shape

```text
chat.wandgx.com
  -> apps/web/src/app/api/copilotkit/route.ts
  -> ORACLE_PROXY_BASE_URL / ORACLE_PROXY_MODEL=oracle-1
  -> llm.wandgx.com /v1/chat/completions
  -> virtual_models.slug=oracle-1
  -> providers.slug=oracle-diffusion-vllm primary
  -> hidden oracle-council-* virtual models backed by zai-main/local fallback
  -> final user response from diffusion path
```

## DB-backed LLM proxy settings pattern

Provider row for diffusion:

```json
{
  "slug": "oracle-diffusion-vllm",
  "type": "openai_compat",
  "base_url": "http://100.100.139.18:8000/v1",
  "models": ["cyankiwi/diffusiongemma-26B-A4B-it-AWQ-INT4"],
  "priority": 0,
  "tags": {
    "diffusion": true,
    "in_house": true,
    "private_network": true,
    "oracle": true,
    "primary": true
  },
  "is_enabled": true
}
```

`oracle-1` virtual model should list diffusion first, then hidden support/fallback candidates:

```json
[
  {"provider_slug":"oracle-diffusion-vllm","model":"cyankiwi/diffusiongemma-26B-A4B-it-AWQ-INT4","weight":100},
  {"provider_slug":"zai-main","model":"glm-5.2","weight":80},
  {"provider_slug":"ollama","model":"Qwen3.6-35B-A3B-UD-Q4_K_M.gguf","weight":40}
]
```

Council virtual models (`oracle-council-reasoning`, `oracle-council-research`, `oracle-council-code`) should resolve to hidden support such as `zai-main` first, then local fallback.

`settings.deliberation.oracle-1` should use gateway mode:

```json
{
  "mode": "oracle_gateway",
  "max_internal_calls": 5,
  "provider_strategy": "primary",
  "cache_ttl_seconds": 0,
  "allow_streaming": true,
  "allowed_councils": ["oracle-council-reasoning", "oracle-council-research", "oracle-council-code"],
  "higher_provider_slug": "zai-main",
  "higher_model": "glm-5.2"
}
```

## Source/code guardrails

In `/opt/apps/LLM/src/llm_proxy/execute.py`, do not allow raw Z.AI fallback to masquerade as diffusion. The gateway must either:

1. get a diffusion draft/direct answer;
2. optionally call hidden Z.AI council(s);
3. call diffusion again for the final response; or
4. return an honest upstream error if diffusion is unreachable and final diffusion is required.

Useful env knobs:

```yaml
ORACLE_DIFFUSION_DRAFT_TIMEOUT_SECONDS: ${ORACLE_DIFFUSION_DRAFT_TIMEOUT_SECONDS:-18}
ORACLE_REQUIRE_DIFFUSION_FINAL: ${ORACLE_REQUIRE_DIFFUSION_FINAL:-true}
```

If `ORACLE_REQUIRE_DIFFUSION_FINAL=true`, `execute_non_stream()` must not catch gateway failure and fall back to `_execute_direct_non_stream()`, because that can route to Z.AI and violate the user-facing contract.

## Chat app wiring pattern

In `/opt/apps/WandGx-chat/apps/web/src/app/api/copilotkit/route.ts`:

- Use an `oracleProxyProvider = createOpenAI({ baseURL: ORACLE_PROXY_BASE_URL, apiKey: ORACLE_PROXY_API_KEY })`.
- Default `oracle-1` and `oracle-diffusion` model headers to `ORACLE_PROXY_MODEL` (normally `oracle-1`).
- Do not point chat directly at raw Z.AI or the raw diffusion vLLM URL.
- Keep customer-facing copy as Oracle by WandGx / Oracle Diffusion; do not reveal provider slugs, private council, or upstream model IDs.

The chat container needs a private LLM proxy API key in `.env`:

```env
ORACLE_PROXY_BASE_URL=http://host.docker.internal:9090/v1
ORACLE_PROXY_MODEL=oracle-1
ORACLE_PROXY_API_KEY=<private wgx_... service key>
```

Generate/store service keys carefully: command output may include logs. When using a script to generate a key, print a unique sentinel like `KEY::<key>` and parse only that line before writing `.env`; otherwise structured logs can pollute the env file.

## Identity/self-description guardrail

The upstream diffusion model can leak its base identity on typoed or indirect identity prompts such as `What model at eyou` or `who made you?`, answering as Gemma/Google/DeepMind. Product contract requires the user-facing identity to stay Oracle Diffusion by WandGx.

Durable fix in `/opt/apps/LLM/src/llm_proxy/execute.py`:

- Keep the prompt explicit: Oracle Diffusion is a text-first diffusion language model, not image-only.
- Add an identity guard for identity/creator/model questions and upstream identity leaks.
- Canonical answer: `I am Oracle Diffusion by WandGx, a text-first diffusion language model for chat, builds, product work, code, and creative exploration.`
- Sanitize/rewrite Gemma/Google/DeepMind/open-weights self-identification before streaming the final answer.
- Verify with exact typo and indirect prompts: `What model at eyou`, `who made you?`, `Are you Gemma?` — none should contain Gemma/Google/DeepMind/open weights.

## Verification checklist

- `python3 -m py_compile src/llm_proxy/execute.py` for LLM proxy code changes.
- Rebuild/recreate LLM proxy: `docker compose build proxy && docker compose up -d proxy`.
- Authenticated `/v1/models` from the proxy returns only public models such as `oracle-1`.
- A request to `oracle-1` logs `virtual_model_resolved` to `oracle-diffusion-vllm` first.
- If diffusion endpoint is unreachable and `ORACLE_REQUIRE_DIFFUSION_FINAL=true`, request returns 503 instead of raw Z.AI answer.
- Rebuild chat web and run focused test: `docker compose run --rm --no-deps web pnpm --filter web exec vitest run src/app/tests/copilotkit-integration.test.ts`.
- Recreate `wandgx-chat-web-1`, verify `https://chat.wandgx.com`, `/api/oracle/agui-status`, auth guard, chat container proxy reachability, and deployed bundle markers.

## Network pitfall

`100.100.x.x` addresses are often Tailscale/private CGNAT. If VM300 cannot reach the diffusion endpoint, do not keep changing chat code. Fix routing by putting VM300 on the same tailnet, exposing a reachable LAN/public URL, or adding a reverse tunnel/proxy from the diffusion host. In the 2026-07-05 incident, the tailnet-style endpoint timed out but a LAN scan found the reachable vLLM server at `http://192.168.1.138:8000/v1`; verify `/v1/models` before assuming the model is down.
