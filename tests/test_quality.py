import os
import sys

from scripts import quality


def test_command_plan_check_reuses_docs_lint_and_tests():
    plan = quality.command_plan("check")

    assert plan == [
        [sys.executable, "-m", "scripts.docs_check"],
        [sys.executable, "-m", "scripts.site_check"],
        [sys.executable, "-m", "ruff", "check", "scripts", "tests"],
        [sys.executable, "-m", "pytest", "-q"],
    ]


def test_live_task_sets_env_only_for_child(monkeypatch):
    calls = []
    monkeypatch.delenv("XHS_LIVE_TEST", raising=False)

    def fake_run_many(commands, *, env=None):
        calls.append((commands, env))
        return 0

    monkeypatch.setattr(quality, "_run_many", fake_run_many)

    assert quality.run_task("live") == 0
    assert calls[0][1]["XHS_LIVE_TEST"] == "1"
    assert "XHS_LIVE_TEST" not in os.environ


def test_site_task_accepts_port():
    assert quality.command_plan("site", port=8899) == [
        [
            sys.executable,
            "-m",
            "http.server",
            "8899",
            "--directory",
            "site",
        ]
    ]
