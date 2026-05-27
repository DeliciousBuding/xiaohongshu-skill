# xiaohongshu-skill

Xiaohongshu (RED) AI Agent toolkit. Search. Post. Engage. One command does it all.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/DeliciousBuding/xiaohongshu-skill?style=social)](https://github.com/DeliciousBuding/xiaohongshu-skill)
[![Version](https://img.shields.io/badge/version-v1.2.0-blue)](https://github.com/DeliciousBuding/xiaohongshu-skill/releases)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ClawHub](https://img.shields.io/badge/ClawHub-download-orange)](https://clawhub.com)

Python + Playwright browser automation. Opens pages, pulls structured data from `window.__INITIAL_STATE__`, and spits out clean JSON. `SKILL.md` follows the [AgentSkills](https://agentskills.io) open spec. Compatible with Claude Code / OpenClaw / Codex / Hermes Agent — any platform that supports the AgentSkills spec.

## What it does

<!-- TODO: record search demo GIF -->
**Search.** Full-text keyword search with every filter you need — sort order, note type, time range, scope, location.
<!-- TODO: record publishing demo GIF -->
**Post.** Images, video, Markdown-to-image, long-form. Schedule or publish right now.
<!-- TODO: record engagement demo GIF -->
**Engage.** Comment, reply, like, bookmark. Human-like delays baked in so you stay under the radar.
<!-- TODO: record operations demo GIF -->
**Automate.** Writing templates for instant drafts. Strategy tracker with daily quotas. SOP workflows on autopilot.

## Install

```bash
# 1. Install
pip install git+https://github.com/DeliciousBuding/xiaohongshu-skill.git

# 2. Install browser (one-time, ~300MB)
playwright install chromium
# Linux/WSL: playwright install-deps chromium

# 3. QR login (one-time, cookies saved automatically)
xiaohongshu-skill qrcode --headless=false

# 4. Go
xiaohongshu-skill search "hotpot"
xiaohongshu-skill check-login
```

After install, the `xiaohongshu-skill` command is available globally.

### Docker (optional)

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
docker compose run --rm xiaohongshu qrcode --headless=false
```

Builds locally from the included Dockerfile. No external images.

## Feature deep dive

### Search notes

```bash
xiaohongshu-skill search "travel guide" --sort-by=最新 --note-type=图文 --limit=10
```

| Parameter | Options |
|-----------|---------|
| `--sort-by` | 综合 / 最新 / 最多点赞 / 最多评论 / 最多收藏 |
| `--note-type` | 不限 / 视频 / 图文 |
| `--publish-time` | 不限 / 一天内 / 一周内 / 半年内 |
| `--search-scope` | 不限 / 已看过 / 未看过 / 已关注 |
| `--location` | 不限 / 同城 / 附近 |

### Post details & user profiles

```bash
# Grab id and xsec_token from search results
xiaohongshu-skill feed <id> <xsec_token>
xiaohongshu-skill feed <id> <xsec_token> --load-comments --max-comments=20
# User profile
xiaohongshu-skill user <user_id> [xsec_token]
xiaohongshu-skill me
```

### Comments & replies

```bash
xiaohongshu-skill comment <id> <token> --content="写得真好"
xiaohongshu-skill reply <id> <token> --comment-id=<cid> --reply-user-id=<uid> --content="感谢"
xiaohongshu-skill reply-notification --content="谢谢" --index=0  # Reply from notifications page — safer
```

### Like & bookmark

```bash
xiaohongshu-skill like <id> <token>
xiaohongshu-skill unlike <id> <token>
xiaohongshu-skill collect <id> <token>
xiaohongshu-skill uncollect <id> <token>
```

### Explore feed & publishing

```bash
xiaohongshu-skill explore --limit=20

# Image-text post (stops at publish button by default; add --auto-publish to go live)
xiaohongshu-skill publish --title="标题" --content="正文" \
  --images="a.jpg,b.jpg" --tags="旅行,美食"

# Video / Markdown-to-image / long-form / scheduled publishing
xiaohongshu-skill publish-video --title="t" --content="c" --video="v.mp4" --tags="vlog"
xiaohongshu-skill publish-md --title="技术文" --file=article.md --width=1080
xiaohongshu-skill publish-longform --title="标题" --content="正文..."
xiaohongshu-skill publish --title="预告" --content="..." --images="img.jpg" --schedule-time="2025-03-01 12:00"
```

### Writing templates & content strategy

```bash
xiaohongshu-skill template --topic="美食探店"
xiaohongshu-skill template --topic="学习方法" --type=长文
# Output: title suggestions + content outline + recommended tags

xiaohongshu-skill strategy-init --persona="旅行博主" \
  --audience="18-35岁" --direction="旅行攻略,小众目的地"
xiaohongshu-skill strategy-show
xiaohongshu-skill strategy-check-limit --limit-type=likes
xiaohongshu-skill strategy-add-post --date="2025-03-01" --topic="春日出行" --type=图文
```

### SOP workflows

```bash
# Full publishing pipeline: topic analysis → content validation → template → publish prep
xiaohongshu-skill sop --type=publish --topic="旅行攻略" --note-type=图文

# Explore feed interaction: simulated browsing with probabilistic like/collect/comment
xiaohongshu-skill sop --type=explore --feed-count=10 --like-prob=0.3 --collect-prob=0.1

# Comment replies: process one by one with quota control
xiaohongshu-skill sop --type=comment \
  --replies='[{"feed_id":"abc","xsec_token":"xyz","content":"好棒"}]'
```

## Output format

Every command outputs JSON. Here's what a search result looks like:

```json
{
  "id": "abc123",
  "xsec_token": "ABxyz...",
  "title": "帖子标题",
  "type": "normal",
  "user": "用户名",
  "user_id": "user123",
  "liked_count": "1234",
  "collected_count": "567",
  "comment_count": "89"
}
```

## Anti-detection measures

Xiaohongshu's anti-bot is aggressive. Keep these protections on:

- Random **3-6s** wait between navigations; extra **10s** cooldown every 5 navigations
- Random **1-2.5s** before clicking buttons, **5-12s** cooldown after; **15-30s** cooldown every 3 engagement batches
- Title input delay **0.5-1.5s**, body text typed character-by-character at **20-60ms** intervals
- Auto-detects toast warnings ("操作太快", "稍后再试"); comment failures auto-retry once
- Throws `CaptchaError` when the security verification page is triggered

Hit a captcha? Wait a few minutes, then run `xiaohongshu-skill qrcode --headless=false` to solve it manually. Cookie expired? Just re-login.

## Platform compatibility

| Platform | Status |
|----------|--------|
| Windows 11 | Primary environment, fully supported |
| WSL2 (Ubuntu) | Headless works out of the box; headed needs WSLg |
| Linux server | Headless only, QR code saved as image |
| macOS | Untested, should work |

Python 3.10+, Playwright >= 1.40.0.

## Mounting as an AI Skill

`SKILL.md` follows the [AgentSkills](https://agentskills.io) open spec. Compatible with Claude Code / OpenClaw / Codex / Hermes Agent — any platform that supports the AgentSkills spec. The `{baseDir}` template variable is automatically resolved to the actual path.

**Supported platforms:**
- **Claude Code** — Add the directory to your Skill config; auto-detected and loaded
- **OpenClaw** — `clawhub install xiaohongshu-skill` one-click install
- **Codex** — Drop into your Skills directory; same system as OpenClaw
- **Hermes Agent** — Import `SKILL.md` and the agent picks up every command automatically

Universal approach: clone the repo into your platform's Skills directory. The AI agent loads it on the next session automatically.

## FAQ

**How long do cookies last?** A few days to a week. Re-login when `check-login` returns false.

**Do I always need to pass xsec_token?** Yes. Xiaohongshu's security params are session-bound. Always use the latest value from your search or user results.

**Can I bulk scrape?** At scale you'll hit captchas instantly. Keep the built-in rate limiting on.

**How do I scan the QR code in headless mode?** The QR code is saved to `data/qrcode.png`. Send it to your phone. For first-time setup, `--headless=false` is recommended.

**Will I get banned?** Anti-detection measures help, but this technically violates the ToS. Use a throwaway account. Proceed at your own risk.

**How does this compare to xiaohongshu-mcp?** Inspired by the Go-based [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp). This is a Python rewrite with more features — publishing, strategy planning, and SOP automation that the Go version doesn't have.

[![Star History Chart](https://api.star-history.com/svg?repos=DeliciousBuding/xiaohongshu-skill&type=Timeline)](https://www.star-history.com/#DeliciousBuding/xiaohongshu-skill&Timeline)

## Community

Like it? Star it. Found a bug? Open an issue (include logs and repro steps). Want to improve something? PRs welcome. Every contribution counts.

## Heads up

- Cookies expire periodically. Re-login when `check-login` returns false.
- Don't disable the built-in rate limiting — you'll hit a captcha in seconds.
- xsec_token is session-bound. Always use the most recent value.
- For educational and research use. Comply with Xiaohongshu's terms of service.

## Credits

Inspired by [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) (Go version).

## License

[MIT](LICENSE)
