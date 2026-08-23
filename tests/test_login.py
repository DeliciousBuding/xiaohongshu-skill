"""Login selector contract integration tests."""

from unittest.mock import MagicMock, patch

from scripts.client import XiaohongshuClient
from scripts.login import LoginAction
from scripts.selectors import LOGIN_PROFILE_LINK_CONTRACT, LOGIN_QRCODE_CONTRACT


def make_login_action():
    """Build a login action with an isolated browser client double."""
    client = MagicMock(spec=XiaohongshuClient)
    client.page = MagicMock()
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
    """The profile fallback uses the profile-link contract primary selector."""
    action = make_login_action()
    qrcode = MagicMock()
    qrcode.count.return_value = 0
    profile_link = MagicMock()
    profile_link.count.return_value = 1
    action.client.page.locator.side_effect = [qrcode, profile_link]
    action.client.context.cookies.return_value = []

    with patch.object(action, "_try_get_username", return_value="tester"):
        result = action.check_login_status(navigate=False)

    assert result == (True, "tester")
    assert action.client.page.locator.call_args_list[1].args == (
        LOGIN_PROFILE_LINK_CONTRACT.primary,
    )
