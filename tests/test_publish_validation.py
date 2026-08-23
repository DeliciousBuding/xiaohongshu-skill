"""发布领域参数校验测试。"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.client import XiaohongshuClient
from scripts.publish import (
    MAX_SCHEDULE_DELAY,
    MIN_SCHEDULE_DELAY,
    PUBLISH_TIMEZONE,
    PublishAction,
    publish_markdown,
    validate_media_paths,
    validate_publish_request,
    validate_schedule_time,
)


class TestScheduleValidation:
    """定时发布格式、时区和范围校验。"""

    def setup_method(self):
        self.now = datetime(2026, 8, 23, 12, 34, 45, tzinfo=PUBLISH_TIMEZONE)

    def test_none_means_immediate_publish(self):
        assert validate_schedule_time(None, now=self.now) is None

    def test_exactly_one_hour_is_allowed(self):
        now = self.now.replace(second=0, microsecond=0)
        schedule = "2026-08-23 13:34"

        parsed = validate_schedule_time(schedule, now=now)

        assert parsed == datetime(2026, 8, 23, 13, 34, tzinfo=PUBLISH_TIMEZONE)
        assert parsed - now == MIN_SCHEDULE_DELAY

    def test_schedule_less_than_one_real_hour_is_rejected(self):
        with pytest.raises(ValueError, match="1 小时至 14 天"):
            validate_schedule_time("2026-08-23 13:34", now=self.now)

    def test_next_minute_after_one_hour_is_allowed(self):
        parsed = validate_schedule_time("2026-08-23 13:35", now=self.now)

        assert parsed - self.now > MIN_SCHEDULE_DELAY

    def test_exactly_fourteen_days_is_allowed(self):
        now = self.now.replace(second=0, microsecond=0)
        schedule = "2026-09-06 12:34"

        parsed = validate_schedule_time(schedule, now=now)

        assert parsed - now == MAX_SCHEDULE_DELAY

    @pytest.mark.parametrize(
        "schedule",
        [
            "2026-08-23",
            "2026/08/23 14:00",
            "2026-08-23 14:00:00",
            "2026-02-30 14:00",
            "2026-8-23 14:00",
            "2026-08-23 4:05",
            "",
        ],
    )
    def test_invalid_format_is_rejected(self, schedule):
        with pytest.raises(ValueError, match="格式"):
            validate_schedule_time(schedule, now=self.now)

    @pytest.mark.parametrize(
        "delta",
        [
            timedelta(minutes=59),
            timedelta(days=14, minutes=1),
        ],
    )
    def test_out_of_range_schedule_is_rejected(self, delta):
        schedule_at = self.now.replace(second=0, microsecond=0) + delta

        with pytest.raises(ValueError, match="1 小时至 14 天"):
            validate_schedule_time(schedule_at.strftime("%Y-%m-%d %H:%M"), now=self.now)

    def test_aware_now_is_converted_to_asia_shanghai(self):
        utc_now = datetime(2026, 8, 23, 4, 0, tzinfo=timezone.utc)

        parsed = validate_schedule_time("2026-08-23 13:00", now=utc_now)

        assert parsed == datetime(2026, 8, 23, 13, 0, tzinfo=PUBLISH_TIMEZONE)


class TestMediaValidation:
    """媒体必须在浏览器导航前通过本地可读性检查。"""

    def test_readable_files_are_accepted(self, tmp_path):
        first = tmp_path / "first.jpg"
        second = tmp_path / "second.jpg"
        first.write_bytes(b"image-one")
        second.write_bytes(b"image-two")

        validated = validate_media_paths([str(first), str(second)])

        assert validated == (str(first), str(second))

    def test_empty_media_list_is_rejected(self):
        with pytest.raises(ValueError, match="至少需要一个"):
            validate_media_paths([])

    def test_missing_file_is_rejected(self, tmp_path):
        missing = tmp_path / "missing.jpg"

        with pytest.raises(ValueError, match="不存在"):
            validate_media_paths([str(missing)])

    def test_directory_is_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="不是普通文件"):
            validate_media_paths([str(tmp_path)])

    def test_unreadable_file_is_rejected(self):
        with (
            patch.object(Path, "is_file", return_value=True),
            patch.object(Path, "open", side_effect=PermissionError("denied")),
        ):
            with pytest.raises(ValueError, match="不可读"):
                validate_media_paths(["locked.jpg"])

    def test_mixed_valid_and_invalid_files_are_rejected(self, tmp_path):
        valid = tmp_path / "valid.jpg"
        valid.write_bytes(b"image")

        with pytest.raises(ValueError, match="missing.jpg"):
            validate_media_paths([str(valid), str(tmp_path / "missing.jpg")])


class TestPublishRequestValidation:
    """统一请求校验供图文、视频、长文和 CLI 复用。"""

    def test_blank_title_is_hard_failure(self):
        with pytest.raises(ValueError, match="标题不能为空"):
            validate_publish_request(title="   ")

    def test_title_at_recommended_limit_has_no_warning(self):
        validation = validate_publish_request(title="题" * 20)

        assert validation.warnings == ()

    def test_long_title_returns_warning_without_blocking(self):
        validation = validate_publish_request(title="题" * 21)

        assert len(validation.warnings) == 1
        assert "超过当前建议" in validation.warnings[0]

    def test_invalid_image_request_does_not_navigate(self, tmp_path):
        client = MagicMock(spec=XiaohongshuClient)
        client.page = MagicMock()
        action = PublishAction(client)

        with pytest.raises(ValueError, match="不存在"):
            action.publish_image(
                title="图文",
                content="正文",
                image_paths=[str(tmp_path / "missing.jpg")],
            )

        client.navigate.assert_not_called()

    def test_relative_image_path_is_normalized_before_upload(self, tmp_path, monkeypatch):
        image = tmp_path / "image.jpg"
        image.write_bytes(b"image")
        monkeypatch.chdir(tmp_path)
        client = MagicMock(spec=XiaohongshuClient)
        client.page = MagicMock()
        action = PublishAction(client)

        with (
            patch.object(action, "_navigate_to_publish"),
            patch.object(action, "_click_publish_tab"),
            patch.object(action, "_upload_images") as mock_upload,
            patch.object(action, "_fill_title"),
            patch.object(action, "_fill_content"),
            patch.object(action, "_set_visibility"),
            patch.object(action, "_check_publish_ready", return_value={"title_ok": True}),
        ):
            result = action.publish_image(
                title="图文",
                content="正文",
                image_paths=["image.jpg"],
                auto_publish=False,
            )

        mock_upload.assert_called_once_with([str(image.resolve())])
        assert result["image_count"] == 1

    def test_invalid_video_request_does_not_navigate(self, tmp_path):
        client = MagicMock(spec=XiaohongshuClient)
        client.page = MagicMock()
        action = PublishAction(client)

        with pytest.raises(ValueError, match="不存在"):
            action.publish_video(
                title="视频",
                content="正文",
                video_path=str(tmp_path / "missing.mp4"),
            )

        client.navigate.assert_not_called()

    def test_invalid_schedule_does_not_navigate(self, tmp_path):
        image = tmp_path / "image.jpg"
        image.write_bytes(b"image")
        client = MagicMock(spec=XiaohongshuClient)
        client.page = MagicMock()
        action = PublishAction(client)

        with pytest.raises(ValueError, match="格式"):
            action.publish_image(
                title="图文",
                content="正文",
                image_paths=[str(image)],
                schedule_time="tomorrow",
            )

        client.navigate.assert_not_called()

    def test_schedule_ui_failure_stops_publish(self):
        client = MagicMock(spec=XiaohongshuClient)
        client.page = MagicMock()
        client.page.locator.return_value.click.side_effect = RuntimeError("missing switch")
        action = PublishAction(client)

        with pytest.raises(RuntimeError, match="已阻止继续发布"):
            action._set_schedule("2026-08-24 12:00")

    @patch("scripts.publish.md_to_images")
    def test_markdown_validates_before_rendering(self, mock_render):
        with pytest.raises(ValueError, match="格式"):
            publish_markdown(
                title="Markdown",
                markdown_text="# Body",
                schedule_time="invalid",
            )

        mock_render.assert_not_called()
