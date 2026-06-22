---
name: step-candidate-profile-update
description: 中文优先指导 workflow 第 15 步「候选 profile 更新」：由 learning-run 生成 candidate_profile_update.yaml、candidate_skill_patch.md 与 promotion_report.md，均为 proposed/inactive 提案，不自动启用。
---

# Step 15 · 候选 profile 更新 (Candidate Profile Update)

工作流第 15 步（收尾）。根据本次 run 提炼候选 profile 更新与 skill patch 提案，等待独立人工审查与受控启用。

## 何时使用

- 已完成 Step 14（运行总结）。
- 需要把本次经验沉淀为候选改进物，但**不**立即修改稳定 profile/skill。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin learning-run --run <run_dir>
```

可选的受控提升与人工修正流程：

```bash
$PYTHON -m ai_writing_plugin correction-harvest --run-dir <run_dir> --corrections <file> --profile <profile_yaml>
$PYTHON -m ai_writing_plugin profile-promote --run-dir <run_dir> --candidate-patch <patch> --eval-report <eval> --target-profile <profile_yaml> [--apply]
```

## 输入

- `learning/run_summary.md`、`learning/reusable_patterns.md`、`trace/*`

## 产出 artifacts

- `learning/candidate_profile_update.yaml`
- `learning/candidate_skill_patch.md`
- `learning/promotion_report.md`

## 边界与约束

- 候选物默认 **proposed / inactive**，不得自动覆盖稳定 Skill 文件或自动启用 profile。
- 不实现自动 skill 替换、候选自动提升或 profile 自动学习。
- `candidate_skill_patch.md` 必须经独立人工审查流程才能应用。
- `profile-promote --apply` 需通过 eval + 显式人工批准 gate 才允许写入外部 profile。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按候选 artifact 逐项核对；方案C 先扫高风险约束（候选物是否保持 proposed/inactive 与未自动覆盖稳定 Skill）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对候选物是否保持 proposed/inactive；② 核对是否未自动覆盖稳定 Skill 或自动启用 profile；③ 核对 promotion_report.md 是否未被写成批准；④ 核对候选 artifact 是否符合契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「从本次 run 提炼候选 profile 更新与 skill patch 提案，保持 proposed/inactive」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 从 run_summary/patterns 逐条提候选；方案B 按候选类型（模板/规则/profile 字段）分组提取；方案C 先比对现有 profile 差异再提增量候选。试跑对比后择优。
2. **分解与执行（第一性原理：以「候选项逐条」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 收集本次 run 可复用信号；② 逐条生成候选物（固定 proposed/inactive）；③ 标注证据与适用范围；④ 校验未自动启用、未覆盖稳定 profile/skill。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "candidate-profile-update",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对候选物保持 proposed/inactive", "status": "done"},
      {"id": "rv-2", "desc": "核对未自动覆盖稳定 Skill 或启用 profile", "status": "running"},
      {"id": "rv-3", "desc": "核对 promotion_report.md 未被写成批准", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "收集本次 run 可复用信号", "status": "done"},
      {"id": "rt-2", "desc": "逐条生成候选物（固定 proposed/inactive）", "status": "running"},
      {"id": "rt-3", "desc": "标注证据与适用范围", "status": "not_run"},
      {"id": "rt-4", "desc": "校验未自动启用、未覆盖稳定 profile/skill", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`learning/candidate_profile_update.yaml`、`learning/candidate_skill_patch.md`、`learning/promotion_report.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：候选物是否保持 proposed / inactive，是否未自动覆盖稳定 Skill 文件或自动启用 profile，`promotion_report.md` 是否未被写成批准。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin learning-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 生成候选 profile 更新 `learning/candidate_profile_update.yaml`，固定 status: proposed / active: false / auto_applied: false / requires_user_approval: true。
   - 生成候选 skill patch `learning/candidate_skill_patch.md`（target 指向 `skills/document-types/<type>/SKILL.md`，Status: proposed_only，标注未应用）。
   - 候选物保持 proposed/inactive，不自动启用，不覆盖 stable profile 或 Skill。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接

工作流结束。状态如 `completed_with_candidate_updates_proposed`，仍非专业批准。
