"""
Selector contract tests.
"""

import builtins
import json
from types import SimpleNamespace

import pytest

from scripts.__main__ import cmd_selectors
from scripts.interact import InteractAction
from scripts.login import LoginAction
from scripts.selectors import (
    INTERACT_COLLECT_ACTIVE_CONTRACT,
    INTERACT_COLLECT_BUTTON_CONTRACT,
    INTERACT_LIKE_ACTIVE_CONTRACT,
    INTERACT_LIKE_BUTTON_CONTRACT,
    INTERACT_RATE_LIMIT_TOAST_CONTRACT,
    LOGIN_CREATOR_READY_CONTRACT,
    LOGIN_PROFILE_LINK_CONTRACT,
    LOGIN_QRCODE_CONTRACT,
    REQUIRED_CONTRACT_NAMES,
    SelectorContract,
    get_selector_contract,
    get_selector_contracts,
    validate_runtime_selector_bindings,
    validate_selector_contracts,
)


def test_required_selector_contracts_exist():
    """Core browser actions must have named selector contracts."""
    names = {contract.name for contract in get_selector_contracts()}

    missing = sorted(REQUIRED_CONTRACT_NAMES - names)

    assert missing == []


def test_selector_contracts_are_valid():
    """Each selector contract should explain the target and stay connected."""
    assert validate_selector_contracts() == []


def test_contract_lookup_by_name():
    """Selectors can be looked up by stable contract name."""
    contract = get_selector_contract("publish.publish_button")

    assert contract.owner == "publish"
    assert "publish" in contract.purpose.lower()
    assert any("xhs-publish-btn" in selector for selector in contract.selectors)


def test_contract_exposes_primary_and_fallbacks():
    """Ordered selectors have explicit preferred and fallback interfaces."""
    contract = SelectorContract(
        name="test.target",
        owner="test",
        purpose="Exercise ordered selector access",
        selectors=(".primary", ".fallback-one", ".fallback-two"),
    )

    assert contract.primary == ".primary"
    assert contract.fallbacks == (".fallback-one", ".fallback-two")


def test_runtime_selector_constants_derive_from_registry_contracts():
    """Compatibility constants must use contract values without duplication."""
    assert get_selector_contract("login.qrcode") is LOGIN_QRCODE_CONTRACT
    assert get_selector_contract("login.profile_link") is LOGIN_PROFILE_LINK_CONTRACT
    assert get_selector_contract("interact.like_button") is INTERACT_LIKE_BUTTON_CONTRACT
    assert get_selector_contract("interact.like_active") is INTERACT_LIKE_ACTIVE_CONTRACT
    assert (
        get_selector_contract("interact.collect_button")
        is INTERACT_COLLECT_BUTTON_CONTRACT
    )
    assert (
        get_selector_contract("interact.collect_active")
        is INTERACT_COLLECT_ACTIVE_CONTRACT
    )

    assert LoginAction.QRCODE_SELECTOR == LOGIN_QRCODE_CONTRACT.primary
    assert LoginAction.PROFILE_LINK_SELECTOR == LOGIN_PROFILE_LINK_CONTRACT.primary
    assert LoginAction.CREATOR_READY_SELECTORS == LOGIN_CREATOR_READY_CONTRACT.selectors
    assert InteractAction.LIKE_SELECTOR == INTERACT_LIKE_BUTTON_CONTRACT.primary
    assert InteractAction.LIKE_ACTIVE_SELECTOR == INTERACT_LIKE_ACTIVE_CONTRACT.primary
    assert InteractAction.COLLECT_SELECTOR == INTERACT_COLLECT_BUTTON_CONTRACT.primary
    assert (
        InteractAction.COLLECT_ACTIVE_SELECTOR
        == INTERACT_COLLECT_ACTIVE_CONTRACT.primary
    )
    assert (
        InteractAction.RATE_LIMIT_SELECTORS
        == INTERACT_RATE_LIMIT_TOAST_CONTRACT.selectors
    )
    assert validate_runtime_selector_bindings() == []


def test_runtime_selector_binding_gate_detects_deliberate_drift(monkeypatch):
    """A runtime selector changed outside its contract must fail the gate."""
    monkeypatch.setattr(LoginAction, "PROFILE_LINK_SELECTOR", "a.drifted-selector")

    errors = validate_runtime_selector_bindings()

    assert errors == [
        "login.profile_link: LoginAction.PROFILE_LINK_SELECTOR "
        "must derive from the contract"
    ]


def test_runtime_selector_binding_gate_fails_closed_on_owner_import(monkeypatch):
    """An owner import error must surface instead of weakening validation."""
    real_import = builtins.__import__

    def fail_interact_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "interact" and level == 1:
            raise ImportError("owner module unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_interact_import)

    with pytest.raises(ImportError, match="owner module unavailable"):
        validate_runtime_selector_bindings()


def test_selector_cli_keeps_runtime_binding_details_private(capsys):
    """Public selector JSON must contain contracts, not runtime constant names."""
    exit_code = cmd_selectors(SimpleNamespace(owner="login"))

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["count"] == 3
    assert all(
        set(contract) == {"name", "owner", "purpose", "selectors", "required"}
        for contract in payload["contracts"]
    )

def test_login_creator_ready_contract_is_registered():
    """The Creator Center ready candidates are registered as a named contract."""
    contract = get_selector_contract("login.creator_ready")

    assert contract.owner == "login"
    assert contract.selectors == ("div.upload-content", "div.creator-tab", 'input[type="file"]')


def test_profile_link_contract_uses_precise_channel_selector():
    """The profile link contract uses the precise channel-anchored selector."""
    assert LOGIN_PROFILE_LINK_CONTRACT.primary == (
        'a.link-wrapper[href^="/user/profile/"]:has(span.channel)'
    )
