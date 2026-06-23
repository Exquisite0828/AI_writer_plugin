# TSC 子 skill · Step 10 · 审查

骨架：`skills/workflow-steps/step-review/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 对照 template、checklist、证据审查 `draft/full_draft.md`。
- 产出 `review/*`。
- 审查结论为 **review-ready 评估**，**不等于**合规认证或 TSC 正式批准。

## TSC 方法论（本步定位）

本步对应 **阶段 7：评审与独立审查** 中的 **内容审查**（系统/安全工程师视角）。

### 三类评审（阶段 7）

| 评审类型 | 关注点 | 本步对应检查 |
|---|---|---|
| **完整性评审** | 每条 FSR 是否有 TSR？每条 SG 是否有机制覆盖？ | Checklist #6–9、追溯矩阵 |
| **一致性评审** | TSC 与 FSC、架构、HARA（FTTI/安全状态）是否矛盾？ | #3、#5、#10、架构与分配一致 |
| **独立性评审** | 机制是否过度依赖同一失效源？ASIL 分解是否合理？ | 机制表、SEC-ASIL |

### 阶段 7 常用检查项（须全部核对）

- [ ] 无样例/参考材料被当作项目事实
- [ ] 每条 TSR 可追溯到 FSR/SG
- [ ] 安全状态定义与 HARA 一致或有记录差异
- [ ] FTTI 链路可解释（检测 + 处理 ≤ FTTI）
- [ ] 未写「TSC 已批准 / 已合规 / 可量产」等越权结论
- [ ] 开放项未静默闭合

### 阶段 6 · 内容审查（本步执行）

1. 每条 TSR 是否链到 FSR 与 SG？
2. 架构分配与机制落点是否一致？
3. ASIL 是否来自 source/HITL？
4. FTTI/故障处理是否过度断言？
5. 验证方法是否过度断言？
6. sample/reference 是否被误当事实？
7. 是否有 **HSC/SSC 泄漏**？
8. TSC 是否仅为 FSR 复述？
9. 完整性/充分性是否被越权「批准」？

### 要回答的问题（审查核对）

| 问题 | 通过条件 |
|---|---|
| 每条 TSR 是什么？ | 技术层表述清晰，有来源或 open |
| 追溯到哪个 FSR/SG？ | Linked FSR/SG 有效 |
| 分配到哪？ | Architecture allocation 有效或 open |
| 机制如何支撑？ | 链 TSR/SG，落点一致或 open |
| FTTI 是否可解释？ | 有 HARA 来源或 open |
| ASIL 如何继承/分解？ | 来自 source 或 HITL |
| 如何验证？ | 候选或已确认，非静默充分 |
| 还缺什么？ | open 完整 |

## 本步 Review / Checklist 要点

### Clause 8 / TSC 内容 Checklist（报告正文必查）

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档目的与范围 | 声明非 HSC/SSC、非批准 |
| 2 | 输入材料 role | sample/reference 未当事实 |
| 3 | 系统架构概述 | 与 architecture source 一致或 open |
| 4 | Safety Goal 追溯 | 每条 SG 可见或 open |
| 5 | FSR 上游追溯 | 与 fsr_source 一致，未改写事实 |
| 6 | TSR 唯一 ID | 每条 TSR 有 ID |
| 7 | TSR→FSR/SG 追溯 | 每条 TSR 链到 FSR 与 SG 或 open |
| 8 | 架构分配 | 每条 TSR 有 allocation 或 open |
| 9 | 安全机制 | 机制链 TSR/SG，落点可解释 |
| 10 | 故障处理/FTTI | 有来源或 open，无静默「已满足」 |
| 11 | ASIL | 来自 source/HITL，无 sample |
| 12 | 验证方法 | 候选或已确认，无静默「已充分」 |
| 13 | TSC 纯净性 | 无 HSC/SSC、详细实现终稿 |
| 14 | 非 FSR 复述 | TSR 体现技术分配/机制，非换措辞 |
| 15 | 开放项 | NEEDS_USER_CONFIRMATION 完整 |
| 16 | Forbidden claims | 无批准/合规/量产措辞 |

### 内容审查维度表

| 维度 | Review 要点 |
|---|---|
| FSR/SG 追溯 | FSR source 未当 blanket 批准 |
| TSR 完整性 | ID、表述、Linked FSR/SG、Allocation 齐全 |
| 机制一致性 | 机制落点与架构/TSR 一致 |
| ASIL | 无 sample 支撑 |
| FTTI | 未越权断言满足 |
| 验证方法 | 未越权断言充分性 |
| HSC/SSC 边界 | 无软硬件安全概念终稿 |
| 缺口诚实性 | open 保留 |
| 文档边界 | 非合规认证 |

### 常见失效模式（审查必查）

| 失效 | 级别 |
|---|---|
| 把 FSR 原句复制为 TSR | P0 |
| 只有需求表，没有机制与故障处理 | P0 |
| 架构图与分配表不一致 | P0 |
| 安全状态与 HARA 不一致且无说明 | P1 |
| 用参考项目机制填本项目 | P0 |
| 在 TSC 中做合规/sign-off 结论 | P0 |
| 忽略 ASIL 分解约束 | P1 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| sample 支撑 TSR/机制/ASIL | 事实来源违规 |
| TSR 无 FSR 链接且标已确认 | 不可追溯 |
| 含 HSC/SSC 章节 | 文档类型漂移 |
| 写「TSC 已批准」「已合规」 | 越权结论 |
| FSR source 当全面批准 | 批准边界错误 |
| reference 证明本项目 TSR/机制 | tier 违规 |
| TSR 仅为 FSR 复述无技术内容 | Clause 8 精神不满足 |

### P1 失效项

- ASIL 继承/分解无 rationale
- 追溯矩阵缺架构或机制列
- 验证方法无 status 列

### 一句话归纳

**Checklist 核心**：每条 TSR 链 FSR/SG、有架构分配、机制一致、FTTI 有来源、无 HSC/SSC、无批准措辞。  
**Review 核心**：追溯一致、tier 合规、sample 未当事实、缺口显式、结论不越权批准。

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 审查重点 | gap 是否诚实 | 参考 TSC 是否渗入事实 |
| open 项 | 多可接受 | 须说明哪些沿用参考、哪些来自本项目 source |
| Δ-Analysis | — | 缺 Δ-Analysis 节 → **建议 P0** |
| 完整性 | 不得越权「批准」 | Δ 节不得把参考当本项目结论 |

## A1 / A2 / B

**A1**：checklist 项有结论；P0 无遗漏。  
**A2**：按 findings 交 Step 12。  
**B**：review 非合规批准。
