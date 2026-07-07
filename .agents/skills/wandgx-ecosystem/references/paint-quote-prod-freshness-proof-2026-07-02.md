# Paint Quote prod freshness proof — 2026-07-02

Use this when the user asks whether Paint Quote code is committed, pushed, merged to main, and actually hosted on prod.

## Durable pattern

Paint Quote health can return `deployment.commit: null`, so do not rely on `/health` alone to prove runtime freshness. Prove all three boundaries separately:

1. **Source control**
   - In the source repo, verify branch is `main`.
   - `git fetch origin main --prune`.
   - Verify `git rev-parse HEAD` equals `git rev-parse origin/main`.
   - Verify `git status --short` is empty.
   - Report recent commits relevant to the deployed changes.

2. **Prod host/container**
   - Target from ecosystem topology: LXC123 / `paintquote-lxc`, LAN `192.168.1.183`, deploy dir `/opt/apps/paint-quote`, service/container `painterquote-web`.
   - Verify the container is running and Docker health is healthy.
   - Capture container image ID and creation time.
   - Check recent `painterquote-web` logs for request/server error keywords.

3. **Live runtime bundle**
   - Fetch public HTML from both `https://painter.wandgx.com` and `https://paint.wandgx.com` plus LAN `http://192.168.1.183:3010`.
   - Extract current hashed JS assets.
   - Hash the served primary bundle from public and LAN origins.
   - Hash the same bundle path inside the running container, e.g. `/app/dist/js/<hash>.js`.
   - Treat matching public + LAN + container hashes as runtime freshness proof when health commit metadata is null.
   - Also scan the live bundle for expected new strings and removed old strings. For the 2026-07-02 auth/PWA work, expected examples were Settings install copy, `Sign up here`, and `Send Reset Link`; removed examples were `Continue with Company Identity`, `pwa-install-dismissed`, and internal central-identity blocker copy.

## Reporting shape

Be explicit about each boundary:

- `main` / `origin/main` status and exact HEAD.
- Prod target and running container/image proof.
- Public health responses.
- Bundle hash parity across public, LAN, and container.
- String presence/absence proof for the change.

If health has `deployment.commit: null`, say that directly and explain that runtime freshness was proven by bundle hash parity and expected string checks instead of commit metadata.
