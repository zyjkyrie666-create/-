from __future__ import annotations

from dataclasses import dataclass

from industrial_agent.domain.models import RiskLevel, Role, TaskRequest, ToolPlan
from industrial_agent.domain.tools import ToolRegistry


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEngine:
    """Small but explicit policy layer for Agent governance."""

    dangerous_terms = (
        "delete database",
        "drop table",
        "删除数据",
        "清空数据库",
        "绕过审核",
        "强制跳过",
    )

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def validate_request(self, request: TaskRequest) -> PolicyDecision:
        normalized = request.query.lower()
        if any(term.lower() in normalized for term in self.dangerous_terms):
            return PolicyDecision(False, "blocked dangerous instruction")
        if not request.query.strip():
            return PolicyDecision(False, "query must not be empty")
        return PolicyDecision(True, "request accepted")

    def validate_tool_plan(self, request: TaskRequest, plan: ToolPlan) -> PolicyDecision:
        tool = self.registry.get(plan.tool_name)
        if tool is None:
            return PolicyDecision(False, f"unknown tool: {plan.tool_name}")
        if request.role not in tool.allowed_roles:
            return PolicyDecision(False, f"role {request.role.value} cannot use {tool.name}")
        if tool.risk_level is RiskLevel.HIGH and request.role is not Role.ADMIN:
            return PolicyDecision(False, f"high-risk tool {tool.name} requires admin")
        return PolicyDecision(True, f"tool {tool.name} allowed")
