"""
共享 pytest fixtures
"""

from unittest.mock import MagicMock, PropertyMock
import pytest


@pytest.fixture
def mock_page():
    """创建 mock Playwright Page 对象"""
    page = MagicMock()
    page.url = "https://www.xiaohongshu.com/explore"
    page.title.return_value = "小红书"
    page.set_default_timeout = MagicMock()
    page.goto = MagicMock()
    page.evaluate = MagicMock(return_value="")
    page.wait_for_function = MagicMock()
    page.wait_for_load_state = MagicMock()
    page.reload = MagicMock()
    page.close = MagicMock()
    return page


@pytest.fixture
def mock_context(mock_page):
    """创建 mock BrowserContext 对象"""
    context = MagicMock()
    context.new_page.return_value = mock_page
    context.add_cookies = MagicMock()
    context.cookies.return_value = []
    context.close = MagicMock()
    return context


@pytest.fixture
def mock_browser(mock_context):
    """创建 mock Browser 对象"""
    browser = MagicMock()
    browser.new_context.return_value = mock_context
    browser.close = MagicMock()
    return browser


@pytest.fixture
def mock_playwright(mock_browser):
    """创建 mock Playwright 对象"""
    pw = MagicMock()
    pw.chromium.launch.return_value = mock_browser
    pw.stop = MagicMock()
    return pw
