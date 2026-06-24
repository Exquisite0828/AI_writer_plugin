---
name: system-architecture-document-type
description: 中文优先指导汽车控制器产品 System Architecture（系统架构）文档写作；保留 ASPICE SYS.3、ISO 26262 系统层接口、架构分配、接口边界、追溯、tier、HITL 与 candidate-update 约束。
---

# System Architecture Document Type Skill

Use this skill for `task_type: SystemArchitecture`.

## 中文交互默认规则

默认用中文解释 System Architecture workflow、架构分解、元素分配、接口边界、诊断与降级链路、验证方法与 open confirmations。保留 System Architecture、SYS.3、logical architecture、physical architecture、allocation、interface、ECU、HITL、NEEDS_USER_CONFIRMATION 等术语。

英文材料可保留原文架构术语与需求语句；说明优先中文。不得把 candidate 措辞写成系统架构已批准、ASPICE 合规认证或 ISO 26262 合规结论。

## Document Type Purpose

System Architecture（系统架构文档）支撑 **汽车控制器（ECU）产品** 在 **ASPICE SYS.3（System Architectural Design）** 与 **ISO 26262 系统层开发接口** 语境下的可追溯、可审查交付物。组织：

- ECU / 产品与架构范围
- 上游 System Requirement / SyRS 追溯摘要
- 逻辑架构（功能分解、职责划分）
- 物理 / 技术架构（ECU 内部模块、外部接口、资源约束）
- 架构元素清单与分配关系
- 接口架构（信号、通信、对端、方向、边界）
- 诊断、降级与故障处理架构链路
- 安全相关架构约束摘要（**引用**既有 FSR / SG / TSC 输入时）
- 需求到架构元素的分配矩阵
- 验证方法候选
- 假设、限制与开放确认

本类型**不**产出 HARA、FSR、TSC、SwRS/HwRS 终稿；**不**做危害分析、ASIL 判定或技术安全需求终稿；**不**批准架构设计或合规结论。

## 总过程概览

经 **13 个** workflow step skill 驱动（逻辑 Step 1–6、9–15；Step 6 含证据·引用·章节计划三阶段）。每步子 skill：`skills/document-types/SystemArchitecture/steps/step-*.md`，内含 **System Architecture 方法论、Review/Checklist 要点**（ASPICE SYS.3 + ISO 26262 系统层接口对齐）。

**一句话**：在已登记的 SyRS / 架构 source 与项目约束之下，用有来源、可追溯、有 open 项的方式整理控制器系统架构候选包；不做 HARA/FSR/TSC/SwRS 终稿，不做批准或合规认证。

## Supported Level And Positioning

`SystemArchitecture` 为 **document-type skill 层**交付类型；通过 `task.yaml` 的 `task_type: SystemArchitecture` 加载本子 skill 与各 step 子 skill。须遵守通用 `writing-core` 与 artifact 契约。

**上下游关系**：

```text
干系人/客户需求（SWRS、RFQ、法规）
    ↓
System Requirement / SyRS（ASPICE SYS.2）
    ↓
System Architecture（本类型）← ASPICE SYS.3
    ↓
├─→ Item Definition / HARA / FSR（功能安全链的上游事实）
├─→ TSC（若已有功能安全上游输入时的下游接口）
└─→ SwRS / HwRS / 详细设计（本类型不写终稿）
```

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| System Requirement / SyRS | source | 架构分解、功能到元素分配的核心上游 |
| 系统上下文 / 项目架构说明 | source | 产品范围、变型、边界 |
| 接口规范 / CAN 矩阵 / 网络拓扑 | source | 接口架构、方向、对端 |
| 诊断约束 / 故障处理说明 | source | 诊断链路、降级架构 |
| 平台资源 / 芯片 / OS / 中间件约束 | source | 物理架构与分配约束 |
| 既有 FSR / SG / TSC 摘要（若有） | source | SEC-SAFE-ARCH **引用**，非新安全分析 |
| 架构模板 | template | L1/L2 结构 |
| SYS.3 / 内部架构检查清单 | checklist | 完备性检查 |
| ASPICE / ISO 26262 写法参考 | reference | 方法学（T3） |
| 参考项目架构文档 | sample | **仅**章节与图表形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | |
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-REF | 参考文件与标准 | |
| SEC-TERMS | 术语与缩略语 | |
| SEC-CONTEXT | 产品/系统上下文与边界 | ★ |
| SEC-REQTRACE | 上游需求摘要与架构入口 | ★ |
| SEC-LARCH | 逻辑架构 | ★ |
| SEC-PARCH | 物理/技术架构 | ★ |
| SEC-ELEM | 架构元素清单 | ★ |
| SEC-IF | 接口架构与边界 | ★ |
| SEC-ALLOC | 需求到架构元素分配矩阵 | ★ |
| SEC-DIAG | 诊断、降级与故障处理架构 | ★ |
| SEC-SAFE-ARCH | 安全相关架构约束（若有） | |
| SEC-RES | 资源与平台约束 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-OPEN | 开放问题与待确认项 | |
| SEC-REVIEW | 审查总结与状态声明 | ★ |
| SEC-DIFF | 与参考架构文档的差异（Δ-Analysis） | With-Reference 建议 |

## Critical Claims

System Architecture critical claim 包括：

- architecture decomposition wording（架构分解表述）
- upstream requirement linkage（上游 SyRS / System Requirement 追溯）
- architecture element definition（架构元素定义）
- interface architecture definition（接口架构定义，含方向与边界）
- allocation rationale（需求到架构元素分配理由）
- diagnostic / degradation architecture linkage（诊断与降级链路）
- platform / resource constraint allocation（资源与平台约束）
- safety-related architecture linkage（若 SEC-SAFE-ARCH：仅引用 FSR/SG/TSC，非新安全分析）
- verification method（验证方法）
- architecture completeness / consistency / sufficiency（完整性 / 一致性 / 充分性）
- final architecture approval / ASPICE or ISO 26262 compliance conclusion

须 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION`。参考架构文档 **不能** blanket 支撑全部架构元素 / 分配 / 接口事实。

## Forbidden Final Claims

无充分 T0/T1 与 HITL 时禁止：

- architecture is approved / 系统架构已批准
- architecture is complete and compliant / 架构完整且合规
- ASPICE SYS.3 satisfied / ASPICE Level X achieved
- ISO 26262 compliant / 已满足功能安全合规
- ready for production release / 可量产
- 将 sample 架构文档中的元素、接口、分配、资源限值照搬为本项目事实

## Forbidden Content（全文）

System Architecture **不得**写入以下专业结论性内容（属其他文档类型）：

- hazard、hazardous event、S/E/C、ASIL、Safety Goal（HARA/FSR）
- 技术安全需求 TSR、技术安全机制终稿（TSC）
- 软件需求 SwRS、硬件需求 HwRS 终稿
- 详细软件模块设计、详细硬件电路设计
- 危害分析、风险可接受结论

SEC-SAFE-ARCH 仅允许：**引用** source 中已存在的 FSR/SG/TSC 约束，并链到架构元素 / 接口 / 分配；**禁止**新做 HARA、ASIL 或 TSR 判断。

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（SyRS、架构说明、接口规范、平台约束等）
- T2：template / checklist
- T3：reference（ASPICE/ISO 写法，不单独证明本项目事实）
- T4：sample（仅形状/风格）
- T5：推断，不支撑 critical claim

**sample 绝不是 fact source**。参考项目架构文档 **不是**本项目架构事实。

## Review / Verification Focus

- ASPICE SYS.3：架构分解、分配、接口与设计约束、与上游需求追溯
- 每条架构元素 / 接口 / 分配 有上游来源或 open
- 接口含**方向**、对端、边界与责任归属
- 逻辑架构与物理架构一致，分配可解释
- 诊断 / 降级链路有 source 或 open
- **无 HARA / ASIL / SG / TSR 泄漏**
- sample / reference 未当事实
- `NEEDS_USER_CONFIRMATION` 保留

## Final Report Boundary

`final_report.md` 为 review-ready 包，非专业批准，非 formal sign-off，非 ASPICE 评估通过声明。

## 贯穿全程的核心原则

1. **System Architecture ≠ HARA/FSR/TSC**：不写危害、ASIL、Safety Goal、TSR 终稿。
2. **System Architecture ≠ SwRS/HwRS**：不写软件/硬件需求终稿或详细实现设计。
3. **事实来源分离**：sample 只借结构；每条架构元素 / 接口 / 分配 须链到**本项目 source**。
4. **缺口显式**：缺材料标 open，不静默填分配、接口方向或资源值。
5. **保守措辞**：架构一致性、验证充分性缺确认时保留 `NEEDS_USER_CONFIRMATION`。
6. **交付边界**：`ready_for_human_review` / `finalized_with_open_items`，**非** approved。

## 两种情景（From-Scratch / With-Reference）

与 SyRS / IDD / TSC 惯例一致；各 step 子 skill 含 **情景差异** 与分步 Checklist。

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断填架构元素 / 接口 / 分配 | 把参考架构文档的元素 / 接口 / 资源当本项目事实 |
| sample 角色 | 仅图表/章节形状 | 同上；参考架构文档必须 `role=sample` |
| 参考架构文档 | 通常无或仅 template | 单独登记 sample；SyRS / 接口规范须独立 source |
| 额外章节 | 无 | 建议 **SEC-DIFF / Δ-Analysis**（`sp-DIFF`、`TASK-DIFF`） |
| 写作模式 | 大量 confirmation_required / placeholder | 更多 conservative_candidate，仍须逐条 EVD |

### 按步快速对照（重点防什么）

| Step | From-Scratch | With-Reference |
|---|---|---|
| 1 输入 | 无 SyRS 仍开跑 | 参考架构文档标成 source |
| 2 清单 | 静默跳过解析失败 | 参考元素 / 接口进 inventory 事实字段 |
| 3 索引 | SyRS / 接口无索引无 gap | 参考架构进 topic_index 事实条目 |
| 4 大纲 | 无材料却标 complete | 参考内容进大纲正文 |
| 5 计划 | 无证据标 supported | 参考架构作 required_evidence |
| 6 证据 | 编造 citation | sample 进 matrix |
| 9 草稿 | 静默填分配 / 接口方向 / 资源值 | 参考措辞无 EVD 进表 |
| 10 审查 | open 被掩盖 | 缺 Δ-Analysis；参考当事实 |
| 11 验证 | 静默填值 | T4 支撑 critical claim |
| 12 修订 | 无证据关 P0 | 用参考关 P0 |
| 13 交付 | 越权批准措辞 | 交付未声明参考边界 |

**一句话**：From-Scratch 查输入够不够、gap 是否诚实；With-Reference 查参考架构文档是否被当事实，并全程保留 Δ-Analysis 与 TASK-DIFF。
