from __future__ import annotations

import json
import os
import time
from pathlib import Path

from hermes_agent.runtime import run_python_crew

QUEUE = "hermes:jobs"


def main() -> None:
    print("Hermes worker started. Waiting for jobs on", QUEUE, flush=True)
    try:
        import redis
    except Exception:
        print("redis package unavailable; worker entering heartbeat-only mode.", flush=True)
        while True:
            time.sleep(30)

    client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
    while True:
        _, raw = client.brpop(QUEUE)
        job = json.loads(raw)
        entrypoint = Path(job.get("entrypoint", "crews/templates/support_crew/crew.py"))
        payload = job.get("payload", {})
        try:
            result = run_python_crew(entrypoint, payload)
            client.lpush(f"{QUEUE}:results", json.dumps({"status": "completed", "result": result}))
        except Exception as exc:  # noqa: BLE001
            client.lpush(f"{QUEUE}:results", json.dumps({"status": "failed", "error": str(exc)}))


if __name__ == "__main__":
    main()
