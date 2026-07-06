# Project Roadmap

Last updated: 2026-07-06

This roadmap turns the current project review into work items. It uses public facts only. Do not add local paths, cookies, account names, tokens, screenshots with personal data, or machine-specific setup details.

## Current Position

`xiaohongshu-skill` is a Python Playwright CLI and AgentSkill for Xiaohongshu. It already covers search, note detail, user pages, explore feed, publish flows, comments, likes, collects, templates, strategy state, and SOP commands.

Public GitHub data checked on 2026-07-06:

| Project | Stars | Main lesson |
| --- | ---: | --- |
| `xpzouying/xiaohongshu-mcp` | 14.5k | Strong install paths, demos, MCP client guides, Docker release, FAQ, and community proof |
| `DeliciousBuding/xiaohongshu-skill` | 32 | Smaller but broader CLI surface, with Skill-first packaging and Python automation |
| `ibreez3/xiaohongshu-skill` | 20 | Confirms demand for Skill-style packaging |

## Borrow From Mature Projects

### Product entry points

- Add a first-screen README choice: `Skill install`, `CLI install`, `Docker`, and `ClawHub`.
- Replace TODO demo comments with short GIFs or linked GitHub user-attachment videos for login, search, publish, and interaction.
- Add copy-paste examples for Claude Code, Codex, OpenClaw, Cursor, Cline, and n8n.
- Add a small FAQ for login expiry, xsec_token freshness, account conflicts, captcha, and headed mode.

### Development

- Keep `python -m pytest -q` under one second for unit tests.
- Keep `python -m ruff check scripts tests` clean.
- Keep browser tests behind explicit `live` or `e2e` markers so CI never touches a real account by accident.
- Keep `make.ps1` as the Windows entry for `test`, `lint`, `check`, `docs-check`, `live`, `site`, and `contracts`.

### Testing

- Unit tests should mock Playwright and never wait through production humanized delays.
- Live tests must require explicit environment variables such as `XHS_LIVE_TEST=1`.
- Keep selector contract tests for publish, search, comments, interaction, captcha, and login. They should validate fallback order without opening Xiaohongshu.
- Keep CLI JSON output contracts in `scripts/output_contracts.py` so agents can rely on stable fields.

### Browser automation

- Keep persistent browser profiles per account. Shared sessions cause account conflicts.
- Use `--profile` for separate account sessions. `profiles` lists local profiles. Later work can add `add`, `switch`, and `set-default`.
- Prefer page objects for search, publish, comments, and profile flows. Shared helpers should cover navigation, toast parsing, captcha detection, and retries.
- Document every selector group in `scripts/selectors.py` with the page it belongs to and the fallback order.

### Safety and platform limits

- Treat anti-bot work as reliability and account-safety work, not as a promise to bypass platform controls.
- Keep navigation pacing, interaction pacing, burst cooldowns, captcha detection, and `auto_publish=false` defaults.
- Add per-action daily limits to the CLI, not only the strategy helpers.
- Stop a run when the site asks for verification. Return a structured `CaptchaError` and tell the user to continue in headed mode.

### Documentation

- Keep `README.md` short enough to sell the project and get a user to the first command.
- Move long command details to `docs/API.md`.
- Add `docs/INSTALL.md` for Windows, macOS, Linux, Docker, and WSL.
- Add `docs/INTEGRATIONS.md` for Claude Code, Codex, OpenClaw, Cursor, Cline, n8n, and ClawHub.
- Add `docs/SECURITY.md` for cookies, local browser profiles, screenshots, logs, and issue-report redaction.

### GitHub Pages, SEO, and GEO

- Build a static landing page with one job: explain what the Skill does and get the user to install it.
- Use a plain title: `Xiaohongshu Skill for AI Agents`.
- Add a short meta description that includes `Xiaohongshu`, `RedNote`, `小红书`, `AI agent`, `Playwright`, and `AgentSkill`.
- Add structured data with `SoftwareApplication`, install commands, license, repository URL, and supported OS names.
- Publish examples as crawlable pages, not only images inside README.
- Add `llms.txt` with install commands, command list, safety rules, and links to API docs.

## Priority Plan

| Priority | Work item | Acceptance check |
| --- | --- | --- |
| P0 | Fast test harness and lint-clean tree | `python -m pytest -q` and `python -m ruff check scripts tests` pass |
| P0 | README install matrix | New users can choose Skill, CLI, Docker, or ClawHub in under one minute |
| P0 | Public privacy guard | Docs and examples contain no local user paths, cookies, tokens, account names, or private screenshots |
| P1 | Integration docs | Claude Code, Codex, OpenClaw, Cursor, Cline, n8n, and ClawHub each have a tested setup block |
| P1 | Demo assets | Login, search, publish, and interaction have short public demos |
| P1 | E2E test marker | Live account tests require `XHS_LIVE_TEST=1` |
| P2 | GitHub Pages site | Landing page, SEO tags, structured data, and `llms.txt` are published |
| P2 | Account profiles | `--profile` and `profiles` are documented and covered by unit tests |

## Public Privacy Rule

Before committing public docs or examples, run:

```bash
python -m scripts.docs_check
```

Allowed path examples must be generic. Use `/path/to/file`, `C:\path\to\file`, or `~/.xiaohongshu/` when a public setup needs a path.
