"""
SOP 编排引擎单元测试
"""

import tempfile
import os
import pytest

from scripts.sop import SOPEngine, run_publish_sop, run_comment_sop, run_explore_sop
from scripts.strategy import StrategyManager, STRATEGY_FILE


@pytest.fixture
def tmp_config():
    """创建临时策略配置文件"""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)
    yield path
    if os.path.exists(path):
        os.unlink(path)


class TestSOPEngine:
    """测试 SOP 引擎基础"""

    def test_init(self, tmp_config):
        """引擎初始化"""
        engine = SOPEngine(tmp_config)
        assert engine.log == []

    def test_log_step(self, tmp_config):
        """步骤日志记录"""
        engine = SOPEngine(tmp_config)
        engine._log_step("测试步骤", "成功", "详情")
        assert len(engine.log) == 1
        assert engine.log[0]["step"] == "测试步骤"
        assert engine.log[0]["status"] == "成功"


class TestPublishSOP:
    """测试发布 SOP"""

    def test_basic_publish_sop(self, tmp_config):
        """基本发布 SOP"""
        result = run_publish_sop("旅行攻略", strategy_path=tmp_config)
        assert result["status"] == "ready"
        assert result["topic"] == "旅行攻略"
        assert "title" in result
        assert "title_suggestions" in result
        assert "content" in result
        assert "tags" in result
        assert "log" in result

    def test_publish_sop_with_custom_title(self, tmp_config):
        """带自定义标题的发布 SOP"""
        result = run_publish_sop(
            "美食", title="我的美食日记", strategy_path=tmp_config,
        )
        assert result["title"] == "我的美食日记"

    def test_publish_sop_video_type(self, tmp_config):
        """视频类型发布 SOP"""
        result = run_publish_sop("美食", note_type="视频", strategy_path=tmp_config)
        assert result["note_type"] == "视频"

    def test_publish_sop_longform_type(self, tmp_config):
        """长文类型发布 SOP"""
        result = run_publish_sop("学习方法", note_type="长文", strategy_path=tmp_config)
        assert result["note_type"] == "长文"

    def test_publish_sop_quota_exceeded(self, tmp_config):
        """配额耗尽时阻止发布"""
        mgr = StrategyManager(tmp_config)
        # 设置发布上限为 1
        mgr.config["daily_limits"]["publishes"] = 1
        mgr._save_config()
        # 第一次成功
        result = run_publish_sop("测试", strategy_path=tmp_config)
        assert result["status"] == "ready"
        # 第二次被阻止
        result = run_publish_sop("测试2", strategy_path=tmp_config)
        assert result["status"] == "blocked"

    def test_publish_sop_has_strategy_info(self, tmp_config):
        """结果包含策略信息"""
        result = run_publish_sop("测试", strategy_path=tmp_config)
        assert "strategy_info" in result
        assert "publish_remaining" in result["strategy_info"]


class TestCommentSOP:
    """测试评论互动 SOP"""

    def test_basic_comment_sop(self, tmp_config):
        """基本评论 SOP"""
        replies = [
            {"feed_id": "f1", "xsec_token": "t1", "content": "好棒"},
            {"feed_id": "f2", "xsec_token": "t2", "content": "感谢分享"},
        ]
        result = run_comment_sop(replies, strategy_path=tmp_config)
        assert result["status"] == "ready"
        assert result["total_items"] == 2

    def test_empty_replies(self, tmp_config):
        """空回复列表"""
        result = run_comment_sop([], strategy_path=tmp_config)
        assert result["status"] == "ready"
        assert result["total_items"] == 0

    def test_invalid_content_rejected(self, tmp_config):
        """无效内容被拒绝"""
        replies = [
            {"feed_id": "f1", "xsec_token": "t1", "content": ""},  # 空内容
            {"feed_id": "f2", "xsec_token": "t2", "content": "正常回复"},
        ]
        result = run_comment_sop(replies, strategy_path=tmp_config)
        assert len(result["rejected_items"]) == 1
        assert result["executable_items"] == 1

    def test_too_long_content_rejected(self, tmp_config):
        """超长内容被拒绝"""
        replies = [
            {"feed_id": "f1", "xsec_token": "t1", "content": "测" * 300},
        ]
        result = run_comment_sop(replies, strategy_path=tmp_config)
        assert len(result["rejected_items"]) == 1

    def test_comment_sop_has_quota(self, tmp_config):
        """结果包含配额信息"""
        result = run_comment_sop([], strategy_path=tmp_config)
        assert "quota" in result
        assert "comments" in result["quota"]
        assert "replies" in result["quota"]

    def test_reply_items_separated(self, tmp_config):
        """评论和回复被正确区分"""
        replies = [
            {"feed_id": "f1", "xsec_token": "t1", "content": "评论"},
            {"feed_id": "f2", "xsec_token": "t2", "content": "回复",
             "comment_id": "c1", "reply_user_id": "u1"},
        ]
        result = run_comment_sop(replies, strategy_path=tmp_config)
        assert result["total_items"] == 2


class TestExploreSOP:
    """测试推荐流互动 SOP"""

    def test_basic_explore_sop(self, tmp_config):
        """基本推荐流 SOP"""
        result = run_explore_sop(feed_count=5, strategy_path=tmp_config)
        assert result["status"] == "ready"
        assert result["feed_count"] == 5
        assert len(result["actions_plan"]) == 5

    def test_explore_sop_probabilities(self, tmp_config):
        """概率设置"""
        result = run_explore_sop(
            feed_count=10,
            like_probability=1.0,  # 100% 点赞
            collect_probability=0.0,  # 0% 收藏
            comment_probability=0.0,
            strategy_path=tmp_config,
        )
        assert result["planned_actions"]["likes"] > 0
        assert result["planned_actions"]["collects"] == 0
        assert result["planned_actions"]["comments"] == 0

    def test_explore_sop_zero_feeds(self, tmp_config):
        """零条笔记"""
        result = run_explore_sop(feed_count=0, strategy_path=tmp_config)
        assert result["feed_count"] == 0
        assert len(result["actions_plan"]) == 0

    def test_explore_sop_has_intervals(self, tmp_config):
        """每条笔记有浏览间隔"""
        result = run_explore_sop(feed_count=3, strategy_path=tmp_config)
        for action in result["actions_plan"]:
            assert "interval" in action
            assert action["interval"] > 0

    def test_explore_sop_respects_quota(self, tmp_config):
        """遵守配额限制"""
        mgr = StrategyManager(tmp_config)
        mgr.config["daily_limits"]["likes"] = 2
        mgr._save_config()

        result = run_explore_sop(
            feed_count=100,
            like_probability=1.0,
            strategy_path=tmp_config,
        )
        assert result["planned_actions"]["likes"] <= 2

    def test_explore_sop_estimated_time(self, tmp_config):
        """预估耗时"""
        result = run_explore_sop(feed_count=5, strategy_path=tmp_config)
        assert result["estimated_time_seconds"] > 0

    def test_explore_sop_quota_remaining(self, tmp_config):
        """剩余配额"""
        result = run_explore_sop(feed_count=5, strategy_path=tmp_config)
        assert "quota_remaining" in result
        assert "likes" in result["quota_remaining"]
