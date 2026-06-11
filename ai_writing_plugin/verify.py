from __future__ import annotations

from typing import Any

from .document_types.base import DocumentTypeRules
from .document_types.context import get_rules_for_task_type


REQUIRED_CHECKS = [
    ("CHK-001", "required_phase5_artifacts_exist", "P0"),
    ("CHK-002", "full_draft_exists", "P0"),
    ("CHK-003", "section_drafts_match_section_tasks", "P1"),
    ("CHK-004", "template_sections_present_in_full_draft", "P1"),
    ("CHK-005", "draft_sections_are_in_task_order", "P2"),
    ("CHK-006", "citation_ids_parseable", "P0"),
    ("CHK-007", "citation_ids_exist_in_citation_plan", "P0"),
    ("CHK-008", "citation_ids_allowed_by_section_task", "P0"),
    ("CHK-009", "cited_sources_exist_in_source_index", "P0"),
    ("CHK-010", "source_support_sections_present", "P1"),
    ("CHK-011", "sample_not_used_as_fact_source", "P0"),
    ("CHK-012", "expected_output_shape_not_used_as_fact_source", "P0"),
    ("CHK-013", "reference_not_used_as_project_fact", "P1"),
    ("CHK-014", "hara_sensitive_sections_keep_confirmation_markers", "P0"),
    ("CHK-015", "final_hara_conclusion_phrases_absent", "P0"),
    ("CHK-016", "unresolved_questions_carried_forward", "P1"),
    ("CHK-017", "knowledge_gaps_carried_forward", "P1"),
    ("CHK-018", "review_artifacts_exist", "P1"),
    ("CHK-019", "no_later_phase_artifacts_generated", "P0"),
    ("CHK-020", "manifest_updated_to_phase_6", "Info"),
    ("CHK-021", "provenance_index_exists", "P1"),
    ("CHK-022", "source_tier_policy_valid", "P0"),
    ("CHK-023", "sample_tier_is_style_only", "P0"),
    ("CHK-024", "reference_tier_is_methodology_only", "P0"),
    ("CHK-025", "critical_claim_source_tier_sufficient", "P0"),
    ("CHK-026", "required_human_confirmation_not_hidden", "P0"),
    ("CHK-027", "final_report_has_provenance_summary", "P1"),
    ("CHK-028", "final_delivery_has_open_confirmations", "P1"),
    ("CHK-029", "profile_version_recorded_when_available", "P1"),
]


def build_verify_report(
    run_id: str,
    generated_at: str,
    facts: dict[str, dict[str, Any]],
    review_items: list[dict[str, Any]],
    final_readiness: str,
    rules: DocumentTypeRules | None = None,
) -> dict[str, Any]:
    rules = rules or get_rules_for_task_type(None)
    checks = [build_check(check_id, name, severity, facts.get(name, {})) for check_id, name, severity in REQUIRED_CHECKS]
    p0_items = [item for item in review_items if item["severity"] == "P0"]
    p1_items = [item for item in review_items if item["severity"] == "P1"]
    blocking_items = [item for item in review_items if item["blocks_final"]]

    failed_checks = [check for check in checks if check["status"] == "failed"]
    blocked_checks = [check for check in checks if check["status"] == "blocked"]
    warning_checks = [check for check in checks if check["status"] == "warning"]

    if failed_checks:
        status = "failed"
    elif blocked_checks or blocking_items:
        status = "blocked"
    elif warning_checks or any(item["severity"] in {"P2", "Info"} for item in review_items):
        status = "passed_with_warnings"
    else:
        status = "passed"

    return {
        "run_id": run_id,
        "generated_at": generated_at,
        "document_type": {
            "task_type": rules.task_type,
            "display_name": rules.display_name,
            "verification_focus": list(rules.verification_focus),
            "critical_claims": list(rules.critical_claims),
            "requires_human_confirmation": list(rules.requires_human_confirmation),
            "forbidden_final_claims": list(rules.forbidden_final_claims),
            "allowed_final_statuses": list(rules.allowed_final_statuses),
            "default_final_status": rules.default_final_status,
            "confirmation_marker": rules.confirmation_marker,
            "sample_policy": rules.sample_policy,
            "reference_policy": rules.reference_policy,
            "candidate_learning_policy": rules.candidate_learning_policy,
        },
        "status": status,
        "summary": {
            "passed": sum(1 for check in checks if check["status"] == "passed"),
            "failed": len(failed_checks),
            "blocked": len(blocked_checks),
            "warnings": len(warning_checks),
            "total_checks": len(checks),
            "p0_review_items": len(p0_items),
            "p1_review_items": len(p1_items),
            "blocking_review_items": len(blocking_items),
            "final_readiness": final_readiness,
        },
        "checks": checks,
        "blocking_failures": build_blocking_failures(failed_checks, blocked_checks, blocking_items),
        "warnings": [check["details"] for check in warning_checks],
    }


def build_check(check_id: str, name: str, severity: str, fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "name": name,
        "status": fact.get("status", "passed"),
        "severity": severity,
        "details": fact.get("details", f"{name} passed."),
        "related_artifacts": fact.get("related_artifacts", []),
        "review_item_ids": fact.get("review_item_ids", []),
    }


def build_blocking_failures(
    failed_checks: list[dict[str, Any]],
    blocked_checks: list[dict[str, Any]],
    blocking_items: list[dict[str, Any]],
) -> list[str]:
    failures: list[str] = []
    for check in [*failed_checks, *blocked_checks]:
        failures.append(f"{check['check_id']} {check['name']}: {check['details']}")
    for item in blocking_items:
        evidence = ", ".join(item["evidence_ids"]) if item["evidence_ids"] else "no evidence id"
        failures.append(f"{item['review_id']} {item['severity']} {item['category']}: {item['description']} ({evidence})")
    return dedupe(failures)


def render_failures_md(
    run_id: str,
    verify_report: dict[str, Any],
    review_items: list[dict[str, Any]],
    rules: DocumentTypeRules | None = None,
) -> str:
    rules = rules or get_rules_for_task_type(None)
    failed_checks = [check for check in verify_report["checks"] if check["status"] == "failed"]
    blocked_checks = [check for check in verify_report["checks"] if check["status"] == "blocked"]
    warning_checks = [check for check in verify_report["checks"] if check["status"] == "warning"]
    confirmation_blockers = [
        item for item in review_items if item["category"] == confirmation_category(rules) and item["blocks_final"]
    ]

    lines = [
        "# 验证失败项",
        "",
        f"Run id: {run_id}",
        "",
        "## 摘要",
        "",
        f"- 验证状态：{verify_report['status']}",
        f"- 失败检查数：{len(failed_checks)}",
        f"- 阻塞检查数：{len(blocked_checks)}",
        f"- Warnings: {len(warning_checks)}",
        "",
        "## 阻塞失败项",
        "",
    ]

    mechanical_failures = [item for item in review_items if item["severity"] == "P0"]
    if not failed_checks and not blocked_checks and not mechanical_failures:
        lines.append("未发现 mechanical verification failure。")
        if confirmation_blockers:
            lines.append(f"最终交付仍被阻塞，因为 {rules.display_name} human confirmations 仍保持 pending。")
    else:
        for check in failed_checks:
            lines.append(f"- {check['check_id']} {check['name']}: {check['details']}")
        for check in blocked_checks:
            lines.append(f"- {check['check_id']} {check['name']}: {check['details']}")
        for item in mechanical_failures:
            evidence = ", ".join(item["evidence_ids"]) if item["evidence_ids"] else "no evidence id"
            lines.append(f"- {item['review_id']} {item['category']}: {item['description']} ({evidence})")

    lines.extend(["", "## 非阻塞 warnings", ""])
    if warning_checks:
        for check in warning_checks:
            lines.append(f"- {check['check_id']} {check['name']}: {check['details']}")
    else:
        lines.append("未发现 non-blocking warning checks。")

    lines.extend(["", "## 人工确认阻塞项", ""])
    if confirmation_blockers:
        for item in confirmation_blockers:
            lines.append(f"- {item['review_id']} | {item['task_id']} | {item['description']}")
    else:
        lines.append("未发现 required human confirmation blockers。")

    lines.extend(
        [
            "",
            "## Phase 7 建议",
            "",
            "- 将所有 P0/P1 review items 转成 Phase 7 revision 或 confirmation tasks。",
            f"- 除非记录 user confirmation，否则对 {professional_judgment_label(rules, plural=True)} 保留 {rules.confirmation_marker}。",
            "- 如果 unresolved questions 仍开放，则在最终交付中保留。",
            "",
            "## 阶段边界说明",
            "",
            "Phase 6 只报告 failures 和 blockers。",
            "修订推迟到 Phase 7。",
            "最终交付推迟到 Phase 7。",
            "",
        ]
    )
    return "\n".join(lines)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def confirmation_category(rules: DocumentTypeRules) -> str:
    if rules.task_type == "hara":
        return "hara_confirmation_required"
    return "critical_claim_confirmation_required"


def professional_judgment_label(rules: DocumentTypeRules, plural: bool = False) -> str:
    key = "professional_judgments" if plural else "professional_judgment"
    fallback = "professional judgments" if plural else "professional judgment"
    return rules.terminology.get(key, fallback)
