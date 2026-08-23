"""当前用户主页识别单元测试。"""

from unittest.mock import MagicMock

from scripts.client import XiaohongshuClient
from scripts.login import MAIN_PROFILE_SELECTOR
from scripts.user import UserProfileAction


def test_my_profile_uses_sidebar_profile_link_only():
    """me 命令只从侧边栏“我”的链接提取用户 ID。"""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
    profile_link = MagicMock()
    profile_link.count.return_value = 1
    profile_link.first.is_visible.return_value = True
    profile_link.first.get_attribute.return_value = (
        "/user/profile/62a16ddb00000000210299d9"
    )
    client.page.locator.return_value = profile_link
    action = UserProfileAction(client)
    action.get_user_profile = MagicMock(
        return_value={"userBasicInfo": {"nickname": "momo"}}
    )

    result = action.get_my_profile()

    assert result == {"userBasicInfo": {"nickname": "momo"}}
    client.page.locator.assert_called_once_with(MAIN_PROFILE_SELECTOR)
    action.get_user_profile.assert_called_once_with("62a16ddb00000000210299d9")


def test_my_profile_ignores_feed_profile_links():
    """页面只有推荐流作者链接时不得返回其主页。"""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
    client.page.locator.return_value.count.return_value = 0
    action = UserProfileAction(client)

    assert action.get_my_profile() is None
    client.page.locator.assert_called_once_with(MAIN_PROFILE_SELECTOR)
