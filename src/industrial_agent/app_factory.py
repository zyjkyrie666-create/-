from __future__ import annotations

from industrial_agent.agent.orchestrator import AgentOrchestrator
from industrial_agent.config import Settings
from industrial_agent.domain.policy import PolicyEngine
from industrial_agent.domain.tools import build_default_registry
from industrial_agent.infrastructure.audit import InMemoryAuditSink
from industrial_agent.infrastructure.repository import SQLiteRunRepository
from industrial_agent.llm.openai_adapter import OpenAIPlanner
from industrial_agent.llm.rule_based import RuleBasedPlanner


def build_orchestrator(settings: Settings | None = None) -> AgentOrchestrator:
    settings = settings or Settings.from_env()
    registry = build_default_registry()
    policy = PolicyEngine(registry)
    audit_sink = InMemoryAuditSink()
    repository = SQLiteRunRepository(settings.db_path)
    planner = (
        OpenAIPlanner(settings.openai_api_key)
        if settings.use_openai and settings.openai_api_key
        else RuleBasedPlanner()
    )
    return AgentOrchestrator(
        registry=registry,
        planner=planner,
        policy=policy,
        audit_sink=audit_sink,
        repository=repository,
    )
