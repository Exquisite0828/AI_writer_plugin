---
name: fsr-document-type
description: 中文优先指导 fsr document type work，同时保留 functional safety requirement、safety goal、ASIL、source tier、provenance、sample/reference、HITL、final-report、TSC-deferred 和 candidate-update boundaries。
---

# FSR Document Type Skill

Use this guideline for `task_type: fsr`.

## 中文交互默认规则

默认用中文解释 FSR workflow、Safety Goal traceability、ASIL inheritance、requirement completeness、verification method 和 open confirmations。保留 `fsr`、Functional Safety Requirements、Safety Goals、ASIL、TSC deferred、HITL、NEEDS_USER_CONFIRMATION 等英文关键术语。

如果功能安全材料为英文，可以保留原文需求语句和引用片段；用户说明优先中文。不要把 FSR candidate wording 写成 safety requirement approval、compliance approval 或 TSC output。

This Skill.md is guideline material only. It must use the plugin workflow and must call the Python deterministic engine through `write-run` or `/ai-writing-plugin:write`. It is not prompt-only execution, and it does not replace artifact contracts, schema validation, source index, evidence trace, review, verify, HITL trace, or candidate update state control.

## Document Type Purpose

FSR supports review-ready Functional Safety Requirements packages. The input materials normally include item definition context, confirmed Safety Goals, a supplied HARA summary or safety-goal trace extract, project constraints, templates, checklists, references, and sample document shapes.

The FSR document type can draft and organize functional safety requirement candidates. It must not approve safety requirements, confirm compliance, validate ASIL inheritance, or claim the requirement set is complete without project source evidence or HITL.

There is no automatic professional approval in this workflow.

## Supported Level And Positioning

`fsr` is an official L3 built-in document type backed by built-in `DocumentTypeRules`, fixtures, regression tests, committed eval cases, and this domain guideline.

The command layer remains generic. There is no fsr-specific pipeline, no `fsr_pipeline.py`, and no duplicated workflow. The project rule is one plugin, one pipeline.

TSC deferred: Phase N8 does not create a TSC document type, TSC Skill, TSC fixture, TSC profile, or technical safety concept workflow.

## Typical Inputs

Recommended inputs:

- `item_definition_source.md` as `source`
- `safety_goals_source.md` as `source`
- `hara_summary_source.md` or a safety-goal trace extract as `source`
- `fsr_template.md` as `template`
- `fsr_checklist.md` as `checklist`
- `fsr_reference.md` as `reference`
- `fsr_sample.md` as `sample`

Only `source` inputs can support project facts. HITL / explicit human confirmation is T0 when captured by the workflow.

## Default / Expected Sections

The FSR default sections are:

- Document purpose and scope
- Input materials and assumptions
- Item definition summary
- Safety goal traceability
- Functional safety requirement table
- ASIL inheritance and rationale
- Verification method candidates
- Assumptions, limitations, and open confirmations
- Review summary
- Final review boundary

The table should keep requirement identifiers, requirement statements, linked Safety Goals, ASIL, rationale, verification method, evidence source, and confirmation status traceable. Missing inputs become open items.

## Critical Claims

FSR critical claim categories include:

- functional safety requirement wording
- safety goal linkage
- ASIL inheritance
- safe state linkage
- verification method
- requirement completeness
- requirement sufficiency
- final FSR approval
- final compliance conclusion

These require source or HITL. If evidence or a recorded human decision is missing, keep `NEEDS_USER_CONFIRMATION`.

## Requires Human Confirmation

Do not automatically finalize:

- functional safety requirement wording
- safety goal linkage
- ASIL inheritance
- verification method adequacy
- requirement completeness and sufficiency conclusion
- final FSR approval or compliance conclusion

Safety Goals and ASIL can be carried from project source material, but the final professional conclusion still needs human review. A HARA summary may support the trace it explicitly contains; it must not be used as a blanket approval for all FSR content.

## Forbidden Final Claims

The following are forbidden final claims unless explicit T0/T1 support and a separate human approval process allow them:

- FSR set is approved
- functional safety requirements are approved
- requirements are complete and compliant
- safety goals are fully satisfied
- ASIL inheritance is validated
- verification method is sufficient
- no open safety issue remains
- ready for production release
- risk is accepted
- compliance is confirmed

These are warning examples, not recommended output.

## Source / Sample / Reference / Provenance Policy

- Project source material is T1 when parsed and relevant.
- HITL / explicit human confirmation is T0.
- Template and checklist constraints are T2.
- `fsr_reference.md` is T3; it may support methodology or terminology but must not prove project-specific Safety Goals, ASIL, requirement wording, verification status, completeness, compliance, or approval.
- `fsr_sample.md` is T4; it can guide structure, style, section granularity, and table shape only.
- Generated / unknown inference is T5 and cannot support critical claim.

sample is not a fact source.
sample is not fact source.
reference cannot prove project facts.
T3/T4/T5 cannot support critical claim by themselves.
Every critical claim needs provenance and a source tier.

## Review Focus

Review focus includes:

- template completeness
- safety goal traceability
- unsupported functional safety requirement wording
- unsupported ASIL inheritance
- unsupported verification method claims
- sample misuse
- reference misuse as project fact
- TSC leakage
- unconfirmed completeness or compliance conclusion

## Verification Focus

Verification focus includes:

- required artifacts
- citation integrity
- source tier and provenance
- sample not fact source
- reference not project fact source
- critical claims confirmation
- FSR claims require source or HITL
- final report is not approval
- candidate update inactive
- TSC deferred and not emitted

## TSC Boundary

Do not create a TSC document.
Do not create technical safety requirements.
Do not create a technical safety concept report.
Do not create technical safety mechanisms as final facts.
Do not create an FSR-specific pipeline.

Downstream technical allocation may be listed as a future open item only when the source material justifies that boundary note. It must not become a TSC deliverable.

## Candidate Update Boundary

candidate update artifacts may be generated only as proposed / inactive material.

`candidate_profile_update.yaml`, `candidate_skill_patch.md`, and promotion reports must not auto-apply changes, must not overwrite stable Skill.md, and must not promote profiles without explicit human approval and eval gate evidence in a later workflow.

## Dependency And Platform Boundary

Use the existing deterministic Python engine. Do not add heavy dependencies. no RAG. no LangChain. no vector DB. Do not add a complex agent framework.

## Demo Fixture / Command

```bash
.venv/bin/python -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml
```

## Common Gotchas

- Do not infer FSR approval from a sample document.
- Do not use a reference to prove this project's Safety Goals or ASIL.
- Do not turn a supplied HARA summary into a new HARA judgment.
- Do not convert FSR output into TSC output.
- Do not claim completeness, compliance, verification sufficiency, or production release readiness without source or HITL.
