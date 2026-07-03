# Crew generation

Crew generation is manifest-first:

```txt
prompt → CrewManifest → schemas/tools/evals/tests → human approval → registry → runtime
```

A generated crew is not registered for production until it has:

- `manifest.json`
- `crew.py`
- `agents.yaml`
- `tasks.yaml`
- input/output schemas
- at least one smoke eval
- permissions reviewed

Create one locally:

```bash
hermes crew create "Lead intake crew for painting quote requests" --write
```
