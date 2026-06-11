from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException

from industrial_agent.agent.orchestrator import run_to_dict
from industrial_agent.api.schemas import RunRequest, RunResponse
from industrial_agent.app_factory import build_orchestrator
from industrial_agent.domain.models import TaskRequest

app = FastAPI(
    title="Industrial AI Agent Platform",
    version="0.1.0",
    description="Enterprise-grade AI Agent runtime with policy, audit, and observability.",
)
orchestrator = build_orchestrator()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/runs", response_model=RunResponse)
def create_run(payload: RunRequest) -> RunResponse:
    run = orchestrator.run(
        TaskRequest(
            query=payload.query,
            user_id=payload.user_id,
            role=payload.role,
            context=payload.context,
            metadata=payload.metadata,
        )
    )
    return RunResponse(
        run_id=run.id,
        status=run.status.value,
        answer=run.answer,
        policy_decisions=run.policy_decisions,
        steps=[asdict(step) for step in run.steps],
    )


@app.get("/api/v1/runs/{run_id}")
def get_run(run_id: str) -> dict:
    if orchestrator.repository is None:
        raise HTTPException(status_code=404, detail="repository is disabled")
    payload = orchestrator.repository.get_payload(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="run not found")
    return payload


@app.get("/api/v1/audit-events")
def list_audit_events() -> list[dict]:
    return orchestrator.audit_sink.export()


@app.get("/api/v1/traces")
def list_traces() -> list[dict]:
    return [asdict(span) for span in orchestrator.trace_recorder.spans]
