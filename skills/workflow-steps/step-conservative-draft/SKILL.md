---
name: step-conservative-draft
description: 中文优先指导 workflow 第 9 步「保守草稿」：由 draft-run 生成 draft/full_draft.md，按章节任务保守成稿，不超出证据、不伪造批准结论。
---

# Step 9 · 保守草稿 (Conservative Draft)

工作流第 9 步。按章节任务和引用计划生成保守草稿：只写有来源支撑的内容，缺证据处保持 pending 或 open。

## 何时使用

- 已完成 Step 8（章节任务），run 处于 phase_4。
- 需要生成首版可审查草稿。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin draft-run --run <run_dir>
```

## 输入

- `plans/section_tasks.json`、`plans/outline_final.md`、`plans/writing_plan.md`
- `plans/citation_plan.json`、`plans/claim_support_matrix.json`、`plans/evidence_map.json`

## 产出 artifacts

- `draft/full_draft.md`

## 边界与约束

- "保守"：不超出证据范围，不把 sample/reference 当事实，不写未支撑的 critical claim。
- critical claim 无 T0/T1 支撑时保持 `NEEDS_USER_CONFIRMATION` / pending。
- 不写 `approved` / `validated` / `compliant` / `risk accepted` / `production ready` 等批准类措辞。
- 保留 source tier、claim 状态与人工确认状态。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按章节逐节核对；方案C 先扫高风险约束（critical claim 支撑与批准类措辞）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对草稿是否超出证据范围；② 核对 critical claim 无 T0/T1 时是否保持 `NEEDS_USER_CONFIRMATION` / pending；③ 核对是否出现 `approved`/`validated`/`compliant` 等批准措辞；④ 核对 source tier 与 claim 状态是否保留。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「按章节任务与引用计划保守成稿，只写有来源支撑的内容，缺证据处保持 pending/open」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 一任务一章节顺序成稿；方案B 先成稿证据充分章节再处理待证章节；方案C 按写作模式分组成稿。试跑对比后择优。
2. **分解与执行（第一性原理：以「章节写作任务」逐任务为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 遍历 section_tasks 逐任务并匹配 citation_plan 章节；② 校验任务证据（validate_task_evidence）只用 allowed evidence ids；③ 逐节渲染保守草稿；④ 汇编 full_draft.md 并保留 tier/claim/HITL 状态。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "conservative-draft",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对草稿未超出证据范围", "status": "done"},
      {"id": "rv-2", "desc": "核对 critical claim 无 T0/T1 时保持 pending", "status": "running"},
      {"id": "rv-3", "desc": "核对未出现批准类措辞、保留 tier/claim 状态", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 section_tasks 并匹配 citation_plan 章节", "status": "done"},
      {"id": "rt-2", "desc": "校验任务证据只用 allowed evidence ids", "status": "running"},
      {"id": "rt-3", "desc": "逐节渲染保守草稿", "status": "not_run"},
      {"id": "rt-4", "desc": "汇编 full_draft.md 并保留 tier/claim/HITL 状态", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`draft/full_draft.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：草稿是否超出证据范围，critical claim 无 T0/T1 时是否保持 `NEEDS_USER_CONFIRMATION` / pending，是否出现 `approved`/`validated`/`compliant` 等批准措辞，source tier 与 claim 状态是否保留。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin draft-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 遍历 section_tasks 逐任务，匹配 citation_plan 章节并校验任务证据（validate_task_evidence），只用任务携带的 allowed evidence ids。
   - 逐节渲染保守草稿（来源支持、草稿正文、限制与开放问题、确认标记）。
   - 汇编 `draft/full_draft.md`，保留 source tier、claim 状态与人工确认状态。
   - critical claim 无 T0/T1 支撑时保持 `NEEDS_USER_CONFIRMATION` / pending，不写未支撑结论与 `approved`/`validated`/`compliant` 等批准类措辞。
   - 不把 sample/reference 当作事实证据。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 10 · 审查**（`review/*`）与 **Step 11 · 验证**（`verify/*`）。
