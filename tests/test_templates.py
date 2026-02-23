"""
写作模板模块单元测试
"""

import pytest

from scripts.templates import (
    TemplateEngine, generate_template,
    TITLE_HOOKS, CONTENT_TEMPLATES, TAG_DATABASE,
    MAX_TITLE_LENGTH, MAX_CONTENT_LENGTH, MAX_LONGFORM_LENGTH, MAX_TAGS,
)


class TestGenerateTitle:
    """测试标题生成"""

    def test_default_count(self):
        """默认生成 5 个标题"""
        titles = TemplateEngine.generate_title("旅行")
        assert len(titles) == 5

    def test_custom_count(self):
        """自定义数量"""
        titles = TemplateEngine.generate_title("美食", count=3)
        assert len(titles) == 3

    def test_specific_style(self):
        """指定风格"""
        titles = TemplateEngine.generate_title("护肤", style="数字型")
        assert len(titles) > 0
        for t in titles:
            assert len(t) <= MAX_TITLE_LENGTH

    def test_mixed_style(self):
        """混合风格（style=None）"""
        titles = TemplateEngine.generate_title("学习", style=None)
        assert len(titles) > 0

    def test_invalid_style_fallback(self):
        """无效风格回退到混合"""
        titles = TemplateEngine.generate_title("测试", style="不存在的风格")
        assert len(titles) > 0

    def test_title_max_length(self):
        """标题不超过最大长度"""
        titles = TemplateEngine.generate_title("非常非常长的主题关键词测试")
        for t in titles:
            assert len(t) <= MAX_TITLE_LENGTH

    def test_topic_in_title(self):
        """主题关键词出现在标题中"""
        titles = TemplateEngine.generate_title("咖啡")
        # 至少有一个标题包含主题
        assert any("咖啡" in t for t in titles)


class TestGenerateContent:
    """测试内容模板生成"""

    def test_image_type(self):
        """图文模板"""
        result = TemplateEngine.generate_content("旅行", "图文")
        assert result["note_type"] == "图文"
        assert "hook" in result
        assert "closing" in result
        assert "structure" in result
        assert len(result["structure"]) > 0

    def test_video_type(self):
        """视频模板"""
        result = TemplateEngine.generate_content("美食", "视频")
        assert result["note_type"] == "视频"

    def test_longform_type(self):
        """长文模板"""
        result = TemplateEngine.generate_content("学习", "长文")
        assert result["note_type"] == "长文"

    def test_unknown_type_fallback(self):
        """未知类型回退到图文"""
        result = TemplateEngine.generate_content("测试", "未知类型")
        assert "hook" in result

    def test_topic_in_content(self):
        """主题出现在 hook 或 closing 中"""
        result = TemplateEngine.generate_content("咖啡", "图文")
        assert "咖啡" in result["hook"] or "咖啡" in result["closing"]


class TestSuggestTags:
    """测试标签推荐"""

    def test_default_count(self):
        """默认返回 6 个标签"""
        tags = TemplateEngine.suggest_tags("旅行")
        assert len(tags) == 6

    def test_custom_count(self):
        """自定义数量"""
        tags = TemplateEngine.suggest_tags("美食", count=4)
        assert len(tags) == 4

    def test_count_clamped(self):
        """数量被限制在 3-10"""
        tags = TemplateEngine.suggest_tags("测试", count=1)
        assert len(tags) >= 3

    def test_known_topic_tags(self):
        """已知主题返回相关标签"""
        tags = TemplateEngine.suggest_tags("旅行", count=8)
        # 应该包含旅行相关标签
        assert any("旅行" in t for t in tags)

    def test_unknown_topic_tags(self):
        """未知主题也能返回标签"""
        tags = TemplateEngine.suggest_tags("量子力学", count=5)
        assert len(tags) == 5

    def test_no_duplicates(self):
        """无重复标签"""
        tags = TemplateEngine.suggest_tags("旅行", count=10)
        assert len(tags) == len(set(tags))


class TestValidate:
    """测试内容校验"""

    def test_valid_content(self):
        """正常内容通过校验"""
        result = TemplateEngine.validate("测试标题", "这是一段正文内容，足够长了")
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_empty_title(self):
        """空标题不通过"""
        result = TemplateEngine.validate("", "正文内容")
        assert result["valid"] is False
        assert any("标题" in e for e in result["errors"])

    def test_long_title(self):
        """超长标题不通过"""
        result = TemplateEngine.validate("测" * 30, "正文内容")
        assert result["valid"] is False
        assert any("超长" in e for e in result["errors"])

    def test_empty_content(self):
        """空正文不通过"""
        result = TemplateEngine.validate("标题", "")
        assert result["valid"] is False
        assert any("正文" in e for e in result["errors"])

    def test_short_content_warning(self):
        """过短正文有警告"""
        result = TemplateEngine.validate("标题", "短")
        assert len(result["warnings"]) > 0

    def test_long_content(self):
        """超长正文不通过"""
        result = TemplateEngine.validate("标题", "测" * (MAX_CONTENT_LENGTH + 1))
        assert result["valid"] is False

    def test_longform_content_limit(self):
        """长文类型有更高的正文上限"""
        long_text = "测" * (MAX_CONTENT_LENGTH + 1)
        result = TemplateEngine.validate("标题", long_text, note_type="长文")
        assert result["valid"] is True  # 长文上限更高

    def test_too_many_tags_warning(self):
        """标签过多有警告"""
        tags = [f"tag{i}" for i in range(15)]
        result = TemplateEngine.validate("标题", "正文内容足够长", tags)
        assert any("标签" in w for w in result["warnings"])


class TestGenerateTemplate:
    """测试一键生成模板"""

    def test_basic(self):
        """基本调用"""
        result = generate_template("旅行攻略")
        assert result["topic"] == "旅行攻略"
        assert result["note_type"] == "图文"
        assert "titles" in result
        assert "content" in result
        assert "tags" in result

    def test_video_type(self):
        """视频类型"""
        result = generate_template("美食探店", "视频")
        assert result["note_type"] == "视频"

    def test_longform_type(self):
        """长文类型"""
        result = generate_template("深度分析", "长文")
        assert result["note_type"] == "长文"
