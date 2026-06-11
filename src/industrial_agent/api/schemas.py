from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from industrial_agent.domain.models import Role


class RunRequest(BaseModel):
    query: str = Field(min_length=1)
    user_id: str = "anonymous"
    role: Role = Role.OPERATOR
    context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RunResponse(BaseModel):
    run_id: str
    status: str
    answer: str | None
    policy_decisions: list[str]
    steps: list[dict[str, Any]]
