---
name: hara-document-type
description: 中文优先指导 HARA document type work，同时保留 HARA terminology、evidence、source tier、HITL、final-report、sample/reference 和 candidate-update boundaries。
---

# HARA Document Type Skill

Use this skill for `task_type: hara`.

## 中文交互默认规则

默认用中文向用户解释 HARA workflow、材料角色、open confirmations、pending 专业判断和最终 artifact。保留 HARA、hazard、hazardous event、S/E/C、ASIL、safety goal、HITL、NEEDS_USER_CONFIRMATION 等专业术语和机器字段。

如果用户输入或引用证据为英文，可以保留原文片段；说明、提醒和最终回复优先中文。中文表达不能把 HARA candidate wording 写成专业批准。

## Document Type Purpose

HARA supports functional-safety hazard analysis report assistance. It helps create a traceable, review-ready HARA package with evidence boundaries, open confirmations, and conservative candidate wording. It must not automatically approve HARA professional judgments.

## HARA 总过程概览

HARA（Hazard Analysis and Risk Assessment，危害分析与风险评估）是 ISO 26262-3 规定的功能安全核心活动，目的是：

- 识别 item（待分析系统）可能产生的危害行为
- 评估危害事件的风险等级（S/E/C → ASIL）
- 为需要功能安全措施的危害事件导出安全目标（Safety Goal）

HARA 输出是功能安全概念的起点，后续所有功能安全需求都须可追溯至 HARA 的安全目标。

本 plugin 通过 **13 个** step skill 驱动 HARA 报告写作（逻辑 Step 编号 1–6、9–15；引用计划与章节任务已并入 Step 6）；每步对应 `skills/document-types/hara/steps/step-*.md`，各步定位详见对应子 skill。


## Supported Level And Positioning

`hara` is an official L3 built-in document type backed by built-in `DocumentTypeRules`, fixtures, regression tests, and this domain guideline.

HARA output may and must preserve HARA terminology: hazard, hazardous event, severity, exposure, controllability, ASIL, S/E/C, risk level, and safety goal.

## Typical Inputs

Typical HARA inputs include:

- item definition source material
- operational situations and modes
- assumptions and constraints
- HARA template
- safety or review checklist
- functional safety methodology reference
- sample HARA report for style and table shape only

## Default / Expected Sections

The HARA default sections are:

- Document purpose and scope
- Input materials and assumptions
- Item definition summary
- Operational situations and modes
- Hazard identification
- Hazardous event analysis
- S/E/C rating table
- ASIL candidate
- Safety goals candidate
- Open issues and required confirmations
- Review summary

## Critical Claims

HARA critical claims include:

- hazard identification
- hazardous event
- severity rating
- exposure rating
- controllability rating
- ASIL or risk level
- safety goal
- final acceptability conclusion

These claims require source evidence or HITL confirmation. Without evidence or a recorded human decision, keep `NEEDS_USER_CONFIRMATION`.

## Requires Human Confirmation

HARA professional judgment cannot be finalized by AI alone. The following require qualified human review and recorded HITL confirmation:

- hazard identification
- hazardous event definition
- severity rating
- exposure rating
- controllability rating
- ASIL or risk level
- safety goal wording
- final acceptability conclusion

User confirmation must be recorded in `trace/hitl_decisions.jsonl` or an equivalent trace artifact.

## Forbidden Final Claims

Without sufficient T0/T1 support and explicit HITL, do not write final claims such as:

- final ASIL is approved
- final ASIL is
- ASIL is confirmed
- risk is acceptable
- hazard is confirmed
- safety goal is approved
- final acceptability conclusion
- final risk level is
- the rating is S1
- the rating is S2
- the rating is S3
- the rating is E1
- the rating is E2
- the rating is E3
- the rating is C1
- the rating is C2
- the rating is C3

These are warning examples, not recommended output.

## Source / Sample / Reference / Provenance Policy

- `source` materials can support project facts when parsed and relevant.
- HITL / explicit human confirmation is T0.
- project source is T1.
- template and checklist constraints are T2.
- reference methodology is T3 and cannot prove project hazard or rating.
- sample style material is T4 and cannot provide hazard, rating, ASIL, safety goal, or final conclusion.
- generated / unknown inference is T5 and cannot support critical claim.

sample is not fact source.
sample must not be used as fact source.
sample HARA reports may guide format, style, table shape, and wording style only.
reference must not prove project-specific facts.
reference cannot prove project facts.
T3/T4/T5 cannot support critical claim by themselves.

## Review Focus

Review focus includes:

- template completeness
- checklist coverage
- unsupported hazard identification
- unsupported hazardous event analysis
- unsupported severity, exposure, or controllability rating
- unsupported ASIL or risk level
- unsupported safety goal
- sample misuse
- reference misuse as project fact
- unconfirmed HARA professional judgments

## Verification Focus

Verification focus includes:

- required artifacts
- citation integrity
- source tier and provenance
- sample not fact source
- reference not project fact source
- critical claims confirmation
- `NEEDS_USER_CONFIRMATION` preservation
- candidate update inactive

## Final Report Boundary

The HARA `final_report.md` is a plugin-generated final package artifact for human review. final report is not approval, not formal compliance approval, and not qualified safety sign-off.

Valid conservative statuses include `finalized_with_open_items`, `ready_for_human_review`, and `blocked_pending_confirmation`. Unresolved HARA items must remain open.

## Demo Boundary

Demo task paths are intentionally not listed in runtime skills. Use a specific user-selected task file only.

## Common Gotchas

- Do not migrate hazard, hazardous event, S/E/C rating, ASIL, safety goal, or final conclusion from sample material.
- Do not let reference methodology prove project-specific hazard or rating.
- Do not remove `NEEDS_USER_CONFIRMATION` without real HITL.
- Do not convert a HARA final report into safety approval.
- candidate update proposed/inactive; generated `candidate_profile_update.yaml` and `candidate_skill_patch.md` must not overwrite a stable skill.


## 贯穿全程的核心原则

1. **事实来源严格分离**：sample 报告（T4）中的 hazard / 评级 / ASIL / safety goal，任何情况下不得作为本项目分析依据。
2. **所有 critical claim 保持 pending**：hazard、hazardous event、S/E/C 评级、ASIL candidate、safety goal，在未经具备资质工程师确认前统一保留 `NEEDS_USER_CONFIRMATION`。
3. **知识缺口显式记录**：输入材料不完整时不推断填值，标 `[PENDING]` 并显式登记 `knowledge_gap`。
4. **AI 不替代工程师判断**：HARA 报告是供人工审查的准备材料，不等于 ISO 26262 合规认证或专业 sign-off。
