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
/ai-writing-plugin:write "Run the writing workflow with examples/item_definition_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/functional_safety_requirement_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/system_requirement_demo_fixture/task.yaml"
```

自然语言快捷意图也可以被识别，但必须映射到明确的 `task_type` 与材料来源：

```text
/ai-writing-plugin:write "写一份 HARA 危害分析报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SystemRequirement 系统需求报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SyRS 系统需求报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SoftwareRequirement 软件需求报告"
/ai-writing-plugin:write "写一份汽车控制器产品 SwRS 软件需求报告"
```

若用户没有提供 task.yaml 或输入材料：

- 明确说是 demo / 示例时，可提示并使用对应 `examples/*_demo_fixture/task.yaml`。
- 真实项目写作时，先要求用户提供 task.yaml 或输入材料清单，不得凭空生成项目事实。

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
task_type: FunctionalSafetyRequirement
task_type: ItemDefinitionDocument
task_type: TechnicalSafetyConcept
task_type: SystemRequirement
task_type: SoftwareRequirement
task_type: generic_document
```

External profiles 可以通过 `document_profile_path` 声明自定义 task type，例如：

```text
task_type: custom_technical_note
document_profile_path: profiles/document_types/customer_demo/custom_technical_note.yaml
```

文档类型差异由 `skills/document-types/<task_type>/SKILL.md` 中的规则表达。command layer 不承载文档业务逻辑；它把控制权交给 `workflow-orchestrator` 总控 skill。

## Demo task files

```text
examples/hara_demo_fixture/task.yaml
examples/technical_solution_demo_fixture/task.yaml
examples/test_report_demo_fixture/task.yaml
examples/fsr_demo_fixture/task.yaml
examples/functional_safety_requirement_demo_fixture/task.yaml
examples/item_definition_demo_fixture/task.yaml
examples/technical_safety_concept_demo_fixture/task.yaml
examples/system_requirement_demo_fixture/task.yaml
examples/generic_document_demo_fixture/task.yaml
examples/custom_technical_note_profile_demo_fixture/task.yaml
```

如果用户提供其他 task file，先请用户给出路径，读取并确认其中声明的 `task_type`。

## 交互 workflow（由 workflow-orchestrator 总控 skill 编排）

本命令的交互编排统一交给 **`workflow-orchestrator`** 总控 skill 执行；它按固定顺序驱动 **13 个** step skill，并对每一步做到「**先子代理审核、后用户确认闸门**」。command 层只负责确认 task、把控制权交给总控 skill。各 step 的 artifacts 由对应 step skill 的 subagent 按 artifact 契约写入 `runs/<run_id>/`。

1. 用中文确认 task file 路径和 `task_type`。若用户只给自然语言意图，先映射到候选 `task_type`（例如 HARA → `hara`；SystemRequirement / SyRS / 系统需求 → `SystemRequirement`；SoftwareRequirement / SwRS / 软件需求 → `SoftwareRequirement`），再确认是使用 demo fixture 还是等待用户提供 task.yaml / 输入材料。真实项目**无 task.yaml 或输入材料时不要凭空开跑**。
2. 启用 **`workflow-orchestrator`** skill 作为总控，按其「编排主循环」逐 stage 推进；每个 stage 覆盖的 step 见下方映射表，逐 step 调用对应 step skill。
3. 每个 step 执行后，按该 step skill 的「子代理审核」小节**新开独立 subagent**：自主完成 A1 审核任务与 A2 修订任务的分解与执行，在 `runs/<run_id>/subagent/<step>/state.json` 以 `review_state` / `revision_state` 三态（`not_run` / `running` / `done`）跟踪进度。循环直到无 P0/P1 且全部子任务 `done`。
4. subagent 审核通过后，再向用户弹出 stage-review 确认问题列表；用户回复 `accepted` / `needs_revision` / `blocked` / `skipped` 后，由总控 skill 在 `runs/<run_id>/stage_reviews/<stage>/decision.json` 落盘决定。未获 `accepted` / `skipped` 不得进入下一 stage。
5. 只有在用户明确回复后，才记录真实 HITL decisions；非交互运行不得伪造，缺失 gate 记为 `not_collected_in_noninteractive_run` / `pending_user_confirmation`。
6. 如果中途中断，下一次会话从仓库根目录重新调用本命令并指向同一 `runs/<run_id>/`，由总控 skill 读取既有 `run_state.json` / `manifest.yaml` / `subagent/<step>/state.json` 继续；不要从头创建新 run，除非 task/profile hash mismatch 或上一 stage 显式 dirty。
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

每个 stage 完成后，由对应 step skill 的 subagent 把 advisory review 材料写到：

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
