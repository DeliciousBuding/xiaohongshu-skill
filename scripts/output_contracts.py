"""
JSON output contracts for agent-facing CLI commands.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OutputContract:
    """Stable JSON shape for one CLI command."""

    name: str
    command: str
    purpose: str
    required_fields: tuple[str, ...]
    item_fields: tuple[str, ...] = field(default_factory=tuple)
    notes: str = ""


OUTPUT_CONTRACTS: tuple[OutputContract, ...] = (
    OutputContract(
        name="login.result",
        command="login",
        purpose="QR login result",
        required_fields=("status", "qrcode_path", "username", "message"),
        notes="status is one of logged_in, timeout, or error",
    ),
    OutputContract(
        name="qrcode.result",
        command="qrcode",
        purpose="QR code path and login result",
        required_fields=("status", "message"),
        notes="qrcode_path is present when a QR image is generated",
    ),
    OutputContract(
        name="check_login.status",
        command="check-login",
        purpose="Current login status",
        required_fields=("is_logged_in", "username"),
    ),
    OutputContract(
        name="creator_login.result",
        command="creator-login",
        purpose="Creator Center interactive login result",
        required_fields=("status", "message"),
        notes="status is one of logged_in, login_required, or timeout",
    ),
    OutputContract(
        name="check_creator_login.status",
        command="check-creator-login",
        purpose="Creator Center login status",
        required_fields=("is_logged_in",),
    ),
    OutputContract(
        name="profiles.list",
        command="profiles",
        purpose="Local account profile inventory",
        required_fields=("count", "profiles"),
        item_fields=("name", "cookie_exists", "user_data_dir_exists"),
    ),
    OutputContract(
        name="selectors.list",
        command="selectors",
        purpose="Browser selector contracts",
        required_fields=("count", "contracts"),
        item_fields=("name", "owner", "purpose", "selectors", "required"),
    ),
    OutputContract(
        name="contracts.list",
        command="contracts",
        purpose="CLI output contracts",
        required_fields=("count", "contracts"),
        item_fields=("name", "command", "purpose", "required_fields", "item_fields", "notes"),
    ),
    OutputContract(
        name="search.results",
        command="search",
        purpose="Search result list",
        required_fields=("count", "results"),
        item_fields=("id", "xsec_token", "title", "type", "user", "user_id"),
    ),
    OutputContract(
        name="feed.detail",
        command="feed",
        purpose="Note detail payload",
        required_fields=(),
        notes="Pass-through note detail object from the extraction layer",
    ),
    OutputContract(
        name="user.profile",
        command="user",
        purpose="User profile payload",
        required_fields=(),
        notes="Pass-through user profile object from the extraction layer",
    ),
    OutputContract(
        name="me.profile",
        command="me",
        purpose="Current account profile payload",
        required_fields=(),
        notes="Pass-through user profile object for the logged-in account",
    ),
    OutputContract(
        name="comment.result",
        command="comment",
        purpose="Post comment result",
        required_fields=("status", "feed_id", "content", "message"),
    ),
    OutputContract(
        name="reply.result",
        command="reply",
        purpose="Reply to a comment",
        required_fields=("status", "feed_id", "comment_id", "content", "message"),
    ),
    OutputContract(
        name="reply_notification.result",
        command="reply-notification",
        purpose="Reply from the notification page",
        required_fields=("status", "action", "notification_index", "content", "message"),
    ),
    OutputContract(
        name="like.result",
        command="like",
        purpose="Like a note",
        required_fields=("status", "action", "feed_id", "message"),
    ),
    OutputContract(
        name="unlike.result",
        command="unlike",
        purpose="Unlike a note",
        required_fields=("status", "action", "feed_id", "message"),
    ),
    OutputContract(
        name="collect.result",
        command="collect",
        purpose="Collect a note",
        required_fields=("status", "action", "feed_id", "message"),
    ),
    OutputContract(
        name="uncollect.result",
        command="uncollect",
        purpose="Uncollect a note",
        required_fields=("status", "action", "feed_id", "message"),
    ),
    OutputContract(
        name="explore.results",
        command="explore",
        purpose="Explore feed list",
        required_fields=(),
        notes="Returns a list of feed item objects",
    ),
    OutputContract(
        name="publish_image.result",
        command="publish",
        purpose="Image-text publish preparation or publish result",
        required_fields=(
            "status", "action", "title", "image_count", "success", "published",
            "message", "warnings",
        ),
        notes="status is ready, confirmed, submitted_unconfirmed, or failed; never retry submitted_unconfirmed automatically",
    ),
    OutputContract(
        name="publish_video.result",
        command="publish-video",
        purpose="Video publish preparation or publish result",
        required_fields=(
            "status", "action", "title", "video_path", "schedule_time", "success",
            "published", "message", "warnings",
        ),
        notes="status is ready, confirmed, submitted_unconfirmed, or failed; never retry submitted_unconfirmed automatically",
    ),
    OutputContract(
        name="publish_md.result",
        command="publish-md",
        purpose="Markdown-to-image publish result",
        required_fields=("status", "message"),
        notes="Successful output follows publish image fields",
    ),
    OutputContract(
        name="publish_longform.result",
        command="publish-longform",
        purpose="Longform publish preparation or publish result",
        required_fields=(
            "status", "action", "title", "success", "published", "message", "warnings",
        ),
        notes="status is ready, confirmed, submitted_unconfirmed, or failed; never retry submitted_unconfirmed automatically",
    ),
    OutputContract(
        name="template.result",
        command="template",
        purpose="Writing template result",
        required_fields=("topic", "note_type", "titles", "content", "tags"),
    ),
    OutputContract(
        name="strategy_init.result",
        command="strategy-init",
        purpose="Initialize content strategy",
        required_fields=("status", "message", "persona", "target_audience", "content_direction"),
    ),
    OutputContract(
        name="strategy_show.result",
        command="strategy-show",
        purpose="Show content strategy",
        required_fields=(),
        notes="Returns the current strategy object or status message",
    ),
    OutputContract(
        name="strategy_add_post.result",
        command="strategy-add-post",
        purpose="Add one scheduled post",
        required_fields=("status", "message", "entry"),
    ),
    OutputContract(
        name="strategy_check_limit.result",
        command="strategy-check-limit",
        purpose="Check one daily quota",
        required_fields=("action_type", "allowed", "used", "limit", "remaining"),
    ),
    OutputContract(
        name="sop.result",
        command="sop",
        purpose="Run one SOP workflow",
        required_fields=("status",),
    ),
)


REQUIRED_OUTPUT_COMMANDS = {contract.command for contract in OUTPUT_CONTRACTS}


def get_output_contracts(command: str | None = None) -> tuple[OutputContract, ...]:
    """Return output contracts, optionally filtered by command."""
    if command is None:
        return OUTPUT_CONTRACTS
    return tuple(contract for contract in OUTPUT_CONTRACTS if contract.command == command)


def get_output_contract(command: str) -> OutputContract:
    """Look up one output contract by command name."""
    for contract in OUTPUT_CONTRACTS:
        if contract.command == command:
            return contract
    raise KeyError(command)


def validate_output_contracts() -> list[str]:
    """Return validation errors for malformed output contracts."""
    errors: list[str] = []
    seen_names: set[str] = set()
    seen_commands: set[str] = set()
    for contract in OUTPUT_CONTRACTS:
        if not contract.name or "." not in contract.name:
            errors.append(f"{contract.name}: name must include a namespace")
        if contract.name in seen_names:
            errors.append(f"{contract.name}: duplicate name")
        seen_names.add(contract.name)
        if not contract.command:
            errors.append(f"{contract.name}: command is required")
        if contract.command in seen_commands:
            errors.append(f"{contract.command}: duplicate command")
        seen_commands.add(contract.command)
        if not contract.purpose:
            errors.append(f"{contract.name}: purpose is required")
        for field_name in contract.required_fields + contract.item_fields:
            if not field_name or not field_name.strip():
                errors.append(f"{contract.name}: field names cannot be blank")
    return errors
