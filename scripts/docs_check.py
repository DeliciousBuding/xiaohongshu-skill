"""
Public documentation checks.

The checks are intentionally small. They catch private local paths, common
secret shapes, and a short list of writing patterns we do not want in public
project docs.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_TARGETS = [
    "README.md",
    "README_EN.md",
    "SKILL.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "docs",
    "examples",
    ".github",
    "site",
]

PUBLIC_SUFFIXES = {".md", ".html", ".txt", ".xml", ".svg", ".json"}

PRIVACY_PATTERNS = [
    re.compile(r"C:\\+Users\\+", re.IGNORECASE),
    re.compile(r"D:\\+Code\\+", re.IGNORECASE),
    re.compile(r"/Users/[^/\s]+"),
    re.compile(r"cookies?\.json", re.IGNORECASE),
    re.compile(r"browser-data", re.IGNORECASE),
    re.compile(r"\.secret", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"手机号"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
]

WRITING_PATTERNS = [
    re.compile(r"—"),
    re.compile(r"\bdelve\b", re.IGNORECASE),
    re.compile(r"\bleverage\b", re.IGNORECASE),
    re.compile(r"\brobust\b", re.IGNORECASE),
    re.compile(r"\bcomprehensive\b", re.IGNORECASE),
    re.compile(r"\bseamless\b", re.IGNORECASE),
    re.compile(r"\bgame[- ]changer\b", re.IGNORECASE),
    re.compile(r"\bimpactful\b", re.IGNORECASE),
    re.compile(r"\bactionable\b", re.IGNORECASE),
    re.compile(r"\bworth noting\b", re.IGNORECASE),
    re.compile(r"\bimportant to note\b", re.IGNORECASE),
    re.compile(r"\bat its core\b", re.IGNORECASE),
    re.compile(r"\bbest practices\b", re.IGNORECASE),
    re.compile(r"\bserves as\b", re.IGNORECASE),
    re.compile(r"落地|闭环|抓手|赋能|沉淀|证据链|证据矩阵"),
]


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    kind: str
    text: str


def iter_public_files(targets: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if not target.exists():
            continue
        if target.is_file() and target.suffix.lower() in PUBLIC_SUFFIXES:
            files.append(target)
        elif target.is_dir():
            files.extend(
                path for path in target.rglob("*")
                if path.is_file()
                and path.suffix.lower() in PUBLIC_SUFFIXES
                and ".git" not in path.parts
                and "__pycache__" not in path.parts
            )
    return sorted(set(files))


def _matches(line_text: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(line_text) for pattern in patterns)


def scan_files(files: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

        for index, line_text in enumerate(lines, start=1):
            if _matches(line_text, PRIVACY_PATTERNS):
                findings.append(Finding(path=path, line=index, kind="privacy", text=line_text.strip()))
            if _matches(line_text, WRITING_PATTERNS):
                findings.append(Finding(path=path, line=index, kind="writing", text=line_text.strip()))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check public docs for private data and writing issues.")
    parser.add_argument("paths", nargs="*", default=DEFAULT_TARGETS, help="Files or directories to scan.")
    args = parser.parse_args(argv)

    files = iter_public_files([Path(path) for path in args.paths])
    findings = scan_files(files)
    for finding in findings:
        print(f"{finding.path}:{finding.line}: {finding.kind}: {finding.text}")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
