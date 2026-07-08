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
/ai-writing-plugin:write "<用户提供的 task.yaml 路径或自然语言写作目标>"
```

自然语言快捷意图也可以被识别，但必须映射到明确的 `task_type` 与材料来源：

```text
/ai-writing-plugin:write "写一份 HARA 危害分析报告"
/ai-writing-plugin:write "写一份 SyRS 系统需求报告"
/ai-writing-plugin:write "写一份系统架构报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SystemRequirement 系统需求报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SystemArchitecture 系统架构报告"
/ai-writing-plugin:write "写一份 SwRS 软件需求报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SoftwareRequirement 软件需求报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SoftwareArchitecture 软件架构报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SwAD 软件架构报告"
```

自然语言须映射到 `task_type`，并继续确认用户要使用真实项目材料、用户提供的 task file，还是一个明确指定的 demo task。不得把 demo 目录当作默认输入来源。

自然语言 → `task_type` 映射（识别后须再确认 demo 或真实 `task.yaml`）：

| 用户表述（示例） | `task_type` |
|---|---|
| HARA、危害分析、危害分析报告 | `hara` |
| SystemRequirement、SyRS、系统需求 | `SystemRequirement` |
| SystemArchitecture、系统架构、SYS.3、系统架构报告 | `SystemArchitecture` |
| SoftwareRequirement、SwRS、软件需求、软件需求规格 | `SoftwareRequirement` |
| SoftwareArchitecture、SwAD、软件架构、SWE.2 | `SoftwareArchitecture` |

注意区分：**系统需求**（`SystemRequirement`，SyRS）与 **软件需求**（`SoftwareRequirement`，SwRS）不可混用；**系统架构**（SYS.3）与 **软件架构**（SWE.2）不可混用。

若用户没有提供 task.yaml 或输入材料：

- 明确说是 demo / 示例时，要求用户确认一个具体 demo task file；不得扫描或批量读取 `examples/`。
- 真实项目写作时，先要求用户提供 task.yaml 或输入材料清单，不得凭空生成项目事实。

部分环境可能存在产品级快捷命令：

```text
/write "<用户提供的 task.yaml 路径或自然语言写作目标>"
```

不要新增每种文档类型一个命令。保持一个统一入口，让 `task_type` 选择规则。

## 支持的 task_type

task YAML 选择文档模式或文档类型：

```text
task_type: hara
task_type: technical_solution
task_type: test_report
task_type: fsr
task_type: FunctionalSafetyRequirement
task_type: ItemDefinitionDocument
task_type: TechnicalSafetyConcept
task_type: SystemRequirement
task_type: SystemArchitecture
task_type: SoftwareRequirement
task_type: SoftwareArchitecture
task_type: generic_document
```

External profiles 可以通过 `document_profile_path` 声明自定义 task type，例如：

```text
task_type: custom_technical_note
document_profile_path: profiles/document_types/customer_demo/custom_technical_note.yaml
```

文档类型差异由 `skills/document-types/<task_type>/SKILL.md` 中的规则表达。command layer 不承载文档业务逻辑；它把控制权交给 `workflow-orchestrator` 总控 skill。

## Task file boundary

如果用户提供 task file，先读取并确认其中声明的 `task_type`。如果用户选择 demo，必须由用户显式确认具体 demo task file；command layer 不维护 demo catalog，不默认遍历 `examples/`，也不把 examples 当作项目事实来源。

## 交互 workflow（由 workflow-orchestrator 薄编排器 / thin controller 编排）

本命令的交互编排统一交给 **`workflow-orchestrator`** 薄编排器 / thin controller 执行；它按固定顺序调度 **13 个** step skill，并对每一步做到「**ProgressLedger 恢复、StepContextPackage 派发、StepWorkerDispatch 派发、Task tool 独立 step worker 产出、Task tool 独立 review worker 审核、ReviewContextPackage 派发、StageGateResult 短返回、后用户确认闸门**」。command 层只负责确认 task、启动或恢复 run、把控制权交给总控 skill，不手写或手动创建 run 起点。Step 1 启动 run 时必须调用 deterministic engine：`python -m ai_writing_plugin init-run --task <task.yaml>`，随后初始化或读取 ProgressLedger：`runs/<run_id>/orchestration/progress_ledger.json`。全 13 step worker handoff 统一使用 StepWorkerDispatch：`runs/<run_id>/orchestration/worker_dispatches/<stage>/<step>.json`，主 Agent 必须通过 Claude Code `Task tool` 新开独立 step worker，并只把 dispatch/context package 路径交给 worker。Step worker 只接收 StepWorkerDispatch 路径和 StepContextPackage 路径。各 step 的 artifacts 由独立 step worker 按对应 step skill 和 artifact 契约写入 `runs/<run_id>/`；主 Agent 的长期上下文只保留稳定编排规则、ProgressLedger 短账本、StepWorkerDispatch 路径/hash、StepContextPackage 路径/hash、ReviewContextPackage 路径/hash、StepResult / ReviewResult / StageGateResult 短摘要和人工闸门状态。

主 Agent 作为薄编排器时必须遵守上下文边界：不得粘贴 artifact 正文，不读取 artifact 正文，不得批量读取 step canonical，不得把动态 artifact 内容、review 明细或输入材料全文带回长期上下文。恢复或继续 run 时，主 Agent 先读取 ProgressLedger 判断下一步，再按需读取 StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`；默认不回放 issues.json，不回放 review_units.json。只有某个 step 需要继续、核对或阻断定位时，才按 ledger 中的 path/hash 打开单个 StepWorkerDispatch、StepContextPackage、StepResult 或 ReviewResult。调度每个 step 前先生成 StepContextPackage：`runs/<run_id>/orchestration/context_packages/<stage>/<step>.json`，再生成 StepWorkerDispatch，并通过 `Task tool` 只把 dispatch/context package 路径交给 step worker。step worker 从 package 中的 path/hash 读取所需文件。每个 step worker 写入 StepResult：`runs/<run_id>/orchestration/step_results/<step>.json`，每个 review worker 写入 ReviewResult：`runs/<run_id>/orchestration/review_results/<stage>/<step>.json`。调度 review worker 前先生成 ReviewContextPackage：`runs/<run_id>/orchestration/review_context_packages/<stage>.json`，并通过 `Task tool` 只把 package 路径交给 review worker。Review worker 只接收 ReviewContextPackage 路径。不得把 artifact 正文、canonical 正文或 review 明细正文传给 worker。stage gate 完成后写入 StageGateResult：`runs/<run_id>/orchestration/stage_gate_results/<stage>.json`；`decision.json` 仍是 stage review gate 的原始 runtime decision，StageGateResult 只是短摘要和 path/hash 索引。每生成 StepContextPackage、StepWorkerDispatch、StepResult、ReviewResult、ReviewContextPackage 或 StageGateResult 后立即更新或参考 ProgressLedger。主 Agent 只读取这些结果 JSON 的短字段：`step`、`stage`、`status`、`artifact_paths`、`artifact_hashes`、`review_package_paths`、`review_package_hashes`、`summary`、`blocking_issues_count`、`next_gate_status`。如果当前运行环境没有 `Task tool`，必须 fail closed：停止当前 step 或 review，记录并报告 `worker_unavailable`，不得 fallback 到主上下文执行 step 或 review，不得自行读取 canonical step 正文并产出 artifacts。

1. 用中文确认 task file 路径和 `task_type`。若用户只给自然语言意图，先映射到候选 `task_type`（例如 HARA → `hara`；SystemRequirement / SyRS / 系统需求 → `SystemRequirement`；SystemArchitecture / 系统架构 / SYS.3 → `SystemArchitecture`；SoftwareRequirement / SwRS / 软件需求 → `SoftwareRequirement`；SoftwareArchitecture / SwAD / 软件架构 / SWE.2 → `SoftwareArchitecture`），再确认是使用用户明确指定的 demo task，还是等待用户提供真实 task.yaml / 输入材料。真实项目**无 task.yaml 或输入材料时不要凭空开跑**。
2. 启用 **`workflow-orchestrator`** skill 作为薄编排器，按其「编排主循环」逐 stage 推进；每个 stage 覆盖的 step 见下方映射表，逐 step 生成 StepContextPackage 和 StepWorkerDispatch 后，必须通过 `Task tool` 调度对应 step worker。
3. 每个 step 执行后，按该 step skill 的「子代理审核」小节通过 `Task tool` **新开独立 review worker**：调度前先生成 ReviewContextPackage 并只传 package 路径，默认只完成 A1 审核任务，在 `runs/<run_id>/subagent/<step>/state.json` 以 `review_state` 三态（`not_run` / `running` / `done`）跟踪进度。无 P0/P1 时 `revision_required=false`，不得重写 step artifacts、不得重新驱动整步任务；只有发现 P0/P1 或用户明确 `needs_revision` 时，才执行 A2 局部修订，并把 `issue_id`、`target_artifact`、`changed_paths` 写入 `revision_state`。
4. subagent 审核完成后，先确认 stage-review package 完整且 `issues.json` 可审查，再向用户弹出 stage-review 确认问题列表；用户回复 `accepted` / `needs_revision` / `blocked` / `skipped` 后，由总控 skill 在 `runs/<run_id>/stage_reviews/<stage>/decision.json` 落盘决定，并写入 StageGateResult。未获 `accepted` / `skipped` 不得进入下一 stage；package 不完整、coverage 不完整，或存在 `severity=P0/P1` 且 `requires_revision=true` 的 issue 时，不得记录 `accepted`，也不得用 `skipped` 绕过。
5. 只有在用户明确回复后，才记录真实 HITL decisions；非交互运行不得伪造，缺失 gate 记为 `not_collected_in_noninteractive_run` / `pending_user_confirmation`。
6. 如果中途中断，下一次会话从仓库根目录重新调用本命令并指向同一 `runs/<run_id>/`，由总控 skill 先读取 `orchestration/progress_ledger.json` 判断下一步；只有需要继续某个 step 时，才按账本 path/hash 打开对应 package/result 文件，并按需核对 `run_state.json` / `manifest.yaml` / `subagent/<step>/state.json`。不要从头创建新 run，除非 task/profile hash mismatch 或上一 stage 显式 dirty。
7. 用中文报告 run directory、final artifacts、pending critical claims 和 candidate update 状态。

### Stage → step skill 映射（总控 skill 据此逐 step 驱动）

| stage | step skill（按顺序） |
|---|---|
| `ingest` | `step-input-materials` / `step-material-inventory` / `step-source-index` |
| `outline` | `step-template-outline` |
| `evidence_planning` | `step-research-questions` / `step-evidence-map` |
| `draft` | `step-conservative-draft` |
| `review` | `step-review` / `step-verification` |
| `finalize` | `step-revision` / `step-final-report` |
| `learning` | `step-run-summary` / `step-candidate-profile-update` |

stage 顺序固定：`ingest → outline → evidence_planning → draft → review → finalize → learning`。

多个 step 共用一个 stage 时，先逐个 step 完成「子代理审核 + 向用户呈现确认问题」，全部确认后再记录该 stage 的单一闸门决定，然后跑下一 stage。完整编排闭环见 `workflow-orchestrator` skill，各步边界与 A1/A2 分解见对应 step skill。

## Stage review 流程

每个 stage 完成后，由对应 step skill 的 subagent 把 advisory review 材料写到；这些材料只服务于 stage-review gate，不得修改原 stage artifacts：

```text
runs/<run_id>/stage_reviews/<stage>/review_prompt.md
runs/<run_id>/stage_reviews/<stage>/review_units.json
runs/<run_id>/stage_reviews/<stage>/issues.json
```

`issues.json` 必须包含：

```text
reviewed_unit_ids
unchecked_unit_ids
issues[].unit_id
```

必须按 `review_units.json` 中的 `unit_id` 逐项审查，不要只做整体总结。每个 required unit 都必须加入 `reviewed_unit_ids`；`unchecked_unit_ids` 非空、unknown unit id、missing coverage 或 reviewed/unchecked overlap 都视为 review 未完成。

记录 `accepted` 前必须先满足以下硬条件：

- `review_prompt.md`、`review_units.json`、`issues.json` 均存在且可读取；缺任一文件时 package 不完整，不得 `accepted`。
- `review_units.json` 必须描述当前 artifact 状态；若 A2 修订过 artifact，必须同步刷新对应 unit。保留旧字段、旧 check id 或已废弃结论的 unit 视为 package 不完整。
- `issues.json.coverage_complete=true`，且 `unchecked_unit_ids=[]`，无 unknown unit id，且 reviewed / unchecked 无重叠。
- `issues[]` 中不存在 `severity=P0` 或 `severity=P1` 且 `requires_revision=true` 的 issue。
- `professional_approval=false`；stage review 只能表示 gate decision，不表示专业批准。

写 `decision.json` 前必须按当前文件系统重新检查上述文件，不得依赖记忆中的“已经生成”。任一硬条件不满足时，decision 必须为 `needs_revision` 或 `blocked`。缺 `review_prompt.md`、`review_units.json` 或 `issues.json` 时固定 `blocked`，notes 写明 `stage_review_package_incomplete` 和缺失文件名。非交互运行不得自动接受 P0/P1；只能显式报告阻断原因并停止在当前 stage。

用户确认 gate decision 后，由总控 skill 在同目录写入 `decision.json`：

```text
runs/<run_id>/stage_reviews/<stage>/decision.json
```

固定 `decision_scope=stage_review_gate_only` 和 `professional_approval=false`，并用 hash 绑定当前 `issues.json`。

Stage review is advisory. It is not professional approval. `coverage_complete=true` is not professional approval. Stage review 不得修改原 stage artifacts，不得添加 project facts，不得把 sample / reference 当事实支撑，不得移除 `NEEDS_USER_CONFIRMATION`。

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
- external `document_profile.yaml` files must validate before use.

## HITL recording gates

只有在用户真实确认后，才记录 real user decisions。由总控 skill 把每次确认追加到 `runs/<run_id>/hitl_log.jsonl`，每条记录含：

```text
stage              # e.g. task_goal_confirmation / material_classification_confirmation / outline_l1_confirmation / evidence_confirmation / final_delivery_confirmation / candidate_update_confirmation
decision           # approved / approved_with_issues / approved_with_open_items / keep_proposed / needs_revision / blocked
comment            # 用户原文确认内容
affected_sections  # 关联章节 ID（可空）
next_action        # continue_to_<stage> / continue_with_confirmation_markers / generate_learning_artifacts_without_activation 等
recorded_at        # ISO 8601 时间戳
```

非交互运行不得伪造任何 HITL 记录；缺失 gate 写 `not_collected_in_noninteractive_run` 或 `pending_user_confirmation`，candidate updates 保持 proposed / inactive。

## 最终回复 checklist

- 用中文报告 `runs/<run_id>/`。
- 报告 `final/final_report.md` 和 `final/delivery_summary.md`。
- 报告 `review/final_review.md` 和 `verify/verify_report.json`。
- 报告 trace 和 learning artifacts。
- 说明 candidate updates 是 proposed / inactive。
- 说明哪些 critical claims 仍然 pending，除非用户已经提供真实确认。
