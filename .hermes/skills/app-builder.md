# Skill: WandGx app builder

Use this skill when Hermes is asked to build a new app on top of WandGx Foundation.

## Output order

Do not start by generating random code. Produce artifacts in this order:

```txt
1. APP_SPEC.md
2. app.manifest.json
3. entity/schema plan
4. crew manifest plan
5. route/page plan
6. tests/evals plan
7. implementation patch
```

## App manifest shape

```json
{
  "app_name": "Example App",
  "slug": "example_app",
  "description": "What the app does",
  "users": ["admin", "operator", "customer"],
  "entities": [],
  "crews": [],
  "interfaces": ["web_dashboard", "admin_hermes", "product_copilot", "api"],
  "human_approval": {
    "default": "approval_required",
    "required_for": ["send_email", "charge_customer"]
  }
}
```

## Generated app modules

Prefer this structure:

```txt
apps/web/app/(dashboard)/<module>/page.tsx
apps/api/routes/<module>.py
packages/contracts/<module>.schema.json
packages/db/migrations/<timestamp>_<module>.sql
crews/generated/<module>_crew/
tests/test_<module>.py
```

## Human-in-the-loop default

For new apps, default risky workflows to approval-required. Examples:

- sending customer communications
- submitting quotes
- charging cards
- deleting records
- exporting customer data
- modifying integrations

## Definition of done

An app scaffold is not done until it has:

- readable pages
- API routes
- DB schema or migration plan
- at least one runtime crew
- feedback capture
- tests/evals
- clear docs on how to run it
