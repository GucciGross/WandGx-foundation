# Self-healing loop

Hermes should not silently edit production. The safe loop is:

```txt
observe issue
  ↓
classify issue
  ↓
create failing eval
  ↓
generate patch proposal
  ↓
run tests/evals
  ↓
human approval / PR
  ↓
merge and deploy
```

Recommended production settings:

```env
HERMES_MODE=guardian
HERMES_AUTOFIX=pr_only
REQUIRE_HUMAN_APPROVAL=true
```
