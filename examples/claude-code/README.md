# Claude Code 集成

xiaohongshu-skill 是一个 Claude Code Skill，Claude 会自动加载 `SKILL.md` 来理解如何使用。

## 怎么用

### 1. 克隆 + 装依赖

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
pip install -r requirements.txt
playwright install chromium
```

### 2. 加到 Claude Code

在 Claude Code 的 Skills 目录加个 symlink：

```bash
# Windows
mklink /D %USERPROFILE%\.claude\skills\xiaohongshu-skill D:\path\to\xiaohongshu-skill

# macOS / Linux
ln -s /path/to/xiaohongshu-skill ~/.claude/skills/xiaohongshu-skill
```

或者直接克隆到 skills 目录：

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.claude/skills/xiaohongshu-skill
```

### 3. 扫码登录

```bash
python -m scripts qrcode --headless=false
```

扫完码 Cookie 自动保存在 `~/.xiaohongshu/`，以后不用再登。

### 4. 试试

在 Claude Code 里说：

- "帮我搜下小红书 北京美食"
- "看看小红书上这个帖子怎么样"（给链接）
- "把这个发到小红书"

Claude 会自动跑对应命令。

## 不想装全局？

用 Docker：

```bash
docker compose run --rm xiaohongshu qrcode --headless=false
docker compose run --rm xiaohongshu search "北京美食" --limit=5
```
