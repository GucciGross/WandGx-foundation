# Oracle Chat CopilotKit / AG-UI / A2UI Tool-Call Repair (2026-07-06)

## When to use

Use this when `chat.wandgx.com` advertises CopilotKit, AG-UI, A2UI, `renderA2ui`, `renderArtifact`, or frontend actions, but the UI only streams plain text, tool surfaces do not render, or CopilotKit/A2UI appears dead after routing Oracle through `llm.wandgx.com`.

## Durable root causes found

1. **Tools disabled on the Oracle proxy route**
   - File: VM300 `/opt/apps/WandGx-chat/apps/web/src/app/api/copilotkit/route.ts`
   - `resolveModelRoute()` had `disableTools: true` for `oracle-1` and `oracle-diffusion`.
   - Result: prompts documented `renderA2ui`/AG-UI tools, but `modelArgs.tools` was never attached for the Oracle proxy path.

2. **LLM proxy dropped tool calls**
   - Files: VM300 `/opt/apps/LLM/src/llm_proxy/routes.py`, `streaming.py`, `providers.py`
   - `providers.py` parsed `msg.tool_calls`, but `_to_openai_response()` emitted only `{role, content}`.
   - Streaming translation also ignored `delta.tool_calls`.
   - Result: CopilotKit/Vercel AI SDK received neither assistant text nor executable frontend tool calls when the model selected a tool.

3. **vLLM rejected explicit `tool_choice: "auto"`**
   - Error shape: `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`.
   - Keep the `tools` schema, but strip redundant explicit `tool_choice: "auto"` before calling OpenAI-compatible vLLM. With `tools` present and `tool_choice` omitted, the backend can still return tool calls.

4. **A2UI renderer schema mismatch**
   - Renderer expects WandGx A2UI components like `{id, component: "Heading", text}`.
   - Models may emit common shorthand like `{type: "header", props: {title}}`.
   - Add a defensive normalizer in `apps/web/src/app/components/a2ui-card.tsx` for aliases (`header -> Heading`, `columns -> Row`, `stat -> Metric`, etc.) and tighten the prompt/tool description to say: use `component`, not `type`, and put props directly on the object.

## Repair pattern

1. Inspect `chat.wandgx.com/api/oracle/agui-status` and container health.
2. Inspect `apps/web/src/app/api/copilotkit/route.ts`:
   - ensure `modelArgs.tools = mergedTools` runs for Oracle proxy paths.
   - do not set `disableTools: true` for `oracle-1` or `oracle-diffusion` unless deliberately disabling CopilotKit surfaces.
3. Inspect `/opt/apps/LLM` proxy:
   - `providers.py` should forward streaming `delta.tool_calls` as `StreamEvent(type="tool_call_delta")`.
   - `streaming.py` should emit OpenAI SSE chunks with `delta.tool_calls`.
   - `routes.py` `_to_openai_response()` should include `message.tool_calls` and preserve `finish_reason: "tool_calls"`.
   - `providers.py` should strip only `payload["tool_choice"] == "auto"`, not `tools`.
4. If Oracle Diffusion still runs as a toolless vLLM leg, add/verify the private marker bridge in `/opt/apps/LLM/src/llm_proxy/execute.py`:
   - The diffusion stage prompt tells the model that client tools are available and to emit a private marker such as `ORACLE_FRONTEND_TOOL_CALL: {"name":"renderA2ui","arguments":{...}}` when a UI/server tool is the next action.
   - The LLM proxy parses that marker and returns normal OpenAI `message.tool_calls` / streaming `delta.tool_calls` to CopilotKit. This preserves the rule that raw OpenAI/CopilotKit tool schemas are not forwarded to vLLM while still allowing AG-UI/A2UI and server tools to execute.
   - Forced `tool_choice` probes should synthesize safe default args if the diffusion model emits malformed marker JSON; otherwise tests can be flaky even though the transport bridge is correct.
   - Also handle legacy/plain text model output like `call:renderArtifact artifactId="...",title="...",content:` by converting it to a real `renderArtifact` tool call in the LLM proxy. This raw `call:*` text must never render in the chat transcript. Normalize `content`/`html`/`source` aliases into the frontend tool's expected `code` argument.
5. Rebuild in order:
   - `/opt/apps/LLM`: `docker compose up -d --build proxy`
   - `/opt/apps/WandGx-chat`: `docker compose up -d --build web`
6. Verify with a direct internal tool-call probe against `http://127.0.0.1:9090/v1/chat/completions` using the Chat container’s existing `ORACLE_PROXY_API_KEY` without printing the key:
   - non-stream: response has `choices[0].message.tool_calls`, tool name `renderA2ui`, finish reason `tool_calls`.
   - stream: SSE contains `"tool_calls"`, contains `renderA2ui`, and does not contain the vLLM `enable-auto-tool-choice` error.
   - automatic tool selection: a current-info prompt with a `webSearch` tool available returns a `webSearch` tool call without a user-visible Search toggle.
7. Verify public endpoints:
   - `https://chat.wandgx.com/ -> 200`
   - `https://chat.wandgx.com/api/oracle/agui-status -> 200`
   - `https://llm.wandgx.com/health -> 200`
   - `wandgx-chat-web-1` and `llm-proxy` healthy
   - no recent `error|exception|traceback|failed|warning|enable-auto-tool-choice` log lines after deploy.
8. Path Resolve / diffusion UI sanity:
   - Do **not** render a giant skeleton/card overlay above the composer. It covers generated content, exposes stage/debug labels, and makes users think streaming is clipped.
   - Keep the diffusion indicator compact, pointer-transparent, and above the composer; the actual answer should resolve in the chat stream.
   - Bundle scan should find no `PATH_RESOLVE`, `path-resolve-card`, `Layout resolving`, or `Oracle is generating` strings after deploy.
   - For buffered Oracle gateway text, set readable chunk pacing with `ORACLE_STREAM_CHUNK_CHARS` / `ORACLE_STREAM_CHUNK_DELAY_SECONDS`; prove SSE contains `[DONE]` and final `finish_reason`.
9. Browser sanity:
   - load `https://chat.wandgx.com/`
   - check console/JS errors are empty.

## User preference lesson

If the user reports CopilotKit/AG-UI/A2UI is broken, do not answer from endpoint health alone. Endpoint health can be green while the tool-call path is severed. Trace the full chain: chat frontend actions -> CopilotKit runtime -> AI SDK tool schema -> LLM proxy -> vLLM response -> OpenAI SSE/non-stream tool call preservation -> frontend renderer.
