# SET core-flow persistence repair pattern (2026-07-03)

Use this reference when SET production shows database drift, partial writes, missing repository support, or core-flow endpoints failing after writes.

## Durable lesson

SET backend routes can look product-complete while still being unsafe if a table is missing from the Postgres metadata repository allow-list, JSONB adapter list, startup healthcheck, or migration repair file. For core-flow repair, fix all four surfaces together:

1. `SET-backend/app/services/data_store.py`
   - Add table to `PostgresMetadataQuery.ALLOWED_COLUMNS`.
   - Add JSONB columns to `POSTGRES_JSONB_COLUMNS`.
   - Add table to `PostgresMetadataClient.healthcheck()` `to_regclass` list.
   - Add information_schema column alias and required-column validation.
   - Keep unsupported customer-data tables fail-closed; do not fall back to process-local storage in production.
2. `SET-backend/database/045_core_product_schema_repair.sql`
   - Create/repair missing tables idempotently with `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.
   - Add missing columns with `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
   - Use deterministic unique constraints/indexes for idempotent sample/demo flows.
3. `SET-backend/tests/test_services/test_metadata_postgres_repository.py`
   - Add contract tests for bound parameters, JSONB adaptation, `on_conflict`, and healthcheck required-table/required-column lists.
4. Focused and broad verification
   - Run targeted API/repository tests first.
   - Run full `tests/test_api tests/test_services` before deploy when the persistence surface is broad.
   - Apply migration to production Postgres before rebuilding backend/celery.
   - Verify public health and protected core endpoints return clean 401/403/404/503 states, not 500s.

## Tables covered in this repair class

Core SET promise tables include:

- workspace/onboarding: `tenants`, `tenant_members`, `roles`, `user_roles`, `departments`, `department_members`, `tenant_quota_config`, `quota_usage`
- documents/sources: `document_sources`, `source_sync_jobs`, `source_sync_errors`, `documents`, `document_chunks`, `document_versions`, `local_document_handles`, `saved_searches`
- AI/tutor/search/chat: `ai_conversations`, `ai_messages`, `tutor_sessions`, `research_sessions`
- generated assets/readiness: `learning_paths`, `learning_path_steps`, `learning_path_assignments`, `quizzes`, `quiz_attempts`, `flashcard_decks`, `flashcards`, `h5p_content`, `h5p_content_versions`, `h5p_generation_queue`, `activity_feed`, `activity_events`, `skill_mastery`, `achievements`, `user_points`, `leaderboards`, `leaderboard_participants`
- notifications/integrations/ops: `notifications`, `notification_preferences`, `push_subscriptions`, `user_google_tokens`, `google_oauth_states`, `email_queue`, `sync_queue`, `vms`

## Production deployment pattern used

On VM301 (`/opt/apps/SET`):

1. Back up changed deployed files under `.hermes-backups/<utc-stamp>/`.
2. Copy repaired files into `/opt/apps/SET`.
3. Apply migration directly through the Postgres container:
   - `docker exec -i set-postgres-1 psql -U set -d set -v ON_ERROR_STOP=1 < SET-backend/database/045_core_product_schema_repair.sql`
4. Rebuild only affected services:
   - `docker compose build backend celery-worker`
   - `docker compose up -d backend celery-worker`
5. Verify:
   - `docker compose ps` shows backend/celery healthy.
   - `https://api.trainwithset.com/api/system/health` returns 200 healthy.
   - `https://trainwithset.com/` and `https://set.wandgx.com/` return 200.
   - Protected core routes return clean auth errors when unauthenticated, not 500.
   - Browser demo page loads with no JS errors.

## Pitfalls

- Do not only create production tables. If the table is missing from `ALLOWED_COLUMNS`, code still fails closed.
- Do not only add allow-list entries. If healthcheck omits `to_regclass`/column aliases, production can boot into a half-working state.
- Do not rely on Cloudflare-proxied public endpoint probes for protected API shape; use LAN `http://192.168.1.249:8000` for clean unauthenticated status checks when public WAF returns 403/1010.
- Use correct route prefixes when smoking core flows:
  - home is `/api/home/overview`, not `/api/home`
  - search global is `/api/search/global`, not `/api/search?q=...`
  - tutor is under `/api/chat/tutor`, not `/api/tutor`
- Postgres quoting through nested SSH is fragile. For exact SQL probes, feed SQL via heredoc to remote `docker exec -i ... psql` instead of embedding nested single quotes in one command.
