"""
Static checks for the GitHub Pages site.
"""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path


REQUIRED_SITE_FILES = ("index.html", "demo.html", "llms.txt", "robots.txt", "sitemap.xml", "og-image.svg")
REQUIRED_DESCRIPTION_TERMS = ("Xiaohongshu", "RedNote", "AI agent", "Playwright")


class SiteHeadParser(HTMLParser):
    """Small HTML head parser for SEO checks."""

    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.json_ld: list[str] = []
        self._in_json_ld = False
        self._json_ld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs_dict.get("name", "").lower() == "description":
            self.description = attrs_dict.get("content", "")
        elif tag == "link" and attrs_dict.get("rel", "").lower() == "canonical":
            self.canonical = attrs_dict.get("href", "")
        elif tag == "script" and attrs_dict.get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._in_json_ld:
            self._in_json_ld = False
            self.json_ld.append("".join(self._json_ld_parts).strip())

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        if self._in_json_ld:
            self._json_ld_parts.append(data)


def check_site(html: str) -> list[str]:
    """Return SEO/GEO findings for index.html content."""
    parser = SiteHeadParser()
    parser.feed(html)

    findings: list[str] = []
    title = parser.title.strip()
    if title != "Xiaohongshu Skill for AI Agents":
        findings.append("index.html: title should be 'Xiaohongshu Skill for AI Agents'")

    if not parser.description:
        findings.append("index.html: missing meta description")
    else:
        for term in REQUIRED_DESCRIPTION_TERMS:
            if term not in parser.description:
                findings.append(f"index.html: meta description should include {term}")

    if not parser.canonical.startswith("https://"):
        findings.append("index.html: canonical URL should be absolute https")

    if not _has_software_application_json_ld(parser.json_ld):
        findings.append("index.html: missing SoftwareApplication JSON-LD")

    return findings


def check_site_dir(site_dir: Path) -> list[str]:
    """Return findings for a Pages site directory."""
    findings: list[str] = []
    for filename in REQUIRED_SITE_FILES:
        if not (site_dir / filename).is_file():
            findings.append(f"{filename}: missing required Pages file")

    index_path = site_dir / "index.html"
    if index_path.is_file():
        findings.extend(check_site(index_path.read_text(encoding="utf-8")))

    demo_path = site_dir / "demo.html"
    if demo_path.is_file():
        demo_text = demo_path.read_text(encoding="utf-8")
        for required in ("Search JSON", "Publish Draft", "Agent Contracts"):
            if required not in demo_text:
                findings.append(f"demo.html: missing {required}")

    llms_path = site_dir / "llms.txt"
    if llms_path.is_file():
        llms_text = llms_path.read_text(encoding="utf-8")
        for required in ("Install", "Safety", "Docs", "xiaohongshu-skill"):
            if required not in llms_text:
                findings.append(f"llms.txt: missing {required}")

    robots_path = site_dir / "robots.txt"
    if robots_path.is_file():
        robots_text = robots_path.read_text(encoding="utf-8")
        if "Sitemap:" not in robots_text:
            findings.append("robots.txt: missing Sitemap directive")

    sitemap_path = site_dir / "sitemap.xml"
    if sitemap_path.is_file():
        sitemap_text = sitemap_path.read_text(encoding="utf-8")
        if "https://deliciousbuding.github.io/xiaohongshu-skill/" not in sitemap_text:
            findings.append("sitemap.xml: missing Pages canonical URL")
        if "https://deliciousbuding.github.io/xiaohongshu-skill/demo.html" not in sitemap_text:
            findings.append("sitemap.xml: missing demo page URL")

    return findings


def _has_software_application_json_ld(json_ld_blocks: list[str]) -> bool:
    for block in json_ld_blocks:
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "SoftwareApplication":
                return True
    return False


def main() -> int:
    site_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("site")
    findings = check_site_dir(site_dir)
    if findings:
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
