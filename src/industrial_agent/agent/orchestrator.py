from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime

from industrial_agent.domain.models import AgentRun, AgentStep, RunStatus, TaskRequest
from industrial_agent.domain.policy import PolicyEngine
from industrial_agent.domain.tools import ToolRegistry
from industrial_agent.infrastructure.audit import AuditEvent, InMemoryAuditSink
from industrial_agent.infrastructure.repository import SQLiteRunRepository
from industrial_agent.llm.base import Planner
from industrial_agent.observability.tracing import TraceRecorder


class AgentOrchestrator:
    def __init__(
        self,
        registry: ToolRegistry,
        planner: Planner,
        policy: PolicyEngine,
        audit_sink: InMemoryAuditSink,
        repository: SQLiteRunRepository | None = None,
        trace_recorder: TraceRecorder | None = None,
    ) -> None:
        self.registry = registry
        self.planner = planner
        self.policy = policy
        self.audit_sink = audit_sink
        self.repository = repository
        self.trace_recorder = trace_recorder or TraceRecorder()

    def run(self, request: TaskRequest) -> AgentRun:
        run = AgentRun(request=request, status=RunStatus.RUNNING)
        self._audit(run, "run_started", {"query": request.query, "role": request.role.value})

        decision = self.policy.validate_request(request)
        run.policy_decisions.append(decision.reason)
        if not decision.allowed:
            run.status = RunStatus.BLOCKED
            run.answer = f"请求已被策略拦截：{decision.reason}"
            self._finish(run)
            return run

        try:
            with self.trace_recorder.span("planner.plan", run_id=run.id):
                run.plan = self.planner.plan(request, self.registry.list_tools())

            tool_outputs: list[dict] = []
            for plan in run.plan:
                decision = self.policy.validate_tool_plan(request, plan)
                run.policy_decisions.append(decision.reason)
                if not decision.allowed:
                    run.steps.append(
                        AgentStep(
                            name=plan.tool_name,
                            status="blocked",
                            input=plan.arguments,
                            error=decision.reason,
                            finished_at=datetime.now(UTC),
                        )
                    )
                    self._audit(run, "tool_blocked", {"tool": plan.tool_name, "reason": decision.reason})
                    continue

                step = AgentStep(name=plan.tool_name, status="running", input=plan.arguments)
                with self.trace_recorder.span("tool.execute", run_id=run.id, tool=plan.tool_name):
                    output = self.registry.execute(plan.tool_name, plan.arguments)
                step.output = output
                step.status = "completed"
                step.finished_at = datetime.now(UTC)
                run.steps.append(step)
                tool_outputs.append(output)
                self._audit(run, "tool_completed", {"tool": plan.tool_name})

            with self.trace_recorder.span("planner.summarize", run_id=run.id):
                run.answer = self.planner.summarize(request, tool_outputs)
            run.status = RunStatus.COMPLETED
        except Exception as exc:
            run.status = RunStatus.FAILED
            run.answer = f"Agent run failed: {exc}"
            self._audit(run, "run_failed", {"error": str(exc)})

        self._finish(run)
        return run

    def _finish(self, run: AgentRun) -> None:
        run.touch()
        self._audit(run, "run_finished", {"status": run.status.value})
        if self.repository is not None:
            self.repository.save(run)

    def _audit(self, run: AgentRun, event_type: str, detail: dict) -> None:
        self.audit_sink.record(
            AuditEvent(
                event_type=event_type,
                run_id=run.id,
                user_id=run.request.user_id,
                detail=detail,
            )
        )


def run_to_dict(run: AgentRun) -> dict:
    payload = asdict(run)
    payload["status"] = run.status.value
    payload["request"]["role"] = run.request.role.value
    return payload
