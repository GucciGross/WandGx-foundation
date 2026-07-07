# Oracle Diffusion Internal Tools + SET RAGFlow Direction (2026-07-06)

## When to use

Use this when wiring or debugging Oracle Diffusion, `llm.wandgx.com`, `chat.wandgx.com`, SET document intelligence, Google Drive/doc ingestion, or hidden web/search/memory/Council tools.

## Correct architecture

Oracle Diffusion is an orchestrator model served by vLLM. GLM-5.2 is **not** self-hosted in vLLM; it is called through the hosted Z.ai API by the server-side proxy.

Correct flow:

```text
user
  -> WandGx Chat / Oracle proxy
  -> Oracle Diffusion on vLLM
  -> proxy-managed internal tools when requested
       - council.ask(GLM-5.2 / other hosted models)
       - web.search(SearXNG)
       - web.read(Firecrawl)
       - memory.search / memory.write
       - rag.query(SET/RAGFlow knowledge)
  -> Oracle Diffusion final answer
  -> user
```

## Critical pitfall

Do **not** send CopilotKit/OpenAI `tools` schemas to the vLLM diffusion endpoint just because Oracle needs Council/web/RAG/memory.

- vLLM only validates tool schemas for the model it serves: Oracle Diffusion.
- GLM-5.2 is behind Z.ai and should be invoked by the proxy as an internal subcall.
- The proxy should parse a hidden internal tool protocol emitted by diffusion, execute the tool server-side, append the result into hidden context, and call diffusion again.

Only use vLLM-native tool calling if intentionally configuring the diffusion model itself with the required vLLM tool parser/template. Otherwise keep the diffusion request plain and do orchestration in the proxy.

## Product rule

Users should not have to enable or select these capabilities. Oracle should automatically decide when to search, read, remember, retrieve docs, or ask Council. Do not expose capability toggles, model selectors, provider labels, or internal tool names in customer UI.

## Internal tool loop contract

Suggested bounded loop:

1. Send user message and hidden system contract to diffusion.
2. If diffusion returns final text, stream it to the user.
3. If diffusion returns an internal tool call, validate the tool and arguments.
4. Execute the tool server-side.
5. Append the tool result to hidden context.
6. Call diffusion again.
7. Stop after a small maximum number of tool rounds and force a final answer or graceful failure.

Example hidden calls:

```json
{"tool":"council.ask","input":{"model":"glm-5.2","question":"..."}}
```

```json
{"tool":"web.research","input":{"query":"...","depth":"quick"}}
```

```json
{"tool":"rag.query","input":{"workspace":"set","query":"..."}}
```

## Infra defaults

- SearXNG: fast metasearch.
- Firecrawl: page scrape/crawl/extract.
- RAGFlow: document knowledge base engine for SET/Oracle document RAG.
- Mem0 or internal memory layer: long-term user/project memory.
- Z.ai GLM-5.2: primary hosted Council model.

## SET document intelligence direction

Current SET does **not** use RAGFlow. It has a homegrown document pipeline:

- `SET-backend/app/services/document_processor.py` extracts/chunks PDFs/DOCX/HTML/text.
- `SET-backend/app/tasks/document_processing.py` embeds chunks through `OllamaService.embed()` defaulting to `nomic-embed-text`.
- `SET-backend/database/003_document_tables.sql` defines `documents`, `document_chunks`, `pgvector`, and vector search SQL functions.
- `SET-backend/app/services/rag_service.py` retrieves chunks with vector search and keyword fallback.
- `SET-backend/app/api/routes/document_sources.py` handles Google Drive folder sources, but source-specific query currently ranks chunks by keyword counts and Google Drive source chunks may have `embedding: None`.

User preference: the user likes RAGFlow and wants it as the likely long-term document/RAG engine.

Target design:

```text
Google Drive / Upload / Local Connector
  -> SET source manager / tenant permissions
  -> RAGFlow dataset ingestion
  -> RAGFlow parsing, chunking, indexing, retrieval, citations
  -> SET training generator / tutor / quiz / SOP builder
  -> Oracle can query the same knowledge layer when needed
```

SET should still own tenants, permissions, training paths, approvals, learner UI, and source UX. RAGFlow should own heavy document parsing/chunking/indexing/retrieval/citations.

## Verification when implementing

- Prove the proxy does not leak internal tool names or model/provider names to the UI.
- Prove vLLM diffusion calls are not receiving OpenAI tool schemas unless deliberately configured.
- Prove Council subcalls hit hosted Z.ai GLM-5.2 through the proxy.
- Prove SearXNG and Firecrawl are reachable from the chat/LLM runtime container.
- For SET/RAGFlow integration, prove tenant-scoped ingestion and retrieval with citations, and preserve SET permission boundaries.
