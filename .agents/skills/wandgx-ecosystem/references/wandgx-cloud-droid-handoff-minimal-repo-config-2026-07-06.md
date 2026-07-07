# WandGx-Cloud Droid handoff: minimal repo-local config

Use this when preparing the clean `WandGx-Cloud` repo on 138 for Droid/Codex/Hermes work.

## Trigger

The user wants a new WandGx iteration (`WandGx-cloud`) and asks to update Droid config with skills, MCP, and `AGENTS.md` using skills.sh / agent skills discovery. They explicitly do **not** want rule-file clutter.

## Repo and host

- Host: `gucci@192.168.1.138`
- Repo: `/home/gucci/Documents/GitHub/WandGx-Cloud`
- Remote: `GucciGross/WandGx-Cloud`
- 138 may not have working GitHub credentials; if push/fetch fails from 138, use an authenticated local/Hermes clone plus `git format-patch` or `git bundle`, then realign 138 with the pushed head.

## Minimal files to add

Keep the repo focused. Do not copy every legacy WandGx factory file. Add only:

```text
AGENTS.md
.factory/settings.json
.factory/mcp.json
.factory/droids/wandgx-cloud-architect.md
.factory/droids/wandgx-cloud-builder.md
.factory/droids/wandgx-cloud-validator.md
.agents/skills/<selected skills>/...
```

Do **not** add:

```text
*.rules
.cursorrules
.codex/rules/*
large legacy .factory hooks/state/history
personal credentials
provider API keys
generated caches/logs
```

## Skills to seed

Use class-level, repo-local skills. Good default set for WandGx-Cloud:

- `wandgx-ecosystem`
- `wandgx-software-factory`
- `wandgx-adaptive-business-os`
- `better-auth-platform-identity`
- `copilotkit-agui`
- `ai-coding-agents`
- `droid`
- `find-skills`
- `frontend-design`
- `react-best-practices`
- `systematic-debugging`
- `verification-before-completion`
- `webapp-testing`

Use `skills.sh` / `npx skills find` as the discovery source when available, but do not block if 138 lacks Node/npm. Existing repo-local skill directories can be copied from trusted local checkouts, and the handoff should mention `find-skills` for later discovery.

## Droid MCP

Droid CLI location observed on 138:

```bash
/home/gucci/.local/bin/droid
```

Useful commands:

```bash
/home/gucci/.local/bin/droid mcp list
/home/gucci/.local/bin/droid mcp add copilotkit https://mcp.copilotkit.ai/sse --type sse
```

Repo-local `.factory/mcp.json` can include CopilotKit MCP with no secrets:

```json
{
  "mcpServers": {
    "copilotkit": {
      "url": "https://mcp.copilotkit.ai/sse",
      "type": "sse",
      "disabled": false,
      "description": "CopilotKit and AG-UI protocol docs/examples for agent UI work. No secrets required."
    }
  }
}
```

Avoid committing MCP configs that contain tokens or personal credentials. If adding GitHub/Firecrawl/etc. later, use environment variables and keep secrets out of the repo.

## AGENTS.md content requirements

The repo `AGENTS.md` should be product-directional, not a pile of rules. Include:

- Load order for repo-local skills.
- WandGx-Cloud product intent: cloud app-building/coding workspace, polished and proof-driven.
- Public UI must hide internal labels: Droid, Codex, MCP, skills, provider names, hidden model/tool names.
- 138/source vs VM300/production boundary.
- Droid launch command:

```bash
droid --cwd /home/gucci/Documents/GitHub/WandGx-Cloud --settings .factory/settings.json --auto high
```

- Completion standard: inspect, patch, test/build/smoke, deploy if needed, live-verify, state proof and unproven assumptions.

## Verification before claiming done

Run these checks:

```bash
cd /home/gucci/Documents/GitHub/WandGx-Cloud
git status --short
find .agents/skills -maxdepth 2 -name SKILL.md | sort
python3 -m json.tool .factory/mcp.json >/dev/null
python3 -m json.tool .factory/settings.json >/dev/null
find . -path './.git' -prune -o \( -iname '*.rules' -o -name '.cursorrules' -o -path '*/rules/*' -o -path '*/.codex/*' \) -print
/home/gucci/.local/bin/droid mcp list
```

Also run a targeted secret-like scan for actual key/token formats, but do not treat redacted placeholders or documentation examples as secrets.

## Push workaround

If 138 push fails with unauthenticated HTTPS, do not stop at a local commit. Use:

1. `git format-patch -1 --stdout <commit>` from 138.
2. Apply patch in a local authenticated clone.
3. Push with local `gh`/Git credentials.
4. Create a `git bundle` from the pushed clone and fetch/reset 138 to that head.
5. Verify 138 `git log -1` matches GitHub main.
