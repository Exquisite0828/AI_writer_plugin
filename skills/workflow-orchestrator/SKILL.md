---
name: workflow-orchestrator
description: 中文优先薄编排器 / thin controller，按顺序调度 workflow 的 13 个 step skills。每个 step 由独立 step execution context 产出 artifacts，再由独立 review worker 审核；必须用户审核通过后才能进入下一 stage。不自动批准、不伪造 HITL。
---

# Workflow Orchestrator Skill

本 skill 是薄编排器 / thin controller：只负责状态机、metadata builder/validator、Task tool / Agent tool handoff、stage gate 和短摘要回收。它不直接写最终文档、不写 step artifacts、不写 StepResult、不写 ReviewResult、不做专业判断。

当前 Python 包只实现 run scaffold 与 orchestration metadata；不执行专业内容 stage，也不提供一键内容或 resume lifecycle。专业 artifacts 只由独立 worker 按当前 step skill 生成。

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

全 13 step worker handoff 使用 StepWorkerDispatch：`runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json`。按 metadata 继续时先读 ProgressLedger：`runs/<run_id>/orchestration/progress_ledger.json`，再按 StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json` 判断下一步；这不是 Python content-resume command。默认不回放 issues.json，不回放 review_units.json。

## Context Boundary

- Main agent keeps only stable orchestration rules, ProgressLedger, package/result path/hash refs, 短摘要 and gate state.
- 不得粘贴 artifact 正文，不读取 artifact 正文，不得批量读取 step canonical，不得把动态 artifact 内容、review 明细或输入材料全文带回长期上下文。
- StepContextPackage：`runs/<run_id>/orchestration/context_packages/<stage>/<step>.json`。Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径。
- ReviewContextPackage：`runs/<run_id>/orchestration/review_context_packages/<stage>.json`。Review worker 只接收 ReviewContextPackage 路径。
- 不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker。
- StepResult：`runs/<run_id>/orchestration/step_results/<step>.json`。ReviewResult：`runs/<run_id>/orchestration/review_results/<stage>/<step>.json`。StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`。
- StepResult / ReviewResult 主 Agent 只读短字段：`step`、`stage`、`status`、`artifact_paths`、`artifact_hashes`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。
- DocumentTypeLazyLoad：不得批量读取 `skills/document-types/**`；只把当前 `task_type` 下实际存在的 document-type path/hash 放进 StepContextPackage。wrapper 与 canonical workflow Skill 是必需引用；document-type root Skill 和 per-step overlay 都按文件存在性懒加载，root-only 模式合法，缺少可选 overlay 不是 `metadata_invalid`。worker 只能通过 StepContextPackage 中的 path/hash 读取当前 `task_type` 的 document type 文件，并必须验证所有已包含引用的 path/hash；不得读取 sibling document types。例：`task_type=hara` 时不得读取 `SoftwareArchitecture`、`SystemRequirement` 或其他 sibling document type。
- worker 只能读取当前用户选择的 task file 以及该 task 声明的 inputs；不得读取 sibling demo。

## Metadata Commands

固定初始化顺序是 `init-run → init-progress-ledger → prepare-step-worker-dispatch`。controller必须先成功创建三个Phase 0 scaffold files和ProgressLedger，才能准备Step 1 dispatch；初始化失败立即fail closed。

除 StepResult/ReviewResult 由独立 worker 写入外，builder-owned orchestration metadata 必须由 `python -m ai_writing_plugin` builder 生成；所有 result/package/ledger/gate metadata 都必须走对应 validator。主 Agent 不得手写 orchestration JSON，不得手动 patch ledger，不得使用 Write/Edit 手写 runtime metadata。

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
python -m ai_writing_plugin build-stage-review-issues
python -m ai_writing_plugin validate-stage-review-issues
python -m ai_writing_plugin validate-review-result
python -m ai_writing_plugin build-stage-gate-result
python -m ai_writing_plugin validate-stage-gate-result
```

固定 step 收口顺序：validate-step-context-package → validate-step-worker-dispatch → validate-step-result → complete-step-worker-dispatch --step-result <result_path> → validate-progress-ledger。任一命令失败立即 metadata_invalid fail closed；不得开修复 worker 反复修 metadata。

`manifest.json` 和 `task_brief.json` 是 `init-run` 生成后的 engine-owned immutable files；`input_refs.json` 同样是 scaffold-owned read-only file。`step-input-materials` 的StepContextPackage自动引用三个scaffold files，该worker的StepResult会把 `manifest.json` 作为真实上游artifact交接给后续step。StepContextPackage.run_refs[] 只是只读输入引用；不得 Write/Edit/MultiEdit task_brief.json；不得 Write/Edit/MultiEdit manifest.json；也不得修改 input_refs.json。Step 1 worker 不得扩展 task_brief.json。

`prepare-step-worker-dispatch` 自动传播已验证的前序 StepResult `artifact_paths`：它必须先验证ProgressLedger、前序StepResult及其artifact path/hash，再按固定13-step顺序生成refs。合并顺序固定为“默认refs → 自动上游refs → 原package额外refs → 新显式 `--input-ref`”，按路径稳定去重。controller只传播 path/hash，不读取 artifact 正文；stage gate、decision等非StepResult输入仍必须显式传入 `--input-ref`。

当使用 `--overwrite-dispatch` 重新派发较早 step 时，已经依赖其输出的所有后续 step 元数据必须同时失效：builder原子删除这些后续 step 的旧 ContextPackage、StepWorkerDispatch 和 ProgressLedger entry，失败则逐字节回滚。controller必须按固定 13-step 顺序重新执行这些下游 step，再开始全 stage 复审；旧 StepResult 文件即使仍在固定路径，也不再是有效绑定。

主 Agent 不得写 step artifacts，主 Agent 不得写 StepResult，主 Agent 不得写 ReviewResult。ProgressLedger 中的 step_result_ref 必须绑定最终 StepResult sha256，ProgressLedger 中的 review_result_ref 必须绑定最终 ReviewResult sha256；不得手动修改 progress_ledger.json。不得在 complete-step-worker-dispatch 后修改 StepResult。修改 StepResult 后必须重新运行 validate-step-result 和 complete-step-worker-dispatch；修改 ReviewResult 后必须重新运行 validate-review-result、重新 complete 对应 dispatch，并重新生成受影响的 StageGateResult。

`complete-step-worker-dispatch --status` 只是一致性断言，不得覆盖 StepResult 或 ReviewResult 的 status。有ReviewResult时必须与ReviewResult.status一致，否则必须与StepResult.status一致；不一致时必须fail closed且不得写入Dispatch或Ledger。

## Worker Result Contract

Task tool / Agent tool 是唯一 worker handoff 机制。若当前环境没有 Task tool / Agent tool，必须记录 `worker_unavailable` 并 fail closed；不得 fallback 到主上下文执行 step 或 review。

Step worker不得继续派发nested worker。每个stage只由controller调度一个Stage review worker；当前run下既有的旧`subagent/`目录不读取、不迁移、不删除，也不作为继续执行或gate依据。

Step worker prompt 必须包含完整 StepResult 字段列表：`kind=step_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`artifact_paths`、`artifact_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。StepResult 不允许 task_type，不允许 knowledge_gaps_count，不允许 completed_at。Step worker 返回前必须自行运行 validate-step-result：`python -m ai_writing_plugin validate-step-result --run-dir <run_dir> --path <result_path>`；同一个 step worker 修正后重跑 validate-step-result，直到通过或返回 `metadata_invalid`。

Review worker prompt 必须包含完整 ReviewResult 字段列表：`kind=review_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。Review worker 返回前必须自行运行 validate-review-result，对每个per-step ReviewResult分别执行：`python -m ai_writing_plugin validate-review-result --run-dir <run_dir> --path <result_path>`；同一个 review worker 修正后重跑 validate-review-result，但修正仅限ReviewResult metadata，直到全部通过或返回 `metadata_invalid`，不得修改专业artifact或StepResult。

## Per-Step Review Closure

每个 stage 只调度一个独立 review worker。ReviewContextPackage.steps[] 中每个 step 必须恰好对应一个 ReviewResult；review worker 按 ReviewContextPackage.steps[] 顺序，沿各 `context_package_refs[]` 读取对应 StepContextPackage 的 `result_paths.review_result`，写入 `orchestration/review_results/<stage>/<step>.json`。禁止返回单个 stage 聚合 ReviewResult；缺失、重复或额外 step 的 ReviewResult 必须 metadata_invalid fail closed。

主 Agent 按相同顺序逐个校验 ReviewResult，并使用未修改的最终 StepResult 重新运行 `complete-step-worker-dispatch --step-result <step_result_path> --review-result <review_result_path>`。每次回写后校验 ProgressLedger；全部 review_result_ref 绑定并通过 validate-progress-ledger 后，才允许 build-stage-gate-result。build-stage-gate-result 必须按相同顺序重复传入全部 --review-result。

任一 ReviewResult 为 `needs_revision` 或 `blocked` 时不得进入 `accepted` gate；全部为 `done` 仍保持 `pending_user_confirmation`，等待真实用户 decision。

Stage review worker不得修改专业artifact或StepResult。它必须按“`issues.json` → `build-stage-review-issues` → `validate-stage-review-issues` → per-step ReviewResult”生成并验证review输出：先写 `stage_reviews/<stage>/issues.json`，再由builder原子产生 `issues_index.json`/详情，最后为每step写ReviewResult。P0/P1或明确 `needs_revision` 时，Controller逐个运行 `prepare-step-worker-dispatch --overwrite-package --overwrite-dispatch`，通过 `--input-ref stage_reviews/<stage>/issues_index.json` 重新派发受影响的原step worker；builder保留原额外 `run_refs[]`、重置目标step旧结果绑定，并使所有后续step的旧handoff元数据失效。A2 worker写入并绑定新StepResult后，controller须按顺序重跑已失效的下游step。

多轮返工顺序固定为“A2完成 → `build-review-context-package --overwrite` 事务重置并解除旧 stage-review refs → 覆盖 issue set → 全stage复审”。全部A2完成并绑定新StepResult后，controller必须先对原stage完整step列表运行 `build-review-context-package --overwrite`；命令成功后才允许review worker覆盖固定路径的issue set。该事务保留当前StepResult绑定，从ContextPackage移除已消费的旧stage-review refs，清除整个stage旧ReviewResult绑定并同步ContextPackage、Dispatch和Ledger hash。随后覆盖issue set、重新审核整个stage并重新绑定全部per-step ReviewResult；完整复审通过前不得构建gate。

## Main Loop

1. 初始化/恢复：读取 ProgressLedger 和上一 stage gate；首个 stage 无上游 gate。
2. 对当前 step 运行 `prepare-step-worker-dispatch`，自动传播已验证的前序StepResult artifacts，生成 StepContextPackage 与 StepWorkerDispatch；立即运行 validators。
3. 通过 Task tool / Agent tool 调 step worker，只传 dispatch/context package 路径。worker 写 artifacts 和 StepResult，并先自校验。
4. 主 Agent 校验 StepResult，运行 `complete-step-worker-dispatch`，更新 ledger。
5. 为本 stage 生成 ReviewContextPackage，通过 Task tool / Agent tool 调一个review-only worker。worker只做A1/B审核，按issues source → builder → validator顺序生成issue set，再为 `steps[]` 中每个step生成和自校验一个ReviewResult；它不得执行A2或修改专业artifact/StepResult。
6. 主 Agent 按 `steps[]` 顺序逐个校验 ReviewResult，并用对应最终 StepResult + ReviewResult 重新 complete dispatch；校验 ledger 中全部 `review_result_ref` 的path/hash与最终结果一致。
7. 若存在P0/P1或明确 `needs_revision`，按问题索引重新prepare并派发受影响的原step worker执行A2；全部新StepResult绑定后，先以 `build-review-context-package --overwrite` 事务解除旧stage-review refs，再允许review worker覆盖issue set并重新审核整个stage，回到第6步。
8. stage review 必须完成当前可验证输出：严格 `issues.json` 已经builder生成并validator校验为当前 `issues_index.json`/详情，每个step恰有一个ReviewResult，且Ledger已绑定它们的最终path/hash。当前runtime不要求另一套review bundle或coverage state。
9. 用户明确回复后才写 `decision.json`；仅在全部per-step ReviewResult已绑定后，按顺序把它们全部传给StageGateResult builder并校验。`accepted` 的硬条件：每个ReviewResult均为 `done`、经验证的 `issues_index.json` 的 `blocking_issues_count=0`，且真实用户decision声明 `decision_scope=stage_review_gate_only` 与 `professional_approval=false`。
10. 非交互运行不得自动 `accepted`，不得伪造 HITL；缺确认时停在当前 stage。

## Forbidden Behavior

- final report is not professional approval; stage review is advisory, not professional approval.
- sample/reference 不能支撑 project facts；fact source != sample document。
- 不自动移除 `NEEDS_USER_CONFIRMATION`，不把 candidate updates 自动激活。
- No auto-fix / no S2B/S3/S4 unless a future active phase explicitly requires it.
- 不引入 RAG、向量库、LangChain 或复杂 agent framework。
- `runs/<run_id>/` 是 runtime output，不提交 git。
