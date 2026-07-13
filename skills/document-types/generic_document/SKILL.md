---
name: generic-document-type
description: 中文优先指导 generic_document 与 external profile 设计资产的 agent-runtime使用边界；当前 Python 不加载profile，同时保留provenance、HITL、sample/reference和final-report limits。
---

# Generic Document Skill

Use this skill for `task_type: generic_document` and when a user explicitly supplies external profile design material such as `custom_technical_note`. Current Python records task metadata but does not load or validate profiles. Default communication is Chinese; keep `generic_document`, `document_profile.yaml`, Markdown Spec, candidate profile, custom_technical_note, HITL, NEEDS_USER_CONFIRMATION.

## Purpose

`generic_document` is an L1 generic design/Skill asset, not an official L3 professional document type. Agent workers may use explicitly supplied source, template, checklist, sample, reference, task, or profile material as guidance, but current Python does not execute a generic content pipeline and no mode promises complete domain professional judgment.

External `document_profile.yaml` is a proposed L2/customer mechanism. `custom_technical_note` is a design/demo asset, not official L3. There is no current Python profile validator; do not describe a profile as active or validated.

## Inputs And Sections

Inputs may include project `source`, `template`, `checklist`, `reference`, `sample`, a user-selected profile design asset, or an upstream Markdown Spec used as worker guidance. Profile/Spec assets remain advisory because the current Python package does not load or validate them.

Default sections: Background and Scope, Confirmed Source Facts, Proposed Approach, Risks and Open Questions, Decision and Human Confirmations, Review Summary. A worker may adopt sections from an explicitly selected external profile as advisory guidance, but must not describe that profile as Python-validated or active.

## Critical Claims

Critical claims may come from task YAML or explicitly reviewed user guidance. Profile/spec fields are advisory until a future loader exists. Defaults include final decision recommendation, approval/acceptance, compliance, release readiness, risk acceptance, cost/schedule commitment, and security/safety claims. Without source or HITL, keep `NEEDS_USER_CONFIRMATION`, pending, or open.

Forbidden final claims without T0/T1 and HITL: approved, accepted, validated, compliant, risk accepted, production ready, release approved, fixed final cost/schedule, no unresolved risk.

## Source Policy

T0=HITL, T1=project source, T2=template/checklist, T3=reference methodology/background/terminology, T4=sample style/shape, T5=inference. sample is not fact source. reference cannot prove project facts. T3/T4/T5 cannot support critical claim by themselves.

Preserve provenance, source tier, claim/evidence/human-confirmation status, profile id, and profile version when available.

## Review / Verification Focus

Check template/checklist coverage, confirmed source fact separation, unsupported decision/approval/cost/schedule/compliance/readiness/security/safety claims, sample/reference misuse, unresolved risks, explicitly supplied profile metadata, required artifacts, citation integrity, candidate update inactive, and document type terminology isolation. Do not claim Python profile validation.

## Profile Boundary

Markdown Spec and profile YAML are human-readable design/config assets in the current tree. Python does not load, generate, or validate them. Any worker-created candidate output stays proposed/inactive and must not overwrite profiles or stable Skills.
