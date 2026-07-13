# Document Profile Design Assets

Status: design/configuration reference; not consumed or enforced by the current Python package.

The repository contains profile YAML and Markdown Spec assets that describe a future data-driven document-type mechanism. Current Python code records `task_type` in Phase 0 metadata but has no profile loader, profile schema validator, document-type registry, profile generator, eval runner, correction harvester, or promotion command.

## Current files

```text
profiles/document_types/generic_document.yaml
profiles/document_types/customer_demo/custom_technical_note.yaml
docs/document_types/generic_document_SPEC.md
docs/DOCUMENT_PROFILE_SPEC_TEMPLATE.md
```

These files are useful for design review and future active phases. Passing a `document_profile_path` in a task does not currently change Python behavior.

## Intended support model

The intended future model distinguishes:

| Level | Intended role | Current implementation |
| --- | --- | --- |
| L1 generic | Shared workflow with task-declared constraints | Skill/profile assets only |
| L2 external profile | Customer/project data loaded after validation | Loader absent |
| L3 official type | Maintained executable rules, fixtures and regression tests | Product labels/Skills/fixtures exist; Python rules absent |

Official product/domain labels currently retained by repository policy are `hara`, `technical_solution`, `test_report`, and `fsr`. That label does not mean a Python registry currently enforces their rules.

## Profile field design

A future external profile may need fields such as:

```yaml
profile_id: customer_demo.custom_technical_note
profile_version: 0.1.0
task_type: custom_technical_note
display_name: Custom Technical Note
description: A profile description.
default_sections:
  - Background
required_sections:
  - background
critical_claims:
  - deployment risk
requires_human_confirmation:
  - deployment risk
forbidden_final_claims:
  - deployment is production ready
confirmation_marker: NEEDS_USER_CONFIRMATION
fact_source_roles:
  - source
non_fact_source_roles:
  - sample
  - template
  - checklist
  - reference
default_final_status: ready_for_human_review
allowed_final_statuses:
  - ready_for_human_review
  - finalized_with_open_items
  - blocked_pending_confirmation
candidate_learning_policy: Generate proposals only; never auto-apply.
```

This is candidate design data, not a statement that these fields are currently parsed or enforced.

## Required future loader boundaries

If a future active phase implements profiles, it must provide:

1. an explicit schema and version policy;
2. safe path resolution and profile hash binding;
3. fail-closed behavior for invalid or missing profiles;
4. tests proving sample/reference cannot become project fact support;
5. critical-claim and final-status enforcement;
6. positive and negative fixtures;
7. no automatic profile or stable Skill overwrite;
8. current documentation and rollback behavior.

Until those conditions exist, documentation must not call a profile “validated” or “active”.

## Markdown Spec role

A Markdown Spec is an upstream human-readable description. It can help experts and maintainers discuss sections, claims, evidence rules, and review focus. It is not a machine rule and the current repository has no command that converts it into an executable profile.

## Source boundary

Any future profile mechanism must retain:

- `source` may support project facts when relevant;
- `template` constrains structure;
- `checklist` constrains review coverage;
- `reference` supports method/background only;
- `sample` supports style/shape only;
- critical claims require T0/T1 or remain open.

Profile data cannot waive these rules.

## Candidate and promotion boundary

Current Skills may describe proposed candidate artifacts, but current Python does not generate, evaluate, apply, or promote them. Any future promotion mechanism requires a separate active phase, explicit human approval, passing evaluation evidence, version/hash binding, and rollback metadata.

## TSC boundary

`TechnicalSafetyConcept` has nonofficial Skill, step-overlay, and fixture assets. It is not an external profile and not an official L3 implementation. Python rules/registry, end-to-end content execution, and dedicated engine tests are absent. Official TSC and HSC/SSC remain deferred.

## What profiles must not imply

- an independent pipeline per document type;
- automatic professional judgment or approval;
- sample/reference fact support;
- automatic candidate activation;
- stable Skill modification;
- current Python behavior that does not exist.
