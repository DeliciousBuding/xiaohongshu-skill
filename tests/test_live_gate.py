"""
Live/e2e test gate tests.
"""

import pytest

from scripts.test_gate import live_skip_reason, should_run_live_tests


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        ("", False),
        ("0", False),
        ("false", False),
        ("False", False),
        ("1", True),
        ("true", True),
        ("yes", True),
    ],
)
def test_should_run_live_tests_uses_explicit_env(value, expected):
    """Live tests only run after explicit opt-in."""
    env = {} if value is None else {"XHS_LIVE_TEST": value}

    assert should_run_live_tests(env) is expected


def test_live_skip_reason_names_the_switch():
    """Skip text should tell contributors how to opt in."""
    assert "XHS_LIVE_TEST=1" in live_skip_reason()
