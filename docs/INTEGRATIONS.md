# Integrations

Last updated: 2026-07-06

`xiaohongshu-skill` exposes one plain CLI and one AgentSkill file. Agent platforms should call the CLI through the instructions in `SKILL.md`.

## Command Rules

- Read-only commands: `check-login`, `search`, `feed`, `user`, `me`, `explore`.
- Profile inspection command: `profiles`.
- Write commands: `publish`, `publish-video`, `publish-md`, `publish-longform`, `comment`, `reply`, `reply-notification`, `like`, `unlike`, `collect`, `uncollect`.
- Agents must ask the user before any write command.
- JSON output is the interface. Do not parse terminal prose.
- Use `--profile <name>` when one machine operates more than one Xiaohongshu account.

## Claude Code

Install:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.claude/skills/xiaohongshu-skill
cd ~/.claude/skills/xiaohongshu-skill
pip install -r requirements.txt
playwright install chromium
python -m scripts qrcode --headless=false
```

Try:

```text
帮我搜下小红书上关于北京咖啡店的笔记，返回 5 条。
```

## Codex

Install:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.codex/skills/xiaohongshu-skill
cd ~/.codex/skills/xiaohongshu-skill
pip install -r requirements.txt
playwright install chromium
python -m scripts qrcode --headless=false
```

Use the same prompts as Claude Code. Codex should read `SKILL.md` and call `python -m scripts`.

## OpenClaw and ClawHub

Preferred install:

```bash
clawhub install xiaohongshu-skill
```

Manual install:

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.openclaw/skills/xiaohongshu-skill
```

After install, restart OpenClaw so it reloads Skill metadata.

## Cursor and Cline

Cursor and Cline can use the repository as an agent-readable Skill folder if your setup supports local Skills. If your setup expects MCP servers only, use this project as a CLI tool from the agent shell.

Recommended shell check:

```bash
python -m scripts check-login
python -m scripts search "旅行攻略" --limit=3
```

Profile example:

```bash
python -m scripts --profile brand-a search "旅行攻略" --limit=3
```

## n8n

Use an Execute Command node to call the CLI, then parse JSON in the next node.

Example command:

```bash
python -m scripts search "上海 brunch" --limit=5
```

For write actions, add a manual approval node before the command node.

## Output Contract

Search returns:

```json
{
  "count": 1,
  "results": [
    {
      "id": "note-id",
      "xsec_token": "token-from-search",
      "title": "笔记标题",
      "user": "作者"
    }
  ]
}
```

Errors return:

```json
{
  "status": "error",
  "error_type": "CaptchaError",
  "message": "触发小红书安全验证"
}
```
