# Software Architecture 子 skill · Step 11 · 最终报告

骨架：`skills/workflow-steps/step-final-report/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 打包 `final/final_report.md`、`final/delivery_summary.md`。
- 状态仅允许：`ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation`。
- 明示下游交接边界与 open 项处理规则。

## Software Architecture 方法论（本步定位）

### 11.1 本步在八阶段方法链中的位置

本步对应 **阶段 7 交付** 与 **阶段 8 下游交接** 的 **正式打包**。

**方法原则**：final 包是 **可交接的 review-ready 产物**，不是 sign-off。下游（详细设计、测试）可据此启动，但 **不得**悄悄闭合 open。

### 11.2 阶段 7–8 · 交付与下游交接方法

#### 交付包组成

```text
final_report.md
├─ 文档元信息（类型、版本、状态、非批准声明）
├─ SwAD 正文（revised/full_draft 审定版）
├─ 追溯摘要（SwRS ↔ SWA-COMP ↔ SWA-IF）
├─ Open Items Registry（按 SEC 分类）
├─ 审查/验证摘要（非 sign-off）
└─ 下游交接说明
delivery_summary.md
├─ document_type: SoftwareArchitecture
├─ writing_scenario
├─ 统计：组件数、接口数、分配行数、open 数、HITL 数
├─ gap 按 SEC 分类
└─ 下游接收方列表
```

#### 下游交接物与使用规则

| 交接物 | 下游 | 使用规则 |
|---|---|---|
| 软件组件清单 | 详细设计（SWE.3） | open 组件须先 HITL 再设计 |
| 软件接口表 | 接口实现、RTE 配置 | Direction 为 open 的不得默认实现 |
| 分配矩阵 | 详细设计、软件测试 | orphan SwRS 须追踪 |
| 任务/资源预算 | OS 配置、资源分析 | pending 预算不得当基线 |
| 诊断架构 | 集成测试、Dem 验证 | 链路 open 须先闭合 |
| Open Items Registry | 全部下游 | **禁止静默关闭** |

#### ASPICE SWE.2 交接说明（写入 delivery_summary）

- 本包满足「可追溯候选 SwAD」目标，**不**声明 SWE.2 能力等级。
- 建议人工软件架构评审后再进入详细设计。

#### From-Scratch 交付方法

- `finalized_with_open_items` 为 **常态**。
- delivery_summary 按 SEC 分类列出 gap 与风险。
- Open Items Registry 须完整，与 verify 结果一致。

#### With-Reference 交付方法

- **必须**含「参考边界声明」段：

  > 历史项目 SwAD（file_id: xxx）仅作章节/图表形状参考，未支撑本项目任何 SWA-COMP / SWA-IF / 分配 / 资源事实。下游不得用该参考闭合 open。

- SEC-DIFF 纳入正文。
- 下游说明加：「Δ-Analysis 中标注 Removed/Modified 的项须单独验证」。

### 11.3 状态选择指南

| 状态 | 适用 |
|---|---|
| ready_for_human_review | P0 已清零，open 已登记，可安排评审 |
| finalized_with_open_items | 有已知 open 但可交接（From-Scratch 常见） |
| blocked_pending_confirmation | 存在阻断性 HITL 未决 |

## 本步 Review / Checklist 要点

### final_report 交付 Checklist（14 项）

| # | 检查项 | 通过条件 |
|---|---|---|
| 1 | 文档元信息 | 类型、版本、run_id、状态齐全 |
| 2 | 非批准声明 | 明示非 HARA/TSC/详细设计/正式批准 |
| 3 | source/sample 边界 | 列明各 role 与 tier |
| 4 | writing_scenario | from_scratch / with_reference 与 manifest 一致 |
| 5 | SEC-SWCTX ~ SEC-ALLOC | 核心架构正文章节齐全 |
| 6 | 三表完整 | COMP / IF / ALLOC 表在正文或附录 |
| 7 | SEC-RES / SEC-DIAG | 资源与诊断章有内容或 open |
| 8 | SEC-VERIF | 验证候选存在 |
| 9 | 追溯摘要 | SwRS↔SWA-COMP 摘要可读 |
| 10 | Open Items Registry | 按 SEC 分类，条数与 verify 一致 |
| 11 | 审查摘要 | 来自 Step 8，**非 sign-off** |
| 12 | 验证摘要 | 来自 Step 9，状态保守 |
| 13 | 下游交接说明 | 列明详细设计/测试/静态分析接收规则 |
| 14 | Forbidden claims | 全文无批准/合规/量产措辞 |

### delivery_summary Checklist（10 项）

- [ ] `document_type: SoftwareArchitecture`
- [ ] `writing_scenario` 字段
- [ ] 保守状态枚举（非 approved）
- [ ] 统计：组件数、接口数、分配行数、open 数、HITL 数
- [ ] gap 按 SEC-* 分类表
- [ ] 下游接收方：详细设计、单元设计、集成测试、V&V、静态分析
- [ ] **open 规则**：「下游不得静默关闭 open」
- [ ] artifact 索引链接齐全
- [ ] P0/P1 关闭摘要
- [ ] SWE.2 **不**声明能力等级达成

### ISO 26262 / 功能安全交接 Checklist

- [ ] 明示：本包 **不**构成 ISO 26262 合规认证
- [ ] SEC-SAFE-ARCH（若有）在 final 中为引用级，非机制批准
- [ ] 下游详细设计须单独处理 TSR 与安全验证，不得从本包推断

### From-Scratch 专属 Checklist

- [ ] 状态多为 `finalized_with_open_items`
- [ ] gap 分类统计写入 delivery_summary
- [ ] Open Registry 完整列出 NEEDS_USER_CONFIRMATION
- [ ] 无 SEC-DIFF（除非另有形状 sample 说明）

### With-Reference 专属 Checklist

- [ ] **参考边界声明**全文存在（历史 SwAD file_id + 用途限定）
- [ ] SEC-DIFF 在正文且 ≥1 行具体差异
- [ ] 下游说明：「不得用历史 SwAD 闭合 open」
- [ ] Δ Removed/Modified 项有下游验证提示

### 本步 Review 要点

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 交付边界 | review-ready，非批准 | 同上 + 参考边界 |
| Open 完整性 | Registry 与 matrix 一致 | 同上 |
| 下游安全 | open 规则明示 | 参考不得当基线 |
| 状态保守 | 无 approved/compliant | 同上 |

### P0 失效项

| 错误 | 后果 |
|---|---|
| 批准/ASPICE/ISO 合规措辞 | 交付越权 |
| Open Registry 不完整 | 下游误关 open |
| With-Reference 未声明参考边界 | 误用历史 SwAD |
| 审查/验证摘要写成 sign-off | 边界错误 |

### 一句话归纳

**Checklist 核心**：final 14 项 + delivery 10 项齐全、状态保守、Open Registry 完整、下游规则明示。  
**Review 核心**：From-Scratch 诚实交付 open；With-Reference 必有参考边界声明与 SEC-DIFF。

## A1 / A2 / B

**A1**：交付完整、状态保守、下游规则明示。  
**A2**：补字段、补参考边界。  
**B**：final 不替代人工评审与 ASPICE 评估。
