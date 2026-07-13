# HARA 子 skill · Step 9 · 验证 (Verification)

通用骨架：`skills/workflow-steps/step-verification/SKILL.md`。HARA 根规则：`skills/document-types/hara/SKILL.md`。

## Purpose

对 HARA 草稿、审查结果和关键 artifacts 做确定性验证。失败项必须写入 `verify/failures.md`，`verify_report.json` status 保守，不输出 `validated`、`approved`、`compliant` 等批准语义。验证不是专业判断或 Confirmation Review。

## Required Checks

| Group | Required checks |
|---|---|
| VC-1 artifacts | manifest/source_index/provenance_index/template/outline/claim_support_matrix/draft/review/unresolved questions 存在且可解析 |
| VC-2 source tier | critical claim 无 T4 sample；无 T5 推断；S/E/C 不仅由 T3 支撑；EVD 有 file_id + L1/L2/L3 + location；无旧式 chunk/SRC 证据 |
| VC-3 critical claim status | H、HE、S、E、C、ASIL、SG 保持 `NEEDS_USER_CONFIRMATION`；SG 禁止性措辞；SG 含 Safe State 和 FTTI |
| VC-4 ASIL logic | ASIL candidate = S × E × C 按 ISO 26262-3 Table 4；ASIL>QM 的 HE 有 SG；ASIL=QM 的 HE 无 SG |
| VC-5 forbidden operations | 无批准措辞；pending 标记保留；candidate update proposed/inactive；无静默解析失败 |

With-Reference 额外检查：sample 内容未进入 critical claim 引用槽；Δ-Analysis 存在且差异来自本项目 source。

## Output Rules

- 每个 CHECK-ID 有 pass/fail 判定；fail 进入 `verify/failures.md`。
- P0 fail 写入 `### P0 (Blocking)`；P1/P2 分节列出；passed CHECK-ID 可列在 `### Passed`。
- `verify_report.status` 只能为 `passed_with_open_items` / `failed` / `blocked` 或当前 contract 支持的保守值；不得用批准状态。
- Confirmation Review 独立性要求只能作为占位/提醒：AI verify_report 不等于 Confirmation Review。

P0 examples: 失败项静默通过；status 写 approved/validated/compliant；独立性等级与最高 ASIL 不匹配；ASIL≥B 场景缺 Confirmation Reviewer 占位。

## A1 / A2 / B

**A1**：核对 failures/report 是否真实反映失败项、status 保守、VC-1~VC-5 逐项有结论、sample 非事实。
**A2**：按 REQUIRED_CHECKS 执行确定性验证，收集 blocking_failures，写 failures/report。
**B**：Stage review worker 核对无静默通过、无批准语义、pending/candidate inactive/source tier/provenance 全部保留。
