# TSC 子 skill · Step 5 · 大纲分析与写作计划

骨架：`skills/workflow-steps/step-research-questions/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 遍历 `outline_l2.md` 每 L2，登记 `research_state.subtasks`（`sp-*`）。
- 产出 `section_writing_plans.json`：**不写正文**；不写 HSC/SSC；不做新 HARA。

## TSC 方法论（本步定位）

本步对应 **阶段 3–5 的规划环**：FSR→TSR 派生、安全机制与故障处理、接口与 ASIL 分解的 **写作计划**（不写正文）。

### 阶段 3 · FSR→TSR 派生（本步规划，Step 7 成稿）

对每条 FSR 在计划中登记结构化派生步骤：

| 步骤 | 规划内容 |
|---|---|
| 1 理解 FSR 意图 | 对应哪个 SG？约束行为/状态/接口？ |
| 2 识别技术实现触点 | 哪个传感器/执行器/算法/通信？ |
| 3 规划 TSR 表述 | 功能要求 → 可分配到架构的技术要求 |
| 4 检查可验证性 | 分析/测试/评审是否可验证？ |
| 5 记录追溯 | FSR-xx → TSR-yy；无法派生 → gap |

**常见派生模式（写入 sp-tsr 备注）**：

| FSR 类型 | TSR / 机制规划方向 |
|---|---|
| 「应检测 X 失效」 | TSR「应在 ≤t ms 内检测…」+ SEC-MECH |
| 「应进入安全状态」 | TSR「关断路径/降级条件」+ 安全状态表 |
| 「应通知驾驶员」 | TSR「HMI 警告触发条件与优先级」+ SEC-DEGRADE |

### 阶段 4 · 安全机制与故障处理（本步规划）

**按危害场景 / SG 组织**（而非仅按 ECU），每条机制计划须回答：

1. 可能发生什么故障？
2. 故障如何被检测？（冗余、监控、Plausibility、CRC、看门狗等）
3. 检测后系统处于什么状态？
4. 是否在 FTTI 内？
5. 驾驶员是否被正确警告？

输出规划：**安全机制表** + **故障处理流程/状态迁移**（Step 7 成稿）。

### 阶段 5 · 接口与 ASIL 分解（本步规划）

- 跨模块安全依赖 → 接口 TSR（超时、无效值、E2E 保护等级等）
- ASIL 分解：分解约束（独立性、免干扰等）须与 TSR ASIL 一致；无 source/HITL → `confirmation_required`

### 阶段 3 · 写作计划（本步执行）

对每一 L2：

1. 明确需哪些 **T0/T1 证据**（哪条 FSR、哪条 SG、哪段架构、哪段 FTTI source）。
2. 每条候选 TSR 规划：**链到哪个 FSR/SG、分配到哪个架构元素、机制如何落点、ASIL 从哪来**。
3. L1→L2→L3 阅读来源，记录已有/缺失。
4. 缺证据标 open，不标 `supported`。

### 成功标准（本步须预判）

- 每条 TSR 计划含 FSR/SG 链接与架构分配规划。
- 机制段计划链到 TSR 或 SG，有架构落点或 open。
- FTTI/故障处理段有 HARA 摘要来源或 `confirmation_required`。
- 验证方法段计划标 `confirmation_required`（若无 source）。
- 全文计划 **无 HSC/SSC**、**无批准结论**意图。

### 默认子任务

| id | L2 | required_evidence |
|---|---|---|
| sp-arch | SEC-ARCH | architecture_source、item_definition_source |
| sp-sg | SEC-SG | safety_goals_source、hara_summary（显式追溯） |
| sp-fsr | SEC-FSR | fsr_source |
| sp-tsr | SEC-TSR | fsr_source + SG + 架构分配依据 |
| sp-mech | SEC-MECH | TSR 计划 + 架构 source |
| sp-fault | SEC-FAULT | hara_summary（FTTI）、机制计划 |
| sp-degrade | SEC-DEGRADE | SG safe state、FSR/HARA 摘要 |
| sp-iface | SEC-IFACE | 架构/接口 source |
| sp-asil | SEC-ASIL | SG/FSR ASIL、分解依据 |
| sp-trace | SEC-TRACE | TSR/机制/FSR/SG 计划 |
| sp-verif | SEC-VERIF | 验证线索或 confirmation_required |
| sp-limit | SEC-LIMIT | 约束、open 框架 |
| sp-review | SEC-REVIEW | checklist 覆盖度 |
| sp-diff | SEC-DIFF · Δ-Analysis | **仅 With-Reference**：结构/流程差异，非参考 TSC 事实 |

### writing_mode_hint

| 模式 | 适用 |
|---|---|
| supported | T0/T1 充分 |
| conservative_candidate | 有部分证据 |
| confirmation_required | 机制/时间约束/验证/完整性缺确认 |
| placeholder_only | 仅占位 |

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 每 L2 有 `section_writing_plans.json` 条目或 gap
- [ ] `required_evidence` **不引用** T4 sample
- [ ] 每条 TSR 计划含：链哪个 FSR/SG、分配到哪、机制落点、ASIL 从哪来
- [ ] 机制/故障段缺 source 时标 `confirmation_required`
- [ ] 计划无 HSC/SSC、无「已批准」意图
- [ ] **With-Reference**：增 **sp-DIFF**（Δ-Analysis 写作计划）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 无证据段不得标 `supported` | 不得把参考 TSC 列为 `required_evidence` |
| TSR/机制段须有 source_hints 或 gaps | Δ 计划只写结构/流程差异，不写参考 TSC 需求事实 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 无证据标 supported | 参考 TSC 作 required_evidence |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 计划引用 sample 作 required_evidence | 事实来源违规 |
| 无证据 TSR 段标 supported | 后续静默填值 |

## A1 / A2 / B

**A1**：research_state 全 done；每 L2 有计划。  
**A2**：重做失败 `sp-*`。  
**B**：计划覆盖 SEC-TSR/MECH/FAULT/TRACE。
