---
name: xiaohongshu
description: Use this skill when the user wants to interact with Xiaohongshu (小红书, RED). This includes searching for posts, getting post details, viewing user profiles, logging in via QR code, and extracting content from the platform. Activate this skill when the user mentions xiaohongshu, 小红书, RED, or wants to scrape/browse Chinese social media content.
---

# Xiaohongshu (小红书) Skill

A Python Playwright-based tool for interacting with Xiaohongshu (小红书/RED), the popular Chinese social media platform.

## How It Works

This skill controls a headless Chromium browser via Playwright, navigates to Xiaohongshu pages, and extracts structured data from `window.__INITIAL_STATE__` (Vue SSR state). This approach avoids unstable API reverse-engineering and works reliably with cookie-based authentication.

## Prerequisites

Before first use, ensure dependencies are installed:

```bash
pip install playwright>=1.40.0
playwright install chromium
```

On Linux/WSL, also run:
```bash
playwright install-deps chromium
```

## Quick Start

All commands are run from the skill's root directory.

### 1. Login (Required First)

```bash
# Opens a browser window with QR code for WeChat/Xiaohongshu scan
python -m scripts qrcode --headless=false

# Check if login is still valid
python -m scripts check-login
```

The QR code image is saved to `data/qrcode.png` for headless environments (e.g., send via Telegram).

### 2. Search

```bash
# Basic search
python -m scripts search "关键词"

# With filters
python -m scripts search "美食" --sort-by=最新 --note-type=图文 --limit=10
```

**Filter options:**
- `--sort-by`: 综合, 最新, 最多点赞, 最多评论, 最多收藏
- `--note-type`: 不限, 视频, 图文
- `--publish-time`: 不限, 一天内, 一周内, 半年内
- `--search-scope`: 不限, 已看过, 未看过, 已关注
- `--location`: 不限, 同城, 附近

### 3. Post Detail (Feed)

```bash
# Get post content (use id and xsec_token from search results)
python -m scripts feed <feed_id> <xsec_token>

# With comments
python -m scripts feed <feed_id> <xsec_token> --load-comments --max-comments=20
```

### 4. User Profile

```bash
python -m scripts user <user_id> [xsec_token]
```

## Data Extraction Paths

| Data Type | JavaScript Path |
|-----------|----------------|
| Search Results | `window.__INITIAL_STATE__.search.feeds` |
| Post Detail | `window.__INITIAL_STATE__.note.noteDetailMap` |
| User Profile | `window.__INITIAL_STATE__.user.userPageData` |
| User Notes | `window.__INITIAL_STATE__.user.notes` |

**Vue Ref handling:** Always unwrap via `.value` or `._value`:
```javascript
const data = obj.value !== undefined ? obj.value : obj._value;
```

## Anti-Scraping Protection

This skill includes built-in protection against Xiaohongshu's anti-bot measures:

- **Rate limiting**: Automatic 3-6s delay between page navigations, 10s cooldown every 5 requests
- **Captcha detection**: Automatically detects security verification redirects and raises `CaptchaError` with actionable advice
- **Human-like behavior**: Randomized delays, scroll patterns, and user-agent spoofing

**If you hit a captcha:**
1. Wait a few minutes before retrying
2. Run `python -m scripts qrcode --headless=false` to manually pass verification
3. Re-scan QR code if cookies are invalidated

## Output Format

All commands output JSON to stdout. Example search result:
```json
{
  "id": "abc123",
  "xsec_token": "ABxyz...",
  "title": "Post title",
  "type": "normal",
  "user": "Username",
  "user_id": "user123",
  "liked_count": "1234",
  "collected_count": "567",
  "comment_count": "89"
}
```

## File Structure

```
xiaohongshu-skill/
├── SKILL.md              # This file (skill specification)
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── data/                 # Runtime data (QR codes, debug output)
└── scripts/              # Core Python modules
    ├── __init__.py
    ├── __main__.py       # CLI entry point
    ├── client.py         # Browser client (Playwright wrapper)
    ├── login.py          # QR code login flow
    ├── search.py         # Search with filters
    ├── feed.py           # Post detail extraction
    └── user.py           # User profile extraction
```

## Cross-Platform Notes

| Environment | Headless | Headed (QR Login) | Notes |
|-------------|----------|-------------------|-------|
| Windows | Works | Works | Primary dev environment |
| WSL2 (Win11) | Works | Works via WSLg | Need `playwright install-deps` |
| Linux Server | Works | N/A | Use headless QR + send image |

## Important Caveats

1. **Cookie expiry**: Cookies expire periodically; re-login when `check-login` returns false
2. **Rate limits**: Excessive scraping triggers captchas; use built-in throttling
3. **xsec_token**: Tokens are session-bound; always use fresh tokens from search/user results
4. **Educational use only**: Respect Xiaohongshu's ToS; this tool is for learning purposes
