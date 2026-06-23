# FSR Document Type Spec

## 1. Purpose

FSR documents support traceable Functional Safety Requirements writing. They organize source-backed safety goal traces, functional safety requirement candidates, ASIL inheritance notes, verification method candidates, assumptions, and open confirmations.

The document type is conservative by default. It may summarize source-backed FSR evidence, but it must not approve safety requirements, validate ASIL inheritance, claim compliance, or conclude the requirement set is complete without source evidence and HITL.

## 2. Target Audience

Functional safety engineers, system requirements reviewers, safety managers, project maintainers, and stakeholders who need a reviewable functional safety requirement package.

## 3. Typical Inputs

- source: `item_definition_source.md`, `safety_goals_source.md`, `hara_summary_source.md`
- template: `fsr_template.md`
- checklist: `fsr_checklist.md`
- reference: `fsr_reference.md`
- sample: `fsr_sample.md`

The supplied HARA summary is source material only for the trace it explicitly contains. It is not a new HARA judgment and not an approval record.

## 4. Default Sections

- 文档目的和范围
- 输入材料和假设
- Item definition 摘要
- 安全目标追溯
- 功能安全需求表
- ASIL 继承和理由
- 验证方法候选
- 假设、限制和开放确认
- 审查摘要
- Final review boundary

## 5. Required Section Markers

FSR rules should preserve at least these semantic sections or equivalent headings:

- scope
- input materials
- item definition
- safety goals
- functional safety requirements
- ASIL inheritance
- verification
- limitations
- open confirmations

## 6. Critical Claims

- functional safety requirement wording
- safety goal linkage
- ASIL inheritance
- safe state linkage
- verification method
- requirement completeness
- requirement sufficiency
- final FSR approval
- final compliance conclusion

## 7. Requires Human Confirmation

- functional safety requirement wording
- safety goal linkage
- ASIL inheritance
- verification method adequacy
- requirement completeness and sufficiency conclusion
- final FSR approval or compliance conclusion

Even when project sources provide safety goals and ASIL values, wording adequacy, verification sufficiency, final completeness, compliance, and approval remain human review decisions unless explicit T0/HITL records exist.

## 8. Forbidden Final Claims

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

These phrases, or equivalent final approval semantics, must not be written as conclusions unless source evidence and recorded HITL confirmation support them.

## 9. Source Policy

`source` inputs may support project-specific facts, including item scope, supplied safety goals, supplied ASIL values, and explicit trace links.

`sample` FSR documents may guide report shape, section granularity, style, and table layout only. They must not supply project-specific requirement content, safety goal linkage, ASIL inheritance, verification status, completeness, compliance, or approval.

`reference` inputs may support functional-safety requirement writing methodology, terminology, or review criteria. They must not prove project-specific safety goals, ASIL values, requirement wording, verification status, completeness, compliance, or approval.

Templates and checklists are non-fact inputs unless a future phase explicitly changes the artifact contract.

## 10. Review Focus

- template completeness
- safety goal traceability
- unsupported functional safety requirement wording
- unsupported ASIL inheritance
- unsupported verification method claims
- sample misuse
- reference misuse as project fact
- TSC scope leakage
- unconfirmed completeness or compliance conclusion

## 11. Verification Focus

- required artifacts
- citation integrity
- sample not fact source
- reference not project fact source
- critical claims confirmation
- FSR claims require source evidence or HITL
- candidate update inactive
- TSC content not emitted from FSR (TSC is a separate downstream document type)

## 12. Final Status Policy

Default final status: `ready_for_human_review`.

Allowed final statuses:

- `ready_for_human_review`
- `finalized_with_open_items`
- `blocked_pending_confirmation`

No unconditional approved, compliant, validated, or production-ready status is allowed.

## 13. Recommended Demo Fixture Structure

Recommended committed fixture:

```text
examples/fsr_demo_fixture/
  task.yaml
  inputs/
    item_definition_source.md
    safety_goals_source.md
    hara_summary_source.md
    fsr_template.md
    fsr_checklist.md
    fsr_reference.md
    fsr_sample.md
```

The fixture should include enough source material to support part of the FSR package and at least one deliberately under-supported critical claim that remains `NEEDS_USER_CONFIRMATION` or an open item.

## 14. Gotchas

- Do not infer FSR approval from a sample.
- Do not use reference methodology to prove project-specific safety goals, ASIL, requirement wording, verification sufficiency, compliance, or approval.
- Do not treat a supplied HARA summary as a new HARA or blanket approval record.
- Do not turn an FSR run into TSC output.
- Do not claim completeness, compliance, or production readiness without source evidence and HITL.

## 15. TSC Boundary

TSC / Technical Safety Concept is a separate downstream document type (`task_type: TechnicalSafetyConcept`). FSR output may identify downstream technical allocation as an open item, but the FSR workflow itself must not generate a Technical Safety Concept, technical safety requirements, technical safety mechanisms, or TSC approval content.
