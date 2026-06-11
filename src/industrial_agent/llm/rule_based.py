from __future__ import annotations

import re

from industrial_agent.domain.models import TaskRequest, ToolPlan
from industrial_agent.domain.tools import Tool


class RuleBasedPlanner:
    """Offline planner used for demos, tests, and local development."""

    def plan(self, request: TaskRequest, tools: list[Tool]) -> list[ToolPlan]:
        del tools
        query = request.query.lower()
        plans: list[ToolPlan] = [
            ToolPlan(
                tool_name="knowledge_search",
                arguments={"query": request.query},
                reason="Search internal knowledge before taking action.",
            )
        ]

        ticket_match = re.search(r"ticket-\d+", query, re.IGNORECASE)
        if "ticket" in query or "工单" in query or ticket_match:
            plans.append(
                ToolPlan(
                    tool_name="ticket_lookup",
                    arguments={"ticket_id": ticket_match.group(0).upper() if ticket_match else "TICKET-1001"},
                    reason="Fetch incident context from ticket system.",
                )
            )

        if any(term in query for term in ("风险", "risk", "告警", "incident", "故障")):
            plans.append(
                ToolPlan(
                    tool_name="risk_assessment",
                    arguments={"query": request.query, "context": request.context},
                    reason="Estimate operational risk and next action.",
                )
            )

        if "override" in query or "绕过" in query:
            plans.append(
                ToolPlan(
                    tool_name="change_freeze_override",
                    arguments={"change_id": request.context.get("change_id", "CHG-DEMO")},
                    reason="User requested emergency override.",
                )
            )

        return plans

    def summarize(self, request: TaskRequest, tool_outputs: list[dict]) -> str:
        risk = next((item for item in tool_outputs if "risk_level" in item), None)
        ticket = next((item for item in tool_outputs if "ticket_id" in item), None)
        parts = [f"已处理请求：{request.query}"]
        if ticket:
            parts.append(
                f"关联工单 {ticket['ticket_id']}，服务 {ticket['service']}，级别 {ticket['severity']}。"
            )
        if risk:
            parts.append(
                f"风险等级 {risk['risk_level']}，建议：{risk['recommendation']}"
            )
        parts.append("所有工具调用已完成策略校验并写入审计记录。")
        return "\n".join(parts)
