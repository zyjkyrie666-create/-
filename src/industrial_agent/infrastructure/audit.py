from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    run_id: str
    user_id: str
    detail: dict
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class InMemoryAuditSink:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def record(self, event: AuditEvent) -> None:
        self.events.append(event)

    def export(self) -> list[dict]:
        return [asdict(event) for event in self.events]
