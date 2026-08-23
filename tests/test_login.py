"""登录状态检测单元测试。"""

from unittest.mock import MagicMock, patch

from scripts.client import XiaohongshuClient
from scripts.login import MAIN_PROFILE_SELECTOR, QRCODE_SELECTOR, LoginAction


def make_action() -> tuple[LoginAction, MagicMock]:
    """创建不访问网络的登录动作。"""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
    client.context = MagicMock()
    return LoginAction(client), client


def test_visible_qrcode_wins_over_stale_web_session():
    """本地残留会话时，可见二维码仍表示未登录。"""
    action, client = make_action()
    client.context.cookies.return_value = [{"name": "web_session"}]
    qrcode = MagicMock()
    qrcode.count.return_value = 1
    qrcode.first.is_visible.return_value = True
    client.page.locator.return_value = qrcode

    assert action.check_login_status(navigate=False) == (False, None)
    client.page.locator.assert_called_once_with(QRCODE_SELECTOR)
    client.context.cookies.assert_not_called()


def test_feed_profile_links_do_not_mean_logged_in():
    """推荐流作者链接不能作为已登录证据。"""
    action, client = make_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    sidebar_profile = MagicMock()
    sidebar_profile.count.return_value = 0
    client.page.locator.side_effect = [qrcode, sidebar_profile]

    assert action.check_login_status(navigate=False) == (False, None)
    assert client.page.locator.call_args_list[1].args == (MAIN_PROFILE_SELECTOR,)


def test_visible_sidebar_profile_means_logged_in():
    """侧边栏“我”的个人主页链接可作为已登录证据。"""
    action, client = make_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    sidebar_profile = MagicMock()
    sidebar_profile.count.return_value = 1
    sidebar_profile.first.is_visible.return_value = True
    client.page.locator.side_effect = [qrcode, sidebar_profile]

    assert action.check_login_status(navigate=False) == (True, "已登录用户")


@patch("scripts.login.time.sleep")
@patch("scripts.login.time.time", side_effect=[0, 0.1, 0.2])
def test_wait_for_login_uses_page_state_not_stale_cookie(mock_time, mock_sleep):
    """扫码等待应以页面认证状态为准，不得仅检查残留 Cookie。"""
    action, client = make_action()
    client.context.cookies.return_value = [{"name": "web_session"}]
    action.check_login_status = MagicMock(return_value=(True, "已登录用户"))

    assert action.wait_for_login(timeout=1, min_wait=0) is True
    action.check_login_status.assert_called_once_with(navigate=False)
    client.context.cookies.assert_not_called()
    client._save_cookies.assert_called_once_with()
    assert mock_time.call_count == 3
    mock_sleep.assert_called_once_with(5)


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
