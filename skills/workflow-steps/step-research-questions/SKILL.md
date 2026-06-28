---
name: step-research-questions
description: 中文优先指导 workflow 第 5 步「大纲分析与写作计划」：对 Step 4 大纲逐段分析研究，读参考文档与领域经验，为每一 L2 小节产出写作计划；state.json 顺序跟踪子任务，汇总 section_writing_plans.json。
---

# Step 5 · 大纲分析与写作计划 (Outline Analysis & Section Writing Plans)

工作流第 5 步。对 Step 4 产出的大纲（`outline_l1.md` + `outline_l2.md`）进行**分析与研究**，结合写作任务（`task_brief`）与用户参考文档，为大纲中**每一小段（L2 小节）**生成可执行的**写作计划**；顺序执行子任务，汇总为 `section_writing_plans.json`。

## 本步核心逻辑

1. **读取前步大纲**：理解 Step 4 的 L1 章 + L2 小节、`intent`、强制要求、证据预期。
2. **逐段分析研究**：按大纲顺序（L1 → L2）遍历；对每个 L2（无 L2 的 L1 则按 L1 一条）登记一条**分析子任务**。
3. **登记执行进度**：主执行上下文为本步维护 `research_state.subtasks`；状态**仅三种**：`not_run` / `running` / `done`。该进度不等于 subagent 审核 state。
4. **顺序执行**：取第一条 `not_run` → `running` → 分析研究该段 → 写出该段写作计划 → `done` → 写回 state.json → 继续下一条。
5. **汇总产出**：各段写作计划合并写入 `plans/section_writing_plans.json`（可选配套 `plans/section_plans/<section_id>.md` 可读稿）。

## 单个子任务的职能

针对当前大纲**小段**（L2 / 或唯一 L1）：

1. **理解段落要求**：读取 `outline_l2.md` 中该节的 `intent`、表格/段落形状、`evidence: expected|pending`。
2. **分析与研究**：结合大模型对该文档类型的写作经验，判断本节应写什么、怎么组织、需哪些事实依据、哪些须 HITL。
3. **阅读参考文档**：经 `topic_index` 定位，按 **L1 → L2 → L3 → 原文** 阅读 T0/T1 事实源与 T3 方法学（见 writing-core）；**禁止** T4 sample 充当事实。
4. **产出该段写作计划**（见下「单段写作计划字段」）：明确写前准备、内容骨架、证据需求、缺口与写作模式建议；**不在此步写正文结论**。

## 单段写作计划字段（写入 section_writing_plans.json）

每条计划对应一个大纲 L2 小节（或 L1 唯一段）：

| 字段 | 说明 |
|---|---|
| `section_id` | L2 小节 id（或 L1 id） |
| `parent_section_id` | 所属 L1 章 id |
| `title` | 小节标题 |
| `writing_intent` | 本节写作目的（来自大纲 intent + 分析结论） |
| `content_outline` | 建议段落/表格结构（列、行类型、顺序） |
| `writing_steps` | 建议写作子步骤（先写什么、后写什么） |
| `required_evidence` | 本节需哪些 T0/T1 事实（描述性，非 EVD 编号） |
| `source_hints` | 已读材料的导航路径：`file_id` + L1/L2/L3 + 用途说明 |
| `research_notes` | 分析研究摘要（材料里有什么、缺什么） |
| `gaps` | 知识缺口 / 待补材料 |
| `writing_mode_hint` | 建议模式：`supported` / `conservative_candidate` / `confirmation_required` / `open_issue_list` / `unsupported_stub` |
| `requires_human_confirmation` | 是否含 critical claim 或缺证据 |
| `status` | `ready` / `partial` / `blocked`（材料是否足以支撑计划执行） |

## 何时使用

- 已完成 Step 4（模板大纲），run 处于 phase_2。
- 需要在大纲骨架上，为每小段形成「写之前该怎么写」的计划，供后续证据映射与成稿使用。

## 输入

- `task_brief`（或等效写作任务说明）
- `plans/template_structure.json`、`plans/outline_l1.md`、`plans/outline_l2.md`
- `knowledge/source_index.json`（`topic_index`）
- `knowledge/provenance_index.json`
- `knowledge/document_tocs/`
- `knowledge/knowledge_gaps.md`
- 用户输入参考文档（按 provenance **逐级**定位后读取）

## 输入文档访问约定（强制，见 writing-core）

每个分析子任务读参考文档时：

1. （可选）`topic_index` 命中 `file_id` + L1/L2/L3 候选
2. `document_tocs/<file_id>.md` **L1 → L2 → L3** 选叶子
3. `provenance_index` 取 `location` 后读原文
4. 无入口或 gap → 该段计划标 `status: blocked` 或 `partial`，`gaps` 如实登记

**禁止**：跳过三级目录全文盲读；`SRC-xxx` / chunk；目录 `brief` 当事实；T4 sample 支撑 critical claim 内容。

## 产出 artifacts

- `plans/section_writing_plans.json`（**主产出**：每 L2 一条写作计划）
- `plans/section_plans/<section_id>.md`（可选：单段可读计划）
- 本步执行进度 state（由主执行上下文维护，不作为 subagent 审核 state）

## state.json 结构

```json
{
  "step": "research-questions",
  "research_state": {
    "subtasks": [
      {
        "id": "sp-001",
        "section_id": "SEC-ITEM-L2-01",
        "parent_section_id": "SEC-ITEM",
        "desc": "分析 Item 功能清单 L2：读 item 材料，产出功能表写作计划",
        "status": "not_run"
      }
    ]
  },
  "review_state": { "chosen_plan": "", "rejected_plans": [], "subtasks": [] },
  "revision_state": { "chosen_plan": "", "rejected_plans": [], "subtasks": [] }
}
```

**状态规则**：仅 `not_run` | `running` | `done`；同时最多一条 `running`；每完成一条立即写回 `done`。

## 执行顺序（主流程）

1. **初始化**：遍历 `outline_l2.md`（无 L2 的 L1 各一条），生成 `research_state.subtasks`（`sp-*`），全部 `not_run`。
2. **顺序执行**（直至无 `not_run`）：
   - 取第一条 `not_run` → `running`
   - 分析研究该段 → 写出该段 `section_writing_plan` 条目（及可选 `.md`）
   - `done` → 写 state.json
3. **合并定稿**：全部 `done` 后写入 `section_writing_plans.json`。
4. **子代理审核**：进入下方审核循环。

## 边界与约束

- 本步产出**写作计划**，不产出章节正文、不给出 hazard/rating/ASIL 等**最终专业结论**。
- 计划中的 `content_outline` / `writing_steps` 可描述表格形状与写作顺序；critical 段须标 `requires_human_confirmation: true`。
- 每个 L2 宜有一条对应计划；`evidence: pending` 的 L2 计划须 `status: partial` 或 `blocked` 并列出 `gaps`。
- 子任务粒度默认 **outline L2 小节**；复杂 L2 可在子 skill 拆多条 `sp-*`（仍顺序执行）。
- 不引入 RAG / 向量库 / 复杂 agent 框架。

## 加载任务专属子 skill（必做）

- 路径：`skills/document-types/<task_type>/steps/step-research-questions.md`
- 例：`task_type: hara` → HARA 各 L2 的默认分析子任务表、单段计划模板、A1/A2、B 检查项

## 子代理审核 (Subagent Review)

`research_state` 全部 `done` 且 `section_writing_plans.json` 初稿完成后，新 subagent 审核已产出的 artifacts。subagent 默认只审核；只有发现 P0/P1 或用户明确 `needs_revision` 时才允许进入局部修订。

### A1 / A2

- **A1**：按子 skill 典型审核子任务核对（覆盖 outline_l2、计划字段完整、无预设结论、无 sample 当事实）。
- **A2**：仅 P0/P1 或用户明确 `needs_revision` 时执行。修订必须绑定具体 `issue_id`、`target_artifact`、`changed_paths`，只修受影响段或对应 JSON 条目；P2/P3 只记录为待用户确认的问题，不得自动修订。

### B

交付 `section_writing_plans.json`、本步执行进度 state、边界 + 子 skill「B 审核检查项」。subagent 只能写入 `runs/<run_id>/subagent/step-research-questions/state.json` 与 stage-review 材料；无 P0/P1 时不得重写 `section_writing_plans.json` 或重跑本步。

## 交接到下一步

进入 **Step 6 · 证据·引用·章节计划**。Step 6 读取 `section_writing_plans.json`，三阶段产出 evidence_map、citation_plan、section_tasks 等全部写作前计划 artifact。
