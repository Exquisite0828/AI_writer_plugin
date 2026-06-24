# Software Architecture 子 skill · Step 12 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/SoftwareArchitecture/SKILL.md`。

## 本步目的要点

- 依 Step 10/11 findings 修订 → `revised/full_draft.md`、`change_log.md`。
- 不新增无 EVD 支撑的组件/接口/分配结论。
- 修订后须满足：P0 已关闭 **或** 显式保留 open 并记录原因。

## Software Architecture 方法论（本步定位）

### 12.1 本步在八阶段方法链中的位置

本步对应 **阶段 7：修订与交付** 的 **修订** 环节。

**方法原则**：修订是 **纠错与收敛**，不是 **补全幻想**。无新 EVD 则只能：删除违规内容、改为 open、或降级 confirmed→NEEDS_USER_CONFIRMATION。

### 12.2 阶段 7 · 修订方法

#### 修订优先级矩阵

| 级别 | 修订项 | 处理方法 |
|---|---|---|
| P0-1 | HARA/ASIL/SG/TSR/TSC/详细设计/代码 | 整段删除或改引用/open |
| P0-2 | sample 支撑 critical claim | 改 open；移入 SEC-OPEN |
| P0-3 | 组件/分配无上游且 confirmed | 补 EVD 或改 open |
| P0-4 | 接口 Direction 空且 confirmed | 补 source 或改 open |
| P0-5 | forbidden claims | 改保守措辞 |
| P0-6 | With-Reference 缺 SEC-DIFF 或「同参考」 | 重写具体差异行 |
| P0-7 | SEC-SAFE-ARCH blanket 引用 | 拆为逐条引用或 open |
| P1 | 模糊词/缺单位/ID 不一致 | 逐句修 |

#### 修订决策树（单条 finding）

```text
有违规内容？
├─ 是越权类型（HARA/代码/批准）→ 删除
├─ 是 sample 支撑 → 删事实，保留 open
├─ 缺 EVD 但可补 source → 回 Step 6 补 EVD 后重写该句
└─ 缺 EVD 且无可补 source → 改 NEEDS_USER_CONFIRMATION
```

#### From-Scratch 修订策略

- **不**为降低 open 数量而批量填默认值。
- 保留诚实的 SEC-OPEN 汇总。
- 分配/接口/资源 open 行 **保留** 除非有 T0/T1 新增。

#### With-Reference 修订策略

- **严禁**用历史 SwAD 闭合任何 P0。
- SEC-DIFF 修订须基于本项目 source EVD。
- 用户口头「沿用参考」→ 创建 HITL 决策条目后方可改 confirmed（仍须 T0）。

#### change_log 规范

每行：`issue_id` | `section_id` | `change_type` | `before` | `after` | `decision_basis`（EVD ID / HITL ID / open 保留原因）

## 本步 Review / Checklist 要点

### 修订执行 Checklist（按 P0 优先级）

| 优先级 | 修订项 | 完成标准 |
|---|---|---|
| P0-1 | HARA/ASIL/SG/TSR/详细设计/代码 | 已删除或改 open/引用 |
| P0-2 | sample 支撑 critical claim | 已改 open 或补 T0/T1 EVD |
| P0-3 | 组件/分配无上游且 confirmed | 已补 EVD 或改 NEEDS_USER_CONFIRMATION |
| P0-4 | 接口 Direction 空且 confirmed | 已补 source 或改 open |
| P0-5 | forbidden claims | 已改保守措辞 |
| P0-6 | With-Reference 缺/空 SEC-DIFF | 已重写具体差异行 |
| P0-7 | SEC-SAFE-ARCH blanket TSR | 已拆为逐条引用或 open |
| P1 | 模糊词/缺单位/ID 不一致 | 已逐项修正 |

### 通用 Checklist（10 项）

- [ ] 每条修订有 Step 10/11 `issue_id` 来源
- [ ] **未新增**无 EVD 的组件/接口/分配事实
- [ ] 必须新增架构元素时，先有 HITL 记录
- [ ] **未删除**应保留的 open（除非 T0/T1 + change_log 记录）
- [ ] **未引入** HARA/TSR/详细设计/代码
- [ ] `change_log.md` 每行含：issue_id、section_id、change_type、before、after、decision_basis
- [ ] `revised/full_draft.md` 与 `draft/full_draft.md` 可 diff
- [ ] 修订后三表 ID 仍唯一
- [ ] 修订后 Direction 规则仍满足 R-DIR
- [ ] 二次审查：P0 已关闭或显式 open 并记录

### From-Scratch 专属 Checklist

- [ ] 未为「漂亮」批量关闭 open
- [ ] 分配/方向/资源仍缺证据时保留 NEEDS_USER_CONFIRMATION
- [ ] SEC-OPEN 条目数 ≥ 修订前（除非有 T0/T1 闭合）

### With-Reference 专属 Checklist

- [ ] **严禁**用历史 SwAD 闭合任何 P0
- [ ] SEC-DIFF 修订行均有本项目 source EVD
- [ ] 「沿用参考」仅有 HITL ID 支撑的变化
- [ ] change_log 中无「参考 SwAD 作为 decision_basis」

### 本步 Review 要点

| 维度 | 通过条件 |
|---|---|
| P0 闭环 | 全部 P0 已修或显式 open + 原因 |
| 追溯性 | change_log 可追到 issue 与 EVD/HITL |
| 无新违规 | 修订未引入 sample 事实或 forbidden 措辞 |
| open 完整性 | 不应减少的 open 仍在 |
| 参考边界 | With-Reference 未用 sample 关 issue |

### P0 失效项

| 错误 | 后果 |
|---|---|
| 无证据补全组件/分配关 P0 | 不可追溯 |
| 用历史 SwAD 关 P0 | 事实违规 |
| 静默删 HITL pending | HITL 失效 |
| 修订引入 HARA/详细设计 | 类型漂移 |

### 一句话归纳

**Checklist 核心**：P0 有据闭合、change_log 完整、无无 EVD 新增、open 不擅删。  
**Review 核心**：From-Scratch 不批量关 open；With-Reference 绝不用参考关 P0。

## A1 / A2 / B

**A1**：P0 已关闭或显式 open；change_log 完整。  
**A2**：重跑未关闭项；二次过 Step 10/11。  
**B**：修订不引入新违规。
