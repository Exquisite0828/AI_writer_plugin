# FSR 子 skill · Step 13 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`、`promotion_report.md`。
- 状态 **`proposed` / `inactive`**。
- **不得**把本次 run 的 FSR/SG/ASIL 写入通用 profile。

## FSR 方法论（本步定位）

从本次 run 提炼 **可复用流程/checklist 信号**，不固化项目事实。

### 可提炼信号（§7 相关）

| 信号 | 可提案 | Clause/规则 |
|---|---|---|
| SG 链接列强制 | FSR 表 Linked SG 列 | 追溯 |
| ASIL 来源检查 | checklist 增强 | ASIL 继承 |
| TSC 防泄漏 | 草稿扫描项 | FSR 不写 TSC |
| 验证方法「候选」默认 | writing_mode 提醒 | 验证 |
| HARA 摘要边界 | 非 blanket 批准提醒 | 批准边界 |
| sample 勿升格 | tier 提醒 | 事实来源 |

### FSR 写作核心原则（patch 可引用）

1. **FSR ≠ TSC**
2. **FSR ≠ 新 HARA**（摘要不 blanket 批准）
3. **sample 不作 fact source**
4. **每条 FSR 链 SG**
5. **review-ready ≠ sign-off**

### 与 IDD 关系（流程说明可含）

- IDD 为 FSR 上游 Item 上下文；候选 patch **不得**混入 IDD 的 F-xx/边界事实。

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] candidate **`active: false`**
- [ ] patch **仅**流程/checklist（SG 链接列、TSC 防泄漏等）
- [ ] **禁止**写入本项目 FSR/SG/ASIL 值

| 可提案 | 禁止 |
|---|---|
| FSR 表列、SG 追溯检查项 | 具体项目 FSR 措辞 |
| TSC 防泄漏 checklist | sample 需求复用 |
| 验证方法候选提醒 | 「本项目 SG-01 为…」 |
| Forbidden claims 扫描规则 | 参考 FSR 事实写入 profile |
| With-Reference：Δ-Analysis / 参考边界 checklist | hazard 模板渗入 FSR |

## A1 / A2 / B

**A1**：candidate `active: false`；无项目事实泄漏。  
**A2**：收紧 patch 范围。  
**B**：promotion_report 须人工审查后启用。
