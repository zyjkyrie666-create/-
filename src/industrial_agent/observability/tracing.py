from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from time import perf_counter
from typing import Iterator


@dataclass
class Span:
    name: str
    status: str = "running"
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    duration_ms: float | None = None
    attributes: dict = field(default_factory=dict)


class TraceRecorder:
    def __init__(self) -> None:
        self.spans: list[Span] = []

    @contextmanager
    def span(self, name: str, **attributes: object) -> Iterator[Span]:
        span = Span(name=name, attributes=dict(attributes))
        start = perf_counter()
        try:
            yield span
            span.status = "ok"
        except Exception as exc:
            span.status = "error"
            span.attributes["error"] = str(exc)
            raise
        finally:
            span.duration_ms = round((perf_counter() - start) * 1000, 3)
            self.spans.append(span)
