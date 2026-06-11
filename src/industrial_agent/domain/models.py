from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class Role(str, Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RunStatus(str, Enum):
    CREATED = "created"
    BLOCKED = "blocked"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class TaskRequest:
    query: str
    user_id: str = "anonymous"
    role: Role = Role.OPERATOR
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ToolPlan:
    tool_name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


@dataclass
class AgentStep:
    name: str
    status: str
    input: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None


@dataclass
class AgentRun:
    request: TaskRequest
    id: str = field(default_factory=lambda: str(uuid4()))
    status: RunStatus = RunStatus.CREATED
    plan: list[ToolPlan] = field(default_factory=list)
    steps: list[AgentStep] = field(default_factory=list)
    answer: str | None = None
    policy_decisions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)
