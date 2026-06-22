---
name: step-verification
description: 中文优先指导 workflow 第 11 步「验证」：由 review-run 生成 verify_report.json 与 failures.md，对草稿做确定性校验并记录失败项。
---

# Step 11 · 验证 (Verification)

工作流第 11 步。对草稿与审查结果做确定性验证检查，输出验证报告和失败清单。

## 何时使用

- 与 Step 10（审查）同属 `review-run`，run 处于 phase_5。
- 需要把"未通过的检查"显式列出，供修订处理。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin review-run --run <run_dir>
```

## 输入

- `draft/full_draft.md`
- `review/review_report.json`
- `plans/*`、`knowledge/*`

## 产出 artifacts

- `verify/verify_report.json`
- `verify/failures.md`

## 边界与约束

- 验证是确定性检查，不替代专业判断或最终批准。
- 失败项必须如实写入 `failures.md`，不得静默通过。
- 验证 `status` 为保守状态，不输出 `validated` 等批准措辞。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact 逐项核对；方案C 先扫高风险约束（失败项是否静默通过、是否出现批准措辞）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对失败项是否如实写入 `failures.md` 而非静默通过；② 核对 `status` 是否保守、未输出 `validated` 等批准措辞；③ 核对 REQUIRED_CHECKS 是否逐项均有结论；④ 核对 verify_report/failures 是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「对草稿与审查结果做确定性验证检查，把未通过项显式列出」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 按 REQUIRED_CHECKS 顺序逐项执行；方案B 先跑阻断类检查再补其余；方案C 按 artifact 维度分组检查。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条验证检查项（REQUIRED_CHECKS）」逐项为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 遍历 REQUIRED_CHECKS 逐项执行确定性检查；② 为每项判定 status；③ 收集 blocking_failures 并如实写入 failures.md；④ 汇总 verify_report.json 保持保守 status。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "verification",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对失败项如实写入 failures.md 而非静默通过", "status": "done"},
      {"id": "rv-2", "desc": "核对 status 保守、未输出 validated 等措辞", "status": "running"},
      {"id": "rv-3", "desc": "核对 REQUIRED_CHECKS 逐项均有结论", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 REQUIRED_CHECKS 逐项执行确定性检查", "status": "done"},
      {"id": "rt-2", "desc": "为每项判定 status", "status": "running"},
      {"id": "rt-3", "desc": "收集 blocking_failures 并写入 failures.md", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总 verify_report.json 保持保守 status", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`verify/verify_report.json`、`verify/failures.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：失败项是否如实写入 `failures.md` 而非静默通过，`status` 是否保守、未输出 `validated` 等批准措辞。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin review-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 对草稿与审查结果逐项执行 REQUIRED_CHECKS 确定性检查。
   - 为每项判定 status，并汇总 blocking_failures。
   - 把失败项如实写入 `verify/failures.md`，不得静默通过。
   - 产出 `verify/verify_report.json`，status 保持保守、不输出 `validated` 等批准措辞。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

审查 + 验证结果一起进入 **Step 12 · 修订**（`revision_plan.json` + `revised/*`）。
