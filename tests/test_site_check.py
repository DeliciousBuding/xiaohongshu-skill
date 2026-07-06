"""
GitHub Pages SEO/GEO checks.
"""

from pathlib import Path

from scripts.site_check import check_site, check_site_dir


def test_site_check_passes_current_site():
    """The checked-in Pages site should include required SEO/GEO files."""
    assert check_site_dir(Path("site")) == []


def test_site_check_flags_missing_required_files(tmp_path: Path):
    """Missing crawl files should be reported."""
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    (site_dir / "index.html").write_text("<html><head><title>x</title></head></html>", encoding="utf-8")

    findings = check_site_dir(site_dir)

    assert any("llms.txt" in finding for finding in findings)
    assert any("robots.txt" in finding for finding in findings)
    assert any("sitemap.xml" in finding for finding in findings)


def test_site_check_flags_missing_json_ld(tmp_path: Path):
    """Index page should include structured data for crawlers."""
    html = """<!doctype html>
<html>
  <head>
    <title>Xiaohongshu Skill for AI Agents</title>
    <meta name="description" content="Xiaohongshu RedNote AI agent Playwright AgentSkill">
    <link rel="canonical" href="https://example.com/">
  </head>
  <body></body>
</html>
"""

    findings = check_site(html)

    assert any("SoftwareApplication" in finding for finding in findings)


def test_site_check_requires_demo_page(tmp_path: Path):
    """The Pages site should expose a crawlable demo page."""
    site_dir = tmp_path / "site"
    site_dir.mkdir()
    for name in ("index.html", "llms.txt", "robots.txt", "sitemap.xml", "og-image.svg"):
        (site_dir / name).write_text("ok", encoding="utf-8")

    findings = check_site_dir(site_dir)

    assert any("demo.html" in finding for finding in findings)
