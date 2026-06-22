---
name: step-source-index
description: 中文优先指导 workflow 第 3 步「来源索引」：由 ingest-run 生成 source_index.json、provenance_index.json 与 knowledge_gaps.md，建立 N4 source tier 与溯源基础。
---

# Step 3 · 来源索引 (Source Index)

工作流第 3 步。基于材料清单，为已解析材料建立来源索引和溯源索引，标注 source tier，并记录知识缺口。

## 何时使用

- 已完成 Step 2（材料清单）。
- 需要为后续证据映射与引用计划提供可溯源的来源基础。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>
```

## 输入

- `inputs/input_inventory.json`
- 已解析材料的抽取文本

## 产出 artifacts

- `knowledge/source_index.json`
- `knowledge/provenance_index.json`
- `knowledge/knowledge_gaps.md`

## N4 Source Tier

- `T0`：HITL / 人工确认
- `T1`：项目 source
- `T2`：template / checklist
- `T3`：reference 方法学
- `T4`：sample 风格
- `T5`：生成 / 未知 / 不支持推断

只有 T0/T1 可支撑 critical project claim；T2 约束结构、T3 解释方法、T4 仅风格；T3/T4/T5 不能单独支撑 critical claim。

## 边界与约束

- 来源索引保留 tier、claim 与 evidence 状态，供 draft/review/verify/final 引用。
- 知识缺口必须显式写入 `knowledge_gaps.md`，不得用推断填补。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（tier 升格 sample=T4/reference=T3 与 T0/T1 边界）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 逐条核对 SRC 的 tier（T0–T5）标注是否准确；② 核对 sample/reference 未被升格为事实证据；③ 核对 T0/T1 与 critical claim 边界是否成立；④ 核对 knowledge_gaps.md 是否完整。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「对已解析材料分块、逐块建来源记录并分层标 tier、建溯源链、记知识缺口」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 按材料逐份分块建 SRC 记录；方案B 按章节主题聚合分块；方案C 先建 tier 分层骨架再回填来源块。试跑对比后择优。
2. **分解与执行（第一性原理：以「已解析材料 → 文本块 → 来源记录」为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 对 source/reference 分块（chunk_text）；② 逐块生成 SRC-xxx 记录并判定 tier（T0–T5）与 support_capabilities；③ 建立 provenance_index 溯源链；④ 汇总未覆盖知识点写 knowledge_gaps.md。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "source-index",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "逐条核对 SRC tier 标注", "status": "done"},
      {"id": "rv-2", "desc": "核对 sample/reference 未升格", "status": "running"},
      {"id": "rv-3", "desc": "核对 knowledge_gaps 完整", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "对 source/reference 分块（chunk_text）", "status": "done"},
      {"id": "rt-2", "desc": "逐块生成 SRC 记录并判定 tier", "status": "running"},
      {"id": "rt-3", "desc": "建立 provenance_index 溯源链", "status": "not_run"},
      {"id": "rt-4", "desc": "汇总知识缺口写 knowledge_gaps.md", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`knowledge/source_index.json`、`knowledge/provenance_index.json`、`knowledge/knowledge_gaps.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：source tier（T0–T5）标注是否准确，T0/T1 与 critical claim 边界是否成立，知识缺口是否完整写入 `knowledge_gaps.md`。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin ingest-run --task <task_yaml>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 对已解析的 source/reference 材料分块（chunk_text），逐块生成 `SRC-xxx` 来源记录写入 `knowledge/source_index.json`。
   - 依材料 role 判定 source tier（T0–T5）及其 support_capabilities（可支撑能力），并写入溯源信息。
   - 生成 `knowledge/provenance_index.json`，建立 source → file → path 的溯源链。
   - 把未覆盖或缺失的知识点写入 `knowledge/knowledge_gaps.md`。
   - 严守 tier 语义：sample=T4 仅风格、reference=T3 仅方法学，不得升格为事实证据。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 4 · 模板大纲**（`outline-run` 产出 `template_structure.json` + `outline_l1.md`）。
