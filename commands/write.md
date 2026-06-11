---
description: 运行 AI 专业文档写作 workflow，支持通过 task YAML 选择文档模式。
---

# Write Command

任务目标：$ARGUMENTS

## 交互语言

默认用中文和用户沟通。保留命令、路径、artifact 文件名、schema 字段、`task_type`、`source`、`sample`、`reference`、`HITL`、`NEEDS_USER_CONFIRMATION` 等英文关键术语。

如果用户材料是英文，可以保留原文术语、标题和引用片段；解释、步骤说明、风险提醒和最终回复优先用中文。

## 统一入口

作为 Claude Code plugin 加载后，可以使用：

```text
/ai-writing-plugin:write "Run the writing workflow with examples/hara_demo_fixture/task.yaml"
```

部分环境可能存在产品级快捷命令：

```text
/write "Run the writing workflow with examples/test_report_demo_fixture/task.yaml"
```

不要新增每种文档类型一个命令。保持一个统一入口，让 `task_type` 选择规则。

## 支持的 task_type

task YAML 选择文档模式或文档类型：

```text
task_type: hara
task_type: technical_solution
task_type: test_report
task_type: fsr
task_type: generic_document
```

External profiles 可以通过 `document_profile_path` 声明自定义 task type，例如：

```text
task_type: custom_technical_note
document_profile_path: profiles/document_types/customer_demo/custom_technical_note.yaml
```

文档类型差异由 `ai_writing_plugin/document_types/` 中的 `DocumentTypeRules` 表达。command layer 不承载文档业务逻辑；它调用 Python engine。

## Demo task files

```text
examples/hara_demo_fixture/task.yaml
examples/technical_solution_demo_fixture/task.yaml
examples/test_report_demo_fixture/task.yaml
examples/fsr_demo_fixture/task.yaml
examples/generic_document_demo_fixture/task.yaml
examples/custom_technical_note_profile_demo_fixture/task.yaml
```

如果用户提供其他 task file，先请用户给出路径，读取并确认其中声明的 `task_type`。

## Python 环境

从仓库根目录运行命令：

```bash
if [ ! -f "pyproject.toml" ] || [ ! -d "ai_writing_plugin" ]; then
  echo "Error: run this command from the AI writing plugin repository root."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Project virtualenv not found. Creating .venv and installing the project..."
  python3 -m venv .venv
  .venv/bin/python -m pip install -U pip
  .venv/bin/python -m pip install -e ".[dev]"
fi

PYTHON=".venv/bin/python"
```

后续使用 `$PYTHON -m ai_writing_plugin` 运行 engine commands。

## 非交互 smoke test

```bash
$PYTHON -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
$PYTHON -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
$PYTHON -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
$PYTHON -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml
$PYTHON -m ai_writing_plugin write-run --task examples/generic_document_demo_fixture/task.yaml
$PYTHON -m ai_writing_plugin write-run --task examples/custom_technical_note_profile_demo_fixture/task.yaml
```

helper 不能伪造 HITL approval。非交互运行会把缺失 gate 记录为 `not_collected_in_noninteractive_run` 或 `pending_user_confirmation`，并保持 candidate updates remain proposed/inactive。

## 交互 workflow

1. 用中文确认 task file 路径和 `task_type`。
2. 运行 ingest，并向用户说明 material classification。
3. 只有在用户明确回复后，才记录真实 HITL decisions。
4. 通过 Python engine 运行 outline、evidence、plan、draft、review、finalize 和 learning。
5. 用中文报告 run directory、final artifacts、pending critical claims 和 candidate update 状态。

## Engine commands

```bash
$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>
$PYTHON -m ai_writing_plugin outline-run --run <run_dir>
$PYTHON -m ai_writing_plugin evidence-run --run <run_dir>
$PYTHON -m ai_writing_plugin plan-run --run <run_dir>
$PYTHON -m ai_writing_plugin draft-run --run <run_dir>
$PYTHON -m ai_writing_plugin review-run --run <run_dir>
$PYTHON -m ai_writing_plugin finalize-run --run <run_dir>
$PYTHON -m ai_writing_plugin learning-run --run <run_dir>
$PYTHON -m ai_writing_plugin record-hitl --run <run_dir> --stage <stage> --decision <decision> --comment <comment> --affected-sections <ids> --next-action <action>
```

## Boundaries

- sample is not fact source.
- sample documents can guide structure or style only.
- expected_output_shape is not fact source.
- reference is not project-specific fact support.
- critical claims require evidence or HITL.
- Keep NEEDS_USER_CONFIRMATION when critical claims are not confirmed.
- final report is not professional approval.
- candidate updates remain proposed/inactive.
- Candidate profile updates and skill patches must not auto-activate or overwrite stable Skill files.
- Markdown Spec can generate candidate profiles through `profile-from-spec`, but it is not the runtime rule.
- external `document_profile.yaml` files must validate before use.

## HITL recording gates

只有在用户真实确认后，才记录 real user decisions。规范 gate 示例：

```bash
$PYTHON -m ai_writing_plugin record-hitl --run "$RUN_DIR" --stage task_goal_confirmation --decision approved --comment "<user confirmation text>" --affected-sections "" --next-action continue_to_ingest
$PYTHON -m ai_writing_plugin record-hitl --run "$RUN_DIR" --stage material_classification_confirmation --decision approved --comment "<user confirmation text>" --affected-sections "" --next-action continue_to_outline
$PYTHON -m ai_writing_plugin record-hitl --run "$RUN_DIR" --stage outline_l1_confirmation --decision approved --comment "<user confirmation text>" --affected-sections "SEC-001" --next-action continue_to_evidence
$PYTHON -m ai_writing_plugin record-hitl --run "$RUN_DIR" --stage evidence_confirmation --decision approved_with_issues --comment "<user confirmation text>" --affected-sections "SEC-001" --next-action continue_with_confirmation_markers
$PYTHON -m ai_writing_plugin record-hitl --run "$RUN_DIR" --stage final_delivery_confirmation --decision approved_with_open_items --comment "<user confirmation text>" --affected-sections "SEC-001" --next-action continue_to_learning
$PYTHON -m ai_writing_plugin record-hitl --run "$RUN_DIR" --stage candidate_update_confirmation --decision keep_proposed --comment "<user confirmation text>" --affected-sections "" --next-action generate_learning_artifacts_without_activation
```

## 最终回复 checklist

- 用中文报告 `runs/<run_id>/`。
- 报告 `final/final_report.md` 和 `final/delivery_summary.md`。
- 报告 `review/final_review.md` 和 `verify/verify_report.json`。
- 报告 trace 和 learning artifacts。
- 说明 candidate updates 是 proposed / inactive。
- 说明哪些 critical claims 仍然 pending，除非用户已经提供真实确认。
