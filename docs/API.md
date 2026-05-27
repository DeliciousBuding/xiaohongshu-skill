# CLI 命令参考

所有命令从项目根目录运行，输出 JSON。

## 登录

```bash
python -m scripts qrcode --headless=false   # 扫码登录
python -m scripts check-login               # 查登录状态
python -m scripts me                        # 看自己主页
```

## 搜索

```bash
python -m scripts search "关键词" --limit=10
python -m scripts search "美食" --sort-by=最新 --note-type=图文
```

| 参数 | 可选值 |
|------|--------|
| `--sort-by` | 综合, 最新, 最多点赞, 最多评论, 最多收藏 |
| `--note-type` | 不限, 视频, 图文 |
| `--publish-time` | 不限, 一天内, 一周内, 半年内 |
| `--search-scope` | 不限, 已看过, 未看过, 已关注 |
| `--location` | 不限, 同城, 附近 |

## 帖子 & 用户

```bash
python -m scripts feed <feed_id> <xsec_token>
python -m scripts feed <feed_id> <xsec_token> --load-comments --max-comments=20
python -m scripts user <user_id> [xsec_token]
```

## 评论

```bash
python -m scripts comment <feed_id> <xsec_token> --content="内容"
python -m scripts reply <feed_id> <xsec_token> --comment-id=<cid> --reply-user-id=<uid> --content="内容"
python -m scripts reply-notification --content="内容" --index=0
```

## 点赞 & 收藏

```bash
python -m scripts like <feed_id> <xsec_token>
python -m scripts unlike <feed_id> <xsec_token>
python -m scripts collect <feed_id> <xsec_token>
python -m scripts uncollect <feed_id> <xsec_token>
```

## 推荐流

```bash
python -m scripts explore --limit=20
```

## 发布

```bash
# 图文
python -m scripts publish --title="标题" --content="正文" --images="a.jpg,b.jpg" --tags="标签1,标签2"
python -m scripts publish --title="标题" --content="正文" --images="a.jpg" --auto-publish

# 视频
python -m scripts publish-video --title="标题" --content="描述" --video="video.mp4" --tags="vlog"

# Markdown 渲染为图片
python -m scripts publish-md --title="标题" --file=article.md --tags="干货"
python -m scripts publish-md --title="标题" --text="# 正文\n内容..." --width=1080

# 长文
python -m scripts publish-longform --title="标题" --content="正文..."

# 定时发布（ISO8601 格式，1小时到14天之间）
python -m scripts publish --title="标题" --content="正文" --images="img.jpg" --schedule-time="2025-03-01T12:00:00+08:00"
```

## 写作模板

```bash
python -m scripts template --topic="旅行攻略"
python -m scripts template --topic="美食探店" --type=视频
python -m scripts template --topic="学习方法" --type=长文
```

输出：标题建议 + 内容框架 + 标签推荐。

## 运营策略

```bash
python -m scripts strategy-init --persona="旅行博主" --audience="18-35岁" --direction="旅行攻略,小众目的地"
python -m scripts strategy-show
python -m scripts strategy-check-limit --limit-type=likes
python -m scripts strategy-check-limit --limit-type=comments
python -m scripts strategy-add-post --date="2025-03-01" --topic="春日出行" --type=图文
```

## SOP 编排

```bash
# 发布全流程
python -m scripts sop --type=publish --topic="旅行攻略" --note-type=图文

# 推荐流互动
python -m scripts sop --type=explore --feed-count=10 --like-prob=0.3 --collect-prob=0.1

# 评论互动
python -m scripts sop --type=comment --replies='[{"feed_id":"abc","xsec_token":"xyz","content":"好棒"}]'
```

## 通用参数

| 参数 | 说明 |
|------|------|
| `--headless` | `true`(默认) 无头 / `false` 显示浏览器 |
| `--limit` / `-n` | 返回数量上限 |

## 退出码

| 码 | 含义 |
|----|------|
| 0 | 成功 |
| 1 | 错误（解析失败、未登录等） |
| 2 | 严重错误 |
