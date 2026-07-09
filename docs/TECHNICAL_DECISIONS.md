# Technical Decisions

Status: Generalization Phase N8 之后的当前技术决策记录。

## Implementation strategy

仓库保留 deterministic Python engine 作为可信执行骨架，并通过 Claude Code command 暴露给用户。

稳定开发顺序保持为：

1. Deterministic Python engine。
2. Stable run artifacts。
3. Tests and fixtures。
4. Claude Code command wrapper。
5. Skills and user-facing plugin polish。

当前实现遵循该顺序，通过一套共享 pipeline 加 document type rules 支持 `hara`、`technical_solution`、`test_report` 和 `fsr`。

## Language and runtime

使用 Python 3.11+。

理由：

1. engine 以文件和 artifact 为中心，适合 Python standard library workflow；
2. CLI implementation 简单；
3. pytest coverage 可本地确定性运行；
4. JSON、JSONL、YAML 和 Markdown artifact 生成直接。

## Package and CLI

Package name：

```text
ai_writing_plugin
```

CLI entry：

```bash
python -m ai_writing_plugin
```

当前 commands：

```text
init-run
ingest-run
resume-run
outline-run
evidence-run
plan-run
draft-run
review-run
finalize-run
learning-run
record-hitl
write-run
prepare-stage-review
validate-stage-review
record-stage-review-decision
check-stage-review-gate
```

`write-run` 是完整非交互 helper。它不能伪造 HITL approval。

`resume-run` 使用 `runs/<run_id>/run_state.json` 从中断的 resumable run 继续。`prepare-stage-review` / `validate-stage-review` 生成并校验辅助审查包；`record-stage-review-decision` / `check-stage-review-gate` 记录并检查用户的 `stage_review_gate_only` decision。`--require-stage-review-gates` 是 opt-in stricter workflow flag；默认 `write-run`、`resume-run` 和 stage commands 不强制 gate。

S2B reuses existing S2A gate artifacts and is opt-in enforcement only; it does not auto-call Claude Code, does not auto-fix, and does not create professional approval.

## Document type rules

document type 差异由 `ai_writing_plugin/document_types/` 下的 Python `DocumentTypeRules` 表达。

当前已注册 task types：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

rules 目前保持为 Python dataclasses。除非未来 active phase/spec 明确要求，不新增 YAML rules loader。

`generic_document` 是 L1 generic mode。validated external `document_profile.yaml` 是 L2 external profile mechanism。`custom_technical_note` 是 external profile demo，不是 official L3 built-in document type。`TechnicalSafetyConcept` 为 document-type skill 层类型（与 `FunctionalSafetyRequirement`、`ItemDefinitionDocument` 同级），已接入；其下游 HSC / SSC 仍 deferred。

## Test framework

使用 pytest。

测试必须 deterministic 且可本地运行。测试不能依赖：

1. Network access；
2. live LLM calls；
3. optional local reference folders；
4. 已提交到 git 的 generated `runs/` outputs。

## Config and artifact formats

task configuration files 使用 YAML。

artifact 格式：

1. JSON 用于 structured artifacts；
2. Markdown 用于 human-readable reports；
3. JSONL 用于 traces；
4. YAML 用于 profiles 和 task configs。

runtime output 写入：

```text
runs/<run_id>/
```

`runs/` 不能提交。

## Schema validation

artifact 和 task models 使用 Pydantic v2。

理由：

1. Python-first validation 适合 deterministic engine；
2. runtime artifacts 可以在生成附近完成 validation；
3. model definitions 在 contract 演进时仍然可读；
4. 未来如有需要，可以导出 JSON Schema。

## Dependencies

当前 runtime dependencies：

- `pydantic>=2,<3`
- `PyYAML>=6,<7`

当前 dev dependency：

- `pytest>=8,<10`

除非未来 active phase/spec 明确要求，否则避免 heavy dependencies：

1. `langchain`
2. `llama-index`
3. `chromadb`
4. `faiss`
5. `celery`
6. `fastapi`
7. `sqlalchemy`
8. `streamlit`
9. complex agent frameworks

## Source boundary decisions

`source` 是正常项目事实来源角色。

以下不是 project fact sources：

- `sample`
- `expected_output_shape`
- `template`
- `checklist`
- `reference`

`reference` 只能支持 methodology/background。它不能证明 project-specific facts、professional conclusions、test results、HARA ratings、architecture decisions 或 release readiness。

## Context boundary and cache-pressure closure

The repository uses deterministic context guards to reduce cache churn risk and keep runtime context below hard limits:

1. static telemetry and budget checks measure `commands/**/*.md` and `skills/**/*.md`;
2. `runs/<run_id>/input_refs.json` records inputs as path/hash metadata, without input body replay;
3. runtime prompt and Skill surfaces are kept short and operational;
4. compact StepContextPackage, ReviewContextPackage, StepResult, ReviewResult, StageGateResult, and ProgressLedger artifacts pass paths and hashes rather than artifact bodies;
5. `stage_reviews/<stage>/issues_index.json` is the default review issue surface, while `issues/<issue_id>.json` details are read only on demand;
6. stage gate decisions bind to `issues_index_ref` when an index exists.

The deterministic harness does not call Claude Code or any LLM API. Therefore API-level prompt-cache read ratio remains `not_measured`; the project can claim structural cache-risk reduction, not a proven provider cache-hit percentage.

Manual context guard commands:

```bash
python -m ai_writing_plugin check-context-budget --root . --task-type hara --step step-input-materials --json
python -m ai_writing_plugin check-context-budget --root . --task-type hara --step step-evidence-map --json
```

No professional approval, S2B/S3/S4 policy automation, safe auto-fix, or target-drift cleanup is implied by these guards.

## Candidate learning decision

candidate learning artifacts 可以生成，但默认保持 proposed 和 inactive。

engine 不能自动覆盖 stable Skill files，也不能自动激活 candidate updates。

## Current decision summary

| Topic | Decision |
| --- | --- |
| Language | Python 3.11+ |
| Tests | pytest |
| Task config | YAML |
| Structured artifacts | JSON |
| Schema validation | Pydantic v2 |
| Trace artifacts | JSONL |
| Human reports | Markdown |
| Runtime output | `runs/<run_id>/` |
| Document type registry | Python `DocumentTypeRules` |
| Supported official L3 task types | `hara`, `technical_solution`, `test_report`, `fsr` |
| Extended modes | `generic_document`, validated external `document_profile.yaml` |
| Live LLM dependency | No |
| Heavy framework dependency | No |
| Optional raw reference dependency | No |
| Development order | deterministic engine first |
