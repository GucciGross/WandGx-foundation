# Skill: Web research tools

Use this skill whenever an agent needs current information from the web.

## Providers

WandGx Foundation uses a two-layer research setup:

```txt
SearXNG   local, no-key metasearch, default provider
Firecrawl optional richer search/scrape/crawl provider
```

SearXNG should be available from Docker Compose at:

```txt
Host:   http://localhost:8888
Docker: http://searxng:8080
```

Firecrawl can be used through the hosted API or a self-hosted deployment. Keep it optional so the foundation remains cloneable without paid services.

## Research flow

```txt
query
  ↓
search with SearXNG
  ↓
select sources
  ↓
scrape with Firecrawl when enabled, otherwise fetch/summarize lightly
  ↓
return source-aware summary
```

## Safety rules

- Do not scrape authenticated/private pages unless the user owns the data and grants permission.
- Prefer official documentation for coding/framework questions.
- For recently changing facts, use web research rather than memory.
- Preserve source URLs in artifacts and summaries.
- Do not hide source content only in prompts.

## CrewAI usage

Use these tool names in manifests:

```txt
web.search
web.scrape
web.research
```

Crews that use these tools should include a source list in their output:

```json
{
  "summary": "...",
  "sources": [
    {"title": "...", "url": "...", "provider": "searxng"}
  ],
  "needs_human": false
}
```
