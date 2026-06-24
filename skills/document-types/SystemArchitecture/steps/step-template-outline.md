# System Architecture 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

### 阶段 A · L1

- 读 task_brief、System Architecture template（T2）、sample architecture doc（T4，仅形状）。
- 产出 `outline_l1.md` + `template_structure.json`。
- **不写** 正文；**不含** HARA/FSR/TSC/SwRS 章。

### 阶段 B · L2

- SEC-REQTRACE：上游需求摘要表
- SEC-LARCH / SEC-PARCH：逻辑架构与物理架构小节
- SEC-ELEM：架构元素清单表
- SEC-IF：接口架构表（**含方向列**）
- SEC-ALLOC：需求到元素分配矩阵
- SEC-DIAG / SEC-RES：诊断/降级架构、资源约束
- 缺口 L2 标 `evidence: pending`

## System Architecture 方法论（本步定位）

本步对应 **阶段 2：定大纲（先 L1，后 L2）**——落实 ASPICE SYS.3 与控制器系统架构文档的典型结构。

### 报告建议结构（章节）

| 章节 | 内容要点 | 标准关联 |
|---|---|---|
| 文档目的与范围 | 读者、适用 ECU、**不含 HARA/TSC/SwRS 终稿/批准** | SYS.3 |
| 输入材料与假设 | 输入清单、source 边界 | 可追溯 |
| 产品上下文与边界 | ECU 上下文、变型、内外边界 | SYS.3 |
| 上游需求摘要 | SyRS requirement 入口 | SYS.3 上游接口 |
| 逻辑架构 | 功能块、职责、数据流 | SYS.3 |
| 物理/技术架构 | 模块、平台、网络、约束 | SYS.3 |
| 架构元素清单 | 元素 ID、职责、边界 | SYS.3 |
| 接口架构 | 对端、方向、协议、边界 | SYS.3 |
| 分配矩阵 | Requirement → Element | SYS.3 / trace |
| 诊断与降级架构 | 故障链路、降级路径 | 系统层接口 |
| 资源与平台约束 | CPU/内存/总线/时序约束 | 设计约束 |
| 安全相关架构约束 | **引用** FSR/TSC 约束，非新分析 | ISO 26262 接口 |
| 验证方法候选 | 建议验证方式 | 评审 / 验证 |
| 假设、限制与开放确认 | 缺口、NEEDS_USER_CONFIRMATION | — |
| 审查摘要 | 非专业批准 | — |

### 强制 L1（section_id）

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-CONTEXT | 产品/系统上下文与边界 | ★ |
| SEC-REQTRACE | 上游需求摘要与架构入口 | ★ |
| SEC-LARCH | 逻辑架构 | ★ |
| SEC-PARCH | 物理/技术架构 | ★ |
| SEC-ELEM | 架构元素清单 | ★ |
| SEC-IF | 接口架构与边界 | ★ |
| SEC-ALLOC | 需求到架构元素分配矩阵 | ★ |
| SEC-DIAG | 诊断、降级与故障处理架构 | ★ |
| SEC-RES | 资源与平台约束 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-ASSUMP | 假设与依赖 | ★ |
| SEC-REVIEW | 审查总结 | ★ |

### 架构元素表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| ELEM ID | 唯一标识 |
| Element name | 元素名称 |
| Type | Logical / Physical / External |
| Responsibility | 职责摘要 |
| Boundary | In scope / External / Shared |
| Linked requirements | 关联 SYS-F / SYS-IF / 约束 |
| Evidence source | T0/T1 来源 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### 接口架构表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| IF-ARCH ID | 唯一标识 |
| Interface name | 接口名称 |
| Type | Signal / Network / Mechanical / Power / HMI |
| **Direction** | In / Out / Bidirectional（**强制**） |
| Counterpart | 对端元素 / ECU / 外部实体 |
| Protocol / medium | CAN / LIN / Eth / ADC / PWM 等 |
| Linked elements | 关联元素 |
| Linked requirements | 关联上游需求 |
| Evidence source | T0/T1 来源 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### 分配矩阵建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| Upstream requirement ID | SyRS / requirement ID |
| Architecture element ID | 分配到的元素 |
| Allocation type | Primary / Supporting / Shared |
| Rationale | 分配理由 |
| Interface impact | 相关接口（可空） |
| Status | confirmed / NEEDS_USER_CONFIRMATION |

## 本步 Review / Checklist 要点

### 通用 Checklist

- [ ] 强制 L1 齐全：SCOPE、INPUT、CONTEXT、REQTRACE、LARCH、PARCH、ELEM、IF、ALLOC、DIAG、RES、VERIF、ASSUMP、REVIEW
- [ ] 架构元素表、接口表、分配矩阵表列完整
- [ ] **无 HARA / ASIL / SG / TSR / TSC / SwRS** L1/L2
- [ ] 缺口 L2 标 `evidence: pending`
- [ ] **With-Reference**：L1 含 **SEC-DIFF**

### From-Scratch 专属 Checklist

- [ ] 无材料 L2 不得标 complete
- [ ] 分配矩阵可大面积 pending，但列定义必须完整

### With-Reference 专属 Checklist

- [ ] 参考架构内容不得进入大纲正文
- [ ] SEC-DIFF 表列完整，且仅作差异槽位，不写事实正文

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 大纲完整性 | 无材料 L2 不得标 complete | 形状可借参考，但正文槽位 pending |
| IF Direction | 强制列存在 | 同上；不得继承参考架构方向数据 |
| SEC-SAFE-ARCH | 通常 open | 不得抄参考安全架构内容 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 大纲含 HARA/ASIL/SG/TSR 章 | 文档类型漂移 |
| 接口架构表无 Direction 列 | 后续分配/集成困难 |
| 参考架构内容抄进大纲正文 | 事实来源违规 |

## A1 / A2 / B

**A1**：L1 覆盖 SYS.3 核心章；无 HARA/TSC；元素/接口/分配表列完整；With-Reference 含 SEC-DIFF。  
**A2**：补 L2、对齐 JSON/outline、修正缺列。  
**B**：三 artifact 一致；sample 未升格事实。
