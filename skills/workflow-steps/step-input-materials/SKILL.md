---
name: step-input-materials
description: 中文优先指导 workflow 第 1 步「输入材料」：通过 task.yaml 声明输入材料并启动 run，保留 input role 与 source!=sample 边界。这是 deterministic engine 的入口，不直接写最终文档。
---

# Step 1 · 输入材料 (Input Materials)

工作流第 1 步。负责把用户提供的原始材料和写作目标，整理成 task.yaml 并启动 run。它是 deterministic Python engine 的入口，不做草稿、审查或专业判断。

## 何时使用

- 用户提供材料并希望开始一次专业文档写作 run。
- 需要确认 `task_type`、`target_audience`、`critical_claims`、`requires_human_confirmation` 等任务声明。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin init-run --task <task_yaml>
# 或直接进入第 1/2/3 步：
$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>
```

`init-run` 创建 Phase 0 run 目录；`ingest-run` 在读取材料后产出材料清单与来源索引。

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

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（source≠sample 与缺失/不支持材料标记）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对 task_type/inputs/role 声明是否正确；② 核对 source≠sample 边界是否成立；③ 核对缺失/不支持材料是否显式标记；④ 核对 manifest/task_brief 是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「初始化 run 并把 task.yaml 声明的每份输入登记入册、区分 source/sample」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 一次性批量登记全部输入后统一校验；方案B 按材料 role（source/sample/reference/template）分组分批登记；方案C 逐份材料登记并即时校验 path 可达性、format 支持与 source≠sample。试跑对比后择优。
2. **分解与执行（第一性原理：以「每一份声明的输入材料 + run 初始化动作」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 创建 run 目录并写 manifest；② 解析 task_type 并加载对应文档类型规则；③ 逐份登记输入材料（分配 file_id、记录 path/title/format/role）；④ 校验 source≠sample 边界与缺失/不支持材料的显式标记。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "input-materials",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对 task_type/inputs/role 声明", "status": "done"},
      {"id": "rv-2", "desc": "核对 source≠sample 边界", "status": "running"},
      {"id": "rv-3", "desc": "核对缺失/不支持材料显式标记", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "创建 run 目录并写 manifest", "status": "done"},
      {"id": "rt-2", "desc": "解析 task_type 并加载文档类型规则", "status": "running"},
      {"id": "rt-3", "desc": "逐份登记输入材料并标注 role", "status": "not_run"},
      {"id": "rt-4", "desc": "校验 source≠sample 边界与缺失/不支持标记", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`manifest.json`、`task_brief.json`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：`task_type` / `inputs` / `role` 声明是否正确，source!=sample 边界是否成立，缺失/不支持材料是否已显式标记。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 创建 `runs/<run_id>/` 并写入 manifest 与 task_brief；解析 `task_type` 并加载对应文档类型规则（DocumentTypeRules / profile）。
   - 把 task.yaml 声明的每份输入登记为材料记录（分配 file_id、记录 path/title/format）。
   - 判定每份材料的 `role`（source/template/checklist/reference/sample/expected_output_shape），据此区分事实来源与样例参考。
   - 把材料与规约写入 `manifest.artifacts` 与 task_brief，作为后续阶段的输入起点与指纹基准。
   - 对缺失/不支持/解析失败的材料显式记录，不静默跳过。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

run 目录建立后，进入 **Step 2 · 材料清单**（`ingest-run` 产出 `inputs/input_inventory.json`）。
