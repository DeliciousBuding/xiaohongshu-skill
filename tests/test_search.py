"""
搜索模块单元测试
"""

import urllib.parse
from unittest.mock import MagicMock
import pytest

from scripts.search import SearchAction, FILTER_OPTIONS_MAP
from scripts.client import XiaohongshuClient


class TestMakeSearchUrl:
    """测试搜索 URL 构建"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.action = SearchAction(self.client)

    def test_basic_keyword(self):
        """基本关键词应正确编码"""
        url = self.action._make_search_url("测试")
        assert "keyword=%E6%B5%8B%E8%AF%95" in url
        assert "source=web_explore_feed" in url
        assert url.startswith("https://www.xiaohongshu.com/search_result?")

    def test_english_keyword(self):
        """英文关键词"""
        url = self.action._make_search_url("food")
        assert "keyword=food" in url

    def test_special_characters(self):
        """特殊字符应被正确 URL 编码"""
        url = self.action._make_search_url("美食 & 旅行")
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        assert params["keyword"] == ["美食 & 旅行"]


class TestFindFilterText:
    """测试筛选文本查找"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.action = SearchAction(self.client)

    def test_sort_by_comprehensive(self):
        """排序-综合"""
        result = self.action._find_filter_text(1, "综合")
        assert result == "综合"

    def test_sort_by_latest(self):
        """排序-最新"""
        result = self.action._find_filter_text(1, "最新")
        assert result == "最新"

    def test_note_type_video(self):
        """笔记类型-视频"""
        result = self.action._find_filter_text(2, "视频")
        assert result == "视频"

    def test_publish_time_week(self):
        """发布时间-一周内"""
        result = self.action._find_filter_text(3, "一周内")
        assert result == "一周内"

    def test_nonexistent_text(self):
        """不存在的筛选文本应返回 None"""
        result = self.action._find_filter_text(1, "不存在的选项")
        assert result is None

    def test_invalid_group(self):
        """无效的分组 ID 应返回 None"""
        result = self.action._find_filter_text(99, "综合")
        assert result is None


class TestFilterOptionsMap:
    """测试筛选选项映射表完整性"""

    def test_has_five_groups(self):
        """应有 5 个筛选分组"""
        assert len(FILTER_OPTIONS_MAP) == 5

    def test_sort_by_options(self):
        """排序分组应有 5 个选项"""
        assert len(FILTER_OPTIONS_MAP[1]) == 5

    def test_note_type_options(self):
        """笔记类型分组应有 3 个选项"""
        assert len(FILTER_OPTIONS_MAP[2]) == 3

    def test_all_options_have_text(self):
        """所有选项都应有 text 字段"""
        for group_id, options in FILTER_OPTIONS_MAP.items():
            for opt in options:
                assert "text" in opt, f"Group {group_id} option missing 'text'"
                assert len(opt["text"]) > 0
