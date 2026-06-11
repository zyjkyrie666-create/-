from __future__ import annotations

from typing import Protocol

from industrial_agent.domain.models import TaskRequest, ToolPlan
from industrial_agent.domain.tools import Tool


class Planner(Protocol):
    def plan(self, request: TaskRequest, tools: list[Tool]) -> list[ToolPlan]:
        ...

    def summarize(self, request: TaskRequest, tool_outputs: list[dict]) -> str:
        ...
