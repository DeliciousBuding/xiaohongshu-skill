"""
发布模块单元测试
"""

from unittest.mock import MagicMock, patch

import pytest

from scripts.client import XiaohongshuClient
from scripts.publish import (
    PUBLISH_STATUS_CONFIRMED,
    PUBLISH_STATUS_FAILED,
    PUBLISH_STATUS_SUBMITTED_UNCONFIRMED,
    PUBLISH_URL,
    PublishAction,
    PublishConfirmation,
    PublishValidation,
)


class TestNavigateToPublish:
    """测试导航到发布页"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_navigate_calls_correct_url(self):
        """导航到创作者中心发布页"""
        self.action._navigate_to_publish()
        self.client.navigate.assert_called_once_with(
            "https://creator.xiaohongshu.com/publish/publish?source=official"
        )


class TestClickPublishTab:
    """测试切换发布类型 TAB"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_click_image_tab(self):
        """切换到上传图文"""
        mock_tab = MagicMock()
        mock_tab.count.return_value = 1
        mock_tab.text_content.return_value = "上传图文"
        mock_tab.evaluate.return_value = False  # is_element_blocked 返回 False
        mock_tabs = MagicMock()
        mock_tabs.count.return_value = 1
        mock_tabs.nth.return_value = mock_tab
        self.client.page.locator.return_value = mock_tabs
        self.client.page.wait_for_selector.return_value = True

        self.action._click_publish_tab("上传图文")
        mock_tab.click.assert_called_once()

    def test_click_video_tab(self):
        """切换到上传视频"""
        mock_tab = MagicMock()
        mock_tab.count.return_value = 1
        mock_tab.text_content.return_value = "上传视频"
        mock_tab.evaluate.return_value = False  # is_element_blocked 返回 False
        mock_tabs = MagicMock()
        mock_tabs.count.return_value = 1
        mock_tabs.nth.return_value = mock_tab
        self.client.page.locator.return_value = mock_tabs
        self.client.page.wait_for_selector.return_value = True

        self.action._click_publish_tab("上传视频")
        mock_tab.click.assert_called_once()


class TestFillTitle:
    """测试填写标题"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_fill_title(self):
        """填写标题"""
        mock_input = MagicMock()
        mock_input.first = MagicMock()
        self.client.page.locator.return_value = mock_input

        # mock max_suffix 不可见
        mock_suffix = MagicMock()
        mock_suffix.count.return_value = 0
        self.client.page.locator.side_effect = [mock_input, mock_suffix]

        self.action._fill_title("测试标题")
        mock_input.first.fill.assert_called_once_with("测试标题")


class TestFillContent:
    """测试填写正文"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.client.page.keyboard = MagicMock()
        self.action = PublishAction(self.client)

    def test_fill_content_quill_editor(self):
        """通过 Quill 编辑器填写正文"""
        mock_ql = MagicMock()
        mock_ql.count.return_value = 1
        mock_ql.first = MagicMock()

        mock_length_error = MagicMock()
        mock_length_error.count.return_value = 0

        self.client.page.locator.side_effect = [mock_ql, mock_length_error]

        self.action._fill_content("测试正文内容")
        mock_ql.first.click.assert_called_once()
        # delay 已改为 random.randint(20, 60)，只验证内容和 delay 范围
        call_args = self.client.page.keyboard.type.call_args
        assert call_args[0][0] == "测试正文内容"
        assert 20 <= call_args[1]["delay"] <= 60


class TestInputTags:
    """测试输入话题标签"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.client.page.keyboard = MagicMock()
        self.action = PublishAction(self.client)

    def test_empty_tags(self):
        """空标签列表不操作"""
        self.action._input_tags([])
        self.client.page.keyboard.type.assert_not_called()

    def test_max_10_tags(self):
        """最多 10 个标签"""
        mock_ql = MagicMock()
        mock_ql.count.return_value = 1
        mock_ql.first = MagicMock()

        mock_topic = MagicMock()
        mock_topic.count.return_value = 0

        self.client.page.locator.side_effect = [mock_ql] + [mock_topic] * 20

        tags = [f"tag{i}" for i in range(15)]
        self.action._input_tags(tags)
        # # 被输入了（每个标签输入 # + 标签文字 + 可能的空格）
        # 验证只处理了 10 个标签（tags[:10]）
        type_calls = self.client.page.keyboard.type.call_args_list
        hash_calls = [c for c in type_calls if c[0][0] == '#']
        assert len(hash_calls) == 10

    def test_strip_hash_prefix(self):
        """自动去除 # 前缀"""
        mock_ql = MagicMock()
        mock_ql.count.return_value = 1
        mock_ql.first = MagicMock()

        mock_topic = MagicMock()
        mock_topic.count.return_value = 0

        self.client.page.locator.side_effect = [mock_ql, mock_topic]

        self.action._input_tags(["#测试标签"])
        type_calls = self.client.page.keyboard.type.call_args_list
        # 应该输入 #, 测试标签, 空格 —— 标签本身不含 #
        tag_calls = [c for c in type_calls if c[0][0] == '测试标签']
        assert len(tag_calls) == 1


class TestCheckPublishReady:
    """测试发布前校验"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_ready_with_title_and_button(self):
        """标题和按钮都就绪"""
        mock_title = MagicMock()
        mock_title.count.return_value = 1
        mock_title.input_value.return_value = "测试标题"

        mock_btn = MagicMock()
        mock_btn.count.return_value = 1
        mock_btn.is_visible.return_value = True

        self.client.page.locator.side_effect = [mock_title, mock_btn]

        status = self.action._check_publish_ready()
        assert status["title"] == "测试标题"
        assert status["title_ok"] is True
        assert status["publish_button_visible"] is True

    def test_not_ready_no_title(self):
        """无标题"""
        mock_title = MagicMock()
        mock_title.count.return_value = 0

        mock_btn = MagicMock()
        mock_btn.count.return_value = 1
        mock_btn.is_visible.return_value = True

        self.client.page.locator.side_effect = [mock_title, mock_btn]

        status = self.action._check_publish_ready()
        assert status["title_ok"] is False


class TestPublishImage:
    """测试发布图文笔记"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)
        self.validation_patcher = patch(
            "scripts.publish.validate_publish_request",
            return_value=PublishValidation(schedule_at=None, warnings=()),
        )
        self.mock_validate = self.validation_patcher.start()

    def teardown_method(self):
        self.validation_patcher.stop()

    @patch.object(PublishAction, '_navigate_to_publish')
    @patch.object(PublishAction, '_click_publish_tab')
    @patch.object(PublishAction, '_upload_images')
    @patch.object(PublishAction, '_fill_title')
    @patch.object(PublishAction, '_fill_content')
    @patch.object(PublishAction, '_check_publish_ready')
    def test_publish_image_no_auto(self, mock_ready, mock_content, mock_title,
                                    mock_upload, mock_tab, mock_nav):
        """图文发布（不自动发布）"""
        mock_ready.return_value = {"title": "测试", "title_ok": True, "publish_button_visible": True}

        result = self.action.publish_image(
            title="测试标题",
            content="正文",
            image_paths=["img1.jpg", "img2.jpg"],
            auto_publish=False,
        )
        assert result["status"] == "ready"
        assert result["published"] is False
        assert result["image_count"] == 2
        mock_nav.assert_called_once()
        mock_tab.assert_called_once_with("上传图文")
        mock_upload.assert_called_once_with(["img1.jpg", "img2.jpg"])

    @patch.object(PublishAction, '_navigate_to_publish')
    @patch.object(PublishAction, '_click_publish_tab')
    @patch.object(PublishAction, '_upload_images')
    @patch.object(PublishAction, '_fill_title')
    @patch.object(PublishAction, '_fill_content')
    @patch.object(PublishAction, '_check_publish_ready')
    @patch.object(
        PublishAction,
        '_publish_and_confirm',
        return_value=PublishConfirmation(
            status=PUBLISH_STATUS_CONFIRMED,
            message='已确认',
            signal='success_feedback',
        ),
    )
    def test_publish_image_auto(self, mock_confirm, mock_ready, mock_content,
                                 mock_title, mock_upload, mock_tab, mock_nav):
        """图文发布（自动发布成功）"""
        mock_ready.return_value = {"title": "测试", "title_ok": True}

        result = self.action.publish_image(
            title="测试",
            content="正文",
            image_paths=["img.jpg"],
            auto_publish=True,
        )
        assert result["status"] == PUBLISH_STATUS_CONFIRMED
        assert result["published"] is True
        assert result["success"] is True
        mock_confirm.assert_called_once()

    @patch.object(PublishAction, '_navigate_to_publish')
    @patch.object(PublishAction, '_click_publish_tab')
    @patch.object(PublishAction, '_upload_images')
    @patch.object(PublishAction, '_fill_title')
    @patch.object(PublishAction, '_fill_content')
    @patch.object(PublishAction, '_input_tags')
    @patch.object(PublishAction, '_check_publish_ready')
    def test_publish_image_with_tags(self, mock_ready, mock_tags, mock_content,
                                      mock_title, mock_upload, mock_tab, mock_nav):
        """图文发布带标签"""
        mock_ready.return_value = {"title": "测试", "title_ok": True}

        self.action.publish_image(
            title="测试",
            content="正文",
            image_paths=["img.jpg"],
            tags=["旅行", "美食"],
        )
        mock_tags.assert_called_once_with(["旅行", "美食"])


class TestPublishVideo:
    """测试发布视频笔记"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)
        self.validation_patcher = patch(
            "scripts.publish.validate_publish_request",
            return_value=PublishValidation(schedule_at=None, warnings=()),
        )
        self.mock_validate = self.validation_patcher.start()

    def teardown_method(self):
        self.validation_patcher.stop()

    @patch.object(PublishAction, '_navigate_to_publish')
    @patch.object(PublishAction, '_click_publish_tab')
    @patch.object(PublishAction, '_upload_video')
    @patch.object(PublishAction, '_fill_title')
    @patch.object(PublishAction, '_fill_content')
    @patch.object(PublishAction, '_check_publish_ready')
    def test_publish_video_no_auto(self, mock_ready, mock_content, mock_title,
                                    mock_upload, mock_tab, mock_nav):
        """视频发布（不自动发布）"""
        mock_ready.return_value = {"title": "视频", "title_ok": True}

        result = self.action.publish_video(
            title="视频标题",
            content="视频描述",
            video_path="video.mp4",
            auto_publish=False,
        )
        assert result["status"] == "ready"
        assert result["published"] is False
        assert result["video_path"] == "video.mp4"
        mock_tab.assert_called_once_with("上传视频")

    @patch.object(PublishAction, '_navigate_to_publish')
    @patch.object(PublishAction, '_click_publish_tab')
    @patch.object(PublishAction, '_upload_video')
    @patch.object(PublishAction, '_fill_title')
    @patch.object(PublishAction, '_fill_content')
    @patch.object(PublishAction, '_check_publish_ready')
    @patch.object(
        PublishAction,
        '_publish_and_confirm',
        return_value=PublishConfirmation(
            status=PUBLISH_STATUS_FAILED,
            message='点击失败',
            signal='click_failed',
        ),
    )
    def test_publish_video_auto_fail(self, mock_confirm, mock_ready, mock_content,
                                      mock_title, mock_upload, mock_tab, mock_nav):
        """视频发布（自动发布失败）"""
        mock_ready.return_value = {"title": "视频", "title_ok": True}

        result = self.action.publish_video(
            title="视频",
            content="描述",
            video_path="video.mp4",
            auto_publish=True,
        )
        assert result["status"] == PUBLISH_STATUS_FAILED
        assert result["published"] is False
        assert result["success"] is False
        mock_confirm.assert_called_once()


class TestClickPublishButton:
    """测试点击发布按钮"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_button_found_and_clicked(self):
        """找到发布按钮并点击"""
        mock_btn = MagicMock()
        mock_btn.count.return_value = 1
        mock_btn.first = MagicMock()

        # xhs-publish-btn 不存在（count=0），回退到旧版按钮
        mock_empty = MagicMock()
        mock_empty.count.return_value = 0

        self.client.page.locator = MagicMock()
        self.client.page.locator.side_effect = lambda sel: mock_empty if "xhs-publish-btn" in sel else mock_btn

        result = self.action._click_publish_button()
        assert result is True
        mock_btn.first.click.assert_called_once()

    def test_button_not_found(self):
        """未找到发布按钮"""
        mock_btn = MagicMock()
        mock_btn.count.return_value = 0
        self.client.page.locator.return_value = mock_btn

        result = self.action._click_publish_button()
        assert result is False


class TestPublishConfirmation:
    """测试发布按钮点击后的可信状态判定。"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.client.page.url = PUBLISH_URL
        feedback = MagicMock()
        feedback.count.return_value = 0
        self.client.page.get_by_text.return_value = feedback
        self.action = PublishAction(self.client)

    @staticmethod
    def _fake_clock():
        current = [0.0]

        def monotonic():
            return current[0]

        def sleep(seconds):
            current[0] += seconds

        return monotonic, sleep

    @patch.object(PublishAction, '_click_publish_button', return_value=True)
    def test_click_without_confirmation_is_not_success(self, mock_click):
        """点击成功但无确认信号时必须返回未确认且 success=false。"""
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._publish_and_confirm(
            timeout=1.0,
            poll_interval=0.5,
            monotonic=monotonic,
            sleep=sleep,
        )
        result = self.action._confirmation_fields(confirmation)

        assert result["status"] == PUBLISH_STATUS_SUBMITTED_UNCONFIRMED
        assert result["success"] is False
        assert result["published"] is False
        assert result["confirmation_signal"] == "confirmation_timeout"
        mock_click.assert_called_once()

    @patch.object(PublishAction, '_click_publish_button', return_value=False)
    def test_click_failure_is_failed(self, mock_click):
        confirmation = self.action._publish_and_confirm()

        assert confirmation.status == PUBLISH_STATUS_FAILED
        assert confirmation.success is False
        assert confirmation.signal == "click_failed"
        mock_click.assert_called_once()

    def test_success_feedback_confirms_publish(self):
        feedback = MagicMock()
        feedback.count.return_value = 1
        feedback.nth.return_value.is_visible.return_value = True
        self.client.page.get_by_text.return_value = feedback
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_CONFIRMED
        assert confirmation.signal == "success_feedback"
        assert confirmation.success is True

    def test_url_leaving_publish_flow_confirms_publish(self):
        self.client.page.url = "https://creator.xiaohongshu.com/creator/home"
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_CONFIRMED
        assert confirmation.signal == "url_left_publish_flow"

    @pytest.mark.parametrize(
        ("url", "signal"),
        [
            ("https://creator.xiaohongshu.com/login", "login_redirect"),
            ("https://www.xiaohongshu.com/website-login/captcha", "captcha_redirect"),
        ],
    )
    def test_auth_redirect_is_failed_before_url_confirmation(self, url, signal):
        self.client.page.url = url
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_FAILED
        assert confirmation.signal == signal
        assert confirmation.success is False

    @patch.object(PublishAction, '_click_publish_button', return_value=True)
    def test_stale_success_feedback_is_not_new_confirmation(self, mock_click):
        feedback = MagicMock()
        feedback.count.return_value = 1
        feedback.nth.return_value.is_visible.return_value = True
        self.client.page.get_by_text.return_value = feedback
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._publish_and_confirm(
            timeout=1.0,
            poll_interval=0.5,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_SUBMITTED_UNCONFIRMED
        mock_click.assert_called_once()

    def test_same_url_security_challenge_is_failed(self):
        self.client._check_captcha.return_value = True
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_FAILED
        assert confirmation.signal == "captcha_detected"

    @pytest.mark.parametrize(
        "url",
        [
            "https://example.com/success",
            "https://creator.xiaohongshu.com/error",
            "https://creator.xiaohongshu.com/404",
        ],
    )
    def test_untrusted_or_error_destination_is_not_confirmation(self, url):
        self.client.page.url = url
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            poll_interval=0.5,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_SUBMITTED_UNCONFIRMED

    def test_publish_query_change_is_not_confirmation(self):
        self.client.page.url = f"{PUBLISH_URL}&draft=1"
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            poll_interval=0.5,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_SUBMITTED_UNCONFIRMED

    def test_non_http_intermediate_page_is_not_confirmation(self):
        self.client.page.url = "about:blank"
        monotonic, sleep = self._fake_clock()

        confirmation = self.action._wait_for_publish_confirmation(
            initial_url=PUBLISH_URL,
            timeout=1.0,
            poll_interval=0.5,
            monotonic=monotonic,
            sleep=sleep,
        )

        assert confirmation.status == PUBLISH_STATUS_SUBMITTED_UNCONFIRMED


class TestPublishLongform:
    """测试长文入口也使用统一校验和发布确认。"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        empty = MagicMock()
        empty.count.return_value = 0
        self.client.page.get_by_text.return_value = empty
        self.client.page.locator.return_value = empty
        self.action = PublishAction(self.client)

    @patch("scripts.publish.validate_publish_request")
    @patch.object(PublishAction, '_navigate_to_publish')
    @patch.object(
        PublishAction,
        '_publish_and_confirm',
        return_value=PublishConfirmation(
            status=PUBLISH_STATUS_SUBMITTED_UNCONFIRMED,
            message='待人工复核',
            signal='confirmation_timeout',
        ),
    )
    def test_longform_auto_uses_common_confirmation(
        self,
        mock_confirm,
        mock_nav,
        mock_validate,
    ):
        mock_validate.return_value = PublishValidation(schedule_at=None, warnings=())

        result = self.action.publish_longform(
            title="长文标题",
            content="长文正文",
            auto_publish=True,
        )

        assert result["status"] == PUBLISH_STATUS_SUBMITTED_UNCONFIRMED
        assert result["success"] is False
        assert result["published"] is False
        mock_validate.assert_called_once_with(title="长文标题")
        mock_confirm.assert_called_once()


class TestUploadImages:
    """测试图片上传"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_no_valid_paths(self):
        """无有效图片路径抛出异常"""
        with pytest.raises(ValueError, match="没有有效的图片文件"):
            self.action._upload_images(["nonexistent1.jpg", "nonexistent2.jpg"])

    @patch('os.path.exists', return_value=True)
    @patch('os.path.abspath', side_effect=lambda x: f"/abs/{x}")
    def test_upload_single_image(self, mock_abs, mock_exists):
        """上传单张图片"""
        mock_upload = MagicMock()
        mock_previews = MagicMock()
        mock_previews.count.return_value = 1
        self.client.page.locator.side_effect = [mock_upload, mock_previews]

        self.action._upload_images(["test.jpg"])
        mock_upload.set_input_files.assert_called_once_with("/abs/test.jpg")


class TestUploadVideo:
    """测试视频上传"""

    def setup_method(self):
        self.client = MagicMock(spec=XiaohongshuClient)
        self.client.page = MagicMock()
        self.action = PublishAction(self.client)

    def test_video_not_exists(self):
        """视频文件不存在抛出异常"""
        with pytest.raises(ValueError, match="视频文件不存在"):
            self.action._upload_video("nonexistent.mp4")
