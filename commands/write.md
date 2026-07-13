---
description: 运行 AI 专业文档写作 workflow，支持通过 task YAML 选择文档模式。
---

# Write Command

任务目标：$ARGUMENTS

默认用中文和用户沟通；保留命令、路径、artifact 文件名、schema 字段、`task_type`、`source`、`sample`、`reference`、`HITL`、`NEEDS_USER_CONFIRMATION` 等英文关键术语。

## Purpose

`/ai-writing-plugin:write "<task.yaml 路径或自然语言写作目标>"` 是唯一写作入口。command 层只做 task 确认、run 初始化/按 ledger 继续、runtime 边界声明，然后把执行交给 `workflow-orchestrator` 薄编排器 / thin controller；command 层不写 step artifacts、不写 StepResult、不写 ReviewResult、不做专业批准。

当前 Python 包只负责 Phase 0 scaffold 和 orchestration metadata builder/validator；它不提供一键内容引擎或 Python resume lifecycle。专业 artifacts 必须由独立 Task/Agent worker 按当前 step skill 生成。

## Inputs

- 优先使用用户提供的 task file；先读取并确认其中的 `task_type` 与输入材料来源。
- 自然语言目标必须先映射为候选 `task_type`，再确认用户要使用真实项目 task file/输入材料，还是一个用户明确指定的 demo task。未确认材料来源时不得开跑。
- 当前基线官方 L3 product/domain 标签为 `hara`、`technical_solution`、`test_report`、`fsr`；当前以 Skill/fixture assets 参与 runtime guidance，不表示存在 Python rules registry。`generic_document` 与 external profile 是设计/config assets，当前 Python 不加载 profile。
- 本仓库仍可能存在 `SystemRequirement`、`SoftwareArchitecture` 等非官方 document-type runtime dirs；不要删除、重命名或把它们改成官方类型。若 task file 明确选择这些类型，只按当前 task 路由，并在报告里记录 target drift。
- 不新增每类文档一个命令；文档差异由当前 `task_type` 的 document-type skill 表达。

## Runtime Context Rules

- Runtime files stay minimal and operational: command、orchestrator、current step wrapper/canonical、current document-type root/step overlay only.
- DocumentTypeLazyLoad：不得批量读取 `skills/document-types/**`；只把当前 `task_type` 下实际存在的 document-type path/hash 放进 StepContextPackage。wrapper 与 canonical workflow Skill 是必需引用；document-type root Skill 和 per-step overlay 都按文件存在性懒加载，root-only 模式合法，缺少可选 overlay 不是 `metadata_invalid`。worker 只能通过 StepContextPackage 中的 path/hash 读取当前 `task_type` 的 document type 文件，并必须验证所有已包含引用的 path/hash；不得读取 sibling document types。例：`task_type=hara` 时不得读取 `SoftwareArchitecture`、`SystemRequirement` 或其他 sibling document type 规则。
- 不把 maintainer docs、example tree、run output tree 当默认上下文；用户选择具体 demo 或测试 fixture 明确引用时，才读取那个 task file 及其声明 inputs。
- worker 只能读取当前用户选择的 task file 以及该 task 声明的 inputs；不得读取 sibling demo。
- Main agent must not replay artifact bodies. 不得粘贴 artifact 正文，不读取 artifact 正文，不得批量读取 step canonical，不回放 issues.json，不回放 review_units.json。
- Path/hash refs only：StepContextPackage、StepWorkerDispatch、ReviewContextPackage、StepResult、ReviewResult、StageGateResult 只在主 Agent 长期上下文中保留短摘要、路径/hash、`artifact_paths`、`artifact_hashes`、`review_package_paths`、`review_package_hashes`、`blocking_issues_count`、`next_gate_status`。
- input materials 通过 `input_refs.json` path/hash 进入 package；不得把 input body、task body、artifact body、review 明细正文传入 worker。
- fact source != sample document。sample 只能指导结构/样式/表格形状，不能支撑 HARA facts、hazards、ratings、ASIL、safety goals 或 final professional conclusions。
- final report、stage review、verification、telemetry 均不是 professional approval。

## Engine And Metadata

Step 1 启动 run 必须调用当前 Python Phase 0 scaffold：

```text
python -m ai_writing_plugin init-run --task <task.yaml>
python -m ai_writing_plugin init-progress-ledger --run-dir <run_dir>
```

固定初始化顺序是 `init-run → init-progress-ledger → prepare-step-worker-dispatch`。`init-run`失败时不得创建ledger或dispatch；三个scaffold files存在后，Step 1 worker只读核对并通过StepResult报告其path/hash。

ValidatedRuntimeMetadata：除 StepResult/ReviewResult 由独立 worker 写入外，builder-owned orchestration metadata 必须由 Python builder 生成；所有 result/package/ledger/gate metadata 都必须走对应 validator。主 Agent 不得手写 orchestration JSON，不得手动 patch ledger，不得使用 Write/Edit 手写 runtime metadata。必须使用并按需传参：

```text
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

`manifest.json` 和 `task_brief.json` 是 `init-run` 生成后的 engine-owned immutable files；`input_refs.json` 同样是 scaffold-owned read-only file。`step-input-materials` 的StepContextPackage自动引用三个scaffold files，该worker的StepResult会把 `manifest.json` 作为真实上游artifact交接给后续step。StepContextPackage.run_refs[] 只是只读引用；不得 Write/Edit/MultiEdit task_brief.json；不得 Write/Edit/MultiEdit manifest.json；也不得修改 input_refs.json。Step 1 worker 不得扩展 task_brief.json。

`prepare-step-worker-dispatch` 自动传播已验证的前序 StepResult `artifact_paths`：它必须先验证ProgressLedger、前序StepResult及其artifact path/hash，再按固定13-step顺序生成refs。合并顺序固定为“默认refs → 自动上游refs → 原package额外refs → 新显式 `--input-ref`”，按路径稳定去重。controller只传播 path/hash，不读取 artifact 正文；stage gate、decision等非StepResult输入仍必须显式传入 `--input-ref`。

当使用 `--overwrite-dispatch` 重新派发较早 step 时，已经依赖其输出的所有后续 step 元数据必须同时失效：builder原子删除这些后续 step 的旧 ContextPackage、StepWorkerDispatch 和 ProgressLedger entry，失败则逐字节回滚。controller必须按固定 13-step 顺序重新执行这些下游 step，再开始全 stage 复审；旧 StepResult 文件即使仍在固定路径，也不再是有效绑定。

固定收口顺序：validate-step-context-package → validate-step-worker-dispatch → validate-step-result → complete-step-worker-dispatch --step-result <result_path> → validate-progress-ledger。任一命令失败立即 metadata_invalid fail closed；不得开修复 worker 反复修 metadata。

## Worker Handoff

真实 worker handoff 必须使用 Task tool / Agent tool。若当前环境无 Task tool / Agent tool，必须 `worker_unavailable` fail closed；不得 fallback 到主上下文执行 step 或 review。

Step worker不得继续派发nested worker。每个stage的审核只由controller在全部StepResult完成后调度一个Stage review worker；当前run下既有的旧`subagent/`目录不读取、不迁移、不删除。

全 13 step worker handoff 统一使用 StepWorkerDispatch：`runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json`。调度 step 前生成 StepContextPackage：`runs/<run_id>/orchestration/context_packages/<stage>/<step>.json`。Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径。Review worker 只接收 ReviewContextPackage 路径：`runs/<run_id>/orchestration/review_context_packages/<stage>.json`。不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker。

Step worker 写 `runs/<run_id>/orchestration/step_results/<step>.json`；Review worker 写 `runs/<run_id>/orchestration/review_results/<stage>/<step>.json`。ProgressLedger：`runs/<run_id>/orchestration/progress_ledger.json`。StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`。

Step worker prompt 必须包含完整 StepResult 字段列表：`kind=step_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`artifact_paths`、`artifact_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。StepResult 不允许 task_type，不允许 knowledge_gaps_count，不允许 completed_at。Step worker 返回前必须自行运行 validate-step-result：`python -m ai_writing_plugin validate-step-result --run-dir <run_dir> --path <result_path>`；同一个 step worker 修正后重跑 validate-step-result。

Review worker prompt 必须包含完整 ReviewResult 字段列表：`kind=review_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。Review worker 返回前必须自行运行 validate-review-result，对每个per-step ReviewResult分别执行：`python -m ai_writing_plugin validate-review-result --run-dir <run_dir> --path <result_path>`；同一个 review worker 修正后重跑 validate-review-result，但修正仅限ReviewResult metadata，不得修改专业artifact或StepResult。

不得在 complete-step-worker-dispatch 后修改 StepResult。修改 StepResult 后必须重新运行 validate-step-result 和 complete-step-worker-dispatch。ProgressLedger 中的 step_result_ref 必须绑定最终 StepResult sha256，ProgressLedger 中的 review_result_ref 必须绑定最终 ReviewResult sha256，且不得手动修改 progress_ledger.json。

`complete-step-worker-dispatch --status` 只是一致性断言，不得覆盖 StepResult 或 ReviewResult 的 status。有ReviewResult时必须与ReviewResult.status一致，否则必须与StepResult.status一致；不一致时必须fail closed且不得写入Dispatch或Ledger。

## Per-Step Review Closure

每个 stage 只调度一个独立 review worker，但 ReviewContextPackage.steps[] 中每个 step 必须恰好对应一个 ReviewResult。review worker 按 ReviewContextPackage.steps[] 顺序，沿各 `context_package_refs[]` 读取对应 StepContextPackage 的 `result_paths.review_result`，写入 `orchestration/review_results/<stage>/<step>.json`。禁止返回单个 stage 聚合 ReviewResult；缺失、重复或额外 step 的 ReviewResult 必须 metadata_invalid fail closed。

主 Agent 逐个运行 `validate-review-result`，再使用未修改的最终 StepResult 重新运行 `complete-step-worker-dispatch --step-result <step_result_path> --review-result <review_result_path>`。每次回写后校验 ProgressLedger；全部 review_result_ref 绑定并通过 validate-progress-ledger 后，才允许 build-stage-gate-result。build-stage-gate-result 必须按相同顺序重复传入全部 --review-result。

任一 ReviewResult 为 `needs_revision` 或 `blocked` 时不得进入 `accepted` gate；全部为 `done` 仍停在 `pending_user_confirmation`，等待真实用户 decision。ReviewResult 修改后必须重新校验、重新 complete 对应 dispatch，并重新生成受影响的 StageGateResult。

Stage review worker不得修改专业artifact或StepResult。它必须按“`issues.json` → `build-stage-review-issues` → `validate-stage-review-issues` → per-step ReviewResult”生成并验证review输出：先写 `stage_reviews/<stage>/issues.json`，再由builder原子产生 `issues_index.json`/详情，最后为每step写ReviewResult。出现P0/P1或明确 `needs_revision` 时，Controller随后为每个受影响step运行 `prepare-step-worker-dispatch --overwrite-package --overwrite-dispatch`，并以 `--input-ref stage_reviews/<stage>/issues_index.json` 加入问题索引；builder会保留原ContextPackage的额外 `run_refs[]`，重置该step的旧结果绑定，并使所有后续step的旧handoff元数据失效。原step worker执行A2并写入新StepResult后，controller须按顺序重跑已失效的下游step。

多轮返工顺序固定为“A2完成 → `build-review-context-package --overwrite` 事务重置并解除旧 stage-review refs → 覆盖 issue set → 全stage复审”。所有受影响step重新complete后，controller必须先对原stage完整step列表运行 `build-review-context-package --overwrite`；命令成功后才允许review worker覆盖固定路径的issue set。该事务保留当前StepResult绑定，从ContextPackage移除已消费的旧stage-review refs，清除整个stage旧ReviewResult绑定并同步ContextPackage、Dispatch和Ledger hash。随后覆盖issue set、重新审核整个stage并重新绑定全部per-step ReviewResult；未完成这轮全stage复审时不得构建gate。

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

每个 stage gate 只记录 `stage_review_gate_only` 决策，不是专业批准。记录 `accepted` 前必须确认每个per-step ReviewResult均为 `done`、全部已在Ledger绑定、经验证的 `issues_index.json` 的 `blocking_issues_count=0`，且真实用户decision声明 `decision_scope=stage_review_gate_only` 与 `professional_approval=false`。非交互运行不得伪造 HITL；缺失用户确认时记录 pending/blocked 并停止。No auto-fix / no S2B/S3/S4，除非未来 active phase 明确要求。

当前 `build-stage-gate-result --status` 只产生结构上可校验的override，Python不会据此证明HITL。主 Agent不得把无真实decision的`accepted`/`skipped` override当作继续依据。
