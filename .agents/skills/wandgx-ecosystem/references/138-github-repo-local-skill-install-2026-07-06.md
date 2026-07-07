# 138 GitHub repo-local WandGx ecosystem skill install

Use this when the user asks to prepare 138 for Codex/Droid/Hermes handoffs across WandGx ecosystem repos.

## Durable pattern

- Host: `gucci@192.168.1.138`.
- Current source workspace on 138: `/home/gucci/Documents/GitHub`.
- Scope discipline: if the user says **138**, work on 138 only. Do not probe or modify nearby hosts such as 137 just because credentials or IPs were mentioned in the same exchange unless the user explicitly asks for that host too.
- Do not assume old Windows paths. Verify `$HOME`, hostname, and the GitHub directory first.
- Put the skill inside each repo, not only in global Hermes/ZCode locations, so external agents launched from the repo can discover it.
- If SSH reports a host-key/fingerprint mismatch for `192.168.1.138`, fix the fingerprint first and distinguish it from auth failure. Refresh known_hosts with `ssh-keygen -R 192.168.1.138`, rescan with `ssh-keyscan -T 8 -t ed25519,rsa 192.168.1.138`, inspect fingerprints, append the fresh keys to the relevant caller's `known_hosts`, then retry with `StrictHostKeyChecking=yes`. Current observed fingerprints after the 2026-07-06 refresh were RSA `SHA256:102iFAem4hzsq0TfS/iUVUz4w71kBrzqc01AyOyt7Uw` and ED25519 `SHA256:WhHnkke7B2qQ6XWCE+87EieNg3XWyA81VdJiRtPThig`. If the handshake then reaches `Permission denied (publickey,password)`, the fingerprint problem is solved and the remaining blocker is SSH auth/key access, not host identity.

## Repo set used for ecosystem handoffs

Install/update these under `/home/gucci/Documents/GitHub` unless the user names a different subset:

- `GucciGross/WandGx`
- `GucciGross/WandGx-vNext`
- `GucciGross/WandGx-chat`
- `GucciGross/SET`
- `GucciGross/SET-backend`
- `GucciGross/SET-frontend`
- `GucciGross/WandGx-Enterprise`
- `GucciGross/llm`
- `GucciGross/paint-quote`
- `sourcebot-dev/sourcebot`

## Install shape per repo

For each repo:

- Full skill directory: `.agents/skills/wandgx-ecosystem/`
- Main file: `.agents/skills/wandgx-ecosystem/SKILL.md`
- Keep all `references/` files with the skill.
- Add or patch `AGENTS.md` with a short marked section telling Codex/Droid/Hermes to load `.agents/skills/wandgx-ecosystem/SKILL.md` before WandGx/SET/Oracle/LLM/Paint Quote ecosystem work.
- Add `.agents/README.md` pointing to `skills/wandgx-ecosystem/SKILL.md`.

Suggested `AGENTS.md` section marker:

```md
<!-- WANDGX-ECOSYSTEM-SKILL:START -->

## WandGx ecosystem handoff context

Before changing this repository for WandGx, SET, Oracle/WandGx Chat, LLM proxy, central identity/Appwrite/ops, Paint Quote, Sourcebot, or shared ecosystem infrastructure, read the repo-local skill:

- `.agents/skills/wandgx-ecosystem/SKILL.md`

Treat that skill as required context for Codex, Droid, Hermes, and any other coding-agent handoff. It contains the current VM topology, product ownership boundaries, auth rules, model/Oracle rules, deployment targets, and verification gates. Do not expose internal provider/model/tool names in customer UI, do not weaken auth guards, and do not claim completion without scoped runtime proof.

<!-- WANDGX-ECOSYSTEM-SKILL:END -->
```

## Verification

For each repo, verify:

```text
repo_ok
skill_ok
agents_pointer_ok
skill_files=<nonzero count, expected around 49 as of 2026-07-06>
origin_clean=https://github.com/...
```

Also inspect `git status --short`. It is expected that this handoff install creates local uncommitted additions/modifications (`AGENTS.md`, `.agents/README.md`, `.agents/skills/wandgx-ecosystem/`) unless the user asks to commit/push them.

## Pitfalls

- Do not leave GitHub tokens embedded in remote origins. Remotes should be clean `https://github.com/org/repo.git` URLs after clone/update.
- If GitHub requires auth, use a temporary askpass/token flow and unset it afterward; never write the token into repo config or `AGENTS.md`.
- If SSH public-key auth fails but password auth is available, `sshpass -e` can be used when `SSHPASS` is already configured in the current environment. Do not print the password.
- Source/deploy archive directories under `/opt/apps` are not the long-term source of truth; this workflow is specifically for repo-local handoff context under `Documents/GitHub` on 138.
