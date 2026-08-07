from __future__ import annotations

import os
from typing import Any

CREW_ID = "support_crew"


def deterministic_support(payload: dict[str, Any]) -> dict[str, Any]:
    message = payload.get("message", "")
    return {
        "crew_id": CREW_ID,
        "status": "completed",
        "answer": (
            "This is the local deterministic Support Crew. "
            "Connect OPENAI_API_KEY and customize agents.yaml/tasks.yaml to run CrewAI with a model. "
            f"I received: {message}"
        ),
        "confidence": 0.72,
        "needs_human": False,
        "next_actions": ["Collect feedback", "Add domain knowledge", "Promote repeated fixes into evals"],
    }


def kickoff(payload: dict[str, Any]) -> dict[str, Any]:
    if not os.getenv("OPENAI_API_KEY"):
        return deterministic_support(payload)

    try:
        from crewai import Agent, Crew, Process, Task
    except ImportError:
        return deterministic_support(payload)

    support_agent = Agent(
        role="Product Support Agent",
        goal="Help the user succeed while escalating anything risky or uncertain.",
        backstory="You are the default user-facing support crew in a Hermes app.",
        verbose=True,
    )
    task = Task(
        description="Answer the user's support request: {message}",
        expected_output="A helpful answer, a confidence score, and whether a human is needed.",
        agent=support_agent,
    )
    crew = Crew(agents=[support_agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff(inputs={"message": payload.get("message", "")})
    return {
        "crew_id": CREW_ID,
        "status": "completed",
        "answer": str(result),
        "confidence": 0.8,
        "needs_human": False,
    }


if __name__ == "__main__":
    print(kickoff({"message": "How do I use this starter?"}))
