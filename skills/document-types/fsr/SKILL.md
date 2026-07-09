---
name: fsr-document-type
description: 中文优先指导 fsr document type work，同时保留 functional safety requirement、safety goal、ASIL、source tier、provenance、sample/reference、HITL、final-report、TSC-deferred 和 candidate-update boundaries。
---

# FSR Document Type Skill

Use this guideline for `task_type: fsr`. Default communication is Chinese; keep `fsr`, Functional Safety Requirements, Safety Goals, ASIL, TSC deferred, HITL, NEEDS_USER_CONFIRMATION, source tier, and artifact field names.

## Purpose

`fsr` is an official L3 built-in for review-ready Functional Safety Requirements packages. It organizes FSR candidates, Safety Goal traceability, ASIL inheritance, rationale, verification method candidates, assumptions, limitations, and open confirmations. It must not approve safety requirements, confirm compliance, validate ASIL inheritance, or claim completeness without T0/T1 evidence.

Use the shared plugin workflow and deterministic engine. No fsr-specific pipeline, no `fsr_pipeline.py`, no duplicated workflow.

## TSC Boundary

TSC is downstream under `task_type: TechnicalSafetyConcept`. FSR output must not create technical safety requirements, technical safety mechanisms, technical safety concept sections, or TSC final facts. Downstream technical allocation may be an open handoff note only when supported by source.

## Typical Inputs And Sections

T1 source examples: item definition context, confirmed Safety Goals, HARA summary or safety-goal trace extract, project constraints. Template/checklist/reference/sample keep their roles.

Default sections: purpose/scope, inputs/assumptions, item summary, Safety Goal traceability, FSR table, ASIL inheritance/rationale, verification method candidates, limitations/open confirmations, review summary, final boundary.

FSR tables should trace requirement ID, statement, linked SG, ASIL, rationale, verification method, evidence source, and confirmation status. Missing inputs become open items.

## Critical Claims

Critical claims include FSR wording, SG linkage, ASIL inheritance, safe state linkage, verification method, completeness, sufficiency, final FSR approval, and compliance conclusion. They require source or HITL; otherwise keep `NEEDS_USER_CONFIRMATION`.

Do not automatically finalize FSR wording, SG linkage, ASIL inheritance, verification adequacy, completeness/sufficiency, approval, or compliance. A HARA summary supports only the trace it explicitly contains; it is not blanket approval.

## Forbidden Final Claims

Do not write that FSR set/requirements are approved, complete and compliant, safety goals fully satisfied, ASIL inheritance validated, verification method sufficient, no open safety issue remains, production ready, risk accepted, or compliance confirmed unless a separate human approval process and evidence support it.

## Source Policy

T0=HITL, T1=project source, T2=template/checklist, T3=reference methodology/terminology, T4=sample shape/style, T5=inference. sample is not fact source. reference cannot prove project facts. T3/T4/T5 cannot support critical claim by themselves.

## Review / Verification Focus

Check template completeness, SG traceability, unsupported FSR wording, unsupported ASIL inheritance, unsupported verification claims, sample/reference misuse, TSC leakage, unconfirmed completeness/compliance, required artifacts, citation integrity, provenance, final report not approval, candidate update inactive.

Candidate updates remain proposed/inactive and must not overwrite stable Skill files or promote profiles.
