# FSR 子 skill · Step 11 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/FunctionalSafetyRequirement/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 链、tier 合规、**TSC deferred**、forbidden claims。
- 失败写入 `verify/failures.md`。

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

### 成功标准（§2.2 验证视角）

- 每条 FSR 追溯到 SG（source 或 open）。
- ASIL 有方向与对端级追溯（来自 SG）。
- 验证方法显式；无 TSC。
- 状态保守：`passed_with_open_items` / `failed`，**无** approved/compliant。

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

仅允许：`passed_with_open_items` / `failed`。禁止 `validated`、`approved`、`ISO 26262 compliant`。

## 本步 Review / Checklist 要点

### VC-1～VC-5 Checklist

| VC | 要点 |
|---|---|
| VC-1 | artifact 链完整 |
| VC-2 | 无 T4/T5；FSR/SG/ASIL EVD 有 provenance |
| VC-3 | 无 forbidden 措辞 |
| VC-4 | 无 TSC；无 HARA 危害表渗入 |
| VC-5 | `NEEDS_USER_CONFIRMATION` 保留；candidate inactive |

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

**A1**：每项 CHECK 有 pass/fail；P0 无遗漏。  
**A2**：修复 blocker 后重验。  
**B**：status 保守，无 approved。
