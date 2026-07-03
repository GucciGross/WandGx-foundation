# Skill: Security and approval model

Use this skill before adding tools, background jobs, integrations, auth, billing, or production deployment behavior.

## Secret handling

Never commit real secrets. Do not write real credentials into examples, manifests, docs, generated crews, tests, or logs.

Acceptable locations for real secrets:

- local `.env`
- deployment secret manager
- CI/CD secret store

## Dangerous actions

The following require human approval by default:

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

## Self-healing rule

Hermes may observe, diagnose, create evals, and propose patches. In production, Hermes must not silently mutate live code or data.

Safe loop:

```txt
observe issue → create failing eval → propose patch → run tests → human approval → merge/deploy
```

## Tool permission rule

Tools must be listed in the crew manifest before a crew can use them. Runtime code should reject tool calls that are not manifest-approved.
