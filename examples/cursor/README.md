# Cursor Example

Use this project as a local Skill folder or call the CLI from Cursor's agent shell.

## Local Setup

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
pip install -r requirements.txt
playwright install chromium
python -m scripts qrcode --headless=false
```

## Shell Checks

```bash
python -m scripts check-login
python -m scripts search "上海咖啡" --limit=3
python -m scripts contracts --command=search
```

## Prompt

```text
Use the xiaohongshu-skill CLI in this repository. Search Xiaohongshu for "上海咖啡", return 3 JSON results, and do not run write commands.
```

Write commands such as `publish`, `comment`, `like`, and `collect` need user confirmation before the agent runs them.
