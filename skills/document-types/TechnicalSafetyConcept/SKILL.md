---
name: technical-safety-concept-document-type
description: 中文优先指导 Technical Safety Concept（TSC，技术安全概念）文档写作；保留 TSR、Safety Goal、FSR 追溯、ASIL、架构分配、安全机制、FTTI、source tier、HITL、HSC/SSC-deferred 与 candidate-update 约束。
---

# Technical Safety Concept Document Type Skill

Use this skill for `task_type: TechnicalSafetyConcept`. This runtime dir is present but is not made official by Round 3. Communicate in Chinese by default; keep TSC、TSR、FSR、Safety Goal、ASIL、safe state、FTTI/FDTI/FHTI、HSC deferred、SSC deferred、HITL、NEEDS_USER_CONFIRMATION.

## Purpose

TSC supports a review-ready ISO 26262-4 Clause 8 technical safety concept package. It organizes item/architecture context, SG/FSR traceability, TSR candidates, architecture allocation, technical safety mechanism concepts, fault detection/handling, warning/degradation, interface safety constraints, ASIL inheritance/decomposition, trace matrix, verification candidates, assumptions, and open confirmations.

It does not create HSC/SSC final deliverables, detailed hardware/software implementation, new HARA judgments, FSR/SG rewrites, sign-off, or compliance approval.

## Position

FSR says what safety function is required; TSC explains how those FSRs are allocated to system architecture, mechanisms, failure handling, timing, and interface constraints. HSC/SSC remain deferred downstream work.

## Typical Inputs

T1 source examples: item definition, confirmed SG list, confirmed FSR/FSC extract, HARA summary only for explicit FTTI/safe state/HE→SG trace, system architecture, project constraints. Template/checklist/reference/sample keep their roles.

Sample TSC may guide section/table shape only. It cannot support TSR wording, mechanism, ASIL, FTTI, architecture allocation, or compliance claims.

## Expected Sections

Scope/input boundary, architecture safety view, SG trace, FSR trace, TSR table, technical safety mechanisms, fault detection/handling, warning/degradation, interface safety requirements, ASIL inheritance/decomposition, trace matrix, verification candidates, assumptions/open confirmations, review status, optional SEC-DIFF for With-Reference.

## Critical Claims

Critical claims include TSR wording, FSR linkage, SG linkage, architecture allocation, safety mechanism concept, fault handling strategy, safe state/degradation linkage, interface safety requirement, ASIL inheritance/decomposition, verification method, completeness/sufficiency, and final TSC approval/compliance. They require T0/T1 support or remain `NEEDS_USER_CONFIRMATION`.

FSR source supports only explicitly stated FSR/SG links; HARA summary supports only explicitly stated FTTI/safe state/trace content. Neither is blanket approval.

## Forbidden Final Claims

Do not write TSC approved, requirements complete/compliant, SG/FSR fully satisfied at technical level, ASIL decomposition validated, verification method sufficient, FTTI fully met, production ready, risk accepted, compliance confirmed, or any sample-derived TSR/mechanism/allocation as project fact.

## Source Policy

T0=HITL, T1=project source, T2=template/checklist, T3=reference methodology, T4=sample shape/style, T5=inference. sample 绝不是 fact source. FSR source is not blanket approval. HARA summary is not new HARA or approval record.

## Review / Verification Focus

- Every TSR traces to FSR and SG or explicit open.
- Architecture allocation and mechanisms are consistent.
- FTTI/FDTI/FHTI are tabled, sourced, or open.
- ASIL inheritance/decomposition comes from source/HITL, not sample.
- No HSC/SSC leakage; no detailed implementation.
- No approval/compliance/production readiness language.
- `NEEDS_USER_CONFIRMATION` preserved.

Final report is review-ready, not formal sign-off and not HSC/SSC delivery.

## Scenario Focus

From-Scratch: check whether FSR/SG/architecture inputs are sufficient and gaps are honest. With-Reference: ensure reference TSC is sample, not fact; preserve SEC-DIFF / TASK-DIFF where applicable.
