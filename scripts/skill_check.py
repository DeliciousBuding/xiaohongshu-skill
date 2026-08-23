"""Validate the repository's Agent Skill frontmatter."""

from __future__ import annotations

import sys
from pathlib import Path

from skills_ref.errors import ParseError
from skills_ref.parser import parse_frontmatter
from skills_ref.validator import validate_metadata


def validate_skill_file(skill_path: Path) -> list[str]:
    """Return Agent Skills validation errors for one SKILL.md file."""
    content = skill_path.read_text(encoding="utf-8")
    try:
        metadata, _ = parse_frontmatter(content)
    except ParseError as exc:
        return [str(exc)]
    canonical_dir = Path(str(metadata.get("name", "")))
    return validate_metadata(metadata, canonical_dir)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    skill_path = Path(args[0]) if args else Path("SKILL.md")
    errors = validate_skill_file(skill_path)
    if errors:
        for error in errors:
            print(f"{skill_path}: {error}", file=sys.stderr)
        return 1
    print(f"Valid skill: {skill_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

