from __future__ import annotations

from .base import DocumentTypeRules


TECHNICAL_SOLUTION_CRITICAL_CLAIMS = (
    "architecture decision",
    "performance target",
    "security boundary",
    "deployment risk",
    "cost estimate",
    "compatibility constraint",
    "rollout risk acceptance",
)


TECHNICAL_SOLUTION_RULES = DocumentTypeRules(
    task_type="technical_solution",
    display_name="技术方案文档",
    description="面向后端、架构或技术评审场景的技术方案写作任务。",
    default_sections=(
        "背景",
        "目标和非目标",
        "需求",
        "架构概览",
        "数据流和接口",
        "实施计划",
        "风险和权衡",
        "上线计划",
        "开放问题",
    ),
    required_sections=(
        "background",
        "goals",
        "requirements",
        "architecture",
        "risks",
        "open issues",
    ),
    optional_sections=(
        "data flow",
        "interfaces",
        "implementation plan",
        "rollout plan",
    ),
    critical_claims=TECHNICAL_SOLUTION_CRITICAL_CLAIMS,
    requires_human_confirmation=(
        "final architecture decision",
        "performance target",
        "security boundary",
        "cost estimate",
        "rollout risk acceptance",
    ),
    forbidden_final_claims=(
        "architecture is approved",
        "no security risk exists",
        "performance target is guaranteed",
        "cost is final",
        "rollout is risk-free",
        "production ready",
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
        "Reference materials may support general technical rationale but must not prove project-specific requirements, "
        "constraints, decisions, performance targets, costs, or risk acceptance."
    ),
    sample_policy="Sample solution documents may guide structure and style but must not supply project facts.",
    default_final_status="ready_for_human_review",
    allowed_final_statuses=(
        "ready_for_human_review",
        "finalized_with_open_items",
        "blocked_pending_confirmation",
    ),
    review_focus=(
        "template completeness",
        "requirements coverage",
        "unsupported architecture decisions",
        "unsupported performance or cost claims",
        "unsupported security boundary claims",
        "sample misuse",
        "reference misuse as project fact",
        "unresolved risks and trade-offs",
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
        "sensitive_title_markers": "architecture|performance|security|deployment|cost|compatibility|rollout|risk|架构|性能|安全|部署|成本|兼容|上线|风险",
        "rating_title_markers": "",
        "rating_placeholder": "decision / target / boundary status pending",
        "professional_judgment": "critical technical claim",
        "professional_judgments": "critical technical claims",
        "critical_claims_label": "technical solution critical claims",
        "critical_judgment_label": "critical technical claims",
        "confirmation_heading": "技术方案开放确认项",
        "final_package_title": "技术方案文档最终交付包",
    },
    output_labels={
        "draft_title": "技术方案文档保守草稿",
        "final_report_title": "技术方案文档最终交付包",
        "confirmation_section": "NEEDS_USER_CONFIRMATION",
        "boundary_note_heading": "核心证据边界",
        "open_items_heading": "技术方案开放确认项",
    },
)
