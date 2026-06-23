# Quickstart

这份文档面向刚 clone 仓库、想在本地首次运行 Claude Code writing plugin 的用户。

请在仓库根目录执行所有命令。

## Prerequisites

- Python 3.11 或更新版本；
- Git；
- Claude Code CLI。

## 普通用户最短路径

### 1. Clone 仓库

```bash
git clone <repository-url>
cd AI_writer_plugin
```

如果本地目录名不同，请使用实际 clone 目录。

### 2. 创建 virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

### 3. 安装插件依赖

仓库使用 `pyproject.toml`，支持 editable install：

```bash
python -m pip install -e ".[dev]"
```

`dev` extra 会安装本地维护检查需要的 pytest 等依赖。普通写作运行不需要先跑完整 pytest。

### 4. 校验 Claude Code plugin manifest

```bash
claude plugin validate .
```

`claude plugin validate .` 只校验 `.claude-plugin/plugin.json` 是否有效。它不会把 `/ai-writing-plugin:write` 加载进当前已经打开的 Claude Code 会话。

### 5. 启动加载本地插件的新 Claude Code 会话

从仓库根目录启动：

```bash
claude --plugin-dir .
```

进入这个新会话后，才能使用本地插件命令。

### 6. 运行第一个 demo

建议第一次运行中文 `technical_solution` demo。它展示通用技术方案 workflow，不需要先理解功能安全术语。

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_zh_demo_fixture/task.yaml"
```

如果想查看英文材料取向的同类 demo，可以运行：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_demo_fixture/task.yaml"
```

命令会输出类似下面的运行目录：

```text
runs/<run_id>/
```

先打开：

```text
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
```

完整阅读顺序见 [Reading Outputs](READING_OUTPUTS.md)。

如果 `final_report.md` 中出现 open confirmations、pending claim 或 `NEEDS_USER_CONFIRMATION`，这通常是正确行为：说明 critical claim 没有足够项目 `source` 或已记录 HITL。

## 用自己的材料运行

最小目录可以这样组织：

```text
my_doc_task/
  task.yaml
  inputs/
    source.md
    template.md
    checklist.md
    sample.md
    reference.md
```

`task.yaml` 示例：

```yaml
task_type: generic_document
task_title: Generate a project document
target_audience: Reviewers
output_format: markdown
allow_inference: false
requires_human_confirmation:
  - final recommendation
inputs:
  - path: inputs/source.md
    role: source
  - path: inputs/template.md
    role: template
  - path: inputs/checklist.md
    role: checklist
  - path: inputs/sample.md
    role: sample
  - path: inputs/reference.md
    role: reference
```

`inputs[*].path` 相对于 `task.yaml` 所在目录解析。你可以把 demo 路径换成自己的 `task.yaml`：

```text
/ai-writing-plugin:write "Run the writing workflow with my_doc_task/task.yaml"
```

`generic_document` 可以作为普通专业文档起点。`hara`、`technical_solution`、`test_report` 和 `fsr` 是 official L3 built-ins，适合内置规则覆盖的增强场景。

## 不用 Claude Code 时的 Python CLI 备用路径

如果需要排查 Python 环境或暂时不用 Claude Code，可以直接运行 CLI：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_zh_demo_fixture/task.yaml
```

替换成自己的 `task.yaml`：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task my_doc_task/task.yaml
```

这条路径和插件命令使用同一个 Python engine。

## Git hygiene

运行输出都在：

```text
runs/<run_id>/
```

`runs/` 是本地 runtime output，仓库 `.gitignore` 已忽略它。不要提交 runtime outputs。

提交文档或源码变更前，建议检查：

```bash
git status --short
git status --short -- runs/
git ls-files runs/
```

`runs/` 不应包含 tracked files。

## 维护者检查

这些命令用于维护者或发布前检查，不是普通用户每次写文档都必须运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
git status --short -- runs/
git ls-files runs/
```

## 常见问题

如果 `claude plugin validate .` 通过但命令不显示，通常是因为当前 Claude Code 会话没有用 `claude --plugin-dir .` 从仓库根目录重新启动。

更多排查见 [Troubleshooting](TROUBLESHOOTING.md)。

## 关键边界

- `sample` is not fact source；
- `reference` 不能证明项目事实；
- critical claim 必须有项目 `source` 或 HITL；
- `final_report.md` 不是专业批准文件；
- eval passed 不是专业批准；
- candidate updates 默认 proposed/inactive；
- TSC / Technical Safety Concept 由 `task_type: TechnicalSafetyConcept` 支持，demo fixture 为 `examples/technical_safety_concept_demo_fixture/`；HSC / SSC（硬件/软件安全概念）仍 deferred。
