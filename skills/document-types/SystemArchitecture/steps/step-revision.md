# System Architecture 子 skill · Step 12 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 依 Step 10/11 findings 修订 → `revised/full_draft.md`、`change_log.md`。
- 不新增无 EVD 支撑的架构元素/接口/分配结论。

## System Architecture 方法论（本步定位）

本步对应 **阶段 7：修订与交付** 中的 **修订** 环节。

## 本步 Review / Checklist 要点

### 修订优先级矩阵

| 级别 | 修订项 | 处理方式 |
|---|---|---|
| **P0-1** | 含 HARA / ASIL / SG / TSR / TSC / SwRS / HwRS 字段或章节 | 整段删除；改为 SEC-SAFE-ARCH 引用或 open |
| **P0-2** | sample / 参考架构支撑 critical claim | 改 EVD 为 open / HITL；移入 SEC-OPEN |
| **P0-3** | 元素 / 接口 / 分配无上游链接且标 confirmed | 补真实上游 EVD；缺则改 NEEDS_USER_CONFIRMATION |
| **P0-4** | 接口 Direction 空白且标 confirmed | 补 source 或改 open |
| **P0-5** | forbidden claims | 整句改保守措辞 |
| **P0-6** | With-Reference 缺 SEC-DIFF 或仅写“同参考” | 重新写具体差异 |
| **P0-7** | SEC-SAFE-ARCH blanket 引用全部 FSR/TSC | 改为显式约束引用，缺则 open |
| **P1** | 模糊词 / 单位缺失 / ID 不一致 / rationale 缺失 | 逐项修语句与表头 |

### 修订原则 Checklist

- [ ] 每条修订**有 Step 10 / Step 11 issue ID 来源**
- [ ] **未新增**无 EVD 的元素/接口/分配；如必须新增，需先经 HITL
- [ ] 修订**不删除** open 项；除非提供 T0/T1 证据并记录 hitl 决策
- [ ] 修订**不引入** HARA / TSR / TSC / SwRS / HwRS 内容
- [ ] `change_log.md` 每行：`issue_id` + `section_id` + `change_type` + `before/after` + `decision_basis`
- [ ] 修订后 `revised/full_draft.md` 与 `draft/full_draft.md` 可 diff 比较

### From-Scratch 专属 Checklist

- [ ] 大量 open 是预期，**不**为“漂亮”而批量关闭
- [ ] 分配/接口方向/资源数值仍 `NEEDS_USER_CONFIRMATION` 时保留状态

### With-Reference 专属 Checklist

- [ ] **严禁**用参考架构文档“关 P0”
- [ ] SEC-DIFF 行修订须基于本项目 source EVD
- [ ] 客户“沿用参考”架构：必须创建 HITL 决策条目

### 常见 P0

| 错误 | 后果 |
|---|---|
| 为关 P0 无证据补全元素/分配 | 不可追溯 |
| 修订引入 HARA / ASIL / TSR | 文档类型漂移 |
| 静默删除 open / HITL pending | HITL 失效 |
| 用参考架构闭合 open（With-Reference） | 事实来源违规 |

## A1 / A2 / B

**A1**：P0 已关闭或显式 open；无 HARA/TSR；无 forbidden claims；change_log 可追溯。  
**A2**：重跑未关闭项；二次过 Step 10/11。  
**B**：修订可追溯到 issue_id 与 decision_basis；With-Reference 未用参考架构关 P0。
