"""Release version consistency checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib

from . import __version__


def read_project_version(pyproject_path: Path = Path("pyproject.toml")) -> str:
    with pyproject_path.open("rb") as handle:
        project = tomllib.load(handle)["project"]
    return str(project["version"])


def validate_release_version(tag: str, project_version: str, runtime_version: str) -> list[str]:
    errors = []
    expected_tag = f"v{project_version}"
    if tag != expected_tag:
        errors.append(f"release tag {tag!r} does not match project version {expected_tag!r}")
    if runtime_version != project_version:
        errors.append(
            f"runtime version {runtime_version!r} does not match project version {project_version!r}"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate release version consistency.")
    parser.add_argument("tag", help="Git tag, for example v1.5.0")
    parser.add_argument("--pyproject", type=Path, default=Path("pyproject.toml"))
    args = parser.parse_args(argv)

    project_version = read_project_version(args.pyproject)
    errors = validate_release_version(args.tag, project_version, __version__)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Release version verified: {args.tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
