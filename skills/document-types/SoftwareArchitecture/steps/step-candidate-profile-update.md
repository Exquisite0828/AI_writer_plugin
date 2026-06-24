# Software Architecture 子 skill · Step 15 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`、`promotion_report.md`。
- 状态 **`proposed` / `inactive`**（`active: false`）。
- 从本次 run 提炼 **可复用流程/checklist**，不固化项目架构事实。

## Software Architecture 方法论（本步定位）

### 15.1 本步在八阶段方法链中的位置

本步对应 **阶段 8：追溯与学习** 的 **候选改进输出**。

**方法原则**：candidate 是「下次写 SwAD 时更好的检查单」，不是「上次项目的架构答案」。须人工审查后才可 promotion。

### 15.2 阶段 8 · 候选提炼方法

#### 从 run 信号到 candidate 的映射

| run 信号 | 可提案到 candidate |
|---|---|
| direction_missing_dense | 强化 SEC-IF Direction 列 VC 规则 |
| reference_misuse_risk | 增 sample 升格 source 防护检查 |
| swrs_gap_dense | Step 1 SwRS 最低输入门槛 |
| alloc_open_dense | SEC-ALLOC rationale 必填规则 |
| safe_arch_leakage | SEC-SAFE-ARCH 引用边界扫描词表 |

#### 可提案 / 禁止内容矩阵

| 可提案 | 禁止 |
|---|---|
| 组件表列、接口 Direction 列、分配矩阵列定义 | 具体 SWA-COMP 名 |
| SwRS→component 追溯检查项 | 本项目 SWR-F→组件映射 |
| App/RTE/BSW/OS 分层检查项 | 本项目 BSW 配置事实 |
| forbidden claims 扫描规则 | 历史 SwAD 事实 |
| With-Reference：SEC-DIFF 列、Δ 方法学 | 本次 Δ 具体内容 |
| From-Scratch：open 密度预期说明 | 本次 open 的具体值 |

#### From-Scratch 候选侧重

- 输入完备性门槛（SwRS + 当前项目架构 + 接口规范）。
- Direction / 分配 rationale / 资源单位 机器规则。
- HARA / 详细设计 / 代码 泄漏词表。

#### With-Reference 候选侧重

- SEC-DIFF 强制与四类 Δ 检查。
- 参考边界声明模板（delivery_summary 用）。
- evidence_map 中 sample file_id 检测规则。
- 「沿用参考」HITL 流程模板。

### 15.3 promotion 边界

- `promotion_report.md` 须列明：提案范围、未包含项、需人工确认点。
- **禁止** auto-promotion；`active` 必须保持 `false` 直至人工批准。

## 本步 Review / Checklist 要点

### candidate 产出 Checklist（8 项）

- [ ] `candidate_profile_update.yaml` 存在
- [ ] `candidate_skill_patch.md` 存在
- [ ] `promotion_report.md` 存在
- [ ] `active: false`
- [ ] `status: proposed`
- [ ] patch 范围在 promotion_report 中声明
- [ ] 无 auto-promotion 语句
- [ ] 无本项目 SWA-COMP/IF/资源具体值

### 可提案 / 禁止 Review 矩阵

| 可提案到 candidate | 禁止写入 |
|---|---|
| 组件/接口/分配表列定义 | 具体组件名、接口名 |
| Direction、R-TRACE 机器规则 | 本项目任务周期、内存值 |
| SWE.2 BP 检查项模板（通用） | 本项目 SwRS→组件映射 |
| forbidden claims 扫描词表 | 历史 SwAD 事实 |
| SEC-DIFF 列定义、Δ 方法学 | 本次 Δ 具体条目 |
| From-Scratch 输入完备性门槛 | 本次 open 的具体值 |
| With-Reference 参考边界声明模板 | 客户「沿用/取消」判断 |
| AUTOSAR 分层检查项（通用） | 本项目 BSW 配置 |

### From-Scratch 候选信号 Checklist

- [ ] 若 `swrs_gap_dense` → 提案 SwRS 最低输入门槛
- [ ] 若 `direction_missing_dense` → 提案 SEC-IF Direction VC 强化
- [ ] 若 `resource_pending_dense` → 提案 SEC-RES 单位检查
- [ ] 含 open 密度预期说明（非本次数值）
- [ ] 含 HARA/详细设计泄漏词表防护

### With-Reference 候选信号 Checklist

- [ ] 若 `reference_misuse_risk` → 提案 sample 升格 source 防护
- [ ] 提案 SEC-DIFF 强制与四类 Δ 检查
- [ ] 提案 delivery 参考边界声明模板
- [ ] 提案 evidence_map 中 sample file_id 检测
- [ ] **无**本次具体 Δ 条目或客户决策

### ISO 26262 / 功能安全边界 Checklist

- [ ] patch **不含** ASIL/TSR/HARA 分析模板
- [ ] 可含「SEC-SAFE-ARCH 仅引用」扫描规则
- [ ] 不含安全机制设计 checklist

### 本步 Review 要点

| 维度 | 通过条件 |
|---|---|
| 范围 | 仅流程/checklist，无架构事实 |
| 状态 | active=false，proposed |
| 可追溯 | promotion_report 说明提案来源 signal |
| 安全 | 无安全分析模板泄漏 |

### P0 失效项

| 错误 | 后果 |
|---|---|
| 本项目组件/接口/资源写入 candidate | 事实泄漏 |
| `active: true` | 越权启用 |
| patch 含 ASIL/TSR/详细设计模板 | 边界破坏 |
| patch 含本次 Δ 具体内容 | 项目泄漏 |

### 一句话归纳

**Checklist 核心**：candidate 三文件齐全、active=false、patch 仅流程、无项目事实。  
**Review 核心**：从 run 信号提炼通用规则；With-Reference 可提案 Δ 方法学但不可写本次 Δ 内容。

## A1 / A2 / B

**A1**：candidate 保守；无事实泄漏。  
**A2**：收紧 patch；删具体事实。  
**B**：promotion 须人工审查；candidate 只改进流程。
