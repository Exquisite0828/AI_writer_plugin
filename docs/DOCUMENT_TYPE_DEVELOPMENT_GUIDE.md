# Document Type Development Guide

这份指南说明如何在未来新增 document type，同时不复制 pipeline、不削弱 evidence / HITL 边界。

当前 official L3 built-in document types 是 `hara`、`technical_solution`、`test_report`、`fsr`。
`generic_document` 是 L1 generic mode；validated external `document_profile.yaml` 是 L2 external profile mechanism。

TSC / Technical Safety Concept 仍 deferred。不要在没有单独 active phase/spec 的情况下顺手实现 TSC。

## 标准扩展流程

新增 official L3 document type 时，按以下顺序推进：

1. 写 `docs/document_types/<task_type>_SPEC.md`。
2. 写 `ai_writing_plugin/document_types/<task_type>.py`。
3. 在 document type registry 中注册 rules。
4. 创建 `examples/<task_type>_demo_fixture/`。
5. 写 `tests/test_<task_type>_demo.py`。
6. 只有在 guideline 支持有价值时，才新增 `skills/document-types/<task_type>/SKILL.md`。
7. 跑现有 `hara`、`technical_solution`、`test_report`、`fsr` 回归。

不要跳过现有 document types 的回归测试。

## Rules checklist

每个新的 `DocumentTypeRules` 定义至少覆盖：

- `task_type`
- `display_name`
- `description`
- `default_sections`
- `required_sections`
- `optional_sections`
- `critical_claims`
- `requires_human_confirmation`
- `forbidden_final_claims`
- `confirmation_marker`
- `fact_source_roles`
- `non_fact_source_roles`
- `reference_policy`
- `sample_policy`
- `default_final_status`
- `allowed_final_statuses`
- `review_focus`
- `verification_focus`
- `candidate_learning_policy`
- terminology and output labels only when needed for user-facing wording

## Fixture checklist

demo fixture 应包含：

- 用于项目事实的 `source` files；
- 用于结构的 `template` file；
- 用于 review criteria 的 `checklist` file；
- 只用于 methodology/background 的 `reference` file；
- 只用于 shape/style 的 `sample` file；
- 带 `task_type` 的 task YAML。

`sample` is not fact source。`reference` is not project-specific fact support。

## Test checklist

推荐覆盖：

- full run succeeds；
- required artifacts exist；
- input roles are correct；
- `sample` 不进入 `source_index` 作为 fact source；
- `sample` 不进入 `citation_plan` 作为 fact evidence；
- `reference` 不证明 project facts；
- critical claims require evidence or HITL；
- forbidden final claims 不会成为 conclusions；
- final status 保持 conservative；
- candidate updates remain proposed/inactive；
- unrelated document type terminology leakage checks；
- 现有 `hara`、`technical_solution`、`test_report`、`fsr` 回归仍通过。

使用 semantic assertions。不要写脆弱的 full-document golden snapshot。不要断言 registry 永远只有三类或四类 document types。

## Stable Skill policy

`skills/document-types/<task_type>/SKILL.md` 是可选 guideline material。`Skill.md` 不能替代 Python engine、artifact contract、schema validation、source index、evidence trace、review/verify、HITL trace 或 candidate update state control。

## 禁止变更

- 不复制 pipeline；
- 不把 `sample` 当成 fact source；
- 不让 `reference` 证明 project facts；
- 不自动确认 critical claims；
- 不自动激活 candidate update；
- 不把 `final report` 描述成专业批准文件；
- 不引入大平台、RAG、LangChain、vector DB 或复杂 agent framework；
- 不在没有单独设计和迁移计划时修改 artifact contract；
- 不在当前任务中顺手实现 TSC。

对应英文 guardrails：

- Do not copy a pipeline.
- Do not use sample as fact source.
- Do not let reference prove project facts.
- Do not automatically confirm critical claims.

## Minimum verification

```bash
.venv/bin/python -m pytest tests/test_document_type_rules.py -q
.venv/bin/python -m pytest tests/test_technical_solution_demo.py -q
.venv/bin/python -m pytest tests/test_test_report_demo.py -q
.venv/bin/python -m pytest tests/test_fsr_demo.py -q
.venv/bin/python -m pytest -q
claude plugin validate .
.venv/bin/python -m ai_writing_plugin write-run --task examples/hara_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/technical_solution_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
.venv/bin/python -m ai_writing_plugin write-run --task examples/fsr_demo_fixture/task.yaml
```
