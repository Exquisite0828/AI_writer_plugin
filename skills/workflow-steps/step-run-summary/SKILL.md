---
name: step-run-summary
description: 中文优先指导 workflow 第 14 步「运行总结」：由 learning-run 生成 session_trace.jsonl、hitl_decisions.jsonl、run_summary.md 与 reusable_patterns.md，汇总整次 run 的轨迹。
---

# Step 14 · 运行总结 (Run Summary)

工作流第 14 步。重建会话轨迹与 HITL 记录，生成本次 run 的总结与可复用模式提炼。

## 何时使用

- 已完成 Step 13（最终报告），run 处于 phase_8。
- 需要回顾整次 run 的流程、决策与可复用经验。

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
- 运行总结应记录三级目录索引质量（L1/L2/L3 覆盖、`knowledge_gaps`）及是否全程遵守 L1→L2→L3 访问协议（无直接全文读输入文件 / 无 SRC chunk）。

## 加载任务专属子 skill（必做）

本步是**通用骨架**，只定义流程、artifact 契约与角色边界。执行本步前，主执行上下文必须按 `task_type` 加载对应的任务专属子 skill：

- 路径：`skills/document-types/<task_type>/steps/step-run-summary.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-run-summary.md`，并配合根 skill `skills/document-types/<task_type>/SKILL.md`。

从子 skill 获取本步的：本步目的要点、A1/A2 候选方案示例与典型子任务、state.json 子任务文案、B 审核检查项及领域规则。若该子 skill 文件缺失，必须显式报告并停下确认，不得用通用占位静默推进。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核本步已产出的 artifacts。subagent 默认只审核；只有发现 P0/P1 或用户明确 `needs_revision` 时才允许进入局部修订。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须先对「审核任务」做动态任务分解，并在同一 `state.json` 中以 `review_state` 跟踪进度。`revision_state` 只有在审核发现 P0/P1 或用户明确 `needs_revision` 时才执行；无 P0/P1 时记录 `revision_required=false`。P2/P3 不触发 A2 修订。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。**本步任务专属候选方案见所加载子 skill 的「A1 审核任务」。**
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。**本步任务专属的典型审核子任务见所加载子 skill 的「A1 审核任务 · 典型审核子任务」。**
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

仅当审核发现 P0/P1 或用户明确 `needs_revision` 时，才针对具体 issue 修订本步产出。P2/P3 只能记录给用户确认，不得自动修订。修订不是重新驱动整步任务，而是按最小必要范围修正受影响 artifact：

1. **方案阶段（生成多方案、评估择优）**：围绕已确认的 P0/P1 issue 生成 **≥2 种**局部修订方案，择优选定；被放弃的方案与选择理由记入 `revision_state`。
2. **分解与执行（按 issue / artifact）**：每个修订子任务必须绑定 `issue_id`、`target_artifact`、`changed_paths`。只读取修订所需的最小 artifact / 原文片段；不得重跑整步、不得重写无关 artifacts。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`。

state.json 最小结构（本步通用 schema；子任务 `desc` 文案见所加载子 skill 的「state.json 示例」）：

```json
{
  "step": "<step-id>",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "<本步审核子任务，见子 skill>", "status": "done"},
      {"id": "rv-2", "desc": "<本步审核子任务，见子 skill>", "status": "running"},
      {"id": "rv-3", "desc": "<本步审核子任务，见子 skill>", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "<本步修订子任务，见子 skill>", "status": "done"},
      {"id": "rt-2", "desc": "<本步修订子任务，见子 skill>", "status": "running"},
      {"id": "rt-3", "desc": "<本步修订子任务，见子 skill>", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（见上「产出 artifacts」）与本文「边界与约束」+ 所加载子 skill 的「B 审核检查项」作为审核标准。
2. subagent 按所加载子 skill 的「B 审核检查项」逐项核对本步产出。
3. **发现 P0/P1 时才修订**：先记录 issue，再按 A2 进行局部修订。修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后只重审受影响 issue 与 artifact；若无 P0/P1，记录审核结论并停止，不得为了“更满意”重写 artifact。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 15 · 候选 profile 更新**（候选改进物，保持 inactive）。
