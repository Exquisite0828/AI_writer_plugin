# Roadmap

Status: future sequencing from the current scaffold/metadata baseline.

This document is not an active implementation phase. It records ordering and gates only.
No future item may be implemented without a separate explicit active phase/spec.

## 1. Current baseline

Implemented and tested now:

- Phase 0 run scaffold with `input_refs.json`, `manifest.json`, and `task_brief.json`;
- safe input path/role/hash metadata;
- context telemetry and deterministic context-budget checks;
- StepContextPackage and StepWorkerDispatch protocols;
- StepResult and ReviewResult validation;
- ProgressLedger;
- ReviewContextPackage;
- StageGateResult;
- thin-controller and runtime context-boundary tests;
- Claude Code command, orchestrator, workflow Skills, document-type guidance, and fixtures.

Not implemented in the current Python package:

- one-shot or stage-by-stage professional content engine;
- resumable content lifecycle;
- source/provenance/evidence/draft/review/final generation modules;
- Python document-type registry and type-specific rules;
- profile loading and validation;
- eval, correction harvesting, or candidate promotion.

## 2. Product invariants

Every future phase must preserve:

1. `fact source != sample document`;
2. reference material cannot prove project facts;
3. unsupported critical claims remain open;
4. professional approval stays human-controlled;
5. runtime outputs stay under `runs/<run_id>/`;
6. failures are explicit and fail closed;
7. runtime context remains path/hash based and document-type lazy;
8. candidate changes never overwrite stable assets automatically;
9. optional local reference folders remain unnecessary;
10. existing tests remain green unless an active spec intentionally changes a contract.

## 3. Future phase sequence

### R1: Host-runtime integration proof

Goal: prove the current 13-step worker protocol in a controlled Claude Code environment.

Required outputs:

- one selected fixture only;
- observable real worker and review-worker handoffs;
- validated metadata at every step;
- explicit user-gate behavior;
- failure evidence for missing worker capability;
- no claim of professional approval.

This phase must not restore the removed content engine.

### R2: First deterministic content stage

Goal: reintroduce one narrowly scoped content stage only after an active design chooses
its ownership and contract.

Required gates:

- exact artifact schema;
- source/sample/reference policy tests;
- invalid-input and parse-failure behavior;
- no fixture-output hard-coding;
- compatibility with current orchestration metadata.

Do not implement all stages in one phase.

### R3: Source, provenance, and evidence core

Goal: establish deterministic source indexing, provenance, evidence mapping, and claim
support before draft generation.

Required gates:

- original-location traceability;
- source tier enforcement;
- sample/reference non-fact tests;
- unsupported-claim propagation;
- deterministic fixtures and badcase coverage.

### R4: Controlled draft, review, verification, and delivery

Goal: add remaining content stages incrementally after R3 contracts stabilize.

Order:

```text
conservative draft -> review -> mechanical verification -> revision -> review-ready final
```

Each stage requires its own active phase and regression tests. Final delivery must retain
open confirmations and cannot become professional approval.

### R5: Document-type execution model

Goal: decide and implement the Python type registry/rules boundary for maintained product
labels.

Completion for an official type requires rules, positive/negative fixtures, regression
tests, terminology isolation, evidence boundaries, and current documentation. Existing
Skills/fixtures alone are not sufficient.

Candidate ordering for official execution is decided by future active specs; this
roadmap does not pre-authorize TSC or any other type.

### R6: Generic and external profiles

Goal: add a validated data-driven extension mechanism only after the shared content
engine and type interface are stable.

Required gates:

- explicit schema and loader;
- path and profile-version binding;
- invalid-profile fail-closed behavior;
- evidence and final-status safety rules;
- smoke and negative tests;
- no automatic stable-profile or Skill overwrite.

### R7: Evaluation harness

Goal: measure engineering and document-policy behavior without conflating it with
professional approval.

Minimum dimensions:

- artifact/schema integrity;
- source and provenance integrity;
- citation validity;
- unsupported critical-claim leakage;
- sample/reference misuse;
- final-status and terminology leakage;
- deterministic regression stability.

### R8: Correction harvesting and controlled promotion

Goal: consider candidate maintenance only after R6 and R7 are stable.

Any promotion design must require explicit approval, passing eval evidence, version/hash
binding, rollback metadata, and a strict prohibition on stable Skill mutation.

## 4. Document-type status during the roadmap

| Asset | Current status |
| --- | --- |
| `hara`, `technical_solution`, `test_report`, `fsr` | Official L3 product/domain Skill and fixture assets; no current Python execution registry |
| `generic_document` | Generic design/Skill/profile asset; no current Python content behavior |
| External profile YAML | Demonstration/config asset; no current loader |
| `TechnicalSafetyConcept` | Nonofficial skill-layer prototype; official L3 engine support deferred |
| HSC/SSC | Deferred |

No row may be upgraded to executable support merely by changing documentation.

## 5. Definition of an active phase

Before implementation begins, an active phase/spec must state:

- exact goal and non-goals;
- code and documentation files in scope;
- artifact/API changes;
- compatibility and migration decisions;
- fixtures and tests;
- failure and rollback behavior;
- acceptance commands;
- explicitly deferred follow-up work.

Historical phase names, old commands, and deleted tests are not active instructions.

## 6. Release gates

A future release claim must be supported by the current tree:

- every documented command appears in CLI help;
- every referenced test exists and passes;
- every “supported” document type meets the declared support level;
- user docs distinguish Python-enforced and agent-worker behavior;
- no sample/reference fact leakage;
- no automated professional approval;
- no tracked runtime output;
- changelog records removals as well as additions.

## 7. Historical note

The repository previously contained a larger Phase 0-8 deterministic writing engine and
related N-phase records. That code was removed before the current metadata layer was
rebuilt. Git history preserves it; it is not the starting point for current execution and
must not be copied back without a new active phase/spec.
