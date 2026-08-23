"""
小红书写作模板系统

提供标题生成、内容模板、标签建议、内容校验等功能
帮助用户快速创建符合小红书风格的笔记
"""

import random
from typing import Any, Dict, List, Optional

# ============================================================
# 内置数据
# ============================================================

# 标题钩子模板（3 种风格）
TITLE_HOOKS = {
    "数字型": [
        "{count}个{topic}技巧，第{n}个绝了",
        "关于{topic}，这{count}点你一定要知道",
        "{topic}必看！{count}个实用方法分享",
        "收藏！{count}个{topic}的实用建议",
        "{count}步搞定{topic}，新手也能学会",
    ],
    "疑问型": [
        "{topic}到底怎么选？看完不纠结",
        "为什么你的{topic}总是不对？原因在这",
        "{topic}真的有用吗？亲测告诉你",
        "还在纠结{topic}？这篇帮你理清思路",
        "{topic}踩过的坑，希望你别再踩了",
    ],
    "情感型": [
        "后悔没早知道的{topic}经验",
        "被{topic}惊艳到了！必须分享给你们",
        "这个{topic}方法太绝了！强烈推荐",
        "真心推荐！{topic}的宝藏经验",
        "终于找到最适合的{topic}方法了",
    ],
}

# 内容模板（按笔记类型）
CONTENT_TEMPLATES = {
    "图文": {
        "structure": [
            "【开头钩子】用 1-2 句话抓住读者注意力",
            "【核心内容】分 3-5 个要点展开",
            "【总结互动】总结要点 + 引导互动提问",
        ],
        "template": (
            "{hook}\n\n"
            "{point_1}\n\n"
            "{point_2}\n\n"
            "{point_3}\n\n"
            "{closing}"
        ),
        "hooks": [
            "姐妹们！这个{topic}真的太好用了，忍不住分享给你们～",
            "关于{topic}，我研究了很久终于找到最优解！",
            "分享一个让我受益匪浅的{topic}经验，建议收藏！",
        ],
        "closings": [
            "以上就是我关于{topic}的分享啦～觉得有用的话记得点赞收藏哦！你们有什么好的建议也欢迎在评论区告诉我～",
            "希望这篇{topic}分享对你有帮助！还有什么想了解的，评论区见～",
            "关于{topic}就分享到这里啦！如果你也有好的经验，欢迎在评论区交流！",
        ],
    },
    "视频": {
        "structure": [
            "【开头 3 秒】用悬念或痛点抓住注意力",
            "【主体内容】清晰的步骤或故事线",
            "【结尾 CTA】引导点赞关注收藏",
        ],
        "template": (
            "{hook}\n\n"
            "今天分享关于{topic}的内容：\n\n"
            "1. {point_1}\n"
            "2. {point_2}\n"
            "3. {point_3}\n\n"
            "{closing}"
        ),
        "hooks": [
            "等等！关于{topic}，这个你一定不知道👇",
            "1 分钟教你搞定{topic}！",
            "关于{topic}，千万别踩这些坑！",
        ],
        "closings": [
            "觉得有用就点个赞吧～关注我获取更多{topic}干货！",
            "喜欢的话记得三连支持一下！还有什么想看的内容评论区告诉我～",
        ],
    },
    "长文": {
        "structure": [
            "【引言】背景介绍 + 阅读价值",
            "【正文】分章节深入展开（3-5 节）",
            "【结语】总结 + 互动引导",
        ],
        "template": (
            "# {title}\n\n"
            "## 前言\n{hook}\n\n"
            "## 一、{section_1_title}\n{section_1}\n\n"
            "## 二、{section_2_title}\n{section_2}\n\n"
            "## 三、{section_3_title}\n{section_3}\n\n"
            "## 总结\n{closing}"
        ),
        "hooks": [
            "这篇文章是我关于{topic}的深度分享，希望能给正在了解这方面内容的你一些帮助。",
            "最近研究{topic}有了一些心得，整理成这篇长文分享给大家。",
        ],
        "closings": [
            "以上就是关于{topic}的全部内容了。如果这篇文章对你有帮助，别忘了点赞收藏，方便以后查看～",
            "关于{topic}的分享就到这里。欢迎在评论区留下你的想法，一起讨论！",
        ],
    },
}

# 标签数据库（按主题分类）
TAG_DATABASE = {
    "旅行": ["旅行攻略", "旅行日记", "小众旅行地", "自由行", "旅行穿搭", "打卡", "周末去哪玩", "城市漫步"],
    "美食": ["美食分享", "食谱", "探店", "家常菜", "烘焙", "减脂餐", "下午茶", "美食推荐"],
    "穿搭": ["穿搭分享", "日常穿搭", "通勤穿搭", "OOTD", "搭配灵感", "显瘦穿搭", "氛围感穿搭", "季节穿搭"],
    "护肤": ["护肤心得", "成分党", "敏感肌", "防晒", "抗老", "平价好物", "护肤步骤", "肌肤管理"],
    "数码": ["数码好物", "科技分享", "App推荐", "效率工具", "电子产品", "测评", "手机摄影", "数码生活"],
    "学习": ["学习方法", "自律打卡", "考试经验", "读书笔记", "成长记录", "知识分享", "高效学习", "自我提升"],
    "职场": ["职场经验", "面试技巧", "副业", "自由职业", "职场干货", "升职加薪", "跳槽经验", "行业分析"],
    "生活": ["生活记录", "居家好物", "收纳整理", "极简生活", "生活方式", "日常vlog", "独居生活", "幸福感"],
    "健身": ["健身打卡", "减脂", "增肌", "瑜伽", "跑步", "健身食谱", "居家健身", "健身入门"],
    "母婴": ["育儿经验", "母婴好物", "辅食食谱", "新手妈妈", "亲子活动", "孕期记录", "儿童教育", "宝宝日常"],
}

# 通用标签（适用于所有主题）
UNIVERSAL_TAGS = ["干货分享", "经验分享", "好物推荐", "日常", "记录生活", "涨知识"]

# 校验常量
MAX_TITLE_LENGTH = 20
MAX_CONTENT_LENGTH = 1000
MAX_LONGFORM_LENGTH = 10000
MAX_TAGS = 10


class TemplateEngine:
    """写作模板引擎"""

    @staticmethod
    def generate_title(topic: str, style: Optional[str] = None, count: int = 5) -> List[str]:
        """
        生成标题建议

        Args:
            topic: 主题关键词
            style: 标题风格（数字型/疑问型/情感型），None 则混合
            count: 生成数量

        Returns:
            标题建议列表
        """
        titles = []

        if style and style in TITLE_HOOKS:
            templates = TITLE_HOOKS[style]
        else:
            # 混合所有风格
            templates = []
            for hooks in TITLE_HOOKS.values():
                templates.extend(hooks)

        # 随机选取并填充
        selected = random.sample(templates, min(count, len(templates)))
        for t in selected:
            title = t.format(
                topic=topic,
                count=random.choice([3, 5, 6, 7, 8, 10]),
                n=random.choice([1, 2, 3]),
            )
            # 截断到 MAX_TITLE_LENGTH
            if len(title) > MAX_TITLE_LENGTH:
                title = title[:MAX_TITLE_LENGTH]
            titles.append(title)

        return titles

    @staticmethod
    def generate_content(topic: str, note_type: str = "图文") -> Dict[str, Any]:
        """
        生成结构化内容模板

        Args:
            topic: 主题关键词
            note_type: 笔记类型（图文/视频/长文）

        Returns:
            包含 structure、template、hook、closing 的字典
        """
        tmpl = CONTENT_TEMPLATES.get(note_type, CONTENT_TEMPLATES["图文"])

        hook = random.choice(tmpl["hooks"]).format(topic=topic)
        closing = random.choice(tmpl["closings"]).format(topic=topic)

        return {
            "note_type": note_type,
            "topic": topic,
            "structure": tmpl["structure"],
            "hook": hook,
            "closing": closing,
            "template": tmpl["template"],
            "placeholders": {
                "hook": hook,
                "closing": closing,
                "topic": topic,
            },
        }

    @staticmethod
    def suggest_tags(topic: str, count: int = 6) -> List[str]:
        """
        推荐话题标签

        Args:
            topic: 主题关键词
            count: 推荐数量（5-8）

        Returns:
            标签建议列表
        """
        count = max(3, min(count, 10))
        tags = []

        # 从主题分类中匹配
        for category, category_tags in TAG_DATABASE.items():
            if category in topic or topic in category:
                tags.extend(category_tags)

        # 如果没找到精确匹配，从所有分类中采样
        if not tags:
            all_tags = []
            for category_tags in TAG_DATABASE.values():
                all_tags.extend(category_tags)
            tags = random.sample(all_tags, min(count, len(all_tags)))

        # 加入通用标签
        tags.extend(UNIVERSAL_TAGS)

        # 去重并截取
        seen = set()
        unique_tags = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique_tags.append(t)

        return unique_tags[:count]

    @staticmethod
    def validate(title: str, content: str, tags: Optional[List[str]] = None,
                 note_type: str = "图文") -> Dict[str, Any]:
        """
        校验标题、正文、标签

        Returns:
            {"valid": bool, "errors": [...], "warnings": [...]}
        """
        errors = []
        warnings = []

        # 标题校验
        if not title or not title.strip():
            errors.append("标题不能为空")
        elif len(title) > MAX_TITLE_LENGTH:
            errors.append(f"标题超长（{len(title)}/{MAX_TITLE_LENGTH} 字）")

        # 正文校验
        max_len = MAX_LONGFORM_LENGTH if note_type == "长文" else MAX_CONTENT_LENGTH
        if not content or not content.strip():
            errors.append("正文不能为空")
        elif len(content) > max_len:
            errors.append(f"正文超长（{len(content)}/{max_len} 字）")
        elif len(content) < 10:
            warnings.append("正文过短，建议至少 10 字")

        # 标签校验
        if tags:
            if len(tags) > MAX_TAGS:
                warnings.append(f"标签过多（{len(tags)}/{MAX_TAGS}），多余的将被截断")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }


# ============================================================
# 便捷函数
# ============================================================

def generate_template(topic: str, note_type: str = "图文") -> Dict[str, Any]:
    """
    一键生成完整写作模板

    Args:
        topic: 主题关键词
        note_type: 笔记类型（图文/视频/长文）

    Returns:
        包含 titles、content、tags 的完整模板
    """
    engine = TemplateEngine()
    return {
        "topic": topic,
        "note_type": note_type,
        "titles": engine.generate_title(topic),
        "content": engine.generate_content(topic, note_type),
        "tags": engine.suggest_tags(topic),
    }
