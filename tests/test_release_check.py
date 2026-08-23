"""Tests for release version consistency."""

from pathlib import Path

from scripts.release_check import read_project_version, validate_release_version


def test_project_version_matches_runtime_version():
    from scripts import __version__

    assert read_project_version() == __version__


def test_release_tag_must_match_project_version():
    assert validate_release_version("v1.5.0", "1.5.0", "1.5.0") == []
    assert validate_release_version("v1.4.0", "1.5.0", "1.5.0") == [
        "release tag 'v1.4.0' does not match project version 'v1.5.0'"
    ]


def test_runtime_version_must_match_project_version():
    errors = validate_release_version("v1.5.0", "1.5.0", "1.4.0")

    assert errors == ["runtime version '1.4.0' does not match project version '1.5.0'"]


def test_read_project_version(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "demo"\nversion = "2.3.4"\n', encoding="utf-8")

    assert read_project_version(Path(pyproject)) == "2.3.4"
