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

Python deterministic engine 暴露以下 stage commands：

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
record-hitl
write-run
```

Claude Code 入口：

```text
/ai-writing-plugin:write
```

`write-run` 是非交互式完整链路 helper。它不会伪造 HITL approval。

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
