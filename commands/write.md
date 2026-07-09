---
description: 运行 AI 专业文档写作 workflow，支持通过 task YAML 选择文档模式。
---

# Write Command

任务目标：$ARGUMENTS

默认用中文和用户沟通；保留命令、路径、artifact 文件名、schema 字段、`task_type`、`source`、`sample`、`reference`、`HITL`、`NEEDS_USER_CONFIRMATION` 等英文关键术语。

## Purpose

`/ai-writing-plugin:write "<task.yaml 路径或自然语言写作目标>"` 是唯一写作入口。command 层只做 task 确认、run 启动/恢复、runtime 边界声明，然后把执行交给 `workflow-orchestrator` 薄编排器 / thin controller；command 层不写 step artifacts、不写 StepResult、不写 ReviewResult、不做专业批准。

## Inputs

- 优先使用用户提供的 task file；先读取并确认其中的 `task_type` 与输入材料来源。
- 自然语言目标必须先映射为候选 `task_type`，再确认用户要使用真实项目 task file/输入材料，还是一个用户明确指定的 demo task。未确认材料来源时不得开跑。
- 当前基线官方 L3 built-ins 由仓库规则定义为 `hara`、`technical_solution`、`test_report`、`fsr`；`generic_document` 是 generic mode；`custom_technical_note` 只能通过 external `document_profile.yaml` 使用。
- 本仓库仍可能存在 `SystemRequirement`、`SoftwareArchitecture` 等非官方 document-type runtime dirs；不要删除、重命名或把它们改成官方类型。若 task file 明确选择这些类型，只按当前 task 路由，并在报告里记录 target drift。
- 不新增每类文档一个命令；文档差异由当前 `task_type` 的 document-type skill 表达。

## Runtime Context Rules

- Runtime files stay minimal and operational: command、orchestrator、current step wrapper/canonical、current document-type root/step overlay only.
- DocumentTypeLazyLoad：不得批量读取 `skills/document-types/**`；只把当前 `task_type` 的 document-type path/hash 放进 StepContextPackage。worker 只能通过 StepContextPackage 中的 path/hash 读取当前 `task_type` 的 document type 文件；不得读取 sibling document types。例：`task_type=hara` 时不得读取 `SoftwareArchitecture`、`SystemRequirement` 或其他 sibling document type 规则。
- 不把 maintainer docs、example tree、run output tree 当默认上下文；用户选择具体 demo 或测试 fixture 明确引用时，才读取那个 task file 及其声明 inputs。
- worker 只能读取当前用户选择的 task file 以及该 task 声明的 inputs；不得读取 sibling demo。
- Main agent must not replay artifact bodies. 不得粘贴 artifact 正文，不读取 artifact 正文，不得批量读取 step canonical，不回放 issues.json，不回放 review_units.json。
- Path/hash refs only：StepContextPackage、StepWorkerDispatch、ReviewContextPackage、StepResult、ReviewResult、StageGateResult 只在主 Agent 长期上下文中保留短摘要、路径/hash、`artifact_paths`、`artifact_hashes`、`review_package_paths`、`review_package_hashes`、`blocking_issues_count`、`next_gate_status`。
- input materials 通过 `input_refs.json` path/hash 进入 package；不得把 input body、task body、artifact body、review 明细正文传入 worker。
- fact source != sample document。sample 只能指导结构/样式/表格形状，不能支撑 HARA facts、hazards、ratings、ASIL、safety goals 或 final professional conclusions。
- final report、stage review、verification、telemetry 均不是 professional approval。

## Engine And Metadata

Step 1 启动 run 必须调用 deterministic engine：

```text
python -m ai_writing_plugin init-run --task <task.yaml>
python -m ai_writing_plugin init-progress-ledger --run-dir <run_dir>
```

ValidatedRuntimeMetadata：所有 orchestration metadata 必须由 Python builder 生成并由 validator 验证；不得手写 orchestration JSON，不得手动 patch ledger，不得使用 Write/Edit 手写 runtime metadata。必须使用并按需传参：

```text
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

`manifest.json` 和 `task_brief.json` 是 `init-run` 生成后的 engine-owned immutable files。StepContextPackage.run_refs[] 只是只读引用；不得 Write/Edit/MultiEdit task_brief.json，不得 Write/Edit/MultiEdit manifest.json。Step 1 worker 不得扩展 task_brief.json。

固定收口顺序：validate-step-context-package → validate-step-worker-dispatch → validate-step-result → complete-step-worker-dispatch --step-result <result_path> → validate-progress-ledger。任一命令失败立即 metadata_invalid fail closed；不得开修复 worker 反复修 metadata。

## Worker Handoff

真实 worker handoff 必须使用 Task tool / Agent tool。若当前环境无 Task tool / Agent tool，必须 `worker_unavailable` fail closed；不得 fallback 到主上下文执行 step 或 review。

全 13 step worker handoff 统一使用 StepWorkerDispatch：`runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json`。调度 step 前生成 StepContextPackage：`runs/<run_id>/orchestration/context_packages/<stage>/<step>.json`。Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径。Review worker 只接收 ReviewContextPackage 路径：`runs/<run_id>/orchestration/review_context_packages/<stage>.json`。不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker。

Step worker 写 `runs/<run_id>/orchestration/step_results/<step>.json`；Review worker 写 `runs/<run_id>/orchestration/review_results/<stage>/<step>.json`。ProgressLedger：`runs/<run_id>/orchestration/progress_ledger.json`。StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`。

Step worker prompt 必须包含完整 StepResult 字段列表：`kind=step_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`artifact_paths`、`artifact_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。StepResult 不允许 task_type，不允许 knowledge_gaps_count，不允许 completed_at。Step worker 返回前必须自行运行 validate-step-result：`python -m ai_writing_plugin validate-step-result --run-dir <run_dir> --path <result_path>`；同一个 step worker 修正后重跑 validate-step-result。

Review worker prompt 必须包含完整 ReviewResult 字段列表：`kind=review_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。Review worker 返回前必须自行运行 validate-review-result：`python -m ai_writing_plugin validate-review-result --run-dir <run_dir> --path <result_path>`；同一个 review worker 修正后重跑 validate-review-result。

不得在 complete-step-worker-dispatch 后修改 StepResult。修改 StepResult 后必须重新运行 validate-step-result 和 complete-step-worker-dispatch。ProgressLedger 中的 step_result_ref 必须绑定最终 StepResult sha256，ProgressLedger 中的 review_result_ref 必须绑定最终 ReviewResult sha256，且不得手动修改 progress_ledger.json。

## Stage Order And Gate

stage 顺序固定：`ingest → outline → evidence_planning → draft → review → finalize → learning`。

| stage | steps |
|---|---|
| `ingest` | `step-input-materials` / `step-material-inventory` / `step-source-index` |
| `outline` | `step-template-outline` |
| `evidence_planning` | `step-research-questions` / `step-evidence-map` |
| `draft` | `step-conservative-draft` |
| `review` | `step-review` / `step-verification` |
| `finalize` | `step-revision` / `step-final-report` |
| `learning` | `step-run-summary` / `step-candidate-profile-update` |

每个 stage gate 只记录 `stage_review_gate_only` 决策，不是专业批准。记录 `accepted` 前必须确认 stage-review package 完整、coverage complete、无 `severity=P0/P1` 且 `requires_revision=true` 的 issue、`professional_approval=false`。非交互运行不得伪造 HITL；缺失用户确认时记录 pending/blocked 并停止。No auto-fix / no S2B/S3/S4，除非未来 active phase 明确要求。
