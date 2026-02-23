"""
首页推荐流模块单元测试
"""

import json
from unittest.mock import MagicMock, patch
import pytest

from scripts.explore import ExploreAction
from scripts.client import XiaohongshuClient


class TestExtractFeeds:
    """测试推荐流数据提取"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = ExploreAction(self.client)

    def test_extract_feeds_success(self):
        """成功提取推荐笔记"""
        mock_data = [
            {
                "id": "note1",
                "xsecToken": "token1",
                "noteCard": {
                    "displayTitle": "测试笔记",
                    "type": "normal",
                    "interactInfo": {"likedCount": "100"},
                    "user": {"nickname": "用户1", "userId": "uid1"},
                    "cover": {"urlDefault": "http://img.com/1.jpg"},
                },
            }
        ]
        self.client.page.evaluate.return_value = json.dumps(mock_data)
        feeds = self.action._extract_feeds()
        assert len(feeds) == 1
        assert feeds[0]["id"] == "note1"
        assert feeds[0]["noteCard"]["displayTitle"] == "测试笔记"

    def test_extract_feeds_empty(self):
        """空数据返回空列表"""
        self.client.page.evaluate.return_value = ""
        feeds = self.action._extract_feeds()
        assert feeds == []

    def test_extract_feeds_invalid_json(self):
        """无效 JSON 返回空列表"""
        self.client.page.evaluate.return_value = "not-json"
        feeds = self.action._extract_feeds()
        assert feeds == []


class TestGetFeeds:
    """测试获取推荐流"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = ExploreAction(self.client)

    @patch.object(ExploreAction, '_extract_feeds')
    def test_get_feeds_enough(self, mock_extract):
        """首次提取就有足够数据"""
        mock_extract.return_value = [{"id": f"note{i}"} for i in range(25)]
        result = self.action.get_feeds(limit=20)
        assert result["count"] == 20
        assert len(result["feeds"]) == 20

    @patch.object(ExploreAction, '_extract_feeds')
    def test_get_feeds_scrolls_for_more(self, mock_extract):
        """数据不够时滚动加载"""
        # 第一次返回 5 条，后续返回更多
        mock_extract.side_effect = [
            [{"id": f"note{i}"} for i in range(5)],
            [{"id": f"note{i}"} for i in range(10)],
            [{"id": f"note{i}"} for i in range(15)],
            [{"id": f"note{i}"} for i in range(20)],
        ]
        result = self.action.get_feeds(limit=20)
        assert result["count"] == 20
        # 应该调用了 scroll_to_bottom
        self.client.scroll_to_bottom.assert_called()

    @patch.object(ExploreAction, '_extract_feeds')
    def test_get_feeds_fewer_than_limit(self, mock_extract):
        """实际数据少于 limit"""
        mock_extract.return_value = [{"id": "note1"}, {"id": "note2"}]
        result = self.action.get_feeds(limit=20)
        assert result["count"] == 2


class TestExploreUrl:
    """测试 URL 常量"""

    def test_explore_url(self):
        """EXPLORE_URL 应指向首页"""
        assert ExploreAction.EXPLORE_URL == "https://www.xiaohongshu.com/explore"
