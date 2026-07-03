from __future__ import annotations

from .schemas import FeedbackRecord, MaintenanceFinding


class FeedbackTriage:
    def summarize(self, records: list[FeedbackRecord]) -> list[MaintenanceFinding]:
        if not records:
            return [
                MaintenanceFinding(
                    severity="info",
                    category="no_feedback_yet",
                    summary="No feedback records were provided.",
                    suggested_fix="Ship the feedback widget and collect run snapshots before changing prompts or code.",
                    eval_candidate={"name": "feedback_collection_smoke", "expected": "feedback table receives records"},
                )
            ]

        bad = [record for record in records if record.rating == "bad"]
        findings: list[MaintenanceFinding] = []
        if bad:
            findings.append(
                MaintenanceFinding(
                    severity="warning",
                    category="negative_feedback",
                    summary=f"{len(bad)} negative feedback records need review.",
                    suggested_fix="Cluster comments, create eval cases for repeated failures, then patch prompts/tools.",
                    eval_candidate={
                        "name": "negative_feedback_regression",
                        "examples": [record.comment for record in bad[:5]],
                    },
                )
            )
        return findings
