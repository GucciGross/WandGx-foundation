# SET mobile Training Copilot launcher bottom-nav clearance — 2026-07-04

Use this when the SET `Training copilot` floating launch button blocks the mobile bottom nav (`Mission`, `Vault`, `Paths`, `Settings`) or sits too low on iOS/Safari.

## Symptom

On mobile, the closed CopilotKit launcher pill (`Training copilot`) is fixed near the bottom-right and overlaps the fixed `MobileBottomNav` bar. The screenshot shows the pill centered over/near `Paths` and `Settings`, making the nav hard to tap.

## Root cause pattern

`TrainingCopilotShell.jsx` used a Tailwind fixed-bottom utility:

```jsx
className="set-copilot-launch fixed bottom-5 right-5 ..."
```

`copilotkit.css` only added:

```css
.set-copilot-launch {
  margin-bottom: env(safe-area-inset-bottom, 0);
}
```

This respects iOS safe area but not the app's own fixed mobile bottom nav (`h-16` plus safe-area padding). The result is visual overlap.

## Preferred fix

Let the scoped CSS own the bottom offset, and remove the Tailwind `bottom-5` utility so it cannot override or fight the mobile rule.

```jsx
className="set-copilot-launch fixed right-5 z-40 inline-flex ..."
```

```css
/* Launch button clears mobile bottom navigation and safe areas. */
.set-copilot-launch {
  bottom: calc(1.25rem + env(safe-area-inset-bottom, 0px));
}

@media (max-width: 640px) {
  .set-copilot-launch {
    bottom: calc(5rem + env(safe-area-inset-bottom, 0px));
    right: max(0.75rem, env(safe-area-inset-right, 0px));
    max-width: calc(100vw - 1.5rem);
  }

  .set-copilot-panel {
    max-width: 100%;
    border-left: 0;
  }
}
```

Why `5rem`: SET mobile bottom nav uses `h-16` (4rem). Add roughly `1rem` visual gap above it, plus safe-area inset.

## Regression test pattern

In `TrainingCopilotProvider.test.jsx`, assert the launcher still renders and no longer carries `bottom-5`:

```jsx
const launchButton = screen.getByRole('button', { name: /Open training copilot/i });
expect(launchButton).toBeInTheDocument();
expect(launchButton.className).toContain('set-copilot-launch');
expect(launchButton.className).not.toContain('bottom-5');
```

## Verification commands

Use containerized Node if the host lacks node/pnpm; do not record that as a durable failure.

```bash
cd /opt/apps/SET

docker run --rm -v /opt/apps/SET/SET-frontend:/app -w /app node:20-alpine \
  sh -lc "npm test -- src/components/copilotkit/__tests__/TrainingCopilotProvider.test.jsx --run"

docker run --rm -v /opt/apps/SET/SET-frontend:/app -w /app node:20-alpine \
  sh -lc "npm run build"
```

Deploy with care: `docker compose up -d --build frontend` may also rebuild/recreate dependent services in this compose graph. Afterward verify:

```bash
docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' set-frontend-1
docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' set-backend-1
docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' set-copilotkit-runtime-1
curl -sS -A 'Mozilla/5.0 Hermes QA' https://api.trainwithset.com/api/system/health
```

If doing final public asset readback, remember Cloudflare/browser cache may still serve a previous CSS asset briefly; use a cache-busting query and inspect the running `set-frontend-1` container's `/usr/share/nginx/html/index.html` as the deployment source of truth.

## Source reconciliation + public readback pattern

This class of SET live UI fix often starts as an emergency patch in the VM301 deployed archive (`/opt/apps/SET`), but `/opt/apps/SET` is not a git worktree. After deploying and verifying the live archive, reconcile the exact changed files back into the canonical GitHub repo (`GucciGross/SET`) before calling the task complete.

Minimal source reconciliation flow:

```bash
mkdir -p /home/claw/work
if [ -d /home/claw/work/SET/.git ]; then
  cd /home/claw/work/SET
  git fetch origin main
  git checkout main
  git reset --hard origin/main
else
  gh repo clone GucciGross/SET /home/claw/work/SET -- --branch main
fi

cd /home/claw/work/SET
scp root@192.168.1.249:/opt/apps/SET/SET-frontend/src/components/copilotkit/TrainingCopilotShell.jsx SET-frontend/src/components/copilotkit/TrainingCopilotShell.jsx
scp root@192.168.1.249:/opt/apps/SET/SET-frontend/src/components/copilotkit/copilotkit.css SET-frontend/src/components/copilotkit/copilotkit.css
scp root@192.168.1.249:/opt/apps/SET/SET-frontend/src/components/copilotkit/__tests__/TrainingCopilotProvider.test.jsx SET-frontend/src/components/copilotkit/__tests__/TrainingCopilotProvider.test.jsx

git diff --check
cd SET-frontend
pnpm install --frozen-lockfile
pnpm exec vitest run src/components/copilotkit/__tests__/TrainingCopilotProvider.test.jsx
pnpm build
cd ..
git add SET-frontend/src/components/copilotkit/TrainingCopilotShell.jsx \
  SET-frontend/src/components/copilotkit/copilotkit.css \
  SET-frontend/src/components/copilotkit/__tests__/TrainingCopilotProvider.test.jsx
git commit -m "fix: lift mobile copilot launcher above nav"
git push origin main
git ls-remote --heads https://github.com/GucciGross/SET.git main
```

Notes:

- Do not treat `/opt/apps/SET` git failures as blockers; it is expected to be archive-style/no-git.
- If a focused `pnpm test -- path --run` unexpectedly fans out to many tests or fails from missing deps, use `pnpm install --frozen-lockfile` and then `pnpm exec vitest run <path>` for the targeted proof.
- Public readback should prove both CSS and JS: the CSS has the mobile `5rem + safe-area` offset, and the JS no longer contains the `bottom-5` launcher class.

Example readback checks:

```text
PUBLIC_CSS_RULE /assets/index-*.css status 200 mobileBottom True rightSafe True
PUBLIC_JS_RULE /assets/index-*.js status 200 noBottom5 True
PUBLIC_READBACK_OK True
API_HEALTH=healthy
```

When using shell readback commands, avoid piping untrusted `curl` output directly into an interpreter. Fetch with Python `urllib` or save the response before parsing.