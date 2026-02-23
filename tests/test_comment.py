"""
评论模块单元测试
"""

from unittest.mock import MagicMock, patch, call
import pytest

from scripts.comment import CommentAction, MAX_COMMENT_LENGTH
from scripts.client import XiaohongshuClient


class TestValidateComment:
    """测试评论内容校验（ops 安全理念）"""

    def test_valid_comment(self):
        """正常评论通过校验"""
        assert CommentAction.validate_comment("好棒的笔记！") is None

    def test_empty_comment(self):
        """空评论不通过"""
        result = CommentAction.validate_comment("")
        assert result is not None
        assert "为空" in result

    def test_whitespace_only(self):
        """纯空格不通过"""
        result = CommentAction.validate_comment("   ")
        assert result is not None
        assert "为空" in result

    def test_too_long_comment(self):
        """超长评论不通过"""
        long_text = "测" * (MAX_COMMENT_LENGTH + 1)
        result = CommentAction.validate_comment(long_text)
        assert result is not None
        assert "超长" in result

    def test_exact_max_length(self):
        """刚好 280 字通过"""
        text = "测" * MAX_COMMENT_LENGTH
        assert CommentAction.validate_comment(text) is None


class TestCheckRateLimit:
    """测试频率限制检测（ops 安全理念）"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = CommentAction(self.client)

    def test_no_rate_limit(self):
        """没有频率限制"""
        mock_toast = MagicMock()
        mock_toast.count.return_value = 0
        self.client.page.locator.return_value = mock_toast

        assert self.action._check_rate_limit() is False

    def test_rate_limit_detected(self):
        """检测到频率限制"""
        mock_toast = MagicMock()
        mock_toast.count.return_value = 1
        mock_toast.first.is_visible.return_value = True
        mock_toast.first.text_content.return_value = "评论过于频繁"
        self.client.page.locator.return_value = mock_toast

        assert self.action._check_rate_limit() is True


class TestPostCommentValidation:
    """测试发表评论时的内容校验"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = CommentAction(self.client)

    def test_empty_content_rejected(self):
        """空内容直接返回错误，不导航"""
        result = self.action.post_comment("feed1", "token1", "")
        assert result["status"] == "error"
        assert "为空" in result["message"]
        self.client.navigate.assert_not_called()

    def test_too_long_content_rejected(self):
        """超长内容直接返回错误，不导航"""
        long_text = "测" * 300
        result = self.action.post_comment("feed1", "token1", long_text)
        assert result["status"] == "error"
        assert "超长" in result["message"]
        self.client.navigate.assert_not_called()


class TestMakeFeedUrl:
    """测试 URL 构建"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.action = CommentAction(self.client)

    def test_basic_url(self):
        """基本 URL 构建"""
        url = self.action._make_feed_url("abc123", "token456")
        assert "abc123" in url
        assert "token456" in url
        assert url.startswith("https://www.xiaohongshu.com/explore/")

    def test_default_xsec_source(self):
        """默认 xsec_source 为 pc_feed"""
        url = self.action._make_feed_url("id", "token")
        assert "xsec_source=pc_feed" in url


class TestPostComment:
    """测试发表评论"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = CommentAction(self.client)

    @patch.object(CommentAction, '_navigate_to_feed')
    @patch.object(CommentAction, '_type_and_submit', return_value=True)
    def test_post_comment_success(self, mock_submit, mock_nav):
        """发表评论成功"""
        result = self.action.post_comment("feed1", "token1", "好棒的笔记！")
        assert result["status"] == "success"
        assert result["feed_id"] == "feed1"
        assert result["content"] == "好棒的笔记！"
        mock_nav.assert_called_once_with("feed1", "token1")
        mock_submit.assert_called_once_with("好棒的笔记！")

    @patch.object(CommentAction, '_navigate_to_feed')
    @patch.object(CommentAction, '_type_and_submit', return_value=False)
    def test_post_comment_failure(self, mock_submit, mock_nav):
        """发表评论失败"""
        result = self.action.post_comment("feed1", "token1", "测试")
        assert result["status"] == "error"
        assert "失败" in result["message"]


class TestReplyToComment:
    """测试回复评论"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = CommentAction(self.client)

    @patch.object(CommentAction, '_navigate_to_feed')
    @patch.object(CommentAction, '_type_and_submit', return_value=True)
    def test_reply_success(self, mock_submit, mock_nav):
        """回复评论成功"""
        # Mock locator chain
        mock_locator = MagicMock()
        mock_locator.count.return_value = 0
        self.client.page.locator.return_value = mock_locator
        mock_locator.filter.return_value = mock_locator

        result = self.action.reply_to_comment(
            "feed1", "token1", "comment_id_1", "user_id_1", "感谢分享"
        )
        assert result["status"] == "success"
        assert result["comment_id"] == "comment_id_1"
        assert result["reply_user_id"] == "user_id_1"

    @patch.object(CommentAction, '_navigate_to_feed')
    @patch.object(CommentAction, '_type_and_submit', return_value=False)
    def test_reply_failure(self, mock_submit, mock_nav):
        """回复评论失败"""
        mock_locator = MagicMock()
        mock_locator.count.return_value = 0
        self.client.page.locator.return_value = mock_locator
        mock_locator.filter.return_value = mock_locator

        result = self.action.reply_to_comment(
            "feed1", "token1", "cid", "uid", "回复"
        )
        assert result["status"] == "error"
