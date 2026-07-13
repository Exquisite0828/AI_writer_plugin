# Quickstart

这份文档说明当前仓库真实可用的两条路径：Claude Code agent运行时和Python Phase 0/metadata工具。

## 1. 安装

```bash
git clone <repository-url>
cd <repository-directory>
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

校验插件manifest：

```bash
claude plugin validate .
```

`validate`只检查manifest，不会把命令加载进已经打开的Claude Code会话。

## 2. 加载本地插件

从仓库根目录启动新会话：

```bash
claude --plugin-dir .
```

进入新会话后，使用：

```text
/ai-writing-plugin:write "Run the writing workflow with path/to/task.yaml"
```

该入口是agent-worker协议，不是Python一键写作命令。它要求宿主环境提供Task/Agent worker。每个stage完成后需要独立review和用户gate；缺少worker时应报告`worker_unavailable`并停止。

## 3. 选择一个明确fixture

第一次可以显式选择中文技术方案fixture：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_zh_demo_fixture/task.yaml"
```

这只是opt-in演示输入。当前pytest验证的是scaffold和编排metadata，不证明该fixture已经由Python端到端生成专业报告。

## 4. 仅运行Python Phase 0

不用Claude Code worker时，可以验证当前Python起点：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin init-run \
  --task examples/generic_document_demo_fixture/task.yaml
```

命令输出run目录，并只创建：

```text
input_refs.json
manifest.json
task_brief.json
```

它不会生成下游专业artifact。当前CLI没有`write-run`或`resume-run`。

## 5. 用自己的材料

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

`inputs[*].path`相对于`task.yaml`解析。当前parser支持受限YAML结构；不支持的结构会显式失败。

## 6. 理解两类输出

Python `init-run`输出：

```text
input_refs.json
manifest.json
task_brief.json
```

Agent-worker协议在真实step运行后可能继续生成：

```text
orchestration/
knowledge/
plans/
draft/
review/
verify/
revised/
final/
trace/
learning/
```

后者不是Python Phase 0输出保证。阅读方法见[Reading Outputs](READING_OUTPUTS.md)。

## 7. 当前边界

- 四个official L3标签是`hara`、`technical_solution`、`test_report`、`fsr`，当前以Skill/fixture资产存在；
- 当前Python没有document-type registry或内容engine；
- external profile文件当前不会被Python加载；
- TSC只有非official Skill/overlay/fixture prototype；
- sample不是fact source；
- stage gate和final report都不是专业批准。

## 8. 基础验证

```bash
.venv/bin/python -m ai_writing_plugin --help
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
claude plugin validate .
```

常见问题见[Troubleshooting](TROUBLESHOOTING.md)。
