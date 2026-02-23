# xiaohongshu-skill

一个用于 [小红书](https://www.xiaohongshu.com)（rednote）的 AI Agent Skill，基于 Python + Playwright 浏览器自动化实现。

同时兼容 **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** 和 **[OpenClaw](https://openclaw.com)**，遵循 [AgentSkills](https://agentskills.io) 开放规范。

支持搜索笔记、提取帖子详情、查看用户主页、二维码扫码登录，并内置反爬保护机制。

## 功能特性

- **二维码登录** — 扫码认证，Cookie 跨会话持久化
- **搜索笔记** — 全文搜索，支持排序、类型、时间、范围、地点等筛选条件
- **帖子详情** — 提取标题、正文、图片、评论及互动数据（点赞/收藏/评论数）
- **用户主页** — 获取用户信息、粉丝数、笔记列表（自动识别置顶帖）
- **反爬保护** — 内置请求频率控制、验证码检测、仿人类延迟

## 安装

```bash
# 克隆仓库
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# Linux/WSL 环境还需安装系统依赖
playwright install-deps chromium
```

## 使用方法

### 登录（首次使用必须）

```bash
# 打开浏览器窗口，显示二维码供扫描
python -m scripts qrcode --headless=false

# 检查登录状态
python -m scripts check-login
```

在无头模式下，二维码图片会保存到 `data/qrcode.png`，可通过其他方式（如 Telegram）发送扫码。

### 搜索

```bash
# 基础搜索
python -m scripts search "美食推荐" --limit=5

# 带筛选条件
python -m scripts search "旅行攻略" --sort-by=最新 --note-type=图文 --limit=10
```

**筛选选项：**
- `--sort-by`：综合、最新、最多点赞、最多评论、最多收藏
- `--note-type`：不限、视频、图文
- `--publish-time`：不限、一天内、一周内、半年内
- `--search-scope`：不限、已看过、未看过、已关注
- `--location`：不限、同城、附近

### 帖子详情

```bash
# 使用搜索结果中的 id 和 xsec_token
python -m scripts feed <feed_id> <xsec_token>

# 加载评论
python -m scripts feed <feed_id> <xsec_token> --load-comments --max-comments=20
```

### 用户主页

```bash
python -m scripts user <user_id> [xsec_token]
```

## 项目结构

```
xiaohongshu-skill/
├── SKILL.md              # Skill 规范文件（兼容 Claude Code + OpenClaw）
├── README.md             # 项目文档
├── requirements.txt      # Python 依赖
├── LICENSE               # MIT 许可证
├── data/                 # 运行时数据（二维码、调试输出）
└── scripts/              # 核心模块
    ├── __init__.py
    ├── __main__.py       # CLI 入口
    ├── client.py         # 浏览器客户端封装（频率控制 + 验证码检测）
    ├── login.py          # 二维码扫码登录流程
    ├── search.py         # 搜索（支持多种筛选条件）
    ├── feed.py           # 帖子详情 + 评论提取
    └── user.py           # 用户主页 + 笔记列表
```

## 工作原理

1. 通过 Playwright 启动无头 Chromium 浏览器
2. 加载已保存的 Cookie 进行身份认证
3. 导航到小红书页面
4. 从 `window.__INITIAL_STATE__`（Vue SSR 状态）中提取结构化数据
5. 返回 JSON 格式结果

### 反爬机制

小红书有严格的反爬策略，本工具通过以下方式应对：

- **请求频率控制**：两次导航间随机延迟 3-6 秒
- **连续请求冷却**：每连续 5 次请求后额外冷却 10 秒
- **验证码检测**：监测安全验证页面重定向，触发时抛出 `CaptchaError` 并给出处理建议
- **会话管理**：Cookie 持久化与登录状态检查

**触发验证码时的处理：**
1. 等待几分钟后重试
2. 运行 `python -m scripts qrcode --headless=false` 手动通过验证
3. 如 Cookie 失效，重新扫码登录

## 输出格式

所有命令输出 JSON 到标准输出。搜索结果示例：

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

## 平台兼容性

| 平台 | 状态 | 备注 |
|------|------|------|
| Windows 11 | 完全支持 | 主要开发环境 |
| WSL2 (Ubuntu) | 支持 | 无头模式开箱即用；有头模式需要 WSLg |
| Linux 服务器 | 支持 | 仅无头模式；二维码保存为图片文件 |
| macOS | 应该可用 | 未经测试 |

## 环境要求

- Python 3.10+
- Playwright >= 1.40.0

## 作为 AI Agent Skill 使用

本项目遵循 [AgentSkills 开放规范](https://agentskills.io)，同时兼容以下平台：

### Claude Code

将本项目目录添加到 Claude Code 的 Skill 配置中，Claude 会自动识别 `SKILL.md` 并加载小红书能力。

### OpenClaw

将本项目放到 OpenClaw 的 Skills 目录中：

```bash
# 方式一：直接克隆到工作区 Skills 目录
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git ~/.openclaw/workspace/skills/xiaohongshu-skill

# 方式二：通过 ClawHub 安装（如已发布）
clawhub install xiaohongshu-skill
```

OpenClaw 会在下一个会话中自动加载。`SKILL.md` 中的 `{baseDir}` 模板变量会被替换为实际的 Skill 目录路径。

## 注意事项

1. **Cookie 过期**：Cookie 会定期过期，`check-login` 返回 false 时需重新登录
2. **频率限制**：过度抓取会触发验证码，请依赖内置的频率控制
3. **xsec_token**：Token 与会话绑定，始终使用搜索/用户结果中的最新 Token
4. **仅供学习**：请遵守小红书的使用条款，本工具仅用于学习研究

## 许可证

[MIT](LICENSE)

## 致谢

灵感来源于 [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)（Go 版本）。
