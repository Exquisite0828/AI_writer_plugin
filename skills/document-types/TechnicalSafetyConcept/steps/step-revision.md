# TSC 子 skill · Step 10 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 依 Step 8/9 findings 修订 → `revised/full_draft.md`、`change_log.md`。
- 不新增无 EVD 支撑的 TSR、机制或 ASIL 结论。

## TSC 方法论（本步定位）

本步对应 **阶段 7–8** 中的 **修订** 环节（定稿前）。

### 阶段 7 · 修订（本步执行，按 P0 优先）

按 P0 优先：

1. **补 FSR/SG 链接**（每条 TSR）
2. **补架构分配**（每条 TSR 或标 open）
3. 修正机制落点与架构不一致
4. 修正 ASIL tier 违规
5. 去除 **HSC/SSC 泄漏**
6. FTTI/验证方法改回「候选」或 open
7. 去除 forbidden / 批准措辞
8. 将 FSR 复述型 TSR 改为技术层表述或标 open
9. 修正架构图与分配表不一致
10. 补全追溯矩阵缺列（架构、机制）
11. 同步 matrix 与 unresolved

### 常见失效模式修订对照

| 失效 | 修订动作 |
|---|---|
| FSR 复述型 TSR | 改为技术表述或标 open |
| 缺机制/故障处理 | 补 SEC-MECH/FAULT 或 gap，不编造 |
| FTTI 静默「已满足」 | 改候选/open + 表格化 FDTI/FHTI |
| 安全状态与 HARA 矛盾 | 对齐或记录差异理由 |

### 修订后仍须满足

- 每条 TSR 链 FSR/SG；有 allocation；无 HSC/SSC；无 forbidden claims
- `NEEDS_USER_CONFIRMATION` 未静默消除

## 本步 Review / Checklist 要点

### 修订 Checklist

- [ ] **P0**：补 FSR/SG 链接、补 allocation、去 HSC/SSC、去 forbidden、修正 tier
- [ ] 机制落点与架构一致或标 open
- [ ] FTTI/验证方法过度断言改回候选/open
- [ ] **未新增**无 EVD 的 TSR/机制
- [ ] `change_log` 追溯 issue id
- [ ] **With-Reference**：修订**不得**用参考 TSC「关 P0」

### 本步 Review 要点

修订后仍须满足 **Step 8** 的 Clause 8 / TSC Checklist。

| From-Scratch | With-Reference |
|---|---|
| 为关 P0 无证据补全 TSR/机制 → P0 | 用参考 TSC 闭合 open → P0 |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 无证据关 P0 | 用参考关 P0 |

### 常见 P0（修订时）

| 错误 | 后果 |
|---|---|
| 为关 P0 无证据补全 TSR/机制 | 不可追溯 |
| 修订引入 HSC/SSC | 文档类型漂移 |
| 静默删除 open | HITL 失效 |

## A1 / A2 / B

**A1**：P0 已关闭或显式 open；无 HSC/SSC；无 forbidden claims。  
**A2**：重跑未关闭项。  
**B**：修订可追溯。
