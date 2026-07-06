# GitHub Pages

Last updated: 2026-07-06

The Pages site should be a product page for users who do not read GitHub READMEs first.

## Page Goals

- Explain what the Skill does in one screen.
- Show install choices: ClawHub, Skill folder, CLI, Docker.
- Link to docs for install, integrations, command reference, safety, and roadmap.
- Give search engines a clear title, description, and structured data.
- Give AI crawlers a short `llms.txt` file with commands and safety rules.

## Recommended Structure

```text
site/
  index.html
  demo.html
  llms.txt
  robots.txt
  sitemap.xml
```

## SEO Fields

Use this title:

```html
<title>Xiaohongshu Skill for AI Agents</title>
```

Use this description:

```html
<meta name="description" content="Xiaohongshu and RedNote Skill for AI agents. Search notes, read details, publish drafts, and run browser automation with Python Playwright.">
```

Use keywords naturally in visible text:

- Xiaohongshu
- RedNote
- 小红书
- AI agent
- AgentSkill
- Playwright
- ClawHub

## Structured Data

Use `SoftwareApplication` JSON-LD. Include:

- `name`: `xiaohongshu-skill`
- `applicationCategory`: `DeveloperApplication`
- `operatingSystem`: `Windows, macOS, Linux`
- `programmingLanguage`: `Python`
- `license`: `MIT`
- `codeRepository`: `https://github.com/DeliciousBuding/xiaohongshu-skill`

## llms.txt

The file should include:

- Short project summary.
- Install commands.
- Read-only commands.
- Write commands and confirmation rule.
- Links to public demo JSON.
- Links to `docs/API.md`, `docs/INSTALL.md`, `docs/INTEGRATIONS.md`, and `docs/SECURITY.md`.

## Launch Checklist

- Page contains no private screenshots or local paths.
- All links point to public repository paths.
- `python -m scripts.docs_check` passes.
- `python -m scripts.site_check` passes.
- `robots.txt` allows the static site.
- `sitemap.xml` lists the landing page, demo page, and `llms.txt`.
