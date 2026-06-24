# SyRS 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 遍历 `outline_l2.md` 每 L2，登记 `research_state.subtasks`（`sp-*`）。
- 产出 `section_writing_plans.json`：**不写正文**；不写 HARA/FSR/TSC/SwRS；不做 ASPICE 合规结论。

## SyRS 方法论（本步定位）

本步对应 **阶段 3：逐段分析与写作计划**。

### 阶段 3 · 写作计划（本步执行）

对每一 L2：

1. 明确需哪些 **T0/T1 证据**（哪份 SWRS/接口规范哪段）。
2. 每条候选 SYS-xx 规划：**链到哪个上游 ID、验证方法是否充分、接口方向是否有来源**。
3. L1→L2→L3 阅读来源，记录已有/缺失。
4. 缺证据标 open，不标 `supported`。

### 成功标准（本步须预判）

- 每条 SYS-F/IF 计划含上游追溯与验证方法规划。
- 接口段计划强制检查 **Direction** 与 **Counterpart** 证据。
- 全文计划 **无 HARA/TSR/TSC**、**无 ASPICE 批准**意图。

### 默认子任务

| id | L2 | required_evidence |
|---|---|---|
| sp-ident | SEC-IDENT | 项目 charter、SWRS 封面 |
| sp-stake | SEC-STAKE | swrs_source、rfq |
| sp-func | SEC-FUNC | SWRS 功能描述 |
| sp-if | SEC-IF | interface_spec（含方向） |
| sp-perf | SEC-PERF | SWRS/技术规范性能段 |
| sp-env | SEC-ENV | ODD、电气/安装规范 |
| sp-diag | SEC-DIAG | diagnostic_spec |
| sp-safe | SEC-SAFE | fsr_source（若有）；无则 gap |
| sp-trace | SEC-TRACE | SWRS ID 映射 |
| sp-verif | SEC-VERIF | 验证线索或 confirmation_required |
| sp-assump | SEC-ASSUMP | 约束、open 框架 |
| sp-review | SEC-REVIEW | checklist 覆盖度 |
| sp-diff | SEC-DIFF · Δ-Analysis | **仅 With-Reference**：结构/流程差异，非参考 SyRS 事实 |

### writing_mode_hint

| 模式 | 适用 |
|---|---|
| supported | T0/T1 充分 |
| conservative_candidate | 有部分证据 |
| confirmation_required | 措辞/限值/验证缺确认 |
| placeholder_only | 仅占位 |

## 本步 Review / Checklist 要点

### 通用 Checklist（每次 run 必查）

- [ ] 每个 L2 有 `section_writing_plans.json` 条目，或在 `knowledge_gaps` 显式 gap
- [ ] 每条 plan 有：`section_id`、`subtasks[sp-*]`、`required_evidence`、`writing_mode_hint`、`status`
- [ ] `required_evidence` **不引用** T4 sample / T5 推断（**P0**）
- [ ] `research_state.subtasks` 全部 `done`，无 `pending` 仍标 `ready`
- [ ] 每条候选 SYS-F 计划含：**上游 ID + 验证方法 + Priority 来源**
- [ ] 每条候选 SYS-IF 计划含：**Direction + Counterpart + 失效行为**来源
- [ ] 验证 / 完整性 / 限值缺 source 时计划标 `confirmation_required` 或 `placeholder_only`
- [ ] 计划**不**含 HARA / TSR / TSC / SwRS / 批准意图
- [ ] **With-Reference**：增 **sp-DIFF**，每类差异（Added/Removed/Modified/Scope-changed）至少一个子任务

### 默认子任务覆盖 Checklist（每章一条）

| section_id | sp-* | required_evidence 必含 | 缺失处理 |
|---|---|---|---|
| SEC-IDENT | sp-ident | 项目 charter / SWRS 封面 | gap |
| SEC-STAKE | sp-stake | swrs_source / rfq | gap（**P0** 若无） |
| SEC-FUNC | sp-func | SWRS 功能描述 | conf_required |
| SEC-IF | sp-if | interface_spec（含 Direction） | conf_required |
| SEC-PERF | sp-perf | 性能源 | placeholder_only 若缺 |
| SEC-ENV | sp-env | ODD / 电气规范 | placeholder_only 若缺 |
| SEC-DIAG | sp-diag | diagnostic_spec | placeholder_only 若缺 |
| SEC-SAFE | sp-safe | fsr_source / SG 清单 | gap，**仅引用** |
| SEC-LEGAL | sp-legal | 法规清单 | 不适用须显式声明 |
| SEC-TRACE | sp-trace | SWRS ID 映射 | conf_required |
| SEC-VERIF | sp-verif | 验证线索 | conf_required |
| SEC-ASSUMP | sp-assump | 平台 / 标定约束 | conf_required |
| SEC-OPEN | sp-open | 全 unresolved 汇总 | always ready |
| SEC-REVIEW | sp-review | checklist 覆盖度 | always ready |
| SEC-DIFF（仅 With-Reference） | sp-diff | 本项目 source + 参考 SyRS 章节对照 | placeholder_only 若 source 缺 |

### writing_mode_hint 决策 Checklist

| 模式 | 适用前置 |
|---|---|
| supported | 有 T0/T1 充分证据；可成稿 |
| conservative_candidate | 有部分证据；正文须保留 NEEDS_USER_CONFIRMATION 槽 |
| confirmation_required | 关键字段缺 source；正文 placeholder + HITL 提示 |
| placeholder_only | 章节几乎无 source；仅写「待补」与 open 项 |

### ASPICE / ISO 26262 维度 Checklist

- [ ] **ASPICE SYS.2 BP1**：sp-stake 计划含「**Customer Req ID → SyRS ID 候选映射**」步骤
- [ ] **ASPICE SYS.2 BP2**：sp-func / sp-if 计划须显式列出 shall 表述生成步骤与验证方法选择步骤
- [ ] **ASPICE SYS.2 BP3**：每章计划须包含「一致性 / 可行性 / 可测试性」自检子步骤
- [ ] **ASPICE SYS.2 BP5**：sp-trace 计划须含 **上游→SyRS** 与 **SyRS→上游** 双向检查
- [ ] **ISO 26262-3 §5 接口**：sp-func / sp-if / sp-env / sp-diag 摘要可作 IDD 输入草案
- [ ] **ISO 26262-3 §7 接口**：sp-safe 仅引用 FSR/SG，不做新分析

### From-Scratch 专属 Checklist

- [ ] sp-stake / sp-func / sp-if 无证据时不得标 `supported`，仅 `confirmation_required` / `placeholder_only`
- [ ] 验证方法计划默认 `confirmation_required`
- [ ] SEC-SAFE 通常 `placeholder_only` 或 `gap`，写「pending FSR 上游」

### With-Reference 专属 Checklist

- [ ] **不得**把参考 SyRS 列为任一 `required_evidence`（**P0**）
- [ ] **sp-DIFF 必须存在**，且每条差异类别都有子任务
- [ ] sp-DIFF 的 `required_evidence` 仅含**本项目** source；参考 SyRS 仅作 `style_hint`
- [ ] 不得用「同参考」一刀切；每条差异要点须明确 Added/Removed/Modified
- [ ] 平台/变型差异（接口、网络安全、诊断）逐项有 sp-* 计划

### 本步 Review 要点（双情景对比）

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 写作模式分布 | 多 confirmation_required / placeholder_only | 可更多 conservative_candidate，但仍逐条 EVD |
| required_evidence | 仅 T1 source / HITL | 参考 SyRS **绝不**列入 |
| sp-DIFF | — | 强制存在并细分 |
| 双向追溯计划 | sp-trace 双向 | 同上；并须包含「参考 ID 处理策略」 |
| Δ 任务来源 | — | 仅本项目 source 支撑 Δ 决策 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 计划引用 sample / 参考 SyRS 作 `required_evidence` | 事实来源违规（**P0**） |
| 无证据 SYS-F 段标 `supported` | 后续静默填值 |
| sp-trace 仅单向 | ASPICE SYS.2 BP5 不满足 |
| sp-DIFF 缺失或仅写「同参考」 | 变型差异未管理 |

### 常见 P1

- writing_mode_hint 与 `required_evidence` 不一致
- sp-* 子任务粒度过粗（如 SEC-FUNC 只一个 sp-func，未拆 normal/degraded）
- 验证方法计划默认 Test 而无理由

## A1 / A2 / B

**A1**：research_state 全 done；每 L2 有计划；sp-DIFF（若 With-Reference）齐全。  
**A2**：重做失败 `sp-*`、修正 writing_mode_hint、补 BP3 一致性子步骤。  
**B**：计划覆盖 SEC-STAKE/FUNC/IF/TRACE/VERIF，且与 evidence_map 输入一致。
