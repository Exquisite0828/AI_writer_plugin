# IDD 子 skill · Step 12 · 修订

骨架：`skills/workflow-steps/step-revision/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 依 Step 10/11 findings 修订草稿 → `revised/full_draft.md`、`change_log.md`、`revision_plan.json`。
- 修订优先：**补边界/接口/误用**、修正 tier 违规、去除 HARA 泄漏、补 `NEEDS_USER_CONFIRMATION`。
- 不新增无 EVD 支撑的功能或接口结论。
- 修订后仍不得写 forbidden final claims。

## IDD 方法论（本步定位）

本步对应 **阶段 7：修订与交付** 中的 **修订** 环节。

### 阶段 7 · 修订（本步执行）

1. **按审查意见修订正文**，优先处理 P0：
   - 补全边界 In/Out 双向说明
   - 补全接口方向与对端
   - 补全或显式 open 误用节
   - 去除 HARA 危害/评级泄漏
   - 修正 sample 当事实的 tier 违规
2. **保留变更记录**（`change_log.md` 追溯到 review/verify issue id）。
3. **同步 citation / open 列表**，确保修订后 EVD↔claim 仍一致。
4. **不新增**无 EVD 支撑的功能或接口结论。

### 修订原则

- 缺口显式：缺材料标 open / gap，**不静默填值**。
- 保守措辞：边界与接口缺确认时保留 `NEEDS_USER_CONFIRMATION`。
- IDD ≠ HARA：修订不得引入 hazard、ASIL、Safety Goal。
- 修订后状态仍为 review-ready，**不等于** sign-off。

## 典型修订子任务

1. 按 P0 issue 逐条改 draft（边界 In/Out、接口方向、误用节）。
2. 去除草稿中 hazard/ASIL/SG 措辞或表格。
3. 将无 EVD 支撑的「已确认」改回 `NEEDS_USER_CONFIRMATION`。
4. 同步 `claim_support_matrix` 与 `unresolved_questions.md`。
5. 更新 `change_log.md`（issue id → 修订动作 → 结果）。

## 本步 Review / Checklist 要点

本步按 Step 10/11 findings 闭环修订；修订后须重新满足 Clause 5 与 Forbidden Claims 要求。

### 修订优先 Checklist（按 P0 顺序）

- [ ] 补全边界 In/Out 双向说明（§5.4.3）
- [ ] 补全接口方向与对端（§5.4.3）
- [ ] 补全或显式 open 误用节（§5.4.4 b）
- [ ] 去除 HARA 危害/评级泄漏（IDD 纯净性）
- [ ] 修正 sample 当事实的 tier 违规（VC-2）
- [ ] 将无 EVD 的「已确认」改回 `NEEDS_USER_CONFIRMATION`
- [ ] 去除 forbidden 措辞（VC-3）
- [ ] 同步 `claim_support_matrix` 与 `unresolved_questions.md`

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| P0 闭环 | 全部 P0 已关闭或显式保留 open 理由 | P0 |
| 证据不增 | 未新增无 EVD 支撑的功能/接口结论 | P0 |
| Forbidden Claims | 修订后无「已批准」「已合规」 | P0 |
| IDD 纯净性 | 修订未引入 hazard/ASIL/SG | P0 |
| 可追溯 | change_log 追溯到 review/verify issue id | P1 |
| 缺口诚实性 | 未静默删除 open 项 | P0 |

### 修订后仍须满足的 Clause 5 要点

- 功能、边界、接口、环境、工况、假设、误用：有来源或 open
- 接口有方向；边界 In/Out 双向；误用独立成节
- 全文无 HARA 内容

## 常见错误（修订时重点防）

| 错误 | 后果 | 级别 |
|---|---|---|
| 为关闭 P0 而无证据补全 F-xx/接口 | 不可追溯 | P0 |
| 修订时引入 HARA 内容 | 文档类型漂移 | P0 |
| 静默删除 open 项 | HITL 失效 | P0 |
| 修订后写「已批准」「已合规」 | 越权结论 | P0 |

## A1 / A2 / B

**A1**：P0 已关闭或显式保留 open 理由；无 forbidden claims；无 HARA 泄漏。  
**A2**：重跑未关闭项。  
**B**：修订可追溯到 review/verify issue id；change_log 完整。
