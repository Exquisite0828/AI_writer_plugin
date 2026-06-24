# SyRS 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点（三阶段顺序）

### Phase A · 证据映射

- **L1→L2→L3→原文** → `EVD-xxx`；critical claim 仅 T0/T1。
- SEC-SAFE 的 EVD **不得**超出 FSR/SG source 显式引用范围。

### Phase B · 引用计划

- claim 类型：`requirement_wording`、`upstream_linkage`、`interface_definition`、`performance_limit`、`diagnostic_requirement`、`safety_related_linkage`、`verification_method`、`requirement_completeness`、`requirement_sufficiency`。
- 缺证据 → `NEEDS_USER_CONFIRMATION`。

### Phase C · 章节任务

- `TASK-xxx` + `outline_final.md`、`section_tasks.json`、`writing_plan.md`。

## SyRS 方法论（本步定位）

本步对应 **阶段 4：证据映射 → 引用计划 → 章节任务**。

### 阶段 4a · 证据映射

- SYS-F/IF 措辞、上游追溯、接口方向、性能/环境/诊断限值 → 文档 + L1/L2/L3 + 摘录。
- 有来源 → `EVD-xxx`；无来源 → `unresolved_questions.md`。

### 阶段 4b · 引用计划

- 哪条 SYS-F-xx 引用哪份 SWRS/RFQ 哪段。
- 哪条 SYS-IF-xx 引用哪份接口规范哪段（含方向）。
- SEC-SAFE **仅**引用 source 中显式 FSR/SG，不 blanket 批准全部 SYS-xx。

### 阶段 4c · 章节任务

| writing_mode | 含义 |
|---|---|
| supported | 证据充分 |
| conservative_candidate | 保守候选 |
| confirmation_required | 须 HITL |
| placeholder_only | 仅占位 |

### Critical Claims（须 T0/T1 或 open）

- 系统需求表述（wording）
- 干系人/上游需求链接（SWRS/RFQ）
- 接口定义（含方向、对端）
- 性能/环境/诊断限值
- 安全相关系统需求链接（若 SEC-SAFE）
- 验证方法
- 需求完整性 / 充分性
- SyRS 最终批准 / ASPICE 或 ISO 26262 合规结论

### 证据 tier

| Tier | 用途 | critical claim |
|---|---|---|
| T0 | HITL | 允许 |
| T1 | SWRS、RFQ、架构、接口规范等 | 允许 |
| T2 | template/checklist | 仅结构 |
| T3 | reference | 不单独证明项目事实 |
| T4 | sample | **禁止** |
| T5 | 推断 | **禁止** |

## TASK 映射示例

| TASK | L2 | writing_mode |
|---|---|---|
| TASK-STAKE | 干系人需求摘要 | conservative_candidate |
| TASK-FUNC | SYS-F-xx 表 | conservative_candidate |
| TASK-IF | SYS-IF-xx 表 | conservative_candidate |
| TASK-PERF | 性能需求 | confirmation_required |
| TASK-ENV | 环境约束 | conservative_candidate |
| TASK-DIAG | 诊断与降级 | conservative_candidate |
| TASK-SAFE | 安全相关系统需求 | confirmation_required |
| TASK-TRACE | 追溯矩阵 | conservative_candidate |
| TASK-VERIF | 验证方法 | confirmation_required |
| TASK-OPEN | 开放项 | open_issue_list |
| TASK-DIFF | Δ-Analysis · 与参考 SyRS 的差异 | **仅 With-Reference**：结构/流程差异，allowed_evidence 不含参考 SyRS 需求事实 |

## 本步 Review / Checklist 要点

### Phase A · 证据映射 Checklist

- [ ] 每条 critical claim 有 `EVD-xxx` 或登记到 `unresolved_questions.md`（**P0** 二选一）
- [ ] 每个 EVD 含：`claim_id`、`source_file_id`、`L1`、`L2`、`L3`、`location`、`tier`、`excerpt`
- [ ] EVD `tier` 仅 T0 / T1 用于 critical claim；T2/T3 仅作结构或方法学，T4/T5 **绝不**支撑 critical claim
- [ ] **SEC-SAFE 的 EVD**：仅来自 fsr_source / SG 清单中**显式列出**的 FSR/SG 段落（不得 blanket 引用）
- [ ] EVD 摘录与原文段落（L3 `location`）一致，不得扩写
- [ ] 七大主题（功能 / 接口 / 性能 / 环境 / 诊断 / 法规 / 安全）均有 EVD 或 gap

### Phase B · 引用计划 Checklist（9 类 claim 覆盖）

| claim 类型 | 必含 EVD 来源 | tier 要求 |
|---|---|---|
| `requirement_wording`（SYS-F/IF 表述） | SWRS / RFQ / HITL | T0/T1 |
| `upstream_linkage`（上游 ID 链接） | swrs_source ID 段落 | T1 |
| `interface_definition`（含 Direction） | interface_spec / CAN 矩阵 | T1 |
| `performance_limit`（限值） | 性能源 / HITL | T0/T1 |
| `environmental_constraint`（环境/电气） | ODD / 电气规范 | T1 |
| `diagnostic_requirement` | diagnostic_spec | T1 |
| `safety_related_linkage`（SEC-SAFE 引用） | fsr_source 显式 FSR/SG | T1（显式段落） |
| `verification_method` | 验证线索 / HITL | T0/T1，缺则 confirmation_required |
| `requirement_completeness_sufficiency` | checklist / HITL | T0/T2（仅作结构） |

- [ ] `claim_support_matrix.json` 每条 critical claim 至少 1 个 EVD 或 `NEEDS_USER_CONFIRMATION`
- [ ] 同一 EVD 不得 blanket 支撑多条无关 claim（粒度不当也是 P0）

### Phase C · 章节任务 Checklist

- [ ] `section_tasks.json` 每条 TASK 引用唯一 `section_id` + L2
- [ ] 每个 TASK 含 `allowed_evidence`（仅 EVD ID 与 HITL ID 列表）、`writing_mode`、`outputs`
- [ ] `outline_final.md` / `writing_plan.md` 与 TASK 列表一致
- [ ] **With-Reference**：含 **TASK-DIFF**（Δ-Analysis 任务），其 `allowed_evidence` **不含**参考 SyRS 内容字段

### TASK 全集示例

| TASK | 对应 L2 | writing_mode | allowed_evidence 范围 |
|---|---|---|---|
| TASK-STAKE | SEC-STAKE 客户需求摘要 | conservative_candidate | swrs/rfq EVD |
| TASK-FUNC | SEC-FUNC SYS-F 表 | conservative_candidate | 功能 EVD + HITL |
| TASK-IF | SEC-IF SYS-IF 表 | conservative_candidate | 接口 EVD（含 Direction） |
| TASK-PERF | SEC-PERF | confirmation_required（默认） | 性能 EVD |
| TASK-ENV | SEC-ENV | conservative_candidate | 环境 EVD |
| TASK-DIAG | SEC-DIAG | conservative_candidate | 诊断 EVD |
| TASK-SAFE | SEC-SAFE | confirmation_required | **仅** FSR/SG 显式 EVD |
| TASK-TRACE | SEC-TRACE | conservative_candidate | 上游 ID EVD |
| TASK-VERIF | SEC-VERIF | confirmation_required | 验证 EVD 或 HITL |
| TASK-OPEN | SEC-OPEN | open_issue_list | unresolved 汇总 |
| TASK-DIFF（仅 With-Reference） | SEC-DIFF | conservative_candidate | **本项目** source EVD + 参考 SyRS `style_hint`（**禁止**需求事实） |

### ASPICE / ISO 26262 维度 Checklist

- [ ] **ASPICE SYS.2 BP1**：TASK-STAKE 与 `claim_support_matrix.upstream_linkage` 闭环
- [ ] **ASPICE SYS.2 BP2**：每条 SYS-F/IF 在 matrix 中有 `requirement_wording` claim
- [ ] **ASPICE SYS.2 BP3**：matrix 含 `requirement_completeness_sufficiency` claim（其支撑可为 checklist+HITL）
- [ ] **ASPICE SYS.2 BP5**：matrix 覆盖 **上游→SyRS** 与 **SyRS→上游** 双向 claim
- [ ] **ISO 26262-3 §7（FSR 接口）**：`safety_related_linkage` claim 的 EVD 必须为 fsr_source 中显式列出的 FSR/SG
- [ ] **ISO 26262 forbidden**：matrix 不得含 `hazard_*` / `asil_*` / `safety_goal_*` / `tsr_*` claim 类型

### From-Scratch 专属 Checklist

- [ ] 大量 `confirmation_required` / `placeholder_only` 属正常；不强求 supported
- [ ] 每条 SYS-F TASK 至少链 1 个上游 EVD 或显式登记到 `unresolved_questions.md`
- [ ] SEC-SAFE TASK 若无 fsr_source，标 `placeholder_only`，**不**编造引用

### With-Reference 专属 Checklist

- [ ] `claim_support_matrix` **不得**出现「参考 SyRS file_id 支撑 SYS-xx」（**P0**）
- [ ] **TASK-DIFF 必存**，且 `allowed_evidence` 注释包含：`参考SyRS 仅作 style_hint，不可作事实`
- [ ] Δ-Analysis claim 类型（如 `delta_added` / `delta_removed`）的 EVD 仅来自本项目 source
- [ ] 参考 SyRS file_id 在 matrix 中只可作 `style_hint`，不可作 `evidence_source`

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| matrix 范围 | 多 confirmation / placeholder | 多 conservative_candidate，但逐条 EVD |
| 编造风险 | 凭经验编 citation → **P0** | 把参考 SyRS 进 matrix → **P0** |
| SEC-SAFE | placeholder 多 | 不得抄参考 SyRS 的 SEC-SAFE EVD |
| SEC-DIFF | — | TASK-DIFF + Δ claim 类型齐全 |
| 双向追溯 | 上游→SyRS 至少完成 | 同上 + Δ 决策追溯 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| sample / 参考 SyRS 支撑 SYS-xx/限值/接口 | 事实来源违规（**P0**） |
| 编造上游链接 / citation | 不可追溯 |
| SEC-SAFE blanket 支撑全部 SYS-xx | 批准边界错误 |
| matrix 含 hazard / ASIL / SG / TSR claim 类型 | 文档类型漂移 |
| TASK 的 `allowed_evidence` 含 T4 sample ID | 后续草稿违规 |

### 常见 P1

- EVD 摘录扩写超原文
- 同一 EVD 不当 blanket 支撑过多 claim
- TASK-DIFF 列入 sample 字段名作为 evidence

## A1 / A2 / B

**A1**：七类 artifact 齐全（evidence_map、unresolved_questions、citation_plan、claim_support_matrix、outline_final、section_tasks、writing_plan）；EVD↔matrix↔TASK 一致。  
**A2**：失败 phase 重跑；修正 tier 违规、补 BP3 / BP5 claim。  
**B**：每条 SYS-F/IF TASK 有上游链接或 open；SEC-SAFE 引用边界明确；With-Reference 含 TASK-DIFF。
