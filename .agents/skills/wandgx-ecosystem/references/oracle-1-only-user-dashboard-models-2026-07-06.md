# Oracle-1-only logged-in dashboard model cleanup (2026-07-06)

Use when the user asks to remove all non-Oracle models from logged-in WandGx dashboards, model-route lists, or chat model selectors.

## Scope

Surfaces involved:

- Oracle / WandGx Chat on VM300: `/opt/apps/WandGx-chat`
  - Container: `wandgx-chat-web-1`
  - Public: `https://chat.wandgx.com`
  - Model metadata: `apps/web/src/app/lib/models.ts`
  - Model context / persisted selection: `apps/web/src/app/lib/model-context.tsx`
  - Header selector: `apps/web/src/app/components/model-switcher.tsx`
  - CopilotKit runtime and WandGx model-list tools: `apps/web/src/app/api/copilotkit/route.ts`
- WandGx vNext on VM300: `/opt/apps/WandGx-vNext`
  - API: `wandgx-vnext-api-1`, public `https://api.wandgx.com`
  - Web/admin dashboard: `wandgx-vnext-web-1`, `wandgx-vnext-admin-1`
  - Runtime store source: `apps/api/src/control-plane-runtime-store.mjs`
  - Persisted runtime records: Postgres container `wandgx-vnext-postgres-1`, table `control_plane_runtime_records`, namespace `control-plane-runtime`, collections `modelRoutes` and `modelRouteVersions`
  - Dashboard/static labels: `apps/web/admin-dashboard.html`, `apps/web/src/shell/model-routing-live-beta-decision.mjs`, `apps/web/src/shell/workspace-shell.ts`, `apps/web/src/admin/admin-dashboard.ts`

## Durable lessons

- Source edits are not enough for vNext model routes. The API uses persisted Postgres runtime records when `WANDGX_CONTROL_PLANE_STORE=postgres`; old `glm-5.2` / `Standard AI` records can survive a source seed change. Patch both source defaults and persisted rows.
- Public `/v1/models` being Oracle-only is not proof that logged-in dashboards are Oracle-only. Also verify authenticated `GET /v1/model-routes` and `POST /v1/model-routes/resolve` with a beta/admin session.
- Chat `MODELS` being one entry is not enough: server-side CopilotKit tools (`wandgxListModels`, `wandgxUserModels`) may still fetch vNext `/model-routes` and expose other model labels inside chat/tool surfaces. Force those tool responses to an Oracle-only list when customer dashboards must be Oracle-only.
- Header/request model guards should treat any non-`oracle-1` `x-oracle-model` as `oracle-1`; do not leave hidden client-selectable GLM/Turbo/Vision aliases in public chat runtime.
- When only one public model exists, render the model header as a static identity, not a clickable selector.
- Remove dashboard copy such as `Standard AI`, `Enhanced AI`, `glm-5.2`, `Oracle Tool Proxy`, `oracle-tool-proxy`, and provider-specific staff model copy from user-facing/dashboard bundles. Keep private provider config, proxy/tool route IDs, and internal council/tool labels out of customer/dashboard UI.

## Proven sequence

1. In `/opt/apps/WandGx-chat`, audit:
   - `apps/web/src/app/lib/models.ts`
   - `apps/web/src/app/lib/model-context.tsx`
   - `apps/web/src/app/components/model-switcher.tsx`
   - `apps/web/src/app/api/copilotkit/route.ts`
2. Ensure `MODELS` contains only `oracle-1` and the switcher becomes static for `MODELS.length <= 1`.
3. In `apps/web/src/app/api/copilotkit/route.ts`:
   - add an `ORACLE_ONLY_MODEL_ROUTES` response object,
   - make `wandgxListModels` and `wandgxUserModels` return it,
   - set `MODEL_MAP` empty or otherwise prevent GLM/Turbo/Vision public model routing,
   - force `resolveModelRoute()` fallback to `oracleProxyProvider` / `ORACLE_PROXY_MODEL` for every non-Oracle header.
4. In `/opt/apps/WandGx-vNext`, patch `apps/api/src/control-plane-runtime-store.mjs` so model route responses normalize to Oracle-1 only:
   - `routeKey: oracle-1`
   - `name/userFacingLabel/capabilityLabel: Oracle-1`
   - `providerDecision.provider: wandgx`
   - `providerDecision.model: oracle-1`
   - `fallbackRouteKey/fallbackChain: oracle-1`
   - `listModelRoutes()` should return a single Oracle-1 route.
5. Patch dashboard/client label sources:
   - `apps/web/admin-dashboard.html`
   - `apps/web/src/shell/model-routing-live-beta-decision.mjs`
   - `apps/web/src/shell/workspace-shell.ts`
   - `apps/web/src/admin/admin-dashboard.ts`
6. Patch persisted vNext Postgres rows as well as source:
   - container: `wandgx-vnext-postgres-1`
   - db: `wandgx_vnext_dev`
   - table: `control_plane_runtime_records`
   - namespace: `control-plane-runtime`
   - collections: `modelRoutes`, `modelRouteVersions`
7. Rebuild/restart:
   - Chat: `docker compose build web && docker compose up -d web` in `/opt/apps/WandGx-chat`
   - vNext web assets: `docker compose exec -T web pnpm --filter @wandgx/web build` in `/opt/apps/WandGx-vNext`
   - vNext services: restart/recreate `api`, `web`, and `admin` as needed.

## Verification gates

- API health:
  - `http://127.0.0.1:31380/health` returns 200.
- Authenticated vNext model routes using a beta/admin session:
  - `GET /v1/model-routes` returns exactly one route with `model: oracle-1`, `label: Oracle-1`, `routeKey: oracle-1`, `provider: wandgx`.
  - `POST /v1/model-routes/resolve` returns decision `model: oracle-1`, `provider: wandgx`, and user-facing label `Oracle-1`.
- Persisted DB proof:
  - `control_plane_runtime_records` has only one `modelRoutes` row and one `modelRouteVersions` row for the namespace, both normalized to Oracle-1.
- Bundle/source scans for dashboard/client surfaces should show no matches for:
  - `Standard AI`
  - `Enhanced AI`
  - `glm-5.2`
  - `glm-5-turbo`
  - `glm-5v-turbo`
  - `gpt-*`, `claude-*`, `deepseek`, `qwen`, `llama` in client/dashboard surfaces
  - `diffusion`, `oracle-diffusion`
  - `Oracle Tool Proxy`, `oracle-tool-proxy`, `tool-proxy`
- Scan only client/dashboard bundles for user-visible proof; server API bundles may contain provider/tool library names from dependencies and are not customer dashboard evidence unless rendered or returned.

## User style/workflow signal

When the user is angry and repeats an instruction, do not over-explain or ask if they mean public vs logged-in dashboards. Treat it as an implementation request, make the change, and return concise proof: exact endpoint responses, services rebuilt, and forbidden-string scans.