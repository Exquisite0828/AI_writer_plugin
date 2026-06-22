---
name: step-citation-plan
description: 中文优先指导 workflow 第 7 步「引用计划」：由 plan-run 生成 citation_plan.json 与 claim_support_matrix.json，规划每个 claim 如何被来源引用支撑。
---

# Step 7 · 引用计划 (Citation Plan)

工作流第 7 步。基于证据映射，规划草稿中每个 claim 引用哪些来源，并建立 claim 与来源支撑的对应矩阵。

## 何时使用

- 已完成 Step 6（证据映射），run 处于 phase_3。
- 需要在写作前固定"claim → 来源引用"的对应关系。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin plan-run --run <run_dir>
```

（引用计划与章节任务由同一条 `plan-run` 产出。）

## 输入

- `plans/evidence_map.json`、`plans/unresolved_questions.md`
- `plans/template_structure.json`、`plans/outline_l1.md`
- `knowledge/source_index.json`、`knowledge/provenance_index.json`

## 产出 artifacts

- `plans/citation_plan.json`
- `plans/claim_support_matrix.json`

## 边界与约束

- `claim_support_matrix.json` 是 N4 核心溯源 artifact，须保留 source tier 与 claim 状态。
- critical claim 必须有 T0/T1 支撑，否则保持 `NEEDS_USER_CONFIRMATION` / pending / open。
- 不得为缺证据的 claim 编造引用。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（critical claim 的 T0/T1 支撑与未为缺证据 claim 编造引用）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对 claim_support_matrix 保留 source tier 与 claim 状态；② 核对 critical claim 由 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION` / pending；③ 核对未为缺证据 claim 编造引用；④ 核对 citation_plan/claim_support_matrix 符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「把研究问题与证据按 outline 归并到各章节，生成 citation_slots 与 claim 支撑矩阵，缺证据保持 pending/open」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 按 outline 顺序逐章节归并；方案B 先按 claim 聚合再回填章节；方案C 先处理 critical claim 再补普通 claim。试跑对比后择优。
2. **分解与执行（第一性原理：以「outline 章节 / claim」逐章节为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 按 outline 顺序归并 research_questions 与 evidence（group_research_questions）；② 逐节判定 requires_human_confirmation；③ 生成 citation_slots/unsupported_claims/weak_notes；④ 建 claim_support_matrix（N4 溯源，含 tier 与 claim 状态）。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "citation-plan",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 claim_support_matrix 保留 tier 与 claim 状态", "status": "done"},
      {"id": "rv-2", "desc": "核对 critical claim 由 T0/T1 支撑或保持 pending", "status": "running"},
      {"id": "rv-3", "desc": "核对未为缺证据 claim 编造引用", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "按 outline 归并 research_questions 与 evidence", "status": "done"},
      {"id": "rt-2", "desc": "逐节判定 requires_human_confirmation", "status": "running"},
      {"id": "rt-3", "desc": "生成 citation_slots/unsupported_claims/weak_notes", "status": "not_run"},
      {"id": "rt-4", "desc": "建 claim_support_matrix（N4 溯源）", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`plans/citation_plan.json`、`plans/claim_support_matrix.json`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：`claim_support_matrix.json` 是否保留 source tier 与 claim 状态，critical claim 是否有 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION` / pending，是否存在为缺证据 claim 编造的引用。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin plan-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 按 outline 顺序把研究问题与证据映射归并到各章节（group_research_questions / evidence_by_question）。
   - 为每节判定 requires_human_confirmation，并生成 citation_slots、unsupported_claims、weak_notes。
   - 产出 `plans/citation_plan.json`（claim → 来源引用槽）。
   - 产出 `plans/claim_support_matrix.json`（N4 核心溯源矩阵，含 source tier 与 claim 状态）。
   - critical claim 无 T0/T1 支撑时保持 `NEEDS_USER_CONFIRMATION` / pending，不为缺证据 claim 编造引用。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 8 · 章节任务**（`section_tasks.json` + `outline_final.md` + `writing_plan.md`）。
