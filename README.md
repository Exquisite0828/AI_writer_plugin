# AI 专业文档写作 Claude Code 插件

这是一个面向 Claude Code 的证据边界专业文档写作技术预览。当前仓库由两部分组成：

- Claude Code `/write`、薄编排器和step/review Skills定义agent-worker写作协议；
- Python提供Phase 0 run scaffold以及context、dispatch、progress、result、stage-review issue和stage-gate元数据工具。

当前Python包不是完整的一键写作引擎，不提供`write-run`或`resume-run`。

## 当前能做什么

### Claude Code运行时协议

在支持Task/Agent worker的Claude Code环境中，插件入口可以按7个stage、13个step编排专业文档工作：

```text
input materials
-> inventory and source index
-> outline and evidence planning
-> conservative draft
-> review and verification
-> revision and review-ready delivery
-> summary and proposed candidate update
```

专业artifact由独立worker按当前Skill生成，不是由Python CLI生成。每个stage需要独立review和明确的用户gate；缺少worker能力时必须停止，不能在主上下文静默代执行。

### Python已实现能力

Python当前负责：

- `init-run`；
- `input_refs.json`路径、role和hash边界；
- context telemetry与budget diagnostics；
- StepContextPackage、StepWorkerDispatch和ProgressLedger；
- StepResult、ReviewResult、ReviewContextPackage和StageGateResult的构建或校验；
- 严格stage-review `issues.json` 到 `issues_index.json`/逐issue详情的事务化构建与校验。

查看准确命令：

```bash
python -m ai_writing_plugin --help
```

## 安装

要求：Python 3.11+、Git和Claude Code CLI。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
claude plugin validate .
```

从仓库根目录加载本地插件：

```bash
claude --plugin-dir .
```

也可以在Claude Code中把本地目录加入marketplace后安装；具体步骤见[Quickstart](docs/QUICKSTART.md)。

## 使用Claude Code入口

使用自己的task：

```text
/ai-writing-plugin:write "Run the writing workflow with path/to/task.yaml"
```

首次了解runtime协议时，可以显式选择一个fixture，例如：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_zh_demo_fixture/task.yaml"
```

Fixture是opt-in资产。运行时不会默认批量读取`examples/`。

## 使用Python Phase 0入口

Python当前可以确定性地创建run起点：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin init-run \
  --task examples/generic_document_demo_fixture/task.yaml
```

输出仅包括：

```text
runs/<run_id>/input_refs.json
runs/<run_id>/manifest.json
runs/<run_id>/task_brief.json
```

这条命令不会生成inventory、source index、draft、review、verification或final report。

## 准备task.yaml

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

路径相对于task文件所在目录解析。当前Python使用受限YAML子集解析器；复杂YAML结构会显式失败。

## 输入角色

| Role | 用途 | 能否证明项目事实 |
| --- | --- | --- |
| `source` | 项目事实、要求、结果和约束 | 相关且正确解释时可以 |
| `template` | 结构和格式 | 不可以 |
| `checklist` | 审查覆盖 | 不可以 |
| `reference` | 方法、背景和术语 | 不可以证明项目事实 |
| `sample` | 风格、形状和颗粒度 | 不可以 |

核心规则：

```text
fact source != sample document
```

## 文档类型资产状态

仓库保留四个official L3产品/domain标签：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

当前树包含相应Skills和fixtures，但没有Python document-type registry、type-specific content rules或端到端内容CLI测试。因此这里的official L3表示维护的产品/domain资产等级，不表示Python已经执行完整写作流程。

其他资产：

- `generic_document`：generic Skill/profile/task资产；当前Python不加载profile或执行generic内容流程。
- `custom_technical_note`：external profile demo；当前没有Python profile loader。
- `TechnicalSafetyConcept`：非official的skill-layer prototype，已提交Skill、step overlays和fixture；没有Python rules、registry、端到端内容CLI或专门engine test。Official L3 TSC及HSC/SSC均deferred。

## 输出与审批边界

Agent worker成功运行时，可能按step生成`knowledge/`、`plans/`、`draft/`、`review/`、`verify/`、`final/`、`trace/`和`learning/`下的artifact。它们属于worker协议的预期输出，不是`init-run`的输出保证。

- unsupported critical claims保持pending或`NEEDS_USER_CONFIRMATION`；
- hash匹配只证明文件身份，不证明内容正确；
- StepResult、ReviewResult和StageGateResult都不是专业批准；
- `final_report.md`只能是review-ready交付物；
- candidate material保持proposal，当前没有自动激活命令。

## 开发检查

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python -m ai_writing_plugin --help
claude plugin validate .
git status --short
```

`runs/`是ignored runtime output，不应提交。

## 文档导航

- [Quickstart](docs/QUICKSTART.md)
- [User Guide](docs/USER_GUIDE.md)
- [Examples](docs/EXAMPLES.md)
- [Reading Outputs](docs/READING_OUTPUTS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Runbook](docs/RUNBOOK.md)
- [Current Artifact Contracts](contracts/CURRENT_ARTIFACT_CONTRACTS.md)
- [Current Architecture](docs/maintainers/ARCHITECTURE.md)
- [Current Project Context](docs/maintainers/PROJECT_CONTEXT.md)
