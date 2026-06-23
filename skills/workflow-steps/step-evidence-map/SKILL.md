---
name: step-evidence-map
description: 中文优先指导 workflow 第 6 步「证据·引用·章节计划」（合并原证据映射/引用计划/章节任务）：按 section_writing_plans 逐段映射 EVD、规划 citation、拆章节写作任务；产出 evidence_map、unresolved_questions、citation_plan、claim_support_matrix、section_tasks、outline_final、writing_plan。
---

# Step 6 · 证据·引用·章节计划 (Evidence, Citation & Section Tasks)

工作流第 6 步（**合并原 Step 6–8**）。基于 Step 5 的 `section_writing_plans.json` 与各段写作计划，**顺序完成三阶段**：

1. **证据映射**：把各段 `required_evidence` 映射到 **L1→L2→L3→原文**，生成 `EVD-xxx`，标记已支撑/未解决项。
2. **引用计划**：规划每个 claim 引用哪些来源，建立 claim–证据支撑矩阵。
3. **章节任务**：把最终大纲拆成逐章节/逐小节写作任务，明确每节来源与引用。

## 三阶段执行顺序（强制）

| 阶段 | 原步骤 | 产出 |
|---|---|---|
| **Phase A · 证据映射** | 原 step-evidence-map | `evidence_map.json`、`unresolved_questions.md` |
| **Phase B · 引用计划** | 引用计划 | `citation_plan.json`、`claim_support_matrix.json` |
| **Phase C · 章节任务** | 章节任务 | `section_tasks.json`、`outline_final.md`、`writing_plan.md` |

**规则**：Phase A 全部子任务 `done` 后才进入 Phase B；Phase B 全部 `done` 后才进入 Phase C。子任务状态仅 `not_run` / `running` / `done`，登记于 `execution_state`，每完成一条立即写回 state.json。

## 何时使用

- 已完成 Step 5（大纲分析与写作计划），run 处于 phase_2/phase_3。
- 需要在成稿前完成：证据定位 → 引用编排 → 可执行章节任务。

## 输入

- `plans/section_writing_plans.json`（Step 5 各 L2 写作计划）
- `plans/template_structure.json`、`plans/outline_l1.md`、`plans/outline_l2.md`
- `knowledge/source_index.json`（`topic_index`）
- `knowledge/provenance_index.json`（L1→L2→L3 目录树与 L3 `location`）
- `knowledge/document_tocs/`、`knowledge/knowledge_gaps.md`
- 用户输入参考文档（按 provenance **逐级**定位后读取）

## Phase A · 证据映射

对 `section_writing_plans.json` 中每条计划的 `required_evidence` / `source_hints`：

1. （可选）`topic_index` 命中 `file_id` + L1/L2/L3
2. `document_tocs/<file_id>.md` **L1 → L2 → L3** 选叶子
3. `provenance_index` 取 `location` 后读原文
4. 摘录生成 `EVD-xxx`：provenance = `file_id` + L1/L2/L3 + `location` + `snippet`
5. 无法定位或无材料 → 写入 `unresolved_questions.md`，关联 `section_id`

**禁止**：跳过三级目录全文盲读；`SRC-xxx` / chunk；目录 `brief` 当 EVD；T4 sample 作 critical claim 证据。

## Phase B · 引用计划

基于 Phase A 的 `evidence_map.json` 与 `unresolved_questions.md`：

- 按 outline L1/L2 顺序，把各段 claim 与 `EVD-xxx` 归并，生成 `citation_slots`
- 建立 `claim_support_matrix.json`（含 tier、status、section_id）
- critical claim 无 T0/T1 支撑 → `NEEDS_USER_CONFIRMATION` / pending / open
- **不得**为缺证据 claim 编造引用

## Phase C · 章节任务

基于 Phase B 与 `section_writing_plans.json`：

- 合并 Step 4 L1+L2 与引用计划 → `outline_final.md`
- 每 L2（或 L1 唯一段）生成 `TASK-xxx`：`writing_mode`、`allowed_evidence`（EVD-xxx）、citation 槽
- 汇总 `section_tasks.json`、`writing_plan.md`
- **只规划不写正文**；保留 strict_template 强制章节

## 产出 artifacts（本步一次性全部交付）

- `plans/evidence_map.json`
- `plans/unresolved_questions.md`
- `plans/citation_plan.json`
- `plans/claim_support_matrix.json`
- `plans/section_tasks.json`
- `plans/outline_final.md`
- `plans/writing_plan.md`
- `runs/<run_id>/subagent/evidence-map/state.json`

## 边界与约束

- `EVD-xxx` 须经 **L1→L2→L3→阅读原文**；只接受 T0/T1 支撑 critical claim。
- `claim_support_matrix.json` 是 N4 核心溯源 artifact，须保留 tier 与 claim 状态。
- `section_tasks.json` 中 `allowed_evidence` 须对应本步 Phase A 的 `EVD-xxx`。
- sample/reference 不能作为事实证据；不得移除 NEEDS_USER_CONFIRMATION。

## state.json · execution_state 结构

```json
{
  "step": "evidence-map",
  "execution_state": {
    "phases": [
      {
        "id": "phase-a",
        "name": "证据映射",
        "status": "running",
        "subtasks": [
          {"id": "em-05", "section_id": "SEC-ITEM-L2-01", "desc": "功能清单：映射 required_evidence → EVD", "status": "done"},
          {"id": "em-06", "section_id": "SEC-ITEM-L2-02", "desc": "系统边界：映射 EVD", "status": "running"}
        ]
      },
      {
        "id": "phase-b",
        "name": "引用计划",
        "status": "not_run",
        "subtasks": [
          {"id": "cp-01", "desc": "按 L2 建立 citation_slots 与 claim_support_matrix", "status": "not_run"}
        ]
      },
      {
        "id": "phase-c",
        "name": "章节任务",
        "status": "not_run",
        "subtasks": [
          {"id": "st-01", "desc": "生成 section_tasks、outline_final、writing_plan", "status": "not_run"}
        ]
      }
    ]
  },
  "review_state": { "subtasks": [] },
  "revision_state": { "subtasks": [] }
}
```

Phase A 子任务默认**按 outline_l2 每 L2 一条** `em-*`；Phase B/C 粒度见所加载子 skill（HARA 可按 L1 或 L2 拆分 `cp-*` / `st-*`）。

## 加载任务专属子 skill（必做）

- 路径：`skills/document-types/<task_type>/steps/step-evidence-map.md`
- 例：`task_type: hara` → `skills/document-types/hara/steps/step-evidence-map.md`

从子 skill 获取：Phase A/B/C 领域规则、A1/A2 审核修订子任务、state.json 示例、B 审核检查项。若缺失须显式报告并停下。

## 子代理审核 (Subagent Review)

三阶段全部 `done` 且七类 artifact 初稿完成后，新 subagent 审核修订。

### A1 / A2

- **A1**：核对 Phase A/B/C 产出完整、EVD provenance、matrix tier、TASK allowed_evidence 一致；见子 skill「B 审核检查项」。
- **A2**：失败阶段将有关子任务重置为 `not_run`，**从该 phase 起重跑**（不必重跑已通过 phase，除非上游 artifact 变更）。

subagent 约束：不得把 sample 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 9 · 保守草稿**（`draft/full_draft.md`）。草稿按 `section_tasks.json` + `outline_final.md` + `writing_plan.md` 执行。
