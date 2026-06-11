from __future__ import annotations

import unittest

from industrial_agent.domain.models import Role, TaskRequest, ToolPlan
from industrial_agent.domain.policy import PolicyEngine
from industrial_agent.domain.tools import build_default_registry


class PolicyEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = build_default_registry()
        self.policy = PolicyEngine(self.registry)

    def test_blocks_dangerous_instruction(self) -> None:
        decision = self.policy.validate_request(
            TaskRequest(query="请删除数据并绕过审批", role=Role.ADMIN)
        )
        self.assertFalse(decision.allowed)

    def test_blocks_high_risk_tool_for_operator(self) -> None:
        decision = self.policy.validate_tool_plan(
            TaskRequest(query="override", role=Role.OPERATOR),
            ToolPlan(tool_name="change_freeze_override"),
        )
        self.assertFalse(decision.allowed)

    def test_allows_low_risk_tool_for_viewer(self) -> None:
        decision = self.policy.validate_tool_plan(
            TaskRequest(query="search", role=Role.VIEWER),
            ToolPlan(tool_name="knowledge_search"),
        )
        self.assertTrue(decision.allowed)


if __name__ == "__main__":
    unittest.main()
