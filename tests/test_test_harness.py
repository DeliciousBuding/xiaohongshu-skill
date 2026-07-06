"""
Test harness behavior.
"""

import time


def test_unit_tests_do_not_sleep_for_real():
    """Unit tests should not wait through production humanization delays."""
    start = time.perf_counter()
    time.sleep(0.05)
    assert time.perf_counter() - start < 0.01
