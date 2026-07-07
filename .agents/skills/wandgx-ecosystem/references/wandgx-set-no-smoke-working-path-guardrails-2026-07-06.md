# WandGx / SET no-smoke working-path guardrails — 2026-07-06

## Trigger

Use this when the user says WandGx or SET is "smoke and mirrors", asks to make product claims actually work, or wants features added without breaking existing flows.

## User correction captured

- Do not frame this work as timelines, phases, or slices.
- Run non-trivial work in background agents/tracked jobs where possible so the user can keep talking.
- Public product copy must only claim capabilities backed by live working flows.
- If a feature cannot be made real yet, hide it or label it honestly as demo/beta; never fake success.
- Parent agent must verify subagent claims with live browser/API proof before saying done.

## Working paths to preserve

### WandGx

Core path:

```text
user describes app
-> account/session exists
-> project/build request is persisted
-> status/proof events are stored
-> dashboard reload shows the record
-> next action is clear
```

Supported public claims must map to this path. If preview/deploy/codegen is not proven, public copy should say build request/build plan/proof, not autonomous shipped app.

### SET

Core path:

```text
user opens/adds source material
-> training object exists
-> practice/tutor/readiness object exists
-> state persists across reload
-> next action is clear
```

Supported public claims must map to real source/training/practice/readiness data. Demo data must be clearly marked demo/sample and never presented as customer proof.

## Safe feature pattern

Before adding a feature, classify it:

- Safe: extends existing objects/events without altering required fields.
- Risky: touches auth, routing, persistence, core object shape, or shell navigation.
- Fake-risk: looks impressive but has no backend proof; block, hide, or label as demo.

Every feature should have:

```text
feature flag / kill switch
stable API contract
loading/error/empty UI states
auth guard proof if protected
persistence-after-reload proof
live browser/API smoke
public-copy capability gate
```

If the feature fails, the user must still be able to complete the core working path.

## Implementation guardrails

- Prefer append-only event streams for proof/readiness over overwriting a fragile status blob.
- Add capability registry or equivalent so public copy and route exposure can be tied to verified capabilities.
- Keep demo-vs-real markers in data shapes, e.g. `mode: demo|real` and `source: sample|user|system`.
- Do not weaken central auth guards to make a demo pass.
- Do not expose internal agent/tool/model/workflow names.
- Deploy only after focused tests/builds pass, then verify live public URLs and relevant API state.

## Verification report shape

Report concise proof, not plans:

```text
changed files
commands run
deployed services restarted
live URLs checked
created object IDs or persisted rows
reload/persistence proof
console/API errors
remaining blockers
```

Avoid roadmap words such as phase, slice, timeline, later, or next quarter unless the user explicitly asks for planning language.
