# IDD 子 skill · Step 15 · 候选 profile 更新

骨架：`skills/workflow-steps/step-candidate-profile-update/SKILL.md`。领域规则：`skills/document-types/ItemDefinitionDocument/SKILL.md`。

## 本步目的要点

- 产出 `candidate_profile_update.yaml`、`candidate_skill_patch.md`、`promotion_report.md`。
- 状态 **`proposed` / `inactive`**，不自动启用、不覆盖稳定 skill。
- 可提炼：IDD 模板 L2 划分习惯、常见 gap 模式、Clause 5 checklist 增强建议。
- **不得**把本次 run 的 F-xx/边界/接口内容写入候选 profile 作为通用事实。

## IDD 方法论（本步定位）

本步对应流程 **学习与候选改进** 环节，从本次 IDD 运行中提炼 **可复用的流程/结构经验**，不固化项目事实。

### 可从本次 run 提炼的 IDD 方法论信号

| 信号类型 | 示例 | 对应 ISO 26262 关注点 |
|---|---|---|
| 结构习惯 | IF-xx 表强制方向列 | §5.4.3 外部接口 |
| gap 模式 | 误用材料常缺失 | §5.4.4 b |
| checklist 增强 | 边界 In/Out 双向检查 | §5.4.3 |
| 写作模式 | 假设与误用分节 | §5.4.4 / §5.4.4 b |
| 流程提醒 | sample 勿升格 source | 事实来源分离 |

### IDD 写作核心原则（候选 patch 可引用，不含项目事实）

1. **IDD ≠ HARA**：不写危害、评级、安全目标。
2. **事实来源分离**：sample 只借结构，T4 不作 critical claim 事实。
3. **缺口显式**：缺材料标 open / gap，不静默填值。
4. **保守措辞**：边界与接口缺确认时保留 `NEEDS_USER_CONFIRMATION`。
5. **交付边界**：review-ready 不等于 sign-off，不等于 ISO 26262 合规认证。

## 候选更新边界

| 可提案 | 禁止 |
|---|---|
| IDD 章节粒度、表列形状（如 IF 方向列） | 具体项目功能/接口值 |
| 误用节写作检查项（§5.4.4 b） | hazard/ASIL 模板渗入 IDD |
| 接口方向列强制提醒 | sample 表格内容复用 |
| Clause 5 checklist 条目增强 | 将本次 F-xx 写入通用 profile |
| 常见 gap 模式（流程级） | 「本项目边界为…」类事实 |

### 与 HARA 下游关系（候选文档可含流程说明）

IDD 候选 profile 可建议「交付时明示 HARA 交接清单」，但 **不得** 在 IDD profile 中预填 hazard 分析模板。

## 本步 Review / Checklist 要点

本步从本次 run 提炼**可复用的审查/checklist 增强建议**；不得固化项目事实。

### 可提案的 Checklist 增强项

| 信号类型 | 可提案内容 | Clause 5 |
|---|---|---|
| 结构习惯 | IF-xx 表强制方向列 | §5.4.3 |
| gap 模式 | 误用材料常缺失 → 强化 Step 1 gap 登记 | §5.4.4 b |
| checklist 增强 | 边界 In/Out 双向检查 | §5.4.3 |
| 写作模式 | 假设与误用分节检查 | §5.4.4 / §5.4.4 b |
| 流程提醒 | sample 勿升格 source | 事实来源 |
| 审查提醒 | Forbidden Claims 自动扫描规则 | VC-3 |
| tier 规则 | T4 不得支撑 critical claim | VC-2 |

### 候选 patch 可引用的 Review 原则（不含项目事实）

1. **IDD ≠ HARA**：审查 checklist 不含 hazard/ASIL/SG 项
2. **事实来源分离**：审查须检查 sample 未当事实
3. **缺口显式**：审查须确认 open 项未静默消除
4. **保守措辞**：审查须扫描 forbidden claims
5. **交付边界**：review-ready ≠ sign-off

### 本步 Review 要点

| 维度 | 检查项 | 级别 |
|---|---|---|
| 无事实泄漏 | patch 不含 F-xx/IF-xx/边界具体值 | P0 |
| 状态 | candidate `active: false` | P0 |
| 范围 | 提案限于流程/结构/checklist | P1 |
| IDD 纯净 | 无 hazard 模板渗入 IDD profile | P0 |

## A1 / A2 / B

**A1**：candidate `active: false`；无项目事实泄漏；提案限于流程/结构/checklist。  
**A2**：收紧 patch 范围，去除任何 F-xx/IF-xx/边界具体值。  
**B**：promotion_report 说明须人工审查后启用；不等于 ISO 26262 方法学批准。
