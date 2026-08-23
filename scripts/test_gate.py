"""
Helpers for opt-in live and e2e tests.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

LIVE_TEST_ENV = "XHS_LIVE_TEST"
TRUE_VALUES = {"1", "true", "yes", "y", "on"}


def should_run_live_tests(env: Mapping[str, str] | None = None) -> bool:
    """Return True only when live tests have been explicitly enabled."""
    values = os.environ if env is None else env
    return values.get(LIVE_TEST_ENV, "").strip().lower() in TRUE_VALUES


def live_skip_reason() -> str:
    """Human-readable reason shown for skipped live/e2e tests."""
    return f"set {LIVE_TEST_ENV}=1 to run tests that touch Xiaohongshu or a browser session"
