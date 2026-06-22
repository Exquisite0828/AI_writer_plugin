---
name: step-final-report
description: 中文优先指导 workflow 第 13 步「最终报告」：由 finalize-run 生成 final/final_report.md 与 final/delivery_summary.md，作为 review-ready 交付包，不等于专业批准。
---

# Step 13 · 最终报告 (Final Report)

工作流第 13 步。把修订后草稿、审查、验证与溯源汇总为最终交付包，供合格人工审查。

## 何时使用

- 已完成 Step 12（修订），run 处于 phase_7。
- 需要产出可交付的报告与交付摘要。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin finalize-run --run <run_dir>
```

## 输入

- `revision_plan.json`、`revised/full_draft.md`、`revised/change_log.md`
- `review/*`、`verify/*`、`knowledge/*`、`plans/*`

## 产出 artifacts

- `final/final_report.md`
- `final/delivery_summary.md`

## 边界与约束

- final report **不是批准**：它是 review-ready package，不替代合格人工审查或专业 sign-off。
- 保守状态如 `finalized_with_open_items` / `ready_for_human_review` / `blocked_pending_confirmation`。
- critical claim 与 open items 保持 pending，禁止输出最终批准类结论。
- `runs/<run_id>/` 为本地 runtime output，不提交 git。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（是否被误写为批准与 critical claim/open items 是否保持 pending）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对最终报告是否未被误写为批准；② 核对状态是否保守（如 finalized_with_open_items）；③ 核对 critical claim 与 open items 是否保持 pending；④ 核对 final_report/delivery_summary 是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「把修订稿、审查、验证与溯源汇编为 review-ready 报告与交付摘要」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 直接由修订稿汇编报告；方案B 先建交付清单再逐项组装；方案C 按章节装配 + 全局一致性回扫。试跑对比后择优。
2. **分解与执行（第一性原理：以「报告组成部分（正文/摘要/开放项/边界标注）」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 汇编 final_report 正文与核心证据边界声明；② 生成 delivery_summary 交付摘要；③ 汇总 open items 与 critical claims 的 pending；④ 校验状态保守、未替代人工批准、无伪造结论。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "final-report",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对最终报告未被误写为批准", "status": "done"},
      {"id": "rv-2", "desc": "核对状态保守（finalized_with_open_items）", "status": "running"},
      {"id": "rv-3", "desc": "核对 critical claim 与 open items 保持 pending", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "汇编 final_report 正文与证据边界声明", "status": "done"},
      {"id": "rt-2", "desc": "生成 delivery_summary 交付摘要", "status": "running"},
      {"id": "rt-3", "desc": "汇总 open items 与 critical claims pending", "status": "not_run"},
      {"id": "rt-4", "desc": "校验状态保守、未替代人工批准", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`final/final_report.md`、`final/delivery_summary.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：最终报告是否被误写为批准、状态是否保守（如 `finalized_with_open_items`），critical claim 与 open items 是否保持 pending。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin finalize-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 汇总修订稿、审查、验证与 revision plan，生成 `final/final_report.md`（含核心证据边界声明、default_final_status、critical claims 边界）。
   - 生成交付摘要 `final/delivery_summary.md`，并刷新 final 输出对应的 verify 报告。
   - 状态保守（如 finalized_with_open_items），标记处的专业判断保持 pending。
   - final report 是 review-ready artifact，不替代合格人工审查或专业批准。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 14 · 运行总结**（`trace/*` + `learning/run_summary.md`）。
