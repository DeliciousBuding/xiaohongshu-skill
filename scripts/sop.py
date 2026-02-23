"""
小红书 SOP 编排引擎

提供三种标准操作流程（SOP）：
- 发布 SOP：选题分析 → 内容校验 → 半程预发 → 人工确认 → 发布
- 评论互动 SOP：导航通知页 → 提取待回复 → 逐条回复（冷却间隔）
- 推荐流互动 SOP：浏览推荐流 → 按概率点赞/收藏/评论 → 间隔控制

依赖 templates.py 和 strategy.py
"""

import random
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

from .templates import TemplateEngine, generate_template
from .strategy import StrategyManager, STRATEGY_FILE


class SOPEngine:
    """SOP 编排引擎"""

    def __init__(self, strategy_path: str = STRATEGY_FILE):
        self.strategy = StrategyManager(strategy_path)
        self.log: List[Dict[str, Any]] = []

    def _log_step(self, step: str, status: str, detail: str = ""):
        """记录步骤日志"""
        entry = {
            "step": step,
            "status": status,
            "detail": detail,
            "timestamp": datetime.now().isoformat(),
        }
        self.log.append(entry)
        print(f"[SOP] {step}: {status} {detail}", file=sys.stderr)

    def get_log(self) -> List[Dict[str, Any]]:
        """获取执行日志"""
        return list(self.log)

    # ============================================================
    # 发布 SOP
    # ============================================================

    def publish_sop(
        self,
        topic: str,
        note_type: str = "图文",
        title: Optional[str] = None,
        content: Optional[str] = None,
        image_paths: Optional[List[str]] = None,
        auto_publish: bool = False,
    ) -> Dict[str, Any]:
        """
        发布 SOP：选题分析 → 内容校验 → 模板生成 → 发布准备

        此方法不实际操作浏览器，而是生成完整的发布计划。
        实际发布需调用 publish 模块的相应方法。

        Args:
            topic: 选题
            note_type: 笔记类型（图文/视频/长文）
            title: 自定义标题（为空则自动生成）
            content: 自定义正文（为空则使用模板）
            image_paths: 图片路径列表（图文类型必需）
            auto_publish: 是否建议自动发布

        Returns:
            发布计划
        """
        self.log = []

        # Step 1: 配额检查
        self._log_step("配额检查", "开始")
        limit_check = self.strategy.check_daily_limit("publishes")
        if not limit_check["allowed"]:
            self._log_step("配额检查", "失败", f"今日发布已达上限 ({limit_check['limit']})")
            return {
                "status": "blocked",
                "reason": "daily_limit_exceeded",
                "message": f"今日发布已达上限 ({limit_check['used']}/{limit_check['limit']})",
                "log": self.get_log(),
            }
        self._log_step("配额检查", "通过", f"剩余 {limit_check['remaining']} 次")

        # Step 2: 选题分析 + 模板生成
        self._log_step("选题分析", "开始", topic)
        template = generate_template(topic, note_type)
        self._log_step("选题分析", "完成", f"生成 {len(template['titles'])} 个标题建议")

        # Step 3: 确定标题和内容
        final_title = title or template["titles"][0]
        final_content = content or template["content"]["hook"] + "\n\n（请在此填写正文内容）\n\n" + template["content"]["closing"]
        suggested_tags = template["tags"]

        self._log_step("内容准备", "完成", f"标题: {final_title}")

        # Step 4: 内容校验
        self._log_step("内容校验", "开始")
        validation = TemplateEngine.validate(final_title, final_content, suggested_tags, note_type)
        if not validation["valid"]:
            self._log_step("内容校验", "失败", str(validation["errors"]))
            return {
                "status": "validation_error",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
                "log": self.get_log(),
            }
        if validation["warnings"]:
            self._log_step("内容校验", "警告", str(validation["warnings"]))
        else:
            self._log_step("内容校验", "通过")

        # Step 5: 生成发布计划
        self._log_step("发布计划", "生成完成")

        plan = {
            "status": "ready",
            "action": f"publish_{note_type}",
            "topic": topic,
            "note_type": note_type,
            "title": final_title,
            "title_suggestions": template["titles"],
            "content": final_content,
            "tags": suggested_tags,
            "image_paths": image_paths or [],
            "auto_publish": auto_publish,
            "validation": validation,
            "strategy_info": {
                "publish_remaining": limit_check["remaining"],
                "best_times": self.strategy.config.get("best_publish_times", []),
            },
            "message": "发布计划已生成。请确认内容后执行发布。",
            "log": self.get_log(),
        }

        # 记录操作
        self.strategy.record_action("publishes")

        return plan

    # ============================================================
    # 评论互动 SOP
    # ============================================================

    def comment_sop(
        self,
        replies: List[Dict[str, str]],
        cooldown_min: float = 15.0,
        cooldown_max: float = 30.0,
    ) -> Dict[str, Any]:
        """
        评论互动 SOP：逐条回复，每条之间有冷却间隔

        此方法不实际操作浏览器，而是生成回复计划并校验配额。
        实际回复需调用 comment 模块。

        Args:
            replies: 回复列表，每项包含 {feed_id, xsec_token, content, [comment_id], [reply_user_id]}
            cooldown_min: 回复间最小冷却（秒）
            cooldown_max: 回复间最大冷却（秒）

        Returns:
            回复计划
        """
        self.log = []

        # Step 1: 配额检查
        self._log_step("配额检查", "开始")
        comment_limit = self.strategy.check_daily_limit("comments")
        reply_limit = self.strategy.check_daily_limit("replies")

        # 区分评论和回复
        comments = [r for r in replies if "comment_id" not in r]
        reply_items = [r for r in replies if "comment_id" in r]

        if comments and not comment_limit["allowed"]:
            self._log_step("配额检查", "警告", "评论配额已用完")
        if reply_items and not reply_limit["allowed"]:
            self._log_step("配额检查", "警告", "回复配额已用完")

        available_comments = min(len(comments), comment_limit["remaining"])
        available_replies = min(len(reply_items), reply_limit["remaining"])

        self._log_step("配额检查", "完成",
                       f"评论 {available_comments}/{len(comments)}, 回复 {available_replies}/{len(reply_items)}")

        # Step 2: 内容校验
        self._log_step("内容校验", "开始")
        valid_items = []
        rejected_items = []
        for item in replies:
            content = item.get("content", "")
            if not content or not content.strip():
                rejected_items.append({"item": item, "reason": "内容为空"})
            elif len(content) > 280:
                rejected_items.append({"item": item, "reason": "内容超长"})
            else:
                valid_items.append(item)

        self._log_step("内容校验", "完成",
                       f"有效 {len(valid_items)}, 拒绝 {len(rejected_items)}")

        # Step 3: 生成执行计划
        self._log_step("执行计划", "生成")

        # 截取到配额范围内
        executable = valid_items[:available_comments + available_replies]
        estimated_time = len(executable) * (cooldown_min + cooldown_max) / 2

        plan = {
            "status": "ready",
            "action": "comment_sop",
            "total_items": len(replies),
            "executable_items": len(executable),
            "rejected_items": rejected_items,
            "items": executable,
            "cooldown_range": [cooldown_min, cooldown_max],
            "estimated_time_seconds": estimated_time,
            "quota": {
                "comments": {"used": comment_limit["used"], "limit": comment_limit["limit"]},
                "replies": {"used": reply_limit["used"], "limit": reply_limit["limit"]},
            },
            "message": f"回复计划已生成，共 {len(executable)} 条，预计耗时 {estimated_time:.0f} 秒。",
            "log": self.get_log(),
        }

        return plan

    # ============================================================
    # 推荐流互动 SOP
    # ============================================================

    def explore_sop(
        self,
        feed_count: int = 10,
        like_probability: float = 0.3,
        collect_probability: float = 0.1,
        comment_probability: float = 0.05,
        browse_interval_min: float = 5.0,
        browse_interval_max: float = 10.0,
    ) -> Dict[str, Any]:
        """
        推荐流互动 SOP：模拟自然浏览行为

        生成互动计划（哪些笔记要点赞/收藏/评论），不实际操作浏览器。

        Args:
            feed_count: 浏览笔记数量
            like_probability: 点赞概率
            collect_probability: 收藏概率
            comment_probability: 评论概率
            browse_interval_min: 浏览间隔下限（秒）
            browse_interval_max: 浏览间隔上限（秒）

        Returns:
            互动计划
        """
        self.log = []

        # Step 1: 配额检查
        self._log_step("配额检查", "开始")
        like_limit = self.strategy.check_daily_limit("likes")
        collect_limit = self.strategy.check_daily_limit("collects")
        comment_limit = self.strategy.check_daily_limit("comments")

        self._log_step("配额检查", "完成",
                       f"点赞剩余 {like_limit['remaining']}, "
                       f"收藏剩余 {collect_limit['remaining']}, "
                       f"评论剩余 {comment_limit['remaining']}")

        # Step 2: 生成互动计划
        self._log_step("互动计划", "生成中")
        actions_plan = []
        total_likes = 0
        total_collects = 0
        total_comments = 0

        for i in range(feed_count):
            actions = []

            # 按概率决定互动行为
            if random.random() < like_probability and total_likes < like_limit["remaining"]:
                actions.append("like")
                total_likes += 1
            if random.random() < collect_probability and total_collects < collect_limit["remaining"]:
                actions.append("collect")
                total_collects += 1
            if random.random() < comment_probability and total_comments < comment_limit["remaining"]:
                actions.append("comment")
                total_comments += 1

            actions_plan.append({
                "feed_index": i + 1,
                "actions": actions,
                "interval": round(random.uniform(browse_interval_min, browse_interval_max), 1),
            })

        estimated_time = sum(a["interval"] for a in actions_plan)

        self._log_step("互动计划", "完成",
                       f"点赞 {total_likes}, 收藏 {total_collects}, 评论 {total_comments}")

        plan = {
            "status": "ready",
            "action": "explore_sop",
            "feed_count": feed_count,
            "probabilities": {
                "like": like_probability,
                "collect": collect_probability,
                "comment": comment_probability,
            },
            "planned_actions": {
                "likes": total_likes,
                "collects": total_collects,
                "comments": total_comments,
            },
            "actions_plan": actions_plan,
            "estimated_time_seconds": estimated_time,
            "quota_remaining": {
                "likes": like_limit["remaining"] - total_likes,
                "collects": collect_limit["remaining"] - total_collects,
                "comments": comment_limit["remaining"] - total_comments,
            },
            "message": f"推荐流互动计划已生成，共 {feed_count} 条笔记，"
                       f"预计点赞 {total_likes} 次、收藏 {total_collects} 次、评论 {total_comments} 次，"
                       f"预计耗时 {estimated_time:.0f} 秒。",
            "log": self.get_log(),
        }

        return plan


# ============================================================
# 便捷函数
# ============================================================

def run_publish_sop(topic: str, note_type: str = "图文",
                    title: Optional[str] = None, content: Optional[str] = None,
                    image_paths: Optional[List[str]] = None,
                    auto_publish: bool = False,
                    strategy_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """执行发布 SOP"""
    engine = SOPEngine(strategy_path)
    return engine.publish_sop(topic, note_type, title, content, image_paths, auto_publish)


def run_comment_sop(replies: List[Dict[str, str]],
                    cooldown_min: float = 15.0, cooldown_max: float = 30.0,
                    strategy_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """执行评论互动 SOP"""
    engine = SOPEngine(strategy_path)
    return engine.comment_sop(replies, cooldown_min, cooldown_max)


def run_explore_sop(feed_count: int = 10,
                    like_probability: float = 0.3,
                    collect_probability: float = 0.1,
                    comment_probability: float = 0.05,
                    strategy_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """执行推荐流互动 SOP"""
    engine = SOPEngine(strategy_path)
    return engine.explore_sop(feed_count, like_probability, collect_probability, comment_probability)
