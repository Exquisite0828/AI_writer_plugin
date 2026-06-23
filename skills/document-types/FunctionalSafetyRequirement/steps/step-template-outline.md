# FSR 子 skill · Step 4 · 模板大纲

骨架：`skills/workflow-steps/step-template-outline/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

### 阶段 A · L1

- 读 task_brief、FSR template（T2）、sample FSR（T4，仅形状）。
- 产出 `outline_l1.md` + `template_structure.json`。
- **不写** FSR 正文；**不含** TSC 章。

### 阶段 B · L2

- SEC-SG：SG 列表；HE→SG 追溯表（若有）
- SEC-FSR：FSR-xx 需求表
- SEC-ASIL：ASIL 继承说明
- SEC-VERIF：验证方法汇总
- 缺口 L2 标 `evidence: pending`

## FSR 方法论（本步定位）

本步对应 **阶段 2：定大纲（先 L1，后 L2）**。

### 报告建议结构（章节）

| 章节 | 内容要点 |
|---|---|
| 文档目的与范围 | 读者、适用 Item、**不含 TSC/批准** |
| 输入材料与假设 | 输入清单、source 边界 |
| Item 定义摘要 | 引用 IDD 上下文（非完整 IDD） |
| 安全目标追溯 | SG 列表及 HARA 追溯关系 |
| **功能安全需求表 FSR-xx** | **核心交付物** |
| ASIL 继承与理由 | 每条 FSR 的 ASIL 及继承说明 |
| 验证方法候选 | 建议验证方式，待 HITL |
| 假设、限制与开放确认 | 缺口、`NEEDS_USER_CONFIRMATION` |
| 审查摘要 / Final review boundary | 非专业批准 |

### 强制 L1（section_id）

| section_id | 标题 | 强制 |
|---|---|:---:|
| SEC-SCOPE | 目的、范围与读者 | ★ |
| SEC-INPUT | 输入材料与 source 边界 | ★ |
| SEC-ITEM | Item 定义摘要 | ★ |
| SEC-SG | Safety Goal 追溯 | ★ |
| SEC-FSR | 功能安全需求 FSR-xx | ★ |
| SEC-ASIL | ASIL 继承与理由 | ★ |
| SEC-VERIF | 验证方法候选 | ★ |
| SEC-LIMIT | 假设、限制与开放确认 | ★ |
| SEC-REVIEW | 审查总结 | ★ |

### FSR 需求表建议列（L2 须定义）

| 列 | 说明 |
|---|---|
| FSR ID | 唯一标识 |
| Requirement statement | 具体、可验证表述 |
| Linked safety goal | 关联 SG ID |
| ASIL | 继承自 SG |
| Rationale | 追溯/分解理由 |
| Verification method | 验证方法候选 |
| Evidence source | T0/T1 来源 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

**禁止**：TSC、技术安全机制、技术安全需求 L1/L2。

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] 强制 L1 齐全：SCOPE、INPUT、ITEM、SG、FSR、ASIL、VERIF、LIMIT、REVIEW
- [ ] FSR 表 L2 含：FSR ID、表述、Linked SG、ASIL、Rationale、Verification、Source、Status
- [ ] **无 TSC** L1/L2
- [ ] 缺口 L2 标 `evidence: pending`
- [ ] **With-Reference**：L1 含 **「与参考 FSR 的差异（Δ-Analysis）」**（建议 SEC-DIFF）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 无材料 L2 不得标 complete | 大纲形状可参考 sample，正文槽位仍 pending 直到有 EVD |
| FSR 表必须有 Linked SG 列 | Δ-Analysis L2：结构/粒度差异，**非需求事实** |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 无材料却标 complete | 参考内容进大纲正文 |
| 额外章节 | 无 | SEC-DIFF / Δ-Analysis |

### 常见 P0

| 错误 | 后果 |
|---|---|
| 大纲含 TSC 章 | 文档类型漂移 |
| FSR 表无 SG 链接列 | 追溯不可审查 |
| 参考 FSR 内容抄进大纲正文 | 事实来源违规 |

## A1 / A2 / B

**A1**：L1 覆盖 FSC/FSR 章；无 TSC；FSR 表列完整。  
**A2**：补 L2、对齐 JSON/outline。  
**B**：三 artifact 一致；sample 未升格事实。
