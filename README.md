# xiaohongshu-skill

小红书 AI Agent 工具箱。搜笔记、发帖子、做互动、跑运营，一条命令全搞定。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/DeliciousBuding/xiaohongshu-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/DeliciousBuding/xiaohongshu-skill/actions/workflows/ci.yml)
[![Stars](https://img.shields.io/github/stars/DeliciousBuding/xiaohongshu-skill?style=social)](https://github.com/DeliciousBuding/xiaohongshu-skill)
[![Version](https://img.shields.io/badge/version-v1.3.0-blue)](https://github.com/DeliciousBuding/xiaohongshu-skill/releases)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ClawHub](https://img.shields.io/badge/ClawHub-download-orange)](https://clawhub.com)

Python + Playwright 浏览器自动化。打开页面，从 `window.__INITIAL_STATE__` 抽结构化数据，纯 JSON 输出。`SKILL.md` 遵循 [AgentSkills](https://agentskills.io) 开放规范，兼容 Claude Code / OpenClaw / Codex / Hermes Agent 等平台。

## 能做什么

<!-- TODO: 录制搜索演示 GIF -->
**搜。** 关键词全文搜索，排序、类型、时间、范围、地点随便筛。
<!-- TODO: 录制发布演示 GIF -->
**发。** 图文、视频、Markdown 转图片、长文。定时发、自动发都行。
<!-- TODO: 录制互动演示 GIF -->
**互动。** 评论、回复、点赞、收藏。内置人性化延迟，防封。
<!-- TODO: 录制运营演示 GIF -->
**运营。** 写作模板一键出稿，策略追踪每日配额，SOP 编排自动化。

## 安装

```bash
# 1. 安装
pip install git+https://github.com/DeliciousBuding/xiaohongshu-skill.git

# 2. 装浏览器（一次性，约 300MB）
playwright install chromium
# Linux/WSL: playwright install-deps chromium

# 3. 扫码登录（一次性，Cookie 自动保存）
xiaohongshu-skill qrcode --headless=false

# 4. 开用
xiaohongshu-skill search "美食"
xiaohongshu-skill check-login
```

装完就能用 `xiaohongshu-skill` 命令，不需要 `xiaohongshu-skill`。

## 功能详解

### 搜索笔记

```bash
xiaohongshu-skill search "旅行攻略" --sort-by=最新 --note-type=图文 --limit=10
```

| 参数 | 可选值 |
|------|--------|
| `--sort-by` | 综合 / 最新 / 最多点赞 / 最多评论 / 最多收藏 |
| `--note-type` | 不限 / 视频 / 图文 |
| `--publish-time` | 不限 / 一天内 / 一周内 / 半年内 |
| `--search-scope` | 不限 / 已看过 / 未看过 / 已关注 |
| `--location` | 不限 / 同城 / 附近 |

### 帖子详情 & 用户主页

```bash
# id 和 xsec_token 从搜索结果拿
xiaohongshu-skill feed <id> <xsec_token>
xiaohongshu-skill feed <id> <xsec_token> --load-comments --max-comments=20
# 用户主页
xiaohongshu-skill user <user_id> [xsec_token]
xiaohongshu-skill me
```

### 评论 & 回复

```bash
xiaohongshu-skill comment <id> <token> --content="写得真好"
xiaohongshu-skill reply <id> <token> --comment-id=<cid> --reply-user-id=<uid> --content="感谢"
xiaohongshu-skill reply-notification --content="谢谢" --index=0  # 从通知页回，更安全
```

### 点赞 & 收藏

```bash
xiaohongshu-skill like <id> <token>
xiaohongshu-skill unlike <id> <token>
xiaohongshu-skill collect <id> <token>
xiaohongshu-skill uncollect <id> <token>
```

### 推荐流 & 发布笔记

```bash
xiaohongshu-skill explore --limit=20

# 图文发布（默认停在发布按钮，加 --auto-publish 自动发）
xiaohongshu-skill publish --title="标题" --content="正文" \
  --images="a.jpg,b.jpg" --tags="旅行,美食"

# 视频 / Markdown 渲染发图 / 长文 / 定时发布
xiaohongshu-skill publish-video --title="t" --content="c" --video="v.mp4" --tags="vlog"
xiaohongshu-skill publish-md --title="技术文" --file=article.md --width=1080
xiaohongshu-skill publish-longform --title="标题" --content="正文..."
xiaohongshu-skill publish --title="预告" --content="..." --images="img.jpg" --schedule-time="2025-03-01 12:00"
```

### 写作模板 & 运营策略

```bash
xiaohongshu-skill template --topic="美食探店"
xiaohongshu-skill template --topic="学习方法" --type=长文
# 输出：标题建议 + 内容框架 + 标签推荐

xiaohongshu-skill strategy-init --persona="旅行博主" \
  --audience="18-35岁" --direction="旅行攻略,小众目的地"
xiaohongshu-skill strategy-show
xiaohongshu-skill strategy-check-limit --limit-type=likes
xiaohongshu-skill strategy-add-post --date="2025-03-01" --topic="春日出行" --type=图文
```

### SOP 编排

```bash
# 发布全流程：选题分析 → 内容校验 → 模板生成 → 发布准备
xiaohongshu-skill sop --type=publish --topic="旅行攻略" --note-type=图文

# 推荐流交互：模拟真实浏览，按概率点赞/收藏/评论
xiaohongshu-skill sop --type=explore --feed-count=10 --like-prob=0.3 --collect-prob=0.1

# 评论回复：逐条处理，配额控制
xiaohongshu-skill sop --type=comment \
  --replies='[{"feed_id":"abc","xsec_token":"xyz","content":"好棒"}]'
```

### X/Twitter 外部素材包

做跨平台选题时，可以先用 [TweetClaw](https://github.com/Xquik-dev/tweetclaw)
导出公开 X/Twitter 帖子、回复、作者、时间和互动数据，再把整理后的素材包交给
`xiaohongshu-skill template` 或 `sop --type=publish`。

建议素材包包含：

- 查询词和时间范围
- 支持、反对、中性观点各 3-5 条
- 适合小红书改写的角度
- 需要复核的事实或版权风险

TweetClaw 只负责公开 X/Twitter 来源证据。小红书搜索、模板、发布准备、评论和互动仍由本项目处理，并继续遵守写操作确认规则。

## 输出格式

所有命令输出 JSON。搜索结果长这样：

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

## 反爬保护

小红书反爬严，下面这套别关：

- 两次导航间随机等 **3-6 秒**；每 5 次额外冷却 **10 秒**
- 点按钮前随机 **1-2.5s**，点完冷却 **5-12s**；每 3 次互动批次冷却 **15-30s**
- 发布时标题输入间隔 **0.5-1.5s**，正文逐字 **20-60ms**
- 自动检测 toast（"操作太快"、"稍后再试"）；评论失败自动重试一次
- 触发安全验证页时抛 `CaptchaError`

触发验证码了？等几分钟，`xiaohongshu-skill qrcode --headless=false` 手动过，Cookie 失效就重登。

## 平台兼容性

| 平台 | 状态 |
|------|------|
| Windows 11 | 主力环境，全功能 |
| WSL2 (Ubuntu) | 无头直接跑，有头需 WSLg |
| Linux 服务器 | 仅无头，二维码存图片 |
| macOS | 未测试，应该可用 |

Python 3.10+，Playwright >= 1.40.0。

## 作为 AI Skill 挂载

`SKILL.md` 遵循 [AgentSkills](https://agentskills.io) 开放规范，兼容所有支持该标准的 AI Agent 平台。`{baseDir}` 模板变量会被自动替换为实际路径。

**支持平台：**
- **Claude Code** — 目录加到 Skill 配置，自动识别加载
- **OpenClaw** — `clawhub install xiaohongshu-skill` 一键安装
- **Codex** — 放入 Skills 目录即可，跟 OpenClaw 同体系
- **Hermes Agent** — 导入 `SKILL.md`，Agent 自动理解所有命令

通用方式：把仓库克隆到平台的 Skills 目录下，AI Agent 会在下个会话自动加载。

## FAQ

**Cookie 多久过期？** 几天到一周。`check-login` 返回 false 就重登。

**xsec_token 必须每次传吗？** 对，小红书的安全参数跟会话绑定。从搜索或用户结果里拿最新的。

**能批量抓取吗？** 量大了必出验证码。内置频率控制别关。

**无头模式怎么扫码？** 二维码存 `data/qrcode.png`，发手机扫。第一次建议 `--headless=false`。

**会封号吗？** 有反爬保护但违反正规 ToS。建议小号，风险自负。

**跟 xiaohongshu-mcp 什么关系？** 灵感来自 Go 版 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)。本项目是 Python 重写，功能更多（发布、策略、SOP）。

[![Star History Chart](https://api.star-history.com/svg?repos=DeliciousBuding/xiaohongshu-skill&type=Timeline)](https://www.star-history.com/#DeliciousBuding/xiaohongshu-skill&Timeline)

## 社区

觉得有用点个 Star。遇到问题开 Issue（带日志和复现步骤），想改代码直接提 PR。任何贡献都欢迎。

## 注意事项

- Cookie 定期过期，`check-login` 返回 false 需重登
- 别关内置频率控制，关了秒出验证码
- xsec_token 跟会话绑定，始终用最新值
- 学习研究用途，遵守小红书使用条款

## 致谢

灵感来自 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)（Go 版本）。

## 许可证

[MIT](LICENSE)
