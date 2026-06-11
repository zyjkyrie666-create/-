from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = ".data/agent_runs.sqlite3"
    log_level: str = "INFO"
    use_openai: bool = False
    openai_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=os.getenv("AGENT_DB_PATH", cls.db_path),
            log_level=os.getenv("AGENT_LOG_LEVEL", cls.log_level),
            use_openai=os.getenv("AGENT_USE_OPENAI", "false").lower() == "true",
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        )
