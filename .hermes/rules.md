# WandGx Foundation Rules

These are the local rules for Hermes, Codex, and any repo-aware agent.

## Identity

You are working inside WandGx Foundation. The goal is to provide a reusable base for agent-first applications. Hermes is the control plane, not the product itself.

## Build philosophy

- Build contracts before implementation.
- Prefer manifests, schemas, tests, and evals over ad-hoc prompts.
- Make every generated module reviewable.
- Keep humans in the loop for risky operations.
- Keep the local developer experience simple: clone, copy env, Docker Compose up.

## Allowed write zones

Agents may write inside these paths unless a task says otherwise:

```txt
apps/
packages/
crews/generated/
crews/templates/
docs/
examples/
infra/
tests/
.hermes/
```

## Approval-gated operations

Always require explicit human approval before implementing or executing:

```txt
send_email
send_sms
charge_customer
delete_data
export_customer_data
run_shell_command
deploy_production
modify_auth
modify_billing
```

## Research rules

- Use SearXNG as the default local web search provider.
- Use Firecrawl for richer scrape/search/crawl only when enabled.
- Cite sources in generated research summaries.
- Store retrieved content as artifacts or references, not hidden prompt-only context.
- Do not scrape private, authenticated, or paywalled content unless the user owns the data and grants permission.

## Crew generation rules

Generated crews must include:

```txt
manifest.json
crew.py
agents.yaml
tasks.yaml
tools.py
schemas/input.schema.json
schemas/output.schema.json
evals/basic.yaml
tests/test_contract.py
```

Do not register a generated crew until its manifest and permissions have been reviewed.
