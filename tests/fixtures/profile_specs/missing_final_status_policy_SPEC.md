# Missing Final Status Policy Spec

Target task_type: generic_document

```yaml document_profile
profile_id: candidate.missing_final_status_policy
profile_version: 0.1.0-candidate
task_type: generic_document
display_name: Generic Document
description: Invalid profile missing final status policy.
default_sections:
  - Background
required_sections:
  - background
optional_sections: []
critical_claims:
  - final decision recommendation
requires_human_confirmation:
  - final decision recommendation
forbidden_final_claims:
  - is approved
confirmation_marker: NEEDS_USER_CONFIRMATION
fact_source_roles:
  - source
non_fact_source_roles:
  - sample
  - template
  - checklist
  - reference
reference_policy: Reference materials may support methodology but must not prove project-specific facts.
sample_policy: Sample documents may guide structure and style but must not supply project-specific facts.
review_focus:
  - unsupported critical claims
verification_focus:
  - sample not fact source
candidate_learning_policy: Generate candidate updates only; keep proposed/inactive unless explicitly approved.
terminology: {}
output_labels: {}
```

