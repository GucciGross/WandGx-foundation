# Install DexCLI

Linux and macOS private-beta users can install DexCLI with one command:

```bash
curl -fsSL https://raw.githubusercontent.com/GucciGross/WandGx-foundation/main/install/dex.sh | sh
```

Then open a new terminal and run:

```bash
dex
```

The public bootstrap prompts for GitHub sign-in when the private beta has not
already been authorized. It fetches the reviewed full installer from
`GucciGross/DexCLI`, installs DexCLI into an isolated user tool environment, and
returns control to the user. Bare `dex` performs first-run model, CrewAI team,
daemon, and Mission Cockpit setup.

Current beta authentication options:

```bash
gh auth login
```

or:

```bash
export GH_TOKEN=YOUR_GITHUB_TOKEN
```

Once public DexCLI release assets are published, the same bootstrap URL will no
longer require private-repository authentication.

Installer options are forwarded to the reviewed DexCLI installer:

```bash
curl -fsSL https://raw.githubusercontent.com/GucciGross/WandGx-foundation/main/install/dex.sh \
  | sh -s -- --help
```
