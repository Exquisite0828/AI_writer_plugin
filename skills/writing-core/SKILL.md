---
name: writing-core
description: 中文优先指导 AI coding tools 通过 deterministic Python engine 运行 AI professional document writing plugin，同时保留 artifact、source、provenance、HITL、final-status、profile 和 candidate-update 边界。
---

# Writing Core Skill

Use this skill when working with the AI professional document writing Claude Code plugin. The plugin provides an evidence-aware, reviewable, traceable writing workflow for professional documents with declared materials, templates, checklists, source support, verification, and human confirmation boundaries.

## 中文交互默认规则

默认用中文和用户沟通，尤其是任务确认、材料分类说明、运行进度、风险提醒、最终结果和后续动作。保留命令、路径、artifact 文件名、schema 字段、`task_type`、`source`、`sample`、`reference`、`HITL`、`NEEDS_USER_CONFIRMATION` 等英文关键术语。

如果输入材料或引用片段是英文，可以保留原文；解释性文字优先中文。不要因为中文交互而弱化 Python deterministic engine、artifact contract、source index、provenance、review、verify、HITL trace 或 candidate update state control。

This is not a normal chat writing assistant. It is not an automatic compliance, safety, architecture, quality, or release approval tool. It must not generate unattended final professional approval conclusions.

## Plugin Workflow And Engine Boundary

This Skill.md is guideline material only. It must use plugin workflow and must call Python engine commands from the repository root. Do not create final documents directly from this Skill.md, and do not replace the Python deterministic engine with prompt-only writing.

The Python deterministic engine is the trusted execution skeleton for:

- schema validation
- artifact generation
- material classification
- source index and provenance index construction
- evidence trace and citation planning
- review and verify checks
- HITL trace recording
- final status handling
- candidate update state control

Skill.md must not replace artifact contract, schema validation, source index, evidence trace, review, verify, HITL trace, or candidate update state control.

## Required Entry Points

Claude Code command:

```text
/ai-writing-plugin:write "Run the writing workflow with examples/hara_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/technical_solution_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/test_report_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/fsr_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/generic_document_demo_fixture/task.yaml"
/ai-writing-plugin:write "Run the writing workflow with examples/custom_technical_note_profile_demo_fixture/task.yaml"
```

## Generic Workflow

The generic workflow is artifact-first:

```text
input materials
-> material inventory
-> source index
-> template outline
-> research questions
-> evidence map
-> citation plan
-> section tasks
-> conservative draft
-> review
-> verification
-> revision
-> final report
-> run summary
-> candidate profile update / candidate skill patch
```

Equivalent stage words include init run, ingest, source index, template outline, research questions, evidence map, citation plan, section tasks, draft, review, verify, finalize, trace, and learning.

## Artifact Contract

The artifact contract is maintained in `docs/CURRENT_ARTIFACT_CONTRACTS.md` and enforced by each step skill's subagent against its declared schema. Skill.md can explain the contract but must not invent a parallel schema.

Core artifacts include:

- `manifest.json`
- `task_brief.json`
- `inputs/input_inventory.json`
- `knowledge/source_index.json`
- `knowledge/provenance_index.json`
- `knowledge/knowledge_gaps.md`
- `plans/template_structure.json`
- `plans/outline_l1.md`
- `plans/research_questions.json`
- `plans/evidence_map.json`
- `plans/unresolved_questions.md`
- `plans/citation_plan.json`
- `plans/outline_final.md`
- `plans/section_tasks.json`
- `plans/claim_support_matrix.json`
- `plans/writing_plan.md`
- `draft/full_draft.md`
- `review/review_report.json`
- `review/final_review.md`
- `verify/verify_report.json`
- `verify/failures.md`
- `revision_plan.json`
- `revised/full_draft.md`
- `revised/change_log.md`
- `final/final_report.md`
- `final/delivery_summary.md`
- `trace/session_trace.jsonl`
- `trace/hitl_decisions.jsonl`
- `learning/run_summary.md`
- `learning/reusable_patterns.md`
- `learning/candidate_profile_update.yaml`
- `learning/candidate_skill_patch.md`
- `learning/promotion_report.md`

Runtime artifacts are written under `runs/<run_id>/` and must not be committed to git.

## Source Roles

Material roles are not interchangeable:

- `source`: normal project fact source role.
- `template`: structure constraint; not automatic project fact support.
- `checklist`: review and verification requirement; not project fact support.
- `reference`: methodology, background, terminology, or review guidance only.
- `sample`: style, shape, table organization, section granularity, and wording style only.
- `expected_output_shape`: output shape guidance only.
- `HITL`: explicit human confirmation recorded through trace.

Required boundaries:

- sample is not fact source.
- sample is not a fact source.
- sample must not be used as a fact source.
- reference cannot prove project facts.
- reference is not project-specific fact support.
- reference must not be used as project-specific fact support.
- Expected-output or sample content must not be promoted into project facts.

## N4 Source Tier And Provenance Policy

N4 source tier rules:

- `T0`: HITL / explicit human confirmation.
- `T1`: project source.
- `T2`: template / checklist.
- `T3`: reference methodology.
- `T4`: sample style only.
- `T5`: generated / unknown / unsupported inference.

Interpretation:

- T0 and T1 can support critical project claims when the recorded material actually supports the claim.
- T2 can constrain structure or review expectations, but it does not prove project facts.
- T3 can explain methodology, but it cannot prove project facts.
- T4 can guide style and output shape only, not project facts.
- T5 is unsupported inference and cannot support critical claim.
- T3/T4/T5 cannot support critical claim by themselves.

`knowledge/provenance_index.json` and `plans/claim_support_matrix.json` are the main N4 provenance artifacts. Draft, review, verify, final report, and delivery summary should preserve source tier, claim status, evidence status, human confirmation status, and profile version where applicable.

## Critical Claim, HITL, And Final Status

A critical claim is a high-risk or key professional judgment. Each document type defines its own critical claims.

Rules:

- critical claim must have source or HITL.
- Critical claim must have T0/T1 support or remain `NEEDS_USER_CONFIRMATION`, pending, or an open item.
- `requires_human_confirmation` claims may still need HITL even when a source exists.
- HITL pending must not be changed to confirmed automatically.
- Noninteractive runs must not fake approval.
- Real HITL decisions must be recorded in `trace/hitl_decisions.jsonl`.

Final boundary:

- final_report is not approval.
- final report is not approval.
- final_report is a review-ready package, not professional approval.
- Do not write unsupported `approved`, `validated`, `compliant`, `risk accepted`, `production ready`, or similar final professional approval language.

## Profiles, Generic Mode, And Markdown Spec

Official L3 document types are implemented through built-in document-type skills under `skills/document-types/`:

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

`generic_document` is L1 generic mode. It helps run the shared workflow for documents that have source, template, checklist, sample, reference, or profile guidance, but it does not promise complete domain professional judgment.

External `document_profile.yaml` is an L2 / customer profile mechanism. It must pass validation before use. `custom_technical_note` is an external profile demo, not an official L3 document type.
TSC / Technical Safety Concept remains deferred and is not an official built-in document type.

Markdown Spec is a human-readable upstream explanation layer. It is not the runtime machine rule and must not be treated as the only execution rule. A Markdown Spec may be converted into a candidate profile, but that candidate profile stays inactive until separately reviewed and activated through a controlled process.

## Candidate Learning Policy

Learning artifacts are proposals:

- `learning/candidate_profile_update.yaml`
- `learning/candidate_skill_patch.md`
- `learning/promotion_report.md`

candidate update proposed/inactive.
candidate updates remain proposed/inactive.
`candidate_profile_update.yaml` and `candidate_skill_patch.md` remain proposed / inactive by default.

They must not automatically overwrite stable Skill files, must not automatically activate profiles, and must not be applied from `runs/<run_id>/learning/candidate_skill_patch.md` without explicit human review in a separate process.

## Common Failure Modes

Avoid these failures:

- Treating sample as a fact source.
- Treating reference as proof of project facts.
- Writing final report as approval.
- Treating Markdown Spec as a runtime rule.
- Treating Skill.md as the execution layer.
- Calling `custom_technical_note` an official L3 document type.
- Leaking HARA terminology such as ASIL, S/E/C, hazardous event, safety goal, severity rating, exposure rating, or controllability rating into `technical_solution` output.
- Creating a new pipeline per document type.
- Automatically applying `candidate_skill_patch.md`.
- Automatically promoting a profile.
- Introducing RAG, LangChain, vector DB, or a complex agent framework.
