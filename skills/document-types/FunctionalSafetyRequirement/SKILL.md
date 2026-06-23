---
name: functional-safety-requirement-document-type
description: 中文优先指导 Functional Safety Requirement（FSR，功能安全需求）文档写作；保留 Safety Goal、ASIL、追溯、tier、HITL、TSC-deferred 与 candidate-update 约束。
---

# Functional Safety Requirement Document Type Skill

Use this skill for `task_type: FunctionalSafetyRequirement`.

## 中文交互默认规则

默认用中文解释 FSR workflow、Safety Goal 追溯、ASIL 继承、验证方法与 open confirmations。保留 FSR、Functional Safety Requirements、Safety Goal、ASIL、safe state、TSC deferred、HITL、NEEDS_USER_CONFIRMATION 等术语。

英文材料可保留原文需求语句；说明优先中文。不得把 candidate 措辞写成 FSR 已批准、合规认证或 TSC 输出。

## Document Type Purpose

Functional Safety Requirement（FSR，功能安全需求）支撑 **ISO 26262-3:2018 概念阶段功能安全概念（FSC，Clause 7）** 中与功能安全需求相关的可追溯、可审查交付物。在已确认的 **Safety Goal** 之下，组织：

- Item 定义上下文摘要
- Safety Goal 追溯（含 HARA 摘要提供的追溯）
- 功能安全需求表（FSR-xx）
- ASIL 继承与理由
- 验证方法候选
- 假设、限制与开放确认

本类型**不**产出 TSC、技术安全需求、技术安全机制终稿；**不**做新 HARA 判断；**不**批准需求集或合规结论。

## 总过程概览

经 **13 个** workflow step skill 驱动（逻辑 Step 1–6、9–15；Step 6 含证据·引用·章节计划三阶段）。每步子 skill：`skills/document-types/FunctionalSafetyRequirement/steps/step-*.md`，内含 **FSR 方法论、Review/Checklist 要点**（ISO 26262-3 Clause 7 / FSC 对齐）。

**一句话**：在已确认 SG 之下，用有来源、可追溯、有 open 项的方式整理 FSR 候选包；不做 TSC，不做批准或合规认证。

## Supported Level And Positioning

`FunctionalSafetyRequirement` 为 **document-type skill 层**交付类型；通过 `task.yaml` 的 `task_type: FunctionalSafetyRequirement` 加载本子 skill 与各 step 子 skill。须遵守通用 `writing-core` 与 artifact 契约。

与既有 `task_type: fsr` 共享同一文档语义；本目录为 PascalCase 技能路径与逐步子 skill 实现。TSC 是**独立下游文档类型**（`task_type: TechnicalSafetyConcept`）：本 FSR workflow **不**产出 TSC 内容，止于功能层需求。

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| Item 定义 / 范围说明 | source | Item 上下文摘要 |
| Safety Goals 确认清单 | source | SG ID、表述、ASIL、安全状态 |
| HARA 摘要 / SG 追溯摘录 | source | **仅**摘要中显式 HE→SG 追溯 |
| 项目约束 / 假设 | source | 限制与依赖 |
| FSR 模板 | template | L1/L2 结构 |
| FSR 检查清单 | checklist | 完备性检查 |
| 功能安全需求写法参考 | reference | 方法学（T3） |
| 样例 FSR | sample | **仅**章节与表格形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | |
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-ITEM | Item 定义摘要 | ★ |
| SEC-SG | Safety Goal 追溯 | ★ |
| SEC-FSR | 功能安全需求表 FSR-xx | ★ |
| SEC-ASIL | ASIL 继承与理由 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-LIMIT | 假设、限制与开放确认 | ★ |
| SEC-OPEN | 开放问题与待确认项 | |
| SEC-REVIEW | 审查总结与状态声明 | ★ |
| SEC-DIFF | 与参考 FSR 的差异（Δ-Analysis） | With-Reference 建议 |

## Critical Claims

FSR critical claim 包括：

- functional safety requirement wording（FSR 表述）
- safety goal linkage（SG 链接）
- ASIL inheritance（ASIL 继承）
- safe state linkage（安全状态链接）
- verification method（验证方法）
- requirement completeness / sufficiency（完整性/充分性）
- final FSR approval / compliance conclusion

须 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION`。HARA 摘要仅支撑其**显式包含**的追溯，不得 blanket 批准全部 FSR。

## Forbidden Final Claims

无充分 T0/T1 与 HITL 时禁止：

- FSR set is approved / 功能安全需求已批准
- requirements are complete and compliant / 需求完整且合规
- safety goals are fully satisfied
- ASIL inheritance is validated
- verification method is sufficient
- ready for production release / 可量产
- risk is accepted / compliance is confirmed
- 将 sample FSR 中的需求/SG/ASIL 照搬为本项目事实

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（SG、HARA 摘要、Item 定义等）
- T2：template / checklist
- T3：reference（写法方法，不单独证明本项目事实）
- T4：sample（仅形状/风格）
- T5：推断，不支撑 critical claim

**sample 绝不是 fact source**。HARA 摘要**不是**新 HARA 或全面批准记录。

## Review / Verification Focus

- Safety Goal 追溯完备性
- 每条 FSR 链到 SG（source 或 open）
- ASIL 来自 source/HITL，非 sample
- 验证方法未越权标为已充分
- **无 TSC 泄漏**
- sample / reference 未当事实
- `NEEDS_USER_CONFIRMATION` 保留

## Final Report Boundary

`final_report.md` 为 review-ready 包，非专业批准，非 formal sign-off，非 TSC 交付。

## 贯穿全程的核心原则

1. **FSR ≠ TSC**：不写技术安全概念、技术安全机制终稿。
2. **FSR ≠ 新 HARA**：不把 HARA 摘要当危害分析结论或 blanket 批准。
3. **事实来源分离**：sample 只借结构；每条 FSR 须链到**本项目 source** 中的 SG。
4. **缺口显式**：缺材料标 open，不静默填需求或 ASIL。
5. **保守措辞**：需求措辞、验证充分性缺确认时保留 `NEEDS_USER_CONFIRMATION`。
6. **交付边界**：`ready_for_human_review` / `finalized_with_open_items`，**非** approved。

## 两种情景（From-Scratch / With-Reference）

与 IDD/HARA 惯例一致；各 step 子 skill 含 **情景差异** 与分步 Checklist。

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断填 FSR/ASIL | 把参考 FSR 的 FSR/SG/ASIL 当本项目事实 |
| sample 角色 | 仅表头/章节形状 | 同上；参考 FSR 必须 `role=sample` |
| 参考 FSR | 通常无或仅 template | 单独登记 sample；本项目 SG/Item 须独立 source |
| 额外章节 | 无 | 建议 **SEC-DIFF / Δ-Analysis**（`sp-DIFF`、`TASK-DIFF`） |
| 写作模式 | 大量 confirmation_required / placeholder | 更多 conservative_candidate，仍须逐条 EVD |

### 按步快速对照（重点防什么）

| Step | From-Scratch | With-Reference |
|---|---|---|
| 1 输入 | 无 SG 仍开跑 | 参考 FSR 标成 source |
| 2 清单 | 静默跳过解析失败 | 参考需求进 inventory 事实字段 |
| 3 索引 | SG 无索引无 gap | 参考 FSR 进 topic_index |
| 4 大纲 | 无材料却标 complete | 参考内容进大纲正文 |
| 5 计划 | 无证据标 supported | 参考 FSR 作 required_evidence |
| 6 证据 | 编造 citation | sample 进 matrix |
| 9 草稿 | 静默填 FSR/ASIL | 参考措辞无 EVD 进表 |
| 10 审查 | open 被掩盖 | 缺 Δ-Analysis；参考当事实 |
| 11 验证 | 静默填值 | T4 支撑 critical claim |
| 12 修订 | 无证据关 P0 | 用参考关 P0 |
| 13 交付 | 越权批准措辞 | 交付未声明参考边界 |

**一句话**：From-Scratch 查输入够不够、gap 是否诚实；With-Reference 查参考 FSR 是否被当事实，并全程保留 Δ-Analysis 与 TASK-DIFF。
