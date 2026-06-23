# FSR 子 skill · Step 9 · 保守草稿

骨架：`skills/workflow-steps/step-conservative-draft/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 按 `section_tasks.json` 成稿 → `draft/full_draft.md`。
- 只用 `allowed_evidence`；核对 L1→L2→L3→原文。
- **禁止**：TSC、技术安全机制、新 HARA、批准/合规措辞。

## FSR 方法论（本步定位）

本步对应 **阶段 5：保守成稿**。

### 阶段 5 · 撰写（本步执行）

| 节 | 写法要点 |
|---|---|
| SEC-SG | SG 列表；HE→SG（仅 HARA 摘要显式内容） |
| SEC-FSR | 每条 FSR：表述清晰可验证、**Linked SG**、ASIL 有来源 |
| SEC-ASIL | 继承理由；不擅自分解 ASIL 除非 source/HITL |
| SEC-VERIF | 验证方法标 **候选** 或 open |
| SEC-LIMIT | 假设、限制、open 项 |

### 成功标准（§2.2 成稿视角）

- 每条 FSR 有唯一 ID，且追溯到 source 中 SG（或 open）。
- ASIL 来自 source 或 HITL，无 sample/reference 支撑。
- 验证方法标候选/待确认，除非 source/HITL 明确支持。
- 需求措辞有来源或显式 open。
- **无 TSC**；无 forbidden final claims。

### FSR 表字段（成稿必查）

| 列 | 通过条件 |
|---|---|
| FSR ID | 唯一 |
| Requirement statement | 具体、可验证；无危害新结论 |
| Linked SG | 至少一个 SG ID 或 open |
| ASIL | 来自 SG source 或 HITL |
| Verification method | 候选或已确认，非静默「已充分」 |
| Confirmation status | confirmed / NEEDS_USER_CONFIRMATION |

### 重要边界

- **FSR ≠ TSC**
- **FSR ≠ 新 HARA**
- **禁止**：requirements approved、complete and compliant、ASIL validated 等

## 本步 Review / Checklist 要点

### 成稿自检 Checklist

- [ ] 每条 FSR 有唯一 ID + Linked SG（或 open）
- [ ] ASIL 来自 SG source/HITL
- [ ] Verification 标 **候选** 或 open，非静默「已充分」
- [ ] Item 摘要与 source 一致或 open
- [ ] **无 TSC**、无新 HARA 危害表
- [ ] 无 forbidden claims
- [ ] **With-Reference**：含 **「与参考 FSR 的差异」** 节，且有**具体差异点**（非仅「同参考」）

### 本步 Review 要点

| From-Scratch | With-Reference |
|---|---|
| 大量 `[PENDING]` / `NEEDS_USER_CONFIRMATION` 正常 | 参考 FSR 措辞**不能**出现在 FSR 表除非有本项目 EVD |
| 不超出 `allowed_evidence` | Δ 节说明：哪些节沿用结构、哪些需求来自本项目 SG |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 静默填 FSR/ASIL | 参考措辞无 EVD 进表 |
| 写作模式 | 大量 confirmation_required / placeholder | 更多 conservative_candidate，仍须逐条 EVD |

### 常见 P0

| 错误 | 后果 |
|---|---|
| FSR 无 SG 却标 confirmed | 不可追溯 |
| 含 TSC | 文档类型漂移 |
| 写「已批准/已合规」 | 越权结论 |
| 参考 FSR 内容无 EVD 写入正文 | 事实来源违规 |

## A1 / A2 / B

**A1**：无超出证据表述；无 TSC/HARA 泄漏；每条 FSR 有 SG 列。  
**A2**：按 TASK 重跑缺证据节。  
**B**：无 forbidden final claims。
