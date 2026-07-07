# ZCode Mac mini operational setup

Use this reference when the user asks to install or refresh WandGx ecosystem context in ZCode, keep the ZCode Mac mini awake, or verify the ZCode host is ready for long-running agent work.

## ZCode host

- Host: `gucci@192.168.1.241`
- Observed hostname: `zs-Mac-mini.local`
- ZCode app: `/Applications/ZCode.app`
- ZCode project: `/Users/gucci/ZCodeProject`
- ZCode config roots:
  - `/Users/gucci/.zcode`
  - `/Users/gucci/Library/Application Support/ZCode`

## Skill install locations

ZCode discovers skills in these paths, highest priority first:

1. `<project>/.zcode/skills/<name>/SKILL.md`
2. `<project>/.agents/skills/<name>/SKILL.md`
3. `~/.zcode/skills/<name>/SKILL.md`
4. `~/.agents/skills/<name>/SKILL.md`

For WandGx ecosystem context, install to both the user-global and ZCode project path:

- `/Users/gucci/.zcode/skills/wandgx-ecosystem/SKILL.md`
- `/Users/gucci/ZCodeProject/.agents/skills/wandgx-ecosystem/SKILL.md`

Verify by checking that both files exist, have the same byte count, and include `name: wandgx-ecosystem`, `VM300`, `https://wandgx.com/app`, and `192.168.1.248`.

## Keep the Mac awake

Prefer the built-in macOS `caffeinate` tool instead of installing a third-party app. Install a LaunchAgent so it survives logouts/restarts:

- LaunchAgent: `/Users/gucci/Library/LaunchAgents/com.wandgx.caffeinate.plist`
- Program: `/usr/bin/caffeinate -d -i -m -s`
- Helper: `/Users/gucci/bin/caffeine`

The helper should support:

```bash
caffeine status
caffeine start
caffeine stop
caffeine restart
```

Verification commands:

```bash
launchctl print gui/$(id -u)/com.wandgx.caffeinate
pgrep -fl 'caffeinate.*-d.*-i.*-m.*-s'
defaults -currentHost read com.apple.screensaver idleTime
pmset -g assertions | egrep 'pid .*caffeinate|PreventUserIdleDisplaySleep|PreventSystemSleep|PreventUserIdleSystemSleep'
pmset -g custom | egrep ' sleep|displaysleep|disksleep|disablesleep'
```

Expected healthy state:

- LaunchAgent state is `running`.
- `pgrep` shows `/usr/bin/caffeinate -d -i -m -s`.
- `defaults -currentHost read com.apple.screensaver idleTime` returns `0`.
- `pmset -g assertions` shows caffeinate assertions for display/system/user-idle sleep.
- `pmset -g custom` shows sleep/display/disk sleep disabled or equivalent no-sleep policy.

## Pitfalls

- Do not assume Homebrew is installed or required. The built-in `caffeinate` binary is enough.
- Do not only run `caffeinate` in an SSH shell; that dies with the shell. Use a LaunchAgent.
- Do not treat a running ZCode process as proof the Mac will stay awake. Verify power assertions.
- Do not store API keys or ZCode credentials in the skill. ZCode config files may contain secrets; inspect carefully and redact if reporting.
