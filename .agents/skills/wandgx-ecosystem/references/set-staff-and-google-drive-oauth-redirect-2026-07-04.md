# SET staff designation and Google Drive OAuth redirect pitfall — 2026-07-04

Use this when the user asks to make a central/SET account staff, or reports a blank `identity.wandgx.com` page after connecting Google Drive from SET.

## SET staff designation pattern

SET has two relevant layers:

1. Central Better Auth identity on VM302 (`platform-identity-postgres`, DB `wandgx_identity`, table `public."user"`).
2. SET app metadata on VM301 (`set-postgres-1`, DB `set`, tables `profiles` and `platform_staff`).

For a SET staff request, verify/update both when appropriate:

```sql
-- VM301 / SET metadata: profile and platform staff row
select p.id, p.email, p.full_name, ps.staff_role, ps.status, ps.permissions
from profiles p
left join platform_staff ps on ps.user_id = p.id
where lower(p.email)=lower('<email>');

insert into platform_staff (user_id, staff_role, permissions, status, notes)
select id, 'super_admin', array['*']::text[], 'active', '<reason/date>'
from profiles
where lower(email)=lower('<email>')
on conflict (user_id) do update set
  staff_role=excluded.staff_role,
  permissions=excluded.permissions,
  status=excluded.status,
  notes=excluded.notes,
  updated_at=now()
returning user_id, staff_role, status, permissions;
```

```sql
-- VM302 / central identity: Better Auth role field
update public."user"
set role='STAFF', "updatedAt"=now()
where lower(email)=lower('<email>')
returning id,email,name,role,"emailVerified";
```

Verification should show:

- SET `platform_staff.status = 'active'`
- SET `staff_role` is the requested elevated role (usually `super_admin` for owner/admin recovery)
- SET `permissions` contains `*` when full platform access is intended
- central Better Auth `public."user".role = 'STAFF'` if the user explicitly asked for database status/role to be `STAFF`

Do not print secrets. Email/user IDs are okay when the user named the account.

## Google Drive blank `identity.wandgx.com` page pitfall

If Google Drive connect from SET lands on a blank white `identity.wandgx.com` page, distinguish these cases:

1. Central identity health: probe `https://identity.wandgx.com/`, `/api/auth/ok`, `/api/auth/jwks`, and `/api/auth/readiness`.
2. SET auth/JWKS health: probe `https://auth.trainwithset.com/api/auth/jwks` and SET backend health.
3. SET Google OAuth callback redirect target.

Durable pitfall: SET backend `app/api/routes/integrations.py` historically used `settings.better_auth_url` inside `_google_redirect()` / `_dropbox_redirect()`. In production `BETTER_AUTH_URL` can point to central identity (`identity.wandgx.com`), so a successful Drive OAuth callback redirects to identity instead of the SET frontend, producing a blank identity page on mobile Safari.

Preferred fix pattern:

```py
import os


def _frontend_redirect_base() -> str:
    return (
        os.environ.get("SET_PUBLIC_URL")
        or os.environ.get("APP_PUBLIC_URL")
        or settings.better_auth_url
        or "http://localhost:5173"
    ).rstrip("/")


def _google_redirect(params: Dict[str, str]) -> str:
    frontend = _frontend_redirect_base()
    return f"{frontend}/documents?{urlencode(params)}"


def _dropbox_redirect(params: Dict[str, str]) -> str:
    frontend = _frontend_redirect_base()
    return f"{frontend}/documents?{urlencode(params)}"
```

Then run at least:

```bash
python3 -m py_compile SET-backend/app/api/routes/integrations.py
```

Deploy/restart only the affected SET backend service, then prove callback behavior with a fake/blocked callback that does not require a real Google grant:

```bash
curl -sS -I 'https://api.trainwithset.com/api/integrations/google/callback?error=access_denied&state=fake' | grep -i '^location:'
```

Expected location should start with:

```text
https://trainwithset.com/documents?
```

not:

```text
https://identity.wandgx.com/
```

Also verify the happy-path prerequisites still report healthy/configured:

- `https://api.trainwithset.com/api/system/health` returns healthy
- `https://identity.wandgx.com/api/auth/jwks` returns 200
- `https://auth.trainwithset.com/api/auth/jwks` returns 200

## Source reconciliation and push pitfall

After a live VM301 archive patch, reconcile the same change into the canonical SET source worktree before declaring the fix durable. In this incident the source path was `/Users/gucci/Documents/GitHub/SET/SET-backend/app/api/routes/integrations.py` on the Mac mini. Use a narrow source patch, run `python3 -m py_compile SET-backend/app/api/routes/integrations.py`, commit, then push `main`.

If `git fetch` on the Mac source worktree fails with a message like `fatal: bad object refs/remotes/origin/HEAD 2`, inspect `.git/refs/remotes/origin/` for duplicate Finder-style or stale lock files such as `HEAD 2`, `HEAD 2.lock`, `HEAD 3.lock`, etc. Removing only those duplicate/lock ref files allowed `git fetch origin main`, `git rebase origin/main`, and `git push origin main` to complete. Do not delete the valid `.git/refs/remotes/origin/HEAD` or `main` refs.

## Approval / side-effect note

Changing DB roles or live OAuth redirect code is a production mutation. If the tool asks for approval and times out, stop and report the unapplied patch; do not keep trying alternate mutation routes without consent.