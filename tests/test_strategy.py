"""
运营策略模块单元测试
"""

import json
import os
import tempfile
import pytest

from scripts.strategy import (
    StrategyManager, init_strategy, show_strategy,
    check_daily_limit, record_action, add_scheduled_post, get_upcoming_posts,
    DEFAULT_DAILY_LIMITS,
)


@pytest.fixture
def tmp_config():
    """创建临时配置文件路径"""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)  # 确保文件不存在
    yield path
    if os.path.exists(path):
        os.unlink(path)


class TestStrategyManager:
    """测试 StrategyManager 基础功能"""

    def test_default_config(self, tmp_config):
        """未初始化时使用默认配置"""
        mgr = StrategyManager(tmp_config)
        assert mgr.config["persona"] == ""
        assert mgr.config["daily_limits"] == DEFAULT_DAILY_LIMITS

    def test_save_and_load(self, tmp_config):
        """保存后可重新加载"""
        mgr = StrategyManager(tmp_config)
        mgr.init_strategy("测试博主")
        mgr2 = StrategyManager(tmp_config)
        assert mgr2.config["persona"] == "测试博主"


class TestInitStrategy:
    """测试初始化策略"""

    def test_basic_init(self, tmp_config):
        """基本初始化"""
        result = init_strategy("旅行博主", config_path=tmp_config)
        assert result["status"] == "success"
        assert result["persona"] == "旅行博主"

    def test_init_with_details(self, tmp_config):
        """带详细信息初始化"""
        result = init_strategy(
            "美食达人",
            target_audience="年轻女性",
            content_direction=["探店", "食谱"],
            config_path=tmp_config,
        )
        assert result["persona"] == "美食达人"
        assert result["target_audience"] == "年轻女性"
        assert len(result["content_direction"]) == 2

    def test_reinit_overwrites(self, tmp_config):
        """重新初始化覆盖旧配置"""
        init_strategy("旧人设", config_path=tmp_config)
        result = init_strategy("新人设", config_path=tmp_config)
        assert result["persona"] == "新人设"


class TestShowStrategy:
    """测试显示策略"""

    def test_show_default(self, tmp_config):
        """显示默认策略"""
        result = show_strategy(config_path=tmp_config)
        assert "persona" in result
        assert "daily_limits" in result
        assert "best_publish_times" in result
        assert "red_lines" in result

    def test_show_after_init(self, tmp_config):
        """初始化后显示"""
        init_strategy("测试", config_path=tmp_config)
        result = show_strategy(config_path=tmp_config)
        assert result["persona"] == "测试"


class TestCheckDailyLimit:
    """测试配额检查"""

    def test_initial_limit(self, tmp_config):
        """初始配额全部可用"""
        result = check_daily_limit("likes", config_path=tmp_config)
        assert result["allowed"] is True
        assert result["used"] == 0
        assert result["limit"] == DEFAULT_DAILY_LIMITS["likes"]
        assert result["remaining"] == DEFAULT_DAILY_LIMITS["likes"]

    def test_after_recording(self, tmp_config):
        """记录操作后配额减少"""
        record_action("likes", config_path=tmp_config)
        result = check_daily_limit("likes", config_path=tmp_config)
        assert result["used"] == 1
        assert result["remaining"] == DEFAULT_DAILY_LIMITS["likes"] - 1

    def test_unknown_action_type(self, tmp_config):
        """未知操作类型配额为 0"""
        result = check_daily_limit("unknown_action", config_path=tmp_config)
        assert result["limit"] == 0
        assert result["allowed"] is False


class TestRecordAction:
    """测试记录操作"""

    def test_record_single(self, tmp_config):
        """记录单次操作"""
        result = record_action("comments", config_path=tmp_config)
        assert result["status"] == "recorded"
        assert result["today_count"] == 1

    def test_record_multiple(self, tmp_config):
        """记录多次操作"""
        record_action("comments", config_path=tmp_config)
        record_action("comments", config_path=tmp_config)
        result = record_action("comments", config_path=tmp_config)
        assert result["today_count"] == 3

    def test_record_different_types(self, tmp_config):
        """记录不同类型操作"""
        record_action("likes", config_path=tmp_config)
        record_action("comments", config_path=tmp_config)
        likes = check_daily_limit("likes", config_path=tmp_config)
        comments = check_daily_limit("comments", config_path=tmp_config)
        assert likes["used"] == 1
        assert comments["used"] == 1


class TestScheduledPosts:
    """测试内容日历"""

    def test_add_post(self, tmp_config):
        """添加内容计划"""
        result = add_scheduled_post("2099-01-01", "测试选题", config_path=tmp_config)
        assert result["status"] == "success"
        assert result["entry"]["topic"] == "测试选题"

    def test_get_upcoming_empty(self, tmp_config):
        """无计划时返回空"""
        result = get_upcoming_posts(config_path=tmp_config)
        assert result["count"] == 0

    def test_get_upcoming_with_future_post(self, tmp_config):
        """未来计划可查询到"""
        # 添加一个未来的计划
        from datetime import datetime, timedelta
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        add_scheduled_post(future_date, "明天的选题", config_path=tmp_config)
        result = get_upcoming_posts(days=7, config_path=tmp_config)
        assert result["count"] == 1
        assert result["posts"][0]["topic"] == "明天的选题"

    def test_past_post_not_shown(self, tmp_config):
        """过去的计划不会显示"""
        add_scheduled_post("2020-01-01", "过去的选题", config_path=tmp_config)
        result = get_upcoming_posts(config_path=tmp_config)
        assert result["count"] == 0
