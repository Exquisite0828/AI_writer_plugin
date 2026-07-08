# Repository Runbook

这是 generalized AI 专业文档写作 Claude Code 插件的当前运行维护说明。

当前 official L3 built-in document types：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

扩展支持模式：

- `generic_document`：L1 generic mode。
- validated external `document_profile.yaml`：L2 external profile mechanism，包括 `custom_technical_note` external profile demo。

如果本地存在历史 archive 目录，不要把它当成当前执行指令。

## Environment

所有命令默认从仓库根目录运行。推荐 runtime：

```bash
.venv/bin/python
```

如果 `.venv/` 不存在：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
```

## Core validation

完整 pytest：

```bash
.venv/bin/python -m pytest -q
```

Claude Code plugin 校验：

```bash
claude plugin validate .
```

这两个命令是提交前的基础检查。pytest 覆盖 deterministic engine、document type rules、artifact contract、eval、correction harvesting、demo fixtures 和文档约束；plugin validate 检查 `.claude-plugin/plugin.json` 和 command 结构。

## Demo runs

运行六类 demo：

```bash
.venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/generic_document_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/custom_technical_note_profile_demo_fixture/task.yaml
```

常见完成状态：

```text
completed_with_candidate_updates_proposed
```

这表示 workflow 完成，并生成 proposed/inactive candidate updates。它不表示专业批准。

## Stage commands

当前 tracked Python scaffold 已实现 Phase 0 run 起点命令：

```bash
.venv/bin/python -m ai_writing_plugin init-run --task examples/generic_document_demo_fixture/task.yaml
```

该命令只创建 `manifest.json` 与 `task_brief.json`，不预创建下游 stage 目录。完整 Phase 0-8 deterministic engine 目标暴露以下 stage commands，后续 engine phase 应按 artifact contract 逐步补齐：

```text
init-run
ingest-run
outline-run
evidence-run
plan-run
draft-run
review-run
finalize-run
learning-run
resume-run
record-hitl
prepare-stage-review
validate-stage-review
write-run
```

Claude Code 入口：

```text
/ai-writing-plugin:write
```

`write-run` 是非交互式完整链路 helper。它不会伪造 HITL approval。

`ingest-run` 和 `write-run` 会创建 `runs/<run_id>/run_state.json`，用于断点续写。`init-run` 保持非 resumable。

如果 Claude Code 或 Python 进程中断，使用：

```bash
.venv/bin/python -m ai_writing_plugin resume-run --run runs/<run_id>
```

`resume-run` 会从第一个非 `done` stage 继续执行。完成后的 run-level `completed` 只表示 deterministic engine lifecycle 完成，不表示专业批准、合规批准或候选更新批准。

典型恢复流程：

1. 找到上次输出的 `runs/<run_id>/`。
2. 确认目录内存在 `run_state.json`。
3. 不修改原 `task.yaml` 和 external `document_profile.yaml`。
4. 执行 `resume-run --run runs/<run_id>`。
5. 完成后照常检查 `review/`、`verify/`、`final/`、`trace/` 和 `learning/` artifacts。

`resume-run` 会拒绝：

- missing `run_state.json`；
- `task.yaml` hash mismatch；
- external `document_profile.yaml` hash mismatch；
- live `.run_state.lock`；
- completed stage output 缺失、空文件、JSON/JSONL 不可解析。

如果 `.run_state.lock` 中的 PID 已不存在，工具会按 stale lock recovery 处理，把之前的 `running` stage 标记为 `interrupted` 后继续。

## Stage review package

Stage Review Gate S1/S1R/S2A 可以在某个 stage 完成后生成 advisory review package，供 Claude Code 读取后做语义审查，并由用户显式记录 stage review gate decision：

```bash
.venv/bin/python -m ai_writing_plugin prepare-stage-review --run runs/<run_id> --stage outline
```

输出位置：

```text
runs/<run_id>/stage_reviews/<stage>/review_context.json
runs/<run_id>/stage_reviews/<stage>/review_prompt.md
runs/<run_id>/stage_reviews/<stage>/issues_schema.json
runs/<run_id>/stage_reviews/<stage>/review_units.json
```

Claude Code 可以读取 `review_prompt.md`、`review_context.json` 和 `review_units.json`，然后只在同一目录下写：

```text
claude_review.md
issues.json
```

S1R 要求 `issues.json` 声明：

```text
reviewed_unit_ids
unchecked_unit_ids
issues[].unit_id
```

每个 required review unit 都必须出现在 `reviewed_unit_ids` 中。S1R 不允许 partial review；`unchecked_unit_ids` 非空、unknown unit id、issue 引用未知 `unit_id` 或 reviewed/unchecked 重叠都会导致 validation failed。

校验 review issues：

```bash
.venv/bin/python -m ai_writing_plugin validate-stage-review --run runs/<run_id> --stage outline
```

可选地指定 issues 文件：

```bash
.venv/bin/python -m ai_writing_plugin validate-stage-review --run runs/<run_id> --stage outline --issues-file path/to/issues.json
```

`validation_report.json` 会写入 `coverage_summary`，其中 `coverage_complete=true` 只表示 required review units 已被 deterministic coverage validation 接受，不表示 professional approval。

记录 S2A gate decision：

```bash
.venv/bin/python -m ai_writing_plugin record-stage-review-decision --run runs/<run_id> --stage outline --decision accepted --notes "Reviewed."
```

`decision` 只允许 `accepted`、`skipped`、`needs_revision`、`blocked`。`skipped` 必须有非空 notes。该命令生成：

```text
runs/<run_id>/stage_reviews/<stage>/decision.json
```

`decision.json` 固定 `decision_scope=stage_review_gate_only` 且 `professional_approval=false`，并记录 `validation_report_sha256` 和 `issues_sha256`。`accepted` / `skipped` 只表示用户允许该 stage review gate 继续；it does not indicate professional approval。

检查 gate：

```bash
.venv/bin/python -m ai_writing_plugin check-stage-review-gate --run runs/<run_id> --stage outline
```

checker 要求 validation report 仍为 `valid`、`coverage_complete=true`、decision 为 `accepted` 或 `skipped`、`professional_approval=false`，并且 `validation_report.json` / `issues.json` hash 未在 decision 后改变。

`stage_reviews/` 是 runtime assistance output，不写入 `manifest.artifacts`，不改变 `run_state.json` lifecycle，不证明项目事实，也不表示 professional approval。S1/S1R/S2A 不调用 Claude Code，不自动修改原 artifacts，不应用 patch，不阻塞下一 stage。

## Stage Review Gate S2B opt-in gated workflow

S2B 是 opt-in gate enforcement。默认 `write-run`、`resume-run` 和 single-stage commands 保持 non-gated 行为。只有显式传入 `--require-stage-review-gates` 时，engine 才会在进入下一阶段前读取上一阶段的 S2A artifacts 并 fail closed。

启动 gated workflow：

```bash
.venv/bin/python -m ai_writing_plugin write-run --task <task.yaml> --require-stage-review-gates
```

该命令只创建 run 并完成 `ingest`，然后停止。下一步是为 `ingest` 准备和记录 stage review gate：

```bash
.venv/bin/python -m ai_writing_plugin prepare-stage-review --run <run_dir> --stage ingest
# Claude Code reads review_prompt.md and review_units.json, then writes issues.json only.
.venv/bin/python -m ai_writing_plugin validate-stage-review --run <run_dir> --stage ingest
.venv/bin/python -m ai_writing_plugin record-stage-review-decision --run <run_dir> --stage ingest --decision accepted --notes "Reviewed."
.venv/bin/python -m ai_writing_plugin check-stage-review-gate --run <run_dir> --stage ingest
.venv/bin/python -m ai_writing_plugin resume-run --run <run_dir> --require-stage-review-gates
```

每次 gated `resume-run` 最多执行一个 pending stage。执行前会检查 immediate previous stage gate；执行成功后立即停止，并提示为刚完成的 stage 准备 review package。

带 flag 的 single-stage commands 也会检查上一阶段 gate：

```bash
.venv/bin/python -m ai_writing_plugin outline-run --run <run_dir> --require-stage-review-gates
.venv/bin/python -m ai_writing_plugin evidence-run --run <run_dir> --require-stage-review-gates
.venv/bin/python -m ai_writing_plugin plan-run --run <run_dir> --require-stage-review-gates
.venv/bin/python -m ai_writing_plugin draft-run --run <run_dir> --require-stage-review-gates
.venv/bin/python -m ai_writing_plugin review-run --run <run_dir> --require-stage-review-gates
.venv/bin/python -m ai_writing_plugin finalize-run --run <run_dir> --require-stage-review-gates
.venv/bin/python -m ai_writing_plugin learning-run --run <run_dir> --require-stage-review-gates
```

S2B only reads:

```text
stage_reviews/<stage>/validation_report.json
stage_reviews/<stage>/issues.json
stage_reviews/<stage>/decision.json
```

S2B 不调用 Claude Code，不自动生成 `issues.json`，不自动修改 professional artifacts，不应用 safe auto-fix，不改变 `run_state.json` schema。`accepted` / `skipped` does not indicate professional approval，`coverage_complete=true` 也不表示 professional approval。

## Focused regression matrix

常用 focused regression：

```bash
.venv/bin/python -m pytest tests/test_document_type_rules.py -q
.venv/bin/python -m pytest tests/test_generalization_phase0_hara_baseline.py -q
.venv/bin/python -m pytest tests/test_generalization_phase2_engine_rules_integration.py -q
.venv/bin/python -m pytest tests/test_technical_solution_demo.py -q
.venv/bin/python -m pytest tests/test_test_report_demo.py -q
.venv/bin/python -m pytest tests/test_fsr_demo.py -q
.venv/bin/python -m pytest tests/test_generic_document_demo.py -q
.venv/bin/python -m pytest tests/test_document_profile_demo.py -q
.venv/bin/python -m pytest tests/test_skill_guidelines.py -q
.venv/bin/python -m pytest tests/test_generalization_phase4_skills.py -q
.venv/bin/python -m pytest tests/test_generalization_phase6_product_docs.py -q
```

完整回归仍然是：

```bash
.venv/bin/python -m pytest -q
```

## Eval regression

运行 deterministic eval runner：

```bash
.venv/bin/python -m ai_writing_plugin.eval.runner --cases tests/evals/cases --output runs/eval-regression
```

检查输出中的 `expectation_mismatch_count`。期望值通常应为 `0`。

eval passed 只表示 deterministic engineering regression 通过，不表示专业批准、合规批准或内容可直接发布。

## Artifact checks

对任意 `runs/<run_id>/`，重点检查：

```text
inputs/input_inventory.json
knowledge/source_index.json
knowledge/provenance_index.json
plans/claim_support_matrix.json
plans/citation_plan.json
draft/full_draft.md
review/review_report.json
review/final_review.md
verify/verify_report.json
verify/failures.md
revision_plan.json
final/final_report.md
final/delivery_summary.md
trace/hitl_decisions.jsonl
learning/candidate_profile_update.yaml
learning/candidate_skill_patch.md
learning/promotion_report.md
```

关键审查顺序：

```text
source_index -> provenance_index -> claim_support_matrix -> review_report -> verify_report -> final_report -> delivery_summary
```

## Sample / reference boundary check

确认：

- `source_index` 没有 sample fact source entries；
- `citation_plan` 没有 sample fact evidence；
- `reference` entries 不能作为 project-specific facts 的 `fact_support`，除非未来有明确设计变更；
- `sample` / `reference` 不能证明 HARA facts、technical decisions、test results、pass/fail、defect state、coverage 或 release readiness；
- critical claims 必须有 T0/T1 support，否则保持 pending / open / `NEEDS_USER_CONFIRMATION`；
- T3/T4/T5 本身不能支持 critical claim。

可搜索关键词：

```text
sample fact source
reference fact_support
source_index
citation_plan
```

## Candidate update check

在 `learning/candidate_profile_update.yaml` 中，期望状态：

```text
status: proposed
active: false
auto_applied: false
rollback_supported: true
```

`candidate_profile_update` 和 `candidate_skill_patch` 只是 proposal。

## Profile and Markdown Spec check

- external `document_profile.yaml` 必须通过 validation 后才能使用；
- `profile-from-spec` 只生成 candidate profiles；
- `Markdown Spec` 是上游说明层，不是 runtime rule；
- `custom_technical_note` 是 external profile demo，不是 official L3 document type；
- candidate profiles 和 candidate skill patches 不能自动覆盖 active profiles 或 stable Skill files。

## Leakage checks

对 `technical_solution`，user-facing outputs 不应出现 HARA-only terms，例如 `ASIL`、`S/E/C`、`hazardous event` 或 `safety goal`。

对 `test_report`，user-facing outputs 不应出现 HARA-only terms，也不应出现 technical_solution-only terms，例如 `architecture decision` 或 `rollout risk acceptance`。

对 `fsr`，user-facing outputs 可以包含用户提供的 HARA trace、safety goal 和 ASIL terms，但不能变成 TSC deliverable。可扫描 TSC-only deliverable phrases，例如 `Technical Safety Concept final report`、`Technical Safety Requirement table`、`TSC approval statement` 或 `technical safety mechanism completeness`。

不要把稳定 machine fields（例如 check ids）误判为用户可见 prose，除非它们真的进入了用户可见输出。

## Common failures

- `verify_report.json` 为 `blocked`：常见原因是 HITL confirmations 仍 pending，非交互 demo 中可能是预期行为；
- `final_report.md` 包含 open confirmations：对未确认 critical claims 是预期行为；
- `sample` 出现在 `source_index` 作为事实来源：blocking defect；
- candidate update 自动变为 active：blocking defect；
- run artifacts 出现在 git status：从 staging 移除，并保持 `runs/` ignored。

## Git hygiene

不要提交：

```text
runs/
.venv/
.pytest_cache/
__pycache__/
generalization_phase*_execution_package.md
generalization_phase*_handoff.md
```

提交前检查：

```bash
git status --short
git status --short -- runs/
git ls-files runs/
git diff --stat
git diff --cached --stat
```

`runs/` 应为空或仅包含未跟踪且被 ignore 的本地 runtime outputs。只提交有意的 source、fixture、test、skill 或 docs changes。
