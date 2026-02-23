# xiaohongshu-skill

A Claude Code Skill for interacting with [Xiaohongshu](https://www.xiaohongshu.com) (小红书/RED) — China's popular lifestyle and social commerce platform.

Built with Python + Playwright, this skill enables searching posts, extracting content, viewing user profiles, and managing login sessions through browser automation.

## Features

- **QR Code Login** — Scan to authenticate, cookies persist across sessions
- **Search** — Full-text search with filters (sort, type, time, scope, location)
- **Post Detail** — Extract title, body, images, comments, and engagement metrics
- **User Profile** — Get user info, follower counts, and note listings
- **Anti-Bot Protection** — Built-in rate limiting, captcha detection, and human-like delays

## Installation

```bash
# Clone the repository
git clone https://github.com/perlica/xiaohongshu-skill.git
cd xiaohongshu-skill

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# On Linux/WSL, also install system dependencies
playwright install-deps chromium
```

## Usage

### Login (required first time)

```bash
# Opens browser for QR code scanning
python -m scripts qrcode --headless=false

# Verify login status
python -m scripts check-login
```

### Search

```bash
# Basic search
python -m scripts search "美食推荐" --limit=5

# With filters
python -m scripts search "旅行攻略" --sort-by=最新 --note-type=图文 --limit=10
```

### Post Detail

```bash
# Use id and xsec_token from search results
python -m scripts feed <feed_id> <xsec_token>

# With comments
python -m scripts feed <feed_id> <xsec_token> --load-comments
```

### User Profile

```bash
python -m scripts user <user_id>
```

## Architecture

```
scripts/
├── client.py    # Playwright browser wrapper with rate limiting & captcha detection
├── login.py     # QR code authentication flow
├── search.py    # Search with filter support
├── feed.py      # Post detail & comment extraction
├── user.py      # User profile & note listing
└── __main__.py  # CLI entry point
```

### How It Works

1. Launches headless Chromium via Playwright
2. Loads saved cookies for authentication
3. Navigates to Xiaohongshu pages
4. Extracts data from `window.__INITIAL_STATE__` (Vue SSR state)
5. Returns structured JSON results

### Anti-Bot Measures

Xiaohongshu has aggressive anti-scraping. This skill handles it with:

- **Request throttling**: 3-6s random delay between navigations
- **Burst protection**: 10s cooldown after every 5 consecutive requests
- **Captcha detection**: Monitors for security verification redirects
- **Session management**: Cookie persistence and status checking

## Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 11 | Fully supported | Primary development platform |
| WSL2 (Ubuntu) | Supported | Headless works out of box; headed needs WSLg |
| Linux Server | Supported | Headless only; QR code saved as image file |
| macOS | Should work | Not tested |

## Requirements

- Python 3.10+
- Playwright >= 1.40.0

## As a Claude Code Skill

This project follows the [Agent Skills Specification](https://agentskills.io/specification). To use it as a Claude Code skill, add the `SKILL.md` file to your Claude Code configuration.

## License

MIT

## Credits

Inspired by [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (Go version).
