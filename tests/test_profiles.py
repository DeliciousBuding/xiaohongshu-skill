"""
Profile path helpers.
"""

import pytest

from scripts.profiles import ProfileNameError, list_profiles, profile_paths


def test_default_profile_keeps_legacy_paths(tmp_path):
    paths = profile_paths(root=tmp_path)

    assert paths.cookie_path == tmp_path / "cookies.json"
    assert paths.user_data_dir == tmp_path / "browser-data"


def test_named_profile_uses_isolated_paths(tmp_path):
    paths = profile_paths("brand-a", root=tmp_path)

    assert paths.cookie_path == tmp_path / "profiles" / "brand-a" / "cookies.json"
    assert paths.user_data_dir == tmp_path / "profiles" / "brand-a" / "browser-data"


def test_profile_name_rejects_path_segments(tmp_path):
    with pytest.raises(ProfileNameError):
        profile_paths("../private", root=tmp_path)


def test_profile_name_rejects_empty_value(tmp_path):
    with pytest.raises(ProfileNameError):
        profile_paths(" ", root=tmp_path)


def test_list_profiles_includes_default_when_legacy_state_exists(tmp_path):
    (tmp_path / "cookies.json").write_text("[]", encoding="utf-8")
    (tmp_path / "browser-data").mkdir()

    profiles = list_profiles(root=tmp_path)

    assert profiles == [
        {
            "name": "default",
            "cookie_path": str(tmp_path / "cookies.json"),
            "user_data_dir": str(tmp_path / "browser-data"),
            "cookie_exists": True,
            "user_data_dir_exists": True,
        }
    ]


def test_list_profiles_includes_named_profiles(tmp_path):
    profile_dir = tmp_path / "profiles" / "brand-a"
    profile_dir.mkdir(parents=True)
    (profile_dir / "browser-data").mkdir()

    profiles = list_profiles(root=tmp_path)

    assert profiles == [
        {
            "name": "brand-a",
            "cookie_path": str(profile_dir / "cookies.json"),
            "user_data_dir": str(profile_dir / "browser-data"),
            "cookie_exists": False,
            "user_data_dir_exists": True,
        }
    ]
