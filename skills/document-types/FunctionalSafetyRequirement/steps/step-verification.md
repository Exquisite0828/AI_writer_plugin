# FSR 子 skill · Step 11 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 链、tier 合规、**TSC deferred**、forbidden claims。
- 输出结构化 `verify/verify_report.json`，覆盖 FSR VC-1～VC-5；不得只写 summary。
- 失败写入 `verify/failures.md`；无失败也必须生成文件并显式说明无 P0/P1 blocking failures。

## FSR 方法论（本步定位）

本步对应 **阶段 6** 中的 **形式/合规验证**（安全工程师/机器检查）。

### 形式/合规验证（VC-1～VC-5）

| 检查编号 | 验证要点 |
|---|---|
| VC-1 | manifest → source_index → … → draft → review → unresolved 完整 |
| VC-2 | critical claim 无 T4/T5；FSR/SG/ASIL EVD 含 L1/L2/L3 provenance |
| VC-3 | 无 forbidden 措辞 |
| VC-4 | 草稿无 TSC 表/章节；无新 HARA 危害表渗入 |
| VC-5 | `NEEDS_USER_CONFIRMATION` 保留；candidate inactive |

### verify_report.json 结构化要求

`verify/verify_report.json` 必须包含 `checks[]`，且至少有以下 5 个 check：

| check_id | name | blocking 规则 |
|---|---|---|
| `FSR-VC-1` | artifact_chain_complete | manifest、source_index、provenance_index、template/outline、evidence/claim plan、draft、review、unresolved/open items 缺失或不可读时 failed/blocked |
| `FSR-VC-2` | provenance_and_tier_integrity | critical claim 使用 T4/T5，或 FSR/SG/ASIL EVD 缺 L1/L2/L3 provenance 时 failed/blocked |
| `FSR-VC-3` | forbidden_professional_claims_absent | 出现 approved/compliant/validated/ready for production/risk accepted 等越权结论时 failed |
| `FSR-VC-4` | no_tsc_or_hara_drift | 草稿生成 TSC 表/章节、重新做 HARA 危害表或重新分类 ASIL 时 failed |
| `FSR-VC-5` | open_confirmations_and_candidate_inactive | `NEEDS_USER_CONFIRMATION` 被移除、candidate update active/promoted，或 open critical claim 被写成已确认时 failed |

每个 check 必须写 `status`、`severity`、`details`、`related_artifacts`。只写 `verification_summary`、`All gates passed`、或没有 FSR-VC-1～FSR-VC-5 的报告，视为 **P0：验证产物无效**。

旧式或泛化 verification 格式不得接受为通过：

- 不得用 `overall_status` 替代 top-level `status`。
- 不得用 `verification_checks` 替代 `checks[]`。
- 不得用 `VC-001`、`VC-002` 等泛化编号替代 `FSR-VC-1`～`FSR-VC-5`。
- 不得只证明“内部一致性”，而漏掉 FSR 专属的 forbidden claims、TSC drift、HARA reclassification、candidate inactive 与 open confirmation 检查。

出现以上任一情况时，subagent 必须判定 P0、`revision_required=true`，并通过 A2 局部重写 `verify_report.json` / `failures.md`；如果无法修复，stage review `issues.json` 必须记录 P0 且 `requires_revision=true`，不得 accepted。

### failures.md 格式要求

`verify/failures.md` 必须始终存在，并至少包含：

- `# 验证失败项`
- run id
- 摘要
- `## P0/P1 Blocking Failures`
- `## Non-blocking Warnings`
- `## Pending HITL / NEEDS_USER_CONFIRMATION`
- `## Stage Boundary`

没有 P0/P1 时，`## P0/P1 Blocking Failures` 下写明 `No P0/P1 blocking failures found by mechanical verification.`；不得省略该文件。存在 failed / blocked check 时，必须按 `check_id` 写入对应失败项。

### 成功标准（§2.2 验证视角）

- 每条 FSR 追溯到 SG（source 或 open）。
- ASIL 有方向与对端级追溯（来自 SG）。
- 验证方法显式；无 TSC。
- 状态保守：`passed` / `passed_with_warnings` / `blocked` / `failed`，**无** approved/compliant/validated。

### Forbidden Claims（验证必查 · P0）

无充分 T0/T1 与 HITL 时禁止：

- FSR set is approved / **功能安全需求已批准**
- requirements are complete and compliant / **需求完整且合规**
- safety goals are fully satisfied
- ASIL inheritance is validated
- verification method is sufficient
- ready for production release / **可量产**
- risk is accepted / compliance is confirmed

### P0 失效项全集

| 失效 | 后果 |
|---|---|
| sample 支撑 FSR/SG/ASIL | 事实来源违规 |
| 草稿含 TSC 内容 | 文档类型漂移 |
| FSR 无 SG 链接且标已确认 | 不可追溯 |
| 含 forbidden final claims | 越权结论 |
| 静默填需求/ASIL（无 EVD 无 open） | 不可追溯 |
| HARA 摘要当 blanket 批准 | 批准边界错误 |

### 审查结论边界

仅允许：`passed` / `passed_with_warnings` / `blocked` / `failed`。禁止 `validated`、`approved`、`ISO 26262 compliant`。

## 本步 Review / Checklist 要点

### VC-1～VC-5 Checklist

| VC | 要点 |
|---|---|
| FSR-VC-1 | artifact 链完整 |
| FSR-VC-2 | 无 T4/T5；FSR/SG/ASIL EVD 有 provenance |
| FSR-VC-3 | 无 forbidden 措辞 |
| FSR-VC-4 | 无 TSC；无 HARA 危害表渗入 |
| FSR-VC-5 | `NEEDS_USER_CONFIRMATION` 保留；candidate inactive |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 静默填值（无 EVD 无 open）→ **P0** | sample 支撑 critical claim → **P0** |
| status | 仅 `passed_with_open_items` / `failed` | 须验证参考 FSR `file_id` 始终 `is_fact_source=false` |

### 常见 P0（验证必查）

| 失效 | 后果 |
|---|---|
| sample 支撑 FSR/SG/ASIL | 事实来源违规 |
| 静默填需求/ASIL（无 EVD 无 open） | 不可追溯 |
| 含 forbidden final claims | 越权结论 |

## A1 / A2 / B

**A1**：先做 meta-contract 检查：`verify_report.json` 必须含 top-level `status`、`checks[]`、FSR-VC-1～FSR-VC-5 逐项结果；不得出现旧式 `overall_status` / `verification_checks` / `VC-001` 作为替代。再确认 `failures.md` 存在，P0/P1 无遗漏。
**A2**：只针对 blocker 局部修复受影响 verification artifact 后重验。
**B**：status 保守，无 approved/compliant/validated；summary-only verification 是 P0。
