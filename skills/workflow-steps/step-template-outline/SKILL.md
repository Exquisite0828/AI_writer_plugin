---
name: step-template-outline
description: 中文优先指导 workflow 第 4 步「模板大纲」：综合用户写作任务、模板文档与同类型参考文档，先确定文档结构与一级大纲，再按实际情况确定二级大纲；产出 template_structure.json、outline_l1.md、outline_l2.md。
---

# Step 4 · 模板大纲 (Template Outline)

工作流第 4 步。综合**用户写作任务**（`task_brief`）、**模板文档**（`role=template`）、**同类型参考文档**（通常为 `role=sample` 或同类已交付样例；必要时 `role=reference` 中的结构范例），先确定**交付文档的结构与一级大纲（L1）**；**一级大纲确定后**，再结合模板细分、参考文档章节粒度、任务 `critical_claims` 与 Step 3 输入材料导航覆盖情况，**按实际情况**确定每个 L1 下的**二级大纲（L2）**。

本步只定义**要写出的报告**的结构与大纲，不填入未经证据支撑的项目事实或专业结论。

## 何时使用

- 已完成 Step 3（文档目录索引），run 处于 phase_2 规划起点。
- 需要固化「写哪几章（L1）、每章下写哪几块（L2）」后再进入研究问题与证据规划。

## 输入

| 来源 | 用途 |
|---|---|
| `manifest.json`、`task_brief.json` | 写作任务：`task_type`、目标读者、`critical_claims`、`strict_template`、`requires_human_confirmation` 等 |
| `inputs/input_inventory.json` | 定位 template / sample / reference 材料及 parse 状态 |
| `role=template` 材料 | **结构约束**（强制章节、顺序、表格形状）；经 Step 3 的 `document_tocs` **L1→L2→L3** 阅读，不得全文盲搜 |
| `role=sample` 或同类型参考文档 | **章节粒度、表格列、小节划分**参考（T4 风格）；只借结构，不借项目事实 |
| `role=reference`（可选） | 方法学/标准文档的**章节组织**参考（T3）；不借具体评级或结论 |
| `knowledge/source_index.json`（`topic_index`） | 判断输入材料是否支撑某 L2 小节（有/无/gap），影响 L2 是否保留或标 open |
| `knowledge/knowledge_gaps.md` | 材料缺失时 L2 仍可有占位，但须标 `pending` / 待证据 |

## 执行方法（两阶段，必做）

### 阶段 A · 确定文档结构与一级大纲（L1）

1. **读懂写作任务**：从 `task_brief` 提取文档类型、交付范围、强制关注点、是否 `strict_template`。
2. **读模板文档（结构）**：对 `role=template` 且已解析的材料，经 `document_tocs/<file_id>.md` **L1→L2→L3** 提取章节骨架、强制节、顺序；template 是 T2 结构约束，不是事实来源。
3. **读同类型参考文档（形状）**：对 `role=sample`（及用户声明的同类型参考），同样经三级目录浏览，提取**章节划分与表格形状**；sample 是 T4，**不得**将其中的 hazard/评级/结论升为本项目 L1 内容。
4. **合并定 L1**：在 `DocumentTypeRules`（或 external profile）约束下，合并任务要求 + 模板强制节 + 参考文档章节粒度，产出 L1 列表（`section_id`、title、order、required、intent、`needs_human_confirmation`）。
5. **写入** `plans/template_structure.json` 的 L1 节点（`level=1`）与 `plans/outline_l1.md`。

**阶段 A 完成标志**：L1 列表完整、强制节未遗漏（`strict_template` 时不可删改 mandatory id/title）、且尚未展开 L2 或 L2 仅为占位。

### 阶段 B · 确定二级大纲（L2）

**仅在阶段 A 的 L1 已定稿后**执行：

1. **按 L1 逐章展开**：对每个 L1 section，结合以下来源定 L2 小节（不预设正文结论）：
   - 模板文档在该 L1 下的 L2/L3 目录（经 `document_tocs` 逐级阅读）
   - 同类型参考文档在同主题下的**小节划分与表格列**（结构参考）
   - 写作任务对该章的 `critical_claims` / 检查要求
   - Step 3 `topic_index`：输入材料是否已有对应主题（影响 L2 是否标 `evidence_expected` / `pending`）
2. **按实际情况裁剪或增补 L2**：材料充分则可细分；材料缺失则 L2 保留占位并标 open；不得为凑结构编造与任务无关的小节。
3. **写入** `template_structure.json` 的 L2 节点（`level=2`，`parent_id` 指向 L1）与 `plans/outline_l2.md`（逐 L1 列出 L2 及 intent / 证据预期状态）。

## 产出 artifacts

| 路径 | 用途 |
|---|---|
| `plans/template_structure.json` | 结构化节点树：L1 + L2（`nodes` / `outline_sections`），含 template 来源与 fallback 说明 |
| `plans/outline_l1.md` | 一级大纲可读稿（章节 id、标题、强制、intent、确认要求） |
| `plans/outline_l2.md` | 二级大纲可读稿（每个 L1 下的 L2 小节、intent、证据/开放状态说明） |

## template_structure.json 与本步约定

在既有 artifact 契约基础上，本步 skill 约定：

- **L1 节点**：`level=1`，对应交付报告章。
- **L2 节点**：`level=2`，`parent_id` 指向所属 L1 的 `node_id` / `section_id`。
- `template_source` 记录实际采用的 template 文件；`warnings` 记录多 template 冲突、fallback、参考文档仅作形状说明等。
- `outline_sections` 与 `nodes` 中 L1 条目与 `outline_l1.md` 一致；L2 与 `outline_l2.md` 一致。

## outline_l1.md / outline_l2.md 建议结构

**outline_l1.md** 须含：Run id、template 来源、L1 章节列表（section_id、title、required、intent、needs_human_confirmation）、warnings、阶段边界说明。

**outline_l2.md** 须含：

```markdown
# Outline L2

## {L1 section_id} · {L1 title}
- {L2_id} · {L2 title} — intent: … — evidence: expected|pending|n/a
```

## 输入文档访问约定（读 template / 参考文档时）

读 template、sample、reference **原文**时须 **L1→L2→L3→原文**（见 `writing-core`）。本步从上述材料只提取**结构与形状**，不提取项目事实。

## 边界与约束

- **fact source ≠ sample**：sample/参考文档只影响 L1/L2 **结构**，不得将其中的项目结论写入 intent 或当作已确认内容。
- template（T2）约束结构；`strict_template=true` 时不得删改 mandatory L1。
- L2 须在 L1 确定后再定；不得跳过 L1 直接写满 L2 细节。
- 大纲只定义结构与写作意图，不在此步写正文、不预设 hazard/rating/ASIL/测试结论等。
- 差异由 `DocumentTypeRules` + 任务专属子 skill 表达，不为每种文档类型新建独立 pipeline。

## 加载任务专属子 skill（必做）

本步是**通用骨架**。执行前须按 `task_type` 加载：

- 路径：`skills/document-types/<task_type>/steps/step-template-outline.md`
- 配合根 skill `skills/document-types/<task_type>/SKILL.md`

若子 skill 缺失，须显式报告并停下确认。

## 子代理审核 (Subagent Review)

本步执行结束前，必须由 Claude Code **新开一个独立 subagent**，审核本步已产出的 artifacts。subagent 默认只审核，不重新生成 L1/L2 大纲；只有发现 P0/P1 时才允许进入局部修订。

审核通过且无 P0/P1 时，subagent 只能写入 `runs/<run_id>/subagent/step-template-outline/state.json` 与本 stage 必需的 review artifacts；不得重写 `plans/template_structure.json`、`plans/outline_l1.md` 或 `plans/outline_l2.md`。P2/P3 只记录为待用户确认的问题，不得自动修订本步 artifacts。

### A. 自主任务分解与进度跟踪（将 human 移出 loop）

subagent 必须先对「审核任务」做动态任务分解，并在同一 `state.json` 中以 `review_state` 跟踪进度。`revision_state` 只有在审核发现 P0/P1 时才执行；无 P0/P1 时记录 `revision_required=false`。P2/P3 不触发 A2 修订。

#### A1. 审核任务：自主分解与进度跟踪

1. **方案阶段**：自主生成 ≥2 种审核分解方案，择优；放弃方案记入 `review_state`。
2. **分解与执行**：以「L1 完整性 / L2 与 L1 对应 / 来源边界」等为单元逐项核对。
3. **进度跟踪**：`review_state.subtasks` 状态仅 `not_run` / `running` / `done`。

#### A2. 修订任务：自主分解与进度跟踪

1. **方案阶段**：仅围绕已确认的 P0/P1 issue 生成 ≥2 种局部修订方案；P2/P3 不进入自动修订。
2. **分解与执行**：每个修订子任务必须绑定 `issue_id`、`target_artifact`、`changed_paths`。只改受影响的 L1/L2 节点或对应 review artifact；不得重新生成整份大纲。
3. **进度跟踪**：`revision_state.subtasks` 同上。

state.json 最小结构见任务专属子 skill 的「state.json 示例」。

### B. 审核与修订要点

1. 交付三份 artifact + 边界 + 子 skill「B 审核检查项」作为审核标准。
2. 发现 P0/P1 时按 A2 局部修订；若无 P0/P1，只记录审核结论，不得重写大纲。P2/P3 只能进入 review artifacts，等待用户确认。
3. 修订后只重审受影响 issue 与 artifact；无 P0/P1 后进入交接。

subagent 约束：不得把 sample/reference 当事实、不得移除 NEEDS_USER_CONFIRMATION、不得输出专业批准结论。

## 交接到下一步

进入 **Step 5 · 大纲分析与写作计划**（`section_writing_plans.json`）。后续 Step 6 消费各段写作计划完成证据·引用·章节任务。
