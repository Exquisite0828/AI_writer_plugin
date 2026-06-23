# FSR 子 skill · Step 12 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 依 Step 10/11 findings 修订 → `revised/full_draft.md`、`change_log.md`。
- 不新增无 EVD 支撑的 FSR 或 ASIL 结论。

## FSR 方法论（本步定位）

本步对应 **阶段 7：修订与交付** 中的 **修订** 环节。

### 阶段 7 · 修订（本步执行）

按 P0 优先：

1. **补 SG 链接**（每条 FSR）
2. 修正 ASIL tier 违规
3. 去除 **TSC 泄漏**
4. 验证方法改回「候选」或 open
5. 去除 forbidden / 批准措辞
6. 同步 matrix 与 unresolved

### 修订后仍须满足（§7 Checklist 节选）

- 每条 FSR 链 SG；ASIL 有来源；无 TSC；无 forbidden claims
- `NEEDS_USER_CONFIRMATION` 未静默消除

## 本步 Review / Checklist 要点

### 修订 Checklist

- [ ] **P0**：补 SG 链接、去 TSC、去 forbidden、修正 tier
- [ ] 验证方法过度断言改回候选/open
- [ ] **未新增**无 EVD 的 FSR
- [ ] `change_log` 追溯 issue id
- [ ] **With-Reference**：修订**不得**用参考 FSR「关 P0」

### 本步 Review 要点

修订后仍须满足 **Step 10** 的 11 项 Clause 7 / FSR Checklist。

| From-Scratch | With-Reference |
|---|---|
| 为关 P0 无证据补全 FSR → P0 | 用参考 FSR 闭合 open → P0 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 无证据关 P0 | 用参考关 P0 |

### 常见 P0（修订时）

| 错误 | 后果 |
|---|---|
| 为关 P0 无证据补全 FSR | 不可追溯 |
| 修订引入 TSC | 文档类型漂移 |
| 静默删除 open | HITL 失效 |

## A1 / A2 / B

**A1**：P0 已关闭或显式 open；无 TSC；无 forbidden claims。  
**A2**：重跑未关闭项。  
**B**：修订可追溯。
