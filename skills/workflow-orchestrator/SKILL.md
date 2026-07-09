---
name: workflow-orchestrator
description: 中文优先薄编排器 / thin controller，按顺序调度 workflow 的 13 个 step skills。每个 step 由独立 step execution context 产出 artifacts，再由独立 review worker 审核；必须用户审核通过后才能进入下一 stage。不自动批准、不伪造 HITL。
---

# Workflow Orchestrator Skill

本 skill 是薄编排器 / thin controller：只负责状态机、metadata builder/validator、Task tool / Agent tool handoff、stage gate 和短摘要回收。它不直接写最终文档、不写 step artifacts、不写 StepResult、不写 ReviewResult、不做专业判断。

## State Machine

stage 顺序固定：`ingest → outline → evidence_planning → draft → review → finalize → learning`。

| stage | step skill |
|---|---|
| `ingest` | `step-input-materials` / `step-material-inventory` / `step-source-index` |
| `outline` | `step-template-outline` |
| `evidence_planning` | `step-research-questions` / `step-evidence-map` |
| `draft` | `step-conservative-draft` |
| `review` | `step-review` / `step-verification` |
| `finalize` | `step-revision` / `step-final-report` |
| `learning` | `step-run-summary` / `step-candidate-profile-update` |

全 13 step worker handoff 使用 StepWorkerDispatch：`runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json`。恢复 run 时先读 ProgressLedger：`runs/<run_id>/orchestration/progress_ledger.json`，再按 StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json` 判断下一步；默认不回放 issues.json，不回放 review_units.json。

## Context Boundary

- Main agent keeps only stable orchestration rules, ProgressLedger, package/result path/hash refs, 短摘要 and gate state.
- 不得粘贴 artifact 正文，不读取 artifact 正文，不得批量读取 step canonical，不得把动态 artifact 内容、review 明细或输入材料全文带回长期上下文。
- StepContextPackage：`runs/<run_id>/orchestration/context_packages/<stage>/<step>.json`。Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径。
- ReviewContextPackage：`runs/<run_id>/orchestration/review_context_packages/<stage>.json`。Review worker 只接收 ReviewContextPackage 路径。
- 不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker。
- StepResult：`runs/<run_id>/orchestration/step_results/<step>.json`。ReviewResult：`runs/<run_id>/orchestration/review_results/<stage>/<step>.json`。StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`。
- StepResult / ReviewResult 主 Agent 只读短字段：`step`、`stage`、`status`、`artifact_paths`、`artifact_hashes`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。
- DocumentTypeLazyLoad：不得批量读取 `skills/document-types/**`；只把当前 `task_type` 的 document-type path/hash 放进 StepContextPackage。worker 只能通过 StepContextPackage 中的 path/hash 读取当前 `task_type` 的 document type 文件，不得读取 sibling document types。例：`task_type=hara` 时不得读取 `SoftwareArchitecture`、`SystemRequirement` 或其他 sibling document type。
- worker 只能读取当前用户选择的 task file 以及该 task 声明的 inputs；不得读取 sibling demo。

## Metadata Commands

所有 orchestration metadata 必须由 `python -m ai_writing_plugin` builder 生成并由 validator 验证；不得手写 orchestration JSON，不得手动 patch ledger，不得使用 Write/Edit 手写 runtime metadata。

```text
python -m ai_writing_plugin init-progress-ledger --run-dir <run_dir>
python -m ai_writing_plugin prepare-step-worker-dispatch
python -m ai_writing_plugin validate-step-context-package
python -m ai_writing_plugin validate-step-worker-dispatch
python -m ai_writing_plugin validate-progress-ledger
python -m ai_writing_plugin validate-step-result
python -m ai_writing_plugin complete-step-worker-dispatch
python -m ai_writing_plugin build-review-context-package
python -m ai_writing_plugin validate-review-context-package
python -m ai_writing_plugin validate-review-result
python -m ai_writing_plugin build-stage-gate-result
python -m ai_writing_plugin validate-stage-gate-result
```

固定 step 收口顺序：validate-step-context-package → validate-step-worker-dispatch → validate-step-result → complete-step-worker-dispatch --step-result <result_path> → validate-progress-ledger。任一命令失败立即 metadata_invalid fail closed；不得开修复 worker 反复修 metadata。

`manifest.json` 和 `task_brief.json` 是 `init-run` 生成后的 engine-owned immutable files。StepContextPackage.run_refs[] 中的文件只是只读输入引用；不得 Write/Edit/MultiEdit task_brief.json；不得 Write/Edit/MultiEdit manifest.json。Step 1 worker 不得扩展 task_brief.json。

主 Agent 不得写 step artifacts，主 Agent 不得写 StepResult，主 Agent 不得写 ReviewResult。ProgressLedger 中的 step_result_ref 必须绑定最终 StepResult sha256，ProgressLedger 中的 review_result_ref 必须绑定最终 ReviewResult sha256；不得手动修改 progress_ledger.json。不得在 complete-step-worker-dispatch 后修改 StepResult。修改 StepResult 后必须重新运行 validate-step-result 和 complete-step-worker-dispatch；修改 ReviewResult 后必须重新运行 validate-review-result，并通过 builder/validator 路径刷新 ledger 或 gate result。

## Worker Result Contract

Task tool / Agent tool 是唯一 worker handoff 机制。若当前环境没有 Task tool / Agent tool，必须记录 `worker_unavailable` 并 fail closed；不得 fallback 到主上下文执行 step 或 review。

Step worker prompt 必须包含完整 StepResult 字段列表：`kind=step_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`artifact_paths`、`artifact_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。StepResult 不允许 task_type，不允许 knowledge_gaps_count，不允许 completed_at。Step worker 返回前必须自行运行 validate-step-result：`python -m ai_writing_plugin validate-step-result --run-dir <run_dir> --path <result_path>`；同一个 step worker 修正后重跑 validate-step-result，直到通过或返回 `metadata_invalid`。

Review worker prompt 必须包含完整 ReviewResult 字段列表：`kind=review_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。Review worker 返回前必须自行运行 validate-review-result：`python -m ai_writing_plugin validate-review-result --run-dir <run_dir> --path <result_path>`；同一个 review worker 修正后重跑 validate-review-result，直到通过或返回 `metadata_invalid`。

## Main Loop

1. 初始化/恢复：读取 ProgressLedger 和上一 stage gate；首个 stage 无上游 gate。
2. 对当前 step 运行 `prepare-step-worker-dispatch`，生成 StepContextPackage 与 StepWorkerDispatch；立即运行 validators。
3. 通过 Task tool / Agent tool 调 step worker，只传 dispatch/context package 路径。worker 写 artifacts 和 StepResult，并先自校验。
4. 主 Agent 校验 StepResult，运行 `complete-step-worker-dispatch`，更新 ledger。
5. 为本 stage 生成 ReviewContextPackage，通过 Task tool / Agent tool 调 review worker；默认只做 A1 审核。P0/P1 或用户 `needs_revision` 时才允许 A2 局部修订，且修订绑定 `issue_id`、`target_artifact`、`changed_paths`。
6. stage-review package 必须完整：`review_prompt.md`、`review_units.json`、`issues.json` 均存在且当前；`coverage_complete=true`；`unchecked_unit_ids=[]`；无 unknown unit id 或 reviewed/unchecked overlap。
7. 用户明确回复后才写 `decision.json`，再生成并校验 StageGateResult。`accepted` 的硬条件：package 完整、coverage complete、无 `severity=P0/P1` 且 `requires_revision=true` 的 issue、`professional_approval=false`。
8. 非交互运行不得自动 `accepted`，不得伪造 HITL；缺确认时停在当前 stage。

## Forbidden Behavior

- final report is not professional approval; stage review is advisory, not professional approval.
- sample/reference 不能支撑 project facts；fact source != sample document。
- 不自动移除 `NEEDS_USER_CONFIRMATION`，不把 candidate updates 自动激活。
- No auto-fix / no S2B/S3/S4 unless a future active phase explicitly requires it.
- 不引入 RAG、向量库、LangChain 或复杂 agent framework。
- `runs/<run_id>/` 是 runtime output，不提交 git。
