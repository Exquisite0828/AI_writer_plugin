---
name: step-review
description: 中文优先指导 workflow 第 10 步「审查」：由 review-run 生成 review_report.json 与 template/checklist/evidence/final review，对照模板、清单与证据审查草稿。
---

# Step 10 · 审查 (Review)

工作流第 10 步。对保守草稿做结构化审查：模板符合性、checklist 满足度、证据支撑情况，并汇总为审查报告。

## 何时使用

- 已完成 Step 9（保守草稿），run 处于 phase_5。
- 需要在交付前发现结构、清单与证据问题。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin review-run --run <run_dir>
```

（审查与验证由同一条 `review-run` 产出。）

## 输入

- `draft/full_draft.md`
- `plans/*`、`knowledge/*`（模板、清单、证据、来源）

## 产出 artifacts

- `review/review_report.json`
- `review/template_review.md`
- `review/checklist_review.md`
- `review/evidence_review.md`
- `review/final_review.md`

## 边界与约束

- 审查是机器辅助检查，不等于合格人工审查或专业批准。
- 不把 sample 当事实、不把 reference 当项目事实证据。
- 审查发现的问题供 Step 12 修订使用，不在此步直接改稿。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（是否出现批准语义与未确认项是否仍可见）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对是否覆盖 template/checklist/evidence/final 关注点；② 核对问题是否具体且 P0/P1 显式；③ 核对是否未出现批准语义；④ 核对未确认项是否仍可见。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「对草稿做多维度审查并登记 P0/P1 问题」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 按审查维度（溯源/一致性/越权结论…）逐维扫描；方案B 按章节逐节多维审查；方案C 维度×章节矩阵抽查高风险项。试跑对比后择优。
2. **分解与执行（第一性原理：以「审查维度 × 章节」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 枚举审查维度与章节；② 逐项扫描并登记 issue（severity/category）；③ 标注 P0/P1 阻断项；④ 汇总 review_report 并校验无漏检。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "review",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对覆盖 template/checklist/evidence/final", "status": "done"},
      {"id": "rv-2", "desc": "核对问题具体且 P0/P1 显式", "status": "running"},
      {"id": "rv-3", "desc": "核对未出现批准语义、未确认项可见", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "枚举审查维度与章节", "status": "done"},
      {"id": "rt-2", "desc": "逐项扫描并登记 issue（severity/category）", "status": "running"},
      {"id": "rt-3", "desc": "标注 P0/P1 阻断项", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总 review_report 并校验无漏检", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`review/review_report.json` 及 `review/*.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：是否覆盖 template/checklist/evidence/final review 关注点，问题是否具体且 P0/P1 显式，是否出现批准语义，未确认项是否仍可见。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin review-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 对草稿运行多维分析（analyze_run），分配 review id，并从四个维度渲染审查：template / checklist / evidence / final。
   - 依问题严重度（P0/P1/P2/info）汇总 `review/review_report.json` 状态（open_blockers / passed_with_warnings / passed）。
   - 逐项具体登记问题（定位、严重度、是否阻断 final）。
   - 不输出专业批准结论；未确认项保持可见。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

与 **Step 11 · 验证** 并列产出；随后进入 **Step 12 · 修订**。
