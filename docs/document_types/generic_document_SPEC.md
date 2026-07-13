# Generic Document Markdown Spec

Implementation status: candidate design asset. The current Python package does not load the referenced profile or execute a generic-document content pipeline.

Spec title: Generic Document Markdown Spec
Spec version: 0.1.0
Spec status: candidate
Target task_type: generic_document
Target display_name: Generic Document
Owner / author: AI writing plugin maintainers
Last updated: 2026-06-07
Intended support level: L1

generic_document is a general-purpose mode, not a new official L3 document type. It supports professional documents that have project sources, a template, a checklist, optional references, and optional samples. This spec is an N3 example for producing a candidate profile package; it does not overwrite `profiles/document_types/generic_document.yaml`.

## 1. Document Purpose

The generic document mode helps users draft reviewable professional documents when there is no official L3 document type yet. It keeps evidence boundaries explicit and preserves open confirmations.

## 2. Target Audience

Project maintainers, reviewers, technical leads, and domain owners who need a conservative document package for human review.

## 3. Typical Use Cases

- Customer-specific notes or review packages.
- Internal process documents with clear source material.
- Early L1/L2 document types before an official L3 profile exists.

## 4. Typical Input Materials

- source: project-specific facts and constraints.
- template: document outline and expected section shape.
- checklist: review expectations.
- reference: methodology or terminology only.
- sample: structure and style only.

## 5. Role Boundaries

`source` may support project-specific facts. `sample` must not be used as a fact source. `reference` must not prove project-specific facts. Templates and checklists constrain structure and review coverage but do not automatically prove facts.

## 6. Default Sections

- 背景和范围
- 已确认来源事实
- 建议方案
- 风险和开放问题
- 人工确认

## 7. Required Sections

- background
- scope
- confirmed facts
- proposed approach
- open questions

## 8. Critical Claims

- final decision recommendation
- approval or acceptance conclusion
- compliance conclusion
- release readiness conclusion

## 9. Requires Human Confirmation

- final decision recommendation
- approval or acceptance conclusion
- compliance conclusion
- release readiness conclusion

## 10. Forbidden Final Claims

- is approved
- is accepted
- is validated
- is compliant
- production ready

## 11. Review Focus

- template completeness
- checklist coverage
- unsupported critical claims
- sample misuse
- reference misuse as project fact

## 12. Verification Focus

- required artifacts
- citation integrity
- sample not fact source
- reference not project fact source
- critical claims confirmation
- candidate update inactive

## 13. Sample Policy

Sample documents may guide structure and style but must not supply project-specific facts, decisions, approvals, compliance status, readiness, or risk acceptance.

## 14. Reference Policy

Reference materials may support structure, style, or methodology but must not prove project-specific facts, decisions, approvals, compliance status, readiness, or risk acceptance.

## 15. Final Status Policy

Default final status: `ready_for_human_review`.

Allowed statuses:

- `ready_for_human_review`
- `finalized_with_open_items`
- `blocked_pending_confirmation`

No approval-like status is allowed.

## 16. Candidate Learning Policy

Generate candidate updates only; keep proposed/inactive unless explicitly approved.

## 17. Common Gotchas

- Do not treat sample content as project facts.
- Do not treat reference content as project fact evidence.
- Do not turn unconfirmed critical claims into final approval.
- Do not promote this candidate automatically.

## 18. Recommended Demo Fixture Structure

```text
fixture_skeleton/
  task.yaml
  inputs/
    source.md
    template.md
    checklist.md
    reference.md
    sample.md
```

## 19. Human Review Checklist

- Confirm critical claims match the intended customer document.
- Confirm sample/reference policy is safe.
- Confirm final status policy is non-approval.
- Confirm the profile remains candidate/inactive.

## Structured Profile Block

```yaml document_profile
profile_id: candidate.generic_document
profile_version: 0.1.0-candidate
task_type: generic_document
display_name: Generic Document
description: Candidate profile generated from a Markdown Spec for generic professional documents.
default_sections:
  - 背景和范围
  - 已确认来源事实
  - 建议方案
  - 风险和开放问题
  - 人工确认
required_sections:
  - background
  - scope
  - confirmed facts
  - proposed approach
  - open questions
optional_sections:
  - review summary
critical_claims:
  - final decision recommendation
  - approval or acceptance conclusion
  - compliance conclusion
  - release readiness conclusion
requires_human_confirmation:
  - final decision recommendation
  - approval or acceptance conclusion
  - compliance conclusion
  - release readiness conclusion
forbidden_final_claims:
  - is approved
  - is accepted
  - is validated
  - is compliant
  - production ready
confirmation_marker: NEEDS_USER_CONFIRMATION
fact_source_roles:
  - source
non_fact_source_roles:
  - sample
  - template
  - checklist
  - reference
reference_policy: Reference materials may support structure, style, or methodology but must not prove project-specific facts, decisions, approvals, compliance status, readiness, or risk acceptance.
sample_policy: Sample documents may guide structure and style but must not supply project-specific facts, decisions, approvals, compliance status, readiness, or risk acceptance.
default_final_status: ready_for_human_review
allowed_final_statuses:
  - ready_for_human_review
  - finalized_with_open_items
  - blocked_pending_confirmation
review_focus:
  - template completeness
  - checklist coverage
  - unsupported critical claims
  - sample misuse
  - reference misuse as project fact
verification_focus:
  - required artifacts
  - citation integrity
  - sample not fact source
  - reference not project fact source
  - critical claims confirmation
  - candidate update inactive
candidate_learning_policy: Generate candidate updates only; keep proposed/inactive unless explicitly approved.
terminology:
  professional_judgment: generic document critical claim
output_labels:
  final_report_title: 通用文档最终交付包
```
