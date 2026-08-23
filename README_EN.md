# xiaohongshu-skill

[![CI](https://github.com/DeliciousBuding/xiaohongshu-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/DeliciousBuding/xiaohongshu-skill/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/DeliciousBuding/xiaohongshu-skill)](https://github.com/DeliciousBuding/xiaohongshu-skill/releases)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue)](LICENSE)

A Xiaohongshu browser toolkit for AI agents and command-line users. The Python Playwright implementation supports discovery, note details, feeds, login, publishing, comments, likes, collections, templates, strategy state, and SOP workflows.

- JSON output is the default interface for agents and automation tools.
- Named profiles isolate browser sessions and local account state.
- Publish results distinguish confirmed, unconfirmed submission, and failure.
- Default tests never contact Xiaohongshu; live browser tests are opt-in.

> This project controls real accounts. Obtain explicit user confirmation before publishing, commenting, replying, liking, or collecting. Stop automation when a captcha or security-verification page appears.

中文文档：[README.md](README.md)

## Capabilities

| Area | Commands | Changes account state |
| --- | --- | --- |
| Login and accounts | `qrcode`, `check-login`, `profiles`, `logout` | `logout` removes local state |
| Discovery | `search`, `feed`, `user`, `me`, `explore` | No |
| Publishing | `publish`, `publish-video`, `publish-md`, `publish-longform` | Yes |
| Interaction | `comment`, `reply`, `reply-notification`, `like`, `collect`, `unlike`, `uncollect` | Yes |
| Content tools | `template`, `strategy-*`, `sop` | Depends on the SOP |
| Development | `selectors`, `contracts` | No |

See [CLI reference](docs/API.md) for complete arguments.

## Install

### ClawHub

```bash
clawhub install xiaohongshu-skill
```

### Agent Skills CLI

```bash
npx skills add DeliciousBuding/xiaohongshu-skill
```

### Reproducible local environment

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
uv sync --frozen --no-dev
uv run playwright install chromium
```

Development environment:

```bash
uv sync --frozen --group dev
uv run python -m scripts.quality check
```

### Global CLI

```bash
pip install git+https://github.com/DeliciousBuding/xiaohongshu-skill.git
playwright install chromium
xiaohongshu-skill --help
```

### Docker

```bash
docker compose build
docker compose run --rm xiaohongshu qrcode --headless=false
```

See [installation guide](docs/INSTALL.md) for system and platform details.

## Quick start

### 1. Login

```bash
uv run python -m scripts qrcode --headless=false
uv run python -m scripts check-login
```

### 2. Search and read

```bash
uv run python -m scripts search "coffee" --limit=5
uv run python -m scripts feed <feed_id> <xsec_token>
uv run python -m scripts user <user_id> <xsec_token>
uv run python -m scripts explore --limit=10
```

Obtain `feed_id`, `user_id`, and `xsec_token` from current-session results. Do not retain security parameters for later sessions.

### 3. Prepare a post

Publishing commands fill the form and stop before submission by default:

```bash
uv run python -m scripts publish \
  --title="Weekend coffee notes" \
  --content="Post body" \
  --images="/path/to/1.jpg,/path/to/2.jpg"
```

After checking the title, body, media, account, and visibility, submit with:

```bash
uv run python -m scripts publish ... --auto-publish
```

Submission states:

| Status | Meaning | Next action |
| --- | --- | --- |
| `confirmed` | A trusted success signal was observed | Record as successful |
| `submitted_unconfirmed` | Submission was clicked without a success signal | Review manually; do not retry automatically |
| `failed` | Submission did not complete or a failure signal appeared | Inspect the error before retrying |
| `ready` | The form is ready and has not been submitted | Review and decide whether to submit |

### 4. Multiple accounts

```bash
uv run python -m scripts --profile brand-a qrcode --headless=false
uv run python -m scripts --profile brand-a search "coffee"
uv run python -m scripts profiles
```

Each profile has separate browser state, cookie backup, and session metadata. `XHS_FP_SEED` can override the stable fingerprint seed for one process.

## Safety and limits

- Keep the built-in navigation intervals and interaction cooldowns enabled.
- Do not run high-frequency bulk scraping or bulk interactions.
- Stop on captcha, login, or security-verification pages.
- Do not attach account data, cookies, complete security parameters, or QR codes to issues and logs.
- The Docker image runs as a non-root user and excludes local state from its build context.
- Set `XHS_ALLOW_NO_SANDBOX=true` only in an isolated environment that explicitly requires Chromium sandbox to be disabled.

See [security guide](docs/SECURITY.md).

## Engineering documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Installation](docs/INSTALL.md)
- [CLI API](docs/API.md)
- [Integrations](docs/INTEGRATIONS.md)
- [Security](docs/SECURITY.md)
- [Reference implementations](docs/REFERENCE.md)
- [Releasing](docs/RELEASING.md)
- [Roadmap](docs/ROADMAP.md)

Default quality gate:

```bash
uv run python -m scripts.quality check
```

CI also tests Python 3.10, 3.11, and 3.12, builds wheel and source distributions, and verifies the Docker image.

## Sources and license

Original repository code is distributed under the [Apache License 2.0](LICENSE). Some browser behavior was studied or adapted from the Apache-2.0 project `xpzouying/xiaohongshu-mcp`; see [third-party notices](THIRD_PARTY_NOTICES.md).

This project is not affiliated with or endorsed by Xiaohongshu. Users are responsible for applicable platform rules, laws, and account safety.
