"""Cross-platform quality task runner for contributors and CI."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Mapping, Sequence

TASKS = ("check", "test", "lint", "docs-check", "live", "site", "contracts", "skill")


def _run(
    command: Sequence[str],
    *,
    env: Mapping[str, str] | None = None,
) -> int:
    print("$ " + " ".join(command), flush=True)
    return subprocess.run(command, env=None if env is None else dict(env), check=False).returncode


def _run_many(
    commands: Sequence[Sequence[str]],
    *,
    env: Mapping[str, str] | None = None,
) -> int:
    for command in commands:
        code = _run(command, env=env)
        if code != 0:
            return code
    return 0


def command_plan(task: str, *, port: int = 8000) -> list[list[str]]:
    python = sys.executable
    plans = {
        "docs-check": [
            [python, "-m", "scripts.docs_check"],
            [python, "-m", "scripts.site_check"],
        ],
        "lint": [[python, "-m", "ruff", "check", "scripts", "tests"]],
        "test": [[python, "-m", "pytest", "-q"]],
        "live": [[python, "-m", "pytest", "tests/live", "-q", "-m", "live"]],
        "site": [
            [
                python,
                "-m",
                "http.server",
                str(port),
                "--directory",
                "site",
            ]
        ],
        "contracts": [
            [python, "-m", "scripts", "contracts"],
            [python, "-m", "scripts", "selectors"],
        ],
        "skill": [[python, "-m", "scripts.skill_check"]],
    }
    plans["check"] = [
        *plans["docs-check"],
        *plans["lint"],
        *plans["test"],
        *plans["contracts"],
        *plans["skill"],
    ]
    return plans[task]


def run_task(task: str, *, port: int = 8000) -> int:
    env = None
    if task == "live":
        env = os.environ.copy()
        env["XHS_LIVE_TEST"] = "1"
    return _run_many(command_plan(task, port=port), env=env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run repository quality tasks.")
    parser.add_argument("task", nargs="?", choices=TASKS, default="check")
    parser.add_argument("--port", type=int, default=8000, help="Port for the site task.")
    args = parser.parse_args(argv)
    return run_task(args.task, port=args.port)


if __name__ == "__main__":
    sys.exit(main())
