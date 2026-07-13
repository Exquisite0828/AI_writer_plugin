---
name: software-requirement-document-type
description: 中文优先指导汽车控制器产品 Software Requirement（SwRS，软件需求）文档写作；保留 ASPICE SWE.1、ISO 26262-6 软件层接口、追溯、System Architecture 参考边界、tier、HITL 与 candidate-update 约束。
---

# Software Requirement Document Type Skill

Use this skill for `task_type: SoftwareRequirement`.

## 中文交互默认规则

默认用中文解释 SwRS workflow、上游系统需求与系统架构追溯、软件接口、时序/资源约束、验证方法与 open confirmations。保留 Software Requirement、SwRS、SWE.1、ISO 26262-6、System Architecture、SWR-F-xx、SWR-IF-xx、HITL、NEEDS_USER_CONFIRMATION 等术语。

## Document Type Purpose

Software Requirement（SwRS，软件需求规格）支撑汽车控制器软件在 **ASPICE SWE.1（Software Requirements Analysis）** 与 **ISO 26262-6 软件开发输入** 语境下的可追溯、可审查交付物。组织：

- 软件范围、上下文与运行假设
- 上游 System Requirement / TSR / System Architecture 追溯摘要
- 软件功能需求（`SWR-F-xx`）
- 软件接口需求（`SWR-IF-xx`）
- 时序、性能、资源与模式转换需求
- 诊断、降级与故障处理的软件行为需求
- 安全相关软件需求摘要（仅引用既有上游，不做新安全分析）
- 需求追溯矩阵（上游 ↔ SwRS ↔ 下游预留）
- 验证方法候选
- 假设、限制与开放确认

本类型**不**产出 HARA、FSR、TSC、Software Architecture / SwAD 终稿；**不**做危害分析、ASIL 判定、技术安全机制设计或软件设计；**不**给出批准或合规结论。

## 总过程概览

本目录按 **13 个** workflow step（Step 1–13；Step 6 含证据·引用·章节计划三阶段）提供 SwRS worker overlay guidance。每步子 skill 位于 `skills/document-types/SoftwareRequirement/steps/step-*.md`，内含 **SwRS 方法论、Checklist 与 Review 要点**，对齐 ASPICE SWE.1 与 ISO 26262-6。

**一句话**：在已登记的系统需求、系统架构、接口规范与项目软件 source 之下，用有来源、可追溯、有 open 项的方式整理控制器软件需求候选包；不做架构终稿、不做安全分析、不做批准或合规认证。

## Supported Level And Positioning

`SoftwareRequirement` 是非 official L3 的 Skill/overlay 指导资产。当前 metadata builder 可在同名 `task_type` 被明确选择时把本目录的路径/hash 放入 StepContextPackage；Python 不把它解释为 SwRS rules registry，也不执行端到端内容引擎。

```text
Stakeholder / Customer Need
    ↓
System Requirement（ASPICE SYS.2）
    ↓
System Architecture（ASPICE SYS.3）
    ↓
Software Requirement / SwRS（本类型）← ASPICE SWE.1
    ↓
Software Architecture / Unit Design / Test
```

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| System Requirement / SyRS | source | 软件需求上游意图与追溯锚点 |
| 当前项目 System Architecture | source | 分配上下文、接口边界、运行模式 |
| 既有项目 System Architecture 报告 | sample / reference | **仅**结构、章节、差异启发，非本项目事实 |
| 系统接口规范 / CAN 矩阵 / 诊断接口 | source | `SWR-IF-xx`、方向、时序 |
| 平台/芯片/OS/BSW 约束 | source | 资源、调度、依赖约束 |
| 既有 TSR / 软件安全需求输入（若有） | source | 安全相关软件需求引用 |
| SwRS 模板 | template | 章节与表格结构 |
| SWE.1 / ISO 26262 检查清单 | checklist | 完备性检查 |
| 方法学参考 | reference | 写法，不证明项目事实 |
| 历史项目 SwRS | sample | **仅**风格与表格形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-SWCTX | 软件上下文、边界与运行模式 | ★ |
| SEC-UPTRACE | 上游需求与架构入口 | ★ |
| SEC-FUNC | 软件功能需求 `SWR-F-xx` | ★ |
| SEC-IF | 软件接口需求 `SWR-IF-xx` | ★ |
| SEC-TIME | 时序与性能需求 | ★ |
| SEC-RESOURCE | 资源与平台约束 | ★ |
| SEC-DIAG | 诊断、故障处理与降级 | ★ |
| SEC-SAFE-SW | 安全相关软件需求（若有） | |
| SEC-TRACE | 需求追溯矩阵 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-ASSUMP | 假设、依赖与开放项 | ★ |
| SEC-REVIEW | 审查总结与状态声明 | ★ |
| SEC-DIFF | 与参考资料的差异（仅 With-Reference） | |

## Critical Claims

SwRS critical claim 包括：

- software requirement wording
- upstream system requirement / architecture linkage
- interface definition（含方向、触发、时序）
- timing / performance / resource limit
- diagnostic / degraded behavior
- safety-related software linkage
- verification method
- requirement completeness / consistency / sufficiency
- final approval / ASPICE or ISO 26262 compliance conclusion

以上须 T0/T1 支撑或保留 `NEEDS_USER_CONFIRMATION`。历史项目 `SystemArchitecture` 报告或历史 SwRS **不能**支撑本项目软件需求事实。

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（SyRS、当前项目 System Architecture、接口规范、平台约束等）
- T2：template / checklist
- T3：reference（方法学）
- T4：sample（仅结构/风格）
- T5：推断

**关键边界**：

1. 当前项目 `SystemArchitecture` 可作为 T1 source。
2. 其他项目的 `SystemArchitecture` 报告只能是 T4 sample 或 T3 reference。
3. sample / reference 不能支撑 `SWR-F-xx`、`SWR-IF-xx`、时序值、资源值、诊断行为。

## Forbidden Final Claims

禁止：

- `SwRS is approved`
- `requirements are complete and compliant`
- `ASPICE SWE.1 satisfied`
- `ISO 26262 compliant`
- `ready for production release`
- 将历史项目架构/需求中的接口、限值、任务周期照搬为本项目事实

## Forbidden Content

SwRS 不得写入：

- HARA、hazardous event、S/E/C、ASIL、Safety Goal
- FSR、TSR、TSC 终稿
- 软件架构设计、任务分配、模块设计终稿
- 单元实现细节、代码级算法说明
- 风险接受或量产批准结论

## Review / Verification Focus

- ASPICE SWE.1：软件需求分析、规格化、上游追溯
- 每条 `SWR-F` / `SWR-IF` 有上游来源或 open
- 接口含方向、触发条件、时序或 open
- 时序/资源/诊断约束有 source 或 open
- **无 HARA / TSR / 架构设计终稿泄漏**
- 历史 `SystemArchitecture` / 历史 SwRS 未当事实
- `NEEDS_USER_CONFIRMATION` 保留

## 两种情景

| 维度 | From-Scratch | With-SystemArchitecture-Reference |
|---|---|---|
| 主要风险 | 输入不足、静默补软件需求 | 把历史项目 `SystemArchitecture` 报告当本项目事实 |
| 架构输入 | 当前项目架构不足则 open | 历史项目架构只作 sample/reference |
| 额外章节 | 无 | 建议 `SEC-DIFF` |
| 写作模式 | 更多 confirmation_required | 更多 conservative_candidate，但仍逐条证据化 |
