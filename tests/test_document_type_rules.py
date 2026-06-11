import dataclasses

import pytest

from ai_writing_plugin.document_types import (
    HARA_RULES,
    DocumentTypeRules,
    get_document_type_rules,
    supported_document_types,
)


REQUIRED_HARA_CLAIMS = {
    "hazard identification",
    "hazardous event",
    "severity rating",
    "exposure rating",
    "controllability rating",
    "ASIL or risk level",
    "safety goal",
    "final acceptability conclusion",
}

REQUIRED_TECHNICAL_SOLUTION_CLAIMS = {
    "architecture decision",
    "performance target",
    "security boundary",
    "cost estimate",
    "rollout risk acceptance",
}

REQUIRED_TEST_REPORT_CLAIMS = {
    "test object and version",
    "test scope coverage",
    "test environment",
    "test case execution status",
    "pass/fail result",
    "defect severity or status",
    "coverage percentage or sufficiency",
    "final test conclusion",
    "release readiness or acceptance recommendation",
}


def test_registry_returns_hara_rules_for_current_compatible_inputs() -> None:
    assert get_document_type_rules("hara") is HARA_RULES
    assert get_document_type_rules("HARA") is HARA_RULES
    assert get_document_type_rules(None) is HARA_RULES
    assert get_document_type_rules("") is HARA_RULES


def test_registry_rejects_unknown_document_type() -> None:
    with pytest.raises(ValueError, match="Unsupported document type"):
        get_document_type_rules("unknown")


def test_supported_document_types_contains_hara_without_blocking_future_types() -> None:
    assert "hara" in supported_document_types()


def test_technical_solution_rules_are_registered_without_blocking_future_types() -> None:
    rules = get_document_type_rules("technical_solution")
    upper_rules = get_document_type_rules("TECHNICAL_SOLUTION")

    assert rules is upper_rules
    assert rules.task_type == "technical_solution"
    assert rules.display_name
    assert "technical_solution" in supported_document_types()
    assert "hara" in supported_document_types()
    assert {"背景", "目标和非目标", "需求", "架构概览", "风险和权衡", "开放问题"} <= set(
        rules.default_sections
    )
    assert REQUIRED_TECHNICAL_SOLUTION_CLAIMS <= set(rules.critical_claims)
    assert {
        "final architecture decision",
        "performance target",
        "security boundary",
        "cost estimate",
        "rollout risk acceptance",
    } <= set(rules.requires_human_confirmation)
    assert {
        "architecture is approved",
        "no security risk exists",
        "performance target is guaranteed",
        "cost is final",
        "rollout is risk-free",
    } <= set(rules.forbidden_final_claims)
    assert rules.confirmation_marker == "NEEDS_USER_CONFIRMATION"
    assert rules.default_final_status == "ready_for_human_review"
    assert {"ready_for_human_review", "finalized_with_open_items", "blocked_pending_confirmation"} <= set(
        rules.allowed_final_statuses
    )
    assert "sample" in rules.sample_policy.lower()
    assert "project facts" in rules.sample_policy.lower()
    assert "reference" in rules.reference_policy.lower()
    assert "must not prove project-specific" in rules.reference_policy.lower()


def test_test_report_rules_are_registered_without_blocking_future_types() -> None:
    rules = get_document_type_rules("test_report")
    upper_rules = get_document_type_rules("TEST_REPORT")

    assert rules is upper_rules
    assert rules.task_type == "test_report"
    assert rules.display_name == "测试报告"
    for task_type in ["hara", "technical_solution", "test_report"]:
        assert task_type in supported_document_types()
    assert {
        "文档目的和范围",
        "测试对象和版本",
        "测试环境",
        "测试用例和执行摘要",
        "测试结果摘要",
        "缺陷和异常",
        "覆盖情况和限制",
        "结论候选",
        "开放问题和必需确认",
    } <= set(rules.default_sections)
    assert REQUIRED_TEST_REPORT_CLAIMS <= set(rules.critical_claims)
    assert {
        "final pass/fail conclusion",
        "release readiness or acceptance recommendation",
        "defect severity acceptance",
        "coverage sufficiency conclusion",
        "unresolved issue acceptance",
        "test sufficiency conclusion",
    } <= set(rules.requires_human_confirmation)
    assert {
        "all tests passed",
        "release is approved",
        "no defects exist",
        "coverage is complete",
        "system is production ready",
    } <= set(rules.forbidden_final_claims)
    assert rules.confirmation_marker == "NEEDS_USER_CONFIRMATION"
    assert rules.default_final_status == "ready_for_human_review"
    assert {"ready_for_human_review", "finalized_with_open_items", "blocked_pending_confirmation"} <= set(
        rules.allowed_final_statuses
    )
    assert "approved" not in rules.allowed_final_statuses
    assert rules.fact_source_roles == ("source",)
    assert {"sample", "template", "checklist", "reference"} <= set(rules.non_fact_source_roles)
    assert "sample test reports" in rules.sample_policy.lower()
    assert "must not supply project-specific test results" in rules.sample_policy.lower()
    assert "reference" in rules.reference_policy.lower()
    assert "must not prove project-specific test results" in rules.reference_policy.lower()
    assert "proposed" in rules.candidate_learning_policy.lower()
    assert "inactive" in rules.candidate_learning_policy.lower()


def test_hara_rules_cover_critical_claims_and_confirmation_policy() -> None:
    assert HARA_RULES.task_type == "hara"
    assert "HARA" in HARA_RULES.display_name
    assert HARA_RULES.confirmation_marker == "NEEDS_USER_CONFIRMATION"
    assert REQUIRED_HARA_CLAIMS <= set(HARA_RULES.critical_claims)
    assert REQUIRED_HARA_CLAIMS <= set(HARA_RULES.requires_human_confirmation)


def test_hara_rules_cover_final_status_and_forbidden_claim_policy() -> None:
    forbidden_claims = set(HARA_RULES.forbidden_final_claims)
    assert "final ASIL is approved" in forbidden_claims
    assert "risk is acceptable" in forbidden_claims
    assert "safety goal is approved" in forbidden_claims
    assert HARA_RULES.default_final_status == "finalized_with_open_items"
    assert "finalized_with_open_items" in HARA_RULES.allowed_final_statuses
    assert "blocked_pending_confirmation" in HARA_RULES.allowed_final_statuses
    assert "ready_for_human_review" in HARA_RULES.allowed_final_statuses
    assert "approved" not in HARA_RULES.allowed_final_statuses


def test_hara_rules_preserve_source_boundaries() -> None:
    assert HARA_RULES.fact_source_roles == ("source",)
    assert "sample" in HARA_RULES.non_fact_source_roles
    assert "template" in HARA_RULES.non_fact_source_roles
    assert "sample" in HARA_RULES.sample_policy.lower()
    assert "fact source" in HARA_RULES.sample_policy.lower()
    assert "reference" in HARA_RULES.reference_policy.lower()
    assert "must not prove project-specific facts" in HARA_RULES.reference_policy.lower()


def test_hara_rules_preserve_candidate_learning_boundary() -> None:
    policy = HARA_RULES.candidate_learning_policy.lower()
    assert "candidate updates only" in policy
    assert "proposed" in policy
    assert "inactive" in policy
    assert "explicitly approved" in policy


def test_document_type_rules_are_frozen() -> None:
    assert dataclasses.is_dataclass(DocumentTypeRules)
    assert DocumentTypeRules.__dataclass_params__.frozen is True
    with pytest.raises(dataclasses.FrozenInstanceError):
        HARA_RULES.task_type = "other"  # type: ignore[misc]
