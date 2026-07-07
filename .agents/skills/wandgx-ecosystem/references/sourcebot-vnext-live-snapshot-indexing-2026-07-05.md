# Sourcebot WandGx-vNext Live Snapshot Indexing — 2026-07-05

Use this when Sourcebot needs WandGx-vNext context for auth/UI incident work and the GitHub repo is not directly accessible from the Sourcebot host.

## Proven topology

- Sourcebot host: `192.168.1.119`
- Sourcebot URL: `http://192.168.1.119:3377`
- Sourcebot version observed: `v5.0.2`
- Sourcebot working dir: `/home/sandbox/sourcebot-workspace`
- Config: `/home/sandbox/sourcebot-workspace/config.json`
- Compose: `/home/sandbox/sourcebot-workspace/docker-compose.yml`
- Local indexed repo mount target: `/repos/WandGx-vNext`
- Host snapshot path: `/home/sandbox/WandGx-vNext`

## Pattern

1. If GitHub clone/pull from the Sourcebot box fails due credentials, prefer a **sanitized live VM300 snapshot** for production incidents because it reflects what `wandgx.com` is serving.
2. Copy from VM300 `/opt/apps/WandGx-vNext`, excluding secrets/runtime/build artifacts:
   - `.env*`
   - `node_modules`
   - `.pnpm-store`
   - `.git`
   - `.next`, `dist`, `build`, `coverage`
   - logs/tmp
   - `*.pem`, `*.key`, `*.p12`, `*.sqlite`, `*.sqlite3`, `*.db`
3. On the Sourcebot host, place it at `/home/sandbox/WandGx-vNext`.
4. Initialize local git metadata so Sourcebot accepts it as a valid git repo:
   - `git init`
   - `git branch -M main`
   - commit the snapshot
   - set `remote.origin.url` to `https://github.com/GucciGross/WandGx-vNext.git`
5. Add to `config.json`:

```json
"local-wandgx-vnext": {
  "type": "git",
  "url": "file:///repos/WandGx-vNext",
  "revisions": { "branches": ["main"] }
}
```

6. Add a read-only compose mount:

```yaml
- "/home/sandbox/WandGx-vNext:/repos/WandGx-vNext:ro"
```

7. Recreate only Sourcebot after validating compose:

```bash
cd /home/sandbox/sourcebot-workspace
docker compose config --quiet
docker compose up -d sourcebot
```

8. Trigger Sourcebot internal sync from inside the container because the worker API is not public:

```bash
docker exec sourcebot sh -lc 'curl -sS -X POST http://127.0.0.1:3060/api/sync-connection -H "Content-Type: application/json" --data "{\"connectionId\":5}"'
```

Use the current DB connection id for `local-wandgx-vnext`; `5` was the value in this session.

## Verification

- `GET http://192.168.1.119:3377/api/version` returns `v5.0.2`.
- `GET http://192.168.1.119:3377/api/repos?perPage=100` includes `github.com/GucciGross/WandGx-vNext`.
- Sourcebot MCP `list_repos` includes `github.com/GucciGross/WandGx-vNext`.
- Sourcebot MCP `search_code` scoped to `github.com/GucciGross/WandGx-vNext` finds production files such as:
  - `apps/api/src/account-auth.mjs`
  - `apps/api/src/server.mjs`
  - `apps/web/src/shell/wandgx-real-build.mjs`
  - `apps/web/src/shell/workspace-shell.css`
  - `scripts/check-account-auth-flow.mjs`

## Pitfalls

- Sourcebot will silently complete a connection sync with warnings and no repo if `/repos/WandGx-vNext` is missing or the local git repo has no `remote.origin.url`.
- Do not expose copied `.env` or token/cookie/session material in Sourcebot. Use sanitized snapshots only.
- Public UI “Trigger sync” can fail for guest users; use the internal worker API from inside the `sourcebot` container when operator access is available.
