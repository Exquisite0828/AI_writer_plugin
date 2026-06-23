---
name: step-input-materials
description: 中文优先指导 workflow 第 1 步「输入材料」：通过 task.yaml 声明输入材料并启动 run，保留 input role 与 source!=sample 边界。这是 deterministic engine 的入口，不直接写最终文档。
---

# Step 1 · 输入材料 (Input Materials)

工作流第 1 步。负责把用户提供的原始材料和写作目标，整理成 task.yaml 并启动 run。它是 deterministic Python engine 的入口，不做草稿、审查或专业判断。

## 何时使用

- 用户提供材料并希望开始一次专业文档写作 run。
- 需要确认 `task_type`、`target_audience`、`critical_claims`、`requires_human_confirmation` 等任务声明。

## 输入

- 用户的 task.yaml（声明 `task_type` 与 `inputs` 列表）。
- 每个输入声明的 `role` 与 `path`。

## 产出 artifacts

- `manifest.json`
- `task_brief.json`

## 边界与约束

材料 `role` 不可互换，且 `fact source != sample document`：

- `source`：项目事实来源。
- `template`：结构约束，不是事实支撑。
- `checklist`：审查/验证要求，不是事实支撑。
- `reference`：方法学/背景/术语，不能证明项目事实。
- `sample` / `expected_output_shape`：仅风格、表格形状、章节粒度。

绝不把 sample / reference / expected_output 当作事实证据；解析失败、缺失、不支持格式必须显式报告，不能静默跳过。

## 加载任务专属子 skill（必做）

本步是**通用骨架**，只定义流程、artifact 契约与角色边界。执行前，subagent 必须按 `task_type` 加载对应的任务专属子 skill：

- 路径：`skills/document-types/<task_type>/steps/step-input-materials.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-input-materials.md`，并配合根 skill `skills/document-types/<task_type>/SKILL.md`。

从子 skill 获取本步的：本步目的要点、A1/A2 候选方案示例与典型子任务、state.json 子任务文案、B 审核检查项及领域规则。若该子 skill 文件缺失，必须显式报告并停下确认，不得用通用占位静默推进。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。**本步任务专属候选方案见所加载子 skill 的「A1 审核任务」。**
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。**本步任务专属的典型审核子任务见所加载子 skill 的「A1 审核任务 · 典型审核子任务」。**
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步要完成的目的（见所加载子 skill 的「本步目的要点」）自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。**本步任务专属候选方案见所加载子 skill 的「A2 修订任务」。**
2. **分解与执行（第一性原理：以本步的自然工作单元为单位）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。**本步任务专属的典型修订子任务见所加载子 skill 的「A2 修订任务 · 典型修订子任务」。**
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

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
3. **发现问题时修订（提取本步目的、自主重新驱动）**：先从所加载子 skill 的「本步目的要点」读取本步要达成的目的，再由 subagent 围绕这些目的自主重新驱动完成本步任务。**底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

run 目录建立后，进入 **Step 2 · 材料清单**（产出 `inputs/input_inventory.json`）。
