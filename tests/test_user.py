"""User profile action tests."""

from unittest.mock import MagicMock, patch

from scripts.client import XiaohongshuClient
from scripts.login import MAIN_PROFILE_SELECTOR
from scripts.user import UserProfileAction


def make_user_action():
    """Build a user profile action with an isolated browser client double."""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
    return UserProfileAction(client)


def test_get_my_profile_uses_login_profile_selector():
    """The logged-in profile link comes from the login module contract."""
    action = make_user_action()
    profile_link = MagicMock()
    profile_link.count.return_value = 0
    action.client.page.locator.return_value = profile_link

    assert action.get_my_profile() is None
    action.client.page.locator.assert_called_once_with(MAIN_PROFILE_SELECTOR)


def test_get_my_profile_extracts_user_id_and_delegates():
    """A visible profile link resolves the user id and fetches the profile."""
    action = make_user_action()
    profile_link = MagicMock()
    profile_link.count.return_value = 1
    profile_link.first.is_visible.return_value = True
    profile_link.first.get_attribute.return_value = "/user/profile/abc123def"
    action.client.page.locator.return_value = profile_link

    expected = {"userBasicInfo": {"nickname": "me"}}
    with patch.object(action, "get_user_profile", return_value=expected) as mock_get:
        assert action.get_my_profile() is expected

    mock_get.assert_called_once_with("abc123def")


def test_get_my_profile_returns_none_when_href_has_no_user_id():
    """A visible link without a profile id must not fabricate a user."""
    action = make_user_action()
    profile_link = MagicMock()
    profile_link.count.return_value = 1
    profile_link.first.is_visible.return_value = True
    profile_link.first.get_attribute.return_value = "/some/other/path"
    action.client.page.locator.return_value = profile_link

    assert action.get_my_profile() is None
