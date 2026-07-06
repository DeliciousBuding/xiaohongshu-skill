# OpenClaw Example

Install through ClawHub when available:

```bash
clawhub install xiaohongshu-skill
```

Manual install:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.openclaw/skills/xiaohongshu-skill
cd ~/.openclaw/skills/xiaohongshu-skill
pip install -r requirements.txt
playwright install chromium
python -m scripts qrcode --headless=false
```

Try:

```text
帮我搜小红书上的深圳徒步攻略，返回 5 条，只要 JSON 摘要。
```

OpenClaw should read `SKILL.md` and call `python -m scripts`. Any write command needs user confirmation first.
