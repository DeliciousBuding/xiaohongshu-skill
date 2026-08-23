"""Login selector contract and Creator Center login tests."""

import time
from unittest.mock import MagicMock, patch

from scripts.client import XiaohongshuClient
from scripts.login import (
    CREATOR_PUBLISH_URL,
    LoginAction,
    check_creator_login,
    creator_login,
)
from scripts.selectors import (
    LOGIN_PROFILE_LINK_CONTRACT,
    LOGIN_QRCODE_CONTRACT,
)


def make_login_action(url="https://www.xiaohongshu.com/explore"):
    """Build a login action with an isolated browser client double."""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
    client.page.url = url
    client.context = MagicMock()
    return LoginAction(client)


def test_check_login_uses_qrcode_contract_primary():
    """The logged-out signal uses the QR code contract primary selector."""
    action = make_login_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 1
    qrcode.first.is_visible.return_value = True
    action.client.page.locator.return_value = qrcode

    assert action.check_login_status(navigate=False) == (False, None)
    action.client.page.locator.assert_called_once_with(LOGIN_QRCODE_CONTRACT.primary)


def test_check_login_uses_profile_link_contract_primary():
    """A visible profile link means logged in, with no cookie check."""
    action = make_login_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    profile_link = MagicMock()
    profile_link.count.return_value = 1
    profile_link.first.is_visible.return_value = True
    action.client.page.locator.side_effect = [qrcode, profile_link]
    action.client.context.cookies.return_value = [{"name": "web_session", "value": "x"}]

    result = action.check_login_status(navigate=False)

    assert result == (True, "已登录用户")
    assert action.client.page.locator.call_args_list[1].args == (
        LOGIN_PROFILE_LINK_CONTRACT.primary,
    )
    action.client.context.cookies.assert_not_called()


def test_check_login_ignores_stale_cookie_without_profile_link():
    """A stale web_session cookie alone must not count as logged in."""
    action = make_login_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    profile_link = MagicMock()
    profile_link.count.return_value = 0
    action.client.page.locator.side_effect = [qrcode, profile_link]
    action.client.context.cookies.return_value = [{"name": "web_session", "value": "x"}]

    assert action.check_login_status(navigate=False) == (False, None)
    action.client.context.cookies.assert_not_called()


def test_check_login_requires_visible_profile_link():
    """An invisible profile link is not a login signal."""
    action = make_login_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    profile_link = MagicMock()
    profile_link.count.return_value = 1
    profile_link.first.is_visible.return_value = False
    action.client.page.locator.side_effect = [qrcode, profile_link]

    assert action.check_login_status(navigate=False) == (False, None)


def test_check_login_navigates_when_requested():
    """navigate=True drives the client to the explore page first."""
    action = make_login_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    profile_link = MagicMock()
    profile_link.count.return_value = 0
    action.client.page.locator.side_effect = [qrcode, profile_link]

    assert action.check_login_status(navigate=True) == (False, None)
    action.client.navigate.assert_called_once_with("https://www.xiaohongshu.com/explore")


def test_check_creator_login_status_detects_login_page():
    action = make_login_action(url="https://creator.xiaohongshu.com/login")
    assert action.check_creator_login_status(navigate=False) is False


def test_check_creator_login_status_detects_captcha_page():
    action = make_login_action(url="https://creator.xiaohongshu.com/captcha")
    assert action.check_creator_login_status(navigate=False) is False


def test_check_creator_login_status_detects_ready_visible():
    action = make_login_action(url="https://creator.xiaohongshu.com/publish/publish")
    loc = MagicMock()
    loc.count.return_value = 1
    loc.first.is_visible.return_value = True
    action.client.page.locator.return_value = loc

    assert action.check_creator_login_status(navigate=False) is True


def test_check_creator_login_status_home_redirect_after_login():
    """After login the browser may land on the Creator Center home (no upload area)."""
    action = make_login_action(url="https://creator.xiaohongshu.com/")
    loc = MagicMock()
    loc.count.return_value = 0
    action.client.page.locator.return_value = loc

    assert action.check_creator_login_status(navigate=False) is True


def test_check_creator_login_status_unknown_offsite_is_not_ready():
    action = make_login_action(url="https://example.com/publish/publish")
    loc = MagicMock()
    loc.count.return_value = 0
    action.client.page.locator.return_value = loc

    assert action.check_creator_login_status(navigate=False) is False


def test_check_creator_login_navigates_to_publish_page():
    action = make_login_action(url="https://creator.xiaohongshu.com/login")
    assert action.check_creator_login_status(navigate=True) is False
    action.client.navigate.assert_called_once_with(CREATOR_PUBLISH_URL)


def test_wait_for_creator_login_succeeds_when_ready():
    action = make_login_action()
    calls = {"n": 0}

    def fake_check(navigate=False):
        calls["n"] += 1
        return calls["n"] >= 2

    action.check_creator_login_status = fake_check
    assert action.wait_for_creator_login(timeout=10) is True
    action.client._save_cookies.assert_called_once()


def test_wait_for_creator_login_times_out(monkeypatch):
    action = make_login_action()
    action.check_creator_login_status = MagicMock(return_value=False)
    times = iter([0.0, 5.0, 999.0])
    monkeypatch.setattr(time, "time", lambda: next(times))

    assert action.wait_for_creator_login(timeout=10) is False
    action.client._save_cookies.assert_not_called()


@patch("scripts.login.XiaohongshuClient")
def test_creator_login_already_logged_in(mock_cls):
    mock_cls.return_value.page = MagicMock()
    with patch.object(LoginAction, "check_creator_login_status", return_value=True):
        result = creator_login(headless=False, cookie_path="c.json", timeout=10)

    assert result == {"status": "logged_in", "message": "创作者中心已登录"}


@patch("scripts.login.XiaohongshuClient")
def test_creator_login_headless_requires_visible_browser(mock_cls):
    mock_cls.return_value.page = MagicMock()
    with patch.object(LoginAction, "check_creator_login_status", return_value=False):
        result = creator_login(headless=True, cookie_path="c.json", timeout=10)

    assert result["status"] == "login_required"


@patch("scripts.login.XiaohongshuClient")
def test_creator_login_timeout(mock_cls):
    mock_cls.return_value.page = MagicMock()
    with patch.object(LoginAction, "check_creator_login_status", return_value=False), \
         patch.object(LoginAction, "wait_for_creator_login", return_value=False):
        result = creator_login(headless=False, cookie_path="c.json", timeout=10)

    assert result["status"] == "timeout"


@patch("scripts.login.XiaohongshuClient")
def test_check_creator_login_returns_bool(mock_cls):
    mock_cls.return_value.page = MagicMock()
    with patch.object(LoginAction, "check_creator_login_status", return_value=True):
        assert check_creator_login(cookie_path="c.json", headless=True) is True
    mock_cls.return_value.close.assert_called_once()
