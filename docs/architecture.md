# Architecture

Hermes Agent Starter splits the system into four planes.

## 1. Control plane

Hermes is the builder and supervisor. It creates manifests, proposes code, generates crews, observes logs, and turns repeated feedback into evals and patch proposals.

## 2. Runtime plane

CrewAI crews do product work: support, intake, quoting, follow-up, research, onboarding, billing, and any domain-specific workflows.

## 3. Interaction plane

AG-UI streams connect backend agent events to user-facing applications. CopilotKit can replace or extend the starter UI when you want prebuilt chat, generative UI, shared state, and HITL components.

## 4. Interop plane

A2A publishes agent cards and allows Hermes or generated app agents to collaborate with other agent services without exposing internal code or tools.

```txt
Web UI / CopilotKit
  ↓ AG-UI stream
FastAPI agent gateway
  ↓
CrewAI runtime crews  ←→  Hermes control plane
  ↓                         ↓
Postgres / Redis / logs      Manifests / evals / patch proposals
  ↓
A2A card for external discovery
```
