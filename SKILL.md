---
name: xiaohongshu-skill
description: 当用户想要与小红书（xiaohongshu/rednote）交互时使用此 Skill。包括搜索笔记、获取帖子详情、查看用户主页、二维码扫码登录、提取平台内容等。当用户提到 xiaohongshu、小红书、rednote，或需要浏览/抓取中国社交媒体内容时激活此 Skill。
user-invokable: true
metadata: {"openclaw": {"emoji": "📕", "requires": {"bins": ["python3", "playwright"], "anyBins": ["python3", "python"]}, "os": ["win32", "linux", "darwin"], "install": [{"id": "pip", "kind": "node", "label": "Install dependencies (pip)", "bins": ["playwright"]}]}}
---

# 小红书 Skill

基于 Python Playwright 的小红书（rednote）交互工具，通过浏览器自动化从 `window.__INITIAL_STATE__`（Vue SSR 状态）中提取结构化数据。

## 前置条件

在 `{baseDir}` 目录下安装依赖：

```bash
cd {baseDir}
pip install -r requirements.txt
playwright install chromium
```

Linux/WSL 环境还需运行：
```bash
playwright install-deps chromium
```

## 快速开始

所有命令从 `{baseDir}` 目录运行。

### 1. 登录（首次必须）

```bash
cd {baseDir}

# 打开浏览器窗口，显示二维码供微信/小红书扫描
python -m scripts qrcode --headless=false

# 检查登录是否仍然有效
python -m scripts check-login
```

在无头环境下，二维码图片保存到 `{baseDir}/data/qrcode.png`，可通过其他渠道发送扫码。

### 2. 搜索

```bash
cd {baseDir}

# 基础搜索
python -m scripts search "关键词"

# 带筛选条件
python -m scripts search "美食" --sort-by=最新 --note-type=图文 --limit=10
```

**筛选选项：**
- `--sort-by`：综合、最新、最多点赞、最多评论、最多收藏
- `--note-type`：不限、视频、图文
- `--publish-time`：不限、一天内、一周内、半年内
- `--search-scope`：不限、已看过、未看过、已关注
- `--location`：不限、同城、附近

### 3. 帖子详情

```bash
cd {baseDir}

# 使用搜索结果中的 id 和 xsec_token
python -m scripts feed <feed_id> <xsec_token>

# 加载评论
python -m scripts feed <feed_id> <xsec_token> --load-comments --max-comments=20
```

### 4. 用户主页

```bash
cd {baseDir}
python -m scripts user <user_id> [xsec_token]
```

## 数据提取路径

| 数据类型 | JavaScript 路径 |
|----------|----------------|
| 搜索结果 | `window.__INITIAL_STATE__.search.feeds` |
| 帖子详情 | `window.__INITIAL_STATE__.note.noteDetailMap` |
| 用户信息 | `window.__INITIAL_STATE__.user.userPageData` |
| 用户笔记 | `window.__INITIAL_STATE__.user.notes` |

**Vue Ref 处理：** 始终通过 `.value` 或 `._value` 解包：
```javascript
const data = obj.value !== undefined ? obj.value : obj._value;
```

## 反爬保护

本 Skill 内置了针对小红书反机器人策略的保护措施：

- **频率控制**：两次导航间自动延迟 3-6 秒，每 5 次连续请求后冷却 10 秒
- **验证码检测**：自动检测安全验证页面重定向，触发时抛出 `CaptchaError` 并给出处理建议
- **仿人类行为**：随机延迟、滚动模式、User-Agent 伪装

**触发验证码时的处理：**
1. 等待几分钟后重试
2. 运行 `cd {baseDir} && python -m scripts qrcode --headless=false` 手动通过验证
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

## 文件结构

```
{baseDir}/
├── SKILL.md              # 本文件（Skill 规范）
├── README.md             # 项目文档
├── requirements.txt      # Python 依赖
├── LICENSE               # MIT 许可证
├── data/                 # 运行时数据（二维码、调试输出）
└── scripts/              # 核心模块
    ├── __init__.py
    ├── __main__.py       # CLI 入口
    ├── client.py         # 浏览器客户端封装（频率控制 + 验证码检测）
    ├── login.py          # 二维码扫码登录流程
    ├── search.py         # 搜索（支持多种筛选）
    ├── feed.py           # 帖子详情提取
    └── user.py           # 用户主页提取
```

## 跨平台兼容性

| 环境 | 无头模式 | 有头模式（扫码登录） | 备注 |
|------|----------|----------------------|------|
| Windows | 支持 | 支持 | 主要开发环境 |
| WSL2 (Win11) | 支持 | 通过 WSLg 支持 | 需要 `playwright install-deps` |
| Linux 服务器 | 支持 | 不适用 | 二维码保存为图片文件 |

## 注意事项

1. **Cookie 过期**：Cookie 会定期过期，`check-login` 返回 false 时需重新登录
2. **频率限制**：过度抓取会触发验证码，请依赖内置的频率控制
3. **xsec_token**：Token 与会话绑定，始终使用搜索/用户结果中的最新 Token
4. **仅供学习**：请遵守小红书的使用条款，本工具仅用于学习研究
