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

## 交互 workflow（由 workflow-orchestrator 总控 skill 编排）

本命令的交互编排统一交给 **`workflow-orchestrator`** 总控 skill 执行；它按固定顺序驱动 `skills/workflow-steps/` 下的 15 个 step skill，并对每一步做到「**先子代理审核、后用户确认闸门**」。command 层只负责确认 task、准备 Python 环境、把控制权交给总控 skill；真实产出仍由下方 Python engine 命令完成。

1. 用中文确认 task file 路径和 `task_type`。**无 task.yaml 时先向用户索取路径与输入材料，不要凭空开跑**（自由文本如「写一份 HARA 报告」不能直接驱动引擎）。
2. 启用 **`workflow-orchestrator`** skill 作为总控，按其「编排主循环」逐 engine stage 推进；每个 stage 覆盖的 step 见下方映射表，逐 step 调用对应 step skill。
3. 每个 step 执行后，按该 step skill 的「子代理审核」小节**新开独立 subagent**：自主完成 A1 审核任务与 A2 修订任务的分解与执行，在 `runs/<run_id>/subagent/<step>/state.json` 以 `review_state` / `revision_state` 三态（`not_run` / `running` / `done`）跟踪进度；修订采用「提取脚本目的、重新驱动」，不机械重跑原命令。循环直到无 P0/P1 且全部子任务 `done`。
4. subagent 审核通过后，再向用户弹出 stage-review 确认问题列表，走真实闸门 `prepare-stage-review → validate-stage-review → record-stage-review-decision → check-stage-review-gate`；未获 `accepted` / `skipped` 不得进入下一 stage。S1/S1R/S2A/S2B 的细节见下文对应小节。
5. 只有在用户明确回复后，才记录真实 HITL decisions；非交互运行不得伪造，缺失 gate 记为 `not_collected_in_noninteractive_run` / `pending_user_confirmation`。
6. 如果中途中断，优先用 `resume-run --run <run_dir>` 从 `run_state.json` 继续；不要从头创建新 run，除非 `resume-run` 明确提示 task/profile hash mismatch、missing run_state 或 dirty completed stage。
7. 用中文报告 run directory、final artifacts、pending critical claims 和 candidate update 状态。

### Stage → step skill 映射（总控 skill 据此逐 step 驱动）

| 引擎 stage | step skill（按顺序） |
|---|---|
| `ingest` | `step-input-materials` / `step-material-inventory` / `step-source-index` |
| `outline` | `step-template-outline` |
| `evidence` | `step-research-questions` / `step-evidence-map` |
| `planning` | `step-citation-plan` / `step-section-tasks` |
| `draft` | `step-conservative-draft` |
| `review` | `step-review` / `step-verification` |
| `finalize` | `step-revision` / `step-final-report` |
| `learning` | `step-run-summary` / `step-candidate-profile-update` |

stage 顺序固定：`ingest → outline → evidence → planning → draft → review → finalize → learning`。多个 step 共用一个 stage 时，先逐个 step 完成「子代理审核 + 向用户呈现确认问题」，全部确认后再记录该 stage 的单一闸门决定，然后跑下一 stage。完整编排闭环见 `workflow-orchestrator` skill，各步边界与 A1/A2 分解见对应 step skill。

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
$PYTHON -m ai_writing_plugin resume-run --run <run_dir>
$PYTHON -m ai_writing_plugin record-hitl --run <run_dir> --stage <stage> --decision <decision> --comment <comment> --affected-sections <ids> --next-action <action>
$PYTHON -m ai_writing_plugin prepare-stage-review --run <run_dir> --stage <stage>
$PYTHON -m ai_writing_plugin validate-stage-review --run <run_dir> --stage <stage>
$PYTHON -m ai_writing_plugin record-stage-review-decision --run <run_dir> --stage <stage> --decision <accepted|needs_revision|blocked|skipped> --notes <notes>
$PYTHON -m ai_writing_plugin check-stage-review-gate --run <run_dir> --stage <stage>
$PYTHON -m ai_writing_plugin write-run --task <task_yaml> --require-stage-review-gates
$PYTHON -m ai_writing_plugin resume-run --run <run_dir> --require-stage-review-gates
```

`ingest-run` 和 `write-run` 会创建 `runs/<run_id>/run_state.json`。如果 Claude Code 会话关闭或 Python 进程中断，下一次从仓库根目录运行：

```bash
$PYTHON -m ai_writing_plugin resume-run --run runs/<run_id>
```

`resume-run` 只恢复 deterministic engine lifecycle，不代表 professional approval。它不会伪造 HITL decisions，不会自动激活 candidate updates，也不会把 dirty completed stage 自动回滚重跑。

## Stage review S1/S1R/S2A flow

在某个 stage 完成后，可以准备 advisory review package：

```bash
$PYTHON -m ai_writing_plugin outline-run --run "$RUN_DIR"
$PYTHON -m ai_writing_plugin prepare-stage-review --run "$RUN_DIR" --stage outline
```

然后读取：

```text
runs/<run_id>/stage_reviews/outline/review_prompt.md
runs/<run_id>/stage_reviews/outline/review_context.json
runs/<run_id>/stage_reviews/outline/review_units.json
```

Claude Code 只允许在同一目录下写：

```text
runs/<run_id>/stage_reviews/outline/claude_review.md
runs/<run_id>/stage_reviews/outline/issues.json
```

`issues.json` 必须包含：

```text
reviewed_unit_ids
unchecked_unit_ids
issues[].unit_id
```

必须按 `review_units.json` 中的 `unit_id` 逐项审查，不要只做整体总结。每个 required unit 都必须加入 `reviewed_unit_ids`。S1R 不允许 partial review；`unchecked_unit_ids` 非空、unknown unit id、missing coverage 或 reviewed/unchecked overlap 都会导致 validation failed。

随后校验：

```bash
$PYTHON -m ai_writing_plugin validate-stage-review --run "$RUN_DIR" --stage outline
```

用户确认当前 stage review gate decision 后，可以记录并检查：

```bash
$PYTHON -m ai_writing_plugin record-stage-review-decision --run "$RUN_DIR" --stage outline --decision accepted --notes "Reviewed."
$PYTHON -m ai_writing_plugin check-stage-review-gate --run "$RUN_DIR" --stage outline
```

`stage_reviews/<stage>/decision.json` 是 runtime assistance artifact，不写入 `manifest.artifacts`。它固定 `decision_scope=stage_review_gate_only` 和 `professional_approval=false`，并用 hash 绑定当前 `validation_report.json` 与 `issues.json`。`accepted` / `skipped` does not indicate professional approval。

Stage review is advisory. It is not professional approval. `coverage_complete=true` is not professional approval. It does not apply fixes in S1/S1R/S2A. It must not add project facts, treat sample/reference as fact support, remove `NEEDS_USER_CONFIRMATION`, or modify original stage artifacts.

## Stage review S2B opt-in gated workflow

S2B adds opt-in stage review gate enforcement via `--require-stage-review-gates`.

Default `write-run`, `resume-run`, and stage commands remain non-gated. With the flag:

- `write-run --require-stage-review-gates` creates the run, completes `ingest`, then stops.
- `resume-run --require-stage-review-gates` checks the previous stage gate, executes one pending stage, then stops.
- `outline-run`, `evidence-run`, `plan-run`, `draft-run`, `review-run`, `finalize-run`, and `learning-run` with the flag check the previous stage gate before running.
- gate missing, invalid validation, incomplete coverage, `needs_revision` / `blocked`, or hash mismatch fails closed.

Example:

```bash
$PYTHON -m ai_writing_plugin write-run --task <task_yaml> --require-stage-review-gates
$PYTHON -m ai_writing_plugin prepare-stage-review --run "$RUN_DIR" --stage ingest
# Claude Code reads review_prompt.md and review_units.json, then writes issues.json only.
$PYTHON -m ai_writing_plugin validate-stage-review --run "$RUN_DIR" --stage ingest
$PYTHON -m ai_writing_plugin record-stage-review-decision --run "$RUN_DIR" --stage ingest --decision accepted --notes "Reviewed."
$PYTHON -m ai_writing_plugin check-stage-review-gate --run "$RUN_DIR" --stage ingest
$PYTHON -m ai_writing_plugin resume-run --run "$RUN_DIR" --require-stage-review-gates
```

`accepted` / `skipped` does not indicate professional approval. `coverage_complete=true` does not indicate professional approval. S2B does not call Claude Code, does not apply fixes, and does not modify professional artifacts.

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
