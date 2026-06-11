# HARA MVP Baseline

## 1. Purpose

This baseline freezes the completed HARA MVP behavior before Generalization Phase 1 begins. Future generalization work must use this record to detect regressions in the existing HARA technical-preview workflow.

This document is a structured summary only. It does not contain full generated draft, review, final report, trace, or learning artifact contents.

## 2. Baseline Scope

The baseline covers the existing HARA demo fixture and completed MVP command chain:

```text
examples/hara_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
```

This baseline does not introduce document type generalization, `document_types/`, `technical_solution`, `test_report`, new plugin commands, or engine refactoring.

## 3. Repository State

| Item | Value |
|---|---|
| Baseline created at | 2026-06-05T14:11:07Z |
| Current git commit | d7628da |
| Python command | `.venv/bin/python` |
| Python version | Python 3.14.5 |
| Phase document source | `docs/maintainers/ARCHITECTURE.md` and historical Generalization Phase 0 notes |

Pre-flight commands run:

```text
git status --short
git log --oneline -5
```

Pre-flight status showed existing documentation-only archive/context changes from the current work session and the untracked source document `GENERALIZATION_PHASE_0_DOCS.md`. No engine changes were present.

Recent commits:

```text
d7628da Archive HARA MVP docs for generalization
d75be3b docs: document local plugin loading
8397d5e docs: align trial setup instructions
0bd2f9a docs: add trial demo fixture
8e5b096 docs: add mentor demo entrypoint
```

## 4. Validation Commands

| Command | Result | Notes |
|---|---|---|
| `.venv/bin/python --version` | pass | `Python 3.14.5` |
| `claude plugin validate .` | pass | Plugin manifest validation passed. |
| `.venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml` | pass | Created `runs/20260605-140728-hara/`. |
| `.venv/bin/python -m pytest tests/test_generalization_phase0_hara_baseline.py -q` | red verified | Failed before this baseline existed, proving the new Phase 0 test checks for the baseline document. |
| `.venv/bin/python -m pytest -q` | pass | `203 passed in 5.50s`. |

## 5. HARA Demo Fixture Run

| Item | Value |
|---|---|
| Command | `.venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml` |
| Result | pass |
| Run directory | `runs/20260605-140728-hara/` |
| Run id | `20260605-140728-hara` |
| Manifest status | `completed_with_candidate_updates_proposed` |
| Manifest phase | `phase_8` |

Command output summary:

```text
Write run completed
Run: runs/20260605-140728-hara
Status: completed_with_candidate_updates_proposed
```

The generated run directory is ignored by git and must not be committed.

## 6. Required Artifact Checklist

| Artifact | Required | Present | Notes |
|---|---:|---:|---|
| `manifest.json` | yes | yes | |
| `task_brief.json` | yes | yes | |
| `inputs/input_inventory.json` | yes | yes | |
| `knowledge/source_index.json` | yes | yes | |
| `knowledge/knowledge_gaps.md` | yes | yes | |
| `plans/template_structure.json` | yes | yes | |
| `plans/outline_l1.md` | yes | yes | |
| `plans/research_questions.json` | yes | yes | |
| `plans/evidence_map.json` | yes | yes | |
| `plans/unresolved_questions.md` | yes | yes | |
| `plans/citation_plan.json` | yes | yes | |
| `plans/outline_final.md` | yes | yes | |
| `plans/section_tasks.json` | yes | yes | |
| `plans/writing_plan.md` | yes | yes | |
| `draft/full_draft.md` | yes | yes | |
| `review/review_report.json` | yes | yes | |
| `review/final_review.md` | yes | yes | |
| `verify/verify_report.json` | yes | yes | |
| `verify/failures.md` | yes | yes | |
| `revision_plan.json` | yes | yes | |
| `revised/full_draft.md` | yes | yes | |
| `revised/change_log.md` | yes | yes | |
| `final/final_report.md` | yes | yes | |
| `final/delivery_summary.md` | yes | yes | |
| `trace/session_trace.jsonl` | yes | yes | |
| `trace/hitl_decisions.jsonl` | yes | yes | |
| `learning/run_summary.md` | yes | yes | |
| `learning/reusable_patterns.md` | yes | yes | |
| `learning/candidate_profile_update.yaml` | yes | yes | |
| `learning/candidate_skill_patch.md` | yes | yes | |
| `learning/promotion_report.md` | yes | yes | |

## 7. Non-regression Contract

Future phases must preserve these HARA behaviors:

1. `hara_demo_fixture` can run end-to-end through `write-run`.
2. `sample` is not treated as a fact source.
3. `reference` is not treated as project fact source.
4. HARA critical professional judgments are not automatically finalized.
5. `NEEDS_USER_CONFIRMATION` or equivalent markers remain where needed.
6. `final_report.md` and `delivery_summary.md` do not claim formal compliance approval.
7. `trace/hitl_decisions.jsonl` is generated.
8. `learning/candidate_profile_update.yaml` is generated.
9. Candidate updates remain proposed/inactive by default.
10. Stable skills are not automatically overwritten.

## 8. Safety and Boundary Conditions

Observed HARA boundary behavior in `runs/20260605-140728-hara/`:

1. `inputs/sample_hara.md` is recorded with `role=sample` and `is_fact_source=false`.
2. `inputs/method_reference.md` is recorded as a non-fact input for project-specific facts.
3. `final/final_report.md` and `final/delivery_summary.md` retain `NEEDS_USER_CONFIRMATION` for HARA professional judgments.
4. Final delivery text states that qualified human review is required before treating HARA judgments as approved.
5. Unsafe approval claims such as final ASIL approval, risk acceptance, or safety goal approval were not observed.

## 9. Candidate Learning Status

Candidate learning artifacts were generated but not activated.

Observed in `learning/candidate_profile_update.yaml`:

```text
status: proposed
active: false
auto_applied: false
requires_user_approval: true
stable_skill_overwrite_allowed: false
```

Observed in `learning/promotion_report.md`:

```text
Current state: proposed
Stable skill overwritten: no
Candidate activated: no
Not promoted automatically.
```

## 10. Known Limitations

1. This baseline is for the completed HARA technical-preview workflow only.
2. It does not prove support for additional document types.
3. It does not approve HARA professional judgments or compliance conclusions.
4. It does not activate candidate profile updates or candidate skill patches.
5. It does not define a generalized `document_type` registry.

## 11. How Future Phases Should Use This Baseline

Future Generalization Phase 1-6 work should compare HARA behavior against this baseline after each architectural change.

At minimum, future phases should:

1. Run the full pytest suite.
2. Run `claude plugin validate .` when available.
3. Run `write-run` with `examples/hara_demo_fixture/task.yaml`.
4. Confirm all required artifacts above still exist or document intentional contract changes in a current phase document.
5. Confirm the non-regression contract remains true.
6. Confirm no runtime `runs/` output is committed.

Equivalent existing and new regression tests include:

| Test | Coverage |
|---|---|
| `tests/test_output_hygiene.py::test_demo_fixture_final_outputs_use_generic_hygiene` | HARA demo final output hygiene, sample non-fact boundary, confirmation markers, unsafe claim blocking. |
| `tests/test_finalize_run.py::test_baseline_final_status_is_not_fully_approved` | Final status is not fully approved and qualified human review remains required. |
| `tests/test_finalize_run.py::test_sample_and_expected_output_are_not_elevated_to_fact_sources` | Sample and expected-output documents are not elevated to fact sources. |
| `tests/test_learning_run.py::test_candidate_profile_update_is_proposed_and_inactive` | Candidate profile update remains proposed and inactive. |
| `tests/test_learning_run.py::test_candidate_skill_patch_is_not_applied` | Candidate skill patch is not applied and stable skill is not overwritten. |
| `tests/test_generalization_phase0_hara_baseline.py::test_generalization_phase0_hara_baseline_is_recorded_and_regression_safe` | Phase 0 baseline document exists; HARA demo required artifacts, source boundaries, non-approval boundary, candidate inactive state, and Phase 0 scope is recorded without permanently blocking future `document_types/` work. |
