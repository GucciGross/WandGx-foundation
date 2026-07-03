# Publishing to GitHub

Do not paste a long-lived PAT into chat. Use the GitHub CLI locally or a short-lived fine-grained token.

```bash
git init
git add -A
git commit -m "Initial Hermes agent starter"
gh auth login
gh repo create hermes-agent-starter --public --source=. --remote=origin --push
```

For a one-shot token flow, create a fine-grained PAT scoped only to the target repository, then revoke it after the push.
