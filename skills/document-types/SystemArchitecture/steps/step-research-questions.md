# System Architecture 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 遍历 `outline_l2.md` 每 L2，登记 `research_state.subtasks`（`sp-*`）。
- 产出 `section_writing_plans.json`：**不写正文**；不写 HARA/FSR/TSC/SwRS；不做 ASPICE 合规结论。

## System Architecture 方法论（本步定位）

本步对应 **阶段 3：逐段分析与写作计划**。

### 阶段 3 · 写作计划（本步执行）

对每一 L2：

1. 明确需哪些 **T0/T1 证据**（哪份 SyRS/接口规范/平台约束哪段）。
2. 每条候选架构元素 / 接口 / 分配规划：**链到哪个上游 requirement、接口方向是否有来源、分配理由是否有证据**。
3. L1→L2→L3 阅读来源，记录已有/缺失。
4. 缺证据标 open，不标 `supported`。

### 默认子任务

| id | L2 | required_evidence |
|---|---|---|
| sp-context | SEC-CONTEXT | system_context |
| sp-reqtrace | SEC-REQTRACE | syrs_source |
| sp-larch | SEC-LARCH | architecture_source / syrs_source |
| sp-parch | SEC-PARCH | architecture_source / platform_constraints |
| sp-elem | SEC-ELEM | architecture_source |
| sp-if | SEC-IF | interface_spec |
| sp-alloc | SEC-ALLOC | syrs_source + architecture_source |
| sp-diag | SEC-DIAG | diagnostic_constraints |
| sp-safe-arch | SEC-SAFE-ARCH | fsr_or_tsc_excerpt |
| sp-res | SEC-RES | platform_constraints |
| sp-verif | SEC-VERIF | verification hints or confirmation_required |
| sp-assump | SEC-ASSUMP | constraints / assumptions |
| sp-review | SEC-REVIEW | checklist coverage |
| sp-diff | SEC-DIFF · Δ-Analysis | **仅 With-Reference**：结构/流程差异，非参考架构事实 |

### writing_mode_hint

| 模式 | 适用 |
|---|---|
| supported | T0/T1 充分 |
| conservative_candidate | 有部分证据 |
| confirmation_required | 分配/方向/资源关键字段缺确认 |
| placeholder_only | 仅占位 |

## 本步 Review / Checklist 要点

### 通用 Checklist

- [ ] 每个 L2 有 `section_writing_plans.json` 条目，或在 `knowledge_gaps` 显式 gap
- [ ] 每条 plan 有 `section_id`、`subtasks[sp-*]`、`required_evidence`、`writing_mode_hint`
- [ ] `required_evidence` **不引用** T4 sample / T5 推断
- [ ] 每条元素/接口/分配计划含：上游 requirement、接口方向或分配理由来源
- [ ] 分配/方向/资源缺 source 时计划标 `confirmation_required` 或 `placeholder_only`
- [ ] 计划**不**含 HARA / TSR / TSC / SwRS / 批准意图
- [ ] **With-Reference**：增 **sp-DIFF**

### ASPICE / ISO 维度 Checklist

- [ ] **ASPICE SYS.3**：sp-alloc 计划含 requirement → element 分配步骤
- [ ] **ASPICE SYS.3**：sp-if 计划含接口边界、方向、对端、协议检查步骤
- [ ] **ASPICE SYS.3**：sp-larch / sp-parch 计划含逻辑-物理一致性检查
- [ ] **ISO 26262 接口**：sp-safe-arch 仅引用 FSR/TSC 约束，不做新分析

### From-Scratch 专属 Checklist

- [ ] 无证据段不得标 `supported`
- [ ] sp-alloc / sp-if 多为 `confirmation_required` 属正常

### With-Reference 专属 Checklist

- [ ] 不得把参考架构文档列为任一 `required_evidence`
- [ ] **sp-DIFF 必须存在**，每类差异（Added/Removed/Modified/Scope-changed）至少一个子任务

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| writing_mode 分布 | 多 confirmation / placeholder | 可更多 conservative_candidate，但仍逐条 EVD |
| required_evidence | 仅 T1 source / HITL | 参考架构绝不列入 |
| sp-DIFF | — | 强制存在并细分 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 计划引用 sample / 参考架构作 `required_evidence` | 事实来源违规 |
| 无证据分配段标 `supported` | 后续静默填值 |
| sp-DIFF 缺失或仅写“同参考” | 变型差异未管理 |

## A1 / A2 / B

**A1**：research_state 全 done；每 L2 有计划；sp-DIFF（若 With-Reference）齐全。  
**A2**：重做失败 `sp-*`、修正 writing_mode_hint。  
**B**：计划覆盖 SEC-REQTRACE / LARCH / IF / ALLOC / VERIF，且与 evidence_map 输入一致。
