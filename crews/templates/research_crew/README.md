# Research Crew

Default WandGx research crew template.

Use this when an app needs current, source-aware research. The template uses local SearXNG through `packages/web_research` and can be extended with Firecrawl for richer page reads.

Required files for a generated production crew:

```txt
manifest.json
crew.py
agents.yaml
tasks.yaml
schemas/input.schema.json
schemas/output.schema.json
evals/basic.yaml
tests/test_contract.py
```
