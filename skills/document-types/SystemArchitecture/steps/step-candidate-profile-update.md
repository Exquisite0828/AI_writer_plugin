# System Architecture 子 skill · Step 15 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`、`promotion_report.md`。
- 状态 **`proposed` / `inactive`**。
- **不得**把本次 run 的元素/接口/分配/资源值写入通用 profile。

## System Architecture 方法论（本步定位）

从本次 run 提炼 **可复用流程/checklist 信号**，不固化项目事实。

## 本步 Review / Checklist 要点

### 可提案 / 禁止内容矩阵

| 可提案信号 | 禁止内容 |
|---|---|
| 元素表列、接口 Direction 列、分配矩阵列 | 具体项目元素名 / 接口名 |
| requirement → element 追溯检查项 | 本项目 SyRS ID → 元素映射 |
| 逻辑-物理一致性检查 | 本项目平台架构事实 |
| forbidden claims 扫描规则 | 参考架构文档事实写入 profile |
| With-Reference：SEC-DIFF 列定义、Δ-Analysis 方法学 | 本次 Δ 具体内容 |

### 通用 Checklist

- [ ] candidate `active: false`
- [ ] patch **仅**流程/checklist（元素表列、Direction、分配、边界检查等）
- [ ] **禁止**写入本项目元素/接口/资源值
- [ ] With-Reference：Δ-Analysis 方法学可写；Δ 具体内容不可写

### From-Scratch 专属 Checklist

- [ ] 信号偏向"输入完备性""Direction 列""分配 rationale""HARA 泄漏防护"

### With-Reference 专属 Checklist

- [ ] 可提案：SEC-DIFF 强制、参考边界声明模板、sample 升格 source 防护
- [ ] **禁止**：本次具体差异条目、客户"沿用 / 取消"判断

### 常见 P0

| 错误 | 后果 |
|---|---|
| 把本项目元素/接口/资源写入 candidate | 项目事实泄漏 |
| candidate `active: true` | 越权启用 |
| patch 含 HARA / ASIL / SG / TSR 模板 | 文档边界破坏 |
| patch 含本次 Δ 具体差异 | 项目事实泄漏 |

## A1 / A2 / B

**A1**：candidate `active: false` 且 `status: proposed`；无项目事实泄漏。  
**A2**：收紧 patch 范围；删去具体事实。  
**B**：promotion_report 须人工审查后启用；候选只补强流程/checklist，不替代项目事实。
