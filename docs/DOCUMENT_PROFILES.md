# Document Profiles

这份指南说明如何使用 `generic_document` 和 external `document_profile.yaml`，而不新增 built-in document type。

## 支持级别

当前项目有三种支持级别：

| 级别 | 机制 | 示例 |
| --- | --- | --- |
| official L3 built-in | 内置 `DocumentTypeRules`、fixtures、tests 和 Skill guideline | `hara`、`technical_solution`、`test_report`、`fsr` |
| document-type skill 层 | PascalCase 路径下的 `SKILL.md` + 逐步子 skill + demo fixture | `ItemDefinitionDocument`、`FunctionalSafetyRequirement`、`TechnicalSafetyConcept` |
| generic mode | 共享 generic rules，加用户声明的 task inputs | `generic_document` |
| external profile | 由 task file 加载并通过校验的 `document_profile.yaml` | `custom_technical_note` demo |

`generic_document` 和 `custom_technical_note` 都不是 official L3 built-ins。

## 什么时候用 generic_document

适合使用 `generic_document` 的情况：

- 文档仍然由项目 `source` materials 驱动；
- 你有 `template` 和 `checklist`；
- 你希望使用共享 artifact tree；
- unresolved critical claims 可以保持 open；
- 当前没有适合该领域的 official L3 built-in。

示例：

```yaml
task_type: generic_document
task_title: Generate migration decision memo
output_format: markdown
allow_inference: false
critical_claims:
  - final decision recommendation
  - release readiness conclusion
requires_human_confirmation:
  - final decision recommendation
inputs:
  - path: inputs/source.md
    role: source
  - path: inputs/template.md
    role: template
  - path: inputs/checklist.md
    role: checklist
  - path: inputs/reference.md
    role: reference
  - path: inputs/sample.md
    role: sample
```

## 什么时候创建 external profile

适合创建 external `document_profile.yaml` 的情况：

- 该文档类型会在多次运行中复用；
- 它有稳定 sections 和 critical claims；
- 它需要可复用的 final-status policy；
- 它不应成为 official L3 built-in；
- 维护者希望 profile changes 作为数据接受 review。

现有 external profile demo：

```text
profiles/document_types/customer_demo/custom_technical_note.yaml
examples/custom_technical_note_profile_demo_fixture/task.yaml
```

task file 通过以下字段引用 profile：

```yaml
task_type: custom_technical_note
document_profile_path: profiles/document_types/customer_demo/custom_technical_note.yaml
```

## Profile fields overview

常见 profile fields：

```yaml
profile_id: customer_demo.custom_technical_note
profile_version: 0.1.0
task_type: custom_technical_note
display_name: Custom Technical Note
description: A profile description.
default_sections:
  - Background
required_sections:
  - background
critical_claims:
  - deployment risk
requires_human_confirmation:
  - deployment risk
forbidden_final_claims:
  - deployment is production ready
confirmation_marker: NEEDS_USER_CONFIRMATION
fact_source_roles:
  - source
non_fact_source_roles:
  - sample
  - template
  - checklist
  - reference
reference_policy: Reference materials may support methodology but must not prove project-specific facts.
sample_policy: Sample documents may guide structure and style but must not be used as fact sources.
default_final_status: ready_for_human_review
allowed_final_statuses:
  - ready_for_human_review
  - finalized_with_open_items
  - blocked_pending_confirmation
review_focus:
  - unsupported critical claims
verification_focus:
  - sample not fact source
  - reference not project fact source
  - critical claims confirmation
candidate_learning_policy: Generate candidate updates only; keep proposed/inactive unless explicitly reviewed.
```

具体 contract 由 profile loader 和 tests enforce。

## Profile validation boundary

External profiles 必须先通过 validation。无效 profile 应 fail safely，不能生成 successful final package。

Profile validation 不等于专业批准。它只表示 profile data 在结构上可以被 engine 使用。

## Markdown Spec -> candidate profile

`Markdown Spec` 是给 human reviewers、domain experts 和 AI coding tools 使用的说明层。

它不是唯一 runtime machine rule。

runtime engine 使用结构化规则：

- built-in Python `DocumentTypeRules`；
- YAML external `document_profile.yaml`；
- review 后生成的 candidate profile material。

`profile-from-spec` command 可以从 `Markdown Spec` 生成 candidate profile material：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m ai_writing_plugin profile-from-spec --spec docs/document_types/generic_document_SPEC.md --out /tmp/candidate-profile
```

生成内容是 candidate output，不会自动 active。

## Correction harvesting 和 promotion gate

Correction flow：

```text
explicit correction events -> correction harvesting -> candidate patch -> eval -> promotion gate
```

关键边界：

- correction harvesting 不能自动修改 stable profile；
- candidate patch 不能自动覆盖 stable profile；
- candidate profile output 默认 proposed/inactive；
- promotion 需要 explicit human approval、eval result、rollback metadata、schema checks 和 base hash checks；
- stable Skill.md files 不会被 profile promotion 覆盖。

## source / sample / reference 边界

Profiles 必须保持和 built-in document types 一样的 source policy：

- `source` 在可解析且相关时可以支持项目事实；
- `template` 约束结构；
- `checklist` 约束 review coverage；
- `sample` 只用于 style 和 shape；
- `reference` 只用于 methodology 或 background；
- critical claims require source or HITL。

不要写入允许 `sample` 提供事实、或允许 `reference` 证明项目事实的 profile policy。

## Profiles 不应该做什么

Profiles 不应该：

- 创建一套独立 pipeline；
- 绕过 Python deterministic engine；
- 把 `Markdown Spec` 当成唯一 runtime rule；
- 自动确认 critical claims；
- 把 `final_report.md` 变成专业批准文件；
- 让 eval passed 变成专业批准；
- 自动 promote candidate patches；
- 覆盖 stable Skills；
- 用 external profile 重新实现 TSC（应直接使用内置 `task_type: TechnicalSafetyConcept`）；
- 通过命名为 `hsc` / `ssc` 等方式实现下游 HSC/SSC（硬件/软件安全概念仍 deferred）。
