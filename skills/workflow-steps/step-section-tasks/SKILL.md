---
name: step-section-tasks
description: 中文优先指导 workflow 第 8 步「章节任务」：由 plan-run 生成 section_tasks.json、outline_final.md 与 writing_plan.md，把大纲分解为可执行写作任务。
---

# Step 8 · 章节任务 (Section Tasks)

工作流第 8 步。把最终大纲分解为逐章节的写作任务，明确每节使用哪些来源与引用，形成写作计划。

## 何时使用

- 已完成 Step 7（引用计划）。
- 需要在草稿前确定每个章节的写作输入与边界。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin plan-run --run <run_dir>
```

## 输入

- `plans/citation_plan.json`、`plans/claim_support_matrix.json`
- `plans/template_structure.json`、`plans/outline_l1.md`、`plans/evidence_map.json`

## 产出 artifacts

- `plans/outline_final.md`
- `plans/section_tasks.json`
- `plans/writing_plan.md`

## 边界与约束

- 章节任务只规划"写什么、用哪些来源"，不在此步生成正文。
- 保留 strict_template 的强制章节要求。
- 无证据章节须标注 open / pending，不预先下结论。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（strict_template 强制章节保留与无证据章节标 open/pending）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对章节任务是否只规划"写什么、用哪些来源"而未生成正文；② 核对 strict_template 强制章节是否保留；③ 核对无证据章节是否标注 open/pending；④ 核对 section_tasks/writing_plan 是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「把 outline_final 各章节分解为逐章节写作任务」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 一节一任务直接映射；方案B 按章节复杂度拆粗/细粒度任务；方案C 按证据充分度分组（充分/待证）排序任务。试跑对比后择优。
2. **分解与执行（第一性原理：以「大纲章节」逐节为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 遍历 outline_final 各章节；② 为每节建写作任务（含引用槽与约束）；③ 标注依赖与 HITL pending；④ 汇总 writing_plan 并校验章节覆盖完整。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "section-tasks",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对章节任务只规划而未生成正文", "status": "done"},
      {"id": "rv-2", "desc": "核对 strict_template 强制章节保留", "status": "running"},
      {"id": "rv-3", "desc": "核对无证据章节标注 open/pending", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 outline_final 各章节", "status": "done"},
      {"id": "rt-2", "desc": "为每节建写作任务（含引用槽与约束）", "status": "running"},
      {"id": "rt-3", "desc": "标注依赖与 HITL pending", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总 writing_plan 并校验覆盖完整", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`plans/outline_final.md`、`plans/section_tasks.json`、`plans/writing_plan.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：章节任务是否只规划"写什么、用哪些来源"而未生成正文，strict_template 强制章节是否保留，无证据章节是否标注 open / pending。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin plan-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 把 citation_plan 各章节转为逐章节写作任务 `TASK-xxx`，确定 writing_mode（supported / conservative_candidate / confirmation_required / open_issue_list / unsupported_stub）。
   - 为每个任务登记来源支撑、claim 状态（needs_confirmation/supported/…）与 future_output_path。
   - 渲染最终大纲 `plans/outline_final.md` 与写作计划 `plans/writing_plan.md`（含 supported/mixed/unsupported/需确认任务统计）。
   - 只规划"写什么、用哪些来源"，不在此步生成正文。
   - 保留 strict_template 强制章节，无证据章节标 open/pending。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 9 · 保守草稿**（`draft/full_draft.md`）。
