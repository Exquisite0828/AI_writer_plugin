---
name: software-architecture-document-type
description: 中文优先指导汽车控制器产品 Software Architecture（SwAD，软件架构）文档写作；保留 ASPICE SWE.2、ISO 26262-6 软件层接口、SwRS 追溯、组件分配、接口边界、tier、HITL 与 candidate-update 约束。
---

# Software Architecture Document Type Skill

Use this skill for `task_type: SoftwareArchitecture`.

## 中文交互默认规则

默认用中文解释 Software Architecture workflow、软件组件分解、SwRS 分配、软件接口、任务/调度架构、资源预算、诊断与降级链路、验证方法与 open confirmations。保留 Software Architecture、SwAD、SWE.2、ISO 26262-6、SwRS、System Architecture、SWA-COMP-xx、SWA-IF-xx、RTE、BSW、HITL、NEEDS_USER_CONFIRMATION 等术语。

英文材料可保留原文架构术语与需求语句；说明优先中文。不得把 candidate 措辞写成软件架构已批准、ASPICE 合规认证或 ISO 26262 合规结论。

## Document Type Purpose

Software Architecture（SwAD，软件架构设计）支撑 **汽车控制器（ECU）软件** 在 **ASPICE SWE.2（Software Architectural Design）** 与 **ISO 26262-6 软件架构设计接口** 语境下的可追溯、可审查交付物。组织：

- ECU 软件范围、分层与运行上下文（App / RTE / BSW / OS 等）
- 上游 SwRS 与 System Architecture 追溯摘要
- 逻辑软件架构（功能分解、职责划分）
- 物理/战术软件架构（组件、任务、调度、通信结构）
- 软件组件清单与 SwRS 分配关系
- 软件接口架构（内部 API、RTE 端口、服务接口、方向与边界）
- 诊断、降级与故障处理的软件架构链路
- 安全相关软件架构约束摘要（**引用**既有 TSR / 软件安全输入时）
- SwRS 到软件组件的分配矩阵
- 资源与实时约束（内存、CPU、栈、时序预算）
- 验证方法候选
- 假设、限制与开放确认

本类型**不**产出 HARA、FSR、TSC、详细设计 / 单元设计终稿；**不**做危害分析、ASIL 判定或技术安全机制终稿；**不**写代码级实现或单元算法；**不**批准架构设计或合规结论。

## 总过程概览

经 **13 个** workflow step skill 驱动（逻辑 Step 1–6、9–15；Step 6 含证据·引用·章节计划三阶段）。每步子 skill：`skills/document-types/SoftwareArchitecture/steps/step-*.md`，内含 **Software Architecture 方法论、Review/Checklist 要点**（ASPICE SWE.2 + ISO 26262-6 对齐）。

**一句话**：在已登记的 SwRS、当前项目 System Architecture、平台/BSW 约束与软件 source 之下，用有来源、可追溯、有 open 项的方式整理控制器软件架构候选包；不做 HARA/FSR/TSC/详细设计终稿，不做批准或合规认证。

## ASPICE Software Architecture 写作方法与过程（总纲）

### 标准语境

汽车控制器产品 Software Architecture（SwAD）对应 **ASPICE SWE.2（Software Architectural Design）**，并与 **ISO 26262-6 §7（软件架构设计）** 接口对齐。本 skill 指导的是 **review-ready 候选包** 的整理过程，不是 ASPICE 评估通过声明，也不是软件架构正式批准。

SWE.2 核心产出在本仓库中映射为：

| SWE.2 关注点 | 本类型章节 | 写作要点 |
|---|---|---|
| 静态架构（组件、分层、接口） | SEC-LOGARCH / SEC-PHYSARCH / SEC-COMP / SEC-IF | 组件职责、Layer、接口方向与边界 |
| 动态架构（任务、调度、模式转换） | SEC-PHYSARCH / SEC-RES | 任务周期、优先级、模式切换链路 |
| 与 SwRS 一致性 | SEC-UPTRACE / SEC-ALLOC | 双向追溯：每条 SwRS 有组件落点或 open |
| 资源消耗 | SEC-RES | 内存/栈/CPU/时序预算，有 source 或 open |
| 设计约束与诊断架构 | SEC-DIAG / SEC-RES | 故障检测/上报/降级在软件层的结构表达 |
| 安全相关约束（引用） | SEC-SAFE-ARCH | 仅引用 TSR/软件安全输入，不做新分析 |
| 验证方法 | SEC-VERIF | 架构评审、集成测试、静态分析等**候选**方法 |

### 八阶段方法链（映射 13 步 workflow）

```text
阶段 0  启动与范围对齐          → Step 1  输入材料
阶段 1  材料消化与索引          → Step 2  材料清单
                                 Step 3  文档目录索引
阶段 2  定大纲（L1→L2）         → Step 4  模板大纲
阶段 3  逐段分析与写作计划      → Step 5  大纲分析与写作计划
阶段 4  证据·引用·章节任务      → Step 6  证据映射（三阶段）
阶段 5  保守成稿                → Step 9  保守草稿
阶段 6  审查与形式验证          → Step 10 审查
                                 Step 11 验证
阶段 7  修订与交付              → Step 12 修订
                                 Step 13 最终报告
阶段 8  追溯与学习              → Step 14 运行总结
                                 Step 15 候选 profile 更新
```

**贯穿全程的读材料顺序**：`L1 → L2 → L3 → 原文摘录 → EVD → claim → 正文`

### 汽车控制器典型内容模型

写 SwAD 时，按以下顺序组织思维（不要求章节顺序完全相同，但内容须覆盖）：

1. **软件边界**：本 ECU 应用软件范围、变型、与 System Architecture 的接口上下文。
2. **分层模型**：App / ComplexDriver / RTE / BSW（Com/Dcm/Dem/…）/ MCAL / OS。
3. **逻辑分解**：功能块 → 候选软件组件（`SWA-COMP-xx`）。
4. **战术落地**：组件映射到任务、Runnable、BSW 模块、通信路径。
5. **接口架构**：RTE 端口、服务、回调、共享内存；**必须含 Direction**。
6. **SwRS 分配**：`SWR-F-xx` / `SWR-IF-xx` → `SWA-COMP-xx`，附分配理由。
7. **资源与实时**：ROM/RAM/栈、任务周期、WCET 线索、调度约束。
8. **诊断与降级**：DTC 处理链、降级模式在组件层的结构（非函数实现）。
9. **安全引用**：若有 TSR/软件安全输入，链到组件/接口/分区策略（引用 only）。
10. **验证候选**：架构评审、集成测试、资源分析、MISRA/静态分析等。

### 两种情景的方法差异

#### 情景 A · From-Scratch（从零开始）

**适用**：仅有 SwRS、当前项目 System Architecture、平台/接口约束，无可用历史 SwAD。

| 方法要点 | 说明 |
|---|---|
| 输入诚实 | 缺 SwRS / 接口 / BSW 约束即登记 gap，不用 reference 补 |
| 候选态写作 | 组件/接口/分配先标 `candidate_only`，大量 `confirmation_required` |
| 禁止静默推断 | 不默认任务周期、栈大小、RTE 端口方向、组件划分 |
| 正常 open 密度 | 初稿大量 `NEEDS_USER_CONFIRMATION` 是预期，不是失败 |
| 无 SEC-DIFF | 通常不设 Δ-Analysis 章（除非另有参考 sample 仅作形状） |

**阶段重点**：Step 1–3 确保上游锚点存在；Step 4–6 以 placeholder / confirmation 为主；Step 9 宁可空表也不编造；Step 10–11 不“关闭”无证据 open。

#### 情景 B · With-Reference（有历史项目 SwAD 参考）

**适用**：除本项目 source 外，还有历史 ECU/平台的 SwAD 或软件架构报告作结构与差异对照。

| 方法要点 | 说明 |
|---|---|
| 参考隔离 | 历史 SwAD 必须 `role=sample`，与本项目 source **分 file_id** |
| 形状可借、事实不可借 | 章节、表列、图类型可参考；组件名/接口/任务/资源值不可直接写入 |
| 强制 Δ-Analysis | `SEC-DIFF` + `sp-DIFF` + `TASK-DIFF` 贯穿 Step 4–13 |
| 差异四类 | Added / Removed / Modified / Scope-changed，每类至少检视 |
| 沿用须 HITL | 用户说“沿用参考方案”→ 须 T0 决策记录，不能 sample 直接升格 |
| 保守候选 | 可比 From-Scratch 更多 `conservative_candidate`，但**每条**仍须 EVD 或 open |

**阶段重点**：Step 1 预声明 SEC-DIFF；Step 2–3 历史 SwAD 只进 `style_hint`；Step 6 matrix 禁止 reference 作 evidence_source；Step 9 参考措辞无 EVD 不进正文；Step 13 交付须声明参考边界。

### 情景判定（Step 1 执行）

在 `task_brief.json` 中登记 `writing_scenario`：

- `from_scratch`：无历史 SwAD，或仅有 template/checklist/reference。
- `with_reference`：存在历史项目 SwAD 且 `role=sample`。

后续每步 Checklist 均按此字段分支执行。

## Supported Level And Positioning

`SoftwareArchitecture` 为 **document-type skill 层**交付类型；通过 `task.yaml` 的 `task_type: SoftwareArchitecture` 加载本子 skill 与各 step 子 skill。须遵守通用 `writing-core` 与 artifact 契约。

**上下游关系**：

```text
System Requirement / SyRS（ASPICE SYS.2）
    ↓
System Architecture（ASPICE SYS.3）
    ↓
Software Requirement / SwRS（ASPICE SWE.1）
    ↓
Software Architecture / SwAD（本类型）← ASPICE SWE.2
    ↓
├─→ Detailed Design / Unit Design（SWE.3）
├─→ Integration / Software Test
└─→ Static Analysis / MISRA / 集成验证
```

## Typical Inputs

| 材料 | 常见 role | 用途 |
|---|---|---|
| Software Requirement / SwRS | source | 组件分解、SwRS 分配的核心上游 |
| **当前项目** System Architecture | source | 系统层边界、接口上下文、运行模式 |
| 软件上下文 / 分层说明（App/RTE/BSW/OS） | source | 软件范围、分层、变型 |
| AUTOSAR / BSW / MCAL / OS 约束 | source | 物理架构、调度、资源约束 |
| RTE / 服务接口 / 内部 API 规范 | source | 软件接口架构、方向、对端 |
| 诊断 / 降级 / 故障处理软件说明 | source | 诊断链路、降级架构 |
| 芯片 / 内存 / 时序 / 调度预算 | source | 资源与实时约束 |
| 既有 TSR / 软件安全需求输入（若有） | source | SEC-SAFE-ARCH **引用**，非新安全分析 |
| SwAD 模板 | template | L1/L2 结构 |
| SWE.2 / ISO 26262-6 检查清单 | checklist | 完备性检查 |
| ASPICE / ISO 写法参考 | reference | 方法学（T3） |
| **历史项目** SwAD / 软件架构文档 | sample | **仅**章节与图表形状 |

## Default / Expected L1 Sections

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-DOC | 文档信息与修订历史 | |
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-REF | 参考文件与标准 | |
| SEC-TERMS | 术语与缩略语 | |
| SEC-SWCTX | 软件上下文、分层与运行模式 | ★ |
| SEC-UPTRACE | 上游 SwRS 与系统架构入口 | ★ |
| SEC-LOGARCH | 逻辑软件架构 | ★ |
| SEC-PHYSARCH | 物理/战术软件架构 | ★ |
| SEC-COMP | 软件组件清单 | ★ |
| SEC-IF | 软件接口架构与边界 | ★ |
| SEC-ALLOC | SwRS 到软件组件分配矩阵 | ★ |
| SEC-DIAG | 诊断、降级与故障处理软件架构 | ★ |
| SEC-SAFE-ARCH | 安全相关软件架构约束（若有） | |
| SEC-RES | 资源、调度与实时约束 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-OPEN | 开放问题与待确认项 | |
| SEC-REVIEW | 审查总结与状态声明 | ★ |
| SEC-DIFF | 与参考软件架构的差异（Δ-Analysis） | With-Reference 建议 |

## Critical Claims

Software Architecture critical claim 包括：

- software architecture decomposition wording（软件架构分解表述）
- upstream SwRS / System Architecture linkage（上游追溯）
- software component definition（软件组件定义）
- software interface architecture definition（软件接口定义，含方向与边界）
- SwRS allocation rationale（SwRS 到组件分配理由）
- task / scheduling architecture linkage（任务/调度架构）
- diagnostic / degradation software architecture linkage（诊断与降级链路）
- resource / timing budget allocation（资源与时序预算）
- safety-related software architecture linkage（若 SEC-SAFE-ARCH：仅引用 TSR/软件安全输入，非新安全分析）
- verification method（验证方法）
- architecture completeness / consistency / sufficiency（完整性 / 一致性 / 充分性）
- final software architecture approval / ASPICE or ISO 26262 compliance conclusion

须 T0/T1 支撑或保持 `NEEDS_USER_CONFIRMATION`。历史项目 SwAD **不能** blanket 支撑全部组件 / 接口 / 分配 / 资源事实。

## Forbidden Final Claims

无充分 T0/T1 与 HITL 时禁止：

- software architecture is approved / 软件架构已批准
- architecture is complete and compliant / 架构完整且合规
- ASPICE SWE.2 satisfied / ASPICE Level X achieved
- ISO 26262 compliant / 已满足功能安全合规
- ready for production release / 可量产
- 将 sample SwAD 中的组件、接口、任务、资源预算照搬为本项目事实

## Forbidden Content（全文）

Software Architecture **不得**写入以下专业结论性内容（属其他文档类型）：

- hazard、hazardous event、S/E/C、ASIL、Safety Goal（HARA/FSR）
- 技术安全需求 TSR、技术安全机制终稿（TSC）
- 详细设计、单元设计、类图、函数级算法、代码片段
- 硬件需求 HwRS 终稿
- 危害分析、风险可接受结论

SEC-SAFE-ARCH 仅允许：**引用** source 中已存在的 TSR / 软件安全约束，并链到软件组件 / 接口 / 分配；**禁止**新做 HARA、ASIL 或 TSR 判断。

## Source / Sample / Reference Policy

- T0：HITL 确认
- T1：项目 source（SwRS、当前项目 System Architecture、RTE/BSW 约束、接口规范、平台约束等）
- T2：template / checklist
- T3：reference（ASPICE/ISO 写法，不单独证明本项目事实）
- T4：sample（仅形状/风格；含历史项目 SwAD）
- T5：推断，不支撑 critical claim

**关键边界**：

1. **当前项目** `SystemArchitecture` 与 **当前项目** `SwRS` 可作为 T1 source。
2. **历史项目** SwAD / 软件架构报告只能是 T4 sample 或 T3 reference。
3. sample / reference 不能支撑 `SWA-COMP-xx`、`SWA-IF-xx`、任务周期、内存预算、栈大小、接口超时。

**sample 绝不是 fact source**。历史项目软件架构文档 **不是**本项目架构事实。

## Review / Verification Focus

- ASPICE SWE.2：软件架构分解、分配、接口与设计约束、与上游 SwRS 追溯
- 每条软件组件 / 接口 / 分配 有上游来源或 open
- 接口含**方向**、对端、边界与责任归属
- 逻辑架构与物理/战术架构一致，分配可解释
- 任务/调度/资源预算有 source 或 open
- 诊断 / 降级链路有 source 或 open
- **无 HARA / ASIL / SG / TSR / TSC / 详细设计泄漏**
- 历史 SwAD / 历史架构未当事实
- `NEEDS_USER_CONFIRMATION` 保留

## Final Report Boundary

`final_report.md` 为 review-ready 包，非专业批准，非 formal sign-off，非 ASPICE 评估通过声明。

## 贯穿全程的核心原则

1. **Software Architecture ≠ HARA/FSR/TSC**：不写危害、ASIL、Safety Goal、TSR 终稿。
2. **Software Architecture ≠ Detailed Design**：不写单元设计、类结构、函数算法、代码。
3. **事实来源分离**：sample 只借结构；每条组件 / 接口 / 分配 须链到**本项目 source**。
4. **缺口显式**：缺材料标 open，不静默填组件、接口方向、任务周期或资源预算。
5. **保守措辞**：架构一致性、验证充分性缺确认时保留 `NEEDS_USER_CONFIRMATION`。
6. **交付边界**：`ready_for_human_review` / `finalized_with_open_items`，**非** approved。

## 两种情景（From-Scratch / With-Reference）

与 SwRS / System Architecture 惯例一致；各 step 子 skill 含 **情景差异** 与分步 Checklist。

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 主要风险 | 输入不全、静默推断填组件 / 接口 / 分配 | 把历史 SwAD 的组件 / 接口 / 任务当本项目事实 |
| sample 角色 | 仅图表/章节形状 | 同上；历史 SwAD 必须 `role=sample` |
| 参考 SwAD | 通常无或仅 template | 单独登记 sample；SwRS / 当前项目架构须独立 source |
| 额外章节 | 无 | 建议 **SEC-DIFF / Δ-Analysis**（`sp-DIFF`、`TASK-DIFF`） |
| 写作模式 | 大量 confirmation_required / placeholder | 更多 conservative_candidate，仍须逐条 EVD |

### 按步快速对照（重点防什么）

| Step | From-Scratch | With-Reference |
|---|---|---|
| 1 输入 | 无 SwRS 仍开跑 | 历史 SwAD 标成 source |
| 2 清单 | 静默跳过解析失败 | 参考组件 / 接口进 inventory 事实字段 |
| 3 索引 | SwRS / 接口无索引无 gap | 历史 SwAD 进 topic_index 事实条目 |
| 4 大纲 | 无材料却标 complete | 参考内容进大纲正文 |
| 5 计划 | 无证据标 supported | 历史 SwAD 作 required_evidence |
| 6 证据 | 编造 citation | sample 进 matrix |
| 9 草稿 | 静默填分配 / 接口方向 / 资源预算 | 参考措辞无 EVD 进表 |
| 10 审查 | open 被掩盖 | 缺 Δ-Analysis；参考当事实 |
| 11 验证 | 静默填值 | T4 支撑 critical claim |
| 12 修订 | 无证据关 P0 | 用参考关 P0 |
| 13 交付 | 越权批准措辞 | 交付未声明参考边界 |

**一句话**：From-Scratch 查输入够不够、gap 是否诚实；With-Reference 查历史 SwAD 是否被当事实，并全程保留 Δ-Analysis 与 TASK-DIFF。
