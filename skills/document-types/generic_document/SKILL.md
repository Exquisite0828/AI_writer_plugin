---
name: generic-document-type
description: 中文优先指导 generic_document mode 和 external document_profile.yaml use，同时保留 L1/L2/L3 boundaries、Markdown Spec candidate-profile rules、provenance、HITL、sample/reference 和 final-report limits。
---

# Generic Document Skill

Use this skill for `task_type: generic_document` and for external profile runs such as `custom_technical_note`. Default communication is Chinese; keep `generic_document`, `document_profile.yaml`, Markdown Spec, candidate profile, custom_technical_note, HITL, NEEDS_USER_CONFIRMATION.

## Purpose

`generic_document` is L1 generic mode, not an official L3 professional document type. It runs the shared evidence-aware workflow when the user provides source, template, checklist, sample, reference, task, or profile information, but it does not promise complete domain professional judgment.

External `document_profile.yaml` is an L2/customer profile mechanism and must validate before use. `custom_technical_note` is an external profile demo, not official L3.

## Inputs And Sections

Inputs may include project `source`, `template`, `checklist`, `reference`, `sample`, optional validated profile, or an upstream Markdown Spec used to create a candidate profile.

Default sections: Background and Scope, Confirmed Source Facts, Proposed Approach, Risks and Open Questions, Decision and Human Confirmations, Review Summary. External profiles may provide sections after validation, but still use the shared pipeline and artifacts.

## Critical Claims

Critical claims may come from task YAML, generic rules, a validated external profile, or a reviewed spec-derived candidate profile. Defaults include final decision recommendation, approval/acceptance, compliance, release readiness, risk acceptance, cost/schedule commitment, security/safety claim, and any profile-declared critical claim. Without source or HITL, keep `NEEDS_USER_CONFIRMATION`, pending, or open.

Forbidden final claims without T0/T1 and HITL: approved, accepted, validated, compliant, risk accepted, production ready, release approved, fixed final cost/schedule, no unresolved risk.

## Source Policy

T0=HITL, T1=project source, T2=template/checklist, T3=reference methodology/background/terminology, T4=sample style/shape, T5=inference. sample is not fact source. reference cannot prove project facts. T3/T4/T5 cannot support critical claim by themselves.

Preserve provenance, source tier, claim/evidence/human-confirmation status, profile id, and profile version when available.

## Review / Verification Focus

Check template/checklist coverage, confirmed source fact separation, unsupported decision/approval/cost/schedule/compliance/readiness/security/safety claims, sample/reference misuse, unresolved risks, custom profile metadata, required artifacts, citation integrity, candidate update inactive, external profile validation, and document type terminology isolation.

## Profile Boundary

Invalid profiles fail safely. Markdown Spec is a human-readable upstream explanation layer; it can generate a proposed candidate profile but cannot replace a structured profile or built-in rules at runtime. Candidate profile outputs stay proposed/inactive and must not overwrite active profiles or stable skills.
