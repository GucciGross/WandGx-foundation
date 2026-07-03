from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class HermesMode(str, Enum):
    dormant = "dormant"
    observe = "observe"
    guardian = "guardian"


class HumanApprovalPolicy(BaseModel):
    required_for: list[str] = Field(default_factory=lambda: [
        "send_email",
        "send_sms",
        "charge_customer",
        "delete_data",
        "export_customer_data",
        "deploy_production",
    ])
    default: Literal["allow", "approval_required", "deny"] = "approval_required"


class EntityManifest(BaseModel):
    name: str
    description: str = ""
    fields: dict[str, str] = Field(default_factory=dict)


class CrewManifest(BaseModel):
    id: str
    name: str
    runtime: Literal["crewai"] = "crewai"
    purpose: str
    inputs_schema: str
    outputs_schema: str
    tools: list[str] = Field(default_factory=list)
    permissions: dict[str, Any] = Field(default_factory=dict)
    requires_human_approval: bool = True
    entrypoint: str = ""
    evals: list[str] = Field(default_factory=list)


class AppManifest(BaseModel):
    app_name: str
    slug: str
    description: str
    users: list[str] = Field(default_factory=list)
    entities: list[EntityManifest] = Field(default_factory=list)
    crews: list[CrewManifest] = Field(default_factory=list)
    interfaces: list[str] = Field(default_factory=lambda: ["web", "admin", "api"])
    human_approval: HumanApprovalPolicy = Field(default_factory=HumanApprovalPolicy)
    created_by: str = "hermes"
    version: str = "0.1.0"


class HermesAction(BaseModel):
    type: str
    title: str
    description: str
    payload: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False


class HermesResponse(BaseModel):
    message: str
    mode: HermesMode = HermesMode.dormant
    actions: list[HermesAction] = Field(default_factory=list)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class FeedbackRecord(BaseModel):
    run_id: str | None = None
    agent_id: str = "product_copilot"
    rating: Literal["good", "bad", "neutral"] = "neutral"
    comment: str = ""
    snapshot: dict[str, Any] = Field(default_factory=dict)


class MaintenanceFinding(BaseModel):
    severity: Literal["info", "warning", "critical"] = "info"
    category: str
    summary: str
    suggested_fix: str
    eval_candidate: dict[str, Any] = Field(default_factory=dict)
