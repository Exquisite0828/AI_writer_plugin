# TSC 子 skill · Step 13 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`、`promotion_report.md`。
- 状态 **`proposed` / `inactive`**。
- **不得**把本次 run 的 TSR/机制/ASIL/架构分配写入通用 profile。

## TSC 方法论（本步定位）

从本次 run 提炼 **可复用流程/checklist 信号**，不固化项目事实。

### 可提炼信号（含常见失效模式 → checklist）

| 信号 | 可提案 | 对应失效模式 |
|---|---|---|
| FSR 非复述检查 | TSR 与 FSR 措辞区分扫描 | FSR 原句复制为 TSR |
| 机制/故障完备性 | SEC-MECH+FAULT 强制检查 | 只有需求表无机制 |
| 架构-分配一致性 | Allocation 与 SEC-ARCH 交叉检查 | 架构图与分配表不一致 |
| 安全状态一致性 | 与 HARA 差异须记录 | 安全状态与 HARA 矛盾 |
| FTTI 表格化提醒 | FDTI/FHTI/FTTI 列强制 | FTTI 隐含 prose |
| ASIL 分解约束检查 | 分解方案与 TSR ASIL 一致 | 忽略 ASIL 分解约束 |

### 可提炼信号（流程）

| 信号 | 可提案 | Clause/规则 |
|---|---|---|
| FSR/SG 链接列强制 | TSR 表 Linked FSR/SG 列 | 追溯 |
| 架构分配列强制 | TSR 表 Architecture allocation 列 | Clause 8 分配 |
| 机制落点检查 | 机制表 Allocation 与 TSR 一致 | 机制一致性 |
| ASIL 来源检查 | checklist 增强 | ASIL 继承/分解 |
| HSC/SSC 防泄漏 | 草稿扫描项 | HSC/SSC deferred |
| FTTI 来源检查 | 故障处理段提醒 | HARA 摘要边界 |
| 验证方法「候选」默认 | writing_mode 提醒 | 验证 |
| sample 勿升格 | tier 提醒 | 事实来源 |

### TSC 写作核心原则（patch 可引用）

1. **TSC ≠ FSR 复述**
2. **TSC ≠ HSC/SSC**
3. **TSC ≠ 新 HARA**（摘要不 blanket 批准）
4. **sample 不作 fact source**
5. **每条 TSR 链 FSR 与 SG**
6. **review-ready ≠ sign-off**

### 与 FSR 关系（流程说明可含）

- FSR 为 TSC 上游；候选 patch **不得**混入 FSR 的 FSR-xx/ASIL 事实。
- TSC 下游为 HSC/SSC；patch **不得**预写 HSC/SSC 内容模板。

## 本步 Review / Checklist 要点

### 本步 Checklist

- [ ] candidate **`active: false`**
- [ ] patch **仅**流程/checklist（TSR 列、追溯、机制一致性、HSC/SSC 防泄漏等）
- [ ] **禁止**写入本项目 TSR/机制/ASIL/架构值

| 可提案 | 禁止 |
|---|---|
| TSR/机制表列、追溯检查项 | 具体项目 TSR 措辞 |
| HSC/SSC 防泄漏 checklist | sample 机制复用 |
| FTTI 来源提醒 | 「本项目 TSR-01 为…」 |
| Forbidden claims 扫描规则 | 参考 TSC 事实写入 profile |
| With-Reference：Δ-Analysis / 参考边界 checklist | 危害/FSR 模板渗入 TSC |

## A1 / A2 / B

**A1**：candidate `active: false`；无项目事实泄漏。  
**A2**：收紧 patch 范围。  
**B**：promotion_report 须人工审查后启用。
