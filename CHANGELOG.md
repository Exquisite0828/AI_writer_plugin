# Changelog

本项目使用接近 Keep a Changelog 的格式记录面向用户和维护者的重要变化。

## [Unreleased]

### Added

- Phase 0 `init-run` scaffold with `input_refs.json`, `manifest.json`, and `task_brief.json`.
- Deterministic context telemetry and context budget guard for runtime prompt/skill surfaces.
- Path/hash-only StepContextPackage and StepWorkerDispatch metadata.
- StepResult and ReviewResult validators.
- ProgressLedger, ReviewContextPackage, and StageGateResult builders/validators.
- Public `build-stage-review-issues` and `validate-stage-review-issues` commands for strict, transactional stage issue metadata; the current CLI now exposes 19 commands.
- Document-type lazy routing and compact runtime context boundaries.
- Nonofficial `TechnicalSafetyConcept` (TSC) Skill-layer prototype with a document-type Skill, step overlays, and an opt-in demo fixture.

### Changed

- `/ai-writing-plugin:write` now describes an independent agent-worker protocol with a thin main controller.
- Python responsibility is limited to Phase 0 scaffolding and orchestration metadata; professional content belongs to independent workers.
- Stage review now has an explicit per-step ReviewResult fan-out, ledger rebinding sequence, strict issue source/index/detail flow, and all-results StageGate handoff without changing existing metadata schemas.
- Runtime worker ownership now uses controller-owned initialization, one worker per step, and one review worker per stage; legacy per-step nested-review state is no longer current runtime input.
- Step 1 now receives `manifest.json` through its ContextPackage, while review-triggered A2 work is redispatched to the original step worker with stale ledger bindings reset before a full-stage re-review.
- `prepare-step-worker-dispatch` now validates and propagates real upstream StepResult artifacts in fixed workflow order; redispatch of an earlier step atomically invalidates later handoff metadata for ordered rerun, while document-type root Skills and per-step overlays remain independently optional and lazily loaded.
- `build-review-context-package --overwrite` is now the transactional review-cycle boundary: it removes consumed stage-review refs, synchronizes ContextPackage/Dispatch/Ledger hashes, preserves current StepResults, and clears stale ReviewResults before full-stage re-review.
- `complete-step-worker-dispatch --status` is now an assertion against the authoritative StepResult or ReviewResult status rather than an override; completion also enforces canonical result paths and atomic Ledger/Dispatch updates.
- Current documentation distinguishes code-enforced capability, runtime instruction assets, and future/historical design.

### Removed

- The former Phase 0-8 Python professional writing engine and its one-shot/stage content commands.
- The former Python resume/run-state lifecycle and stage-review command lifecycle.
- The former Python document-type registry/rules, profile loader/generator, eval, correction-harvesting, and promotion implementation.
- Completed context-optimization plan records and metric snapshots from the current public documentation tree; Git history remains the archive.

### Notes

- StageGateResult is orchestration metadata. It does not create professional approval, compliance approval, or safety approval.
- Python does not invoke Claude Code workers or generate professional artifacts.
- TSC is not an official L3 built-in and has no Python rules/registry, end-to-end content CLI, or dedicated engine test. Official L3 TSC and HSC/SSC remain deferred.
- Deterministic tests report API prompt-cache ratio as `not_measured`; they do not prove a real Claude prompt-cache hit rate.

## [0.1.0] - 2026-06-08

### Added

- Claude Code plugin manifest and `/ai-writing-plugin:write` command.
- Deterministic Python writing workflow for traceable professional document packages.
- Official built-in profiles:
  - `hara`
  - `technical_solution`
  - `test_report`
  - `fsr`
- `generic_document` generic mode.
- External `document_profile.yaml` demo through `custom_technical_note`.
- Artifact tree under `runs/<run_id>/`.
- Evidence boundary checks for `source`, `sample`, `reference`, HITL, review, verification, final report, and proposed candidate updates.

### Notes

- `generic_document` is not an official built-in profile.
- `custom_technical_note` is not an official built-in profile.
- At the 0.1.0 release, TSC / Technical Safety Concept was deferred and was not implemented as an official type, profile, Skill, fixture, or test target. Nonofficial prototype assets were added after this release; see Unreleased.
- `final_report.md`, eval passed, promotion report, and candidate updates are not professional approval.
