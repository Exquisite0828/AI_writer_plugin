# Troubleshooting

这份文档覆盖普通 GitHub 用户首次本地运行时最常见的问题。

## `validate` 通过但插件命令不显示

症状：

```bash
claude plugin validate .
```

通过，但 Claude Code 里看不到 `/ai-writing-plugin:write`。

原因通常是：`validate` 只校验 manifest，不会把命令加载进当前 Claude Code 会话。

从仓库根目录启动新的会话：

```bash
claude --plugin-dir .
```

然后在新会话里运行：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_demo_fixture/task.yaml"
```

## 当前目录不对

请确认你在仓库根目录。根目录应包含：

```text
.claude-plugin/plugin.json
commands/write.md
pyproject.toml
```

如果缺少这些文件，先 `cd` 到实际 clone 的 `AI_writer_plugin` 目录。

## Python 命令不可用

优先使用仓库内 virtual environment：

```bash
.venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
```

如果 `.venv/bin/python` 不存在，先创建并安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

如果已经激活 venv，也可以使用：

```bash
python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
```

## `runs/` 出现本地输出

这是正常 runtime output。每次运行会写入：

```text
runs/<run_id>/
```

不要提交这些输出。仓库 `.gitignore` 已忽略 `runs/`，提交前可以检查：

```bash
git status --short -- runs/
git ls-files runs/
```

`git ls-files runs/` 不应输出 tracked files。

## 输出包含 `NEEDS_USER_CONFIRMATION`

`NEEDS_USER_CONFIRMATION`、pending claims、open confirmations 或 blocked verification 通常不是失败。

它们表示插件没有找到足够的项目 `source` 或已记录 HITL 来支持某个 critical claim。应补充真实项目材料，或在 workflow 中记录真实人工确认；不要把 `sample` 或 `reference` 当作项目事实来源。

## `claude plugin validate` 没有在 CI 跑

GitHub runner 未必安装 Claude Code CLI，所以 CI 不一定能运行：

```bash
claude plugin validate .
```

本地发布或交付前仍建议在安装了 Claude Code CLI 的环境中执行该检查。
