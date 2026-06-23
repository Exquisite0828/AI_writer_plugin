# TSC 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点（三阶段顺序）

### Phase A · 证据映射

- **L1→L2→L3→原文** → `EVD-xxx`；critical claim 仅 T0/T1。
- FSR source EVD **不得**超出 FSR 显式内容范围。
- HARA 摘要 EVD **不得**超出摘要显式 FTTI/安全状态/追溯范围。

### Phase B · 引用计划

- claim 类型：`tsr_wording`、`fsr_linkage`、`sg_linkage`、`architecture_allocation`、`safety_mechanism_concept`、`fault_handling_strategy`、`safe_state_degradation`、`interface_safety_requirement`、`asil_inheritance_decomposition`、`verification_method`、`requirement_completeness`、`requirement_sufficiency`。
- 缺证据 → `NEEDS_USER_CONFIRMATION`。

### Phase C · 章节任务

- `TASK-xxx` + `outline_final.md`、`section_tasks.json`、`writing_plan.md`。

## TSC 方法论（本步定位）

本步对应 **阶段 3–6 的证据与任务环**：FSR→TSR 派生证据、机制/故障处理证据、追溯矩阵与验证计划。

### 阶段 6 · 追溯矩阵与验证计划（本步 Phase B/C 落实）

1. 完成 **SG–FSR–TSR–机制–架构元素** 双向追溯（TASK-TRACE）。
2. 为每条 TSR 指定验证方法（评审/分析/测试）**候选**；**不在 TSC 中宣称「已充分验证」**。
3. 汇总 open items 与待确认项（TASK-OPEN）。

### 阶段 4a–4c · 证据映射 → 引用计划 → 章节任务（本步三 Phase）

- TSR 措辞、FSR/SG 链接、架构分配、机制概念、故障处理、ASIL、验证方法 → 文档 + L1/L2/L3 + 摘录。
- 有来源 → `EVD-xxx`；无来源 → `unresolved_questions.md`。

### 阶段 4b · 引用计划

- 哪条 TSR-xx 引用哪份 FSR source 哪段、哪条 SG、哪个架构元素。
- FSR source **仅**支撑其显式 FSR-xx，不 blanket 批准全部 TSR。
- HARA 摘要 **仅**支撑其显式 FTTI/安全状态。

### 阶段 4c · 章节任务

| writing_mode | 含义 |
|---|---|
| supported | 证据充分 |
| conservative_candidate | 保守候选 |
| confirmation_required | 须 HITL |
| placeholder_only | 仅占位 |

### Critical Claims（须 T0/T1 或 open）

- 技术安全需求表述（TSR wording）
- FSR 链接
- Safety Goal 链接
- 架构分配
- 安全机制概念
- 故障处理策略
- 安全状态/降级链接
- 接口安全需求
- ASIL 继承/分解
- 验证方法
- 需求完整性/充分性
- TSC 最终批准/合规结论

### 证据 tier

| Tier | 用途 | critical claim |
|---|---|---|
| T0 | HITL | 允许 |
| T1 | FSR、SG、HARA 摘要、架构、Item 定义等 | 允许 |
| T2 | template/checklist | 仅结构 |
| T3 | reference | 不单独证明项目事实 |
| T4 | sample | **禁止** |
| T5 | 推断 | **禁止** |

## TASK 映射示例

| TASK | L2 | writing_mode |
|---|---|---|
| TASK-ARCH | 架构概述 | conservative_candidate |
| TASK-SG | SG 追溯 | conservative_candidate |
| TASK-FSR | FSR 上游追溯 | conservative_candidate |
| TASK-TSR | TSR-xx 表 | conservative_candidate |
| TASK-MECH | 安全机制 | conservative_candidate |
| TASK-FAULT | 故障检测与处理 | confirmation_required |
| TASK-DEGRADE | 警告与降级 | conservative_candidate |
| TASK-IFACE | 接口安全需求 | confirmation_required |
| TASK-ASIL | ASIL 继承/分解 | conservative_candidate |
| TASK-TRACE | 追溯矩阵 | conservative_candidate |
| TASK-VERIF | 验证方法 | confirmation_required |
| TASK-OPEN | 开放项 | open_issue_list |
| TASK-DIFF | Δ-Analysis · 与参考 TSC 的差异 | **仅 With-Reference**：结构/流程差异，allowed_evidence 不含参考 TSC 需求事实 |

## 本步 Review / Checklist 要点

### Phase A · 证据映射 Checklist

- [ ] 每条 TSR/机制/FSR/SG/ASIL/验证 claim 有 EVD 或 `unresolved_questions.md`
- [ ] EVD 含 L1/L2/L3 provenance
- [ ] FSR source EVD **不超出**显式 FSR-xx
- [ ] HARA 摘要 EVD **不超出**显式 FTTI/安全状态
- [ ] T4/T5 **不支撑** critical claim

### Phase B · 引用计划 Checklist

- [ ] `claim_support_matrix` 覆盖：tsr_wording、fsr_linkage、sg_linkage、architecture_allocation、safety_mechanism_concept 等
- [ ] 缺证据 → `NEEDS_USER_CONFIRMATION`

### Phase C · 章节任务 Checklist

- [ ] `section_tasks.json` 与 matrix 一致
- [ ] **With-Reference**：含 **TASK-DIFF**（Δ-Analysis 任务）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 大量 `confirmation_required` 属正常 | matrix 中**不得**出现「参考 TSC 支撑 TSR-xx」 |
| 每条 TSR TASK 须有 FSR/SG 链接或 open | Δ task 的 `allowed_evidence` **不含**参考 TSC 需求事实 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 编造 citation | sample 进 matrix |

### 常见 P0

| 错误 | 后果 |
|---|---|
| sample/参考 TSC 支撑 TSR/机制/ASIL | 事实来源违规 |
| 编造 FSR/SG 链接 / citation | 不可追溯 |
| FSR source blanket 支撑全部 TSR | 批准边界错误 |

## A1 / A2 / B

**A1**：七类 artifact 齐全；EVD↔matrix↔TASK 一致。  
**A2**：失败 phase 重跑。  
**B**：每条 TSR TASK 有 FSR/SG 链接或 open。
