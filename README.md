# AI 专业文档写作 Claude Code 插件

面向 Claude Code 的 AI 专业文档写作插件：用一套确定性的 Python workflow，把用户材料整理成可追踪、可审查、关注证据边界的专业文档交付包。

## 适合什么场景

- 你有 `source`、`template`、`checklist`、`sample` 或 `reference` 等材料；
- 你希望生成 professional document draft、review package 和 traceable artifacts；
- 你需要区分项目事实、结构模板、示例风格、参考资料和人工确认；
- 你希望 unsupported critical claims 保持 pending，而不是被自动写成结论。

## Quickstart

要求：

- Python 3.11+
- Claude Code CLI

在仓库根目录准备 Python 环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

校验插件 manifest：

```bash
claude plugin validate .
```

`validate` 只检查 manifest 合法；要在当前 Claude Code 会话中使用本地插件，请从仓库根目录启动：

```bash
claude --plugin-dir .
```

如果 `validate` 通过但命令不显示，见 [Troubleshooting](docs/TROUBLESHOOTING.md)。



进入claudecode界面

# 1. 添加本地目录为 marketplace

/plugin marketplace add D:\Github\Ancoder\Ancoder_Writer_Agent

# 2. 安装插件

/plugin install ai-writing-plugin@ancoder-writer

# 3. 重载插件使其生效

/reload-plugins



用自己的 `task.yaml` 启动 workflow：

```text
/ai-writing-plugin:write "Run the writing workflow with path/to/task.yaml"
```

如果只是第一次体验，可以先运行一个 demo：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_zh_demo_fixture/task.yaml"
```

命令会输出类似下面的运行目录：

```text
runs/<run_id>/
```

`runs/` 是本地 runtime output，仓库 `.gitignore` 已忽略它，不要提交。

优先查看：

```text
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
```

输出阅读顺序和 pending 状态解释见 [Reading Outputs](docs/READING_OUTPUTS.md)。

完整第一次运行步骤见 [Quickstart](docs/QUICKSTART.md)。

## 准备自己的输入

插件的入口是 `task.yaml`。`task_type` 决定使用哪种文档模式，`inputs` 声明材料路径和角色。

通用专业文档可以先从 `generic_document` 开始：

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

路径相对于 `task.yaml` 所在目录解析。你可以把 `path/to/task.yaml` 换成自己的文件路径；不需要使用 demo fixture。

## 使用方式

| 使用方式                           | 适合场景                                                              | 示例                                                              |
| ---------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `generic_document` 通用模式      | 大多数有 `source` / `template` / `checklist` 的专业文档         | `examples/generic_document_demo_fixture/task.yaml`              |
| external `document_profile.yaml` | 团队或项目内反复使用的自定义文档                                      | `examples/custom_technical_note_profile_demo_fixture/task.yaml` |
| official built-in profiles         | 高价值、高风险、高频场景，带内置规则、fixture、测试和 Skill guideline | `hara` / `technical_solution` / `test_report` / `fsr`     |

当前 official built-in profiles：

| `task_type`          | 用途                                        |
| ---------------------- | ------------------------------------------- |
| `hara`               | HARA hazard analysis report 辅助写作        |
| `technical_solution` | 技术方案、架构方案或实现方案写作            |
| `test_report`        | 测试报告包写作                              |
| `fsr`                | Functional Safety Requirements package 写作 |

`generic_document` 是通用模式，不是 official built-in profile。
`custom_technical_note` 是 external profile demo，不是 official built-in profile。
项目未实现 TSC / Technical Safety Concept；当前没有 official TSC type、profile、Skill、fixture 或测试目标。

## 运行示例

这些 demo 用于体验不同场景，不代表插件只能写这些文档。

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/generic_document_demo_fixture/task.yaml
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/custom_technical_note_profile_demo_fixture/task.yaml
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_zh_demo_fixture/task.yaml
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml
```

每个 demo 展示什么、推荐运行顺序、预期状态和边界检查，见 [Examples](docs/EXAMPLES.md)。

## Claude Code 插件入口

Plugin manifest：

```text
.claude-plugin/plugin.json
```

Command 文档：

```text
commands/write.md
```

在 Claude Code 加载本地插件后，可以使用：

```text
/ai-writing-plugin:write "Run the writing workflow with path/to/task.yaml"
```

command layer 保持通用；具体文档行为由 `task_type`、内置 `DocumentTypeRules` 和可选 external profile 决定。

## 核心证据边界

- `source` 可以作为项目事实来源；
- `sample` is not fact source；它只能作为结构、风格和表格形态参考；
- `reference` is not project-specific fact support；它可以支持方法、背景或术语，但不能证明项目事实；
- critical claim 必须有 `source` 或 HITL，否则保持 pending / `NEEDS_USER_CONFIRMATION`；
- `final_report.md` 是 review-ready artifact，`final report` 不是专业批准文件；
- eval、promotion report 和 candidate updates remain proposed/inactive；它们都不是专业批准；
- candidate update / candidate patch 默认 proposed / inactive，不会自动覆盖 stable profile 或 Skill。

## 输出目录

运行输出写入：

```text
runs/<run_id>/
```

常用输出：

```text
runs/<run_id>/final/final_report.md
runs/<run_id>/final/delivery_summary.md
runs/<run_id>/review/review_report.json
runs/<run_id>/verify/verify_report.json
runs/<run_id>/learning/candidate_profile_update.yaml
```

先读哪些文件、哪些 artifact 适合审查或排查，见 [Reading Outputs](docs/READING_OUTPUTS.md)。

完整 artifact contract 见 [Artifact Contracts](docs/CURRENT_ARTIFACT_CONTRACTS.md)。

## 开发检查

这些命令用于维护者检查，不是普通用户每次写文档都必须运行：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generalization_phase6_product_docs.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_skill_guidelines.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
```

## 文档导航

- [Documentation](docs/README.md)
- [Quickstart](docs/QUICKSTART.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Reading Outputs](docs/READING_OUTPUTS.md)
- [User Guide](docs/USER_GUIDE.md)
- [Examples](docs/EXAMPLES.md)
- [Document Profiles](docs/DOCUMENT_PROFILES.md)
- [Runbook](docs/RUNBOOK.md)
- [Artifact Contracts](docs/CURRENT_ARTIFACT_CONTRACTS.md)
- [Document Type Development Guide](docs/DOCUMENT_TYPE_DEVELOPMENT_GUIDE.md)
