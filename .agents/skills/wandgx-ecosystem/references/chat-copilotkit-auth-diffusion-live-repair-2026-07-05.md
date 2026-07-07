# Chat CopilotKit auth + diffusion live repair (2026-07-05)

Use when `chat.wandgx.com` users can open the app but cannot log in normally, CopilotKit requests start, and no assistant message reaches the UI.

## Durable symptoms

- `wandgx-chat-web-1` logs show `[oracle-copilotkit] request_start` but the browser receives no assistant message.
- Chat logs show `Agent execution failed: AI SDK stream error` with upstream `Oracle diffusion backend is unavailable`.
- `llm-proxy` logs show `oracle_gateway_start` followed by `provider_attempt_failed` / `oracle_gateway_diffusion_required_unavailable` for `oracle-diffusion-vllm`.
- Browser public route is healthy (`https://chat.wandgx.com/ -> 200`), so route health alone is insufficient.

## First checks

On VM300 (`192.168.1.248`):

```bash
docker logs --since 4h --tail 700 wandgx-chat-web-1
docker logs --since 4h --tail 700 llm-proxy
curl -k -sS -o /dev/null -w '%{http_code}' https://chat.wandgx.com/
curl -k -sS -o /dev/null -w '%{http_code}' https://chat.wandgx.com/api/oracle/agui-status
curl -k -sS -o /dev/null -w '%{http_code}' -X POST https://chat.wandgx.com/api/copilotkit -H 'content-type: application/json' --data '{}'
```

Expected auth guard: unauthenticated CopilotKit stays `401`.

## Diffusion endpoint discovery pattern

If the configured diffusion endpoint is a `100.100.x.x`/tailnet-style address and VM300 times out, do not keep patching CopilotKit. Scan reachable LAN model ports from VM300 and verify `/v1/models`:

```python
import socket, concurrent.futures, ipaddress
ports=[8000,8188]
ips=[str(ip) for ip in ipaddress.ip_network('192.168.1.0/24')]
def check(ip, port):
    s=socket.socket(); s.settimeout(0.25)
    try: s.connect((ip, port)); return (ip, port)
    except Exception: return None
    finally: s.close()
with concurrent.futures.ThreadPoolExecutor(max_workers=128) as ex:
    print(sorted(x for x in ex.map(lambda a: check(*a), [(ip,p) for ip in ips for p in ports]) if x))
```

In this incident the reachable vLLM endpoint was:

```text
http://192.168.1.138:8000/v1
model: cyankiwi/diffusiongemma-26B-A4B-it-AWQ-INT4
```

Update both the DB-backed provider and compose default so restarts do not revert:

```sql
update providers
set base_url='http://192.168.1.138:8000/v1', updated_at=datetime('now')
where slug='oracle-diffusion-vllm';
```

Patch `/opt/apps/WandGx-chat/docker-compose.yml` default `ORACLE_DIFFUSION_BASE_URL` to the reachable LAN URL, even if Chat should route through the proxy, because stale env defaults cause future confusion.

## Streaming failure UX fix

CopilotKit/AI SDK may treat OpenAI SSE `data: {"error":...}` as a stream failure and render no assistant message. For oracle-gateway streaming, convert diffusion-unavailable gateway exceptions into a normal assistant delta + finish event when you want the UI to receive a visible diagnostic message. Keep this honest: do not raw-fallback to Z.AI when `ORACLE_REQUIRE_DIFFUSION_FINAL=true`.

Proven LLM proxy source location:

```text
/opt/apps/LLM/src/llm_proxy/execute.py
```

Pattern:

- Add `ORACLE_STREAM_ERRORS_AS_ASSISTANT=true` default.
- In `execute_stream()`, when buffered gateway `execute_non_stream()` raises and policy mode is `oracle_gateway`, yield `StreamEvent(type="delta", text=<honest diffusion unreachable message>)` chunks and then `StreamEvent(type="finish", ...)`.
- Leave non-streaming behavior fail-closed with `503` so automation and logs still see the backend failure.

## Login/session repair pattern

Chat auth proxy lives at:

```text
/opt/apps/WandGx-chat/apps/web/src/app/api/auth/route.ts
/opt/apps/WandGx-chat/apps/web/src/lib/auth-client.ts
/opt/apps/WandGx-chat/apps/web/src/app/hooks/use-auth.tsx
/opt/apps/WandGx-chat/apps/web/src/app/components/auth-gate.tsx
/opt/apps/WandGx-chat/apps/web/src/app/components/auth-modal.tsx
```

Durable fixes:

- Add `GET /api/auth?action=google` to server-side call central Better Auth `/api/auth/sign-in/social` and return a `302` to Google. **Important:** copy/append the upstream `Set-Cookie` header(s) onto the product response. If the product proxy redirects to Google but drops `__Secure-better-auth.state` (`Domain=.wandgx.com`), real Google login returns `state_mismatch` on `identity.wandgx.com`.
- Add `GET /api/auth?action=session` to exchange an existing central Better Auth cookie for the product JWT, so returning users can bootstrap a chat session. For browser console cleanliness, a missing optional session can return `200 { authenticated: false }`; keep protected APIs such as `/api/copilotkit` at `401`.
- Normalize magic-link and signup `callbackURL` to absolute `https://chat.wandgx.com/` (or trusted `*.wandgx.com`) rather than relative `/` or `/build`.
- In the auth hook, attempt `bootstrapExistingSession()` on mount before showing the signed-out auth gate; otherwise users with central cookies can see a false login prompt/flicker.
- Keep protected `/api/copilotkit` unauthenticated response at `401`.

## Deployment and proof

Rebuild/restart only affected services:

```bash
cd /opt/apps/LLM && docker compose build proxy && docker compose up -d proxy
cd /opt/apps/WandGx-chat && docker compose build web && docker compose up -d web
```

Focused test command inside the chat container may need repo-root mounts because the Docker image only copies selected files:

```bash
docker compose run --rm --no-deps \
  -v /opt/apps/WandGx-chat/docker-compose.yml:/app/docker-compose.yml:ro \
  -v /opt/apps/WandGx-chat/.env.example:/app/.env.example:ro \
  web pnpm --filter web test -- src/app/tests/copilotkit-integration.test.ts src/app/tests/central-auth-config.test.ts
```

Expected proof after repair:

```text
/llm-proxy running healthy
/wandgx-chat-web-1 running healthy
https://chat.wandgx.com/ -> 200
/api/oracle/agui-status -> 200
/api/auth?action=session without cookie -> 401
/api/auth?action=google -> 302 to Google
/api/copilotkit without JWT -> 401
http://192.168.1.138:8000/v1/models -> 200
proxy stream oracle-1 -> content delta, no error object
```

For stream proof, send an authenticated `oracle-1` request to `http://127.0.0.1:9090/v1/chat/completions` using the chat service's private proxy key extracted inside VM300 without printing it; assert returned SSE contains `choices[].delta.content` and no top-level error object.

## Cron/watchdog lesson

The WandGx ops watchdog report can already contain the root signal. Check `/home/claw/.hermes/cron/output/<job_id>/...` or `cronjob list` before deep debugging. In this incident, the report flagged `wandgx-chat-web-1 upstream_error` and `llm-proxy oracle-diffusion-vllm failed`, matching the live logs.