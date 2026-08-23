---
name: xiaohongshu-skill
description: 小红书 / Xiaohongshu / RedNote AI Agent Skill。用 Python Playwright 搜索和读取内容、管理登录会话、发布图文/视频/长文、评论、点赞和收藏；默认输出 JSON，任何写操作都必须先获得用户确认。用户提到 xiaohongshu、小红书、rednote、小红书搜索、发到小红书、小红书笔记分析、小红书运营或小红书自动化时触发。
license: MIT
compatibility: Requires Python 3.10 or newer and Playwright Chromium. Supports Windows, macOS, and Linux.
metadata:
  openclaw:
    emoji: "📕"
    requires:
      anyBins:
        - python3
        - python
    os:
      - win32
      - linux
      - darwin
---

# 小红书 Skill

通过 JSON CLI 操作小红书浏览器会话。执行入口统一为：

```bash
cd {baseDir}
uv run python -m scripts <command>
```

## 安全规则

发布、评论、回复、点赞、收藏、取消点赞和取消收藏会改变真实账号状态。执行前必须：

1. 展示目标账号、内容、媒体和操作类型。
2. 获得用户明确确认。
3. 只执行用户确认的单次操作。

遇到验证码、登录页或安全验证页时停止。不要自动绕过验证，不要运行批量抓取或批量互动。

## 任务路由

| 用户目标 | 命令或参考 |
| --- | --- |
| 首次登录或重新登录 | `qrcode --headless=false` |
| 检查登录 | `check-login` |
| 管理多个账号 | `--profile <name>`；详见 `docs/INSTALL.md` |
| 搜索笔记 | `search` |
| 读取笔记详情 | `feed` |
| 读取用户主页 | `user` 或 `me` |
| 获取推荐流 | `explore` |
| 准备或发布图文 | `publish` |
| 准备或发布视频 | `publish-video` |
| Markdown 转图片发布 | `publish-md` |
| 准备或发布长文 | `publish-longform` |
| 评论和回复 | `comment`、`reply`、`reply-notification` |
| 点赞和收藏 | `like`、`collect`、`unlike`、`uncollect` |
| 模板、策略和 SOP | `template`、`strategy-*`、`sop` |
| 查看参数 | `python -m scripts <command> --help` |

完整命令见 `docs/API.md`；安装和平台接入见 `docs/INSTALL.md`、`docs/INTEGRATIONS.md`。

## 初始化

```bash
cd {baseDir}
uv sync --frozen --no-dev
uv run playwright install chromium
uv run python -m scripts qrcode --headless=false
```

开发者使用：

```bash
uv sync --frozen --group dev
uv run python -m scripts.quality check
```

## 只读示例

```bash
uv run python -m scripts search "咖啡" --limit=5
uv run python -m scripts feed <feed_id> <xsec_token>
uv run python -m scripts explore --limit=10
```

`feed_id`、`user_id` 和 `xsec_token` 必须来自当前会话的结果，不要长期缓存。

## 发布语义

发布命令默认填写表单并返回 `ready`。用户确认后才能追加 `--auto-publish`。

自动提交可能返回：

- `confirmed`：已观察到可信成功信号。
- `submitted_unconfirmed`：已点击提交但未确认成功；必须人工复核，禁止自动重试。
- `failed`：提交失败或出现登录、验证码、安全验证等失败信号。

## 输出和错误

标准输出是 JSON；诊断信息写入标准错误。Agent 应先读取 `status`，再依据 `scripts/output_contracts.py` 中的契约处理字段。

发生 `captcha_required` 或浏览器安全验证时，不要重试循环。切换到有头模式并由用户处理。

## 本地状态

每个 profile 独立保存浏览器状态、Cookie 备份和会话元数据。不要读取、展示、提交或外发这些文件。`XHS_FP_SEED` 只用于显式覆盖当前进程的稳定指纹 seed。

安全和隐私规则见 `docs/SECURITY.md`。架构说明见 `docs/ARCHITECTURE.md`。
