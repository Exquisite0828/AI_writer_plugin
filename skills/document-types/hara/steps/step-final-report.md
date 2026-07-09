# HARA 子 skill · Step 13 · 最终报告 (Final Report)

通用骨架：`skills/workflow-steps/step-final-report/SKILL.md`。HARA 根规则：`skills/document-types/hara/SKILL.md`。

## Purpose

把修订后的 HARA 草稿、审查、验证、open items 和 evidence traceability 汇编为供合格人工审查的最终包。final report 是 review-ready artifact，不替代 HARA professional sign-off、Confirmation Review 或 ISO 26262 compliance certification。

## Allowed Status

仅使用保守状态：

- `ready_for_human_review`：无 P0、产物齐全、open items 已汇总。
- `finalized_with_open_items`：P0 清除，仍有 P1/P2 或 `NEEDS_USER_CONFIRMATION`。
- `blocked_pending_confirmation`：存在未修复阻断问题。

禁止：`approved` / `validated` / `compliant` / `completed` / `HARA 已完成` / `ASIL D（已批准）` 或等价批准语义。

## Required Package

- `final/final_report.md` 或 HARA report body。
- `final/delivery_summary.md`。
- open items registry：全部 `NEEDS_USER_CONFIRMATION`、pending、knowledge gaps。
- evidence traceability：claim → EVD → file_id + L1/L2/L3 + location + tier。
- review/verification/revision summary。
- Confirmation Review / sign-off placeholders when required; placeholders are not approvals.

Mandatory report content: document info, scope/standard version, references/terms, item definition, operational situations, hazards, HE, S/E/C, ASIL candidates, safety goals with Safe State/FTTI, open issues, verification record, traceability matrix, signature placeholders, and With-Reference Differences from Reference HARA.

## Required Disclaimer

Final report must explicitly state, in Chinese or equivalent:

```text
本报告由 AI 辅助工具生成，是供具备资质工程师审查的准备材料。
本报告不等于 HARA 专业批准或 ISO 26262 合规认证，不等于 Confirmation Review。
所有 hazard、hazardous event、S/E/C、ASIL candidate、安全目标和 final acceptability 在签字前保持 pending / NEEDS_USER_CONFIRMATION。
```

## Self-Check

- 全文无专业批准措辞。
- document_status 是允许的保守状态。
- open_items_registry 覆盖所有 pending。
- evidence traceability 可回溯。
- ASIL 仅为 candidate；SG 仅为 candidate。
- final package 未关闭无证据的 critical claim，未把 sample/reference 当事实。

## A1 / A2 / B

**A1**：核对最终包未被误写为 HARA 批准、状态保守、critical claim/open items pending、artifact contract 满足。
**A2**：汇编 final report 和 delivery summary，补齐 open items/evidence traceability/disclaimer；不改变专业结论状态。
**B**：subagent 核对 final report 不等于专业批准或合规认证，且未移除 `NEEDS_USER_CONFIRMATION`。
