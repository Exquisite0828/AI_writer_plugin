# Document Profile Spec Template

Status: future design template. The current Python package does not load profiles or generate candidate profiles from Markdown.

这个模板用于讨论未来的 `Markdown Spec` -> `document_profile.yaml` / candidate profile 工作。

`Markdown Spec` 是上游说明层，用来帮助 human reviewers、domain experts 和 Codex 以可审查方式描述一个 document type。它不是当前 engine runtime rule。当前仓库没有 profile loader、spec generator或Python document-type rules；未来实现必须先通过独立 active phase/spec。

任何未来生成结果都必须是candidate package。candidate profile不能自动promote，active profiles和stable Skill不能被自动覆盖。当前Python不会生成或应用这些candidate。

保留的英文边界原句：

- Markdown Spec is an upstream explanation layer.
- sample must not be used as a fact source.
- reference must not prove project-specific facts.
- candidate profile must not be automatically promoted.
- stable Skill must not be automatically overwritten.
- human review is required.

## Metadata

- Spec title:
- Spec version:
- Spec status: draft / candidate / reviewed
- Target task_type:
- Target display_name:
- Owner / author:
- Last updated:
- Intended support level: L1 / L2 / L3 candidate

## 1. Document Purpose

说明这个 document type 要产出什么。

## 2. Target Audience

说明谁会阅读、review 或维护该文档。

## 3. Typical Use Cases

列出该 document type 的典型使用场景。

## 4. Typical Input Materials

说明预期的 `source`、`template`、`checklist`、`sample` 和 `reference` 材料。

## 5. Source / Template / Checklist / Sample / Reference Roles

- `source`: 可以支持 project-specific facts。
- `template`: 约束文档结构和格式。
- `checklist`: 约束 review coverage 和 quality gates。
- `sample`: 不能作为 fact source；只能指导 structure、style、section granularity、table shape 和 final deliverable appearance。
- `reference`: 不能证明 project-specific facts；只能支持 methodology、terminology 或 review rationale。

## 6. Default Sections

- TODO

## 7. Required Sections

- TODO

## 8. Critical Claims

Critical claims 必须有 `source` evidence 或 HITL confirmation。如果 evidence 或 HITL 缺失，生成文档必须保留 `NEEDS_USER_CONFIRMATION` 或 open item。

- TODO

## 9. Requires Human Confirmation

- TODO

## 10. Forbidden Final Claims

Final status 不能使用 approval-like wording，包括 `approved`、`validated`、`compliant`、`production_ready` 或 `risk_accepted`。

- TODO

## 11. Review Focus

- TODO

## 12. Verification Focus

- TODO

## 13. Sample Policy

明确写出 `sample` material 不能作为 fact source。

## 14. Reference Policy

明确写出 `reference` material 不能证明 project-specific facts。

## 15. Final Status Policy

使用安全状态，例如：

- `ready_for_human_review`
- `finalized_with_open_items`
- `blocked_pending_confirmation`

不要使用 approval-like statuses。

## 16. Candidate Learning Policy

明确写出 generated candidate updates 在 explicit review 前保持 proposed/inactive。

## 17. Common Gotchas

- 不要从 `sample` 推断 project facts。
- 不要把 `reference` 当成 project fact evidence。
- 不要把未确认 critical claims 写成 final approval。
- 不要自动 promote candidate profiles。
- 不要自动修改 stable Skills。

## 18. Recommended Demo Fixture Structure

```text
examples/<task_type>_demo_fixture/
  task.yaml
  inputs/
    source.md
    template.md
    checklist.md
    reference.md
    sample.md
```

## 19. Human Review Checklist

- structured profile block 包含完整 required fields；
- sample policy 阻止 `sample` 作为 fact source；
- reference policy 阻止 `reference` 证明 project facts；
- critical claims 覆盖该 document type 的关键声明；
- final status policy 是 non-approval；
- candidate profile remains inactive。

## Structured Profile Block

生成器会 deterministically 解析且只解析一个名为 `document_profile` 的 fenced YAML block。

```yaml document_profile
profile_id: candidate.example_task_type
profile_version: 0.1.0-candidate
task_type: example_task_type
display_name: Example Document
description: Example description.
default_sections:
  - Background
required_sections:
  - background
optional_sections: []
critical_claims:
  - final decision
requires_human_confirmation:
  - final decision
forbidden_final_claims:
  - final decision is approved
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
candidate_learning_policy: Generate candidate updates only; keep proposed/inactive unless explicitly approved.
terminology: {}
output_labels: {}
```
