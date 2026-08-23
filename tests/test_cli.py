"""
CLI (__main__.py) 单元测试
"""

import json
from unittest.mock import patch

from scripts.__main__ import format_output, main
from scripts.client import CaptchaError


class TestFormatOutput:
    """测试 format_output 格式化函数"""

    def test_none_returns_error_json(self):
        """None 输入应返回包含 error 的 JSON"""
        result = format_output(None)
        parsed = json.loads(result)
        assert "error" in parsed
        assert parsed["error"] == "No data"

    def test_dict_returns_json(self):
        """字典输入应返回有效 JSON"""
        data = {"count": 5, "results": [{"id": "abc"}]}
        result = format_output(data)
        parsed = json.loads(result)
        assert parsed["count"] == 5
        assert len(parsed["results"]) == 1

    def test_empty_dict_returns_json(self):
        """空字典应返回有效 JSON"""
        result = format_output({})
        parsed = json.loads(result)
        assert parsed == {}

    def test_chinese_not_escaped(self):
        """中文字符不应被 unicode 转义"""
        result = format_output({"title": "测试标题"})
        assert "测试标题" in result
        # 不应有 \uXXXX 转义
        assert "\\u" not in result


class TestCLIExceptionHandling:
    """测试 CLI 全局异常捕获"""

    @patch("scripts.__main__.search")
    def test_captcha_error_returns_json(self, mock_search_module, capsys):
        """CaptchaError 应被捕获并输出结构化 JSON"""
        mock_search_module.search.side_effect = CaptchaError(
            url="https://www.xiaohongshu.com/captcha",
            message="触发安全验证"
        )

        with patch("sys.argv", ["scripts", "search", "测试关键词"]):
            exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["status"] == "error"
        assert parsed["error_type"] == "CaptchaError"
        assert "captcha_url" in parsed

    @patch("scripts.__main__.search")
    def test_generic_exception_returns_json(self, mock_search_module, capsys):
        """通用 Exception 应被捕获并输出结构化 JSON"""
        mock_search_module.search.side_effect = RuntimeError("浏览器崩溃")

        with patch("sys.argv", ["scripts", "search", "测试关键词"]):
            exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["status"] == "error"
        assert parsed["error_type"] == "RuntimeError"
        assert "浏览器崩溃" in parsed["message"]

    def test_no_command_returns_zero(self, capsys):
        """无子命令时应返回 0"""
        with patch("sys.argv", ["scripts"]):
            exit_code = main()
        assert exit_code == 0


class TestCLIProfiles:
    """测试 CLI profile 参数"""

    @patch("scripts.__main__.login.check_login")
    def test_profile_uses_isolated_cookie_path(self, mock_check_login, capsys):
        """命名 profile 应使用独立 cookie 路径"""
        mock_check_login.return_value = (False, None)

        with patch("sys.argv", ["scripts", "--profile", "brand-a", "check-login"]):
            exit_code = main()

        assert exit_code == 0
        cookie_path = mock_check_login.call_args.kwargs["cookie_path"]
        assert "profiles" in cookie_path
        assert "brand-a" in cookie_path
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["is_logged_in"] is False

    def test_invalid_profile_returns_json_error(self, capsys):
        """非法 profile 名称应返回结构化错误"""
        with patch("sys.argv", ["scripts", "--profile", "../private", "check-login"]):
            exit_code = main()

        assert exit_code == 1
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["status"] == "error"
        assert parsed["error_type"] == "ProfileNameError"

    @patch("scripts.__main__.list_profiles")
    def test_profiles_command_returns_json(self, mock_list_profiles, capsys):
        """profiles 命令应返回本地 profile 列表"""
        mock_list_profiles.return_value = [
            {"name": "default", "cookie_exists": True, "user_data_dir_exists": True}
        ]

        with patch("sys.argv", ["scripts", "profiles"]):
            exit_code = main()

        assert exit_code == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["count"] == 1
        assert parsed["profiles"][0]["name"] == "default"


class TestCLISelectors:
    """测试 selector contract 命令"""

    def test_selectors_command_returns_contracts(self, capsys):
        """selectors 命令应输出只读 selector contracts"""
        with patch("sys.argv", ["scripts", "selectors", "--owner", "publish"]):
            exit_code = main()

        assert exit_code == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["count"] >= 1
        assert all(item["owner"] == "publish" for item in parsed["contracts"])
        assert any(item["name"] == "publish.publish_button" for item in parsed["contracts"])


class TestCLIContracts:
    """测试 output contract 命令"""

    def test_contracts_command_returns_output_contracts(self, capsys):
        """contracts 命令应输出 CLI JSON 输出契约"""
        with patch("sys.argv", ["scripts", "contracts", "--command", "search"]):
            exit_code = main()

        assert exit_code == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["count"] == 1
        assert parsed["contracts"][0]["command"] == "search"
        assert parsed["contracts"][0]["required_fields"] == ["count", "results"]

class TestPublishExitCodes:
    def test_confirmed_and_ready_are_successful(self):
        from scripts.__main__ import _publish_exit_code

        assert _publish_exit_code({"status": "confirmed"}) == 0
        assert _publish_exit_code({"status": "ready"}) == 0

    def test_unconfirmed_submission_is_indeterminate(self):
        from scripts.__main__ import _publish_exit_code

        assert _publish_exit_code({"status": "submitted_unconfirmed"}) == 2

    def test_failed_submission_is_failure(self):
        from scripts.__main__ import _publish_exit_code

        assert _publish_exit_code({"status": "failed"}) == 1
        assert _publish_exit_code({"status": "error"}) == 1

class TestCLICreatorLogin:
    """测试创作者中心登录子命令"""

    @patch("scripts.__main__.login.creator_login")
    def test_creator_login_logged_in_returns_zero(self, mock_creator_login, capsys):
        mock_creator_login.return_value = {"status": "logged_in", "message": "已登录"}
        with patch("sys.argv", ["scripts", "creator-login"]):
            exit_code = main()
        assert exit_code == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["status"] == "logged_in"

    @patch("scripts.__main__.login.creator_login")
    def test_creator_login_timeout_returns_one(self, mock_creator_login, capsys):
        mock_creator_login.return_value = {"status": "timeout", "message": "超时"}
        with patch("sys.argv", ["scripts", "creator-login"]):
            exit_code = main()
        assert exit_code == 1
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["status"] == "timeout"

    @patch("scripts.__main__.login.check_creator_login")
    def test_check_creator_login_returns_zero(self, mock_check_creator_login, capsys):
        mock_check_creator_login.return_value = True
        with patch("sys.argv", ["scripts", "check-creator-login"]):
            exit_code = main()
        assert exit_code == 0
        parsed = json.loads(capsys.readouterr().out)
        assert parsed["is_logged_in"] is True

    @patch("scripts.__main__.login.check_creator_login")
    def test_check_creator_login_headless_wired_through(self, mock_check_creator_login, capsys):
        mock_check_creator_login.return_value = False
        with patch("sys.argv", ["scripts", "check-creator-login", "--headless", "false"]):
            exit_code = main()
        assert exit_code == 0
        assert mock_check_creator_login.call_args.kwargs["headless"] is False
