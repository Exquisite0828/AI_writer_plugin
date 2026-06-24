# System Architecture 子 skill · Step 6 · 证据·引用·章节计划

骨架：`skills/workflow-steps/step-evidence-map/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点（三阶段顺序）

### Phase A · 证据映射

- **L1→L2→L3→原文** → `EVD-xxx`；critical claim 仅 T0/T1。
- SEC-SAFE-ARCH 的 EVD **不得**超出 FSR/TSC source 显式引用范围。

### Phase B · 引用计划

- claim 类型：`architecture_wording`、`upstream_linkage`、`element_definition`、`interface_architecture`、`allocation_rationale`、`diagnostic_architecture`、`resource_constraint`、`safety_architecture_linkage`、`verification_method`、`architecture_completeness_consistency`。
- 缺证据 → `NEEDS_USER_CONFIRMATION`。

### Phase C · 章节任务

- `TASK-xxx` + `outline_final.md`、`section_tasks.json`、`writing_plan.md`。

## System Architecture 方法论（本步定位）

本步对应 **阶段 4：证据映射 → 引用计划 → 章节任务**。

### Phase A · 证据映射

- 架构元素定义、接口方向、分配关系、资源约束、诊断/降级链路 → 文档 + L1/L2/L3 + 摘录。
- 有来源 → `EVD-xxx`；无来源 → `unresolved_questions.md`。

### Phase B · 引用计划

- 哪条分配矩阵行引用哪条 SyRS 需求哪段。
- 哪条接口架构行引用哪份接口规范哪段（含方向/对端）。
- SEC-SAFE-ARCH **仅**引用 source 中显式 FSR/SG/TSC 约束，不 blanket 支撑全部架构。

### Phase C · 章节任务

| writing_mode | 含义 |
|---|---|
| supported | 证据充分 |
| conservative_candidate | 保守候选 |
| confirmation_required | 须 HITL |
| placeholder_only | 仅占位 |

## 本步 Review / Checklist 要点

### Phase A · 证据映射 Checklist

- [ ] 每条元素 / 接口 / 分配 / 资源 / 诊断架构 claim 有 `EVD-xxx` 或 `unresolved_questions.md`
- [ ] 每个 EVD 含 L1/L2/L3 provenance
- [ ] SEC-SAFE-ARCH 的 EVD **不超出**显式 FSR/TSC 引用
- [ ] T4/T5 **不支撑** critical claim

### Phase B · 引用计划 Checklist

- [ ] `claim_support_matrix` 覆盖：architecture_wording、upstream_linkage、element_definition、interface_architecture、allocation_rationale、verification_method 等
- [ ] 缺证据 → `NEEDS_USER_CONFIRMATION`
- [ ] 同一 EVD 不得 blanket 支撑无关架构 claim

### Phase C · 章节任务 Checklist

- [ ] `section_tasks.json` 与 matrix 一致
- [ ] **With-Reference**：含 **TASK-DIFF**

### TASK 映射示例

| TASK | L2 | writing_mode |
|---|---|---|
| TASK-REQTRACE | SEC-REQTRACE | conservative_candidate |
| TASK-LARCH | SEC-LARCH | conservative_candidate |
| TASK-PARCH | SEC-PARCH | conservative_candidate |
| TASK-ELEM | SEC-ELEM | conservative_candidate |
| TASK-IF | SEC-IF | conservative_candidate |
| TASK-ALLOC | SEC-ALLOC | confirmation_required |
| TASK-DIAG | SEC-DIAG | conservative_candidate |
| TASK-SAFE-ARCH | SEC-SAFE-ARCH | confirmation_required |
| TASK-RES | SEC-RES | confirmation_required |
| TASK-VERIF | SEC-VERIF | confirmation_required |
| TASK-OPEN | SEC-OPEN | open_issue_list |
| TASK-DIFF | SEC-DIFF | **仅 With-Reference**：结构/流程差异，allowed_evidence 不含参考架构事实 |

### From-Scratch 专属 Checklist

- [ ] 大量 `confirmation_required` / `placeholder_only` 属正常
- [ ] 分配矩阵每行至少链 1 个上游 EVD 或显式登记 unresolved

### With-Reference 专属 Checklist

- [ ] matrix 中**不得**出现「参考架构文档支撑元素 / 接口 / 分配」
- [ ] TASK-DIFF 的 `allowed_evidence` **不含**参考架构事实字段

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| matrix 范围 | 多 confirmation / placeholder | 多 conservative_candidate，但逐条 EVD |
| 编造风险 | 凭经验编 citation → **P0** | 把参考架构进 matrix → **P0** |
| SEC-SAFE-ARCH | placeholder 多 | 不得抄参考架构的安全约束 EVD |

### 常见 P0

| 错误 | 后果 |
|---|---|
| sample / 参考架构支撑元素/接口/分配/资源 | 事实来源违规 |
| 编造上游链接 / citation | 不可追溯 |
| SEC-SAFE-ARCH blanket 支撑全部架构 | 批准边界错误 |

## A1 / A2 / B

**A1**：evidence_map、citation_plan、claim_support_matrix、outline_final、section_tasks、writing_plan、unresolved_questions 齐全；EVD↔matrix↔TASK 一致。  
**A2**：失败 phase 重跑；修正 tier 违规。  
**B**：每条架构元素/接口/分配 TASK 有上游链接或 open；With-Reference 含 TASK-DIFF。
