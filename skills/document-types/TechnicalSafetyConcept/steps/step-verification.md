# TSC 子 skill · Step 11 · 验证

骨架：`skills/workflow-steps/step-verification/SKILL.md`。领域规则：`skills/document-types/TechnicalSafetyConcept/SKILL.md`。

## 本步目的要点

- 确定性检查：artifact 链、tier 合规、**HSC/SSC deferred**、forbidden claims。
- 失败写入 `verify/failures.md`。

## TSC 方法论（本步定位）

本步对应 **阶段 7** 中的 **形式/合规验证**（机器检查 + 独立审查补充）。

### 形式验证与阶段 7 检查项对齐

除 VC-1～VC-5 外，须机器/清单验证阶段 7 六项：

- [ ] 样例/参考未当事实（VC-2）
- [ ] 每条 TSR→FSR/SG（VC-2）
- [ ] 安全状态与 HARA 一致或有差异记录
- [ ] FTTI 链路可解释或 open
- [ ] 无 forbidden 措辞（VC-3）
- [ ] open 未静默闭合（VC-5）

### 形式/合规验证（VC-1～VC-5）

| 检查编号 | 验证要点 |
|---|---|
| VC-1 | manifest → source_index → … → draft → review → unresolved 完整 |
| VC-2 | critical claim 无 T4/T5；TSR/FSR/SG/机制 EVD 含 L1/L2/L3 provenance |
| VC-3 | 无 forbidden 措辞 |
| VC-4 | 草稿无 HSC/SSC 表/章节；无新 HARA 危害表渗入 |
| VC-5 | `NEEDS_USER_CONFIRMATION` 保留；candidate inactive |

### 成功标准（验证视角）

- 每条 TSR 追溯到 FSR 与 SG（source 或 open）。
- 架构分配与机制落点可追溯或 open。
- ASIL 有方向与对端级追溯（来自 SG/FSR）。
- FTTI 主张显式；无 HSC/SSC。
- 验证方法显式；状态保守：`passed_with_open_items` / `failed`，**无** approved/compliant。

### Forbidden Claims（验证必查 · P0）

无充分 T0/T1 与 HITL 时禁止：

- TSC is approved / **技术安全概念已批准**
- requirements are complete and compliant / **需求完整且合规**
- safety goals / FSR are fully satisfied at technical level
- ASIL inheritance / decomposition is validated
- verification method is sufficient
- fault tolerance time requirements are fully met
- ready for production release / **可量产**
- risk is accepted / compliance is confirmed

### P0 失效项全集

| 失效 | 后果 |
|---|---|
| sample 支撑 TSR/机制/ASIL | 事实来源违规 |
| 草稿含 HSC/SSC 内容 | 文档类型漂移 |
| TSR 无 FSR 链接且标已确认 | 不可追溯 |
| 含 forbidden final claims | 越权结论 |
| 静默填 TSR/机制/ASIL（无 EVD 无 open） | 不可追溯 |
| FSR source 当 blanket 批准 | 批准边界错误 |
| TSR 仅为 FSR 复述 | Clause 8 精神不满足 |

### 审查结论边界

仅允许：`passed_with_open_items` / `failed`。禁止 `validated`、`approved`、`ISO 26262 compliant`。

## 本步 Review / Checklist 要点

### VC-1～VC-5 Checklist

| VC | 要点 |
|---|---|
| VC-1 | artifact 链完整 |
| VC-2 | 无 T4/T5；TSR/FSR/SG/机制 EVD 有 provenance |
| VC-3 | 无 forbidden 措辞 |
| VC-4 | 无 HSC/SSC；无 HARA 危害表渗入 |
| VC-5 | `NEEDS_USER_CONFIRMATION` 保留；candidate inactive |

### 情景差异

| 维度 | From-Scratch | With-Reference |
|---|---|---|
| 重点防 | 静默填值（无 EVD 无 open）→ **P0** | sample 支撑 critical claim → **P0** |
| status | 仅 `passed_with_open_items` / `failed` | 须验证参考 TSC `file_id` 始终 `is_fact_source=false` |

### 常见 P0（验证必查）

| 失效 | 后果 |
|---|---|
| sample 支撑 TSR/机制/ASIL | 事实来源违规 |
| 静默填 TSR/机制（无 EVD 无 open） | 不可追溯 |
| 含 forbidden final claims | 越权结论 |

## A1 / A2 / B

**A1**：每项 CHECK 有 pass/fail；P0 无遗漏。  
**A2**：修复 blocker 后重验。  
**B**：status 保守，无 approved。
