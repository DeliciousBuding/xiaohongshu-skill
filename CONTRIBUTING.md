# 贡献指南

感谢你对 xiaohongshu-skill 的关注！欢迎任何形式的贡献。

## 如何参与

在动手之前，建议先到 [GitHub Issues](https://github.com/DeliciousBuding/xiaohongshu-skill/issues) 中搜索或发起讨论，确认你的想法与项目方向一致，避免重复劳动。

### 报告问题

- 使用 Bug Report 模板提交 issue
- 尽可能附上复现步骤、期望行为、实际行为、环境信息（OS、Python 版本）
- 如果涉及报错，附上完整的错误信息和堆栈

### 提功能建议

- 先搜索已有 issue，避免重复
- 使用 Feature Request 模板
- 描述清楚使用场景和期望效果

## 开发流程

### 分支策略

1. 从 `main` 分支创建 feature 分支：`git checkout -b feature/xxx`
2. 在 feature 分支上开发和测试
3. 推送到远程并创建 Pull Request 到 `main`
4. 等待 review，通过后合并

分支命名规范：
- `feature/xxx` — 新功能
- `fix/xxx` — 问题修复
- `docs/xxx` — 文档更新
- `chore/xxx` — 杂项（依赖更新、CI 配置等）

### 开发环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/DeliciousBuding/xiaohongshu-skill.git
cd xiaohongshu-skill

# 2. 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium

# 5. 运行测试确认环境正常
pytest -v
```

### 代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 不做过度抽象，保持代码直白可读
- 函数和类添加 docstring，说明用途和参数
- 优先使用标准库，减少不必要的第三方依赖

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 添加定时发布功能
fix: 修复搜索页码越界问题
docs: 补充 Docker 部署文档
chore: 升级 playwright 到 1.42
test: 增加发布模块的单元测试
refactor: 提取公共的 xsec_token 校验逻辑
```

### 测试要求

- 新功能必须附带测试用例
- 修改核心逻辑（`client.py`、`login.py`、`search.py` 等）需确保已有测试仍然通过
- 运行 `pytest -v` 确认全部测试通过后再提交

### Pull Request 检查清单

- [ ] 代码符合 PEP 8 风格
- [ ] 新功能有对应的测试用例
- [ ] 所有测试通过（`pytest -v`）
- [ ] 提交信息符合 Conventional Commits 规范
- [ ] 如有破坏性变更，已在 PR 描述中说明
- [ ] 没有引入新的第三方依赖（除非必要并已说明理由）

## 沟通准则

- 保持友善和尊重
- 就事论事，聚焦技术讨论
- PR review 意见是对代码不对人

感谢你的贡献！
