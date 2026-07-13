---
name: writing-core
description: 中文优先指导 AI coding tools 运行 agent-driven professional document workflow；Python 只负责 Phase 0 scaffold 与 orchestration metadata，同时保留 artifact、source、provenance、HITL 和 non-approval 边界。
---

# Writing Core Skill

Use this skill for shared writing boundaries across document types. `/ai-writing-plugin:write` is an agent-worker protocol. The current deterministic Python layer creates Phase 0 scaffold and validates orchestration metadata; it does not generate professional content. Runtime artifacts live under `runs/<run_id>/` and must not be committed.

## Shared Workflow

The workflow is evidence-aware and artifact-first:

```text
input materials -> material inventory -> document navigation index -> template outline -> section plans -> evidence map / citation plan / section tasks -> conservative draft -> review -> verification -> revision -> final report -> run summary -> candidate update
```

Each step creates only the artifacts it owns. When exact paths or schemas are needed, read `contracts/CURRENT_ARTIFACT_CONTRACTS.md` intentionally for that question; do not copy a full artifact tree into runtime prompts.

## Input Document Access

Step 4 and later must access original input text only by this path:

```text
knowledge/document_tocs/<file_id>.md or provenance_index.json -> L1 -> L2 -> L3 -> location -> original text
```

Allowed cross-document entry: `source_index.json.topic_index` pointing to `file_id + L1/L2/L3`. Forbidden: direct full-text blind search, old `SRC-xxx` chunk jumps, treating `input_inventory.path` as already-read evidence, skipping L1/L2/L3, or using TOC `brief` as evidence.

## Source Roles

- `source`: project fact source when parsed and relevant.
- `template` / `checklist`: structure and review constraints, not project fact proof.
- `reference`: methodology/background/terminology only.
- `sample` / `expected_output_shape`: structure, style, table shape, granularity, wording style only.
- `HITL`: explicit human confirmation recorded in trace.

Required boundary:

```text
fact source != sample document
sample is not fact source
sample must not be used as fact source
reference cannot prove project facts
T3/T4/T5 cannot support critical claim by themselves
```

Tiers: `T0=HITL`, `T1=project source`, `T2=template/checklist`, `T3=reference`, `T4=sample`, `T5=generated/unknown inference`.

## Critical Claims And Final Status

Critical claims require T0/T1 support or remain `NEEDS_USER_CONFIRMATION`, pending, or open. HITL pending must not become confirmed automatically. Noninteractive runs must not fake approval.

Do not write unsupported professional approval language such as `approved`, `validated`, `compliant`, `risk accepted`, `production ready`, or equivalent. `final_report.md` is a review-ready package, not professional approval.

## Document Type And Profile Boundary

Current repository guidance defines official L3 product/domain asset labels as `hara`, `technical_solution`, `test_report`, and `fsr`. The current Python package has no document-type registry or type-specific content engine. `generic_document`, external `document_profile.yaml`, and `custom_technical_note` are design/config assets and are not loaded by current Python code.

Other document-type runtime dirs may exist for historical or drift reasons. Do not load sibling document types by default and do not make them official from this skill.

## Candidate Learning

If a learning worker creates candidate artifacts, they are proposals only:

- `learning/candidate_profile_update.yaml`
- `learning/candidate_skill_patch.md`
- `learning/promotion_report.md`

candidate update proposed/inactive. They must not overwrite stable Skill files, activate profiles, or apply runtime patches. The current Python package has no candidate generation, eval, or promotion command.

## Common Failure Modes

- Treating sample/reference as project fact support.
- Reading original inputs without the L1/L2/L3 navigation path.
- Writing final reports as approval or compliance.
- Calling `custom_technical_note` official L3.
- Leaking HARA terms such as ASIL/S/E/C/hazardous event into unrelated outputs.
- Creating a new pipeline per document type.
- Introducing RAG, LangChain, vector DB, heavy dependencies, or complex agent frameworks.
