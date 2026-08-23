"""
Named selector contracts for browser automation.

Contracts are the selector source of truth. Runtime modules may expose
compatibility constants, but those constants must be derived from the matching
contract instead of repeating selector values.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectorContract:
    """A named, ordered set of selectors for one automation target."""

    name: str
    owner: str
    purpose: str
    selectors: tuple[str, ...]
    required: bool = True

    @property
    def primary(self) -> str:
        """Return the preferred selector used by the runtime."""
        if not self.selectors:
            raise ValueError(f"{self.name}: at least one selector is required")
        return self.selectors[0]

    @property
    def fallbacks(self) -> tuple[str, ...]:
        """Return selectors tried after the primary selector."""
        return self.selectors[1:]


LOGIN_QRCODE_CONTRACT = SelectorContract(
    name="login.qrcode",
    owner="login",
    purpose="Find the WeChat QR code image during login",
    selectors=('img.qrcode-img[src^="data:image"]',),
)
LOGIN_PROFILE_LINK_CONTRACT = SelectorContract(
    name="login.profile_link",
    owner="login",
    purpose="Detect a logged-in profile link",
    selectors=('a[href*="/user/profile/"]',),
)
INTERACT_LIKE_BUTTON_CONTRACT = SelectorContract(
    name="interact.like_button",
    owner="interact",
    purpose="Click the note like button",
    selectors=(".interact-container .left .like-wrapper",),
)
INTERACT_LIKE_ACTIVE_CONTRACT = SelectorContract(
    name="interact.like_active",
    owner="interact",
    purpose="Detect an active note like button",
    selectors=(
        ".interact-container .left .like-wrapper.active, "
        ".interact-container .left .like-wrapper.liked",
    ),
)
INTERACT_COLLECT_BUTTON_CONTRACT = SelectorContract(
    name="interact.collect_button",
    owner="interact",
    purpose="Click the note collect button",
    selectors=(".interact-container .left .collect-wrapper",),
)
INTERACT_COLLECT_ACTIVE_CONTRACT = SelectorContract(
    name="interact.collect_active",
    owner="interact",
    purpose="Detect an active note collect button",
    selectors=(
        ".interact-container .left .collect-wrapper.active, "
        ".interact-container .left .collect-wrapper.collected",
    ),
)
INTERACT_RATE_LIMIT_TOAST_CONTRACT = SelectorContract(
    name="comment.rate_limit_toast",
    owner="comment",
    purpose="Detect comment rate-limit feedback",
    selectors=(
        'div.d-toast:has-text("频繁")',
        'div.d-toast:has-text("操作太快")',
        'div.d-toast:has-text("稍后再试")',
        'div.d-toast:has-text("限制")',
    ),
)


SELECTOR_CONTRACTS: tuple[SelectorContract, ...] = (
    LOGIN_QRCODE_CONTRACT,
    LOGIN_PROFILE_LINK_CONTRACT,
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
        selectors=(
            "div.ql-editor",
            '[role="textbox"]',
            'div[contenteditable="true"]',
        ),
    ),
    SelectorContract(
        name="publish.publish_button",
        owner="publish",
        purpose="Click publish after the user has confirmed the action",
        selectors=(
            "xhs-publish-btn",
            ".publish-page-publish-btn button.bg-red",
            'button:has-text("发布")',
        ),
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
    INTERACT_RATE_LIMIT_TOAST_CONTRACT,
    INTERACT_LIKE_BUTTON_CONTRACT,
    INTERACT_LIKE_ACTIVE_CONTRACT,
    INTERACT_COLLECT_BUTTON_CONTRACT,
    INTERACT_COLLECT_ACTIVE_CONTRACT,
    SelectorContract(
        name="client.captcha_url",
        owner="client",
        purpose="Detect captcha and security verification pages",
        selectors=(
            "captcha",
            "security-verification",
            "website-login/captcha",
            "verifyType",
            "verifyBiz",
        ),
    ),
)


REQUIRED_CONTRACT_NAMES = {
    contract.name for contract in SELECTOR_CONTRACTS if contract.required
}


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


def validate_runtime_selector_bindings() -> list[str]:
    """Return errors when compatibility constants drift from their contracts.

    Imports are intentionally not caught. A broken owner module is a contract
    failure and must fail closed instead of silently weakening the gate.
    """
    from .interact import InteractAction
    from .login import LoginAction

    bindings = (
        (
            LOGIN_QRCODE_CONTRACT,
            LoginAction.QRCODE_SELECTOR,
            LOGIN_QRCODE_CONTRACT.primary,
            "LoginAction.QRCODE_SELECTOR",
        ),
        (
            LOGIN_PROFILE_LINK_CONTRACT,
            LoginAction.PROFILE_LINK_SELECTOR,
            LOGIN_PROFILE_LINK_CONTRACT.primary,
            "LoginAction.PROFILE_LINK_SELECTOR",
        ),
        (
            INTERACT_LIKE_BUTTON_CONTRACT,
            InteractAction.LIKE_SELECTOR,
            INTERACT_LIKE_BUTTON_CONTRACT.primary,
            "InteractAction.LIKE_SELECTOR",
        ),
        (
            INTERACT_LIKE_ACTIVE_CONTRACT,
            InteractAction.LIKE_ACTIVE_SELECTOR,
            INTERACT_LIKE_ACTIVE_CONTRACT.primary,
            "InteractAction.LIKE_ACTIVE_SELECTOR",
        ),
        (
            INTERACT_COLLECT_BUTTON_CONTRACT,
            InteractAction.COLLECT_SELECTOR,
            INTERACT_COLLECT_BUTTON_CONTRACT.primary,
            "InteractAction.COLLECT_SELECTOR",
        ),
        (
            INTERACT_COLLECT_ACTIVE_CONTRACT,
            InteractAction.COLLECT_ACTIVE_SELECTOR,
            INTERACT_COLLECT_ACTIVE_CONTRACT.primary,
            "InteractAction.COLLECT_ACTIVE_SELECTOR",
        ),
        (
            INTERACT_RATE_LIMIT_TOAST_CONTRACT,
            InteractAction.RATE_LIMIT_SELECTORS,
            INTERACT_RATE_LIMIT_TOAST_CONTRACT.selectors,
            "InteractAction.RATE_LIMIT_SELECTORS",
        ),
    )

    errors: list[str] = []
    for contract, runtime_value, expected, runtime_name in bindings:
        if runtime_value != expected:
            errors.append(
                f"{contract.name}: {runtime_name} must derive from the contract"
            )
    return errors


def validate_selector_contracts() -> list[str]:
    """Return validation errors for malformed or disconnected contracts."""
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
    errors.extend(validate_runtime_selector_bindings())
    return errors
