---
name: system-requirement-document-type
description: 中文优先指导汽车控制器产品 System Requirement（SyRS，系统需求）文档写作；保留 ISO 26262、ASPICE SYS.2/SYS.3 接口、追溯、tier、HITL 与 candidate-update 约束。
---

# System Requirement Document Type Skill

Use this skill for `task_type: SystemRequirement`.

## 中文交互默认规则

默认用中文解释 SyRS workflow、干系人需求追溯、接口方向、验证方法与 open confirmations。保留 SyRS、System Requirement、SWRS、SYS-F-xx、SYS-IF-xx、SYS.2、SYS.3、HITL、NEEDS_USER_CONFIRMATION 等术语。

英文材料可保留原文需求语句；说明优先中文。不得把 candidate 措辞写成 SyRS 已批准、ASPICE 合规认证或 ISO 26262 合规结论。

## Document Type Purpose

System Requirement（SyRS，系统需求规格）支撑 **汽车控制器（ECU）产品** 在 **ASPICE SYS.2（System Requirements Analysis）** 与 **ISO 26262 系统层开发输入** 语境下的可追溯、可审查交付物。组织：

- ECU/产品标识与范围
- 干系人/客户需求摘要与上游追溯（SWRS、RFQ 等）
- 功能需求表（SYS-F-xx）
- 接口需求表（SYS-IF-xx，含方向）
- 性能、环境、诊断与降级需求
- 安全相关系统需求摘要（**引用**既有 FSR/SG，**不做** HARA）
- 需求追溯矩阵（上游 ↔ SyRS ↔ 下游预留）
- 验证方法候选
- 假设、限制与开放确认

本类型**不**产出 HARA、FSR、TSC、SwRS/HwRS 终稿；**不**做危害分析或 ASIL 判定；**不**批准需求集或 ASPICE/ISO 26262 合规结论。

## 总过程概览

本目录按 **13 个** workflow step（Step 1–13；Step 6 含证据·引用·章节计划三阶段）提供 SyRS worker overlay guidance。每步子 skill：`skills/document-types/SystemRequirement/steps/step-*.md`，内含 **SyRS 方法论、Review/Checklist 要点**（ASPICE SYS.2 + ISO 26262 系统层输入对齐）。

**一句话**：在已登记的上游客户需求与项目 source 之下，用有来源、可追溯、有 open 项的方式整理控制器 SyRS 候选包；不做 HARA/FSR/TSC，不做批准或合规认证。

## Supported Level And Positioning

`SystemRequirement` 是非 official L3 的 Skill/overlay 指导资产。当前 metadata builder 可在同名 `task_type` 被明确选择时把本目录的路径/hash 放入 StepContextPackage；Python 不把它解释为 SyRS rules registry，也不执行端到端内容引擎。

**上下游关系**：

```text
干系人/客户需求（SWRS、RFQ、法规）
    ↓
SyRS（本类型）← ASPICE SYS.2
    ↓
├─→ Item Definition（ISO 26262-3 §5）
├─→ 系统架构（ASPICE SYS.3）
├─→ FSR / HARA（功能安全链，独立文档类型）
└─→ SwRS / HwRS（软件/硬件需求，本类型不写终稿）
```

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| OEM SWRS / 客户需求 / RFQ | source | 干系人需求、功能/约束事实 |
| 系统架构说明 / 子系统划分 | source | 边界、分配上下文 |
| 接口规范 / CAN 矩阵 / 信号列表 | source | SYS-IF-xx、方向 |
| ODD / 运行场景说明 | source | 环境、工况上下文 |
| 诊断规范 / DTC 列表 | source | SEC-DIAG |
| 法规 / 型式认证要求清单 | source / reference | SEC-LEGAL |
| 既有 FSR / SG 清单（若有） | source | SEC-SAFE **引用**，非新安全分析 |
| SyRS 模板 | template | L1/L2 结构 |
| ASPICE SYS.2 / 内部 SyRS 检查清单 | checklist | 完备性检查 |
| ISO 26262 / ASPICE 写法参考 | reference | 方法学（T3） |
| 参考项目 SyRS | sample | **仅**章节与表格形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | |
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-REF | 参考文件与标准 | |
| SEC-TERMS | 术语与缩略语 | |
| SEC-IDENT | ECU/产品标识 | ★ |
| SEC-STAKE | 干系人需求摘要与来源 | ★ |
| SEC-FUNC | 功能需求 SYS-F-xx | ★ |
| SEC-IF | 接口需求 SYS-IF-xx | ★ |
| SEC-PERF | 性能与实时性 | ★ |
| SEC-ENV | 环境与运行约束 | ★ |
| SEC-DIAG | 诊断与降级 | ★ |
| SEC-SAFE | 安全相关系统需求（若有） | |
| SEC-SEC | 网络安全需求（若适用） | |
| SEC-LEGAL | 法规与合规约束 | |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-TRACE | 需求追溯矩阵 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-OPEN | 开放问题与待确认项 | |
| SEC-REVIEW | 审查总结与状态声明 | ★ |
| SEC-DIFF | 与参考 SyRS 的差异（Δ-Analysis） | With-Reference 建议 |

## Critical Claims

SyRS critical claim 包括：

- system requirement wording（需求表述）
- stakeholder / upstream requirement linkage（SWRS/RFQ 等上游追溯）
- interface definition（接口定义，含方向与对端）
- performance / limit values（性能与限值）
- safety-related system requirement linkage（若 SEC-SAFE：仅引用 FSR/SG，非新 HARA）
- verification method（验证方法）
- requirement completeness / sufficiency（完整性/充分性）
- final SyRS approval / ASPICE or ISO 26262 compliance conclusion

须 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION`。参考 SyRS **不能** blanket 支撑全部 SYS-xx。

## Forbidden Final Claims

无充分 T0/T1 与 HITL 时禁止：

- SyRS is approved / 系统需求已批准
- requirements are complete and compliant / 需求完整且合规
- ASPICE SYS.2 satisfied / ASPICE Level X achieved
- ISO 26262 compliant / 已满足功能安全合规
- ready for production release / 可量产
- 将 sample SyRS 中的需求/接口/限值照搬为本项目事实

## Forbidden Content（全文）

SyRS **不得**写入以下专业结论性内容（属其他文档类型）：

- hazard、hazardous event、S/E/C、ASIL、Safety Goal（HARA/FSR）
- 技术安全需求 TSR、技术安全机制（TSC）
- 软件需求 SwRS、硬件需求 HwRS 终稿
- 危害分析、风险可接受结论

SEC-SAFE 仅允许：**引用** source 中已存在的 FSR/SG 或客户安全需求，并链到 SYS-F/IF；**禁止**新做 HARA 判断。

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（SWRS、RFQ、架构、接口规范等）
- T2：template / checklist
- T3：reference（ASPICE/ISO 写法，不单独证明本项目事实）
- T4：sample（仅形状/风格）
- T5：推断，不支撑 critical claim

**sample 绝不是 fact source**。参考项目 SyRS **不是**本项目需求事实。

## Review / Verification Focus

- ASPICE SYS.2：干系人需求分析、系统需求规格、双向追溯（至少上游→SyRS）
- 每条 SYS-F / SYS-IF 有上游来源或 open
- 接口含**方向**与对端
- 性能/环境/诊断限值有 source 或 open
- **无 HARA/ASIL/SG/TSR 泄漏**
- sample / reference 未当事实
- `NEEDS_USER_CONFIRMATION` 保留

## Final Report Boundary

`final_report.md` 为 review-ready 包，非专业批准，非 formal sign-off，非 ASPICE 评估通过声明。

## 贯穿全程的核心原则

1. **SyRS ≠ HARA/FSR**：不写危害、ASIL、Safety Goal 新结论。
2. **SyRS ≠ TSC/SwRS**：不写技术安全机制或软件/硬件需求终稿。
3. **事实来源分离**：sample 只借结构；每条 SYS-xx 须链到**本项目 source**。
4. **缺口显式**：缺材料标 open，不静默填需求或限值。
5. **保守措辞**：需求措辞、验证充分性缺确认时保留 `NEEDS_USER_CONFIRMATION`。
6. **交付边界**：`ready_for_human_review` / `finalized_with_open_items`，**非** approved。

## 两种情景（From-Scratch / With-Reference）

与 IDD/FSR/HARA 惯例一致；各 step 子 skill 含 **情景差异** 与分步 Checklist。

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断填 SYS-xx/限值 | 把参考 SyRS 的需求/接口当本项目事实 |
| sample 角色 | 仅表头/章节形状 | 同上；参考 SyRS 必须 `role=sample` |
| 参考 SyRS | 通常无或仅 template | 单独登记 sample；SWRS/RFQ 须独立 source |
| 额外章节 | 无 | 建议 **SEC-DIFF / Δ-Analysis**（`sp-DIFF`、`TASK-DIFF`） |
| 写作模式 | 大量 confirmation_required / placeholder | 更多 conservative_candidate，仍须逐条 EVD |

### 按步快速对照（重点防什么）

| Step | From-Scratch | With-Reference |
|---|---|---|
| 1 输入 | 无 SWRS 仍开跑 | 参考 SyRS 标成 source |
| 2 清单 | 静默跳过解析失败 | 参考需求进 inventory 事实字段 |
| 3 索引 | SWRS 无索引无 gap | 参考 SyRS 进 topic_index 事实条目 |
| 4 大纲 | 无材料却标 complete | 参考内容进大纲正文 |
| 5 计划 | 无证据标 supported | 参考 SyRS 作 required_evidence |
| 6 证据 | 编造 citation | sample 进 matrix |
| 9 草稿 | 静默填 SYS-xx/限值 | 参考措辞无 EVD 进表 |
| 10 审查 | open 被掩盖 | 缺 Δ-Analysis；参考当事实 |
| 11 验证 | 静默填值 | T4 支撑 critical claim |
| 12 修订 | 无证据关 P0 | 用参考关 P0 |
| 13 交付 | 越权批准措辞 | 交付未声明参考边界 |

**一句话**：From-Scratch 查输入够不够、gap 是否诚实；With-Reference 查参考 SyRS 是否被当事实，并全程保留 Δ-Analysis 与 TASK-DIFF。
