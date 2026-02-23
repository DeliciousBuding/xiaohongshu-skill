"""
CLI (__main__.py) 单元测试
"""

import json
import sys
from unittest.mock import patch, MagicMock
import pytest

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
