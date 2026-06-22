---
name: step-material-inventory
description: 中文优先指导 workflow 第 2 步「材料清单」：由 ingest-run 生成 input_inventory.json，登记每个文件的 role、parse_status 与 fact-source 标记。
---

# Step 2 · 材料清单 (Material Inventory)

工作流第 2 步。把声明的输入材料逐一登记为结构化清单，记录是否解析成功、角色和是否为事实来源。

## 何时使用

- 已完成 Step 1（输入材料声明）。
- 需要核对哪些文件被成功解析、哪些缺失或不支持、哪些是 fact source。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>
```

（材料清单与来源索引由同一条 `ingest-run` 产出。）

## 输入

- `manifest.json`、`task_brief.json`
- task.yaml 声明的输入文件

## 产出 artifacts

- `inputs/input_inventory.json`

每条文件记录含：`file_id`、`path`、`role`、`format`、`parse_status`、`is_fact_source`、`title`、`notes`、`error_message`。

`parse_status` 取值：`parsed` / `missing` / `unsupported` / `failed`。

## 边界与约束

- 清单只做"登记"，不做事实判断，也不把 sample/reference 提升为事实来源。
- `missing` / `unsupported` / `failed` 必须如实记录，禁止静默忽略。
- `summary` 字段提供 parsed/fact-source 计数，供后续步骤与人工审查参考。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（failed/unsupported/missing 如实登记与 is_fact_source 判定）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 逐条核对 role/parse_status/is_fact_source 是否正确；② 核对 missing/unsupported/failed 是否如实登记；③ 核对 summary 计数是否一致；④ 核对清单是否符合 artifact 契约。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「对每份材料按格式解析、生成结构化清单并标注 role/parse_status/is_fact_source」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 按文件格式分组（PDF/DOCX/MD…）分别选 reader 批处理；方案B 逐份材料串行解析并即时登记；方案C 先快速探测格式与可解析性，再对可解析项深解析、对失败项单独登记。试跑对比后择优。
2. **分解与执行（第一性原理：以「每一份待解析材料」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 枚举待解析材料并探测格式；② 逐份抽取文本生成清单记录；③ 标注 role/parse_status/is_fact_source；④ 校验 summary 计数一致、failed/unsupported/missing 如实登记。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "material-inventory",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "逐条核对 role/parse_status/is_fact_source", "status": "done"},
      {"id": "rv-2", "desc": "核对 missing/unsupported/failed 如实登记", "status": "running"},
      {"id": "rv-3", "desc": "核对 summary 计数一致", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "枚举待解析材料并探测格式", "status": "done"},
      {"id": "rt-2", "desc": "逐份抽取文本生成清单记录", "status": "running"},
      {"id": "rt-3", "desc": "标注 role/parse_status/is_fact_source", "status": "not_run"},
      {"id": "rt-4", "desc": "校验 summary 计数一致、失败/缺失如实登记", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`inputs/input_inventory.json`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：每条记录的 `role` / `parse_status` / `is_fact_source` 是否正确，`missing` / `unsupported` / `failed` 是否如实登记，`summary` 计数是否一致。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 对每份材料按格式选择 reader 抽取文本，生成结构化清单 `inputs/input_inventory.json`。
   - 为每条记录登记 `role` / `parse_status`（parsed/failed/unsupported/missing）/ `is_fact_source` 等字段。
   - 仅对 parsed 且 role ∈ {source, reference} 的材料保留可供后续索引的抽取文本。
   - 如实标记 missing/unsupported/failed，不静默吞掉解析问题。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

清单建立后，进入 **Step 3 · 来源索引**（`source_index.json` + `provenance_index.json` + `knowledge_gaps.md`）。
