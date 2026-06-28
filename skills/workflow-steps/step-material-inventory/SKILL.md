---
name: step-material-inventory
description: 中文优先指导 workflow 第 2 步「材料清单」：由 ingest-run 生成 input_inventory.json，登记每个文件的 role、parse_status 与 fact-source 标记。
---

# Step 2 · 材料清单 (Material Inventory)

工作流第 2 步。把声明的输入材料逐一登记为结构化清单，记录是否解析成功、角色和是否为事实来源。

## 何时使用

- 已完成 Step 1（输入材料声明）。
- 需要核对哪些文件被成功解析、哪些缺失或不支持、哪些是 fact source。

## 输入

- `manifest.json`、`task_brief.json`
- task.yaml 声明的输入文件

## 产出 artifacts

- `inputs/input_inventory.json`

每条文件记录含：`file_id`、`path`、`role`、`format`、`parse_status`、`is_fact_source`、`title`、`notes`、`error_message`。

`parse_status` 取值：`parsed` / `missing` / `unsupported` / `failed`。

## 路径解析与写入规则（必做）

- `task.yaml` 中的输入路径按 `task.yaml` 所在目录解析；不得按当前 shell cwd、`runs/<run_id>/`、或 subagent 的 cwd 重新解释。
- 写入 `inputs/input_inventory.json` 时，`files[].path` 必须是已解析、已验证存在、后续步骤可直接读取的绝对路径。
- 禁止把 `../`、`../../`、`../../../inputdoc/...` 或其他依赖当前 cwd 的相对路径原样写入 `files[].path`。
- 若解析后的文件不存在或无法读取，必须把该材料记录为 `parse_status=missing` 或 `failed`，并在 `error_message` 中写明解析基准目录与解析后的绝对路径；不得留给 Step 3 或 subagent 再猜路径。

## 边界与约束

- 清单只做"登记"，不做事实判断，也不把 sample/reference 提升为事实来源。
- `missing` / `unsupported` / `failed` 必须如实记录，禁止静默忽略。
- `summary` 字段提供 parsed/fact-source 计数，供后续步骤与人工审查参考。

## 加载任务专属子 skill（必做）

本步是**通用骨架**，只定义流程、artifact 契约与角色边界。执行本步前，主执行上下文必须按 `task_type` 加载对应的任务专属子 skill：

- 路径：`skills/document-types/<task_type>/steps/step-material-inventory.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-material-inventory.md`，并配合根 skill `skills/document-types/<task_type>/SKILL.md`。

从子 skill 获取本步的：本步目的要点、A1/A2 候选方案示例与典型子任务、state.json 子任务文案、B 审核检查项及领域规则。若该子 skill 文件缺失，必须显式报告并停下确认，不得用通用占位静默推进。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核本步已产出的 artifacts。subagent 默认只审核，不重新生成材料清单；只有发现 P0/P1 时才允许进入局部修订。

审核通过且无 P0/P1 时，subagent 只能写入 `runs/<run_id>/subagent/step-material-inventory/state.json`，不得重写 `inputs/input_inventory.json`。P2/P3 只记录为待用户确认的问题，不得自动修订本步 artifacts。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须先对「审核任务」做动态任务分解，并在同一 `state.json` 中以 `review_state` 跟踪进度。`revision_state` 只有在审核发现 P0/P1 时才执行；无 P0/P1 时记录 `revision_required=false`。P2/P3 不触发 A2 修订。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。**本步任务专属候选方案见所加载子 skill 的「A1 审核任务」。**
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。**本步任务专属的典型审核子任务见所加载子 skill 的「A1 审核任务 · 典型审核子任务」。**
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

仅当审核发现 P0/P1 时，才针对具体 issue 修订本步产出。P2/P3 只能记录给用户确认，不得自动修订。修订不是重新驱动整步任务，而是按最小必要范围修正受影响 artifact：

1. **方案阶段（生成多方案、评估择优）**：围绕已确认的 P0/P1 issue 生成 **≥2 种**局部修订方案，择优选定；被放弃的方案与选择理由记入 `revision_state`。
2. **分解与执行（按 issue / artifact）**：每个修订子任务必须绑定 `issue_id`、`target_artifact`、`changed_paths`。只读取修订所需的最小 artifact / 原始任务声明片段；不得重新遍历全部输入、不得重写整份 `input_inventory.json`。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构（本步通用 schema；子任务 `desc` 文案见所加载子 skill 的「state.json 示例」）：

```json
{
  "step": "<step-id>",
  "revision_required": false,
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
    "chosen_plan": "no_revision_required",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": []
  }
}
```

若 `revision_required=true`，`revision_state.subtasks[]` 中每个修订子任务还必须包含 `issue_id`、`target_artifact`、`changed_paths`。

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（见上「产出 artifacts」）与本文「边界与约束」+ 所加载子 skill 的「B 审核检查项」作为审核标准。
2. subagent 按所加载子 skill 的「B 审核检查项」逐项核对本步产出。
3. **发现 P0/P1 时才修订**：先记录 issue，再按 A2 进行局部修订。修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后只重审受影响 issue 与 artifact；若无 P0/P1，记录审核结论并停止，不得为了“更满意”重写 artifact。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

清单建立后，进入 **Step 3 · 文档目录索引**（L1/L2/L3 三级目录 + `source_index.json` + `provenance_index.json` + `document_tocs/` + `knowledge_gaps.md`）。
