# xiaohongshu-skill

[![CI](https://github.com/DeliciousBuding/xiaohongshu-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/DeliciousBuding/xiaohongshu-skill/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/DeliciousBuding/xiaohongshu-skill)](https://github.com/DeliciousBuding/xiaohongshu-skill/releases)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue)](LICENSE)

面向 AI Agent 和命令行用户的小红书浏览器工具箱。它通过 Python Playwright 提供搜索、详情读取、推荐流、登录、发布、评论、点赞、收藏、模板、策略和 SOP 能力。

- CLI 默认输出 JSON，适合 Agent 和自动化工具消费。
- 多账号通过 profile 隔离浏览器会话和本地状态。
- 发布结果区分已确认、已提交但未确认、失败，避免把按钮点击当成发布成功。
- 默认测试不访问小红书；真实浏览器测试需要显式开启。

> 本项目会操作真实账号。发布、评论、回复、点赞和收藏前必须获得用户明确确认。遇到验证码或安全验证时停止自动操作并切换到人工处理。

English documentation: [README_EN.md](README_EN.md)

## 能力

| 类别 | 命令 | 写入账号 |
| --- | --- | --- |
| 登录与账号 | `qrcode`, `check-login`, `profiles`, `logout` | `logout` 会清除本地状态 |
| 内容发现 | `search`, `feed`, `user`, `me`, `explore` | 否 |
| 内容发布 | `publish`, `publish-video`, `publish-md`, `publish-longform` | 是 |
| 互动 | `comment`, `reply`, `reply-notification`, `like`, `collect`, `unlike`, `uncollect` | 是 |
| 内容工具 | `template`, `strategy-*`, `sop` | SOP 取决于具体动作 |
| 开发辅助 | `selectors`, `contracts` | 否 |

完整参数见 [CLI 命令参考](docs/API.md)。

## 安装

### ClawHub

```bash
clawhub install xiaohongshu-skill
```

### Agent Skills CLI

```bash
npx skills add DeliciousBuding/xiaohongshu-skill
```

### 本地可复现环境

```bash
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill
uv sync --frozen --no-dev
uv run playwright install chromium
```

开发环境：

```bash
uv sync --frozen --group dev
uv run python -m scripts.quality check
```

### 全局 CLI

```bash
pip install git+https://github.com/DeliciousBuding/xiaohongshu-skill.git
playwright install chromium
xiaohongshu-skill --help
```

### Docker

```bash
docker compose build
docker compose run --rm xiaohongshu qrcode --headless=false
```

更完整的系统和平台说明见 [安装指南](docs/INSTALL.md)。

## 快速开始

### 1. 登录

```bash
uv run python -m scripts qrcode --headless=false
uv run python -m scripts check-login
```

### 2. 搜索和读取

```bash
uv run python -m scripts search "咖啡" --limit=5
uv run python -m scripts feed <feed_id> <xsec_token>
uv run python -m scripts user <user_id> <xsec_token>
uv run python -m scripts explore --limit=10
```

`feed_id`、`user_id` 和 `xsec_token` 应来自当前会话的搜索或详情结果，不要长期缓存安全参数。

### 3. 准备发布

默认发布命令只填写内容并停在发布页：

```bash
uv run python -m scripts publish \
  --title="周末咖啡记录" \
  --content="正文内容" \
  --images="/path/to/1.jpg,/path/to/2.jpg"
```

确认标题、正文、媒体、账号和可见范围后，才使用：

```bash
uv run python -m scripts publish ... --auto-publish
```

自动提交结果状态：

| 状态 | 含义 | 建议动作 |
| --- | --- | --- |
| `confirmed` | 观察到可信成功信号 | 可以记录为成功 |
| `submitted_unconfirmed` | 已点击提交，但没有观察到成功信号 | 人工复核，禁止自动重试 |
| `failed` | 未提交或观察到失败信号 | 检查错误后再决定 |
| `ready` | 内容已填写，尚未点击发布 | 人工检查后决定是否提交 |

### 4. 多账号

```bash
uv run python -m scripts --profile brand-a qrcode --headless=false
uv run python -m scripts --profile brand-a search "咖啡"
uv run python -m scripts profiles
```

不同 profile 使用独立的浏览器数据、Cookie 备份和会话元数据。`XHS_FP_SEED` 可临时覆盖当前进程的稳定指纹 seed。

## 安全和限制

- 不要关闭内置导航间隔和互动冷却。
- 不要运行高频批量抓取或批量互动。
- 遇到验证码、登录页或安全验证页时停止。
- 不要在 issue、日志或截图中提交账号信息、Cookie、完整安全参数或二维码。
- Docker 镜像以非 root 用户运行，本地敏感状态不会进入构建上下文。
- `XHS_ALLOW_NO_SANDBOX=true` 只适用于明确需要关闭 Chromium sandbox 的隔离环境。

详见 [安全说明](docs/SECURITY.md)。

## 工程设计

- [架构](docs/ARCHITECTURE.md)
- [安装](docs/INSTALL.md)
- [CLI API](docs/API.md)
- [平台集成](docs/INTEGRATIONS.md)
- [安全](docs/SECURITY.md)
- [参考实现与来源](docs/REFERENCE.md)
- [发布流程](docs/RELEASING.md)
- [路线图](docs/ROADMAP.md)

默认质量门：

```bash
uv run python -m scripts.quality check
```

CI 还会测试 Python 3.10、3.11、3.12，构建 wheel 和源码包，并验证 Docker 镜像。

## 来源与许可证

仓库原创代码按 [Apache License 2.0](LICENSE) 发布。部分浏览器行为参考或改写自 Apache-2.0 项目 `xpzouying/xiaohongshu-mcp`，详情见 [第三方声明](THIRD_PARTY_NOTICES.md)。

本项目与小红书官方无隶属或授权关系。使用者应自行遵守适用的平台规则、法律法规和账号安全要求。
