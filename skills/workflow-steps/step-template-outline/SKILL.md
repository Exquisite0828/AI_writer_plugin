---
name: step-template-outline
description: 中文优先指导 workflow 第 4 步「模板大纲」：综合用户写作任务、模板文档与同类型参考文档，先确定文档结构与一级大纲，再按实际情况确定二级大纲；产出 template_structure.json、outline_l1.md、outline_l2.md。
---

# Step 4 · 模板大纲 (Template Outline)

工作流第 4 步。综合**用户写作任务**（`task_brief`）、**模板文档**（`role=template`）、**同类型参考文档**（通常为 `role=sample` 或同类已交付样例；必要时 `role=reference` 中的结构范例），先确定**交付文档的结构与一级大纲（L1）**；**一级大纲确定后**，再结合模板细分、参考文档章节粒度、任务 `critical_claims` 与 Step 3 输入材料导航覆盖情况，**按实际情况**确定每个 L1 下的**二级大纲（L2）**。

本步只定义**要写出的报告**的结构与大纲，不填入未经证据支撑的项目事实或专业结论。

## 何时使用

- 已完成 Step 3（文档目录索引），对应 artifacts 已由 worker 生成并在 StepResult 中报告。
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
4. **合并定 L1**：在当前 task 声明、所选 document-type Skill/overlay 与用户材料约束下，合并任务要求 + 模板强制节 + 参考文档章节粒度，产出 L1 列表（`section_id`、title、order、required、intent、`needs_human_confirmation`）。当前 Python 不加载 external profile 或 type rules。
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
- 当前差异由任务声明 + 任务专属 Skill/overlay 表达，不为每种文档类型新建独立 pipeline。未来 executable rules 需要独立 active phase。

## 当前 worker 与 document-type guidance

当前 step worker 只能通过 StepContextPackage.instruction_refs[] 中的 path/hash 读取已纳入 package 的 instructions。wrapper 与本 canonical workflow Skill 是必需引用；document-type root Skill 与 per-step overlay 都按文件存在性懒加载，未出现时不加入 package。root Skill 存在但 per-step overlay 缺失是合法的 root-only 模式；可选 document-type root Skill 或 overlay 未出现不得判为 `metadata_invalid`。所有实际出现在 `instruction_refs[]` 中的引用都必须通过 path/hash 校验；已包含的引用缺失或 hash 无效时返回 `metadata_invalid` 并停止。不得由 controller 直接加载这些正文，不得读取 sibling document types。

## StepResult 与 stage review交接

当前 step worker 读取允许的refs，生成本步声明的专业artifacts，写入并自行校验StepResult，然后返回并结束。它不得继续派发其他worker，也不得创建独立审核状态或stage gate。

Stage review worker 在本stage所有StepResult完成后由controller统一调度，只接收ReviewContextPackage路径。它按 `steps[]` 顺序沿 `context_package_refs[]` 读取本canonical与当前document-type guidance；overlay存在时叠加其领域检查。

### A1/B 通用审核检查

- 本步声明的必需artifact均存在，StepResult path/hash与最终文件一致。
- 产出满足本canonical的输入、输出、顺序和边界约束。
- sample/reference未被当作项目事实，critical claim缺T0/T1时仍为pending或 `NEEDS_USER_CONFIRMATION`。
- 未生成批准、合规、风险接受或生产就绪结论。
- 当前document-type guidance存在时，其A1/B领域检查全部执行。

### A2 局部修订

Stage review worker只记录问题，不修改专业artifact或StepResult。它必须先汇总写入 `stage_reviews/<stage>/issues.json`，再对该stage一次性调用 `build-stage-review-issues` 与 `validate-stage-review-issues`，由builder原子生成并校验固定路径的index/details。本step存在P0/P1或明确返工项时，其ReviewResult返回 `needs_revision`；P2/P3只进入review/open items。A2由重新派发的原step worker执行，并绑定 `issue_id`、`target_artifact`、`changed_paths`；A2 worker不得自行派发其他step。若目标不是最后一步，controller按自动依赖协议重跑被失效的后续step。

Stage review worker为本step写入并校验一个ReviewResult，不创建第二套持久化编排状态。

## 交接到下一步

进入 **Step 5 · 大纲分析与写作计划**（`section_writing_plans.json`）。后续 Step 6 消费各段写作计划完成证据·引用·章节任务。
