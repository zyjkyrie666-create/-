from __future__ import annotations

from industrial_agent.domain.models import TaskRequest, ToolPlan
from industrial_agent.domain.tools import Tool
from industrial_agent.llm.rule_based import RuleBasedPlanner


class OpenAIPlanner:
    """Placeholder adapter for production LLM integration.

    The project keeps this adapter thin so enterprise teams can route calls through
    OpenAI, Azure OpenAI, a private gateway, or an internal model service without
    changing the Agent runtime.
    """

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.fallback = RuleBasedPlanner()

    def plan(self, request: TaskRequest, tools: list[Tool]) -> list[ToolPlan]:
        # Production implementation would call the model with tool schemas here.
        return self.fallback.plan(request, tools)

    def summarize(self, request: TaskRequest, tool_outputs: list[dict]) -> str:
        return self.fallback.summarize(request, tool_outputs)
