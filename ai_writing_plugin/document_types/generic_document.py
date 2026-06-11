from __future__ import annotations

from .base import DocumentTypeRules


GENERIC_DOCUMENT_CRITICAL_CLAIMS = (
    "final decision recommendation",
    "approval or acceptance conclusion",
    "compliance conclusion",
    "release readiness conclusion",
    "risk acceptance conclusion",
    "cost or schedule commitment",
    "security or safety claim",
)


GENERIC_DOCUMENT_RULES = DocumentTypeRules(
    task_type="generic_document",
    display_name="Generic Document",
    description="General-purpose evidence-aware document writing mode for conservative technical-preview memos.",
    default_sections=(
        "背景和范围",
        "已确认来源事实",
        "建议方案",
        "风险和开放问题",
        "决策和人工确认",
        "审查摘要",
    ),
    required_sections=(
        "background",
        "scope",
        "confirmed facts",
        "proposed approach",
        "risks",
        "open questions",
        "confirmations",
    ),
    optional_sections=(
        "review summary",
        "decision context",
        "limitations",
    ),
    critical_claims=GENERIC_DOCUMENT_CRITICAL_CLAIMS,
    requires_human_confirmation=GENERIC_DOCUMENT_CRITICAL_CLAIMS,
    forbidden_final_claims=(
        "is approved",
        "is accepted",
        "is validated",
        "is compliant",
        "risk is accepted",
        "production ready",
        "release approved",
        "final cost is fixed",
        "schedule is guaranteed",
        "no unresolved risk",
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
        "Reference materials may support structure, style, or general methodology but must not prove project-specific "
        "facts, decisions, approvals, costs, schedules, compliance status, readiness, or risk acceptance."
    ),
    sample_policy=(
        "Sample documents may guide structure and style but must not supply project-specific facts, decisions, "
        "approvals, costs, schedules, compliance status, readiness, or risk acceptance."
    ),
    default_final_status="ready_for_human_review",
    allowed_final_statuses=(
        "ready_for_human_review",
        "finalized_with_open_items",
        "blocked_pending_confirmation",
    ),
    review_focus=(
        "template completeness",
        "checklist coverage",
        "confirmed source fact separation",
        "unsupported decision or approval claims",
        "unsupported cost or schedule claims",
        "unsupported compliance or readiness claims",
        "sample misuse",
        "reference misuse as project fact",
        "unresolved risks and open questions",
    ),
    verification_focus=(
        "required artifacts",
        "citation integrity",
        "sample not fact source",
        "reference not project fact source",
        "critical claims confirmation",
        "document type terminology isolation",
        "candidate update inactive",
    ),
    candidate_learning_policy="Generate candidate updates only; keep proposed/inactive unless explicitly approved.",
    terminology={
        "sensitive_title_markers": (
            "decision|approval|acceptance|compliance|readiness|risk|cost|schedule|security|confirmation|open question|"
            "决策|批准|接受|合规|就绪|风险|成本|排期|安全|确认|开放问题"
        ),
        "rating_title_markers": "",
        "rating_placeholder": "claim status pending",
        "professional_judgment": "generic document critical claim",
        "professional_judgments": "generic document critical claims",
        "critical_claims_label": "generic document critical claims",
        "critical_judgment_label": "generic document critical claims",
        "confirmation_heading": "通用文档开放确认项",
        "final_package_title": "通用文档最终交付包",
    },
    output_labels={
        "draft_title": "通用文档保守草稿",
        "final_report_title": "通用文档最终交付包",
        "confirmation_section": "NEEDS_USER_CONFIRMATION",
        "boundary_note_heading": "核心证据边界",
        "open_items_heading": "通用文档开放确认项",
        "critical_claims_label": "Generic document critical claims",
        "no_forbidden_final_claim_detail": "No forbidden final generic document phrase was found.",
        "confirmation_marker_detail": "Generic document critical claims keep NEEDS_USER_CONFIRMATION markers.",
    },
)
