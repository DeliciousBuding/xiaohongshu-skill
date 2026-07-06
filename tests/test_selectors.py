"""
Selector contract tests.
"""

from scripts.selectors import (
    REQUIRED_CONTRACT_NAMES,
    get_selector_contract,
    get_selector_contracts,
    validate_selector_contracts,
)


def test_required_selector_contracts_exist():
    """Core browser actions must have named selector contracts."""
    names = {contract.name for contract in get_selector_contracts()}

    missing = sorted(REQUIRED_CONTRACT_NAMES - names)

    assert missing == []


def test_selector_contracts_are_valid():
    """Each selector contract should explain the target and provide fallbacks."""
    assert validate_selector_contracts() == []


def test_contract_lookup_by_name():
    """Selectors can be looked up by stable contract name."""
    contract = get_selector_contract("publish.publish_button")

    assert contract.owner == "publish"
    assert "publish" in contract.purpose.lower()
    assert any("xhs-publish-btn" in selector for selector in contract.selectors)
