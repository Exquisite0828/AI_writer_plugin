---
name: workflow-orchestrator
description: 中文优先薄编排器 / thin controller，按顺序调度 workflow 的 13 个 step skills。每个 step 由独立 step execution context 产出 artifacts，再由独立 subagent 审核并产出 stage-review 材料；必须用户审核通过（在 stage_reviews/<stage>/decision.json 落 accepted）才能进入下一步。不自动批准、不伪造 HITL。
---

# Workflow Orchestrator Skill

总控 skill 是薄编排器 / thin controller：按固定顺序调度 **13 个** registerable step skill（`ai-writing-plugin:step-*`），并在**每一步执行完毕后弹出供用户确认的问题列表**，由用户审核该步产出后才允许进入下一步。

本 skill 是编排指导层，不直接写最终文档，不直接产出 step artifacts。各 step 的 artifacts 必须由 Claude Code `Task tool` 新开的独立 step worker 按对应 step skill 产出（须符合 artifact 契约）；独立 review worker 默认只审核这些已产出的 artifacts，并在需要时产出 stage-review 材料。只有发现 P0/P1 或用户落 `decision=needs_revision` 后，才允许 review worker 进入局部修订；stage-review 闸门通过 `runs/<run_id>/stage_reviews/<stage>/decision.json` 记录，不自动批准、不伪造 HITL。

## 何时使用

- 用户希望「一步一步、每步人工确认」地走完整条专业文档写作流程。
- 需要在每个步骤产出后做人工审核，未通过不得继续。
- 作为 `/ai-writing-plugin:write` 命令「交互 workflow」的薄编排层：command 确认 task 后把控制权交给本 skill，由本 skill 逐 stage 调度 **13 个** step skill（每步先子代理审核、后用户确认闸门）。

## 核心原则

- **顺序、单向、artifact-first**：每步只消费上游 `runs/<run_id>/` 下的 artifacts。
- **step skill 注册名与正文分离**：调用 step 时使用一级注册名 `ai-writing-plugin:step-<name>`（例如 `ai-writing-plugin:step-source-index`）。每个一级 step skill 是 Claude Code 注册 wrapper；完整 canonical 说明仍在 `skills/workflow-steps/<step>/SKILL.md`，执行前必须读取并遵守该 canonical 文件。
- **薄编排器长期上下文**：主 Agent 只保留稳定编排规则、ProgressLedger 短账本、StepContextPackage 路径/hash、ReviewContextPackage 路径/hash、StepResult / ReviewResult / StageGateResult 短摘要和人工闸门状态；不得粘贴 artifact 正文，不读取 artifact 正文，不得批量读取 step canonical，不得把动态 artifact 内容、review 明细或输入材料全文带回长期上下文。
- **ProgressLedger 恢复协议**：初始化或恢复 run 时先读取 `runs/<run_id>/orchestration/progress_ledger.json`。每生成 StepContextPackage、StepResult 或 ReviewResult 后立即更新 ledger。恢复时主 Agent 只用 ledger 判断下一步；只有某个 step 需要继续、核对或阻断定位时，才按 ledger 中的 path/hash 打开单个 package/result 文件。
- **StepContextPackage 派发协议**：调度每个 step 前先生成 `runs/<run_id>/orchestration/context_packages/<stage>/<step>.json`。主 Agent 只把该 package 路径交给 step worker；step worker 从 package 中的 path/hash 读取 step wrapper、canonical step、任务专属规则和 run artifacts，不要求主 Agent 粘贴正文。
- **DocumentTypeLazyLoad**：主 Agent 只确认 `task_type`，只把当前 `task_type` 的 document-type path/hash 放进 StepContextPackage；不得批量读取 `skills/document-types/**`。worker 只能通过 StepContextPackage 中的 path/hash 读取当前 `task_type` 的 document type 文件，不得读取 sibling document types。例如 `task_type=hara` 时不得读取 `SoftwareArchitecture`、`SystemRequirement`、`SystemArchitecture`、`SoftwareRequirement`、`fsr` 或其他 sibling document type 规则。
- **ValidatedRuntimeMetadata**：所有 orchestration metadata 必须由 `python -m ai_writing_plugin` builder 生成并由 validator 验证；不得手写 orchestration JSON，不得手动 patch ledger，不得使用 Write/Edit 手写 runtime metadata。初始化 run 后必须调用 `python -m ai_writing_plugin init-progress-ledger --run-dir <run_dir>`；调度 step 前必须调用 `python -m ai_writing_plugin prepare-step-worker-dispatch`，再运行 `python -m ai_writing_plugin validate-step-context-package`、`python -m ai_writing_plugin validate-step-worker-dispatch`、`python -m ai_writing_plugin validate-progress-ledger`。Step worker 写结果后必须运行 `python -m ai_writing_plugin validate-step-result`；Review worker 写结果后必须运行 `python -m ai_writing_plugin validate-review-result`；主 Agent 完成 step 后必须调用 `python -m ai_writing_plugin complete-step-worker-dispatch`。Review 和 stage gate metadata 必须通过 `python -m ai_writing_plugin build-review-context-package`、`python -m ai_writing_plugin validate-review-context-package`、`python -m ai_writing_plugin build-stage-gate-result`、`python -m ai_writing_plugin validate-stage-gate-result` 生成和校验。任一 validator 失败必须 `metadata_invalid` fail closed，不得继续调度 worker 或进入下一步。主 Agent 不得写 step artifacts，主 Agent 不得写 StepResult，主 Agent 不得写 ReviewResult。ProgressLedger 中的 step_result_ref 必须绑定最终 StepResult sha256，ProgressLedger 中的 review_result_ref 必须绑定最终 ReviewResult sha256；不得手动修改 progress_ledger.json，不得在 complete-step-worker-dispatch 后修改 StepResult。修改 StepResult 后必须重新运行 validate-step-result 和 complete-step-worker-dispatch；修改 ReviewResult 后必须重新运行 validate-review-result，并通过 builder/validator 路径刷新 ledger 或 gate result。
- **Worker 短结果 schema 固定**：Step worker prompt 必须包含完整 StepResult 字段列表：`kind=step_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`artifact_paths`、`artifact_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。StepResult 不允许 task_type，不允许 knowledge_gaps_count，不允许 completed_at，不允许 P0/P1/P2 计数字段、revision 状态或其他未知字段。Step worker 返回前必须自行运行 validate-step-result：`python -m ai_writing_plugin validate-step-result --run-dir <run_dir> --path <result_path>`；若失败，必须由同一个 step worker 修正后重跑 validate-step-result，直到通过或返回 `metadata_invalid`。Review worker prompt 必须包含完整 ReviewResult 字段列表：`kind=review_result`、`schema_version=1`、`run_id`、`stage`、`step`、`status`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。Review worker 返回前必须自行运行 validate-review-result：`python -m ai_writing_plugin validate-review-result --run-dir <run_dir> --path <result_path>`；若失败，必须由同一个 review worker 修正后重跑 validate-review-result，直到通过或返回 `metadata_invalid`。
- **StepWorkerDispatch / 全 13 step worker handoff**：全部 13 个 workflow step 都使用 StepWorkerDispatch：`runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json`。主 Agent 必须通过 Claude Code `Task tool` / `Agent tool` 新开独立 step worker；不同运行日志可能显示为 Task tool / Agent tool，二者都表示独立 worker/subagent handoff。Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径。
- **Task tool fail closed 边界**：如果当前运行环境没有 `Task tool` / `Agent tool`，必须 fail closed：停止当前 step 或 review，记录并报告 `worker_unavailable`，不得 fallback 到主上下文执行 step 或 review，不得自行读取 canonical step 正文并产出 artifacts。
- **StepResult / ReviewResult 短返回协议**：每个 step worker 写入 `runs/<run_id>/orchestration/step_results/<step>.json`；每个 review worker 写入 `runs/<run_id>/orchestration/review_results/<stage>/<step>.json`。StepResult 短字段只包含 `step`、`stage`、`status`、`artifact_paths`、`artifact_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。ReviewResult 短字段只包含 `step`、`stage`、`status`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。
- **ReviewContextPackage 派发协议**：调度 review worker 前先生成 `runs/<run_id>/orchestration/review_context_packages/<stage>.json`。主 Agent 必须通过 `Task tool` 新开独立 review worker，并只把 package 路径交给 review worker。Review worker 只接收 ReviewContextPackage 路径。不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker；review worker 从 package 中的 StepResult path/hash 和 stage review refs 读取所需文件，不要求主 Agent 粘贴 `issues.json` 或 `review_units.json` 正文。
- **StageGateResult 短返回协议**：stage gate 完成后写入 `runs/<run_id>/orchestration/stage_gate_results/<stage>.json`。`decision.json` 仍是 stage review gate 的原始 runtime decision，StageGateResult 只是短摘要和 path/hash 索引。恢复或继续时主 Agent 先读 ProgressLedger 和 StageGateResult，默认不回放 issues.json，不回放 review_units.json；只有向用户展示具体问题时才按需打开单个 review 文件。
- **运行期上下文边界**：不得把 artifact contract、maintainer docs 或 examples 当作默认上下文。contract 只在需要精确路径或 schema 时按需读取；examples 只在用户显式选择具体 demo task 时使用。
- **路径锚定，不依赖 cwd**：所有 step 与 subagent 读取输入文件时，必须使用上游 artifact 中已经解析好的路径或派发时显式传入的绝对路径。当前 shell cwd / subagent cwd 只代表执行上下文，不得用于推导 `inputdoc/`、`runs/<run_id>/inputdoc/` 或其他输入根目录。
- **输入文档仅经 L1→L2→L3 访问**：Step 4 及以后读原始输入须遵守 `writing-core` 输入文档访问协议；禁止 chunk/SRC/直接全文盲搜。
- **每步先子代理审核、再人工确认**：每个 step 执行后先由独立 subagent 审核已产出的 artifacts（见各 step skill 的「子代理审核」小节），通过后才向用户弹出确认问题列表。确认问题列表来自该 step 的 subagent 产出（`stage_reviews/<stage>/review_prompt.md` + `review_units.json` + `issues.json`），不是凭空生成。
- **子代理轻量审核 + 条件修订**：subagent 默认只执行「审核任务」并写入 `review_state`；无 P0/P1 时不得重写 step artifacts，不得重新驱动整步任务。P2/P3 只进入 issues / review prompt 供用户确认，不自动修。只有发现 P0/P1 或用户落 `decision=needs_revision` 时，才进入 `revision_state` 修订任务。
- **局部修订，不整步重跑**：修订必须绑定具体 `issue_id`、`target_artifact`、`changed_paths`，只改受影响 artifact；不得为“更满意”、修 P2/P3、修统计/措辞小问题而重新阅读全部输入、重新生成全部目录/大纲，或为当前任务生成替代脚本整步重跑。
- **真实闸门**：用户「审核通过」必须落地为 `runs/<run_id>/stage_reviews/<stage>/decision.json`（`decision=accepted`，固定 `decision_scope=stage_review_gate_only`、`professional_approval=false`），否则不得进入下一步。`accepted` 还必须通过硬闸门：stage-review package 完整、coverage complete、无 `severity=P0/P1` 且 `requires_revision=true` 的 issue。
- **不自动批准**：禁止自动 `accepted`、禁止伪造 HITL、禁止把 sample/reference 当事实、禁止输出专业批准结论；subagent 不得移除 `NEEDS_USER_CONFIRMATION`、不得给出专业批准。
- **13 步 vs 7 个 stage 闸门**：7 个 deterministic stage 处提供真实可记录的闸门；多个 step 共用一个 stage 时，先逐个 step 向用户呈现确认问题，全部确认后再记录该 stage 的单一闸门决定，然后才跑下一 stage。

## Step → stage 映射

stage 是 stage-review 闸门记录的单元；多个 step 共用一个 stage 时共享该 stage 的单一闸门决定。各 step 的产出由 `Task tool` 新开的独立 step worker 按对应 step skill 完成；review worker 默认只做独立审核。

| Step | stage |
|---|---|
| 1 输入材料 / 2 材料清单 / 3 文档目录索引 | `ingest` |
| 4 模板大纲 | `outline` |
| 5 大纲分析与写作计划 / 6 证据·引用·章节计划 | `evidence_planning` |
| 9 保守草稿 | `draft` |
| 10 审查 / 11 验证 | `review` |
| 12 修订 / 13 最终报告 | `finalize` |
| 14 运行总结 / 15 候选 profile 更新 | `learning` |

7 个 stage 顺序固定：`ingest → outline → evidence_planning → draft → review → finalize → learning`。

## 编排主循环

对每个 stage（按上表顺序），执行以下闭环：

1. **调度本 stage 产出（step worker）**：进入本 stage 前先读取并验证 ProgressLedger：`runs/<run_id>/orchestration/progress_ledger.json`，用账本判断本 stage / step 的最近状态；再确认上一 stage 的 `runs/<run_id>/stage_reviews/<prev_stage>/decision.json` 存在且 `decision ∈ {accepted, skipped}`（首个 stage `ingest` 无上游闸门）。随后对本 stage 覆盖的每个 step（见上表），调用 `python -m ai_writing_plugin prepare-step-worker-dispatch` 生成 StepContextPackage、StepWorkerDispatch 并更新 ledger 为 `context_ready`；随后必须立即运行对应 validator，任一失败则 `metadata_invalid` fail closed。随后必须用 Claude Code `Task tool` / `Agent tool` 调用独立 step worker，并把 step artifact 生产职责交给该 worker。step worker 只接收 dispatch/context package 路径，从 package 中的 path/hash 读取 wrapper、canonical step、任务专属规则和 run artifacts，产出符合 artifact 契约的 artifacts，写入 `runs/<run_id>/orchestration/step_results/<step>.json`，并只向主 Agent 返回 StepResult 短摘要；主 Agent 随后运行 `python -m ai_writing_plugin validate-step-result` 和 `python -m ai_writing_plugin complete-step-worker-dispatch`，把 StepResult path/hash 记录进 ledger。若 `Task tool` / `Agent tool` 不可用，必须 fail closed，记录/报告 `worker_unavailable` 并停止当前 step。

2. **逐个 step 的 review worker 审核（state.json 三态推进）**：对本 stage 覆盖的每个 step，先生成 ReviewContextPackage：`runs/<run_id>/orchestration/review_context_packages/<stage>.json`，再按该 step skill 的「子代理审核」小节通过 `Task tool` 新开独立 review worker，只把 review context package 路径交给 worker。review worker 自主完成 A1 审核任务，在 `runs/<run_id>/subagent/<step>/state.json` 以 `review_state` 三态跟踪进度，并写入 `runs/<run_id>/orchestration/review_results/<stage>/<step>.json`；主 Agent 随后把该 ReviewResult path/hash 记录进 ledger。无 P0/P1 时 `revision_required=false` 且不得改写 step artifacts。P2/P3 只能记录到 `issues.json` / review prompt，等待用户确认，不得由薄编排器或 review worker 自动修订。只有发现 P0/P1 时，才按具体 issue 进入 A2 局部修订，并在 `revision_state` 记录 `issue_id`、`target_artifact`、`changed_paths`。review worker 不得伪造 HITL、不得移除 `NEEDS_USER_CONFIRMATION`、不得输出专业批准结论；主 Agent 只读取 ReviewResult 短摘要，不读取 artifact 正文。若 `Task tool` 不可用，必须 fail closed，记录/报告 `worker_unavailable` 并停止当前 review。

3. **逐个 step 说明产出**：参照本 stage 覆盖的 step skill，用中文向用户说明每个 step 产出的 artifact 与边界。

4. **生成 stage-review 包**：由本 stage 末尾的 step skill subagent 写入：

   ```text
   runs/<run_id>/stage_reviews/<stage>/review_prompt.md
   runs/<run_id>/stage_reviews/<stage>/review_units.json
   ```

   `review_units.json` 必须穷举本 stage 内每个 step 的 required units；不允许漏单元。

5. **完成 unit 级审查**：subagent 读取 `review_prompt.md` 与 `review_units.json`，对每个 required unit 逐一审查，写出 `stage_reviews/<stage>/issues.json`，必须包含：

   ```text
   reviewed_unit_ids   # 覆盖全部 required units
   unchecked_unit_ids  # 必须为空
   issues[].unit_id    # 每条 issue 必须挂在已知 unit 上
   coverage_complete   # true 仅当 unchecked_unit_ids 为空且无 reviewed/unchecked overlap
   ```

6. **校验 stage-review package 完整性**：进入用户确认前，必须基于当前文件系统重新确认 `review_prompt.md`、`review_units.json`、`issues.json` 均存在且可读取，不得依赖记忆中的“已经生成”。`review_units.json` 必须描述当前 artifact 状态；若 A2 修订过 artifact，必须同步刷新对应 unit。保留旧字段、旧 check id 或已废弃结论的 unit 视为 package 不完整。缺任一文件、`coverage_complete=false`、`unchecked_unit_ids` 非空、unknown unit id、missing coverage 或 reviewed/unchecked overlap，都视为 stage review 未完成，不得进入 accepted decision。所有 stage 都适用，包括 `review`、`finalize`、`learning`；不得因某 stage 已有 `issues.json` 而省略 `review_prompt.md`。

7. **弹出确认问题列表**：把 `issues.json` 中的 issues（按 step / unit 归类）整理成中文「待用户确认问题列表」呈现给用户，明确标注 P0/P1、`requires_revision`、`requires_user_review`、`requires_hitl` 项。此列表即用户审核本 stage 产出的依据。

8. **等待用户审核**：用户逐项确认。未获明确「通过」前，**不得**进行第 9 步。

9. **记录闸门决定**：用户回复后，由总控 skill 在以下路径落盘 decision（`decided_by` 写用户标识或 `interactive_user`）：

   ```text
   runs/<run_id>/stage_reviews/<stage>/decision.json
   ```

   schema：

   ```yaml
   stage: <stage>
   decision: accepted | needs_revision | blocked | skipped
   decision_scope: stage_review_gate_only      # 固定值
   professional_approval: false                 # 固定值
   notes: "<用户审核结论原文>"
   decided_by: "<user>"
   decided_at: "<ISO 8601 时间戳>"
   issues_hash: "<issues.json 的 SHA-256，绑定本次决定>"
   ```

   `decision` 取值：`accepted` / `needs_revision` / `blocked` / `skipped`（`skipped` 必须填 `notes`）。只有 `accepted` 或 `skipped` 才允许进入下一 stage。`coverage_complete=false` 不得标 `accepted`。

   `accepted` 的硬条件：

   - `review_prompt.md`、`review_units.json`、`issues.json` 均存在且可读取。
   - `review_units.json` 描述当前 artifact 状态；若 A2 修订过 artifact，相关 unit 已同步刷新，不含旧字段、旧 check id 或已废弃结论。
   - `issues.json.coverage_complete=true`，`unchecked_unit_ids=[]`，所有 issue 都绑定已知 `unit_id`。
   - `issues[]` 中不存在 `severity=P0` 或 `severity=P1` 且 `requires_revision=true` 的 issue。
   - `professional_approval=false`。

   写 `decision.json` 前必须重新读取目录和 `issues.json` 做一次 fail-closed check。任一硬条件不满足时，不得 `accepted`；必须记录 `needs_revision` 或 `blocked`。缺 `review_prompt.md`、`review_units.json` 或 `issues.json` 时固定 `blocked`，notes 写明 `stage_review_package_incomplete` 和缺失文件名。`skipped` 只能用于用户明确跳过 advisory review 的非阻断场景，不得用于绕过 P0/P1、缺失 package 或 incomplete coverage。非交互运行不得自动接受 P0/P1，只能显式报告阻断原因并停在当前 stage。decision 落盘后立即生成 StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`；主 Agent 恢复/继续时用 StageGateResult 判断能否进入下一 stage，而不是回放 `issues.json` / `review_units.json` 正文。

10. **进入下一 stage**：`decision.json` 落盘且 `decision ∈ {accepted, skipped}` 后，回到第 1 步处理下一个 stage。

## 审核不通过的处理

- 用户发现问题 → 落 `decision=needs_revision`（或 `blocked`），**不要**进入下一 stage。
- 按 issues 修正：交由对应 step 的 subagent 走 A2 局部修订任务。修订必须绑定具体 issue，只读取修订所需的最小 artifact / 原文片段，只改 `target_artifact`，并在 `state.json` 的 `revision_state` 记录 `issue_id`、`target_artifact`、`changed_paths`；不得整步重跑或重新生成无关 artifacts。修订产出仍须符合 artifact 契约与边界、保持可追溯。修订后重新走 `生成 stage-review 包 → 审查 → 用户确认 → 落 decision(accepted)` 闭环。
- 真实人工确认（如 critical claim 的 HITL）由总控 skill 追加写入 `runs/<run_id>/hitl_log.jsonl`；非交互运行不得伪造。

## 边界与约束

- 本 skill 不生成草稿、不产出 step artifacts、不做专业判断、不下最终结论；这些由对应 step worker 按 artifact 契约产出，review worker 只做独立审核与必要的局部修订。
- `final/final_report.md` 是 review-ready package，不等于专业批准。
- 候选物（`candidate_profile_update.yaml` / `candidate_skill_patch.md`）保持 proposed/inactive，不在编排中自动启用。
- 不引入 RAG / 向量库 / 复杂 agent 框架；不为单一文档类型新建并行 pipeline。
- `runs/<run_id>/` 是本地 runtime 输出，不提交 git。
