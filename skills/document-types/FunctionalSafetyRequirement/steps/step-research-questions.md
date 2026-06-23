# FSR 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 遍历 `outline_l2.md` 每 L2，登记 `research_state.subtasks`（`sp-*`）。
- 产出 `section_writing_plans.json`：**不写正文**；不写 TSC；不做新 HARA。

## FSR 方法论（本步定位）

本步对应 **阶段 3：逐段分析与写作计划**。

### 阶段 3 · 写作计划（本步执行）

对每一 L2：

1. 明确需哪些 **T0/T1 证据**（哪条 SG、哪段 source）。
2. 每条候选 FSR 规划：**链到哪个 SG、ASIL 从哪来、验证方法是否充分**。
3. L1→L2→L3 阅读来源，记录已有/缺失。
4. 缺证据标 open，不标 `supported`。

### 成功标准（本步须预判，对齐 §2.2）

- 每条 FSR 计划含 SG 链接与 ASIL 来源规划。
- 验证方法段计划标 `confirmation_required`（若无 source）。
- 全文计划 **无 TSC**、**无批准结论**意图。

### 默认子任务

| id | L2 | required_evidence |
|---|---|---|
| sp-item | SEC-ITEM | item_definition_source |
| sp-sg | SEC-SG | safety_goals_source、hara_summary（显式追溯） |
| sp-fsr | SEC-FSR | SG source + 分解依据 |
| sp-asil | SEC-ASIL | SG ASIL、继承规则 |
| sp-verif | SEC-VERIF | 验证线索或 confirmation_required |
| sp-limit | SEC-LIMIT | 约束、open 框架 |
| sp-review | SEC-REVIEW | checklist 覆盖度 |
| sp-diff | SEC-DIFF · Δ-Analysis | **仅 With-Reference**：结构/流程差异，非参考 FSR 事实 |

### writing_mode_hint

| 模式 | 适用 |
|---|---|
| supported | T0/T1 充分 |
| conservative_candidate | 有部分证据 |
| confirmation_required | 措辞/验证/完整性缺确认 |
| placeholder_only | 仅占位 |

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 每 L2 有 `section_writing_plans.json` 条目或 gap
- [ ] `required_evidence` **不引用** T4 sample
- [ ] 每条 FSR 计划含：链哪个 SG、ASIL 从哪来、验证是否充分
- [ ] 验证/完整性段缺 source 时标 `confirmation_required`
- [ ] 计划无 TSC、无「已批准」意图
- [ ] **With-Reference**：增 **sp-DIFF**（Δ-Analysis 写作计划）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 无证据段不得标 `supported` | 不得把参考 FSR 列为 `required_evidence` |
| SG/FSR 段须有 source_hints 或 gaps | Δ 计划只写结构/流程差异，不写参考 FSR 需求事实 |
| 写作模式多为 confirmation_required / placeholder | 可更多 conservative_candidate，但仍须逐条 EVD |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 无证据标 supported | 参考 FSR 作 required_evidence |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 计划引用 sample 作 required_evidence | 事实来源违规 |
| 无证据 FSR 段标 supported | 后续静默填值 |

## A1 / A2 / B

**A1**：research_state 全 done；每 L2 有计划。  
**A2**：重做失败 `sp-*`。  
**B**：计划覆盖 SEC-SG/FSR/ASIL/VERIF。
