# FSR 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点（三阶段顺序）

### Phase A · 证据映射

- **L1→L2→L3→原文** → `EVD-xxx`；critical claim 仅 T0/T1。
- HARA 摘要 EVD **不得**超出摘要显式追溯范围。

### Phase B · 引用计划

- claim 类型：`fsr_wording`、`safety_goal_linkage`、`asil_inheritance`、`safe_state_linkage`、`verification_method`、`requirement_completeness`、`requirement_sufficiency`。
- 缺证据 → `NEEDS_USER_CONFIRMATION`。

### Phase C · 章节任务

- `TASK-xxx` + `outline_final.md`、`section_tasks.json`、`writing_plan.md`。

## FSR 方法论（本步定位）

本步对应 **阶段 4：证据映射 → 引用计划 → 章节任务**。

### 阶段 4a · 证据映射

- FSR 措辞、SG 链接、ASIL、验证方法 → 文档 + L1/L2/L3 + 摘录。
- 有来源 → `EVD-xxx`；无来源 → `unresolved_questions.md`。

### 阶段 4b · 引用计划

- 哪条 FSR-xx 引用哪份 SG source 哪段。
- HARA 摘要 **仅**支撑其显式 HE→SG，不 blanket 批准全部 FSR。

### 阶段 4c · 章节任务

| writing_mode | 含义 |
|---|---|
| supported | 证据充分 |
| conservative_candidate | 保守候选 |
| confirmation_required | 须 HITL |
| placeholder_only | 仅占位 |

### Critical Claims（§6，须 T0/T1 或 open）

- 功能安全需求表述（wording）
- Safety Goal 链接
- ASIL 继承
- 安全状态（safe state）链接
- 验证方法
- 需求完整性 / 充分性
- FSR 最终批准 / 合规结论

### 证据 tier（§6）

| Tier | 用途 | critical claim |
|---|---|---|
| T0 | HITL | 允许 |
| T1 | SG、HARA 摘要、Item 定义等 | 允许 |
| T2 | template/checklist | 仅结构 |
| T3 | reference | 不单独证明项目事实 |
| T4 | sample | **禁止** |
| T5 | 推断 | **禁止** |

## TASK 映射示例

| TASK | L2 | writing_mode |
|---|---|---|
| TASK-SG | SG 追溯 | conservative_candidate |
| TASK-FSR | FSR-xx 表 | conservative_candidate |
| TASK-ASIL | ASIL 继承 | conservative_candidate |
| TASK-VERIF | 验证方法 | confirmation_required |
| TASK-OPEN | 开放项 | open_issue_list |
| TASK-DIFF | Δ-Analysis · 与参考 FSR 的差异 | **仅 With-Reference**：结构/流程差异，allowed_evidence 不含参考 FSR 需求事实 |

## 本步 Review / Checklist 要点

### Phase A · 证据映射 Checklist

- [ ] 每条 FSR/SG/ASIL/验证 claim 有 EVD 或 `unresolved_questions.md`
- [ ] EVD 含 L1/L2/L3 provenance
- [ ] HARA 摘要 EVD **不超出**显式追溯
- [ ] T4/T5 **不支撑** critical claim

### Phase B · 引用计划 Checklist

- [ ] `claim_support_matrix` 覆盖：fsr_wording、sg_linkage、asil_inheritance、verification_method 等
- [ ] 缺证据 → `NEEDS_USER_CONFIRMATION`

### Phase C · 章节任务 Checklist

- [ ] `section_tasks.json` 与 matrix 一致
- [ ] **With-Reference**：含 **TASK-DIFF**（Δ-Analysis 任务）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 大量 `confirmation_required` 属正常 | matrix 中**不得**出现「参考 FSR 支撑 FSR-xx」 |
| 每条 FSR TASK 须有 SG 链接或 open | Δ task 的 `allowed_evidence` **不含**参考 FSR 需求事实 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 编造 citation | sample 进 matrix |

### 常见 P0

| 错误 | 后果 |
|---|---|
| sample/参考 FSR 支撑 FSR/SG/ASIL | 事实来源违规 |
| 编造 SG 链接 / citation | 不可追溯 |
| HARA 摘要 blanket 支撑全部 FSR | 批准边界错误 |

## A1 / A2 / B

**A1**：七类 artifact 齐全；EVD↔matrix↔TASK 一致。  
**A2**：失败 phase 重跑。  
**B**：每条 FSR TASK 有 SG 链接或 open。
