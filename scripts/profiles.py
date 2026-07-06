"""
Browser profile path helpers.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_PROFILE = "default"
DEFAULT_ROOT = Path(os.path.expanduser("~/.xiaohongshu"))
PROFILE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class ProfileNameError(ValueError):
    """Invalid profile name."""


@dataclass(frozen=True)
class ProfilePaths:
    cookie_path: Path
    user_data_dir: Path


def _normalize_profile(profile: str | None) -> str:
    name = (profile or DEFAULT_PROFILE).strip()
    if name == DEFAULT_PROFILE:
        return DEFAULT_PROFILE
    if not PROFILE_RE.match(name):
        raise ProfileNameError(
            "Profile names may contain letters, numbers, dot, underscore, or dash only."
        )
    return name


def profile_paths(profile: str | None = None, root: str | Path | None = None) -> ProfilePaths:
    """Return cookie and browser-data paths for a profile."""
    root_path = Path(root) if root is not None else DEFAULT_ROOT
    name = _normalize_profile(profile)

    if name == DEFAULT_PROFILE:
        return ProfilePaths(
            cookie_path=root_path / "cookies.json",
            user_data_dir=root_path / "browser-data",
        )

    profile_dir = root_path / "profiles" / name
    return ProfilePaths(
        cookie_path=profile_dir / "cookies.json",
        user_data_dir=profile_dir / "browser-data",
    )


def _profile_info(name: str, paths: ProfilePaths) -> dict[str, object]:
    return {
        "name": name,
        "cookie_path": str(paths.cookie_path),
        "user_data_dir": str(paths.user_data_dir),
        "cookie_exists": paths.cookie_path.exists(),
        "user_data_dir_exists": paths.user_data_dir.exists(),
    }


def list_profiles(root: str | Path | None = None) -> list[dict[str, object]]:
    """List profiles that already have local state."""
    root_path = Path(root) if root is not None else DEFAULT_ROOT
    profiles: list[dict[str, object]] = []

    default_paths = profile_paths(DEFAULT_PROFILE, root=root_path)
    if default_paths.cookie_path.exists() or default_paths.user_data_dir.exists():
        profiles.append(_profile_info(DEFAULT_PROFILE, default_paths))

    profiles_dir = root_path / "profiles"
    if profiles_dir.exists():
        for profile_dir in sorted(path for path in profiles_dir.iterdir() if path.is_dir()):
            name = profile_dir.name
            if not PROFILE_RE.match(name):
                continue
            paths = profile_paths(name, root=root_path)
            if paths.cookie_path.exists() or paths.user_data_dir.exists():
                profiles.append(_profile_info(name, paths))

    return profiles


def env_profile() -> str | None:
    """Return the process profile override, if present."""
    return os.environ.get("XHS_PROFILE") or None
