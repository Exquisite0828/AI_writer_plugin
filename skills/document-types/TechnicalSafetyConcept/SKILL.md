---
name: technical-safety-concept-document-type
description: 中文优先指导 Technical Safety Concept（TSC，技术安全概念）文档写作；保留 TSR、Safety Goal、FSR 追溯、ASIL、架构分配、安全机制、FTTI、source tier、HITL、HSC/SSC-deferred 与 candidate-update 约束。
---

# Technical Safety Concept Document Type Skill

Use this skill for `task_type: TechnicalSafetyConcept`.

## 中文交互默认规则

默认用中文解释 TSC workflow、FSR/SG 追溯、TSR 派生、架构分配、安全机制、ASIL 继承/分解、验证方法与 open confirmations。保留 TSC、Technical Safety Concept、TSR、FSR、Safety Goal、ASIL、safe state、FTTI、FDTI、FHTI、HSC deferred、SSC deferred、HITL、NEEDS_USER_CONFIRMATION 等术语。

英文材料可保留原文需求语句；说明优先中文。不得把 candidate 措辞写成 TSC 已批准、合规认证或 HSC/SSC 输出。

## Document Type Purpose

Technical Safety Concept（TSC，技术安全概念）支撑 **ISO 26262-4:2018 系统层面产品开发 Clause 8（Technical Safety Concept）** 中与技术安全概念相关的可追溯、可审查交付物。在已确认的 **FSR / Safety Goal** 与 **系统架构** 之上，组织：

- Item 定义与架构上下文摘要
- Safety Goal 与 FSR 上游追溯
- 技术安全需求表（TSR-xx）
- 架构元素安全分配
- 技术安全机制概念
- 故障检测与处理策略（含 FTTI/FDTI/FHTI 概念）
- 警告与降级策略
- 接口安全需求（HW-SW / SW-SW，概要级）
- ASIL 继承与分解理由
- 追溯矩阵（SG ↔ FSR ↔ TSR ↔ 架构元素 ↔ 机制）
- 验证方法候选
- 假设、限制与开放确认

本类型**不**产出 HSC/SSC 终稿、详细软硬件实现、系统设计 sign-off；**不**做新 HARA 判断；**不**改写上游 FSR/SG 事实；**不**批准 TSC 或合规结论。

## 总过程概览

经 **13 个** workflow step skill 驱动（逻辑 Step 1–6、9–15；Step 6 含证据·引用·章节计划三阶段）。每步子 skill：`skills/document-types/TechnicalSafetyConcept/steps/step-*.md`，内含 **TSC 方法论、Review/Checklist 要点**（ISO 26262-4 Clause 8 对齐）。

**一句话**：在已确认 FSR/SG 与架构上下文之下，用可追溯方式回答——安全需求落在哪、靠什么机制检测与处理故障、如何在时间内进入安全状态、接口约束什么；产出 review-ready TSC 包，而非实现细节或合规批准书。

### 功能安全生命周期位置

```
Item 定义（Part 3, Clause 5）
    ↓
HARA（Part 3, Clause 6）→ Safety Goal（SG）
    ↓
功能安全概念 FSC（Part 3, Clause 7）→ 功能安全需求 FSR
    ↓
技术安全概念 TSC（Part 4, Clause 8）  ← 本类型
    ↓
系统设计 / HW-SW 接口 / 软硬件安全需求细化
    ↓
硬件安全概念、软件安全概念、生产与运行…  ← HSC/SSC deferred
```

**核心转变**：FSR 描述「功能层面要实现什么安全目标」；TSC 回答「技术上如何把 FSR 落实到系统架构、安全机制、故障处理与接口约束上」。FSR 技能止于功能层；TSC 是独立下游交付物。

### 8 工程阶段 ↔ 13 workflow step 映射

| 工程阶段 | 内容要点 | workflow step |
|---|---|---|
| 阶段 0：启动与范围对齐 | 确认 Item/变型/ECU 范围；锁定 FSR/SG 版本；列 open | Step 1 |
| 阶段 1：输入清点与来源分级 | T0–T5 分级；解析材料 | Step 2 |
| 阶段 2：架构与安全元素识别 | 安全相关元素、单点/共因敏感区 | Step 3–4 |
| 阶段 3：FSR→TSR 派生 | 结构化派生、可验证性检查 | Step 5–6、9 |
| 阶段 4：安全机制与故障处理 | 按 SG 组织；FTTI 链路 | Step 5–6、9 |
| 阶段 5：接口与 ASIL 分解 | 接口 TSR；分解约束 | Step 5–6、9 |
| 阶段 6：追溯矩阵与验证计划 | SG–FSR–TSR–机制–架构 | Step 6、9 |
| 阶段 7：评审与独立审查 | 完整性/一致性/独立性 | Step 10–11 |
| 阶段 8：定稿与下游交接 | review-ready 包；交接 HSC/SSC | Step 12–13 |

### TSC 目的（读者应能理解）

1. 每条 **TSR** 如何从 **FSR / SG** 派生
2. 安全需求在 **架构元素**（ECU、传感器、执行器、通信、软件组件等）上的 **分配**
3. 实现安全目标所需的 **技术安全机制**（检测、缓解、进入安全状态）
4. **故障检测与处理**、安全状态、降级/警告策略
5. 为 **系统设计、HW-SW 接口、软硬件安全需求** 提供可追溯输入

### TSC 边界（做什么 / 不做什么）

| TSC 应包含 | TSC 通常不包含（留给下游） |
|---|---|
| 技术安全需求（TSR）及追溯 | 详细电路设计、详细软件实现 |
| 架构级安全分配与安全机制概念 | 完整硬件安全概念（HSC）终稿 |
| 故障处理与安全状态策略 | 完整软件安全概念（SSC）终稿 |
| HW-SW / SW-SW 接口安全约束（概要） | 生产、运行、服务阶段详细规程 |
| ASIL 分解/继承的技术侧理由 | 功能安全认证结论或 sign-off |

### 与相邻文档的关系

```
         SG / HARA
              │
         FSC / FSR  ──派生──▶  TSR（在 TSC 中）
              │                    │
              │                    ├──▶ 系统架构分配
              │                    ├──▶ 安全机制
              │                    └──▶ 接口安全需求
              ▼
    系统设计规格（更细）
              │
      ┌───────┴───────┐
      ▼               ▼
  HW 安全概念      SW 安全概念
```

| 文档 | 与 TSC 关系 |
|---|---|
| FSR | 上游；TSC 不得改写 SG/FSR 事实，只能派生 TSR |
| 系统设计 | 下游；将 TSC 机制细化为设计决策 |
| HSC / SSC | 下游；把架构级机制落实为软硬件需求 |
| 安全验证报告 | 下游；验证 TSR 是否满足；TSC 不宣称已验证 |

### 常见失效模式（全程警惕）

| 失效 | 后果 |
|---|---|
| 把 FSR 原句复制为 TSR | 无法指导设计与验证 |
| 只有需求表，没有机制与故障处理 | 不满足 Clause 8 精神 |
| 架构图与分配表不一致 | 追溯断裂 |
| 安全状态与 HARA 不一致且无说明 | 概念与系统阶段脱节 |
| 用参考项目机制填本项目 | 事实来源污染（P0） |
| 在 TSC 中做合规/sign-off 结论 | 越权 |
| 忽略 ASIL 分解约束 | 后续 HW/SW 安全需求 ASIL 错误 |

## Supported Level And Positioning

`TechnicalSafetyConcept` 为 **document-type skill 层**交付类型；通过 `task.yaml` 的 `task_type: TechnicalSafetyConcept` 加载本子 skill 与各 step 子 skill。须遵守通用 `writing-core` 与 artifact 契约。

与既有 `task_type: tsc`（若配置）共享同一文档语义；本目录为 PascalCase 技能路径与逐步子 skill 实现。HSC/SSC **deferred**：不创建 HSC/SSC 文档类型或 workflow。

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| Item 定义 / 范围说明 | source | Item 与系统边界上下文 |
| Safety Goals 确认清单 | source | SG ID、表述、ASIL、安全状态 |
| FSR 确认清单 / FSC 摘录 | source | **核心上游**：FSR-xx 及 SG 链接 |
| HARA 摘要 / FTTI / 安全状态摘录 | source | **仅**摘要中显式 FTTI、安全状态、HE→SG |
| 系统架构 / 框图 / 元素清单 | source | TSR 分配、机制落点 |
| 项目约束 / 假设 | source | 限制与依赖 |
| TSC 模板 | template | L1/L2 结构 |
| TSC 检查清单 | checklist | 完备性检查 |
| 技术安全概念写法参考 | reference | 方法学（T3） |
| 样例 TSC | sample | **仅**章节与表格形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | |
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-ARCH | 系统架构概述（安全视角） | ★ |
| SEC-SG | Safety Goal 追溯 | ★ |
| SEC-FSR | FSR 上游追溯摘要 | ★ |
| SEC-TSR | 技术安全需求表 TSR-xx | ★ |
| SEC-MECH | 技术安全机制 | ★ |
| SEC-FAULT | 故障检测与处理概念 | ★ |
| SEC-DEGRADE | 警告与降级策略 | ★ |
| SEC-IFACE | 接口安全需求（概要） | ★ |
| SEC-ASIL | ASIL 继承与分解 | ★ |
| SEC-TRACE | 追溯矩阵 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-LIMIT | 假设、限制与开放确认 | ★ |
| SEC-OPEN | 开放问题与待确认项 | |
| SEC-REVIEW | 审查总结与状态声明 | ★ |
| SEC-DIFF | 与参考 TSC 的差异（Δ-Analysis） | With-Reference 建议 |

## Critical Claims

TSC critical claim 包括：

- technical safety requirement wording（TSR 表述）
- fsr linkage（FSR 链接）
- safety goal linkage（SG 链接）
- architecture allocation（架构分配）
- safety mechanism concept（安全机制概念）
- fault handling strategy（故障处理策略）
- safe state / degradation linkage（安全状态/降级链接）
- interface safety requirement（接口安全需求）
- asil inheritance / decomposition（ASIL 继承/分解）
- verification method（验证方法）
- requirement completeness / sufficiency（完整性/充分性）
- final TSC approval / compliance conclusion

须 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION`。FSR source 仅支撑其**显式包含**的 FSR-xx 与 SG 链接，不得 blanket 批准全部 TSR。HARA 摘要仅支撑其**显式包含**的 FTTI/安全状态/追溯。

## Forbidden Final Claims

无充分 T0/T1 与 HITL 时禁止：

- TSC is approved / 技术安全概念已批准
- requirements are complete and compliant / 需求完整且合规
- safety goals / FSR are fully satisfied at technical level
- ASIL inheritance / decomposition is validated
- verification method is sufficient
- fault tolerance time requirements are fully met
- ready for production release / 可量产
- risk is accepted / compliance is confirmed
- 将 sample TSC 中的 TSR/机制/ASIL/架构分配照搬为本项目事实

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（FSR、SG、HARA 摘要、架构、Item 定义等）
- T2：template / checklist
- T3：reference（写法方法，不单独证明本项目事实）
- T4：sample（仅形状/风格）
- T5：推断，不支撑 critical claim

**sample 绝不是 fact source**。FSR source **不是** blanket 批准记录；HARA 摘要**不是**新 HARA 或全面批准记录。

## Review / Verification Focus

- FSR / SG 追溯完备性
- 每条 TSR 链到 FSR 与 SG（source 或 open）
- 架构分配与机制落点一致
- ASIL 来自 source/HITL，非 sample
- FTTI/FDTI/FHTI 有来源或 open，非静默断言满足
- 验证方法未越权标为已充分
- **无 HSC/SSC 泄漏**
- sample / reference 未当事实
- `NEEDS_USER_CONFIRMATION` 保留

## Final Report Boundary

`final_report.md` 为 review-ready 包，非专业批准，非 formal sign-off，非 HSC/SSC 交付。

## 贯穿全程的核心原则（质量原则）

1. **TSC ≠ FSR 复述**：须体现技术分配与机制，而非换措辞重复功能需求。
2. **追溯双向**：不仅能从 TSR 追到 SG，也能从 SG 追到 TSR 覆盖。
3. **时间约束显式**：FTTI/FHTI/FDTI 不能隐含在 prose 里，宜表格化。
4. **TSC ≠ HSC/SSC**：不写硬件/软件安全概念终稿或详细实现。
5. **TSC ≠ 新 HARA**：不把 HARA 摘要当危害分析结论或 blanket 批准。
6. **事实来源分离**：sample 只借结构，不借内容；每条 TSR 须链到**本项目 source** 中的 FSR/SG。
7. **缺口显式**：缺架构、缺 FSR、缺 FTTI 来源 → 标 open，不编造 TSR。
8. **保守措辞**：用「候选」「待确认」「review-ready」，避免「已批准」「已合规」。
9. **交付边界**：`ready_for_human_review` / `finalized_with_open_items`，**非** approved。

## 全程 P0 红线（两种情景均适用）

无论 From-Scratch 还是 With-Reference，以下 5 条任一违反即 **P0**，须各 step 子 skill 在 Checklist / Review 中持续守护：

1. 样例 / 参考 TSC **不能**支撑 TSR / 机制 / ASIL 事实（sample ≠ fact source）。
2. 每条 TSR 须链 FSR / SG（或显式 open），不得无追溯锚点。
3. 禁止 HSC / SSC 泄漏；禁止「已批准 / 已合规 / 可量产」等越权结论。
4. FTTI 须 **表格化**、有来源或 open，不得 prose 隐含或静默断言满足。
5. TSC ≠ FSR 复述：TSR 须体现技术分配与机制，而非换措辞重复功能需求。

## 两种情景（From-Scratch / With-Reference）

与 FSR/IDD/HARA 惯例一致；各 step 子 skill 含 **情景差异** 与分步 Checklist。

### 核心差异速览

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断填 TSR/机制 | 把参考 TSC 的 TSR/机制/ASIL 当本项目事实 |
| sample 角色 | 仅表头/章节形状 | 参考 TSC 必须 `role=sample`，`is_fact_source=false` |
| 额外章节 | 无 | 建议 **SEC-DIFF / Δ-Analysis** |
| 写作模式 | 大量 confirmation_required / placeholder | 可更多 conservative_candidate，仍须逐条 EVD |
| 参考 TSC | 通常无或仅 template | 单独登记 sample；本项目 FSR/SG/架构须独立 source；用 `sp-DIFF`、`TASK-DIFF` |

### 按步快速对照（重点防什么）

| Step | From-Scratch | With-Reference |
|---|---|---|
| 1 输入 | 无 FSR 仍开跑 | 参考 TSC 标成 source |
| 2 清单 | 静默跳过解析失败 | 参考 TSR 进 inventory 事实字段 |
| 3 索引 | FSR 无索引无 gap | 参考 TSC 进 topic_index |
| 4 大纲 | 无材料却标 complete | 参考内容进大纲正文 |
| 5 计划 | 无证据标 supported | 参考 TSC 作 required_evidence |
| 6 证据 | 编造 citation | sample 进 matrix |
| 9 草稿 | 静默填 TSR/机制 | 参考措辞无 EVD 进表 |
| 10 审查 | open 被掩盖 | 缺 Δ-Analysis；参考当事实 |
| 11 验证 | 静默填值 | T4 支撑 critical claim |
| 12 修订 | 无证据关 P0 | 用参考关 P0 |
| 13 交付 | 越权批准措辞 | 交付未声明参考边界 |

**一句话**：From-Scratch 查输入够不够、gap 是否诚实；With-Reference 查参考 TSC 是否被当事实，并全程保留 Δ-Analysis 与 TASK-DIFF。
