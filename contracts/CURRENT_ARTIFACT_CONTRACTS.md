# CURRENT_ARTIFACT_CONTRACTS.md

## 0. Generalized Document Type Contract

本文件定义当前 deterministic engine 的 artifact contract。它是维护者判断 `runs/<run_id>/` 输出是否稳定、可追踪、可测试的依据。

当前仓库通过一个 shared artifact contract 支持四类 official L3 document types：

- `hara`
- `technical_solution`
- `test_report`
- `fsr`

这是 shared artifact contract。artifact contract does not fork by task_type。task_type affects content、document labels、critical claims、required confirmations、final status policy 和 readable terminology，但不会改变 core run directory structure。

完整 `write-run` 的 core tree：

```text
runs/<run_id>/
  manifest.json
  run_state.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/provenance_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
  plans/research_questions.json
  plans/evidence_map.json
  plans/unresolved_questions.md
  plans/citation_plan.json
  plans/outline_final.md
  plans/section_tasks.json
  plans/writing_plan.md
  draft/full_draft.md
  review/review_report.json
  review/final_review.md
  verify/verify_report.json
  verify/failures.md
  revision_plan.json
  revised/full_draft.md
  revised/change_log.md
  final/final_report.md
  final/delivery_summary.md
  trace/session_trace.jsonl
  trace/hitl_decisions.jsonl
  learning/run_summary.md
  learning/reusable_patterns.md
  learning/candidate_profile_update.yaml
  learning/candidate_skill_patch.md
  learning/promotion_report.md
```

`run_state.json` 是断点续写使用的 runtime control artifact。它不是专业内容 artifact，不表示专业批准，不是 eval 结果，不是 promotion approval，也不会写入 `manifest.artifacts`。维护 artifact contract 时应把它作为 orchestration metadata 单独处理，而不是放宽专业内容 artifact 的阶段边界。

`stage_reviews/` 是可选 runtime assistance artifact directory，用于 Stage Review Gate S1/S1R/S2A。它不是 professional artifact，不是 fact source，不表示 professional approval，不改变 `run_state.json` lifecycle，也不会写入 `manifest.artifacts`。S1/S1R 只生成 Claude Code 可读取的 review package，并校验人工/命令层写出的 `issues.json`；S1R 的 `coverage_complete` 只表示 required review units 已被声明覆盖，不表示专业批准。S2A 只记录用户对 stage review gate 的操作决定并检查 gate 是否可继续，`accepted` / `skipped` does not indicate professional approval。S1/S1R/S2A 不调用 Claude Code、不修改原 stage artifacts、不应用 patch、不阻塞下一 stage。

S2B adds opt-in stage review gate enforcement through `--require-stage-review-gates`. It introduces no new artifact schema. It only reads existing S2A artifacts:

```text
stage_reviews/<stage>/validation_report.json
stage_reviews/<stage>/issues.json
stage_reviews/<stage>/decision.json
```

S2B does not write `manifest.artifacts`, does not alter the `run_state.json` schema, does not call Claude Code, does not generate `issues.json`, does not apply fixes, and does not indicate professional approval. `run_state.json` `schema_version` remains `1`.

共享 role boundaries：

1. `source` 是正常 project fact source role。
2. `template` 提供结构，不是 project fact support。
3. `checklist` 提供 review criteria，不是 project fact support。
4. sample is not fact source.
5. reference is not project-specific fact support.
6. critical claims require evidence or HITL.
7. final report is not professional approval.
8. candidate updates remain proposed/inactive.

Document-specific examples：

1. HARA critical claims include hazard identification, hazardous event, S/E/C rating, ASIL, safety goal, and final acceptability.
2. technical_solution critical claims include architecture decision, performance target, security boundary, cost estimate, and rollout risk acceptance.
3. test_report critical claims include test result, pass/fail result, defect status, coverage sufficiency, final test conclusion, and release readiness.
4. fsr critical claims include functional safety requirement wording, safety goal linkage, ASIL inheritance, verification method adequacy, requirement completeness, compliance-related conclusions, and final FSR conclusions.

## 1. Engine Artifact Lifecycle Status

本文件中的 phases 是 engine artifact lifecycle phases。它们不同于历史 Generalization Phase 0-6；后者已经完成，不属于当前 public self-service documentation。

当前已实现 engine artifact phases：

1. Phase 0: Project Skeleton and Run Contract.
2. Phase 1: Input Inventory and Source Index.
3. Phase 2: Template Structure and Outline L1.
4. Phase 3: Research Questions and Evidence Mapping.
5. Phase 4: Citation Plan and Writing Tasks.
6. Phase 5: Conservative Draft Generation.
7. Phase 6: Review and Verification.
8. Phase 7: Revision and Final Delivery.
9. Phase 8: Claude Code Entry and Candidate Learning.

当前 post-Phase-8 deterministic support utilities：

1. Phase N6: deterministic eval harness for committed regression cases.
2. Phase N7: deterministic correction harvesting and explicit external profile promotion gate.
3. Phase N8: built-in FSR L3 document type, demo fixture, skill guideline, and eval cases.

当前未实现能力：

1. Stable skill promotion.
2. Automatic active profile management.
3. Profile promotion without explicit approval, passing eval, profile validation, base hash match, and rollback metadata.
4. Real HITL approval workflow beyond explicit approval files and recorded decisions.
5. TSC / Technical Safety Concept remains unimplemented as an official document type.

## 2. CLI Commands

当前可用 commands：

```bash
PYTHON=".venv/bin/python"
$PYTHON -m ai_writing_plugin init-run --task examples/hara_minimal_fixture/task.yaml
$PYTHON -m ai_writing_plugin ingest-run --task examples/hara_minimal_fixture/task.yaml
$PYTHON -m ai_writing_plugin outline-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin evidence-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin plan-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin draft-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin review-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin finalize-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin learning-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin resume-run --run runs/<run_id>
$PYTHON -m ai_writing_plugin record-hitl --run runs/<run_id> --stage outline_l1_confirmation --decision approved_with_issues --comment "Keep unsupported sections marked." --affected-sections SEC-003,SEC-005 --next-action continue_with_confirmation_marker
$PYTHON -m ai_writing_plugin prepare-stage-review --run runs/<run_id> --stage draft
$PYTHON -m ai_writing_plugin validate-stage-review --run runs/<run_id> --stage draft
$PYTHON -m ai_writing_plugin record-stage-review-decision --run runs/<run_id> --stage draft --decision accepted --notes "Reviewed."
$PYTHON -m ai_writing_plugin check-stage-review-gate --run runs/<run_id> --stage draft
$PYTHON -m ai_writing_plugin write-run --task examples/hara_minimal_fixture/task.yaml
$PYTHON -m ai_writing_plugin write-run --task examples/hara_minimal_fixture/task.yaml --require-stage-review-gates
$PYTHON -m ai_writing_plugin resume-run --run runs/<run_id> --require-stage-review-gates
$PYTHON -m ai_writing_plugin correction-harvest --run-dir runs/<run_id> --corrections path/to/corrections.yaml --profile path/to/document_profile.yaml
$PYTHON -m ai_writing_plugin profile-promote --run-dir runs/<run_id> --candidate-patch runs/<run_id>/learning/candidate_profile_patch.yaml --eval-report runs/eval-n6/<eval_run>/eval_report.json --approval path/to/approval.yaml --target-profile path/to/document_profile.yaml --output-dir runs/<run_id>/learning --apply
```

`init-run` 只生成 Phase 0 artifacts。

`ingest-run` 生成 Phase 0 和 Phase 1 artifacts。

`outline-run` 更新已有 Phase 1 run，并生成 Phase 2 artifacts。

`evidence-run` 更新已有 Phase 2 run，并生成 Phase 3 evidence-planning artifacts。

`plan-run` 更新已有 Phase 3 run，并生成 Phase 4 citation and writing plan artifacts。

`draft-run` 更新已有 Phase 4 run，并生成 Phase 5 conservative draft artifacts。

`review-run` 更新已有 Phase 5 run，并生成 Phase 6 review and verification artifacts。

`finalize-run` 更新已有 Phase 6 run，并生成 Phase 7 revision and final delivery artifacts。

`learning-run` 更新已有 Phase 7 run，并生成 Phase 8 trace and learning artifacts。

`resume-run` 从已有 `run_state.json` 继续一个 resumable run。`completed` 只表示 deterministic engine lifecycle 完成，不表示 professional approval。`resume-run` 会拒绝 task hash mismatch、external profile hash mismatch、live lock 和 dirty completed stage。

`record-hitl` 向 `trace/hitl_decisions.jsonl` 追加 human-in-the-loop decision record。

`prepare-stage-review` 为已完成 stage 生成 advisory Claude Code review package：

```text
runs/<run_id>/stage_reviews/<stage>/review_context.json
runs/<run_id>/stage_reviews/<stage>/review_prompt.md
runs/<run_id>/stage_reviews/<stage>/issues_schema.json
runs/<run_id>/stage_reviews/<stage>/review_units.json
```

`validate-stage-review` 校验 `stage_reviews/<stage>/issues.json` 的 schema 和安全边界，并生成：

```text
runs/<run_id>/stage_reviews/<stage>/validation_report.json
```

`review_units.json` 包含 deterministic review units。`issues.json` 必须声明 `reviewed_unit_ids`、`unchecked_unit_ids`，并且每个 issue 必须包含已知 `unit_id`。`validation_report.json` 包含 `coverage_summary.coverage_complete` 和 `unit_validation`，用于说明 required units 是否全部被覆盖。

`record-stage-review-decision` 在 validation report 为 `valid` 且 `coverage_summary.coverage_complete=true` 后写入：

```text
runs/<run_id>/stage_reviews/<stage>/decision.json
```

`decision.json` 是 runtime assistance artifact，不写入 `manifest.artifacts`，不是 evidence source，也不是 critical claim confirmation。它的固定边界字段包括：

```text
kind = stage_review_decision
schema_version = 1
decision_scope = stage_review_gate_only
professional_approval = false
decision = accepted | needs_revision | blocked | skipped
allow_next_stage = true only for accepted/skipped
validation_report_sha256
issues_sha256
```

`skipped` 必须记录非空 `notes`。`accepted` / `skipped` 只表示用户允许 stage review gate 继续，不表示 professional approval、compliance approval、safety approval 或文档最终正确。

`check-stage-review-gate` 只读取 `validation_report.json`、`issues.json` 和 `decision.json`，并要求 validation 仍为 valid、coverage 仍 complete、decision 为 `accepted` 或 `skipped`、`professional_approval=false`，且 validation report / issues hashes 与记录 decision 时一致。通过时只表示 S2A gate check passed；it does not indicate professional approval。

这些命令不修改 professional artifacts，不写 `manifest.artifacts`，不修改 `run_state.json` stage status，不应用 auto-fix，也不表示 professional approval。

`write-run` 是 noninteractive helper，会创建新 run 并执行完整 Phase 0-8 chain。

`--require-stage-review-gates` 是 S2B opt-in enforcement flag。默认不加该 flag 时，`write-run`、`resume-run` 和 single-stage commands 行为保持 non-gated。加该 flag 时：

1. `write-run` 只创建 run 并完成 `ingest`，然后停止，等待 `ingest` stage review gate。
2. `resume-run` 每次最多执行一个 pending stage；执行前必须通过上一阶段 `check-stage-review-gate`。
3. `outline-run`、`evidence-run`、`plan-run`、`draft-run`、`review-run`、`finalize-run`、`learning-run` 会在执行前检查上一阶段 gate。
4. gate missing、invalid、non-passing decision 或 hash mismatch 都 fail closed，且不把目标 stage 标记为 failed。
5. S2B 只 enforcement，不自动调用 Claude Code、不自动生成 `issues.json`、不自动修改 professional artifacts、不应用 safe auto-fix。

`correction-harvest` 读取显式 correction YAML/JSON/JSONL input 和 external document profile，然后在指定 run directory 下写入 N7 correction 和 candidate profile patch artifacts。

`profile-promote` 对 N7 candidate profile patch 执行 promotion gate。无论结果是 blocked、dry-run 还是 promoted，都会写 promotion report。它只会修改明确传入的 external YAML profile target，并且只有在传入 `--apply` 且 approval/eval/hash/schema/rollback gates 全部通过时才修改。

Interactive plugin flow 可以在 `review-run` 前调用 `record-hitl`。这种情况下，`trace/hitl_decisions.jsonl` 是 Phase 6 review 前唯一允许的 trace artifact。`trace/session_trace.jsonl` 和 `learning/` 仍然是 Phase 8 artifacts，在 Phase 8 前禁止生成。Checkpoint / resume 机制本身不得提前生成 `trace/session_trace.jsonl`；但 invalid external profile fail-safe path 保持下方记录 `document_profile_validation` event 的既有例外。

External profile validation failure path：

1. 当 task 使用 invalid external `document_profile.yaml` 时，engine 必须 fail safely。
2. `manifest.json` 使用 `status = blocked_invalid_document_profile`。
3. `task_brief.json` 和 `manifest.json` 中的 `profile.validation_status` 使用 `failed`。
4. `verify/verify_report.json` 必须包含 `document_profile_validation` check。
5. `verify/failures.md` 必须说明 `profile validation failure`，并提示修正 `document_profile.yaml` 后重跑。
6. `trace/session_trace.jsonl` 必须记录 `document_profile_validation` event。
7. invalid profile failure 不能生成 successful final package，也不能自动创建 candidate update。

## 2.1 Resumable Run State

`ingest-run` 和 `write-run` 创建 resumable run 时会写：

```text
runs/<run_id>/run_state.json
```

`init-run` 保持非 resumable，只生成 Phase 0 artifacts。

`run_state.json` 记录：

1. `schema_version`
2. `run_id`
3. `task_file`
4. `task_sha256`
5. `profile_path`
6. `profile_sha256`
7. run-level `status`
8. `stage_order`
9. per-stage `status`, `phase`, required outputs, output hashes, timestamps, and failure/dirty metadata

Stage registry：

1. `ingest -> phase_1`
2. `outline -> phase_2`
3. `evidence -> phase_3`
4. `planning -> phase_4`
5. `draft -> phase_5`
6. `review -> phase_6`
7. `finalize -> phase_7`
8. `learning -> phase_8`

Stage statuses：

```text
pending
running
done
failed
interrupted
dirty
skipped
```

Run-level statuses：

```text
running
completed
failed
interrupted
```

`resume-run` validates all completed stage outputs before skipping them. Missing, empty, invalid JSON, or invalid JSONL output marks the completed stage as `dirty` and fails safely. V1 does not automatically rewind upstream artifacts or delete downstream outputs; start a new `write-run` or restore the missing/corrupt artifact.

The lock file is:

```text
runs/<run_id>/.run_state.lock
```

It records `pid`, `created_at`, and `command`. A live PID blocks resume. A dead PID is treated as stale lock recovery: the stale lock is replaced, any previous `running` stage is marked `interrupted`, and resume continues from that stage. Malformed lock content fails for manual inspection.

## 3. Phase 0 Artifacts

`init-run` 创建：

```text
runs/<run_id>/
  manifest.json
  task_brief.json
```

### 3.1 manifest.json

字段：

1. `run_id`
2. `task_file`
3. `created_at`
4. `status`
5. `phase`
6. `artifacts`

Phase 0 固定值：

1. `status = initialized`
2. `phase = phase_0`

`artifacts` 包含：

1. `manifest.json`
2. `task_brief.json`

每个 artifact item 包含：

1. `path`
2. `kind`
3. `created_at`

### 3.2 task_brief.json

字段：

1. `run_id`
2. `task_type`
3. `task_title`
4. `target_audience`
5. `output_format`
6. `strict_template`
7. `allow_inference`
8. `requires_human_confirmation`

`task_brief.json` 不包含 `inputs`。Inputs 属于 task config，不属于 Phase 0 task brief artifact。

## 4. Phase 1 Artifacts

`ingest-run` 创建：

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/provenance_index.json
  knowledge/knowledge_gaps.md
```

### 4.1 manifest.json for ingest-run

固定值：

1. `status = ingested`
2. `phase = phase_1`

`artifacts` 包含：

1. `manifest.json`
2. `task_brief.json`
3. `inputs/input_inventory.json`
4. `knowledge/source_index.json`
5. `knowledge/provenance_index.json`
6. `knowledge/knowledge_gaps.md`

### 4.2 inputs/input_inventory.json

Top-level fields：

1. `run_id`
2. `generated_at`
3. `files`
4. `summary`

File item fields：

1. `file_id`
2. `path`
3. `role`
4. `format`
5. `parse_status`
6. `is_fact_source`
7. `title`
8. `notes`
9. `error_message`

允许的 `role` values：

1. `source`
2. `template`
3. `checklist`
4. `reference`
5. `sample`
6. `expected_output_shape`

允许的 `parse_status` values：

1. `parsed`
2. `missing`
3. `unsupported`
4. `failed`

Fact-source rules：

1. `source` -> `is_fact_source=true`.
2. `reference` -> `is_fact_source=false`.
3. `template` -> `is_fact_source=false`.
4. `checklist` -> `is_fact_source=false`.
5. `sample` -> `is_fact_source=false`.
6. `expected_output_shape` -> `is_fact_source=false`.

Summary fields：

1. `total_files`
2. `parsed_files`
3. `missing_files`
4. `unsupported_files`
5. `failed_files`
6. `fact_source_files`
7. `parsed_fact_source_files`
8. `non_fact_source_files`
9. `parsed_non_fact_source_files`

Summary semantics：

1. `fact_source_files` is the number of files declared as fact sources.
2. `parsed_fact_source_files` is the number of files that were successfully parsed and can produce fact evidence chunks.
3. `non_fact_source_files` is the number of files declared as non-fact-source materials.
4. `parsed_non_fact_source_files` is the number of non-fact-source files that were successfully parsed.
5. Future evidence mapping 必须使用 `source_index.json` 作为 evidence availability source of truth，不能只看 `fact_source_files`。

### 4.3 knowledge/source_index.json

Top-level fields：

1. `run_id`
2. `generated_at`
3. `sources`
4. `summary`

Source item fields：

1. `source_id`
2. `file_id`
3. `path`
4. `title`
5. `section`
6. `anchor`
7. `text`
8. `keywords`
9. `source_role`
10. `is_fact_source`
11. `source_tier`
12. `can_support_project_fact`
13. `can_support_methodology`
14. `can_support_style`
15. `can_support_critical_claim`
16. `source_date`
17. `owner`
18. `char_start`
19. `char_end`

允许的 `source_role` values：

1. `source`
2. `reference`

`source_index.json` 只包含：

1. Parsed `source` files.
2. Parsed `reference` files.

`source_index.json` 不包含：

1. `template`
2. `checklist`
3. `sample`
4. `expected_output_shape`
5. Missing files.
6. Unsupported files.
7. Failed files.

Required source boundary：

1. `sample` must not enter `source_index.json`.
2. `expected_output_shape` must not enter `source_index.json`.
3. `reference` may enter `source_index.json`, but must use `is_fact_source=false`.
4. `source` may enter `source_index.json`, and must use `is_fact_source=true`.
5. `source` entries use `source_tier=T1_PROJECT_SOURCE`.
6. `reference` entries use `source_tier=T3_REFERENCE_METHODOLOGY`.

### 4.4 knowledge/provenance_index.json

Top-level fields:

1. `schema_version`
2. `run_id`
3. `generated_at`
4. `task_type`
5. `document_type_display_name`
6. `profile_id`
7. `profile_version`
8. `profile_source`
9. `source_tier_policy`
10. `sources`
11. `hitl_sources`

`schema_version` is `n4.provenance_index.v1`.

Source item fields include:

1. `source_id`
2. `file_id`
3. `path`
4. `title`
5. `role`
6. `source_tier`
7. `can_support_project_fact`
8. `can_support_methodology`
9. `can_support_style`
10. `can_support_critical_claim`
11. `source_date`
12. `owner`
13. `notes`
14. `parse_status`
15. `is_fact_source`
16. `source_indexed`
17. `section`
18. `anchor`

Source tier mapping:

1. `source` -> `T1_PROJECT_SOURCE`
2. `template` and `checklist` -> `T2_TEMPLATE_CHECKLIST`
3. `reference` -> `T3_REFERENCE_METHODOLOGY`
4. `sample` and `expected_output_shape` -> `T4_SAMPLE_STYLE_ONLY`
5. Unknown/generated/inferred support -> `T5_AI_INFERENCE`

Tier policy is restrictive: `T3_REFERENCE_METHODOLOGY`, `T4_SAMPLE_STYLE_ONLY`, and `T5_AI_INFERENCE` cannot prove project facts or final critical claims.

### 4.5 knowledge/knowledge_gaps.md

Required sections:

1. `Missing files`
2. `Unsupported files`
3. `Failed files`
4. `Non-fact-source materials excluded from factual indexing`
5. `Notes for next phases`

Required notes:

1. Missing source files are recorded.
2. Unsupported input files are recorded.
3. Sample and expected-output-shape materials are not factual evidence.
4. Template parsing is deferred to Phase 2.
5. Evidence mapping is deferred to Phase 3.

## 5. Phase 2 Artifacts

`outline-run` updates an existing Phase 1 run:

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/provenance_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
```

The command reads:

1. `manifest.json`
2. `task_brief.json`
3. `inputs/input_inventory.json`

It does not read `source_index.json` to derive the outline. Template structure comes from the `role=template` input declared in `input_inventory.json`.

### 5.1 manifest.json for outline-run

Fixed values after successful `outline-run`:

1. `status = outlined`
2. `phase = phase_2`

`artifacts` contains the Phase 0 and Phase 1 artifacts plus:

1. `plans/template_structure.json`
2. `plans/outline_l1.md`

Repeated `outline-run` execution may overwrite Phase 2 artifact contents, but each artifact path appears only once in `manifest.json`.

### 5.2 plans/template_structure.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `status`
4. `template_source`
5. `fallback_used`
6. `fallback_reason`
7. `document_title`
8. `nodes`
9. `outline_sections`
10. `warnings`
11. `summary`

Allowed `status` values:

1. `parsed`
2. `fallback`

`template_source` fields:

1. `file_id`
2. `path`
3. `title`
4. `format`
5. `parse_status`

Template selection rules:

1. Select only records from `input_inventory.json`.
2. Eligible records must have `role=template`, `parse_status=parsed`, and `format=md`.
3. If multiple templates are eligible, the first one is used and others are recorded in `warnings`.
4. `sample` and `expected_output_shape` are never template sources.
5. If no usable Markdown template exists, deterministic HARA fallback sections are used.

`nodes` item fields:

1. `node_id`
2. `title`
3. `level`
4. `order`
5. `parent_id`
6. `children`
7. `required`
8. `optional`
9. `intent`
10. `source_line`
11. `anchor`

`outline_sections` item fields:

1. `section_id`
2. `template_node_id`
3. `title`
4. `order`
5. `required`
6. `intent`
7. `anchor`
8. `needs_human_confirmation`

`summary` fields:

1. `total_nodes`
2. `l1_sections`
3. `required_sections`
4. `optional_sections`
5. `fallback_used`
6. `warnings_count`

### 5.3 plans/outline_l1.md

Required contents:

1. `# Outline L1`
2. Run id
3. Status
4. Template source
5. Fallback note when fallback is used
6. L1 section list
7. Warnings
8. Phase boundary note

Each section includes:

1. Section id
2. Title
3. Required status
4. Intent
5. Template anchor
6. Human confirmation note

Phase boundary note records:

1. Phase 2 only creates template structure and L1 outline.
2. Evidence mapping is deferred to Phase 3.
3. Citation planning and section tasks are deferred to later phases.
4. Draft generation is not performed in Phase 2.
5. Sample documents are not used as factual sources.

### 5.4 Phase 2 Forbidden Artifacts

`outline-run` does not generate:

1. `plans/outline_final.md`
2. `plans/research_questions.json`
3. `plans/evidence_map.json`
4. `plans/citation_plan.json`
5. `plans/section_tasks.json`
6. `plans/writing_plan.md`
7. Draft artifacts
8. Review artifacts
9. Verify artifacts
10. Final report artifacts
11. Trace artifacts
12. Learning artifacts

## 6. Phase 3 Artifacts

`evidence-run` updates an existing Phase 2 run:

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/provenance_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
  plans/research_questions.json
  plans/evidence_map.json
  plans/unresolved_questions.md
```

The command reads:

1. `manifest.json`
2. `task_brief.json`
3. `inputs/input_inventory.json`
4. `knowledge/source_index.json`
5. `knowledge/provenance_index.json`
6. `knowledge/knowledge_gaps.md`
7. `plans/template_structure.json`
8. `plans/outline_l1.md`

Evidence candidates must be selected only from `knowledge/source_index.json.sources`.

### 6.1 manifest.json for evidence-run

Fixed values after successful `evidence-run`:

1. `status = evidence_mapped`
2. `phase = phase_3`

`artifacts` contains the Phase 0, Phase 1, and Phase 2 artifacts plus:

1. `plans/research_questions.json`
2. `plans/evidence_map.json`
3. `plans/unresolved_questions.md`

Repeated `evidence-run` execution may overwrite Phase 3 artifact contents, but each artifact path appears only once in `manifest.json`.

### 6.2 plans/research_questions.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `questions`
4. `summary`
5. `warnings`

Question item fields:

1. `question_id`
2. `section_id`
3. `section_title`
4. `question`
5. `question_type`
6. `requires_human_confirmation`
7. `priority`
8. `expected_evidence_role`
9. `status`

Allowed `question_type` values:

1. `scope`
2. `input_summary`
3. `hazard`
4. `hazardous_event`
5. `rating`
6. `safety_goal`
7. `open_issue`
8. `general`

Allowed `status` values:

1. `supported`
2. `weak`
3. `unsupported`

Summary fields:

1. `total_questions`
2. `supported_questions`
3. `weak_questions`
4. `unsupported_questions`
5. `human_confirmation_required`
6. `sections_covered`

Every `outline_sections[].section_id` from `template_structure.json` must appear in at least one research question.

### 6.3 plans/evidence_map.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `questions`
4. `summary`
5. `warnings`

Question item fields:

1. `question_id`
2. `section_id`
3. `section_title`
4. `question`
5. `evidence_candidates`
6. `status`
7. `requires_human_confirmation`
8. `unresolved_reason`

Evidence candidate fields:

1. `evidence_id`
2. `source_id`
3. `file_id`
4. `source_role`
5. `is_fact_source`
6. `source_tier`
7. `evidence_status`
8. `can_support_project_fact`
9. `can_support_critical_claim`
10. `human_confirmation_status`
11. `provenance_support_type`
12. `support_type`
13. `confidence`
14. `snippet`
15. `matched_terms`

Allowed `support_type` values:

1. `direct`
2. `methodology`
3. `context`
4. `weak_keyword`

Evidence candidate rules:

1. `source_id` must exist in `knowledge/source_index.json.sources`.
2. `file_id`, `source_role`, and `is_fact_source` must match the referenced source.
3. `snippet` must be copied from referenced `source.text`.
4. `source_role=reference` must not use `support_type=direct`.
5. `sample`, `expected_output_shape`, `template`, and `checklist` must not appear as evidence.
6. `source_tier` must be propagated from the referenced `source_index.json` entry.
7. `reference` evidence is methodology/context only and must not become project fact support.

Summary fields:

1. `total_questions`
2. `questions_with_candidates`
3. `supported_questions`
4. `weak_questions`
5. `unsupported_questions`
6. `total_evidence_candidates`
7. `fact_source_candidates`
8. `reference_candidates`
9. `human_confirmation_required`

### 6.4 plans/unresolved_questions.md

Required sections:

1. `摘要`
2. `Unsupported 问题`
3. `Weak evidence 问题`
4. `需要人工确认`
5. `从 knowledge gaps 带入的 missing / unsupported 材料`
6. `阶段边界说明`

All `unsupported`, `weak`, and `requires_human_confirmation=true` questions must be listed.

阶段边界说明 states that citation planning, section tasks, drafting, review, and verification are deferred to later phases.

### 6.5 Phase 3 Forbidden Artifacts

`evidence-run` does not generate:

1. `plans/citation_plan.json`
2. `plans/claim_support_matrix.json`
3. `plans/outline_final.md`
4. `plans/section_tasks.json`
5. `plans/writing_plan.md`
6. Draft artifacts
7. Review artifacts
8. Verify artifacts
9. Final report artifacts
10. Trace artifacts
11. Learning artifacts
12. Root-level `commands/`, `skills/`, `schemas/`, `scripts/`, `agents/`, or `profiles/`

## 7. Phase 4 Artifacts

`plan-run` updates an existing Phase 3 run:

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/provenance_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
  plans/research_questions.json
  plans/evidence_map.json
  plans/unresolved_questions.md
  plans/citation_plan.json
  plans/claim_support_matrix.json
  plans/outline_final.md
  plans/section_tasks.json
  plans/writing_plan.md
```

The command reads:

1. `manifest.json`
2. `task_brief.json`
3. `inputs/input_inventory.json`
4. `knowledge/source_index.json`
5. `knowledge/provenance_index.json`
6. `knowledge/knowledge_gaps.md`
7. `plans/template_structure.json`
8. `plans/outline_l1.md`
9. `plans/research_questions.json`
10. `plans/evidence_map.json`
11. `plans/unresolved_questions.md`

Allowed evidence must come from `plans/evidence_map.json`, and every allowed evidence id must trace to `knowledge/source_index.json`.

### 7.1 manifest.json for plan-run

Fixed values after successful `plan-run`:

1. `status = writing_planned`
2. `phase = phase_4`

`artifacts` contains Phase 0 through Phase 3 artifact paths plus:

1. `plans/citation_plan.json`
2. `plans/claim_support_matrix.json`
3. `plans/outline_final.md`
4. `plans/section_tasks.json`
5. `plans/writing_plan.md`

Repeated `plan-run` execution may overwrite Phase 4 artifact contents, but each artifact path appears only once in `manifest.json`.

### 7.2 plans/citation_plan.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `sections`
4. `summary`
5. `warnings`

Section item fields:

1. `section_id`
2. `section_title`
3. `order`
4. `question_ids`
5. `allowed_evidence`
6. `evidence_details`
7. `citation_slots`
8. `unsupported_claims`
9. `weak_evidence_notes`
10. `requires_human_confirmation`
11. `evidence_status`
12. `unresolved_question_ids`
13. `notes`

Allowed `evidence_status` values:

1. `supported`
2. `mixed`
3. `weak`
4. `unsupported`

Evidence detail fields:

1. `evidence_id`
2. `question_id`
3. `source_id`
4. `file_id`
5. `source_role`
6. `is_fact_source`
7. `source_tier`
8. `evidence_status`
9. `can_support_project_fact`
10. `can_support_critical_claim`
11. `human_confirmation_status`
12. `provenance_support_type`
13. `claim_status`
14. `support_type`
15. `confidence`
16. `usage`
17. `snippet`
18. `matched_terms`

Allowed `usage` values:

1. `fact_support`
2. `methodology_support`
3. `context_support`
4. `weak_support`
5. `human_confirmation_context`

Citation slot fields:

1. `slot_id`
2. `section_id`
3. `question_id`
4. `claim_type`
5. `description`
6. `allowed_evidence`
7. `status`
8. `required_for_draft`
9. `instruction`

Allowed citation slot `status` values:

1. `filled`
2. `weak`
3. `unsupported`
4. `requires_human_confirmation`

Unsupported claim fields:

1. `claim_id`
2. `section_id`
3. `question_id`
4. `description`
5. `reason`
6. `required_action`

Evidence boundary rules:

1. Every `allowed_evidence` id must exist in `evidence_map.json`.
2. Every `evidence_details[].source_id` must exist in `source_index.json`.
3. `source_role=reference` must not use `usage=fact_support`.
4. `sample`, `expected_output_shape`, `template`, and `checklist` must not appear as citation evidence.
5. HARA-sensitive questions must use `citation_slots[].status=requires_human_confirmation`.
6. `provenance_support_type=project_fact` is allowed only for `T1_PROJECT_SOURCE` or `T0_HITL`.
7. `T3_REFERENCE_METHODOLOGY`, `T4_SAMPLE_STYLE_ONLY`, and `T5_AI_INFERENCE` must not be represented as project fact support.

Summary fields:

1. `total_sections`
2. `sections_supported`
3. `sections_mixed`
4. `sections_weak`
5. `sections_unsupported`
6. `total_citation_slots`
7. `filled_slots`
8. `weak_slots`
9. `unsupported_slots`
10. `human_confirmation_slots`
11. `total_allowed_evidence`
12. `fact_support_evidence`
13. `methodology_or_context_evidence`

### 7.3 plans/claim_support_matrix.json

Top-level fields:

1. `schema_version`
2. `run_id`
3. `generated_at`
4. `task_type`
5. `profile_id`
6. `profile_version`
7. `profile_source`
8. `confirmation_marker`
9. `claims`
10. `summary`

`schema_version` is `n4.claim_support_matrix.v1`.

Claim item fields:

1. `claim_category`
2. `required_human_confirmation`
3. `claim_status`
4. `evidence_status`
5. `human_confirmation_status`
6. `source_support`
7. `blocking_reason`
8. `notes`

Required rules:

1. Every `DocumentTypeRules.critical_claims` entry appears as a claim entry.
2. A claim requiring human confirmation without `T0_HITL` must use `claim_status=needs_confirmation` and `human_confirmation_status=pending`.
3. A claim marked `supported` must have `T1_PROJECT_SOURCE` project fact support and must not rely on `T3`, `T4`, or `T5` as project fact support.
4. Missing support is explicit through `evidence_status=missing` and an open blocking reason.

### 7.4 plans/outline_final.md

Required contents:

1. `# 最终写作大纲`
2. Run id
3. `Status: writing_planned`
4. `来源 artifacts`
5. `最终写作大纲`
6. Task ids
7. Evidence status
8. Citation slots
9. Allowed evidence
10. Human confirmation requirements
11. `需要人工确认`
12. `继续带入的 unsupported / weak evidence`
13. `阶段边界说明`

`outline_final.md` is not draft content. It must not create or simulate final prose.

### 7.5 plans/section_tasks.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `tasks`
4. `summary`
5. `warnings`

Task item fields:

1. `task_id`
2. `section_id`
3. `section_title`
4. `order`
5. `task_title`
6. `task_type`
7. `writing_goal`
8. `writing_mode`
9. `allowed_evidence`
10. `required_citation_slots`
11. `evidence_status`
12. `requires_human_confirmation`
13. `unresolved_question_ids`
14. `forbidden_sources`
15. `word_limit`
16. `must_include`
17. `must_not_include`
18. `confirmation_markers`
19. `future_output_path`
20. `source_support_requirements`
21. `source_support`
22. `provenance_summary`
23. `notes`

Allowed `task_type` values:

1. `prose`
2. `table`
3. `issue_list`
4. `summary`

Allowed `writing_mode` values:

1. `evidence_grounded_summary`
2. `conservative_candidate`
3. `confirmation_required`
4. `unsupported_stub`
5. `open_issue_list`

Task rules:

1. `forbidden_sources` must include `sample`, `expected_output_shape`, `template`, and `checklist`.
2. `word_limit` must be between 200 and 500.
3. HARA-sensitive tasks must include `NEEDS_USER_CONFIRMATION`.
4. HARA-sensitive tasks must forbid final professional conclusions.
5. `future_output_path` is only a planned Phase 5 path and does not create draft files.
6. `source_support` and `provenance_summary` expose source tiers and human confirmation status for downstream draft/final visibility.

### 7.6 plans/writing_plan.md

Required contents:

1. `# 写作计划`
2. Run id
3. `Status: writing_planned`
4. 摘要
5. 使用的输入
6. 写作顺序
7. 任务详情
8. Phase 5 引用规则
9. 需要人工确认
10. 继续带入的 unsupported / weak evidence
11. 阶段边界说明

### 7.7 Phase 4 Forbidden Artifacts

`plan-run` does not generate:

1. `draft/`
2. `review/`
3. `verify/`
4. `revised/`
5. `final/`
6. `trace/`
7. `learning/`
8. `revision_plan.json`
9. Root-level `commands/`, `skills/`, `schemas/`, `scripts/`, `agents/`, or `profiles/`

## 8. Phase 5 Artifacts

`draft-run` updates an existing Phase 4 run:

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
  plans/research_questions.json
  plans/evidence_map.json
  plans/unresolved_questions.md
  plans/citation_plan.json
  plans/claim_support_matrix.json
  plans/outline_final.md
  plans/section_tasks.json
  plans/writing_plan.md
  draft/section_001.md
  draft/section_002.md
  draft/full_draft.md
```

The command reads:

1. `manifest.json`
2. `task_brief.json`
3. `inputs/input_inventory.json`
4. `knowledge/source_index.json`
5. `knowledge/knowledge_gaps.md`
6. `plans/template_structure.json`
7. `plans/outline_l1.md`
8. `plans/research_questions.json`
9. `plans/evidence_map.json`
10. `plans/unresolved_questions.md`
11. `plans/citation_plan.json`
12. `plans/outline_final.md`
13. `plans/section_tasks.json`
14. `plans/writing_plan.md`

Phase 5 uses `section_tasks.json.tasks` as the writing task authority and `citation_plan.json.sections` as the evidence and citation authority.

### 8.1 manifest.json for draft-run

Fixed values after successful `draft-run`:

1. `status = drafted`
2. `phase = phase_5`

`artifacts` contains Phase 0 through Phase 4 artifact paths plus:

1. `draft/section_*.md`
2. `draft/full_draft.md`

Repeated `draft-run` execution may overwrite Phase 5 artifact contents, but each draft artifact path appears only once in `manifest.json`.

### 8.2 draft/section_*.md

One section draft is generated for each `section_tasks.json.tasks[]` item.

Required contents:

1. `# <Section Title>`
2. `Task id:`
3. `Section id:`
4. `Draft status: conservative_draft`
5. `Evidence status:`
6. `Writing mode:`
7. `Requires human confirmation:`
8. `Future review required: true`
9. `## 来源支持`
10. `## 草稿正文`
11. `## NEEDS_USER_CONFIRMATION`
12. `## 限制和开放问题`
13. `## 草稿边界说明`

来源支持 rules:

1. Every listed evidence id must come from the current task `allowed_evidence`.
2. Every listed evidence id must exist in `citation_plan.json`.
3. Every source id must trace to `source_index.json`.
4. If no allowed evidence exists, the section says `本章节没有可用的 allowed evidence。`
5. Reference evidence is identified as methodology, context, weak support, or human-confirmation context, not as project-specific fact.

Draft rules:

1. The draft is deterministic template text.
2. Unsupported tasks use conservative stubs.
3. Weak tasks use candidate language.
4. HARA-sensitive tasks include `NEEDS_USER_CONFIRMATION` and pending status.
5. S/E/C rating drafts use `S?`, `E?`, `C?`, and `TBD`.
6. No final HARA professional judgment is made.

### 8.3 draft/full_draft.md

Required contents:

1. `# HARA 危害分析报告保守草稿`
2. Run id
3. `Draft status: conservative_draft`
4. `Source: section_tasks.json + citation_plan.json`
5. `Not final: true`
6. `## 全局草稿边界说明`
7. `## 目录`
8. All section drafts in task order, separated by `---`
9. `## 全局开放问题和必需确认`
10. `## 阶段边界说明`

The global boundary note states:

1. This is a conservative draft.
2. The draft is generated only from allowed evidence in `citation_plan.json` and `section_tasks.json`.
3. It does not make final HARA professional judgments.
4. HARA confirmations, weak evidence, and unsupported content are marked with `NEEDS_USER_CONFIRMATION`.
5. Sample and expected-output-shape materials are not factual evidence.

### 8.4 Phase 5 Forbidden Artifacts

`draft-run` does not generate:

1. `review/`
2. `verify/`
3. `revised/`
4. `final/`
5. `trace/`
6. `learning/`
7. `revision_plan.json`
8. Root-level `commands/`, `skills/`, `schemas/`, `scripts/`, `agents/`, or `profiles/`

## 9. Phase 6 Artifacts

`review-run` updates an existing Phase 5 run:

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
  plans/research_questions.json
  plans/evidence_map.json
  plans/unresolved_questions.md
  plans/citation_plan.json
  plans/claim_support_matrix.json
  plans/outline_final.md
  plans/section_tasks.json
  plans/writing_plan.md
  draft/section_001.md
  draft/section_002.md
  draft/full_draft.md
  review/review_report.json
  review/template_review.md
  review/checklist_review.md
  review/evidence_review.md
  review/final_review.md
  verify/verify_report.json
  verify/failures.md
```

The command reads Phase 0 through Phase 5 artifacts. It uses `section_tasks.json` as the task authority, `citation_plan.json` as the citation authority, `source_index.json` and `provenance_index.json` as source authorities, `claim_support_matrix.json` as the critical-claim provenance authority, and `draft/` files as the review target.

### 9.1 manifest.json for review-run

Fixed values after successful `review-run`:

1. `status = reviewed_verified`
2. `phase = phase_6`

`artifacts` contains Phase 0 through Phase 5 artifact paths plus:

1. `review/review_report.json`
2. `review/template_review.md`
3. `review/checklist_review.md`
4. `review/evidence_review.md`
5. `review/final_review.md`
6. `verify/verify_report.json`
7. `verify/failures.md`

Repeated `review-run` execution may overwrite Phase 6 artifact contents, but each Phase 6 artifact path appears only once in `manifest.json`.

### 9.2 review/review_report.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `status`
4. `items`
5. `summary`
6. `warnings`

Allowed `status` values:

1. `passed`
2. `passed_with_warnings`
3. `open_blockers`
4. `failed`

Review item fields:

1. `review_id`
2. `severity`
3. `category`
4. `section_id`
5. `task_id`
6. `artifact`
7. `description`
8. `evidence_ids`
9. `suggested_fix`
10. `status`
11. `blocks_final`

Allowed `severity` values:

1. `P0`
2. `P1`
3. `P2`
4. `Info`

Phase 6 only writes review item `status=open`. P0 and P1 items block final readiness by default.

Required review categories include:

1. `template_mismatch`
2. `checklist_gap`
3. `unsupported_claim`
4. `weak_evidence`
5. `missing_source_support`
6. `invalid_citation`
7. `sample_fact_source`
8. `expected_output_shape_fact_source`
9. `reference_fact_misuse`
10. `hara_confirmation_required`
11. `final_hara_conclusion`
12. `missing_boundary_note`
13. `unresolved_question`
14. `knowledge_gap`
15. `formatting_issue`
16. `phase_boundary_violation`
17. `mechanical_draft_quality`
18. `provenance_policy_violation`
19. `no_issue`

### 9.3 review/*.md

`review/template_review.md` contains:

1. `# 模板审查`
2. 摘要
3. 模板章节覆盖 table
4. 问题
5. 说明

`review/checklist_review.md` contains:

1. `# Checklist 审查`
2. 摘要
3. Checklist 材料状态 table
4. 内置草稿检查清单 table
5. 问题
6. 说明

`review/evidence_review.md` contains:

1. `# 证据审查`
2. 摘要
3. 引用可追溯性 table
4. 来源边界检查
5. 确认检查
6. 问题

`review/final_review.md` contains:

1. `# 最终审查`
2. 审查摘要
3. 阻塞问题
4. 非阻塞问题
5. 需要人工确认
6. Unsupported / weak evidence
7. 建议的 Phase 7 动作
8. 阶段边界说明

### 9.4 verify/verify_report.json

Top-level fields:

1. `run_id`
2. `generated_at`
3. `status`
4. `summary`
5. `checks`
6. `blocking_failures`
7. `warnings`

Allowed `status` values:

1. `passed`
2. `passed_with_warnings`
3. `blocked`
4. `failed`

Each check contains:

1. `check_id`
2. `name`
3. `status`
4. `severity`
5. `details`
6. `related_artifacts`
7. `review_item_ids`

Required check ids:

1. `CHK-001 required_phase5_artifacts_exist`
2. `CHK-002 full_draft_exists`
3. `CHK-003 section_drafts_match_section_tasks`
4. `CHK-004 template_sections_present_in_full_draft`
5. `CHK-005 draft_sections_are_in_task_order`
6. `CHK-006 citation_ids_parseable`
7. `CHK-007 citation_ids_exist_in_citation_plan`
8. `CHK-008 citation_ids_allowed_by_section_task`
9. `CHK-009 cited_sources_exist_in_source_index`
10. `CHK-010 source_support_sections_present`
11. `CHK-011 sample_not_used_as_fact_source`
12. `CHK-012 expected_output_shape_not_used_as_fact_source`
13. `CHK-013 reference_not_used_as_project_fact`
14. `CHK-014 hara_sensitive_sections_keep_confirmation_markers`
15. `CHK-015 final_hara_conclusion_phrases_absent`
16. `CHK-016 unresolved_questions_carried_forward`
17. `CHK-017 knowledge_gaps_carried_forward`
18. `CHK-018 review_artifacts_exist`
19. `CHK-019 no_later_phase_artifacts_generated`
20. `CHK-020 manifest_updated_to_phase_6`
21. `CHK-021 provenance_index_exists`
22. `CHK-022 source_tier_policy_valid`
23. `CHK-023 sample_tier_is_style_only`
24. `CHK-024 reference_tier_is_methodology_only`
25. `CHK-025 critical_claim_source_tier_sufficient`
26. `CHK-026 required_human_confirmation_not_hidden`
27. `CHK-027 final_report_has_provenance_summary`
28. `CHK-028 final_delivery_has_open_confirmations`
29. `CHK-029 profile_version_recorded_when_available`

N4 provenance checks enforce:

1. Pending confirmation is not a failure when clearly exposed.
2. Critical claims marked `supported` require allowed `T1_PROJECT_SOURCE` support or `T0_HITL`.
3. `sample` and `expected_output_shape` remain `T4_SAMPLE_STYLE_ONLY`.
4. `reference` remains `T3_REFERENCE_METHODOLOGY`.
5. Final report and delivery summary provenance visibility checks are refreshed during Phase 7 after final artifacts are written.

### 9.5 verify/failures.md

Required contents:

1. `# 验证失败项`
2. Run id
3. 摘要
4. 阻塞失败项
5. 非阻塞 warnings
6. 人工确认阻塞项
7. Phase 7 建议
8. 阶段边界说明

If only HARA human confirmation remains open, the file states that no mechanical verification failure was found and final delivery remains blocked pending human confirmation.

### 9.6 Phase 6 Forbidden Artifacts

`review-run` does not generate:

1. `revision_plan.json`
2. `revised/`
3. `final/`
4. `trace/session_trace.jsonl`
5. `learning/`
6. Root-level `commands/`, `skills/`, `schemas/`, `scripts/`, `agents/`, or `profiles/`

A valid pre-existing `trace/hitl_decisions.jsonl` is allowed when it was created by interactive `record-hitl` calls before `review-run`. It does not cause `CHK-019 no_later_phase_artifacts_generated` to fail. Any other early `trace/` content, including `trace/session_trace.jsonl`, remains a Phase 6 boundary violation.

## 10. Phase 7 Artifacts

`finalize-run` updates an existing Phase 6 run:

```text
runs/<run_id>/
  manifest.json
  task_brief.json
  inputs/input_inventory.json
  knowledge/source_index.json
  knowledge/knowledge_gaps.md
  plans/template_structure.json
  plans/outline_l1.md
  plans/research_questions.json
  plans/evidence_map.json
  plans/unresolved_questions.md
  plans/citation_plan.json
  plans/outline_final.md
  plans/section_tasks.json
  plans/writing_plan.md
  draft/section_001.md
  draft/section_002.md
  draft/full_draft.md
  review/review_report.json
  review/template_review.md
  review/checklist_review.md
  review/evidence_review.md
  review/final_review.md
  verify/verify_report.json
  verify/failures.md
  revision_plan.json
  revised/full_draft.md
  revised/change_log.md
  final/final_report.md
  final/delivery_summary.md
```

The command reads Phase 0 through Phase 6 artifacts. It uses `review/review_report.json`, `review/final_review.md`, `verify/verify_report.json`, `verify/failures.md`, `plans/unresolved_questions.md`, `plans/claim_support_matrix.json`, `knowledge/provenance_index.json`, `knowledge/knowledge_gaps.md`, and `draft/full_draft.md` as the revision and final delivery basis.

After writing `final/final_report.md` and `final/delivery_summary.md`, Phase 7 refreshes the final-output provenance visibility checks in `verify/verify_report.json` and `verify/failures.md`.

### 10.1 manifest.json for finalize-run

Fixed values after successful `finalize-run`:

1. `status = finalized_with_open_items`
2. `phase = phase_7`

`finalized_with_open_items` 表示 final delivery package 已生成，但 HARA professional judgments 和其他 open items 仍等待 qualified human review。

`artifacts` contains Phase 0 through Phase 6 artifact paths plus:

1. `revision_plan.json`
2. `revised/full_draft.md`
3. `revised/change_log.md`
4. `final/final_report.md`
5. `final/delivery_summary.md`

Repeated `finalize-run` execution may overwrite Phase 7 artifact contents, but each Phase 7 artifact path appears only once in `manifest.json`.

### 10.2 revision_plan.json

Top-level fields:

1. `run_id`
2. `phase`
3. `generated_at`
4. `status`
5. `source_artifacts`
6. `summary`
7. `tasks`
8. `open_items_policy`

Fixed values:

1. `phase = phase_7`
2. `status = applied_with_open_items`
3. `summary.status = finalized_with_open_items`

`summary` fields:

1. `total_review_items`
2. `total_revision_tasks`
3. `auto_applied_tasks`
4. `pending_user_confirmation_tasks`
5. `carried_to_final_open_items`
6. `status`

Task item fields:

1. `revision_task_id`
2. `source_review_id`
3. `severity`
4. `category`
5. `section_id`
6. `task_id`
7. `artifact`
8. `action`
9. `auto_applicable`
10. `requires_user_confirmation`
11. `result`
12. `notes`

Allowed `action` values:

1. `preserve_NEEDS_USER_CONFIRMATION`
2. `carry_to_final_open_issues`
3. `add_boundary_note`
4. `add_source_support_note`
5. `mark_unresolved`
6. `omit_unsupported_final_claim`
7. `copy_without_change`

除非未来 phase 加入 external qualified human confirmation process，否则所有 HARA professional judgment tasks 都保持 pending。

### 10.3 revised/full_draft.md

Required contents:

1. `# HARA 危害分析报告修订草稿`
2. Run id
3. `Status: revised_with_open_items`
4. Phase 7 修订边界说明
5. 已应用修订摘要
6. 剩余人工确认项
7. 带 Phase 7 注释的原始保守草稿

The revised draft is a controlled revision artifact. It preserves `NEEDS_USER_CONFIRMATION`, `pending`, `TBD`, `S? / E? / C?`, unsupported, weak evidence, missing source, and knowledge gap markers.

Unsafe final professional claims 会替换为：

```text
NEEDS_USER_CONFIRMATION: Unsupported final professional judgment omitted by Phase 7.
```

### 10.4 revised/change_log.md

Required contents:

1. `# Phase 7 Change Log`
2. Run id
3. Summary
4. Source Artifacts
5. Applied Mechanical Changes
6. Items Carried Forward
7. Not Changed Automatically
8. Phase Boundary

### 10.5 final/final_report.md

Required contents:

1. `# HARA 危害分析报告最终交付包`
2. Run id
3. `Status: finalized_with_open_items`
4. 核心证据边界
5. 来源依据
6. 修订后草稿路径
7. 审查摘要
8. 验证摘要
9. 溯源摘要
10. Critical claim 来源支持
11. HARA 开放确认项
12. 证据不足 / 弱证据
13. 知识缺口和不可用材料
14. 剩余阻塞项
15. 交付限制
16. 下一步人工动作

`final/final_report.md` 不是 qualified HARA approval record。它必须说明需要 qualified human review，并说明 engine 不 finalize hazard identification、hazardous events、S/E/C ratings、ASIL or risk level、safety goals 或 HARA acceptability。

溯源摘要必须暴露 source tier counts、profile version、sample/reference limitations 和 pending human confirmations。它不能把 pending 或 unsupported critical claims 转成 approval language。

### 10.6 final/delivery_summary.md

Required contents:

1. `# 交付摘要`
2. Run id
3. `Status: finalized_with_open_items`
4. 生成的内容
5. 使用的输入
6. 审查 / 验证结果
7. 溯源摘要
8. 开放确认项
9. 剩余阻塞项
10. 需要人工确认
11. 已知限制
12. Workflow 范围说明
13. 建议下一步

The delivery summary must not claim that plugin entry, trace, learning, or candidate update artifacts are missing from the overall workflow. It only describes the finalization step. Trace and learning artifacts, when generated by `learning-run` or `write-run`, are stored under `trace/` and `learning/`. Candidate updates remain proposed and inactive unless explicitly approved later.

### 10.7 Phase 7 Forbidden Artifacts

`finalize-run` does not generate:

1. `trace/`
2. `learning/`
3. `trace/session_trace.jsonl`
4. `trace/hitl_decisions.jsonl`
5. `learning/run_summary.md`
6. `learning/candidate_profile_update.yaml`
7. `learning/candidate_skill_patch.md`
8. Root-level `commands/`, `skills/`, `schemas/`, `scripts/`, `agents/`, `profiles/`, or `plugin.json`

## 11. Phase 8 Artifacts

`learning-run` updates an existing Phase 7 run:

```text
runs/<run_id>/
  trace/session_trace.jsonl
  trace/hitl_decisions.jsonl
  learning/run_summary.md
  learning/reusable_patterns.md
  learning/candidate_profile_update.yaml
  learning/candidate_skill_patch.md
  learning/promotion_report.md
```

`record-hitl` appends a HITL decision to:

```text
runs/<run_id>/trace/hitl_decisions.jsonl
```

`write-run` creates a new run and executes ingest, outline, evidence, plan, draft, review, finalize, and learning.

### 11.1 Claude Code Plugin Entry

Phase 8 creates:

```text
.claude-plugin/plugin.json
commands/write.md
```

The plugin manifest command path is:

```text
./commands/write.md
```

The product shorthand is `/write`; the Claude Code plugin command is:

```text
/ai-writing-plugin:write
```

Root-level `plugin.json` is not used.

### 11.2 manifest.json for learning-run

Fixed values after successful `learning-run`:

1. `status = completed_with_candidate_updates_proposed`
2. `phase = phase_8`

`artifacts` contains Phase 0 through Phase 7 artifact paths plus:

1. `trace/session_trace.jsonl`
2. `trace/hitl_decisions.jsonl`
3. `learning/run_summary.md`
4. `learning/reusable_patterns.md`
5. `learning/candidate_profile_update.yaml`
6. `learning/candidate_skill_patch.md`
7. `learning/promotion_report.md`

Repeated `learning-run` execution may overwrite learning Markdown/YAML files and reconstructed session trace, but each Phase 8 artifact path appears only once in `manifest.json`. Default HITL gates are not duplicated.

If an older run already contains `ingest_confirmation` or `outline_confirmation`, `learning-run` treats them as aliases for `material_classification_confirmation` and `outline_l1_confirmation` when deciding whether default gates are missing. The raw legacy records are preserved.

### 11.3 trace/session_trace.jsonl

Each JSONL record contains:

1. `timestamp`
2. `run_id`
3. `stage`
4. `event`
5. `artifact`
6. `status`
7. `source`

Required stages include:

1. `ingest`
2. `outline`
3. `evidence`
4. `planning`
5. `draft`
6. `review`
7. `finalize`
8. `learning`

### 11.4 trace/hitl_decisions.jsonl

Each JSONL record contains:

1. `timestamp`
2. `run_id`
3. `stage`
4. `decision`
5. `user_comment`
6. `affected_sections`
7. `next_action`
8. `requires_user_confirmation`
9. `status`

Default gates:

1. `task_goal_confirmation`
2. `material_classification_confirmation`
3. `outline_l1_confirmation`
4. `evidence_confirmation`
5. `final_delivery_confirmation`
6. `candidate_update_confirmation`

默认 noninteractive decisions 使用 `not_collected_in_noninteractive_run` 并保持 `pending`。engine 不能生成 fake approvals。

Backward-compatible aliases:

1. `ingest_confirmation` -> `material_classification_confirmation`
2. `outline_confirmation` -> `outline_l1_confirmation`

Newly recorded HITL decisions use canonical gate names.

### 11.5 learning/run_summary.md

Required contents:

1. `# 运行摘要`
2. Run id
3. `Status: completed_with_candidate_updates_proposed`
4. 执行的 workflow
5. 关键 artifacts
6. 审查与验证摘要
7. 最终交付摘要
8. 人工确认状态
9. 继续带入的开放问题
10. 生成的 candidate updates
11. 不会自动应用的内容

The human confirmation status section lists all canonical HITL gates. Each gate status is one of `recorded`, `missing`, `not_collected_in_noninteractive_run`, or `pending_user_confirmation`.

### 11.6 learning/reusable_patterns.md

Required contents:

1. `# Reusable Patterns`
2. Document type
3. Reusable workflow patterns
4. Reusable review patterns
5. Reusable evidence rules
6. Non-reusable facts
7. Human confirmation rules

It must state that sample documents and expected output shape are not fact sources.

### 11.7 learning/candidate_profile_update.yaml

Required candidate boundary fields:

```text
status: proposed
active: false
auto_applied: false
requires_user_approval: true
rollback_supported: true
stable_skill_overwrite_allowed: false
```

### 11.8 learning/candidate_skill_patch.md

Required boundary statements:

1. `proposed_only`
2. `not applied`
3. `No stable skill was overwritten`
4. `requires user approval`

不会创建或修改实际 stable skill。

### 11.9 learning/promotion_report.md

Required boundary statements:

1. `Current state: proposed`
2. `Not promoted automatically`
3. `Candidate activated: no`
4. `Stable skill overwritten: no`

### 11.10 Phase 8 Forbidden Artifacts and Systems

Phase 8 does not create:

1. `skills/`
2. `agents/`
3. `profiles/`
4. `scripts/`
5. `hooks/`
6. `monitors/`
7. `.mcp.json`
8. `.lsp.json`
9. `settings.json`
10. root-level `plugin.json`

Phase 8 不引入 MetaHarness、RAG、vector databases、LangChain、MCP servers、hooks、background monitors 或 agent frameworks。

## 12. Phase N7 Correction and Profile Promotion Artifacts

Phase N7 artifacts 由 `correction-harvest` 和 `profile-promote` 生成。它们不属于常规 Phase 0-8 `write-run` lifecycle，`write-run` 不会自动读取或应用这些 artifacts。

N7 可创建：

```text
runs/<run_id>/
  trace/correction_events.jsonl
  learning/candidate_profile_patch.yaml
  learning/candidate_eval_case.json
  learning/profile_promotion_report.json
  learning/profile_promotion_report.md
  learning/profile_rollback_metadata.yaml
  learning/rollback_previous_profile.yaml
```

N7 boundaries：

1. Correction events 必须来自 explicit user correction input。
2. Candidate profile patches 保持 `status: proposed`、`activation_status: inactive` 和 `auto_apply: false`。
3. Candidate profile patches 只能提出 safe additive list updates 或 safe mapping-key updates。
4. 放松 sample/reference/final-status/source-role policy 的修改不能自动应用。
5. Promotion 需要 explicit approval file、passing N6 eval report、matching base profile hash、patched profile validation 和 rollback metadata。
6. Promotion 只作用于明确传入的 external YAML document profile。
7. Promotion never modifies stable Skill files or built-in Python document type rules。
8. Promotion report 是 engineering gate report，不是 professional approval、compliance approval、risk acceptance、production readiness approval 或 final report approval。

### 12.1 trace/correction_events.jsonl

Each JSONL record contains:

1. `event_id`
2. `profile_id`
3. `profile_version`
4. `correction_type`
5. `field`
6. `operation`
7. `value`
8. `rationale`
9. `source`
10. `status`
11. `auto_patch_status`

如果 input 省略 `event_id`，harvester 会从 canonical event content 生成 deterministic `corr-<hash>` id。

### 12.2 learning/candidate_profile_patch.yaml

Required boundary fields：

```text
patch_id: n7patch-<stable-hash>
status: proposed
activation_status: inactive
auto_apply: false
phase: N7
safety.requires_human_approval: true
safety.requires_eval: true
safety.allowed_without_approval: false
safety.stable_skill_update_allowed: false
safety.built_in_rules_update_allowed: false
promotion.promoted: false
rollback.required: true
```

`base_profile` 包含 `profile_id`、`profile_version`、`profile_path` 和 `sha256`。

`proposed_changes` 只包含 N7 allowlisted safe operations。Unsafe 或 high-risk corrections 会记录在 `blocked_changes` 中，不能自动应用。

### 12.3 learning/candidate_eval_case.json

Required contents：

1. `case_id`
2. `phase = N7`
3. `mode = candidate_profile_patch`
4. `profile_id`
5. `candidate_patch_path`
6. `expected.patch_status = inactive`
7. `expected.auto_apply = false`
8. `expected.requires_human_approval = true`
9. `expected.requires_eval = true`
10. `expected.stable_skill_update_allowed = false`

该 artifact 是 deterministic candidate profile patch guard。它不批准 patch，也不批准 final report。

### 12.4 learning/profile_promotion_report.json and .md

Required contents：

1. `schema_version = profile_promotion_report.v1`
2. `phase = N7`
3. `status`
4. `promoted`
5. `dry_run`
6. candidate patch path and id
7. target profile path
8. eval report path, hash, and result summary
9. approval gate information
10. base and new profile metadata when applicable
11. rollback status
12. non-approval notice

允许的 statuses：

```text
blocked_pending_human_approval
blocked_missing_eval
blocked_eval_failed
blocked_approval_mismatch
blocked_profile_hash_mismatch
blocked_profile_validation_failed
blocked_unsafe_target
blocked_unsupported_operation
dry_run_ready_to_promote
promoted
failed
```

### 12.5 learning/profile_rollback_metadata.yaml

Required contents：

1. `rollback_id`
2. `promotion_id`
3. `profile_id`
4. `previous_profile.path`
5. `previous_profile.version`
6. `previous_profile.sha256`
7. `previous_profile.content_backup_path`
8. `new_profile.path`
9. `new_profile.version`
10. `new_profile.sha256`
11. `rollback_requires_human_approval = true`
12. `stable_skill_touched = false`
13. `built_in_rules_touched = false`

`learning/rollback_previous_profile.yaml` 是 previous external profile content 的 byte-for-byte backup，用于 audit 和 human-controlled rollback planning。

## 13. Fixture Contract

当前 deterministic fixture：

```text
examples/hara_minimal_fixture/task.yaml
examples/hara_minimal_fixture/inputs/
```

`task.yaml` 中的 input paths 相对于 `task.yaml` 所在目录解析。

仓库不依赖 optional local raw material folders。如果本地存在 `HARA报告生成参考资料集_EPS/`，不要直接把它作为 automated test fixture。测试应使用 `examples/` 下已提交的 deterministic fixtures，尤其是 `examples/hara_minimal_fixture/`。

## 14. Phase Boundary

Phase 0 through Phase 8 不实现：

1. Stable skill promotion.
2. Active profile management.
3. Automatic candidate profile activation.
4. Automatic stable skill overwrite.
5. Root-level `skills/`, `agents/`, `profiles/`, `scripts/`, `hooks/`, or `monitors/`.
