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
                reason="先检索学习方法和课程规划知识。",
            )
        ]

        course_match = re.search(
            r"(高数|线代|英语|机器学习|数据库|计算机网络|操作系统|python|java|math|english|ml)",
            query,
            re.IGNORECASE,
        )
        if course_match or any(term in query for term in ("课程", "作业", "考试", "复习", "论文")):
            plans.append(
                ToolPlan(
                    tool_name="course_lookup",
                    arguments={"course": course_match.group(0) if course_match else "通用课程"},
                    reason="识别课程场景，补充学习重点。",
                )
            )

        plans.append(
            ToolPlan(
                tool_name="study_plan_builder",
                arguments={"query": request.query, "context": request.context},
                reason="把输入拆成可执行的每日学习计划。",
            )
        )

        if any(term in query for term in ("ddl", "deadline", "考试", "作业", "今天", "明天", "下周", "周五")):
            plans.append(
                ToolPlan(
                    tool_name="deadline_risk_check",
                    arguments={"query": request.query, "context": request.context},
                    reason="检查时间压力，提醒优先级和风险。",
                )
            )

        if "强制跳过" in query or "override" in query:
            plans.append(
                ToolPlan(
                    tool_name="deadline_override",
                    arguments={"reason": request.context.get("reason", "demo")},
                    reason="用户请求跳过正常规划流程。",
                )
            )

        return plans

    def summarize(self, request: TaskRequest, tool_outputs: list[dict]) -> str:
        course = next((item for item in tool_outputs if "course" in item), None)
        plan = next((item for item in tool_outputs if "daily_plan" in item), None)
        risk = next((item for item in tool_outputs if "pressure_level" in item), None)

        parts = [f"已收到你的学习需求：{request.query}", ""]

        if course:
            parts.append("一、课程重点")
            parts.append(f"- 课程：{course['course']}")
            parts.extend(f"- {item}" for item in course["focus_points"])
            parts.append("")

        if plan:
            parts.append("二、任务拆解")
            parts.extend(f"- {item}" for item in plan["tasks"])
            parts.append("")
            parts.append("三、每日安排")
            parts.extend(f"- {item['day']}：{item['todo']}" for item in plan["daily_plan"])
            parts.append("")
            parts.append(f"今天优先做：{plan['today_focus']}")

        if risk:
            parts.append("")
            parts.append("四、DDL 风险提醒")
            parts.append(f"- 时间压力：{risk['pressure_level']}")
            parts.append(f"- 建议：{risk['recommendation']}")

        parts.append("")
        parts.append("建议你先按今天的任务执行，完成后再让 Agent 根据进度重新调整计划。")
        return "\n".join(parts)
