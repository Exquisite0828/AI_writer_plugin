---
name: test-report-document-type
description: 中文优先指导 test_report document type work，同时保留 pass/fail、defect、coverage、release readiness、source tier、provenance、sample/reference、HITL、final-report 和 candidate-update boundaries。
---

# Test Report Document Type Skill

Use this guideline for `task_type: test_report`.

## 中文交互默认规则

默认用中文解释测试报告 workflow、测试材料、执行结果证据、缺陷边界、coverage/release readiness 的 open confirmations，以及最终 artifact。保留 `test_report`、pass/fail、defect、coverage、release readiness、HITL、NEEDS_USER_CONFIRMATION 等英文关键术语。

如果测试计划、结果表或缺陷材料为英文，可以保留原文字段和证据片段；用户说明优先中文。不要把 sample test report 或模型推断写成真实测试结论。

This Skill.md is guideline material only. It must use plugin workflow and must call the Python engine. Skill.md does not replace artifact contract, schema validation, source index, evidence trace, review, verify, HITL trace, or candidate update state control.

## Document Type Purpose

test_report supports review-ready test report packages based on test plans, test results, defect records, environment information, coverage material, templates, and checklists.

It must not invent test results, pass/fail status, coverage, defect status, or release readiness.

## Supported Level And Positioning

`test_report` is an official L3 built-in document type backed by built-in `DocumentTypeRules`, fixtures, regression tests, and this domain guideline.

The command layer remains generic. There is no test_report-specific pipeline.

## Typical Inputs

Recommended inputs:

- `system_under_test.md` as `source`
- `test_plan.md` as `source`
- `test_results.csv` as `source`
- `defect_summary.md` as `source`
- `test_report_template.md` as `template`
- `checklist.md` as `checklist`
- `test_methodology_reference.md` as `reference`
- `sample_test_report.md` as `sample`

## Default / Expected Sections

The test_report default sections are:

- Document purpose and scope
- Test object and version
- Input materials and assumptions
- Test scope and strategy
- Test environment
- Test cases and execution summary
- Test results summary
- Defects and anomalies
- Coverage and limitations
- Conclusion candidate
- Open issues and required confirmations
- Review summary

## Critical Claims

test_report critical claims include:

- test object and version
- test scope coverage
- test environment
- test case execution status
- pass/fail result
- defect severity or status
- coverage percentage or sufficiency
- final test conclusion
- release readiness or acceptance recommendation

These require source evidence or HITL. If evidence or a recorded human decision is missing, keep `NEEDS_USER_CONFIRMATION`.

## Requires Human Confirmation

Do not automatically finalize:

- final pass/fail conclusion
- release readiness or acceptance recommendation
- defect severity acceptance
- coverage sufficiency conclusion
- unresolved issue acceptance
- test sufficiency conclusion

pass/fail, defect, coverage, and release readiness cannot be invented from sample material or model inference. Test result conclusions must have project source or HITL.

## Forbidden Final Claims

The following are forbidden unless explicit T0/T1 support and HITL confirmation support them:

- all tests passed
- release is approved
- no defects exist
- coverage is complete
- system is production ready
- quality is guaranteed
- test conclusion is approved
- ready for production without risk

These are warning examples, not recommended output.

## Source / Sample / Reference / Provenance Policy

- test result source material is T1 when parsed and relevant.
- HITL / explicit human confirmation is T0.
- template and checklist constraints are T2.
- test_methodology_reference is T3; it may support methodology or terminology but must not prove project-specific test results, pass/fail, defect state, coverage sufficiency, or release readiness.
- sample_test_report is T4; it can guide structure, style, section granularity, and table shape only.
- generated / unknown inference is T5 and cannot support critical claim.

sample not fact source.
sample is not fact source.
sample content must not supply project-specific test results, defect status, coverage status, pass/fail status, or final conclusions.
reference is not project-specific fact support.
reference cannot prove project facts.
T3/T4/T5 cannot support critical claim by themselves.

## Review Focus

Review focus includes:

- template completeness
- test scope and requirements coverage
- test result evidence alignment
- unsupported pass/fail or coverage claims
- unsupported defect severity or status claims
- unsupported release readiness claims
- sample misuse
- reference misuse as project fact
- unresolved issues and limitations
- unconfirmed final test conclusion

## Verification Focus

Verification focus includes:

- required artifacts
- citation integrity
- source tier and provenance
- sample not fact source
- reference not project fact source
- critical claims confirmation
- test result claims require evidence or HITL
- pass/fail conclusion requires evidence or HITL
- document type terminology isolation
- candidate update inactive

## Final Report Boundary

final report is not approval. The final package is for human review and must carry open confirmations where critical test_report claims remain unresolved.

Do not describe the final report as validated, production ready, release approved, or ready for production without explicit T0/T1 support and a rule that allows that wording.

## Demo Fixture / Command

```bash
.venv/bin/python -m ai_writing_plugin write-run --task examples/test_report_demo_fixture/task.yaml
```

## Common Gotchas

- Do not infer pass/fail from a sample report.
- Do not invent coverage or defect status from missing tables.
- Do not use reference methodology to prove this project's test result.
- Missing table-style test inputs should become gaps or open confirmations.
- candidate update proposed/inactive; `candidate_profile_update.yaml` and `candidate_skill_patch.md` must remain proposed and inactive unless the user explicitly approves promotion in a separate process.
