---
name: step-run-summary
description: 中文优先指导 workflow 第 14 步「运行总结」：由 learning-run 生成 session_trace.jsonl、hitl_decisions.jsonl、run_summary.md 与 reusable_patterns.md，汇总整次 run 的轨迹。
---

# Step 14 · 运行总结 (Run Summary)

工作流第 14 步。重建会话轨迹与 HITL 记录，生成本次 run 的总结与可复用模式提炼。

## 何时使用

- 已完成 Step 13（最终报告），run 处于 phase_8。
- 需要回顾整次 run 的流程、决策与可复用经验。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin learning-run --run <run_dir>
```

（运行总结与候选 profile 更新由同一条 `learning-run` 产出。）

## 输入

- `final/final_report.md`、`final/delivery_summary.md`
- `review/*`、`verify/*`、`plans/*`、`knowledge/*`、已有 HITL 记录

## 产出 artifacts

- `trace/session_trace.jsonl`
- `trace/hitl_decisions.jsonl`
- `learning/run_summary.md`
- `learning/reusable_patterns.md`

## 边界与约束

- 运行总结只描述发生了什么，不重新下专业结论。
- 真实 HITL 决策记录在 `trace/hitl_decisions.jsonl`，非交互 run 不得伪造确认。
- `completed` 仅表示 engine lifecycle 完成，不表示专业批准。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact 逐项核对；方案C 先扫高风险约束（是否重下专业结论、是否伪造 HITL 确认、是否把 completed 当批准）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对总结是否只描述发生了什么而未重下专业结论；② 核对非交互 run 是否未伪造 HITL 确认；③ 核对 `completed` 是否未被当作专业批准；④ 核对 trace/summary/patterns 是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「重建 run 各阶段轨迹与 HITL 决策、生成中性 run 总结与可复用模式，不重下专业结论」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 按 run 各阶段顺序重建轨迹再汇总；方案B 先抽 HITL 决策与 open items 再生成总结；方案C 按 artifact（trace/summary/patterns）分组生成。试跑对比后择优。
2. **分解与执行（第一性原理：以「run 各阶段 / 各 artifact」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 重建 session_trace 与 hitl_decisions；② 抽取 HITL 决策与 open items；③ 生成中性 run_summary；④ 提炼 reusable_patterns。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "run-summary",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对总结未重下专业结论", "status": "done"},
      {"id": "rv-2", "desc": "核对非交互 run 未伪造 HITL 确认", "status": "running"},
      {"id": "rv-3", "desc": "核对 completed 未被当作专业批准", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "重建 session_trace 与 hitl_decisions", "status": "done"},
      {"id": "rt-2", "desc": "抽取 HITL 决策与 open items", "status": "running"},
      {"id": "rt-3", "desc": "生成中性 run_summary", "status": "not_run"},
      {"id": "rt-4", "desc": "提炼 reusable_patterns", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`trace/session_trace.jsonl`、`trace/hitl_decisions.jsonl`、`learning/run_summary.md`、`learning/reusable_patterns.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：总结是否只描述发生了什么而未重下专业结论，非交互 run 是否未伪造 HITL 确认，`completed` 是否未被当作专业批准。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin learning-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 重建 run 各阶段的 `trace/session_trace.jsonl` 与 `trace/hitl_decisions.jsonl`，如实记录发生过什么。
   - 抽取 HITL 决策、open items 与各阶段状态，非交互 run 不伪造 HITL 确认。
   - 生成中性 `learning/run_summary.md`，只描述发生了什么，不重下专业结论、不把 `completed` 当作专业批准。
   - 提炼 `learning/reusable_patterns.md`，仅记录可复用结构/流程模式，不掺入事实结论。
   - 不把 sample/reference 当作事实证据。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 15 · 候选 profile 更新**（候选改进物，保持 inactive）。
