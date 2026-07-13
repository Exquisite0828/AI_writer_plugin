# Markdown Export Service Test Plan

## Test Scope

The test pass covers functional checks for Markdown export behavior, citation preservation, missing source handling, unsupported attachment handling, and delivery summary generation.

## Strategy

Testing uses deterministic manual execution records captured in `test_results.csv`. Each case records a requirement id, status, evidence id, and notes.

## Test Environment

- Environment: local CLI demo environment.
- Python runtime: project virtual environment.
- Input set: committed demo fixture materials.
- Execution mode: noninteractive run.

## Entry Criteria

- Demo task file is available.
- Source, template, checklist, reference, and sample inputs are present.
- The Python CLI can execute `init-run` for this task without network access; this verifies only Phase 0 scaffold creation.

## Exit Criteria Candidate

Exit criteria cannot be finalized automatically. Final pass/fail conclusion, release readiness, coverage sufficiency, and unresolved issue acceptance require human confirmation.

## Non-goals

- No production release approval.
- No coverage sufficiency approval.
- No defect acceptance approval.
