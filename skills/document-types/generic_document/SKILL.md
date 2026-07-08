---
name: generic-document-type
description: 中文优先指导 generic_document mode 和 external document_profile.yaml use，同时保留 L1/L2/L3 boundaries、Markdown Spec candidate-profile rules、provenance、HITL、sample/reference 和 final-report limits。
---

# Generic Document Skill

Use this skill for `task_type: generic_document` and for explaining external profile runs such as `custom_technical_note`.

## 中文交互默认规则

默认用中文解释 generic_document workflow、external profile 使用方式、材料角色、critical claims、open confirmations 和 candidate updates。保留 `generic_document`、`document_profile.yaml`、Markdown Spec、candidate profile、profile-from-spec、custom_technical_note、HITL、NEEDS_USER_CONFIRMATION 等英文关键术语。

如果用户材料或 profile 字段为英文，可以保留字段名和引用片段；说明性文字优先中文。不要把 generic mode 或 external profile 描述成 official L3，也不要把 profile validation 写成专业批准。

## Document Type Purpose

generic_document supports evidence-aware professional document assistance when the user provides source, template, checklist, sample, reference, task, or profile information but there is no official L3 built-in document type.

It helps run the same plugin workflow and produces a review-ready package with open confirmations. It does not promise complete domain professional judgment.

## Supported Level And Positioning

`generic_document` is L1 generic mode, not an official L3 professional document type.

External `document_profile.yaml` is an L2 / customer profile mechanism. It must pass validation before use.

`custom_technical_note` is an external profile demo, not L3 and not an official built-in document type.

## Typical Inputs

Typical generic_document inputs include:

- project source material as `source`
- reusable document outline as `template`
- review requirements as `checklist`
- methodology or background as `reference`
- sample document as `sample`
- optional validated external `document_profile.yaml`
- optional Markdown Spec used upstream to create a candidate profile

## Default / Expected Sections

The generic_document default sections are:

- Background and Scope
- Confirmed Source Facts
- Proposed Approach
- Risks and Open Questions
- Decision and Human Confirmations
- Review Summary

External profiles may provide sections after validation, but they must still use the shared pipeline and artifact tree.

## Critical Claims

generic_document critical claims can come from task YAML, built-in generic rules, a validated external profile, or a spec-derived candidate profile after review.

Default generic critical claims include:

- final decision recommendation
- approval or acceptance conclusion
- compliance conclusion
- release readiness conclusion
- risk acceptance conclusion
- cost or schedule commitment
- security or safety claim

Critical claims are not automatically confirmed. They need source evidence or HITL, otherwise keep `NEEDS_USER_CONFIRMATION`, pending status, or an open item.

## Requires Human Confirmation

Requires human confirmation includes:

- final decision recommendation
- approval or acceptance conclusion
- compliance conclusion
- release readiness conclusion
- risk acceptance conclusion
- cost or schedule commitment
- security or safety claim
- any critical claim declared by a validated external profile

The engine must not convert external profile guidance into automatic professional approval.

## Forbidden Final Claims

Without sufficient T0/T1 support and explicit HITL, do not write final claims such as:

- is approved
- is accepted
- is validated
- is compliant
- risk is accepted
- production ready
- release approved
- final cost is fixed
- schedule is guaranteed
- no unresolved risk

These are warning examples, not recommended output.

## Source / Sample / Reference / Provenance Policy

- project source is T1 when parsed and relevant.
- HITL / explicit human confirmation is T0.
- template and checklist constraints are T2.
- reference is T3 and may support methodology, background, terminology, or review guidance only.
- sample is T4 and may support style, shape, table organization, section granularity, and wording style only.
- generated / unknown inference is T5 and cannot support critical claim.

sample is not fact source.
sample must not supply project facts, decisions, approvals, costs, schedules, compliance status, readiness, or risk acceptance.
reference cannot prove project facts.
reference is not project-specific fact support.
T3/T4/T5 cannot support critical claim by themselves.

Artifacts should preserve provenance, source tier, claim status, evidence status, human confirmation status, profile id, and profile version when available.

## Review Focus

Review focus includes:

- template completeness
- checklist coverage
- confirmed source fact separation
- unsupported decision or approval claims
- unsupported cost or schedule claims
- unsupported compliance or readiness claims
- unsupported security or safety claims
- sample misuse
- reference misuse as project fact
- unresolved risks and open questions
- custom profile metadata preservation

## Verification Focus

Verification focus includes:

- required artifacts
- citation integrity
- source tier and provenance
- sample not fact source
- reference not project fact source
- critical claims confirmation
- document type terminology isolation
- candidate update inactive
- external profile validation status
- profile id and profile version propagation

## Final Report Boundary

The generic_document final report is a review-ready package, not approval. Default final status should be `ready_for_human_review`, `finalized_with_open_items`, or `blocked_pending_confirmation`.

Open confirmations must remain visible when evidence or HITL is missing.

## Profile And Markdown Spec Boundary

External profile runs use validated `document_profile.yaml`. Invalid profiles must fail safely and must not become a successful final report.

Markdown Spec is a human-readable upstream explanation layer. It can be used by `profile-from-spec` to generate a candidate profile, but Markdown Spec is not a runtime rule and cannot directly replace the structured profile or built-in rules.

Candidate profile output from `profile-from-spec` is proposed / inactive and cannot overwrite an active profile.

## Demo Boundary

Demo task paths are intentionally not listed in runtime skills. Use a specific user-selected task file only.

## Common Gotchas

- Do not describe generic_document as an official L3 type.
- Do not describe custom_technical_note as L3.
- Do not treat external profile guidance as professional approval.
- Do not treat Markdown Spec as a runtime rule.
- Do not use sample or reference material as project facts.
- Do not add a per-document pipeline for customer profiles.
- candidate update proposed/inactive; `candidate_profile_update.yaml`, `candidate_skill_patch.md`, and candidate profile outputs must not automatically replace stable Skill files or active profiles.
