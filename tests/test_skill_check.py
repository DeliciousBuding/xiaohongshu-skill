"""Tests for the Agent Skills validator wrapper."""

from pathlib import Path

from scripts.skill_check import main, validate_skill_file


def test_repository_skill_is_valid():
    assert validate_skill_file(Path("SKILL.md")) == []


def test_unknown_frontmatter_field_fails(tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(
        "---\nname: demo\ndescription: Use when testing.\nunknown: true\n---\n# Demo\n",
        encoding="utf-8",
    )

    errors = validate_skill_file(skill_path)

    assert any("Unexpected fields" in error for error in errors)


def test_cli_returns_nonzero_for_invalid_skill(tmp_path):
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text("# Missing frontmatter\n", encoding="utf-8")

    assert main([str(skill_path)]) == 1
