"""
Documentation checks.
"""

from pathlib import Path

from scripts.docs_check import iter_public_files, scan_files


def test_docs_check_flags_private_paths_and_ai_writing_patterns(tmp_path: Path):
    doc = tmp_path / "bad.md"
    doc.write_text(
        "Local path: D:\\Code\\secret\\file.txt\n"
        "This workflow is seamless.\n",
        encoding="utf-8",
    )

    findings = scan_files([doc])

    assert ("bad.md", 1, "privacy") in [
        (finding.path.name, finding.line, finding.kind) for finding in findings
    ]
    assert ("bad.md", 2, "writing") in [
        (finding.path.name, finding.line, finding.kind) for finding in findings
    ]


def test_docs_check_allows_public_placeholders(tmp_path: Path):
    doc = tmp_path / "good.md"
    doc.write_text(
        "Use /path/to/file or C:\\path\\to\\file in public examples.\n",
        encoding="utf-8",
    )

    assert scan_files([doc]) == []


def test_docs_check_scans_pages_assets(tmp_path: Path):
    html = tmp_path / "index.html"
    txt = tmp_path / "llms.txt"
    xml = tmp_path / "sitemap.xml"
    svg = tmp_path / "og-image.svg"
    for path in (html, txt, xml, svg):
        path.write_text("ok", encoding="utf-8")

    names = {path.name for path in iter_public_files([tmp_path])}

    assert {"index.html", "llms.txt", "sitemap.xml", "og-image.svg"} <= names


def test_docs_check_scans_public_json_assets(tmp_path: Path):
    """Public JSON demo files should be checked for private data."""
    doc = tmp_path / "demo.json"
    doc.write_text('{"path": "D:\\\\Code\\\\private\\\\image.jpg"}', encoding="utf-8")

    findings = scan_files(iter_public_files([tmp_path]))

    assert any(finding.path.name == "demo.json" and finding.kind == "privacy" for finding in findings)
