"""
XiaohongshuClient 单元测试
"""

import json
import time
from unittest.mock import MagicMock

import pytest

from scripts.client import CaptchaError, XiaohongshuClient


class TestInstanceStateIsolation:
    """测试实例状态隔离：多个 Client 的限流状态不应互相干扰"""

    def test_navigate_count_isolated(self):
        """两个 Client 实例的 _navigate_count 应独立"""
        client_a = XiaohongshuClient()
        client_b = XiaohongshuClient()

        client_a._navigate_count = 10
        assert client_b._navigate_count == 0

    def test_last_navigate_time_isolated(self):
        """两个 Client 实例的 _last_navigate_time 应独立"""
        client_a = XiaohongshuClient()
        client_b = XiaohongshuClient()

        client_a._last_navigate_time = 12345.0
        assert client_b._last_navigate_time == 0.0

    def test_session_start_isolated(self):
        """两个 Client 实例的 _session_start 应独立"""
        client_a = XiaohongshuClient()
        client_b = XiaohongshuClient()

        client_a._session_start = 99999.0
        assert client_b._session_start == 0.0


class TestGetDataByPath:
    """测试 get_data_by_path 字典路径解析"""

    def _make_client_with_state(self, state: dict) -> XiaohongshuClient:
        """辅助：创建一个 mock 了 get_initial_state 的 Client"""
        client = XiaohongshuClient()
        client.get_initial_state = MagicMock(return_value=state)
        client.page = MagicMock()
        return client

    def test_simple_path(self):
        """简单路径解析"""
        client = self._make_client_with_state({
            "search": {"feeds": [{"id": "abc"}]}
        })
        result = client.get_data_by_path("search.feeds")
        assert result == [{"id": "abc"}]

    def test_nested_path(self):
        """深层嵌套路径解析"""
        client = self._make_client_with_state({
            "note": {"noteDetailMap": {"abc123": {"title": "测试笔记"}}}
        })
        result = client.get_data_by_path("note.noteDetailMap")
        assert result == {"abc123": {"title": "测试笔记"}}

    def test_value_unwrap(self):
        """Vue Ref value 解包"""
        client = self._make_client_with_state({
            "search": {"feeds": {"value": [{"id": "1"}, {"id": "2"}]}}
        })
        result = client.get_data_by_path("search.feeds")
        assert result == [{"id": "1"}, {"id": "2"}]

    def test_underscore_value_unwrap(self):
        """Vue Ref _value 解包"""
        client = self._make_client_with_state({
            "user": {"notes": {"_value": [{"id": "n1"}]}}
        })
        result = client.get_data_by_path("user.notes")
        assert result == [{"id": "n1"}]

    def test_missing_key_returns_none(self):
        """缺失的 key 应返回 None"""
        client = self._make_client_with_state({"search": {}})
        result = client.get_data_by_path("search.feeds")
        assert result is None

    def test_completely_missing_path_returns_none(self):
        """完全不存在的路径应返回 None"""
        client = self._make_client_with_state({})
        result = client.get_data_by_path("nonexistent.path.deep")
        assert result is None

    def test_empty_state_returns_none(self):
        """空状态应返回 None"""
        client = self._make_client_with_state({})
        result = client.get_data_by_path("search")
        assert result is None


class TestCheckCaptcha:
    """测试验证码检测逻辑"""

    def _make_client_with_url(self, url: str, title: str = "小红书") -> XiaohongshuClient:
        client = XiaohongshuClient()
        client.page = MagicMock()
        client.page.url = url
        client.page.title.return_value = title
        return client

    def test_normal_url_not_captcha(self):
        """正常 URL 不应触发验证码检测"""
        client = self._make_client_with_url("https://www.xiaohongshu.com/explore")
        assert client._check_captcha() is False

    def test_captcha_url_detected(self):
        """包含验证码特征的 URL 应被检测到"""
        client = self._make_client_with_url(
            "https://www.xiaohongshu.com/website-login/captcha?type=slide"
        )
        assert client._check_captcha() is True

    def test_security_verification_url_detected(self):
        """安全验证 URL 应被检测到"""
        client = self._make_client_with_url(
            "https://www.xiaohongshu.com/security-verification?redirect=xxx"
        )
        assert client._check_captcha() is True

    def test_captcha_title_detected(self):
        """包含验证码特征的页面标题应被检测到"""
        client = self._make_client_with_url(
            "https://www.xiaohongshu.com/some-page",
            title="安全验证 - 小红书"
        )
        assert client._check_captcha() is True

    def test_no_page_returns_false(self):
        """page 为 None 时应返回 False"""
        client = XiaohongshuClient()
        client.page = None
        assert client._check_captcha() is False


class TestHandleCaptcha:
    """测试验证码处理（抛出异常）"""

    def test_raises_captcha_error(self):
        """_handle_captcha 应抛出 CaptchaError"""
        client = XiaohongshuClient()
        client.page = MagicMock()
        client.page.url = "https://www.xiaohongshu.com/captcha"
        client._navigate_count = 5

        with pytest.raises(CaptchaError) as exc_info:
            client._handle_captcha()

        assert "captcha" in exc_info.value.captcha_url
        assert "5" in str(exc_info.value)


class TestThrottle:
    """测试频率控制逻辑"""

    def test_first_call_no_delay(self):
        """首次调用不应有延迟"""
        client = XiaohongshuClient()
        start = time.time()
        client._throttle()
        elapsed = time.time() - start
        # 首次调用应该几乎没有延迟
        assert elapsed < 1.0

    def test_session_start_initialized(self):
        """调用后 _session_start 应被初始化"""
        client = XiaohongshuClient()
        assert client._session_start == 0.0
        client._throttle()
        assert client._session_start > 0.0

    def test_navigate_count_incremented(self):
        """每次调用 _navigate_count 应递增"""
        client = XiaohongshuClient()
        assert client._navigate_count == 0
        client._throttle()
        assert client._navigate_count == 1
        client._throttle()
        assert client._navigate_count == 2


class TestBrowserAutomationContract:
    """测试浏览器自动化启动契约"""

    def test_start_uses_persistent_context_and_stealth(self, monkeypatch, tmp_path):
        """start 应使用持久化上下文并注入 stealth 脚本"""
        fake_page = MagicMock()
        fake_context = MagicMock()
        fake_context.cookies.return_value = []
        fake_context.pages = []
        fake_context.new_page.return_value = fake_page

        fake_playwright = MagicMock()
        fake_playwright.chromium.launch_persistent_context.return_value = fake_context

        fake_sync = MagicMock()
        fake_sync.start.return_value = fake_playwright
        monkeypatch.setattr("scripts.client.sync_playwright", lambda: fake_sync)
        monkeypatch.delenv("XHS_ALLOW_NO_SANDBOX", raising=False)

        client = XiaohongshuClient(
            cookie_path=str(tmp_path / "cookies.json"),
            user_data_dir=str(tmp_path / "browser-data"),
        )
        client.STEALTH_JS_PATH = str(tmp_path / "stealth.js")

        client.start()

        call_args = fake_playwright.chromium.launch_persistent_context.call_args
        assert call_args.kwargs["user_data_dir"] == str(tmp_path / "browser-data")
        assert "--enable-automation" in call_args.kwargs["ignore_default_args"]
        assert "--disable-blink-features=AutomationControlled" in call_args.kwargs["args"]
        assert "--no-sandbox" not in call_args.kwargs["args"]
        assert call_args.kwargs["locale"] == "zh-CN"
        assert call_args.kwargs["timezone_id"] == "Asia/Shanghai"
        fake_context.add_init_script.assert_called_once()
        assert "navigator, 'webdriver'" in fake_context.add_init_script.call_args.args[0]
        fake_page.set_default_timeout.assert_called_once_with(client.timeout)

    def test_stealth_script_covers_common_automation_signals(self):
        """内置 stealth 脚本应覆盖常见自动化特征"""
        stealth_js = XiaohongshuClient.STEALTH_JS

        assert "navigator, 'webdriver'" in stealth_js
        assert "window.chrome.runtime" in stealth_js
        assert "navigator, 'plugins'" in stealth_js
        assert "navigator, 'languages'" in stealth_js
        assert "WebGLRenderingContext.prototype.getParameter" in stealth_js
        assert "HTMLCanvasElement.prototype.toDataURL" in stealth_js
        assert "Math.random" not in stealth_js
        assert "__XHS_FINGERPRINT_SEED__" in stealth_js
        assert "Error.prototype, 'stack'" in stealth_js

    def test_same_seed_builds_stable_script_and_seed_is_not_embedded(self, tmp_path):
        """同一 seed 的注入脚本稳定，不把原始 seed 放进脚本。"""
        client = XiaohongshuClient(
            cookie_path=str(tmp_path / "cookies.json"),
            user_data_dir=str(tmp_path / "browser-data"),
        )
        client.STEALTH_JS_PATH = str(tmp_path / "stealth.js")

        first = client._load_stealth_js("private-profile-seed")
        second = client._load_stealth_js("private-profile-seed")
        other = client._load_stealth_js("another-profile-seed")

        assert first == second
        assert first != other
        assert "private-profile-seed" not in first
        assert "__XHS_FINGERPRINT_SEED__" not in first
        assert "__xhsCanvasNoise" in first

    def test_no_sandbox_requires_explicit_environment_switch(
        self, monkeypatch, tmp_path
    ):
        """Only an explicit environment switch may disable Chromium sandboxing."""
        fake_page = MagicMock()
        fake_context = MagicMock()
        fake_context.cookies.return_value = []
        fake_context.pages = []
        fake_context.new_page.return_value = fake_page

        fake_playwright = MagicMock()
        fake_playwright.chromium.launch_persistent_context.return_value = fake_context

        fake_sync = MagicMock()
        fake_sync.start.return_value = fake_playwright
        monkeypatch.setattr("scripts.client.sync_playwright", lambda: fake_sync)
        monkeypatch.setenv("XHS_ALLOW_NO_SANDBOX", "true")

        client = XiaohongshuClient(
            cookie_path=str(tmp_path / "cookies.json"),
            user_data_dir=str(tmp_path / "browser-data"),
        )
        client.STEALTH_JS_PATH = str(tmp_path / "stealth.js")
        client.start()

        call_args = fake_playwright.chromium.launch_persistent_context.call_args
        assert "--no-sandbox" in call_args.kwargs["args"]


class TestCaptchaError:
    """测试 CaptchaError 异常类"""

    def test_attributes(self):
        """CaptchaError 应包含 captcha_url 属性"""
        err = CaptchaError(url="https://example.com/captcha", message="test")
        assert err.captcha_url == "https://example.com/captcha"
        assert str(err) == "test"

    def test_default_message(self):
        """默认消息应包含 URL"""
        err = CaptchaError(url="https://example.com/captcha")
        assert "https://example.com/captcha" in str(err)


class TestCookieBackup:
    """Cookie backup compatibility and redaction tests."""

    def test_legacy_cookie_list_is_loaded_without_logging_values(self, tmp_path, caplog):
        caplog.set_level("INFO")
        cookie_path = tmp_path / "cookies.json"
        secret_value = "sensitive-cookie-value"
        cookies = [{"name": "web_session", "value": secret_value, "domain": ".example"}]
        cookie_path.write_text(json.dumps(cookies), encoding="utf-8")
        client = XiaohongshuClient(
            cookie_path=str(cookie_path),
            user_data_dir=str(tmp_path / "browser-data"),
        )
        client.context = MagicMock()

        client._load_cookies()

        client.context.add_cookies.assert_called_once_with(cookies)
        assert secret_value not in caplog.text

    def test_non_list_cookie_backup_is_ignored(self, tmp_path, caplog):
        cookie_path = tmp_path / "cookies.json"
        cookie_path.write_text('{"cookies": []}', encoding="utf-8")
        client = XiaohongshuClient(
            cookie_path=str(cookie_path),
            user_data_dir=str(tmp_path / "browser-data"),
        )
        client.context = MagicMock()

        client._load_cookies()

        client.context.add_cookies.assert_not_called()
        assert "continuing with browser profile" in caplog.text

    def test_cookie_backup_remains_a_json_array(self, tmp_path, caplog):
        caplog.set_level("INFO")
        cookie_path = tmp_path / "cookies.json"
        secret_value = "sensitive-cookie-value"
        cookies = [{"name": "web_session", "value": secret_value}]
        client = XiaohongshuClient(
            cookie_path=str(cookie_path),
            user_data_dir=str(tmp_path / "browser-data"),
        )
        client.context = MagicMock()
        client.context.cookies.return_value = cookies

        client._save_cookies()

        assert json.loads(cookie_path.read_text(encoding="utf-8")) == cookies
        assert isinstance(json.loads(cookie_path.read_text(encoding="utf-8")), list)
        assert secret_value not in caplog.text
        assert list(tmp_path.glob(".cookies.json.*.tmp")) == []
