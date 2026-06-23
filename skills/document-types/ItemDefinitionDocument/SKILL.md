---
name: item-definition-document-type
description: 中文优先指导 Item Definition Document（功能安全 Item 定义文档）写作；保留 ISO 26262-3 Clause 5 术语、source tier、HITL、sample/reference 边界与 candidate-update 约束。
---

# Item Definition Document Type Skill

Use this skill for `task_type: ItemDefinitionDocument`.

## 中文交互默认规则

默认用中文解释 Item 定义文档 workflow、材料角色、open confirmations 与最终 artifact。保留 Item、F-xx、IF-xx、system boundary、operational situation、reasonably foreseeable misuse、HITL、NEEDS_USER_CONFIRMATION 等术语。

英文材料可保留原文片段；说明优先中文。不得把 candidate 措辞写成 Item 定义已批准或 ISO 26262 合规结论。

## Document Type Purpose

Item Definition Document（IDD，Item 定义文档）支撑 **ISO 26262-3:2018 Clause 5（Item Definition）** 的可追溯、可审查交付物。目的是为后续 HARA / 安全概念提供**经来源支撑且边界清晰**的 Item 描述，包括：

- Item 标识与范围
- 功能描述（F-xx）
- 系统边界（In / Out of scope）
- 外部接口（IF-xx）
- 运行环境与约束
- 运行工况与模式（作为 HARA 输入上下文，**不在此文档做危害分析**）
- 假设、依赖与合理可预见误用

本类型**不**产出 hazard、S/E/C、ASIL、safety goal；不得将 IDD 写成 HARA 报告。

## 总过程概览

经 **13 个** workflow step skill 驱动（逻辑 Step 1–6、9–15；Step 6 含证据·引用·章节计划三阶段）。每步子 skill：`skills/document-types/ItemDefinitionDocument/steps/step-*.md`。

## Supported Level And Positioning

`ItemDefinitionDocument` 为 **document-type skill 层**交付类型；通过 `task.yaml` 的 `task_type: ItemDefinitionDocument` 加载本子 skill 与各 step 子 skill。须遵守通用 `writing-core` 与 artifact 契约。

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| SyRS / SRS / 系统需求 / 架构说明 | source | 功能、边界、接口事实 |
| 接口规范 / CAN 矩阵 / 信号列表 | source | IF-xx 与方向 |
| ODD / 运行场景说明 | source | 环境与工况上下文 |
| 假设与约束清单 | source | 假设、依赖 |
| IDD 模板 | template | L1/L2 结构 |
| ISO 26262-3 / 公司规范 | reference | Clause 5 方法学 |
| 检查清单 | checklist | 完备性检查 |
| 既有 IDD / Item 定义样例 | sample | **仅**章节与表格形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | |
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-REF | 参考文件与标准 | |
| SEC-TERMS | 术语与缩略语 | |
| SEC-IDENT | Item 标识（名称、版本、变型） | ★ |
| SEC-FUNC | 功能描述与功能清单 F-xx | ★ |
| SEC-BOUNDARY | 系统边界 | ★ |
| SEC-IF | 外部接口 IF-xx | ★ |
| SEC-ENV | 运行环境与约束 | ★ |
| SEC-OPS | 运行工况与模式（HARA 输入上下文） | ★ |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-MISUSE | 合理可预见误用 | ★ |
| SEC-DEP | 与其他 Item / 系统的交互与依赖 | |
| SEC-OPEN | 开放问题与待确认项 | |
| SEC-REVIEW | 审查总结与状态声明 | ★ |

## Critical Claims

IDD critical claim 包括：

- item 功能描述（F-xx）的准确性与完整性
- 系统边界（In / Out of scope）
- 外部接口定义（信号/机械/人机，含方向）
- 运行环境与操作约束
- 运行工况与模式描述（事实性，非危害结论）
- 假设与依赖
- 合理可预见误用场景
- Item 间交互与依赖关系

须 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION`。缺证据不得推断填值。

## Forbidden Final Claims

无充分 T0/T1 与 HITL 时禁止：

- item definition is approved / 定义已批准
- boundaries are final / 边界已最终确认
- all interfaces are complete and verified
- ISO 26262 compliant / 已满足 Clause 5 合规
- ready for production / 可量产
- 将 sample 中的功能/边界/接口照搬为本项目事实

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（SyRS、架构、接口规范等）
- T2：template / checklist（结构）
- T3：reference（Clause 5 框架，不单独证明本项目事实）
- T4：sample（仅形状/风格）
- T5：推断，不支撑 critical claim

**sample 绝不是 fact source**。不得从 sample IDD 或 sample HARA 的 Item 章节迁移具体功能/边界事实。

## Review / Verification Focus

- Clause 5 输入完备性（功能、边界、接口、环境、误用）
- 接口信号方向是否明确
- 边界是否有 In/Out 双向说明
- sample / reference 未当事实
- 无 hazard / ASIL / SG 内容渗入 IDD
- `NEEDS_USER_CONFIRMATION` 保留

## Final Report Boundary

`final_report.md` 为 review-ready 包，非专业批准，非 formal sign-off。

## 贯穿全程的核心原则

1. **IDD ≠ HARA**：不写危害、评级、安全目标。
2. **事实来源分离**：sample 只借结构。
3. **缺口显式**：缺材料标 open / gap，不静默填值。
4. **保守措辞**：边界与接口缺确认时保留 `NEEDS_USER_CONFIRMATION`。
