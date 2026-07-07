# WandGx vNext competitor-gap audit + low-risk feature pattern (2026-07-04)

Use when asked to audit WandGx vNext against AI app-builder competitors (Lovable, Bolt, v0, Replit, etc.) and ship one small competitiveness improvement.

## Durable workflow

1. Ground the competitor matrix with current public/docs evidence, not memory.
   - Lovable publish docs: live URLs, website access control, custom domains, metadata/OG image, security scans, publish/update/unpublish, GitHub sync/export.
   - Bolt project docs: project list, created/starred/recent/shared views, rename/duplicate/download/export/open in StackBlitz, transfer/share permissions, custom-domain transfer caveats.
   - v0 homepage/docs: templates, prompt chips, publish live websites, GitHub repo sync, deploy to Vercel, design mode.
   - Replit docs: publishing/custom domains, free subdomain, custom domain DNS/verification, TLS, app monitoring/checkpoints/file history/tasks.
2. Compare against the actual vNext source surface before choosing a feature.
   - In the current Vite React workspace, relevant files were `apps/web/src/react/shell/HomeView.tsx`, `BuildView.tsx`, `ProjectView.tsx`, `App.tsx`, `api/client.ts`, and `styles.css`.
   - Existing partial strengths: hosted app link, iframe preview, source download, project list, build history.
   - Common visible gaps: starter templates/examples, custom domain UI, publish/share/access controls, GitHub sync affordance, billing/top-up UI, richer project organization.
3. Prefer the smallest user-visible feature that does not require new backend/storage/auth surfaces.
   - Starter templates / prompt examples are a good first move: high competitor parity with v0/Lovable/Replit onboarding, low risk, no backend migration, no auth weakening.
   - Avoid claiming custom domains, GitHub sync, billing, or publishing controls are done unless the backend path and live proof exist.
4. Implement shared data + UI reuse.
   - Add a small shared catalog such as `apps/web/src/react/shell/starterTemplates.ts`.
   - Render it in both the dashboard composer and build composer so users see it before and during intent editing.
   - Keep copy product-safe: no internal agent/provider/tool names.
5. Preserve design and architecture constraints.
   - Flat cards only; no gradients, no purple/indigo primary, no chat bubbles, no flashing, no shadcn/card-stack feel.
   - Do not add raw internal workflow names to public UI.
   - Do not modify unrelated auth guards or central identity flows.
6. Verify locally with focused package gates.
   - For the Vite web workspace, run `pnpm --filter @wandgx/web typecheck` and `pnpm --filter @wandgx/web build` after dependencies are installed.
   - If `node_modules` is missing, `pnpm install --frozen-lockfile` is a setup step, not a product finding.
7. Report source boundaries honestly.
   - If the worktree already contains unrelated user/agent edits, explicitly say which files you changed and which unrelated files were left untouched.
   - Do not summarize unrelated diffs as your implementation.

## Example low-risk implementation shape

- `starterTemplates.ts`: exported array of title/category/description/intent.
- `HomeView.tsx`: “Start faster from an example” section; clicking a card calls `onBuild({ title, intent })`.
- `BuildView.tsx`: “Starter examples” section under the intent textarea; clicking a card fills title + intent and leaves the prompt editable.
- `styles.css`: responsive flat template card grid using existing tokens.

## Verification evidence from this session

- `pnpm --filter @wandgx/web typecheck` passed.
- `pnpm --filter @wandgx/web build` passed; Vite produced `dist/workspace-shell.html`, CSS, and JS bundle.
