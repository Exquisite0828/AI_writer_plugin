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

**规则**：Phase A 全部子任务 `done` 后才进入 Phase B；Phase B 全部 `done` 后才进入 Phase C。子任务状态仅 `not_run` / `running` / `done`，由当前 step worker在隔离执行上下文的 `execution_state` 中跟踪。该进度不持久化为独立runtime artifact，也不进入controller上下文或ProgressLedger。

## 何时使用

- 已完成 Step 5（大纲分析与写作计划），对应 artifacts 已由 worker 生成并在 StepResult 中报告。
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

## 边界与约束

- `EVD-xxx` 须经 **L1→L2→L3→阅读原文**；只接受 T0/T1 支撑 critical claim。
- `claim_support_matrix.json` 是 N4 核心溯源 artifact，须保留 tier 与 claim 状态。
- `section_tasks.json` 中 `allowed_evidence` 须对应本步 Phase A 的 `EVD-xxx`。
- sample/reference 不能作为事实证据；不得移除 NEEDS_USER_CONFIRMATION。

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

进入 **Step 7 · 保守草稿**（`draft/full_draft.md`）。草稿按 `section_tasks.json` + `outline_final.md` + `writing_plan.md` 执行。
