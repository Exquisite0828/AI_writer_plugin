# Test Report Document Type Spec

## 1. Purpose

Test report documents support traceable reporting for test execution results, defect status, coverage limitations, and open release-review questions.

The document type is conservative by default. It may summarize source-backed test evidence, but it must not invent test results, pass/fail status, defect state, coverage sufficiency, or final release conclusions.

## 2. Target Audience

QA leads, development teams, release reviewers, project maintainers, and stakeholders who need a reviewable test evidence package.

## 3. Typical Inputs

- source: `system_under_test.md`, `test_plan.md`, `test_results.csv`, `defect_summary.md`
- template: `test_report_template.md`
- checklist: `checklist.md`
- reference: `test_methodology_reference.md`
- sample: `sample_test_report.md`

## 4. Default Sections

- 文档目的和范围
- 测试对象和版本
- 输入材料和假设
- 测试范围和策略
- 测试环境
- 测试用例和执行摘要
- 测试结果摘要
- 缺陷和异常
- 覆盖情况和限制
- 结论候选
- 开放问题和必需确认
- 审查摘要

## 5. Critical Claims

- test object and version
- test scope coverage
- test environment
- test case execution status
- pass/fail result
- defect severity or status
- coverage percentage or sufficiency
- final test conclusion
- release readiness or acceptance recommendation

## 6. Requires Human Confirmation

- final pass/fail conclusion
- release readiness or acceptance recommendation
- defect severity acceptance
- coverage sufficiency conclusion
- unresolved issue acceptance
- test sufficiency conclusion

Even when source files contain test results, whether the results are sufficient for release, whether unresolved defects are acceptable, and whether testing is adequate remain human review decisions.

## 7. Forbidden Final Claims

- all tests passed
- no defects exist
- system is production ready
- release is approved
- quality is guaranteed
- coverage is complete
- test conclusion is approved
- ready for production without risk

These phrases, or equivalent final approval semantics, must not be written as conclusions unless source evidence and recorded HITL confirmation support them.

## 8. Source Policy

`source` inputs may support project-specific facts, including the test object, test plan, execution status, defect records, and explicit source-backed limitations.

`sample` test reports may guide report shape, section granularity, and style only. They must not supply project-specific test results, metrics, defects, pass/fail status, or final conclusions.

`reference` inputs may support testing methodology, terminology, or report structure. They must not prove project-specific test results, pass/fail status, defect state, coverage, or release readiness.

Templates and checklists are non-fact inputs unless a future phase explicitly changes the artifact contract.

## 9. Review Focus

- template completeness
- test scope and requirements coverage
- test result evidence alignment
- unsupported pass/fail or coverage claims
- unsupported defect severity or status claims
- sample misuse
- reference misuse as project fact
- unresolved issues and limitations
- unconfirmed final test conclusion

## 10. Verification Focus

- required artifacts
- citation integrity
- sample not fact source
- reference not project fact source
- critical claims confirmation
- test result claims require evidence or HITL
- pass/fail conclusion requires evidence or HITL
- candidate update inactive
- document type terminology isolation

## 11. Final Status Policy

Default final status: `ready_for_human_review`.

Allowed final statuses:

- `ready_for_human_review`
- `finalized_with_open_items`
- `blocked_pending_confirmation`

No unconditional approved status is allowed.

## 12. Result Integrity Boundary

The engine must not fabricate:

- test results
- pass/fail status
- defect severity or acceptance status
- coverage percentage or sufficiency
- release readiness
- final test conclusion

If a claim is not source-backed or HITL-confirmed, the output must keep `NEEDS_USER_CONFIRMATION` or an open confirmation item.
