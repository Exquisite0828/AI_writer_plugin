# FSR 子 skill · Step 10 · 审查

骨架：`skills/workflow-steps/step-review/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 对照 template、checklist、证据审查 `draft/full_draft.md`。
- 产出 `review/*`。
- 审查结论为 **review-ready 评估**，**不等于**合规认证或 FSR 正式批准。

## FSR 方法论（本步定位）

本步对应 **阶段 6：审查与验证** 中的 **内容审查**（同行/系统工程师视角）。

### 阶段 6 · 内容审查（本步执行）

1. 每条 FSR 是否链到 SG？
2. ASIL 是否来自 source/HITL？
3. 验证方法是否过度断言？
4. sample/reference 是否被误当事实？
5. 是否有 **TSC 泄漏**？
6. 完整性/充分性是否被越权「批准」？

### 要回答的问题（审查核对）

| 问题 | 通过条件 |
|---|---|
| 每条 FSR 是什么？ | 表述清晰，有来源或 open |
| 追溯到哪个 SG？ | Linked SG 有效 |
| ASIL 如何继承？ | 来自 SG source 或 HITL |
| 如何验证？ | 候选或已确认，非静默充分 |
| 还缺什么？ | open 完整 |

## 本步 Review / Checklist 要点

### Clause 7 / FSR 内容 Checklist（报告正文必查）

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档目的与范围 | 声明非 TSC、非批准 |
| 2 | 输入材料 role | sample/reference 未当事实 |
| 3 | Item 定义摘要 | 与 source 一致或 open |
| 4 | Safety Goal 追溯 | 每条 SG 可见或 open |
| 5 | FSR 唯一 ID | 每条 FSR 有 ID |
| 6 | FSR→SG 追溯 | 每条 FSR 链到 ≥1 SG 或 open |
| 7 | ASIL | 来自 SG source/HITL，无 sample |
| 8 | 验证方法 | 候选或已确认，无静默「已充分」 |
| 9 | FSR 纯净性 | 无 TSC、技术机制、技术安全需求终稿 |
| 10 | 开放项 | NEEDS_USER_CONFIRMATION 完整 |
| 11 | Forbidden claims | 无批准/合规/量产措辞 |

### 内容审查维度表

| 维度 | Review 要点 |
|---|---|
| SG 追溯 | HARA 摘要未当 blanket 批准 |
| FSR 完整性 | ID、表述、Linked SG 齐全 |
| ASIL | 无 sample 支撑 |
| 验证方法 | 未越权断言充分性 |
| TSC 边界 | 无技术安全机制终稿 |
| 缺口诚实性 | open 保留 |
| 文档边界 | 非合规认证 |

### P0 失效项

| 失效 | 后果 |
|---|---|
| sample 支撑 FSR/SG/ASIL | 事实来源违规 |
| FSR 无 SG 链接且标已确认 | 不可追溯 |
| 含 TSC 章节 | 文档类型漂移 |
| 写「FSR 已批准」「已合规」 | 越权结论 |
| HARA 摘要当全面批准 | 批准边界错误 |
| reference 证明本项目 SG/ASIL | tier 违规 |

### P1 失效项

- ASIL 继承无 rationale
- 验证方法无 status 列

### 一句话归纳

**Checklist 核心**：每条 FSR 链 SG、ASIL 有来源、验证方法显式、无 TSC、无批准措辞。  
**Review 核心**：追溯一致、tier 合规、sample 未当事实、缺口显式、结论不越权批准。

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 审查重点 | gap 是否诚实 | 参考 FSR 是否渗入事实 |
| open 项 | 多可接受 | 须说明哪些沿用参考、哪些来自本项目 source |
| Δ-Analysis | — | 缺 Δ-Analysis 节 → **建议 P0**（对齐 HARA 惯例） |
| 完整性 | 不得越权「批准」 | Δ 节不得把参考当本项目结论 |

| From-Scratch 重点防 | With-Reference 重点防 |
|---|---|
| open 被掩盖 | 缺 Δ-Analysis；参考当事实 |

## A1 / A2 / B

**A1**：checklist 项有结论；P0 无遗漏。  
**A2**：按 findings 交 Step 12。  
**B**：review 非合规批准。
