---
name: step-verification
description: 中文优先指导 workflow 第 11 步「验证」：由 review-run 生成 verify_report.json 与 failures.md，对草稿做确定性校验并记录失败项。
---

# Step 11 · 验证 (Verification)

工作流第 11 步。对草稿与审查结果做确定性验证检查，输出验证报告和失败清单。

## 何时使用

- 与 Step 10（审查）同属同一审查阶段，run 处于 phase_5。
- 需要把"未通过的检查"显式列出，供修订处理。

## 输入

- `draft/full_draft.md`
- `review/review_report.json`
- `plans/*`、`knowledge/*`

## 产出 artifacts

- `verify/verify_report.json`
- `verify/failures.md`

## verify artifact 硬契约

`verify/verify_report.json` 不得只写 summary / verification_summary。它必须是结构化报告，至少包含：

- `run_id`
- `generated_at`
- `status`：只能取 `passed` / `passed_with_warnings` / `blocked` / `failed`
- `summary`
- `checks[]`：逐项检查结果；每项必须含 `check_id`、`name`、`status`、`severity`、`details`、`related_artifacts`
- `blocking_failures[]`
- `warnings[]`

每个任务专属子 skill 定义的 VC / CHECK-ID 都必须在 `checks[]` 中有明确 pass / warn / fail / blocked 结论。若只输出一段“全部通过”总结、缺少逐项检查，或未覆盖任务专属 VC，则本步自身为 P0 失败。

`verify/failures.md` 必须始终生成。即使没有 blocking failure，也必须写明 run id、摘要、阻塞失败项为空、非阻塞 warnings、人工确认阻塞项、阶段边界说明。任何 failed / blocked check 必须出现在 `failures.md`；不得静默通过。

subagent 审核本步时必须先做 meta-contract 检查：`verify_report.json` 是否使用上述 top-level 字段与任务专属 `check_id`，`failures.md` 是否存在。若报告使用旧式字段（例如 `overall_status`、`verification_checks`）或泛化编号（例如 `VC-001`）替代任务专属 check id，应标为 P0、`revision_required=true`，并在 A2 中局部重写 `verify/verify_report.json` 与 `verify/failures.md`。不得把内容看起来“通过”的旧格式报告判为 pass。

## 边界与约束

- 验证是确定性检查，不替代专业判断或最终批准。
- 失败项必须如实写入 `failures.md`，不得静默通过。
- 验证须包含：L1/L2/L3 目录完整性、`EVD-xxx` 是否经三级路径可回溯原文（禁止 SRC/chunk 或直接全文读输入文件），见任务专属子 skill。

## 加载任务专属子 skill（必做）

本步是**通用骨架**，只定义流程、artifact 契约与角色边界。执行本步前，主执行上下文必须按 `task_type` 加载对应的任务专属子 skill：

- 路径：`skills/document-types/<task_type>/steps/step-verification.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-verification.md`，并配合根 skill `skills/document-types/<task_type>/SKILL.md`。
- FSR alias：`task_type: fsr` 使用根 skill `skills/document-types/fsr/SKILL.md`，但逐步子 skill 共享 `skills/document-types/FunctionalSafetyRequirement/steps/step-verification.md`。

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

审查 + 验证结果一起进入 **Step 12 · 修订**（`revision_plan.json` + `revised/*`）。
