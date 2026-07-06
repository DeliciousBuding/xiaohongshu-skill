# Install

Last updated: 2026-07-06

This guide covers local CLI, Skill, Docker, and platform setup. Use a test account first. Xiaohongshu can ask for manual verification, and the tool will stop when that happens.

## Requirements

- Python 3.10 or newer
- Playwright Chromium
- A Xiaohongshu account that can log in on the web

## Local CLI

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python -m scripts qrcode --headless=false
python -m scripts check-login
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
python -m scripts qrcode --headless=false
python -m scripts check-login
```

For Linux servers, install browser dependencies once:

```bash
playwright install-deps chromium
```

## Global CLI

```bash
pip install git+https://github.com/DeliciousBuding/xiaohongshu-skill.git
playwright install chromium
xiaohongshu-skill qrcode --headless=false
xiaohongshu-skill search "美食" --limit=5
```

## Docker

```bash
docker compose build
docker compose run --rm xiaohongshu qrcode --headless=false
docker compose run --rm xiaohongshu search "美食" --limit=5
```

Headed browser mode inside Docker needs a desktop display or a VNC setup. Use local CLI mode when you need the simplest QR login path.

## Skill Install

Clone the repository into the Skill directory used by your agent, then restart the agent process.

Claude Code:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.claude/skills/xiaohongshu-skill
```

Codex:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.codex/skills/xiaohongshu-skill
```

OpenClaw:

```bash
clawhub install xiaohongshu-skill
```

If ClawHub is unavailable, install the same folder manually:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.openclaw/skills/xiaohongshu-skill
```

## Verify

```bash
python -m scripts check-login
python -m scripts search "咖啡" --limit=3
```

Expected output is JSON. If login is false, run QR login again in headed mode.

## Account Profiles

Use `--profile` when you operate more than one account. Profile names may contain letters, numbers, dot, underscore, and dash.

```bash
python -m scripts --profile brand-a qrcode --headless=false
python -m scripts --profile brand-a check-login
python -m scripts --profile brand-a search "咖啡" --limit=3
python -m scripts profiles
```

The default profile keeps the old path layout. Named profiles use isolated storage under the Xiaohongshu profile root.

## Developer Checks

Optional local switches live in `.env.example`. Copy it to `.env` only for your own machine, and do not commit filled values.

Default checks do not touch Xiaohongshu:

```bash
python -m scripts.docs_check
python -m scripts.site_check
python -m ruff check scripts tests
python -m pytest -q
```

Windows PowerShell:

```powershell
.\make.ps1 check
```

Live browser checks are opt-in:

```bash
XHS_LIVE_TEST=1 python -m pytest tests/live -q -m live
```

PowerShell:

```powershell
$env:XHS_LIVE_TEST='1'; python -m pytest tests/live -q -m live
```

## Common Problems

| Problem | Fix |
| --- | --- |
| Browser opens but QR login does not complete | Use `--headless=false` and scan in the visible browser |
| Search returns no structured data | Log in again and retry with a fresh browser session |
| Captcha or verification page appears | Stop the run, wait, then continue in headed mode |
| Docker cannot show the browser | Use local CLI for login, or configure a display for the container |
