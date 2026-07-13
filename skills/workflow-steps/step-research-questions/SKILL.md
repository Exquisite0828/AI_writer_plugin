---
name: step-research-questions
description: 中文优先指导 workflow 第 5 步「大纲分析与写作计划」：对 Step 4 大纲逐段分析研究，读参考文档与领域经验，为每一 L2 小节产出写作计划；worker内部顺序跟踪子任务，汇总 section_writing_plans.json。
---

# Step 5 · 大纲分析与写作计划 (Outline Analysis & Section Writing Plans)

工作流第 5 步。对 Step 4 产出的大纲（`outline_l1.md` + `outline_l2.md`）进行**分析与研究**，结合写作任务（`task_brief`）与用户参考文档，为大纲中**每一小段（L2 小节）**生成可执行的**写作计划**；顺序执行子任务，汇总为 `section_writing_plans.json`。

## 本步核心逻辑

1. **读取前步大纲**：理解 Step 4 的 L1 章 + L2 小节、`intent`、强制要求、证据预期。
2. **逐段分析研究**：按大纲顺序（L1 → L2）遍历；对每个 L2（无 L2 的 L1 则按 L1 一条）登记一条**分析子任务**。
3. **登记执行进度**：当前 step worker可在隔离执行上下文中维护 `research_state.subtasks`；状态仅为 `not_run` / `running` / `done`。该进度不持久化为独立runtime artifact，也不进入controller上下文或ProgressLedger。
4. **顺序执行**：取第一条 `not_run` → `running` → 分析研究该段 → 写出该段写作计划 → `done` → 更新worker内部进度 → 继续下一条。
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

- 已完成 Step 4（模板大纲），对应 artifacts 已由 worker 生成并在 StepResult 中报告。
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

## 执行顺序（主流程）

1. **初始化**：遍历 `outline_l2.md`（无 L2 的 L1 各一条），生成 `research_state.subtasks`（`sp-*`），全部 `not_run`。
2. **顺序执行**（直至无 `not_run`）：
   - 取第一条 `not_run` → `running`
   - 分析研究该段 → 写出该段 `section_writing_plan` 条目（及可选 `.md`）
   - `done` → 更新worker内部进度
3. **合并定稿**：全部 `done` 后写入 `section_writing_plans.json`。
4. **完成交接**：写入并校验StepResult后返回controller。

## 边界与约束

- 本步产出**写作计划**，不产出章节正文、不给出 hazard/rating/ASIL 等**最终专业结论**。
- 计划中的 `content_outline` / `writing_steps` 可描述表格形状与写作顺序；critical 段须标 `requires_human_confirmation: true`。
- 每个 L2 宜有一条对应计划；`evidence: pending` 的 L2 计划须 `status: partial` 或 `blocked` 并列出 `gaps`。
- 子任务粒度默认 **outline L2 小节**；复杂 L2 可在子 skill 拆多条 `sp-*`（仍顺序执行）。
- 不引入 RAG / 向量库 / 复杂 agent 框架。

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

进入 **Step 6 · 证据·引用·章节计划**。Step 6 读取 `section_writing_plans.json`，三阶段产出 evidence_map、citation_plan、section_tasks 等全部写作前计划 artifact。
