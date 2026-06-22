---
name: step-revision
description: 中文优先指导 workflow 第 12 步「修订」：由 finalize-run 生成 revision_plan.json 与 revised/full_draft.md、change_log.md，按审查与验证结果确定性修订草稿。
---

# Step 12 · 修订 (Revision)

工作流第 12 步。基于审查报告与验证失败项，生成确定性修订计划并产出修订后草稿与变更日志。

## 何时使用

- 已完成 Step 10/11（审查与验证），run 处于 phase_6。
- 需要把审查/验证发现转化为可追溯的修订。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin finalize-run --run <run_dir>
```

（修订与最终报告由同一条 `finalize-run` 产出。）

## 输入

- `review/review_report.json`、`review/final_review.md`
- `verify/verify_report.json`、`verify/failures.md`
- `draft/full_draft.md`、`plans/*`、`knowledge/*`

## 产出 artifacts

- `revision_plan.json`
- `revised/full_draft.md`
- `revised/change_log.md`

## 边界与约束

- 修订是确定性的，依据审查/验证结果，不引入未支撑的新结论。
- 无法解决的开放项继续带入最终交付的 open items，保持 pending。
- 仍不输出批准类措辞；HITL pending 不得自动改为 confirmed。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按修订条目逐条核对；方案C 先扫高风险约束（HITL pending 是否被自动改为 confirmed、是否引入未支撑新结论）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对修订是否严格依据审查/验证结果；② 核对未引入未支撑新结论；③ 核对无法解决的开放项是否保留为 open items；④ 核对 HITL pending 是否未被自动改为 confirmed。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「依据审查/验证结果生成修订计划并逐条修订草稿，保留无法解决项为 open items、不引入未支撑新结论」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 一任务一修订条目顺序处理；方案B 先处理阻断类（blocking_failures）再处理一般审查项；方案C 按章节聚合修订条目处理。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条修订任务」逐条为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 汇总 review_report.items 与 blocking_failures 建立修订任务（RT）；② 逐条修订草稿、只依据允许证据；③ 记录 change_log；④ 保留 open items 与 HITL pending 状态。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "revision",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对修订严格依据审查/验证结果", "status": "done"},
      {"id": "rv-2", "desc": "核对未引入未支撑新结论", "status": "running"},
      {"id": "rv-3", "desc": "核对开放项保留、HITL pending 未被改为 confirmed", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "汇总 items 与 blocking_failures 建 RT", "status": "done"},
      {"id": "rt-2", "desc": "逐条修订草稿、只依据允许证据", "status": "running"},
      {"id": "rt-3", "desc": "记录 change_log", "status": "not_run"},
      {"id": "rt-4", "desc": "保留 open items 与 HITL pending 状态", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`revision_plan.json`、`revised/full_draft.md`、`revised/change_log.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：修订是否严格依据审查/验证结果、未引入未支撑新结论，无法解决的开放项是否保留为 open items，HITL pending 是否未被自动改为 confirmed。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin finalize-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 汇总 review_report.items 与 verify failures（含 blocking_failures），建立结构化修订任务（RT）。
   - 逐条修订草稿，只依据审查/验证指出的问题与允许证据，不引入未支撑的新结论。
   - 记录 `revised/change_log.md`，逐条对应修订前后变化与依据。
   - 无法解决的项保留为 open items，HITL pending 保持 pending、不自动改为 confirmed。
   - 不把 sample/reference 当作事实证据。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 13 · 最终报告**（`final/final_report.md` + `final/delivery_summary.md`）。
