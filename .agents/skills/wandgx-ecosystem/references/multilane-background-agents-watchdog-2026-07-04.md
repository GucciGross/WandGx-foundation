# Multi-lane background agents + watchdog pattern — 2026-07-04

Use when the user asks Hermes to kick off several WandGx ecosystem workstreams in background and keep showing progress.

## Durable pattern

1. Create a durable run folder, e.g.:

```text
~/.hermes/project-runs/<date>-wandgx-multilane/
├── CONTINUATION.md
├── prompts/
├── logs/
├── reports/
├── handoffs/
└── watchdog-state.json
```

2. Write one prompt file per lane and launch explicit background Hermes CLI workers with `notify_on_complete=true`, not native `delegate_task`, when:
   - the lane may run longer than the child timeout,
   - each lane needs a different model/provider,
   - the work needs full tools/browser/terminal access,
   - or the user wants durable progress across context compression.

3. Keep `CONTINUATION.md` self-contained:
   - user instruction and current scope,
   - lane status,
   - process/session IDs if known,
   - report paths,
   - resume instructions after compression.

4. Each lane writes a final report under `reports/`. Parent/controller must verify reports and artifacts before claiming completion; do not trust a worker self-report alone.

5. Add a script-only cron watchdog for compact progress ticks when the user asks to see ongoing status:
   - create a script in `~/.hermes/scripts/`, not inline shell in the cron `script` field;
   - cron `script` must be just the filename, e.g. `wandgx_multilane_watchdog.py`;
   - use `no_agent=true` so it reads logs/reports and prints a fixed status block without LLM tokens;
   - use `schedule="every 10m"`, not bare `10m`, for recurring updates;
   - set `attach_to_session=true` / deliver to origin when the user wants updates in the same chat.

## Watchdog behavior

The script should:

- read the durable run folder;
- mark lanes as `DONE` when report exists, `RUN` when matching background process exists, `CHECK` when log exists but no report/process, `WAIT` when no log/report;
- show compact status and a few sanitized log-tail lines;
- redact secrets from log snippets;
- go quiet after all final reports exist by writing a sentinel file.

## Pitfalls

- Background Hermes sessions can hit their own context windows. When that happens, use log/report inspection to salvage partial work and launch a smaller follow-up lane instead of resuming the giant session.
- If a worker modified/deployed something but failed before writing the report, create a parent-authored partial report from logs and live verification, then launch a narrow closeout worker.
- Do not let the watchdog recursively create cron jobs.
- Do not paste raw logs into Telegram; summarize status and tails compactly.
