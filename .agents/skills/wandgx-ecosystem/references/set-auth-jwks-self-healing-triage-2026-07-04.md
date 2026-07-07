# SET auth JWKS self-healing triage — 2026-07-04

Use this when SET public pages and backend health look green, but users report auth/session/JWT/JWKS errors or the ops watchdog sees Better Auth failures from `set-auth-1`.

## Symptom

Public checks can pass:

```text
https://trainwithset.com/ -> 200
https://api.trainwithset.com/api/system/health -> 200 healthy
https://auth.trainwithset.com/api/auth/ok -> 200 {"ok":true}
```

But auth JWKS fails:

```text
https://auth.trainwithset.com/api/auth/jwks -> HTTP 500
```

`set-auth-1` logs show:

```text
ERROR [Better Auth]: relation "jwks" does not exist
# SERVER_ERROR: error: relation "jwks" does not exist
```

Read-only schema proof:

```text
docker exec set-postgres-1 psql -U set -d set -Atc "select coalesce(to_regclass('public.jwks')::text,'MISSING');"
# MISSING
```

## Root cause class

SET auth is running Better Auth with JWT/JWKS support, but the production auth database schema is missing the `jwks` table required by the Better Auth JWT plugin. The running plugin calls `adapter.findMany({ model: "jwks" })` and expects fields:

- `publicKey` string required
- `privateKey` string required
- `createdAt` date required
- `expiresAt` date optional

This can break auth/JWT/JWKS flows even while landing pages, `/api/system/health`, and `/api/auth/ok` pass.

## Self-healing / watchdog lesson

The ops watchdog must include `set-auth-1` in the VM301 container list. Watching only `set-frontend-1`, `set-backend-1`, celery, redis, and runtime misses this class of user-facing auth failure.

The watchdog should also filter noisy access-log and normal-auth lines so real incidents are not drowned out:

- normal `authenticated: true/false` log lines
- expected `401` for protected `/v1/models` without an API key
- successful `HTTP/1.1 2xx/3xx OK` client requests
- stack continuation lines once the headline error is captured
- nginx access log lines with status `<500`

Keep the triage/deploy gate locked:

- write incident JSONL and triage prompt/report
- `triage.sla_minutes = 20`
- `human_deploy_approval_required = true`
- no automatic DB mutation/restart/deploy from the watchdog

## Read-only confirmation commands

Do not print secrets. Redact `DATABASE_URL`, auth secrets, cookies, JWTs, SMTP passwords, OAuth secrets, and Better Auth secret values.

```bash
curl -sS -w '\nHTTP %{http_code}\n' https://auth.trainwithset.com/api/auth/jwks
ssh root@192.168.1.249 'docker logs --since=30m set-auth-1 2>&1 | egrep -i "relation \\\"jwks\\\"|SERVER_ERROR|jwks|ERROR" | tail -80'
ssh root@192.168.1.249 'docker exec set-postgres-1 psql -U set -d set -Atc "select coalesce(to_regclass('"'"'public.jwks'"'"')::text,'"'"'MISSING'"'"');"'
ssh root@192.168.1.249 'docker exec set-auth-1 node -e "const u=new URL(process.env.DATABASE_URL); console.log({host:u.hostname, database:u.pathname.slice(1), user:u.username})"'
ssh root@192.168.1.249 'cd /opt/apps/SET && find . -maxdepth 4 -iname "*auth*" -o -iname "*migration*" | sed -n "1,120p"'
```

## Minimal safe fix plan after approval

1. Inspect SET auth source and migration mechanism. Prefer Better Auth's migration generator if present; avoid guessing table naming conventions.
2. Add the missing Better Auth JWT/JWKS migration in source.
3. Apply the migration to VM301 Postgres.
4. Restart/recreate only `set-auth-1` if required.
5. Verify:
   - `/api/auth/jwks` returns 200 JSON, not 500.
   - no new `relation "jwks" does not exist` log lines appear.
   - `/login` still renders.
   - auth/session/token paths return correct 200/401/403 states, not 500.

## Proven production fix applied

On VM301 `/opt/apps/SET`, the approved repair was:

1. Add an idempotent source-side migration at `SET-auth/database/001_better_auth_jwks.sql`:

```sql
create extension if not exists pgcrypto;
create table if not exists public.jwks (
  id text primary key default gen_random_uuid()::text,
  "publicKey" text not null,
  "privateKey" text not null,
  "createdAt" timestamp with time zone not null default now(),
  "expiresAt" timestamp with time zone null,
  alg text null,
  crv text null
);
create index if not exists jwks_created_at_idx on public.jwks ("createdAt" desc);
```

2. Apply it directly through `set-postgres-1` with `ON_ERROR_STOP=1`.
3. Trigger `https://auth.trainwithset.com/api/auth/jwks` once. Better Auth creates the first RSA key row automatically.
4. Verify:
   - `/api/auth/jwks` returns 200 with a `keys` array.
   - `select count(*) from public.jwks;` returns at least `1`.
   - no new `relation "jwks" does not exist` or `SERVER_ERROR` lines appear in `set-auth-1` logs after the fix.

No `set-auth-1` restart is required for this specific table-missing repair once the DB migration is applied.

## QA pitfall

A broad browser QA pass that only visits `trainwithset.com`, `/login`, `api.trainwithset.com/`, and `auth.trainwithset.com/` may miss this. Add direct JWKS/token probes when the user reports SET auth errors or when testing self-healing triage.