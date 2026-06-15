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
            description="Search campus learning methods and planning tips.",
            risk_level=RiskLevel.LOW,
            allowed_roles=(Role.VIEWER, Role.OPERATOR, Role.ADMIN),
            handler=_knowledge_search,
        )
    )
    registry.register(
        Tool(
            name="course_lookup",
            description="Identify course focus points for a student task.",
            risk_level=RiskLevel.LOW,
            allowed_roles=(Role.OPERATOR, Role.ADMIN),
            handler=_course_lookup,
        )
    )
    registry.register(
        Tool(
            name="study_plan_builder",
            description="Build a short daily study plan from a student request.",
            risk_level=RiskLevel.LOW,
            allowed_roles=(Role.VIEWER, Role.OPERATOR, Role.ADMIN),
            handler=_study_plan_builder,
        )
    )
    registry.register(
        Tool(
            name="deadline_risk_check",
            description="Check deadline pressure and learning priority.",
            risk_level=RiskLevel.MEDIUM,
            allowed_roles=(Role.OPERATOR, Role.ADMIN),
            handler=_deadline_risk_check,
        )
    )
    registry.register(
        Tool(
            name="deadline_override",
            description="Admin-only demo action for skipping normal planning policy.",
            risk_level=RiskLevel.HIGH,
            allowed_roles=(Role.ADMIN,),
            handler=_deadline_override,
        )
    )
    return registry


def _knowledge_search(arguments: dict) -> dict:
    query = str(arguments.get("query", ""))
    articles = [
        {
            "title": "考试复习三步法",
            "summary": "先列考点，再做高频题，最后用错题回顾薄弱知识。",
        },
        {
            "title": "作业拆解方法",
            "summary": "把作业拆成理解题目、查资料、完成初稿、检查提交四步。",
        },
    ]
    return {"query": query, "matches": articles[:2]}


def _course_lookup(arguments: dict) -> dict:
    course = str(arguments.get("course") or "通用课程")
    return {
        "course": course,
        "focus_points": [
            "先确认老师最近强调的章节和题型。",
            "优先处理影响成绩占比最高的作业、考试或项目。",
            "把大任务拆成 30 到 60 分钟可以完成的小块。",
        ],
    }


def _study_plan_builder(arguments: dict) -> dict:
    query = str(arguments.get("query", "")).lower()
    tasks = ["整理任务要求和截止时间", "拆分学习内容", "安排每天可执行的小任务"]
    if any(term in query for term in ("考试", "exam", "复习")):
        tasks.extend(["复习核心概念", "完成一组练习题", "整理错题"])
    if any(term in query for term in ("作业", "homework", "论文", "报告")):
        tasks.extend(["完成作业初稿", "检查格式和提交要求"])

    return {
        "tasks": tasks,
        "daily_plan": [
            {"day": "今天", "todo": "明确任务要求，完成最重要的一小块。"},
            {"day": "明天", "todo": "集中处理难点，至少完成 50% 主体内容。"},
            {"day": "后天", "todo": "查漏补缺，整理错题或修改作业。"},
            {"day": "提交前", "todo": "检查格式、文件名、提交入口和截止时间。"},
        ],
        "today_focus": "先做最接近 DDL、分值最高、最容易卡住的任务。",
    }


def _deadline_risk_check(arguments: dict) -> dict:
    text = " ".join(str(value) for value in arguments.values()).lower()
    urgent_terms = ("今天", "今晚", "明天", "tomorrow")
    medium_terms = ("后天", "这周", "周五", "下周", "ddl", "deadline", "考试", "作业")
    if any(term in text for term in urgent_terms):
        level = "高"
        recommendation = "先暂停低优先级任务，把今天拆成 2 到 3 个专注时段。"
    elif any(term in text for term in medium_terms):
        level = "中"
        recommendation = "建议每天固定一个学习时段，避免把任务集中到最后一天。"
    else:
        level = "低"
        recommendation = "可以按正常节奏推进，但仍建议每天记录完成情况。"
    return {
        "pressure_level": level,
        "recommendation": recommendation,
    }


def _deadline_override(arguments: dict) -> dict:
    return {
        "approved": True,
        "reason": arguments.get("reason", "demo"),
        "message": "Override recorded for demo audit.",
    }
