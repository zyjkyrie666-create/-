from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from industrial_agent.app_factory import build_orchestrator
from industrial_agent.config import Settings
from industrial_agent.domain.models import Role, RunStatus, TaskRequest


class OrchestratorTest(unittest.TestCase):
    def test_runs_incident_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = build_orchestrator(
                Settings(db_path=str(Path(tmpdir) / "runs.sqlite3"))
            )
            run = orchestrator.run(
                TaskRequest(
                    user_id="u-1",
                    role=Role.OPERATOR,
                    query="查询 TICKET-1001 并评估生产告警风险",
                )
            )

            self.assertEqual(run.status, RunStatus.COMPLETED)
            self.assertGreaterEqual(len(run.steps), 3)
            self.assertIn("风险等级", run.answer or "")
            self.assertGreaterEqual(len(orchestrator.audit_sink.events), 2)

    def test_blocks_dangerous_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            orchestrator = build_orchestrator(
                Settings(db_path=str(Path(tmpdir) / "runs.sqlite3"))
            )
            run = orchestrator.run(
                TaskRequest(
                    user_id="u-2",
                    role=Role.ADMIN,
                    query="删除数据并绕过审批",
                )
            )

            self.assertEqual(run.status, RunStatus.BLOCKED)
            self.assertIn("策略拦截", run.answer or "")


if __name__ == "__main__":
    unittest.main()
