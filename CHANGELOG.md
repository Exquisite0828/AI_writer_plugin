# Changelog

本项目使用接近 Keep a Changelog 的格式记录面向用户和维护者的重要变化。

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
