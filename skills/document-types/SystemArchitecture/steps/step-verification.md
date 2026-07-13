# System Architecture 子 skill · Step 9 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/SystemArchitecture/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 链、tier 合规、**HARA/TSR/TSC deferred**、forbidden claims。
- 失败写入 `verify/failures.md`。

## System Architecture 方法论（本步定位）

本步对应 **阶段 6** 中的 **形式/合规验证**（质量工程师 / 机器检查）。

## 本步 Review / Checklist 要点

### VC-1 · Artifact 链完整性

- [ ] `manifest.json`、`task_brief.json` 存在
- [ ] `input_inventory.json`、`source_index.json`、`provenance_index.json` 存在
- [ ] `template_structure.json`、`outline_l1.md`、`outline_l2.md`、`section_writing_plans.json`、`evidence_map.json`、`citation_plan.json`、`outline_final.md`、`section_tasks.json`、`claim_support_matrix.json`、`writing_plan.md`、`unresolved_questions.md` 齐全
- [ ] `draft/full_draft.md`、`review/review_report.json` 存在

### VC-2 · Tier 合规与 Provenance

- [ ] critical claim 在 `claim_support_matrix.json` 中全部有支撑（EVD 或 NEEDS_USER_CONFIRMATION）
- [ ] critical claim 支撑 tier ∈ {T0, T1}；**禁止** T4、T5
- [ ] 每条 EVD 含：`source_file_id` + L1 + L2 + L3 + `location` + `excerpt`
- [ ] 接口 EVD：含 `direction` 字段或对应 L3 摘录显示方向信息

### VC-3 · Forbidden Claims 扫描

- [ ] 草稿与 final 报告**不**包含：
  - `architecture is approved`
  - `architecture is complete and compliant`
  - `ASPICE SYS.3 satisfied`
  - `ISO 26262 compliant`
  - `ready for production release`
  - `validated` / `risk accepted`
- [ ] 状态字段仅允许保守枚举

### VC-4 · 文档类型纯净性扫描

- [ ] 草稿**不出现**：`hazard`、`hazardous event`、`S/E/C`、`ASIL`、`Safety Goal`、`TSR`、`technical safety mechanism`、`SwRS table`、`HwRS table`
- [ ] SEC-SAFE-ARCH 仅出现引用字段，不出现新分析字段

### VC-5 · HITL 与 candidate 状态

- [ ] `NEEDS_USER_CONFIRMATION` 未被静默消除
- [ ] `candidate_profile_update.yaml` / `candidate_skill_patch.md`：`active: false` 或 `status: proposed`

### 机器/规则化 Checklist

| 规则 | 描述 |
|---|---|
| ID 命名 | ELEM-xxx / IF-ARCH-xxx / ALLOC-xxx 正则匹配，唯一 |
| Direction 列 | 接口表 Direction ∈ {In, Out, Bidirectional, NEEDS_USER_CONFIRMATION} |
| 双向追溯 | 每条元素/分配至少 1 个上游 requirement 或 `orphan`；每个 requirement 至少 1 个分配或显式 open |
| 单位检查 | 资源 / 时序数字带单位（ms、MHz、MB、kbps 等） |

### From-Scratch 专属 Checklist

- [ ] 大量 `NEEDS_USER_CONFIRMATION` 是预期，**不**触发 `failed`
- [ ] 分配 / 方向 / 资源 open 状态在 verify 后保留

### With-Reference 专属 Checklist

- [ ] `evidence_map.json` 与 `claim_support_matrix.json` 中任何 `source_file_id` ≠ 参考架构 file_id（**P0**）
- [ ] 参考架构 file_id 在 `input_inventory.json` 中 `role=sample` 且 `is_fact_source=false`
- [ ] SEC-DIFF 存在；至少一行；行内有具体差异类型

### 常见 P0

| 失效 | 后果 |
|---|---|
| sample 支撑元素 / 接口 / 分配 / 资源 | 事实来源违规 |
| 静默填值（无 EVD 无 open） | 不可追溯 |
| 含 forbidden final claims | 越权结论 |
| 接口 Direction 空白且标 confirmed | 不可集成 |
| With-Reference：参考架构 file_id 进 evidence_map | 事实来源违规 |

## A1 / A2 / B

**A1**：每项 CHECK 有 pass/fail；P0 无遗漏；状态保守。  
**A2**：修复 blocker 后重验；按机器规则逐项校正。  
**B**：status 保守（`passed_with_open_items` / `failed`），无 approved / compliant。
