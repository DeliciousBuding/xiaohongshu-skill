# GitHub Pages

Last updated: 2026-07-07

The Pages site should be a product page for users who do not read GitHub READMEs first.

## Page Goals

- Explain what the Skill does in one screen.
- Show install choices: ClawHub, Skill folder, CLI, Docker.
- Link to the skills.sh page and install command.
- Link to docs for install, integrations, command reference, safety, and roadmap.
- Give search engines a clear title, description, and structured data.
- Give AI crawlers `llms.txt` and `llms-full.txt` files with commands, aliases, safety rules, and public doc links.

## Recommended Structure

```text
site/
  index.html
  demo.html
  llms.txt
  llms-full.txt
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
- skills.sh
- Claude Code
- Codex
- OpenClaw

## Structured Data

Use `SoftwareApplication` JSON-LD. Include:

- `name`: `xiaohongshu-skill`
- `applicationCategory`: `DeveloperApplication`
- `applicationSubCategory`: `AgentSkill`
- `operatingSystem`: `Windows, macOS, Linux`
- `programmingLanguage`: `Python`
- `license`: `MIT`
- `codeRepository`: `https://github.com/DeliciousBuding/xiaohongshu-skill`
- `sameAs`: GitHub, skills.sh, and `llms.txt`

## LLM Text Files

The `llms.txt` and `llms-full.txt` files should include:

- Short project summary.
- Search aliases such as Xiaohongshu, RedNote, 小红书, xhs, and RED.
- Install commands.
- Read-only commands.
- Write commands and confirmation rule.
- Links to public demo JSON.
- Links to `docs/API.md`, `docs/INSTALL.md`, `docs/INTEGRATIONS.md`, and `docs/SECURITY.md`.

## Launch Checklist

- Page contains no private screenshots or local paths.
- All links point to public repository paths.
- `python -m scripts.quality docs-check` passes.
- `robots.txt` allows the static site.
- `sitemap.xml` lists the landing page, demo page, `llms.txt`, and `llms-full.txt`.
