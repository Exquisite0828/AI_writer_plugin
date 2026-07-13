## Repository Purpose

This repository is for developing an AI professional document writing plugin for Claude Code.

The former HARA Phase 0-8 MVP and Generalization Phase 0-6/N8 deliveries are historical records; they do not imply that the removed Python content engine remains available.
The current code baseline is a technical preview with a Python Phase 0 scaffold/orchestration-metadata layer and a Claude Code agent-worker protocol.
`hara`, `technical_solution`, `test_report`, and `fsr` are the four official L3 product/domain asset labels, backed by Skills and fixtures. The current Python package has no document-type rules registry or end-to-end content engine for them.
`generic_document` remains a generic design/Skill asset, and `custom_technical_note` remains an external `document_profile.yaml` demo rather than an official L3 type; current Python does not load those profiles.

The product should guide a user through a traceable, reviewable, evidence-aware writing workflow:

input materials → material inventory → source index → template outline → evidence map → citation plan → section tasks → conservative draft → review → verification → revision → final report → run summary → candidate profile update.

Future implementation work must be developed phase by phase with an explicit active phase/spec document.
Current project guidance is governed by `docs/maintainers/ARCHITECTURE.md`, current product docs, and future active phase documents when present.

Historical phase docs and process archives are not part of the current public self-service documentation. If local archive folders such as `docs/archive/` or `local_archive/` exist, treat them as historical reference only and never as current execution instructions.

Do not implement future phases early.

## Instruction Priority

When working in this repository, follow this priority order:

1. The user's current explicit instruction.
2. This `AGENTS.md`.
3. Current active phase execution documents, when present and not under local archive folders.
4. `docs/maintainers/ARCHITECTURE.md`.
5. `contracts/CURRENT_ARTIFACT_CONTRACTS.md`.
6. `docs/maintainers/PROJECT_CONTEXT.md`.
7. `docs/TECHNICAL_DECISIONS.md`.

If there is a conflict between historical/local archive materials and current project docs, the current project docs win.

## Repository Boundaries

### `docs/`

Contains current design guidance, repository rules, active phase documents when present, and development notes.

Do not treat historical phase docs, process archives, handoff materials, or original PRD materials as direct coding tasks.

### Runtime Context Boundary

Runtime files are `commands/**/*.md` and `skills/**/*.md`. Keep them minimal and operational.

Runtime files must not:

1. Reference `docs/maintainers/*` as execution instructions.
2. Bulk-read or glob `examples/**` as default context or default input.
3. Embed the complete artifact tree from `contracts/CURRENT_ARTIFACT_CONTRACTS.md`.
4. Use a full artifact list as a checklist to pre-create every possible `runs/<run_id>/` directory or artifact.

Runtime files may point to `contracts/CURRENT_ARTIFACT_CONTRACTS.md` as the single artifact/schema authority, but they should read it intentionally only when exact paths, required files, or schema details are needed.

`examples/` contains opt-in demos and deterministic fixtures. Read a specific example only when the user selected that demo or a test explicitly references the fixture.

Maintainer context boundary policy: `docs/maintainers/RUNTIME_CONTEXT_BOUNDARY.md`.

### Optional Local Reference Folders

The MVP repository does not depend on these local reference folders:

1. `superpowers本体架构/`
2. `HARA报告生成参考资料集_EPS/`

They are ignored by git and may be absent in a fresh GitHub clone. The plugin, CLI, tests, and Claude Code command must run without them.

If either folder exists locally, treat it as read-only reference material. Do not modify it, do not copy large implementation blocks or raw materials into product code, and do not use the full raw HARA folder as automated test input. Use committed fixtures under `examples/` for deterministic tests.

## Source and Sample Rules

The project has a strict source boundary:

```
fact source != sample document
```

Sample documents and expected-output examples are not fact sources.

Never use sample, example, or expected-output content as support for:

1. HARA facts.
2. System boundaries.
3. Hazards.
4. Hazardous events.
5. Severity ratings.
6. Exposure ratings.
7. Controllability ratings.
8. ASIL or risk classification.
9. Safety goals.
10. Final professional conclusions.

Sample documents may only be used for:

1. Output structure.
2. Style.
3. Section granularity.
4. Table shape.
5. Wording style.
6. Final deliverable appearance.

If sample content is treated as factual evidence, it is a P0 defect.

## Hard Do-Not Rules

Unless the current generalization phase document explicitly asks for it, do not:

1. Implement MetaHarness.
2. Build a generic large writing platform.
3. Implement automatic stable skill replacement.
4. Implement candidate skill promotion.
5. Implement profile learning.
6. Implement draft generation.
7. Implement review or verification.
8. Implement HARA professional judgment.
9. Implement vector database, RAG platform, LangChain, or a complex agent framework.
10. Add heavy dependencies.
11. Create empty skill folders or placeholder modules to appear complete.
12. Create large plugin structures that do not run.
13. Depend on optional local reference folders such as `superpowers本体架构/` or `HARA报告生成参考资料集_EPS/`.
14. Modify local raw HARA reference materials if they happen to exist.
15. Treat samples or expected outputs as fact sources.
16. Hard-code fixture expected outputs into program logic.
17. Silently ignore parse failures.
18. Skip tests when tests are required by the Phase Spec.

## Development Mode

Preserve the current deterministic Phase 0/metadata layer before expanding capability. Do not infer that the removed full writing engine should be restored.

For any future content stage authorized by an explicit active phase/spec, the safe development order is:

1. Reconfirm the current CLI/code/test baseline.
2. Stabilize the narrowly scoped artifact contract.
3. Add deterministic positive and negative tests/fixtures.
4. Implement only the authorized Python or agent-runtime responsibility.
5. Update the Claude Code wrapper, Skills, and user documentation to the verified support level.

`/write` is currently an agent-worker protocol. New Python content commands or lifecycle behavior require an active phase/spec and testable contracts.

## Preferred Technical Defaults

Unless the current Phase Spec says otherwise:

1. Language: Python 3.11+
2. Test framework: pytest
3. CLI entry: `python -m ai_writing_plugin`
4. Config format: YAML
5. Schema validation: follow `docs/TECHNICAL_DECISIONS.md`
6. Encoding: UTF-8
7. Runtime outputs: `runs/<run_id>/`
8. Runtime outputs must not be committed to git.

## Artifact Discipline

Every generated artifact must be:

1. Stored under `runs/<run_id>/`.
2. Traceable to the command or stage that created it.
3. Valid against the current artifact contract when a contract exists.
4. Explicit about skipped, failed, or unsupported operations.

Do not silently skip missing input, unsupported formats, or failed parsing.

If an artifact schema has already been stabilized in `contracts/CURRENT_ARTIFACT_CONTRACTS.md`, do not change it unless the current generalization phase document explicitly requires the change.

## Done Criteria for Any Coding Task

At the end of a coding task, report:

1. Files created.
2. Files modified.
3. Commands run.
4. Test results.
5. Intentionally deferred work.
6. Conflicts between the current generalization docs and existing docs.
7. Any risk of target drift.

Do not claim completion if required tests were not run.

## Current Pre-Implementation Rule

If the user asks only to prepare repository documentation, do not create product code.

For documentation-preparation tasks, only create or update files explicitly requested by the user or the prompt.
