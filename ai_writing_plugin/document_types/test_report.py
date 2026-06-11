from __future__ import annotations

from .base import DocumentTypeRules


TEST_REPORT_CRITICAL_CLAIMS = (
    "test object and version",
    "test scope coverage",
    "test environment",
    "test case execution status",
    "pass/fail result",
    "defect severity or status",
    "coverage percentage or sufficiency",
    "final test conclusion",
    "release readiness or acceptance recommendation",
)


TEST_REPORT_RULES = DocumentTypeRules(
    task_type="test_report",
    display_name="测试报告",
    description="面向测试执行结果、缺陷状态、覆盖情况和结论确认的测试报告写作任务。",
    default_sections=(
        "文档目的和范围",
        "测试对象和版本",
        "输入材料和假设",
        "测试范围和策略",
        "测试环境",
        "测试用例和执行摘要",
        "测试结果摘要",
        "缺陷和异常",
        "覆盖情况和限制",
        "结论候选",
        "开放问题和必需确认",
        "审查摘要",
    ),
    required_sections=(
        "scope",
        "test object",
        "test environment",
        "test cases",
        "test results",
        "defects",
        "coverage",
        "limitations",
        "open issues",
    ),
    optional_sections=(
        "test strategy",
        "input materials",
        "conclusion candidate",
        "review summary",
    ),
    critical_claims=TEST_REPORT_CRITICAL_CLAIMS,
    requires_human_confirmation=(
        "final pass/fail conclusion",
        "release readiness or acceptance recommendation",
        "defect severity acceptance",
        "coverage sufficiency conclusion",
        "unresolved issue acceptance",
        "test sufficiency conclusion",
    ),
    forbidden_final_claims=(
        "all tests passed",
        "no defects exist",
        "system is production ready",
        "release is approved",
        "quality is guaranteed",
        "coverage is complete",
        "test conclusion is approved",
        "ready for production without risk",
    ),
    confirmation_marker="NEEDS_USER_CONFIRMATION",
    fact_source_roles=("source",),
    non_fact_source_roles=(
        "sample",
        "template",
        "checklist",
        "reference",
        "expected_output_shape",
    ),
    reference_policy=(
        "Reference materials may support testing methodology or report structure but must not prove project-specific "
        "test results, pass/fail status, defect state, coverage, or release readiness."
    ),
    sample_policy=(
        "Sample test reports may guide structure and style but must not supply project-specific test results, metrics, "
        "defects, pass/fail status, or final conclusions."
    ),
    default_final_status="ready_for_human_review",
    allowed_final_statuses=(
        "ready_for_human_review",
        "finalized_with_open_items",
        "blocked_pending_confirmation",
    ),
    review_focus=(
        "template completeness",
        "test scope and requirements coverage",
        "test result evidence alignment",
        "unsupported pass/fail or coverage claims",
        "unsupported defect severity or status claims",
        "sample misuse",
        "reference misuse as project fact",
        "unresolved issues and limitations",
        "unconfirmed final test conclusion",
    ),
    verification_focus=(
        "required artifacts",
        "citation integrity",
        "sample not fact source",
        "reference not project fact source",
        "critical claims confirmation",
        "test result claims require evidence or HITL",
        "pass/fail conclusion requires evidence or HITL",
        "candidate update inactive",
        "document type terminology isolation",
    ),
    candidate_learning_policy="Generate candidate updates only; keep proposed/inactive unless explicitly approved.",
    terminology={
        "sensitive_title_markers": (
            "test object|test scope|test environment|test case|test result|execution|pass/fail|defect|coverage|"
            "limitation|conclusion|release readiness|acceptance|open issue|unresolved issue|sufficiency|"
            "测试对象|测试范围|测试环境|测试用例|测试结果|执行|通过|失败|缺陷|覆盖|限制|结论|发布就绪|接受|开放问题|未解决问题|充分性"
        ),
        "rating_title_markers": "",
        "rating_placeholder": "test result / defect / coverage status pending",
        "professional_judgment": "critical test report claim",
        "professional_judgments": "critical test report claims",
        "critical_claims_label": "Critical test report claims",
        "critical_judgment_label": "critical test report claims",
        "confirmation_heading": "测试报告开放确认项",
        "final_package_title": "测试报告最终交付包",
    },
    output_labels={
        "draft_title": "测试报告保守草稿",
        "final_report_title": "测试报告最终交付包",
        "confirmation_section": "NEEDS_USER_CONFIRMATION",
        "boundary_note_heading": "核心证据边界",
        "open_items_heading": "测试报告开放确认项",
        "critical_claims_label": "Critical test report claims",
        "no_forbidden_final_claim_detail": "No forbidden final test conclusion phrase was found.",
        "confirmation_marker_detail": "Critical test report claims keep NEEDS_USER_CONFIRMATION markers.",
    },
)
