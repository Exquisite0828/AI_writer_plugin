---
name: step-template-outline
description: 中文优先指导 workflow 第 4 步「模板大纲」：由 outline-run 生成 template_structure.json 与 outline_l1.md，确定文档结构约束与一级大纲。
---

# Step 4 · 模板大纲 (Template Outline)

工作流第 4 步。根据 `task_type` 的 `DocumentTypeRules`（或 external profile）和声明的 template，建立文档结构与一级大纲。

## 何时使用

- 已完成 Step 3（来源索引），run 处于 phase_1。
- 需要确定文档章节骨架后再进入证据与写作规划。

## 引擎命令

```bash
$PYTHON -m ai_writing_plugin outline-run --run <run_dir>
```

## 输入

- `manifest.json`、`task_brief.json`
- `inputs/input_inventory.json`
- template role 材料（如有）

## 产出 artifacts

- `plans/template_structure.json`
- `plans/outline_l1.md`

## 边界与约束

- template 是结构约束，不是项目事实支撑。
- `strict_template` 为真时不得擅自增删强制章节。
- 大纲只定义结构，不在此步填入未经证据支撑的结论。
- 不为每种文档类型新建独立 pipeline；差异由 `DocumentTypeRules` 表达。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核并修订本步产出，直到满意后才能进入下一步。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须**自主**地分别对「审核任务」与「修订任务」做动态任务分解，并在同一 `state.json` 中以两个独立任务组（`review_state` / `revision_state`）各自跟踪进度，无需人工逐步介入。

#### A1. 审核任务：自主分解与进度跟踪

针对"审核本步产出是否满足边界与约束"这一任务，自主分解为逐项可判定的审核子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：自主生成 **≥2 种**不同的审核分解方案，对每种做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定；被放弃的方案与理由记入 state.json 的 review_state。
   - 本步审核候选方案（示例）：方案A 按检查维度逐项核对；方案B 按 artifact/章节逐项核对；方案C 先扫高风险约束（strict_template 强制章节保留与跨文档类型术语泄漏）再补其余。试跑对比后择优。
2. **分解与执行（第一性原理：以「单条审核检查项」为自然单元）**：把审核沿检查项拆为多步子任务依次核对，子任务应足够小、可独立判定通过/不通过。本步典型审核子任务：① 核对模板覆盖是否完整；② 核对 strict_template 强制章节是否保留；③ 扫描有无跨文档类型术语泄漏；④ 核对大纲是否非空且非敷衍。
3. **进度跟踪（state.json·review_state）**：在 `runs/<run_id>/subagent/<step>/state.json` 的 `review_state.subtasks` 为每个审核子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；全部审核子任务为 `done` 且无 P0/P1 后审核阶段才算结束。

#### A2. 修订任务：自主分解与进度跟踪

针对"修订本步产出"这一任务（提取脚本目的、重新驱动，而非机械重跑原脚本），自主分解为可执行修订子任务并跟踪进度：

1. **方案阶段（生成多方案、评估择优）**：针对本步脚本真正要完成的「依模板材料与文档类型规则建立 template_structure 与一级大纲」自主生成 **≥2 种**不同的任务分解方案，对每种方案做评估与小规模试跑（按覆盖度、可靠性、成本、可验证性比较），择优选定最终方案；被放弃的方案与选择理由记入 state.json 的 revision_state。
   - 本步修订候选方案（示例）：方案A 直接套用文档类型内置模板骨架；方案B 从 inventory 选取的 template 材料提取章节结构；方案C 二者合并去重（strict_template 强制章节优先）。试跑对比后择优。
2. **分解与执行（第一性原理：以「模板章节」逐节为自然单元）**：从本步要完成的任务出发，把长任务沿该自然单元拆为多步子任务（或多个并列子任务），依次遍历执行；子任务应足够小、可独立验证。本步典型子任务：① 选取 template 材料并解析其章节；② 与文档类型规则合并建 template_structure；③ 逐节生成 order/section_id/title/intent；④ 标注 strict_template 强制章节与 needs_human_confirmation。
3. **进度跟踪（state.json·revision_state）**：在同一 `state.json` 的 `revision_state.subtasks` 为每个修订子任务登记一条记录，状态字段**仅三种取值**：`not_run` / `running` / `done`；子任务开始时置 `running`，完成且自检通过后置 `done`；全部修订子任务为 `done` 后本步才算结束。

state.json 最小结构示例（本步，含审核/修订两组任务）：

```json
{
  "step": "template-outline",
  "review_state": {
    "chosen_plan": "<选定审核方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rv-1", "desc": "核对模板覆盖完整", "status": "done"},
      {"id": "rv-2", "desc": "核对 strict_template 强制章节保留", "status": "running"},
      {"id": "rv-3", "desc": "扫描跨文档类型术语泄漏", "status": "not_run"}
    ]
  },
  "revision_state": {
    "chosen_plan": "<选定修订方案>",
    "rejected_plans": ["<方案及放弃理由>"],
    "subtasks": [
      {"id": "rt-1", "desc": "选取 template 材料并解析章节", "status": "done"},
      {"id": "rt-2", "desc": "与文档类型规则合并建 template_structure", "status": "running"},
      {"id": "rt-3", "desc": "逐节生成 order/section_id/title/intent", "status": "not_run"},
      {"id": "rt-4", "desc": "标注强制章节与 needs_human_confirmation", "status": "not_run"}
    ]
  }
}
```

### B. 审核与修订要点

1. 派发新 subagent（fresh context），交付本步 artifact（`plans/template_structure.json`、`plans/outline_l1.md`）与本文「边界与约束」作为审核标准。
2. subagent 逐项核对：模板覆盖是否完整，`strict_template` 强制章节是否保留，是否存在跨文档类型术语泄漏，大纲是否非空且非敷衍。
3. **发现问题时修订（提取脚本目的、重新驱动，不机械重跑原脚本）**：不要再机械重跑原脚本（`$PYTHON -m ai_writing_plugin outline-run --run <run_dir>`）。先把该脚本的执行目的细化展开为以下要点，再由 subagent 围绕这些目的重新驱动完成本步任务，必要时依据这些目的为当前任务重新生成更适用的新脚本来执行：
   - 从 inventory 选取 template 材料（select_template），结合文档类型规则建立 `plans/template_structure.json`。
   - 生成带 order/section_id/title/intent 的结构化章节，并标注 needs_human_confirmation。
   - 保留 strict_template 的强制章节（mandatory sections），不得删减或改名。
   - 渲染一级大纲 `plans/outline_l1.md`。
   - 只定义结构与章节意图，不写正文、不预设结论。
   - **底线**：修订后的产出须符合本步 artifact 契约与上述边界、保持可追溯，不得伪造或越权。
4. 修订后重新审核，循环直到无 P0/P1 问题且满足全部边界，记录审核结论。
5. subagent 审核满意后，再执行下方交接（并配合 workflow-orchestrator 的用户确认闸门）。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 5 · 研究问题**（`evidence-run` 产出 `research_questions.json`）。
