"""
Opt-in live smoke tests.

These tests touch Xiaohongshu and may open a browser session. They are excluded
from the default pytest run and are also skipped unless XHS_LIVE_TEST=1 is set.
"""

import os

import pytest

from scripts.search import search
from scripts.test_gate import live_skip_reason, should_run_live_tests

pytestmark = [
    pytest.mark.live,
    pytest.mark.e2e,
    pytest.mark.skipif(not should_run_live_tests(), reason=live_skip_reason()),
]


def test_readonly_search_returns_a_list():
    """Search smoke test that does not write to the account."""
    keyword = os.getenv("XHS_LIVE_KEYWORD", "咖啡")
    headless = os.getenv("XHS_LIVE_HEADLESS", "true").lower() != "false"

    results = search(keyword=keyword, limit=1, headless=headless)

    assert isinstance(results, list)
