# AGENTS.md

xiaohongshu-skill — 小红书 AI Agent 工具箱。本项目是 [AgentSkills](https://agentskills.io) 规范兼容的 Skill。

## AI Agent 工作约定

1. **读写操作分离**：`search` / `feed` / `user` / `explore` / `me` / `check-login` 是只读的，可以放心跑。`publish` / `comment` / `reply` / `like` / `collect` 会改动账号数据，**必须先让用户确认**，用 `AskUserQuestion` 弹确认框。
2. **CLI 优先**：所有功能通过 `python -m scripts <command>` 调用。不要直接 import 脚本模块。
3. **Cookie 生命周期**：首次使用前跑 `qrcode --headless=false` 扫码登录。Cookie 过期（几天到一周）`check-login` 会返回 false，重登就行。
4. **频率控制别关**：内置 3-6s 导航间隔、5 次请求 10s 冷却。强制跳过会触发验证码。
5. **xsec_token**：跟会话绑定的安全参数，始终从搜索结果/用户数据里拿最新的，别缓存。
6. **安全第一**：本工具操作真实小红书账号。不确定的时候问用户，别自己猜。

## 目录结构

```
xiaohongshu-skill/
├── AGENTS.md             # 本文件
├── SKILL.md              # Skill 规范（Agent 自动加载）
├── README.md             # 中文项目文档
├── CONTRIBUTING.md       # 贡献指南
├── Dockerfile            # Docker 构建文件
├── docker-compose.yml    # Docker Compose 配置
├── .env.example          # 环境变量模板
├── scripts/              # 核心源码
│   ├── __main__.py       # CLI 入口（22+ 子命令）
│   ├── client.py         # 浏览器客户端（Playwright 封装）
│   ├── _utils.py         # 公共工具函数
│   └── ...
├── tests/                # 单元测试（pytest）
├── examples/             # 平台集成示例
└── docs/                 # 文档
```

## 开发约定

- Python 3.10+，Playwright >= 1.40.0
- 遵循 PEP 8，不做过度抽象
- 新功能带测试（pytest）
- Conventional Commits（feat/fix/docs/chore/test/refactor）
- 改 `client.py` 要跑全量测试：`pytest -v`

## 平台兼容

`SKILL.md` 按 AgentSkills 开放规范编写，兼容：
- Claude Code
- OpenClaw
- Codex
- Hermes Agent
- 其他支持 AgentSkills 的平台
