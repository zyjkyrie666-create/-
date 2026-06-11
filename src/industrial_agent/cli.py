from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from industrial_agent.app_factory import build_orchestrator
from industrial_agent.domain.models import Role, TaskRequest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Industrial AI Agent from CLI.")
    parser.add_argument("query", help="User task or incident description.")
    parser.add_argument("--user-id", default="cli-user")
    parser.add_argument("--role", choices=[role.value for role in Role], default=Role.OPERATOR.value)
    parser.add_argument("--json", action="store_true", help="Print full run payload as JSON.")
    args = parser.parse_args(argv)

    orchestrator = build_orchestrator()
    run = orchestrator.run(
        TaskRequest(
            query=args.query,
            user_id=args.user_id,
            role=Role(args.role),
        )
    )

    if args.json:
        print(json.dumps(asdict(run), ensure_ascii=False, default=str, indent=2))
    else:
        print(run.answer)
    return 0 if run.status.value in {"completed", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
