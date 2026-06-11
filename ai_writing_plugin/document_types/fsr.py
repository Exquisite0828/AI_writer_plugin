from __future__ import annotations

from .base import DocumentTypeRules


FSR_CRITICAL_CLAIMS = (
    "functional safety requirement wording",
    "safety goal linkage",
    "ASIL inheritance",
    "safe state linkage",
    "verification method",
    "requirement completeness",
    "requirement sufficiency",
    "final FSR approval",
    "final compliance conclusion",
)


FSR_RULES = DocumentTypeRules(
    task_type="fsr",
    display_name="FSR 功能安全需求文档",
    description=(
        "Functional Safety Requirements document writing task for traceable, evidence-aware FSR packages. "
        "This built-in L3 type drafts review material and does not approve requirements."
    ),
    default_sections=(
        "文档目的和范围",
        "输入材料和假设",
        "Item definition 摘要",
        "安全目标追溯",
        "功能安全需求表",
        "ASIL 继承和理由",
        "验证方法候选",
        "假设、限制和开放确认",
        "审查摘要",
        "最终审查边界",
    ),
    required_sections=(
        "scope",
        "input materials",
        "item definition",
        "safety goals",
        "functional safety requirements",
        "ASIL inheritance",
        "verification",
        "limitations",
        "open confirmations",
    ),
    optional_sections=(
        "assumptions",
        "rationale",
        "traceability",
        "review summary",
    ),
    critical_claims=FSR_CRITICAL_CLAIMS,
    requires_human_confirmation=(
        "functional safety requirement wording",
        "safety goal linkage",
        "ASIL inheritance",
        "verification method adequacy",
        "requirement completeness and sufficiency conclusion",
        "final FSR approval or compliance conclusion",
    ),
    forbidden_final_claims=(
        "FSR set is approved",
        "functional safety requirements are approved",
        "requirements are complete and compliant",
        "safety goals are fully satisfied",
        "ASIL inheritance is validated",
        "verification method is sufficient",
        "no open safety issue remains",
        "ready for production release",
        "risk is accepted",
        "compliance is confirmed",
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
        "Reference materials may support functional-safety requirement writing methodology, but must not prove "
        "project-specific safety goals, ASIL values, requirement wording, verification status, completeness, "
        "compliance, or approval."
    ),
    sample_policy=(
        "Sample FSR documents may guide structure, style, section granularity, and table shape, but must not supply "
        "project-specific requirement content, safety goal linkage, ASIL inheritance, verification status, "
        "completeness, compliance, or approval."
    ),
    default_final_status="ready_for_human_review",
    allowed_final_statuses=(
        "ready_for_human_review",
        "finalized_with_open_items",
        "blocked_pending_confirmation",
    ),
    review_focus=(
        "template completeness",
        "safety goal traceability",
        "unsupported functional safety requirement wording",
        "unsupported ASIL inheritance",
        "unsupported verification method claims",
        "sample misuse",
        "reference misuse as project fact",
        "TSC scope leakage",
        "unconfirmed completeness or compliance conclusion",
    ),
    verification_focus=(
        "required artifacts",
        "citation integrity",
        "source tier and provenance",
        "sample not fact source",
        "reference not project fact source",
        "critical claims confirmation",
        "functional safety requirement claims require source or HITL",
        "candidate update inactive",
        "TSC deferred and not emitted",
    ),
    candidate_learning_policy="Generate candidate updates only; keep proposed/inactive unless explicitly approved.",
    terminology={
        "sensitive_title_markers": (
            "functional safety requirement|fsr|safety goal|asil|safe state|verification|validation|"
            "traceability|completeness|sufficiency|compliance|approval|"
            "功能安全需求|安全目标|安全状态|验证|确认|追溯|完整性|充分性|合规|批准"
        ),
        "rating_title_markers": "asil|safety goal|safe state|verification|compliance|approval|安全目标|安全状态|验证|合规|批准",
        "rating_placeholder": "FSR / safety goal / ASIL / verification status pending",
        "professional_judgment": "critical FSR claim",
        "professional_judgments": "critical FSR claims",
        "critical_claims_label": "FSR critical claims",
        "critical_judgment_label": "critical FSR claims",
        "confirmation_heading": "FSR 开放确认项",
        "final_package_title": "FSR 功能安全需求文档最终交付包",
    },
    output_labels={
        "draft_title": "FSR 功能安全需求文档保守草稿",
        "final_report_title": "FSR 功能安全需求文档最终交付包",
        "confirmation_section": "NEEDS_USER_CONFIRMATION",
        "boundary_note_heading": "FSR 核心证据边界",
        "open_items_heading": "FSR 开放确认项",
        "critical_claims_label": "FSR critical claims",
        "no_forbidden_final_claim_detail": "No forbidden final FSR approval phrase was found.",
        "confirmation_marker_detail": "Critical FSR claims keep NEEDS_USER_CONFIRMATION markers.",
    },
)
