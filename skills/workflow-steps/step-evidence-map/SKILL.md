---
name: step-evidence-map
description: 中文优先指导 workflow 第 6 步「证据映射」：由 evidence-run 生成 evidence_map.json 与 unresolved_questions.md，把研究问题映射到具体来源证据。
---

# Step 6 · 证据映射 (Evidence Map)

工作流第 6 步。把研究问题映射到来源索引中的具体证据，标记哪些有支撑、哪些仍未解决。

## 何时使用

- 已完成 Step 5（研究问题）。
- 需要在写作前确认每个关键问题的证据状态。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin evidence-run --run <run_dir>
```

## 输入

- `plans/research_questions.json`
- `knowledge/source_index.json`、`knowledge/provenance_index.json`

## 产出 artifacts

- `plans/evidence_map.json`
- `plans/unresolved_questions.md`

## 边界与约束

- 只允许用 T0/T1 来源支撑 critical claim；T3/T4/T5 不能单独支撑。
- 没有证据的问题写入 `unresolved_questions.md`，保持 open，不得推断填补。
- sample/reference 不能作为事实证据进入证据映射。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/问题逐项核对；方案C 先扫高风险约束（critical claim 的 T0/T1 支撑与 open 标记）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对 critical claim 是否仅由 T0/T1 支撑；② 核对无证据问题是否进入 unresolved_questions.md 并保持 open；③ 核对 sample/reference 未被误当事实证据；④ 核对 evidence_map 是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「把每个研究问题映射到 source_index 中的证据，未命中标 open」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 逐题在 source_index 检索匹配；方案B 先按 tier 过滤来源再对题匹配；方案C 按章节分组批量匹配。试跑对比后择优。
2. **分解与执行（第一性原理：以「研究问题」逐题为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 遍历 research_questions 逐题；② 在 source_index 检索候选证据并记 tier；③ 建立 question→evidence 映射；④ 未命中/弱证据问题标 open。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "evidence-map",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 critical claim 仅由 T0/T1 支撑", "status": "done"},
      {"id": "rv-2", "desc": "核对无证据问题进入 unresolved 并保持 open", "status": "running"},
      {"id": "rv-3", "desc": "核对 sample/reference 未被误当事实证据", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "遍历 research_questions 逐题", "status": "done"},
      {"id": "rt-2", "desc": "在 source_index 检索候选证据并记 tier", "status": "running"},
      {"id": "rt-3", "desc": "建立 question→evidence 映射", "status": "not_run"},
      {"id": "rt-4", "desc": "未命中/弱证据问题标 open", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`plans/evidence_map.json`、`plans/unresolved_questions.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：critical claim 是否仅由 T0/T1 支撑，无证据问题是否进入 `unresolved_questions.md` 并保持 open，sample/reference 是否被误当事实证据。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin evidence-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 对每个问题在 source_index 做术语匹配打分（match_evidence，score ≥ 2 取前 3），生成 `EVD-xxx` 证据候选。
   - 依候选来源 tier 判定支撑能力，并定出问题 status（supported/weak/unsupported）。
   - 写入 `plans/evidence_map.json`：问题 → 证据候选的映射。
   - 把 weak/unsupported/需确认的问题汇入 `plans/unresolved_questions.md` 并保持 open。
   - 不得把 sample/reference 当作事实证据。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 7 · 引用计划**（`citation_plan.json` + `claim_support_matrix.json`）。
