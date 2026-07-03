# Skill: Frontend surfaces

Use this skill when editing `apps/web`.

## Surfaces

WandGx Foundation has two frontend agent surfaces:

```txt
/admin/hermes   admin/developer control plane
/app/support    user-facing product copilot
```

## Rules

- Keep Hermes Admin separate from user-facing copilots.
- Do not expose dangerous tools directly to end users.
- Use approval cards for risky actions.
- Capture thumbs-up/thumbs-down feedback with run snapshots.
- Prefer reusable components under `apps/web/components/`.
- Keep the default UI dependency-resilient; CopilotKit examples can exist without forcing the whole app to depend on a configured cloud runtime.
