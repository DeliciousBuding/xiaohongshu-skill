"""登录状态检测单元测试。"""

from unittest.mock import MagicMock

from scripts.client import XiaohongshuClient
from scripts.login import LoginAction


def make_action() -> tuple[LoginAction, MagicMock]:
    """创建不访问网络的登录动作。"""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
    client.context = MagicMock()
    return LoginAction(client), client


def test_web_session_wins_over_stale_visible_qrcode():
    """有效会话不应被页面上残留的二维码误判为未登录。"""
    action, client = make_action()
    client.context.cookies.return_value = [{"name": "web_session"}]
    action._try_get_username = MagicMock(return_value="测试用户")

    is_logged_in, username = action.check_login_status(navigate=False)

    assert is_logged_in is True
    assert username == "测试用户"
    client.page.locator.assert_not_called()


def test_visible_qrcode_without_web_session_is_logged_out():
    """没有会话且二维码可见时应判定为未登录。"""
    action, client = make_action()
    client.context.cookies.return_value = []
    qrcode = MagicMock()
    qrcode.count.return_value = 1
    qrcode.first.is_visible.return_value = True
    client.page.locator.return_value = qrcode

    assert action.check_login_status(navigate=False) == (False, None)


def test_creator_login_requires_publish_page_not_login_redirect():
    """创作者中心跳转到登录页时应判定为未登录。"""
    action, client = make_action()
    client.page.url = "https://creator.xiaohongshu.com/login?redirectReason=401"

    assert action.check_creator_login_status(navigate=False) is False
    client.page.locator.assert_not_called()


def test_creator_login_accepts_ready_publish_page():
    """发布页上传区已加载时应判定创作者中心已登录。"""
    action, client = make_action()
    client.page.url = "https://creator.xiaohongshu.com/publish/publish?source=official"
    client.page.locator.return_value.count.return_value = 1

    assert action.check_creator_login_status(navigate=False) is True
