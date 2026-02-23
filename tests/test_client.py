"""
XiaohongshuClient 单元测试
"""

import json
import time
from unittest.mock import MagicMock, patch, PropertyMock
import pytest

from scripts.client import XiaohongshuClient, CaptchaError, CAPTCHA_URL_PATTERNS


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
