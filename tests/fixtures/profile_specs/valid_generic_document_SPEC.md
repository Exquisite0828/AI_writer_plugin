# Generic Document Candidate Profile Spec

Spec title: Generic Document Candidate Profile Spec
Spec version: 0.1.0
Spec status: candidate
Target task_type: generic_document
Target display_name: Generic Document
Owner / author: AI writing plugin maintainers
Last updated: 2026-06-07
Intended support level: L1

## Purpose

This fixture describes the generic document mode as a Markdown Spec input for the Phase N3 profile-from-spec generator.

## Structured Profile Block

```yaml document_profile
profile_id: candidate.generic_document
profile_version: 0.1.0-candidate
task_type: generic_document
display_name: Generic Document
description: Candidate profile generated from a Markdown Spec for generic professional documents.
default_sections:
  - Background and Scope
  - Confirmed Source Facts
  - Proposed Approach
  - Risks and Open Questions
  - Human Confirmations
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
  final_report_title: Final Generic Document Package
```

