"""
互动模块（点赞/收藏）单元测试
"""

import json
from unittest.mock import MagicMock, patch
import pytest

from scripts.interact import InteractAction
from scripts.client import XiaohongshuClient


class TestGetInteractState:
    """测试互动状态获取"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = InteractAction(self.client)

    def test_liked_and_collected(self):
        """已点赞已收藏"""
        self.client.page.evaluate.return_value = json.dumps(
            {"liked": True, "collected": True}
        )
        state = self.action._get_interact_state("feed1")
        assert state["liked"] is True
        assert state["collected"] is True

    def test_not_liked_not_collected(self):
        """未点赞未收藏"""
        self.client.page.evaluate.return_value = json.dumps(
            {"liked": False, "collected": False}
        )
        state = self.action._get_interact_state("feed1")
        assert state["liked"] is False
        assert state["collected"] is False

    def test_empty_result(self):
        """空结果返回默认值"""
        self.client.page.evaluate.return_value = ""
        state = self.action._get_interact_state("feed1")
        assert state["liked"] is False
        assert state["collected"] is False

    def test_invalid_json(self):
        """无效 JSON 返回默认值"""
        self.client.page.evaluate.return_value = "not-json"
        state = self.action._get_interact_state("feed1")
        assert state["liked"] is False
        assert state["collected"] is False


class TestLike:
    """测试点赞"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = InteractAction(self.client)

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    @patch.object(InteractAction, '_click_button', return_value=True)
    def test_like_success(self, mock_click, mock_state, mock_nav):
        """点赞成功"""
        mock_state.return_value = {"liked": False, "collected": False}
        result = self.action.like("feed1", "token1")
        assert result["status"] == "success"
        assert result["action"] == "like"
        mock_click.assert_called_once()

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    def test_like_already_liked(self, mock_state, mock_nav):
        """已经点赞过"""
        mock_state.return_value = {"liked": True, "collected": False}
        result = self.action.like("feed1", "token1")
        assert result["status"] == "success"
        assert result["already_liked"] is True


class TestUnlike:
    """测试取消点赞"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = InteractAction(self.client)

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    @patch.object(InteractAction, '_click_button', return_value=True)
    def test_unlike_success(self, mock_click, mock_state, mock_nav):
        """取消点赞成功"""
        mock_state.return_value = {"liked": True, "collected": False}
        result = self.action.unlike("feed1", "token1")
        assert result["status"] == "success"
        assert result["action"] == "unlike"

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    def test_unlike_not_liked(self, mock_state, mock_nav):
        """未点赞无需取消"""
        mock_state.return_value = {"liked": False, "collected": False}
        result = self.action.unlike("feed1", "token1")
        assert result["already_unliked"] is True


class TestCollect:
    """测试收藏"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = InteractAction(self.client)

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    @patch.object(InteractAction, '_click_button', return_value=True)
    def test_collect_success(self, mock_click, mock_state, mock_nav):
        """收藏成功"""
        mock_state.return_value = {"liked": False, "collected": False}
        result = self.action.collect("feed1", "token1")
        assert result["status"] == "success"
        assert result["action"] == "collect"

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    def test_collect_already_collected(self, mock_state, mock_nav):
        """已收藏"""
        mock_state.return_value = {"liked": False, "collected": True}
        result = self.action.collect("feed1", "token1")
        assert result["already_collected"] is True


class TestUncollect:
    """测试取消收藏"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = InteractAction(self.client)

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    @patch.object(InteractAction, '_click_button', return_value=True)
    def test_uncollect_success(self, mock_click, mock_state, mock_nav):
        """取消收藏成功"""
        mock_state.return_value = {"liked": False, "collected": True}
        result = self.action.uncollect("feed1", "token1")
        assert result["status"] == "success"
        assert result["action"] == "uncollect"

    @patch.object(InteractAction, '_navigate_to_feed')
    @patch.object(InteractAction, '_get_interact_state')
    def test_uncollect_not_collected(self, mock_state, mock_nav):
        """未收藏无需取消"""
        mock_state.return_value = {"liked": False, "collected": False}
        result = self.action.uncollect("feed1", "token1")
        assert result["already_uncollected"] is True


class TestClickButton:
    """测试按钮点击"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = InteractAction(self.client)

    def test_button_found_and_clicked(self):
        """找到按钮并点击"""
        mock_btn = MagicMock()
        mock_btn.count.return_value = 1
        self.client.page.locator.return_value = mock_btn
        result = self.action._click_button(".some-selector", "测试")
        assert result is True
        mock_btn.first.click.assert_called_once()

    def test_button_not_found(self):
        """未找到按钮"""
        mock_btn = MagicMock()
        mock_btn.count.return_value = 0
        self.client.page.locator.return_value = mock_btn
        result = self.action._click_button(".some-selector", "测试")
        assert result is False
