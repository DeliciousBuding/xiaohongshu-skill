"""
Named selector contracts for browser automation.

The selectors still live near the actions that use them. This registry gives
tests and docs one stable map to check when Xiaohongshu changes the page shape.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectorContract:
    """A named set of selectors for one browser automation target."""

    name: str
    owner: str
    purpose: str
    selectors: tuple[str, ...]
    required: bool = True


SELECTOR_CONTRACTS: tuple[SelectorContract, ...] = (
    SelectorContract(
        name="login.qrcode",
        owner="login",
        purpose="Find the WeChat QR code image during login",
        selectors=('img.qrcode-img[src^="data:image"]',),
    ),
    SelectorContract(
        name="login.profile_link",
        owner="login",
        purpose="Detect a logged-in profile link",
        selectors=('a[href*="/user/profile/"]',),
    ),
    SelectorContract(
        name="login.creator_ready",
        owner="login",
        purpose="Detect an authenticated Creator Center publish page",
        selectors=("div.upload-content", "div.creator-tab", 'input[type="file"]'),
    ),
    SelectorContract(
        name="search.filter_button",
        owner="search",
        purpose="Open the search filter panel",
        selectors=("div.filter",),
    ),
    SelectorContract(
        name="search.filter_panel",
        owner="search",
        purpose="Find the search filter panel after hover",
        selectors=("div.filter-panel",),
    ),
    SelectorContract(
        name="search.note_item",
        owner="search",
        purpose="Find rendered search result cards",
        selectors=("section.note-item",),
    ),
    SelectorContract(
        name="search.cover_link",
        owner="search",
        purpose="Extract note ids and xsec_token from result links",
        selectors=('a.cover[href*="/explore/"]', 'a[href*="/explore/"]'),
    ),
    SelectorContract(
        name="publish.upload_area",
        owner="publish",
        purpose="Detect that the creator upload page has loaded",
        selectors=("div.upload-content", "div.creator-tab"),
    ),
    SelectorContract(
        name="publish.tab",
        owner="publish",
        purpose="Switch between image, video, and longform publish modes",
        selectors=("div.creator-tab",),
    ),
    SelectorContract(
        name="publish.file_input",
        owner="publish",
        purpose="Upload image or video files",
        selectors=(".upload-input", 'input[type="file"]'),
    ),
    SelectorContract(
        name="publish.title_input",
        owner="publish",
        purpose="Fill the publish title input",
        selectors=("div.d-input input", 'input[placeholder*="标题"]'),
    ),
    SelectorContract(
        name="publish.content_editor",
        owner="publish",
        purpose="Fill the publish content editor",
        selectors=("div.ql-editor", '[role="textbox"]', 'div[contenteditable="true"]'),
    ),
    SelectorContract(
        name="publish.publish_button",
        owner="publish",
        purpose="Click publish after the user has confirmed the action",
        selectors=("xhs-publish-btn", ".publish-page-publish-btn button.bg-red", 'button:has-text("发布")'),
    ),
    SelectorContract(
        name="comment.input_trigger",
        owner="comment",
        purpose="Activate the comment input",
        selectors=("div.input-box div.content-edit span",),
    ),
    SelectorContract(
        name="comment.input_editor",
        owner="comment",
        purpose="Type comment or reply content",
        selectors=("div.input-box div.content-edit p.content-input",),
    ),
    SelectorContract(
        name="comment.submit_button",
        owner="comment",
        purpose="Submit a comment or reply",
        selectors=("div.bottom button.submit",),
    ),
    SelectorContract(
        name="comment.reply_button",
        owner="comment",
        purpose="Find a reply affordance on an existing comment",
        selectors=(".reply-btn", 'button:has-text("回复")', 'span:has-text("回复")'),
    ),
    SelectorContract(
        name="comment.rate_limit_toast",
        owner="comment",
        purpose="Detect comment rate-limit feedback",
        selectors=(
            'div.d-toast:has-text("频繁")',
            'div.d-toast:has-text("操作太快")',
            'div.d-toast:has-text("稍后再试")',
            'div.d-toast:has-text("限制")',
        ),
    ),
    SelectorContract(
        name="interact.like_button",
        owner="interact",
        purpose="Click the note like button",
        selectors=(".interact-container .left .like-wrapper",),
    ),
    SelectorContract(
        name="interact.collect_button",
        owner="interact",
        purpose="Click the note collect button",
        selectors=(".interact-container .left .collect-wrapper",),
    ),
    SelectorContract(
        name="client.captcha_url",
        owner="client",
        purpose="Detect captcha and security verification pages",
        selectors=("captcha", "security-verification", "website-login/captcha", "verifyType", "verifyBiz"),
    ),
)


REQUIRED_CONTRACT_NAMES = {contract.name for contract in SELECTOR_CONTRACTS if contract.required}


def get_selector_contracts(owner: str | None = None) -> tuple[SelectorContract, ...]:
    """Return selector contracts, optionally filtered by module owner."""
    if owner is None:
        return SELECTOR_CONTRACTS
    return tuple(contract for contract in SELECTOR_CONTRACTS if contract.owner == owner)


def get_selector_contract(name: str) -> SelectorContract:
    """Look up one selector contract by stable name."""
    for contract in SELECTOR_CONTRACTS:
        if contract.name == name:
            return contract
    raise KeyError(name)


def validate_selector_contracts() -> list[str]:
    """Return validation errors for malformed contracts."""
    errors: list[str] = []
    seen: set[str] = set()
    for contract in SELECTOR_CONTRACTS:
        if not contract.name or "." not in contract.name:
            errors.append(f"{contract.name}: name must include owner prefix")
        if contract.name in seen:
            errors.append(f"{contract.name}: duplicate name")
        seen.add(contract.name)
        if not contract.owner:
            errors.append(f"{contract.name}: owner is required")
        if not contract.purpose:
            errors.append(f"{contract.name}: purpose is required")
        if not contract.selectors:
            errors.append(f"{contract.name}: at least one selector is required")
        for selector in contract.selectors:
            if not selector or not selector.strip():
                errors.append(f"{contract.name}: selector cannot be blank")
    return errors
