# Changelog

本项目使用接近 Keep a Changelog 的格式记录面向用户和维护者的重要变化。

## [Unreleased]

### Added

- Resumable write runs with `runs/<run_id>/run_state.json` and `resume-run`.
- Stage Review Gate package generation and validation through `prepare-stage-review` and `validate-stage-review`.
- Review unit coverage validation with `review_units.json`, `reviewed_unit_ids`, `unchecked_unit_ids`, and `issues[].unit_id`.
- User stage review decisions through `record-stage-review-decision` and `check-stage-review-gate`.
- Opt-in `--require-stage-review-gates` enforcement for stricter stage-by-stage workflows.
- Deterministic context telemetry and context budget guard for runtime prompt/skill surfaces.
- Stable `input_refs.json` path/hash manifest for input context boundaries.
- Compressed runtime prompt/skill surface to reduce active context size.
- Stage review issue index/detail split with hash-bound stage gate decisions.

### Notes

- Stage Review Gate is an auxiliary review mechanism. It does not create professional approval, compliance approval, or safety approval.
- The workflow does not automatically invoke Claude Code, does not automatically modify professional artifacts, and does not implement auto-fix or S4 auto apply.
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
- TSC / Technical Safety Concept is deferred and not implemented as an official type, profile, Skill, fixture, or test target.
- `final_report.md`, eval passed, promotion report, and candidate updates are not professional approval.
