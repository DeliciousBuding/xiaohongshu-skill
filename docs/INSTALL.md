# Install

This guide covers the local CLI, Agent Skill installation, Docker, account profiles, and development setup.

## Requirements

- Python 3.10, 3.11, or 3.12
- `uv` for the reproducible local environment
- Playwright Chromium
- A Xiaohongshu account that can use the web interface

Use a dedicated test account before relying on any write command.

## Local CLI

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
uv sync --frozen --no-dev
uv run playwright install chromium
```

On Linux, install browser system dependencies with:

```bash
uv run playwright install --with-deps chromium
```

Login and verify:

```bash
uv run python -m scripts qrcode --headless=false
uv run python -m scripts check-login
uv run python -m scripts search "咖啡" --limit=3
```

## Global CLI

```bash
pip install git+https://github.com/DeliciousBuding/xiaohongshu-skill.git
playwright install chromium
xiaohongshu-skill qrcode --headless=false
xiaohongshu-skill search "咖啡" --limit=3
```

The cloned `uv.lock` path is recommended for development and reproducible local runs. The global Git installation is a convenience path.

## Agent Skill

Recommended cross-platform installation:

```bash
npx skills add DeliciousBuding/xiaohongshu-skill
```

ClawHub:

```bash
clawhub install xiaohongshu-skill
```

Manual folders:

```text
Claude Code: ~/.claude/skills/xiaohongshu-skill
Codex/Cursor shared view: ~/.agents/skills/xiaohongshu-skill
```

After cloning into a Skill folder, install Python dependencies from that folder and restart the agent host if it does not reload Skill metadata automatically.

## Docker

```bash
docker compose build
docker compose run --rm xiaohongshu qrcode --headless=false
docker compose run --rm xiaohongshu search "咖啡" --limit=3
```

The image runs as a non-root user. The compose file mounts the host account directory and `data/` into writable locations. Local environment files, repository metadata, tests, and account state are excluded from the build context.

Headed browser mode inside Docker needs a desktop display or VNC. Local CLI mode is usually simpler for QR login.

## Account profiles

Use `--profile` to isolate multiple accounts:

```bash
uv run python -m scripts --profile brand-a qrcode --headless=false
uv run python -m scripts --profile brand-a check-login
uv run python -m scripts --profile brand-a search "咖啡"
uv run python -m scripts profiles
```

Profile names may contain letters, numbers, dots, underscores, and dashes. Do not point two simultaneous processes at the same profile.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `XHS_PROFILE` | Default named profile |
| `XHS_FP_SEED` | Process-local fingerprint seed override |
| `XHS_ALLOW_NO_SANDBOX` | Explicitly disable Chromium sandbox in an isolated environment |
| `XHS_LIVE_TEST` | Enable opt-in live tests |
| `XHS_LIVE_KEYWORD` | Keyword for the read-only live smoke test |
| `XHS_LIVE_HEADLESS` | Headless mode for the live smoke test |

`XHS_ALLOW_NO_SANDBOX` is disabled by default and should not be set for normal desktop use.

## Development setup

```bash
uv sync --frozen --group dev
uv run python -m scripts.quality check
```

The quality command runs documentation checks, lint, unit tests, contract smoke tests, and Agent Skills validation.

Targeted commands:

```bash
uv run pytest -q
uv run ruff check scripts tests
uv run python -m scripts.quality contracts
uv run python -m scripts.quality skill
```

## Common problems

| Problem | Action |
| --- | --- |
| QR login does not complete | Use `--headless=false` and finish the flow in the visible browser |
| Search returns no structured data | Check login state, then retry with a fresh session |
| Captcha or security verification appears | Stop automation and complete the step manually |
| Docker cannot display the browser | Use local CLI login or configure a display server |
| Publish returns `submitted_unconfirmed` | Review the creator page manually and do not retry automatically |
