# Research stack

WandGx Foundation keeps web research local-first.

## SearXNG

Config lives under `infra/searxng/`.

Run the example service:

```bash
cd infra/searxng
docker compose -f compose.example.yml up
```

Then open `http://localhost:8888`.

The settings enable JSON output so agents can use SearXNG as a search backend.

## Firecrawl

Firecrawl is the optional richer provider for page reading, crawling, and search with page content. Keep any provider configuration in local environment or deployment settings rather than committed source.

Recommended flow:

```txt
SearXNG search → choose URLs → Firecrawl page read when enabled → source-aware summary
```
