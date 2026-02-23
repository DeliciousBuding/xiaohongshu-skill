"""
小红书运营策略模块

提供账号定位、每日互动配额、内容日历等运营管理功能
配置持久化到 ~/.xiaohongshu/strategy.json
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


# 配置文件路径
STRATEGY_DIR = os.path.expanduser("~/.xiaohongshu")
STRATEGY_FILE = os.path.join(STRATEGY_DIR, "strategy.json")

# 每日互动配额（安全上限）
DEFAULT_DAILY_LIMITS = {
    "likes": 30,
    "comments": 10,
    "replies": 20,
    "collects": 10,
    "publishes": 3,
}

# 最佳发布时间段
BEST_PUBLISH_TIMES = [
    "07:00-09:00",   # 早高峰通勤
    "11:30-13:30",   # 午休
    "17:30-19:00",   # 晚高峰通勤
    "20:00-22:00",   # 晚间黄金时段
]

# 红线规则
RED_LINES = [
    "单日互动总量不超过 80 次",
    "连续互动不超过 3 次，需批次冷却 15-30 秒",
    "单次评论间隔至少 30 秒",
    "避免深夜（00:00-06:00）大量操作",
    "禁止重复发送相同评论内容",
    "新账号前 7 天减半配额",
]


class StrategyManager:
    """运营策略管理器"""

    def __init__(self, config_path: str = STRATEGY_FILE):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._default_config()

    def _save_config(self):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """默认配置"""
        return {
            "persona": "",
            "target_audience": "",
            "content_direction": [],
            "daily_limits": dict(DEFAULT_DAILY_LIMITS),
            "best_publish_times": list(BEST_PUBLISH_TIMES),
            "red_lines": list(RED_LINES),
            "action_log": {},
            "content_calendar": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    def init_strategy(self, persona: str, target_audience: str = "",
                      content_direction: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        初始化账号定位

        Args:
            persona: 账号人设（如"旅行博主"、"美食达人"）
            target_audience: 目标受众
            content_direction: 内容方向列表

        Returns:
            初始化结果
        """
        self.config["persona"] = persona
        self.config["target_audience"] = target_audience
        self.config["content_direction"] = content_direction or []
        self.config["updated_at"] = datetime.now().isoformat()
        self._save_config()

        return {
            "status": "success",
            "message": f"账号定位已初始化: {persona}",
            "persona": persona,
            "target_audience": target_audience,
            "content_direction": content_direction or [],
        }

    def show_strategy(self) -> Dict[str, Any]:
        """
        显示当前运营策略配置

        Returns:
            完整策略配置
        """
        today = datetime.now().strftime("%Y-%m-%d")
        today_actions = self.config.get("action_log", {}).get(today, {})

        return {
            "persona": self.config.get("persona", "未设置"),
            "target_audience": self.config.get("target_audience", "未设置"),
            "content_direction": self.config.get("content_direction", []),
            "daily_limits": self.config.get("daily_limits", DEFAULT_DAILY_LIMITS),
            "today_usage": today_actions,
            "best_publish_times": self.config.get("best_publish_times", BEST_PUBLISH_TIMES),
            "red_lines": self.config.get("red_lines", RED_LINES),
            "upcoming_posts": self._get_upcoming_posts(7),
        }

    def check_daily_limit(self, action_type: str) -> Dict[str, Any]:
        """
        检查某类操作的每日配额

        Args:
            action_type: 操作类型（likes/comments/replies/collects/publishes）

        Returns:
            {"allowed": bool, "used": int, "limit": int, "remaining": int}
        """
        limits = self.config.get("daily_limits", DEFAULT_DAILY_LIMITS)
        limit = limits.get(action_type, 0)

        today = datetime.now().strftime("%Y-%m-%d")
        today_actions = self.config.get("action_log", {}).get(today, {})
        used = today_actions.get(action_type, 0)

        remaining = max(0, limit - used)
        return {
            "action_type": action_type,
            "allowed": remaining > 0,
            "used": used,
            "limit": limit,
            "remaining": remaining,
        }

    def record_action(self, action_type: str) -> Dict[str, Any]:
        """
        记录一次操作（用于配额追踪）

        Args:
            action_type: 操作类型

        Returns:
            记录结果
        """
        today = datetime.now().strftime("%Y-%m-%d")

        if "action_log" not in self.config:
            self.config["action_log"] = {}
        if today not in self.config["action_log"]:
            self.config["action_log"][today] = {}

        current = self.config["action_log"][today].get(action_type, 0)
        self.config["action_log"][today][action_type] = current + 1
        self.config["updated_at"] = datetime.now().isoformat()
        self._save_config()

        # 清理 7 天前的日志
        self._cleanup_old_logs()

        limit_info = self.check_daily_limit(action_type)
        return {
            "status": "recorded",
            "action_type": action_type,
            "today_count": current + 1,
            "remaining": limit_info["remaining"],
        }

    def add_scheduled_post(self, date: str, topic: str,
                           note_type: str = "图文", notes: str = "") -> Dict[str, Any]:
        """
        添加内容日历条目

        Args:
            date: 日期（YYYY-MM-DD）
            topic: 选题
            note_type: 笔记类型
            notes: 备注

        Returns:
            添加结果
        """
        if "content_calendar" not in self.config:
            self.config["content_calendar"] = []

        entry = {
            "date": date,
            "topic": topic,
            "note_type": note_type,
            "notes": notes,
            "status": "planned",
            "created_at": datetime.now().isoformat(),
        }

        self.config["content_calendar"].append(entry)
        self.config["updated_at"] = datetime.now().isoformat()
        self._save_config()

        return {
            "status": "success",
            "message": f"已添加内容计划: {date} - {topic}",
            "entry": entry,
        }

    def get_upcoming_posts(self, days: int = 7) -> Dict[str, Any]:
        """
        查看未来 N 天的内容计划

        Args:
            days: 天数

        Returns:
            内容计划列表
        """
        posts = self._get_upcoming_posts(days)
        return {
            "days": days,
            "count": len(posts),
            "posts": posts,
        }

    def _get_upcoming_posts(self, days: int) -> List[Dict[str, Any]]:
        """内部方法：获取未来 N 天的计划"""
        calendar = self.config.get("content_calendar", [])
        today = datetime.now().date()
        end_date = today + timedelta(days=days)

        upcoming = []
        for entry in calendar:
            try:
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
                if today <= entry_date <= end_date:
                    upcoming.append(entry)
            except (ValueError, KeyError):
                continue

        upcoming.sort(key=lambda x: x.get("date", ""))
        return upcoming

    def _cleanup_old_logs(self, keep_days: int = 7):
        """清理超过 N 天的操作日志"""
        if "action_log" not in self.config:
            return

        cutoff = (datetime.now() - timedelta(days=keep_days)).strftime("%Y-%m-%d")
        old_keys = [k for k in self.config["action_log"] if k < cutoff]
        for k in old_keys:
            del self.config["action_log"][k]


# ============================================================
# 便捷函数
# ============================================================

def init_strategy(persona: str, target_audience: str = "",
                  content_direction: Optional[List[str]] = None,
                  config_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """初始化运营策略"""
    mgr = StrategyManager(config_path)
    return mgr.init_strategy(persona, target_audience, content_direction)


def show_strategy(config_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """显示运营策略"""
    mgr = StrategyManager(config_path)
    return mgr.show_strategy()


def check_daily_limit(action_type: str,
                      config_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """检查每日配额"""
    mgr = StrategyManager(config_path)
    return mgr.check_daily_limit(action_type)


def record_action(action_type: str,
                  config_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """记录操作"""
    mgr = StrategyManager(config_path)
    return mgr.record_action(action_type)


def add_scheduled_post(date: str, topic: str, note_type: str = "图文",
                       notes: str = "",
                       config_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """添加内容计划"""
    mgr = StrategyManager(config_path)
    return mgr.add_scheduled_post(date, topic, note_type, notes)


def get_upcoming_posts(days: int = 7,
                       config_path: str = STRATEGY_FILE) -> Dict[str, Any]:
    """查看内容计划"""
    mgr = StrategyManager(config_path)
    return mgr.get_upcoming_posts(days)
