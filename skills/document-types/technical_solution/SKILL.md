---
name: technical-solution-document-type
description: 中文优先指导 technical_solution document type work，同时保留 architecture、performance、security、cost、rollout、source tier、provenance、sample/reference、HITL 和 no-HARA-leakage boundaries。
---

# Technical Solution Document Type Skill

Use this skill for `task_type: technical_solution` / technical solution / 技术方案.

## 中文交互默认规则

默认用中文解释技术方案 workflow、输入材料、架构决策边界、open confirmations、review/verify 结果和最终交付物。保留 `technical_solution`、architecture decision、performance target、security boundary、HITL、NEEDS_USER_CONFIRMATION 等英文关键术语。

如果用户材料是英文，可以保留原文术语和引用片段；面向用户的步骤说明和风险提示优先中文。不要把中文输出写成架构批准、性能保证、安全批准、最终成本或 rollout risk acceptance。

## Document Type Purpose

technical_solution supports technical方案, backend, architecture, implementation, and technical review writing workflows. It organizes project context, requirements, architecture overview, data flow, interfaces, implementation plan, risks, rollout, and open issues.

It does not automatically approve architecture decisions.

## Supported Level And Positioning

`technical_solution` is an official L3 product/domain asset label backed in the current tree by fixtures and this domain guideline. Current Python has no document-type registry, executable type rules, or end-to-end content test.

The command layer remains generic. There is no technical_solution-specific pipeline.

## Typical Inputs

The demo fixture shows the expected material roles:

- `system_context.md` as `source`
- `requirements.md` as `source`
- `solution_template.md` as `template`
- `checklist.md` as `checklist`
- `architecture_reference.md` as `reference`
- `sample_solution.md` as `sample`

## Default / Expected Sections

The technical_solution default sections are:

- Background
- Goals and Non-goals
- Requirements
- Architecture Overview
- Data Flow and Interfaces
- Implementation Plan
- Risks and Trade-offs
- Rollout Plan
- Open Issues

## Critical Claims

technical_solution critical claims include:

- architecture decision
- performance target
- security boundary
- deployment risk
- cost estimate
- compatibility constraint
- rollout risk acceptance

These claims need source evidence or HITL confirmation. If evidence or user confirmation is missing, keep `NEEDS_USER_CONFIRMATION` or list an open confirmation.

## Requires Human Confirmation

The following must not be finalized automatically:

- final architecture decision
- performance target
- security boundary
- cost estimate
- rollout risk acceptance

The plugin must not automatically approve architecture decisions, guarantee performance, define final cost, approve security boundary, or accept rollout risk.

## Forbidden Final Claims

Without sufficient T0/T1 support and explicit HITL, do not write final claims such as:

- architecture is approved
- no security risk exists
- performance target is guaranteed
- cost is final
- rollout is risk-free
- production ready

These are warning examples, not recommended output.

## Source / Sample / Reference / Provenance Policy

- project source is T1 and can support project-specific facts when parsed and relevant.
- HITL / explicit human confirmation is T0.
- template and checklist constraints are T2.
- architecture_reference is T3; it can support general technical rationale or methodology but must not prove project-specific requirements, constraints, architecture decision, performance target, security boundary, cost estimate, or rollout risk acceptance.
- sample_solution is T4; it can guide structure, style, and expression granularity only.
- generated / unknown inference is T5 and cannot support critical claim.

sample_solution must not be used as fact source.
sample is not fact source.
reference cannot prove project facts.
reference must not prove project-specific requirements or constraints.
T3/T4/T5 cannot support critical claim by themselves.

## Review Focus

Review focus includes:

- template completeness
- requirements coverage
- unsupported architecture decisions
- unsupported performance or cost claims
- unsupported security boundary claims
- unsupported deployment or compatibility risk claims
- unsupported rollout risk acceptance
- sample misuse
- reference misuse as project fact
- unresolved risks and trade-offs

## Verification Focus

Verification focus includes:

- required artifacts
- citation integrity
- source tier and provenance
- sample not fact source
- reference not project fact source
- critical claims confirmation
- document type terminology isolation
- HARA leakage warning enforcement
- candidate update inactive

## HARA Leakage Warning

technical_solution output must not leak HARA-only terminology. The warning terms include:

- ASIL
- S/E/C
- hazardous event
- safety goal
- severity rating
- exposure rating
- controllability rating

These terms may appear in this Skill only as a no-HARA-leakage warning. They should not appear as technical_solution output content unless the user explicitly provides a project source that truly requires discussing HARA terminology, and even then it should be treated as a source-specific fact rather than generic technical_solution boilerplate.

## Final Report Boundary

The final package is for human review, not architecture approval. Valid final status values are `ready_for_human_review`, `finalized_with_open_items`, and `blocked_pending_confirmation`.

Unconfirmed critical claims remain pending until real HITL decisions are recorded. final report is not approval.

## Demo Boundary

Demo task paths are intentionally not listed in runtime skills. Use a specific user-selected task file only.

## Common Gotchas

- Do not use a sample solution as project facts.
- Do not use reference architecture material to prove project requirements or constraints.
- Do not write guaranteed performance, final cost, final security status, or accepted rollout risk without T0/T1 support.
- Do not introduce HARA terms into technical_solution output.
- candidate update proposed/inactive; generated `candidate_profile_update.yaml` and `candidate_skill_patch.md` must not overwrite a stable skill.
