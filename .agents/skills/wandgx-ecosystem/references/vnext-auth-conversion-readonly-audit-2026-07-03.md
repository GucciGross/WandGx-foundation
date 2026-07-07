# WandGx vNext auth/conversion read-only launch audit — 2026-07-03

Use this reference when asked to audit WandGx vNext self-service auth, signup/register conversion, or public launch readiness without editing. Keep Paint Quote / PainterQuote excluded unless explicitly included.

## Scope and constraints

- Target VM: VM300 `192.168.1.248`.
- Deployed root: `/opt/apps/WandGx-vNext`.
- Public app routes: `https://wandgx.com`, `/app`, `/build`, `/register`, `/signup`, `/sign-up`.
- Do not edit during read-only launch audits.
- Do not include Paint Quote / PainterQuote findings when the user excludes them.
- Treat deployed `/opt/apps/WandGx-vNext` as archive/live deploy, not durable canonical source: `.git` may be absent.

## Exact ownership found

Runtime web container:

- `wandgx-vnext-web-1`
- image `node:24-bookworm-slim`
- bind mount `/opt/apps/WandGx-vNext:/workspace`
- command:
  - `node scripts/local-dev-138.mjs serve-static --service web --root apps/web --port 31381 --api-host api --api-port 31380 --default-file index.html`

Route alias owner:

- `/opt/apps/WandGx-vNext/scripts/local-dev-138.mjs`
- `PUBLIC_WORKSPACE_ROUTE_ALIASES` maps `/app`, `/build`, `/workspace`, `/register`, `/signup`, `/sign-up` to `workspace-shell.html`.
- `publicWorkspaceRouteAlias()` normalizes trailing slashes and serves the alias before static file resolution.

Top-nav and auth markup owners:

- `/opt/apps/WandGx-vNext/apps/web/workspace-shell.html`
  - top-nav Sign in/Register: lines around `20-34`.
  - auth prompt Sign in/Register: lines around `37-42`.
  - legacy/static account tab markup: lines around `418-436`.

Visible auth/signup behavior owner:

- `/opt/apps/WandGx-vNext/apps/web/src/shell/wandgx-real-build.mjs`
  - `signupRequestedByLocation()` returns true when `intent=signup`, hash contains `signup`, or pathname is `/register`, `/signup`, `/sign-up`.
  - `showAuth('register')` opens the visible Create account modal.
  - top-nav buttons bind with `data-action="open-auth"` and `data-action="open-register"`.
  - `registerAccount()` posts to `/api/auth/sign-up/email`.

Landing page conversion CTA owner:

- `/opt/apps/WandGx-vNext/apps/web/index.html`
  - observed public CTAs point at `/app?intent=signup#account-auth-tab-signup`.

Legacy account flow owner:

- `/opt/apps/WandGx-vNext/apps/web/src/shell/account-auth-flow.mjs`
  - manages static tabbed account form when loaded.
  - At audit time `workspace-shell.html` did not include this module; visible behavior came from `wandgx-real-build.mjs`.

## Efficient read-only command pattern

From a local Hermes shell, inspect VM300 with SSH and Python to avoid noisy raw greps:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 root@192.168.1.248 'python3 - <<'"'"'PY'"'"'
import os, json, subprocess
root = "/opt/apps/WandGx-vNext"
print("HOST_PATH_EXISTS", root, os.path.isdir(root))
print("IS_GIT_WORKTREE", os.path.isdir(os.path.join(root, ".git")))
out = subprocess.check_output(["docker", "ps", "--format", "{{.Names}} {{.Ports}}"], text=True)
print("\n".join(line for line in out.splitlines() if "wandgx-vnext" in line))
PY'
```

Use a deployed-source sweep for route/auth strings:

```bash
ssh root@192.168.1.248 'python3 - <<'"'"'PY'"'"'
import os
root = "/opt/apps/WandGx-vNext"
terms = ["/register", "/signup", "/sign-up", "intent=signup", "account-auth-tab-signup", "Sign in", "Register", "Create account", "openAccountModal", "data-auth-intent"]
for sr in [root + "/apps/web", root + "/scripts"]:
    for dirpath, dirnames, filenames in os.walk(sr):
        dirnames[:] = [d for d in dirnames if d not in {"node_modules", ".git", "vendor", "assets", ".pnpm-store"}]
        for fn in filenames:
            if not fn.endswith((".html", ".mjs", ".js", ".css", ".json", ".ts", ".tsx", ".md")): continue
            p = os.path.join(dirpath, fn)
            data = open(p, encoding="utf-8", errors="ignore").read()
            if any(t in data for t in terms):
                print(os.path.relpath(p, root))
PY'
```

Verify LAN routes from inside VM300 to avoid raw-IP approval friction:

```bash
ssh root@192.168.1.248 'python3 - <<'"'"'PY'"'"'
import urllib.request
for path in ["/", "/app", "/build", "/register", "/signup", "/sign-up", "/app?intent=signup"]:
    with urllib.request.urlopen("http://localhost:31381" + path, timeout=8) as r:
        html = r.read(300000).decode("utf-8", "ignore")
        print(path, r.status, "workspace", "data-testid=\"wandgx-real-build-app\"" in html, "register", "data-testid=\"real-register\"" in html)
PY'
```

Then use browser tools for public rendered behavior, not just HTML markers:

- `/register`, `/signup`, `/sign-up`, and `/app?intent=signup#account-auth-tab-signup` should open a visible Create account modal.
- `/app` should not auto-open auth; top-nav Sign in and Register should be visible and clickable.
- `/` landing should expose a conversion CTA; check whether Sign in is also present if the user asks for both top-nav actions.

## Findings and patch recommendations from the 2026-07-03 audit

Current behavior was good enough to prove signup routes are live:

- `/register`, `/signup`, `/sign-up`, `/app?intent=signup` served workspace and opened the visible Create account modal.
- `/app` showed top-nav Sign in/Register; click Sign in opened Sign in modal, click Register opened Create account modal.

Minimal patch recommendations:

1. Canonicalize public signup CTAs from `/app?intent=signup#account-auth-tab-signup` to `/register` or `/signup`. The hash targets a legacy/static hidden tab while the visible modal is controlled by `wandgx-real-build.mjs`.
2. Add an explicit Sign in link next to Create account on the landing page top nav if launch criteria require both customer auth actions at top level.
3. If old hash URLs must remain supported, either bind/import `account-auth-flow.mjs` in `workspace-shell.html`, synchronize the static panel mode from `wandgx-real-build.mjs`, or remove the hash from all public CTAs.
4. Optional no-JS hardening: make top-nav Sign in/Register anchors with JS interception instead of buttons-only controls.

## Reporting shape

Report:

- exact VM and deployed path,
- exact owning files and line ranges,
- exact verification commands,
- current public behavior from rendered browser checks,
- minimal patch recommendations,
- no edits performed.
