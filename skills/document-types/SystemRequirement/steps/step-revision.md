# SyRS 子 skill · Step 10 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 依 Step 8/9 findings 修订 → `revised/full_draft.md`、`change_log.md`。
- 不新增无 EVD 支撑的 SYS-xx 或限值结论。

## SyRS 方法论（本步定位）

本步对应 **阶段 7：修订与交付** 中的 **修订** 环节。

### 阶段 7 · 修订（本步执行）

按 P0 优先：

1. **补上游追溯**（每条 SYS-F/IF）
2. **补接口方向/对端**
3. 修正 tier 违规（去除 sample 支撑）
4. 去除 **HARA/ASIL/SG/TSR 泄漏**
5. 验证方法改回「候选」或 open
6. 去除 forbidden / 批准措辞
7. 同步 matrix 与 unresolved

### 修订后仍须满足

- 每条 SYS-xx 链上游；接口有方向；无 HARA/TSR/TSC
- `NEEDS_USER_CONFIRMATION` 未静默消除

## 本步 Review / Checklist 要点

### 修订优先级矩阵（必须按此顺序处理）

| 级别 | 修订项 | 处理方式 |
|---|---|---|
| **P0-1** | 含 HARA / ASIL / SG / TSR / TSC / SwRS 字段或章节 | 整段删除；改为 SEC-SAFE 引用或 open |
| **P0-2** | sample / 参考 SyRS 支撑 critical claim | 改 EVD 为 open / HITL；移入 SEC-OPEN |
| **P0-3** | SYS-xx 无上游链接且标 confirmed | 补真实上游 EVD；缺则改 NEEDS_USER_CONFIRMATION |
| **P0-4** | SYS-IF Direction 空白且标 confirmed | 补 source 或改 open |
| **P0-5** | forbidden claims（approved / compliant / 量产） | 整句改保守措辞；不留半句 |
| **P0-6** | With-Reference 缺 SEC-DIFF 或仅写「同参考」 | 重新写具体差异 |
| **P0-7** | SEC-SAFE blanket 引用全部 FSR/SG | 改为显式 FSR/SG 引用，缺则 open |
| **P1** | 模糊词 / 多重 shall / 单位缺失 / ID 不一致 / 反向追溯空白 | 逐项修语句、补单位、补反向列 |

### 修订原则 Checklist

- [ ] 每条修订**有 Step 8 / Step 9 issue ID 来源**；无 issue 不修订
- [ ] **未新增**无 EVD 的 SYS-xx；如必须新增，必须先经 HITL（生成 hitl_decisions.jsonl 条目）
- [ ] 修订**不删除** open 项；除非提供 T0/T1 证据并记录 hitl 决策
- [ ] 修订**不引入** HARA / TSR / TSC / SwRS 内容
- [ ] `revised/change_log.md` 每行：`issue_id` + `section_id` + `change_type` + `before/after 摘要` + `decision_basis`
- [ ] 修订后 `revised/full_draft.md` 与 `draft/full_draft.md` 通过 diff 可比对

### Forbidden 修订动作 Checklist

- [ ] **禁止**：为关闭 P0 而把 NEEDS_USER_CONFIRMATION 改为 confirmed 且无 HITL
- [ ] **禁止**：为关闭 P0 而新增伪造 EVD
- [ ] **禁止**：为关闭 P0 而调低需求优先级或修改其表述使其「无需追溯」
- [ ] **禁止**：合并多条 SYS-xx 以消除 orphan
- [ ] **禁止**：删除 SEC-OPEN 中的 open 项

### ASPICE / ISO 维度 Checklist

- [ ] **ASPICE SYS.2 BP5**：修订后双向追溯仍闭合或显式 open
- [ ] **ASPICE SYS.2 BP3**：修订后一致性/可测试性问题逐条 close 或转 open
- [ ] **ASPICE SYS.2 BP4**：修订前后的客户沟通项（OEM 反馈）记录在 SEC-OPEN
- [ ] **ISO 26262-3 §5 接口**：修订后 SEC-FUNC/IF/ENV/DIAG 仍可作 IDD 输入
- [ ] **ISO 26262-3 §7 接口**：SEC-SAFE 修订仅在 fsr_source 显式范围内

### From-Scratch 专属 Checklist

- [ ] 大量 open 是预期，**不**为「漂亮」而批量关闭
- [ ] 限值数字仍 `NEEDS_USER_CONFIRMATION` 时保留状态
- [ ] 修订主要在补 EVD、改 shall 语句、修正 ID 命名

### With-Reference 专属 Checklist

- [ ] **修订严禁**用参考 SyRS「关 P0」（**P0**）
- [ ] 修订过程：若某条原引参考 SyRS → 必须改为本项目 EVD / HITL / open
- [ ] SEC-DIFF 行修订须基于本项目 source EVD；不得用参考 SyRS 闭合 Δ 缺口
- [ ] 客户「沿用参考」需求：必须创建 HITL 决策条目，change_log 引用 HITL ID

### change_log 字段 Checklist

| 字段 | 通过条件 |
|---|---|
| issue_id | 对应 Step 8/9 findings |
| section_id | 唯一定位 |
| change_type | added / removed / modified / status_changed / open_added |
| before / after | 摘要可对比 |
| decision_basis | EVD ID / HITL ID / checklist 项 |
| risk | 修订潜在风险（如「Direction 从 In 改 Bidirectional 是否影响集成」） |

### 修订后回归 Checklist（须二次过 Step 8/9）

- [ ] 14 项 SYS.2 内容 checklist 全部通过或转 open
- [ ] VC-1 ~ VC-5 全部通过
- [ ] P0 列表清空或显式 open + HITL
- [ ] `unresolved_questions.md` 与 SEC-OPEN 一致

### 常见 P0（修订时）

| 错误 | 后果 |
|---|---|
| 为关 P0 无证据补全 SYS-xx | 不可追溯 |
| 修订引入 HARA / ASIL / TSR | 文档类型漂移 |
| 静默删除 open / HITL pending | HITL 失效 |
| 用参考 SyRS 闭合 open（With-Reference） | 事实来源违规 |
| 把 forbidden 措辞改为同义词（如「批准」→「认可」） | 仍是越权结论 |

### 常见 P1

- change_log 缺 decision_basis
- 修订只改局部表述未同步 SEC-TRACE
- 修订后 SEC-OPEN 与 unresolved_questions 不一致

## A1 / A2 / B

**A1**：P0 已关闭或显式 open；无 HARA/TSR；无 forbidden claims；change_log 可追溯。  
**A2**：重跑未关闭项；二次过 Step 8/9。
**B**：修订可追溯到 issue_id 与 decision_basis；With-Reference 未用参考 SyRS 关 P0。
