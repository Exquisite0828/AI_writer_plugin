# TSC 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

### 阶段 A · L1

- 读 task_brief、TSC template（T2）、sample TSC（T4，仅形状）。
- 产出 `outline_l1.md` + `template_structure.json`。
- **不写** TSC 正文；**不含** HSC/SSC 章。

### 阶段 B · L2

- SEC-SG：SG 列表；HE→SG 追溯表（若有）
- SEC-FSR：FSR-xx 上游追溯摘要
- SEC-ARCH：架构元素清单
- SEC-TSR：TSR-xx 需求表
- SEC-MECH：安全机制表
- SEC-FAULT：故障检测与处理表
- SEC-TRACE：追溯矩阵
- 缺口 L2 标 `evidence: pending`

## TSC 方法论（本步定位）

本步对应 **阶段 2：定大纲（先 L1，后 L2）**——落实 ISO 26262 Clause 8 典型内容结构（4.1–4.11）。

### 报告典型内容结构（ISO 26262 逻辑）

#### 4.1 文档元信息与范围（SEC-DOC、SEC-SCOPE）

- 文档标识、版本、适用 Item、读者对象
- **明确声明**：本文是技术安全概念，**不是** FSR 批准书，**不是**最终系统设计 sign-off

#### 4.2 参考与输入追溯（SEC-INPUT）

- 引用的 FSC/FSR、Item 定义、HARA、架构文档
- 输入版本与变更记录

#### 4.3 系统架构概述（SEC-ARCH）

- 功能架构 / 技术架构框图
- **安全相关元素清单**（传感器、控制器、执行器、通信、电源、看门狗等）
- 外部接口与依赖（其他 ECU、驾驶员、环境）

#### 4.4 技术安全需求 TSR（SEC-TSR）— 核心交付物

**写法要点**：TSR 应是「技术可实现、可验证」的陈述（故障检测覆盖率、冗余策略、诊断周期上限、安全关断路径等），**而不是重复 FSR 的功能表述**。

#### 4.5 安全机制（SEC-MECH）

对每个关键 SG，大纲须预留：检测什么故障 → 如何检测 → 检测后如何处理 → 机制落点 → 与 FTTI 关系。

#### 4.6 故障检测与处理（SEC-FAULT）

- FDTI（故障检测时间间隔）概念
- FHTI（故障处理时间间隔）概念
- 端到端 FTTI 是否满足（表格化，非 prose 隐含）
- 安全状态定义表（与 HARA/FSC 一致或显式说明差异）

#### 4.7 警告与降级（SEC-DEGRADE）

- 驾驶员可感知警告（HMI）策略
- 降级模式层级（limp-home、功能受限、停车等）
- 各模式与 SG/FSR 对应关系

#### 4.8 接口安全需求（SEC-IFACE，概要）

- HW-SW：诊断引脚、安全关断、冗余通道映射
- SW-SW：关键信号语义、失效值、超时策略
- 系统间：车载网络完整性、E2E 保护需求（概念级）

#### 4.9 ASIL 分解与继承（SEC-ASIL）

- 分解方案（要素、约束、共存规则）
- 各子要素 ASIL 及技术侧满足证据思路
- 未分解项的完整 ASIL 要求

#### 4.10 假设、限制与开放确认（SEC-LIMIT、SEC-OPEN）

- 平台能力假设；待供应商确认项；`NEEDS_USER_CONFIRMATION`

#### 4.11 追溯矩阵（SEC-TRACE）— 核心附件

SG ↔ FSR ↔ TSR ↔ 架构元素 ↔ 安全机制 ↔ 验证方法；**宜作核心附件，非附录摆设**。

### 报告建议结构（章节速查）

| 章节 | 内容要点 |
|---|---|
| 文档目的与范围 | 读者、适用 Item/系统、**不含 HSC/SSC/批准** |
| 输入材料与假设 | 输入清单、source 边界 |
| 系统架构概述 | 安全相关元素、框图引用 |
| Safety Goal 追溯 | SG 列表及上游关系 |
| FSR 上游追溯 | FSR-xx 摘要（**不改写 FSR 事实**） |
| **技术安全需求表 TSR-xx** | **核心交付物** |
| 技术安全机制 | 检测/缓解/安全状态迁移概念 |
| 故障检测与处理 | FDTI/FHTI/FTTI 概念表 |
| 警告与降级策略 | 驾驶员感知与降级层级 |
| 接口安全需求 | HW-SW/SW-SW 概要约束 |
| ASIL 继承与分解 | 每条 TSR 的 ASIL 及理由 |
| 追溯矩阵 | SG↔FSR↔TSR↔架构↔机制 |
| 验证方法候选 | 建议验证方式，待 HITL |
| 假设、限制与开放确认 | 缺口、`NEEDS_USER_CONFIRMATION` |
| 审查摘要 / Final review boundary | 非专业批准 |

### 强制 L1（section_id）

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-ARCH | 系统架构概述（安全视角） | ★ |
| SEC-SG | Safety Goal 追溯 | ★ |
| SEC-FSR | FSR 上游追溯摘要 | ★ |
| SEC-TSR | 技术安全需求 TSR-xx | ★ |
| SEC-MECH | 技术安全机制 | ★ |
| SEC-FAULT | 故障检测与处理概念 | ★ |
| SEC-DEGRADE | 警告与降级策略 | ★ |
| SEC-IFACE | 接口安全需求（概要） | ★ |
| SEC-ASIL | ASIL 继承与分解 | ★ |
| SEC-TRACE | 追溯矩阵 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-LIMIT | 假设、限制与开放确认 | ★ |
| SEC-REVIEW | 审查总结 | ★ |

### TSR 需求表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| TSR ID | 唯一标识 |
| Requirement statement | 具体、可验证技术层表述 |
| Linked FSR | 关联 FSR ID |
| Linked safety goal | 关联 SG ID |
| Architecture allocation | 分配到的架构元素 |
| ASIL | 继承/分解后等级 |
| Rationale | 派生/分配理由 |
| Verification method | 验证方法候选 |
| Evidence source | T0/T1 来源 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### 安全机制表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| Mechanism ID | 唯一标识 |
| Linked TSR / SG | 支撑的 TSR 或 SG |
| Fault / hazard context | 针对的故障或场景（来自 source） |
| Detection concept | 检测概念 |
| Reaction concept | 处理/迁移概念 |
| Allocation | 机制落点（架构元素） |
| FTTI relevance | 与 FTTI 关系；检测+处理 ≤ FTTI 或 open |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### 故障处理表建议列（SEC-FAULT L2）

| 列 | 说明 |
|---|---|
| Fault context | 故障或场景（来自 source） |
| FDTI concept | 检测时间概念 |
| FHTI concept | 处理时间概念 |
| FTTI | 来自 HARA 摘要或 open |
| FTTI satisfied | 候选 / open（**禁止**静默「已满足」） |
| Safe state | 与 HARA/SG 一致或记录差异 |
| Linked TSR / Mechanism | 追溯 |

**禁止**：HSC/SSC 终稿、详细电路/代码实现 L1/L2。

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 强制 L1 齐全：SCOPE、INPUT、ARCH、SG、FSR、TSR、MECH、FAULT、DEGRADE、IFACE、ASIL、TRACE、VERIF、LIMIT、REVIEW
- [ ] TSR 表 L2 含：TSR ID、表述、Linked FSR、Linked SG、Allocation、ASIL、Verification、Source、Status
- [ ] 机制表 L2 含：Mechanism ID、Linked TSR/SG、Detection、Reaction、Allocation、Status
- [ ] **无 HSC/SSC** L1/L2
- [ ] 缺口 L2 标 `evidence: pending`
- [ ] **With-Reference**：L1 含 **「与参考 TSC 的差异（Δ-Analysis）」**（建议 SEC-DIFF）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 无材料 L2 不得标 complete | 大纲形状可参考 sample，正文槽位仍 pending 直到有 EVD |
| TSR 表必须有 Linked FSR 与 SG 列 | Δ-Analysis L2：结构/粒度差异，**非 TSR 事实** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 无材料却标 complete | 参考内容进大纲正文 |
| 额外章节 | 无 | SEC-DIFF / Δ-Analysis |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 大纲含 HSC/SSC 章 | 文档类型漂移 |
| TSR 表无 FSR/SG 链接列 | 追溯不可审查 |
| 参考 TSC 内容抄进大纲正文 | 事实来源违规 |

## A1 / A2 / B

**A1**：L1 覆盖 Clause 8 TSC 章；无 HSC/SSC；TSR/机制表列完整。  
**A2**：补 L2、对齐 JSON/outline。  
**B**：三 artifact 一致；sample 未升格事实。
