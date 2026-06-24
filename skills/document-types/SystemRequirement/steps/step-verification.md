# SyRS 子 skill · Step 11 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/SystemRequirement/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 链、tier 合规、**HARA/TSR/TSC deferred**、forbidden claims。
- 失败写入 `verify/failures.md`。

## SyRS 方法论（本步定位）

本步对应 **阶段 6** 中的 **形式/合规验证**（质量工程师/机器检查）。

### 形式/合规验证（VC-1～VC-5）

| 检查编号 | 验证要点 |
|---|---|
| VC-1 | manifest → source_index → … → draft → review → unresolved 完整 |
| VC-2 | critical claim 无 T4/T5；SYS-xx/接口 EVD 含 L1/L2/L3 provenance |
| VC-3 | 无 forbidden 措辞 |
| VC-4 | 草稿无 HARA/ASIL/SG/TSR/TSC/SwRS 表/章节渗入 |
| VC-5 | `NEEDS_USER_CONFIRMATION` 保留；candidate inactive |

### 成功标准（验证视角）

- 每条 SYS-F/IF 追溯到上游（source 或 open）。
- 接口方向与对端可追溯或 open。
- 验证方法显式；无 HARA/TSR/TSC。
- 状态保守：`passed_with_open_items` / `failed`，**无** approved/compliant。

### Forbidden Claims（验证必查 · P0）

无充分 T0/T1 与 HITL 时禁止：

- SyRS is approved / **系统需求已批准**
- requirements are complete and compliant / **需求完整且合规**
- ASPICE SYS.2 satisfied / **ASPICE Level X 达成**
- ISO 26262 compliant / **已满足功能安全合规**
- ready for production release / **可量产**
- risk is accepted / compliance is confirmed

### P0 失效项全集

| 失效 | 后果 |
|---|---|
| sample 支撑 SYS-xx/限值 | 事实来源违规 |
| 草稿含 HARA/ASIL/SG/TSR | 文档类型漂移 |
| SYS-xx 无上游链接且标已确认 | 不可追溯 |
| 接口无方向且标已确认 | 不可集成 |
| 含 forbidden final claims | 越权结论 |
| 静默填需求/限值（无 EVD 无 open） | 不可追溯 |

### 审查结论边界

仅允许：`passed_with_open_items` / `failed`。禁止 `validated`、`approved`、`ASPICE compliant`。

## 本步 Review / Checklist 要点

### VC-1 · Artifact 链完整性

- [ ] `manifest.json`、`task_brief.json` 存在
- [ ] `inputs/input_inventory.json`、`knowledge/source_index.json`、`knowledge/provenance_index.json` 存在
- [ ] `plans/template_structure.json`、`outline_l1.md`、`outline_l2.md`、`section_writing_plans.json`、`evidence_map.json`、`citation_plan.json`、`outline_final.md`、`section_tasks.json`、`claim_support_matrix.json`、`writing_plan.md`、`unresolved_questions.md` 齐全
- [ ] `draft/full_draft.md`、`review/review_report.json` 存在
- [ ] `trace/session_trace.jsonl`、`trace/hitl_decisions.jsonl` 存在

### VC-2 · Tier 合规与 Provenance

- [ ] critical claim 在 `claim_support_matrix.json` 中**全部**有支撑（EVD 或 NEEDS_USER_CONFIRMATION）
- [ ] critical claim 支撑 tier ∈ {T0, T1}；**禁止** T4、T5
- [ ] 每条 EVD 含：`source_file_id` + L1 + L2 + L3 + `location` + `excerpt`
- [ ] 接口 EVD：含 `direction` 字段或对应 L3 摘录显示方向信息
- [ ] 性能/环境/诊断 EVD：含数值 + 单位 + 工况（若 source 有）

### VC-3 · Forbidden Claims 扫描

- [ ] 草稿与 final 报告**不**包含任意：
  - `SyRS is approved` / **「SyRS 已批准」**
  - `requirements (are) complete and compliant` / **「需求完整且合规」**
  - `ASPICE SYS.2 satisfied` / `ASPICE Level [0-9]+ achieved`
  - `ISO 26262 compliant` / **「已满足功能安全合规」**
  - `ready for production (release)` / **「可量产」**
  - `risk is accepted` / `compliance is confirmed` / `validated`
- [ ] 文档状态字段仅允许：`draft` / `ready_for_human_review` / `finalized_with_open_items` / `blocked_pending_confirmation` / `passed_with_open_items` / `failed`

### VC-4 · 文档类型纯净性扫描

- [ ] 草稿**不出现**字段或章节：`hazard`、`hazardous event`、`S/E/C`、`ASIL`、`Safety Goal`、`safe state`（新建）、`TSR`、`technical safety mechanism`、`HSC`、`SSC`、`SwRS table`、`HwRS table`
- [ ] SEC-SAFE 仅出现 **引用** 字段，不出现新分析字段
- [ ] 无 `hazard_*` / `asil_*` / `tsr_*` 类 claim 类型在 `claim_support_matrix.json`

### VC-5 · HITL 与 candidate 状态

- [ ] `NEEDS_USER_CONFIRMATION` 数量 ≥ `task_brief.critical_claims` 中 unconfirmed 数量
- [ ] **不存在**「HITL pending → confirmed」的静默改写记录（须有 `trace/hitl_decisions.jsonl` 条目）
- [ ] `learning/candidate_profile_update.yaml` 与 `candidate_skill_patch.md`：`active: false` 或 `status: proposed`
- [ ] 无自动启用 candidate 的记录

### 机器/规则化 Checklist（可脚本化）

| 规则 | 描述 |
|---|---|
| ID 命名 | SYS-F-xxx / SYS-IF-xxx / SYS-PERF-xxx 等正则匹配，唯一 |
| shall 句式 | 需求语句必含 `shall` 或 `应`；不允许 `will`、`should`（除非 Should 优先级行） |
| Direction 列 | SYS-IF 表 Direction ∈ {In, Out, Bidirectional, NEEDS_USER_CONFIRMATION} |
| 双向追溯 | 每条 SYS-xx 至少 1 个上游 ID 或 `orphan`；每个 SWRS ID 至少 1 个下游 SYS-xx 或显式 open |
| 列完整性 | SYS-F 表 8 列、SYS-IF 表 9 列、SEC-TRACE 矩阵 5 列齐全 |
| 单位检查 | SEC-PERF / SEC-ENV 数字带单位（℃、V、ms、kHz、km/h 等） |
| 重复检查 | SYS-F / SYS-IF / SWRS ID 无重复；多条同一 shall 表述合并或编号区分 |

### From-Scratch 专属 Checklist

- [ ] 大量 `NEEDS_USER_CONFIRMATION` 是预期，**不**触发 `failed`
- [ ] 限值数字 `NEEDS_USER_CONFIRMATION` 状态在 verify 后保留
- [ ] SEC-SAFE 若无 fsr_source，须为 placeholder + open，**不**误标 confirmed

### With-Reference 专属 Checklist

- [ ] **机器扫描**：`evidence_map.json` 与 `claim_support_matrix.json` 中任何 `source_file_id` ≠ 参考 SyRS file_id（**P0**）
- [ ] 参考 SyRS file_id 在 `input_inventory.json` 中 `role=sample` 且 `is_fact_source=false` 自始至终
- [ ] SEC-DIFF 存在；至少一行；行内有具体差异类型
- [ ] `claim_support_matrix.json` 不含 `delta_*` 类型的 T4 EVD

### ASPICE / ISO 维度对照 Checklist

- [ ] ASPICE SYS.2 BP5：双向追溯机器规则全通过或 open
- [ ] ASPICE SYS.2 BP2：每个 SYS-F/IF 有 Verification method 字段（值或 open）
- [ ] ISO 26262-3 §5：草稿无 hazard / ASIL / SG 字样
- [ ] ISO 26262-3 §7：SEC-SAFE 引用范围与 fsr_source 显式列表一致

### 验证结论边界

仅允许：

- `passed_with_open_items`：所有 P0 关闭，剩余 open 项归 NEEDS_USER_CONFIRMATION
- `failed`：存在未处理 P0

**禁止**：`validated`、`approved`、`ASPICE compliant`、`ISO 26262 compliant`、`production ready`。

### 常见 P0（验证必查）

| 失效 | 后果 |
|---|---|
| sample 支撑 SYS-xx / 限值 / 接口 | 事实来源违规 |
| 静默填值（无 EVD 无 open） | 不可追溯 |
| 含 forbidden final claims | 越权结论 |
| SYS-IF Direction 空白且标 confirmed | 不可集成 |
| HITL pending 被自动改 confirmed | 控制失效 |
| Candidate 自动启用 | 学习边界失效 |
| With-Reference：参考 SyRS file_id 进 evidence_map | 事实来源违规 |

### 常见 P1

- ID 命名不一致
- 单位缺失
- 重复 ID
- artifact 文件存在但内容空
- HITL 决策记录 `decision` 字段为空

## A1 / A2 / B

**A1**：每项 CHECK 有 pass/fail；P0 无遗漏；状态保守。  
**A2**：修复 blocker 后重验；按机器规则逐项校正。  
**B**：status 保守（`passed_with_open_items` / `failed`），无 approved / compliant。
