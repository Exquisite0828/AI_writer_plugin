# TSC 子 skill · Step 7 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 成稿 → `draft/full_draft.md`。
- 只用 `allowed_evidence`；核对 L1→L2→L3→原文。
- **禁止**：HSC/SSC 终稿、详细实现、新 HARA、批准/合规措辞。

## TSC 方法论（本步定位）

本步对应 **阶段 3–6 的成稿环**：FSR→TSR 派生、安全机制与故障处理设计、接口与 ASIL、追溯矩阵的 **保守撰写**。

### 阶段 3 · FSR→TSR 派生（本步成稿执行）

对每条 FSR 执行（与 Step 5 计划一致）：

1. **理解 FSR 意图** → 对应 SG、约束类型
2. **识别技术触点** → 传感器/执行器/算法/通信
3. **写出 TSR** → 技术可实现、可验证；**非 FSR 原句复述**
4. **检查可验证性** → 验证方法候选或 open
5. **记录追溯** → FSR-xx → TSR-yy；无法派生 → `NEEDS_USER_CONFIRMATION`

**常见派生示例**：

- FSR「应检测 X 失效」→ TSR「应在 ≤t ms 内检测…」+ SEC-MECH 机制行
- FSR「应进入安全状态」→ TSR「关断路径/降级条件」+ SEC-FAULT 安全状态表
- FSR「应通知驾驶员」→ TSR「HMI 警告触发条件与优先级」+ SEC-DEGRADE

### 阶段 4 · 安全机制与故障处理（本步成稿）

按 **SG / 危害场景** 组织 SEC-MECH、SEC-FAULT，对每个场景回答：

| 问题 | 成稿要求 |
|---|---|
| 可能发生什么故障？ | 来自 source 或 open |
| 故障如何被检测？ | Detection concept + Allocation |
| 检测后什么状态？ | Reaction concept + Safe state |
| 是否在 FTTI 内？ | FDTI+FHTI ≤ FTTI 或 open（**表格化**） |
| 驾驶员是否被警告？ | SEC-DEGRADE 链接 |

### 阶段 5 · 接口与 ASIL（本步成稿）

- **SEC-IFACE**：HW-SW（诊断引脚、安全关断、冗余映射）；SW-SW（失效值、超时）；系统间（E2E 概念级）
- **SEC-ASIL**：分解方案、约束、各子要素 ASIL；无 source → open

### 阶段 6 · 追溯矩阵（本步成稿）

SEC-TRACE 须覆盖：**SG ↔ FSR ↔ TSR ↔ 架构元素 ↔ 安全机制 ↔ 验证方法**（核心附件，非摆设）。

### 阶段 5 · 撰写（章节写法）

| 节 | 写法要点 |
|---|---|
| SEC-ARCH | 架构元素清单；安全相关元素标注；与 source 一致或 open |
| SEC-SG | SG 列表；HE→SG（仅 HARA 摘要显式内容） |
| SEC-FSR | FSR-xx 上游摘要；**不改写 FSR 事实** |
| SEC-TSR | 每条 TSR：技术层可验证表述、**Linked FSR/SG**、**Architecture allocation**、ASIL 有来源 |
| SEC-MECH | 机制：检测概念、反应概念、落点；链 TSR/SG |
| SEC-FAULT | FDTI/FHTI/FTTI 概念；有 HARA 来源或 open |
| SEC-DEGRADE | 警告与降级；与 SG 安全状态一致或说明差异 |
| SEC-IFACE | HW-SW/SW-SW 概要约束；非详细接口规格 |
| SEC-TRACE | SG↔FSR↔TSR↔架构↔机制矩阵 |
| SEC-ASIL | 继承/分解理由；不擅自分解除非 source/HITL |
| SEC-VERIF | 验证方法标 **候选** 或 open |

### 成功标准（成稿视角）

- 每条 TSR 有唯一 ID，且追溯到 source 中 FSR 与 SG（或 open）。
- 架构分配与机制落点一致或可解释 open。
- ASIL 来自 source 或 HITL，无 sample/reference 支撑。
- FTTI 相关主张有 HARA 摘要或 HITL，非静默「已满足」。
- 验证方法标候选/待确认，除非 source/HITL 明确支持。
- **无 HSC/SSC**；无 forbidden final claims。

### TSR 表字段（成稿必查）

| 列 | 通过条件 |
|---|---|
| TSR ID | 唯一 |
| Requirement statement | 技术层、可验证；非 FSR 原句复述 |
| Linked FSR | 至少一个 FSR ID 或 open |
| Linked SG | 至少一个 SG ID 或 open |
| Architecture allocation | 有架构元素或 open |
| ASIL | 来自 SG/FSR source 或 HITL |
| Verification method | 候选或已确认，非静默「已充分」 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### 常见失效模式（本步成稿时警惕）

| 失效 | 本步防法 |
|---|---|
| FSR 原句复制为 TSR | 改写为技术层表述或标 open |
| 只有 TSR 表无机制/故障处理 | 补 SEC-MECH、SEC-FAULT 或 gap |
| 架构图与分配表不一致 | 对齐 SEC-ARCH 与 TSR Allocation |
| 安全状态与 HARA 不一致无说明 | SEC-FAULT 记录差异或 open |
| FTTI 隐含在 prose | 改为 FDTI/FHTI/FTTI 表 |

### 重要边界

- **TSC ≠ FSR 复述**
- **TSC ≠ HSC/SSC**
- **TSC ≠ 新 HARA**
- **禁止**：TSC approved、complete and compliant、ASIL validated、FTTI fully met 等

## 本步 Review / Checklist 要点

### 成稿自检 Checklist

- [ ] 每条 TSR 有唯一 ID + Linked FSR/SG（或 open）
- [ ] 每条 TSR 有 Architecture allocation（或 open）
- [ ] 机制表与 TSR/架构落点一致或可解释 open
- [ ] ASIL 来自 source/HITL
- [ ] FTTI 主张有来源或 open
- [ ] Verification 标 **候选** 或 open
- [ ] **无 HSC/SSC**、无新 HARA 危害表
- [ ] 无 forbidden claims
- [ ] **With-Reference**：含 **「与参考 TSC 的差异」** 节，且有**具体差异点**

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 大量 `[PENDING]` / `NEEDS_USER_CONFIRMATION` 正常 | 参考 TSC 措辞**不能**出现在 TSR/机制表除非有本项目 EVD |
| 不超出 `allowed_evidence` | Δ 节说明：哪些节沿用结构、哪些需求来自本项目 FSR |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 静默填 TSR/机制 | 参考措辞无 EVD 进表 |

### 常见 P0

| 错误 | 后果 |
|---|---|
| TSR 无 FSR 却标 confirmed | 不可追溯 |
| TSR 仅为 FSR 换措辞 | Clause 8 精神不满足 |
| 含 HSC/SSC 详细实现 | 文档类型漂移 |
| 写「已批准/已合规」 | 越权结论 |
| 参考 TSC 内容无 EVD 写入正文 | 事实来源违规 |

## A1 / A2 / B

**A1**：无超出证据表述；无 HSC/SSC/HARA 泄漏；每条 TSR 有 FSR/SG/分配列。  
**A2**：按 TASK 重跑缺证据节。  
**B**：无 forbidden final claims。
