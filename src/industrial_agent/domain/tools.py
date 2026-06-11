from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from industrial_agent.domain.models import RiskLevel, Role


class ToolHandler(Protocol):
    def __call__(self, arguments: dict) -> dict:
        ...


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    risk_level: RiskLevel
    allowed_roles: tuple[Role, ...]
    handler: ToolHandler


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    def execute(self, name: str, arguments: dict) -> dict:
        tool = self.get(name)
        if tool is None:
            raise KeyError(f"unknown tool: {name}")
        return tool.handler(arguments)


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        Tool(
            name="knowledge_search",
            description="Search internal operations knowledge base.",
            risk_level=RiskLevel.LOW,
            allowed_roles=(Role.VIEWER, Role.OPERATOR, Role.ADMIN),
            handler=_knowledge_search,
        )
    )
    registry.register(
        Tool(
            name="ticket_lookup",
            description="Read production incident ticket information.",
            risk_level=RiskLevel.LOW,
            allowed_roles=(Role.OPERATOR, Role.ADMIN),
            handler=_ticket_lookup,
        )
    )
    registry.register(
        Tool(
            name="risk_assessment",
            description="Assess operational risk from context and tool outputs.",
            risk_level=RiskLevel.MEDIUM,
            allowed_roles=(Role.OPERATOR, Role.ADMIN),
            handler=_risk_assessment,
        )
    )
    registry.register(
        Tool(
            name="change_freeze_override",
            description="Override change freeze window for emergency operations.",
            risk_level=RiskLevel.HIGH,
            allowed_roles=(Role.ADMIN,),
            handler=_change_freeze_override,
        )
    )
    return registry


def _knowledge_search(arguments: dict) -> dict:
    query = str(arguments.get("query", ""))
    articles = [
        {
            "title": "生产告警处理标准流程",
            "summary": "先确认影响面，再检查最近发布、容量指标和依赖服务状态。",
        },
        {
            "title": "变更窗口治理规范",
            "summary": "非紧急变更必须在审批窗口内执行，高风险操作需要管理员确认。",
        },
    ]
    return {"query": query, "matches": articles[:2]}


def _ticket_lookup(arguments: dict) -> dict:
    ticket_id = str(arguments.get("ticket_id") or "TICKET-1001")
    return {
        "ticket_id": ticket_id,
        "service": "payment-gateway",
        "severity": "P2",
        "symptom": "error rate increased after deployment",
        "owner": "platform-oncall",
    }


def _risk_assessment(arguments: dict) -> dict:
    text = " ".join(str(value) for value in arguments.values()).lower()
    score = 0.75 if any(term in text for term in ("p1", "p2", "error", "告警")) else 0.35
    level = "high" if score >= 0.7 else "medium" if score >= 0.4 else "low"
    return {
        "risk_score": score,
        "risk_level": level,
        "recommendation": "建议先回滚最近变更并保持人工确认。" if level == "high" else "建议继续观察并补充指标。",
    }


def _change_freeze_override(arguments: dict) -> dict:
    return {
        "approved": True,
        "change_id": arguments.get("change_id", "CHG-DEMO"),
        "message": "Emergency override recorded for audit.",
    }
