# Software Architecture 子 skill · Step 9 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 链、tier 合规、文档类型纯净性、forbidden claims。
- 与 Step 8 人工审查互补：本步为 **机器可重复** 规则验证。
- 失败写入 `verify/failures.md`。

## Software Architecture 方法论（本步定位）

### 9.1 本步在八阶段方法链中的位置

本步对应 **阶段 6** 中的 **形式/合规验证**（质量工程师 / 自动化检查）。

**方法原则**：验证不改变正文，只判定 pass/fail。大量 `NEEDS_USER_CONFIRMATION` 在 From-Scratch 下 **不** 单独构成 fail。

### 9.2 阶段 6 · 形式验证方法

#### VC-1 · Artifact 链完整性

验证前置 Step 1–8 产物齐全且可链接：manifest → inventory → index → outline → plans → evidence_map → section_tasks → draft → review。

#### VC-2 · Tier 与 Provenance

- critical claim 的 tier ∈ {T0, T1} 或 explicit open。
- 每条 EVD：`source_file_id` + L1 + L2 + L3 + `location` + `excerpt`。
- 接口 EVD 须含 direction 信息或对应 open。

#### VC-3 · Forbidden Claims 扫描

禁止短语（全文扫描 draft 与即将交付的 final）：

- `software architecture is approved` / `架构已批准`
- `ASPICE SWE.2 satisfied` / `Level X achieved`
- `ISO 26262 compliant`
- `ready for production release` / `可量产`
- `validated` / `risk accepted`

#### VC-4 · 文档类型纯净性

禁止词/段：hazard、hazardous event、ASIL、Safety Goal、TSR（新编）、technical safety mechanism（终稿）、detailed design、unit design、class diagram、function implementation、pseudocode。

#### VC-5 · HITL 与 candidate 状态

- open 未被批量删除。
- candidate_profile `active: false`。

#### 机器规则（汽车控制器 SwAD 特有）

| 规则 ID | 描述 |
|---|---|
| R-ID | SWA-COMP/IF/ALLOC ID 正则唯一 |
| R-DIR | Direction ∈ {Provider, Consumer, Bidirectional, NEEDS_USER_CONFIRMATION} |
| R-TRACE | 每 SwRS 行有分配或 explicit orphan |
| R-UNIT | 资源/时序数字带单位 |
| R-LAYER | Layer ∈ 已知枚举或 open |

#### From-Scratch 验证策略

- open 密度高 → `passed_with_open_items` 合法。
- 检查重点：是否有 **无 EVD 的 confirmed**（这才是 fail）。

#### With-Reference 验证策略

- 扫描 evidence_map / matrix 中 `source_file_id` 是否含历史 SwAD file_id → **P0 fail**。
- SEC-DIFF 存在且 ≥1 行有具体 Δ Type。
- 历史 SwAD 在 inventory 中 `role=sample`。

## 本步 Review / Checklist 要点

### VC-1 · Artifact 链完整性 Checklist

- [ ] `manifest.json`、`task_brief.json` 存在且 `writing_scenario` 有效
- [ ] `input_inventory.json`、`source_index.json`、`provenance_index.json` 存在
- [ ] `outline_l1/l2`、`section_writing_plans.json`、`evidence_map.json`、`citation_plan.json`、`claim_support_matrix.json`、`section_tasks.json`、`writing_plan.md`、`unresolved_questions.md` 齐全
- [ ] `draft/full_draft.md`、`review/review_report.json` 存在
- [ ] 前置 Step 1–8 产物路径可追溯

### VC-2 · Tier 与 Provenance Checklist

- [ ] critical claim 在 matrix 中均有 EVD 或 `NEEDS_USER_CONFIRMATION`
- [ ] critical claim 支撑 tier ∈ {T0, T1}；**禁止** T4、T5
- [ ] 每条 EVD 含：`source_file_id` + L1 + L2 + L3 + `location` + `excerpt`
- [ ] 接口相关 EVD 含 `direction` 或 L3 摘录显示方向
- [ ] 历史 SwAD file_id **不在**任何 critical EVD 中（With-Reference **P0**）

### VC-3 · Forbidden Claims 扫描 Checklist

- [ ] 全文无：`software architecture is approved`、`架构已批准`
- [ ] 全文无：`ASPICE SWE.2 satisfied`、`Level X achieved`
- [ ] 全文无：`ISO 26262 compliant`、`已满足功能安全合规`
- [ ] 全文无：`ready for production release`、`可量产`、`validated`、`risk accepted`
- [ ] 状态字段仅保守枚举

### VC-4 · 文档类型纯净性 Checklist

- [ ] 无：hazard、hazardous event、S/E/C、ASIL、Safety Goal
- [ ] 无：TSR（新编）、technical safety mechanism（终稿）
- [ ] 无：detailed design、unit design、class diagram、pseudocode、function implementation
- [ ] SEC-SAFE-ARCH 仅引用字段，无新分析字段

### VC-5 · HITL 与 Open 保持 Checklist

- [ ] `NEEDS_USER_CONFIRMATION` 未被批量删除
- [ ] SEC-OPEN 与 matrix open 数量一致（允许 ±说明）
- [ ] `candidate_profile_update`：`active: false` 或 `status: proposed`

### 机器规则 Checklist（汽车 SwAD）

| 规则 | 检查内容 | fail 条件 |
|---|---|---|
| R-ID | SWA-COMP/IF/ALLOC ID 唯一、正则匹配 | 重复或空 ID |
| R-DIR | Direction ∈ {Provider, Consumer, Bidirectional, NEEDS_USER_CONFIRMATION} | 空且 confirmed |
| R-TRACE | 每 SwRS 有分配或 orphan；每 COMP 有 SwRS 或 orphan 说明 | 静默 orphan |
| R-UNIT | 资源/时序数字带单位 | 裸数字且 confirmed |
| R-LAYER | Layer 在枚举内或 open | 随意字符串且 confirmed |

### From-Scratch 验证策略 Checklist

- [ ] 大量 open **不**单独导致 `failed`
- [ ] 重点 fail：**无 EVD 的 confirmed** 行
- [ ] 分配/方向/资源 open 在 verify 后仍保留

### With-Reference 验证策略 Checklist

- [ ] evidence_map/matrix 中 `source_file_id` ≠ 历史 SwAD file_id（**P0**）
- [ ] 历史 SwAD 在 inventory：`role=sample`，`is_fact_source=false`
- [ ] SEC-DIFF 存在；≥1 行；Δ Type 具体
- [ ] delivery 参考边界声明将在 Step 11 出现（预检 task_brief）

### 验证结论枚举

- `passed` — 无 P0，open 可存在
- `passed_with_open_items` — **From-Scratch 推荐常态**
- `failed` — 存在 P0

### P0 fail 与处理

| 失效 | 处理 |
|---|---|
| T4 支撑 critical claim | 回 Step 6 修 matrix |
| 历史 SwAD 进 evidence_map | 删 EVD、改 open |
| forbidden claims | 交 Step 10 删改 |
| 接口 Direction 空且 confirmed | 改 open 或补 EVD |
| artifact 链断裂 | 回对应 Step 补产物 |

### 一句话归纳

**Checklist 核心**：VC-1~5 全过、机器规则 R-ID/R-DIR/R-TRACE 无 P0、open 未被删。  
**Review 核心**：From-Scratch 允许 passed_with_open_items；With-Reference 严查 sample 进 EVD。

## A1 / A2 / B

**A1**：每项 CHECK 有 pass/fail；P0 无遗漏。  
**A2**：修 blocker 后重验。  
**B**：status 保守，无 approved/compliant。
