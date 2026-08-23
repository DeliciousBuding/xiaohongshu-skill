"""
CLI JSON output contract tests.
"""

from scripts.output_contracts import (
    REQUIRED_OUTPUT_COMMANDS,
    get_output_contract,
    get_output_contracts,
    validate_output_contracts,
)
from scripts.strategy import StrategyManager
from scripts.templates import generate_template


def test_required_output_contracts_exist():
    """Agent-facing commands should have documented JSON output contracts."""
    commands = {contract.command for contract in get_output_contracts()}

    missing = sorted(REQUIRED_OUTPUT_COMMANDS - commands)

    assert missing == []


def test_output_contracts_are_valid():
    """Contracts should have stable names and at least one top-level field."""
    assert validate_output_contracts() == []


def test_contract_lookup_by_command():
    """One command can be looked up by its stable command name."""
    contract = get_output_contract("search")

    assert contract.name == "search.results"
    assert "count" in contract.required_fields
    assert "results" in contract.required_fields


def test_template_contract_matches_real_output():
    """Template contract should match the pure template generator."""
    payload = generate_template("咖啡")
    contract = get_output_contract("template")

    assert set(contract.required_fields) <= payload.keys()


def test_strategy_contracts_match_real_outputs(tmp_path):
    """Strategy contracts should match local config-backed outputs."""
    manager = StrategyManager(config_path=str(tmp_path / "strategy.json"))

    outputs = {
        "strategy-init": manager.init_strategy("测试账号"),
        "strategy-show": manager.show_strategy(),
        "strategy-add-post": manager.add_scheduled_post("2026-07-07", "测试选题"),
        "strategy-check-limit": manager.check_daily_limit("likes"),
    }

    for command, payload in outputs.items():
        contract = get_output_contract(command)
        assert set(contract.required_fields) <= payload.keys(), command


def test_publish_contracts_describe_confirmation_states():
    for command in ("publish", "publish-video", "publish-longform"):
        contract = get_output_contract(command)
        assert {"success", "published", "warnings"} <= set(contract.required_fields)
        assert "submitted_unconfirmed" in contract.notes
        assert "never retry" in contract.notes

    video_contract = get_output_contract("publish-video")
    assert "schedule_time" in video_contract.required_fields

def test_creator_login_contracts_are_registered():
    """Creator Center commands should have documented output contracts."""
    creator_login = get_output_contract("creator-login")
    assert creator_login.name == "creator_login.result"
    assert set(creator_login.required_fields) == {"status", "message"}
    assert "logged_in" in creator_login.notes
    assert "login_required" in creator_login.notes
    assert "timeout" in creator_login.notes

    check_creator_login = get_output_contract("check-creator-login")
    assert check_creator_login.name == "check_creator_login.status"
    assert set(check_creator_login.required_fields) == {"is_logged_in"}
