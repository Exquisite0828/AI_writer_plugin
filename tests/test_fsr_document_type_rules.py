from __future__ import annotations

from pathlib import Path

import pytest

from ai_writing_plugin.document_types import get_document_type_rules, supported_document_types


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_fsr_is_registered_as_official_l3_document_type() -> None:
    rules = get_document_type_rules("fsr")

    assert rules.task_type == "fsr"
    assert "fsr" in supported_document_types()
    assert "Functional Safety Requirements" in rules.description
    assert "功能安全需求" in rules.display_name


def test_fsr_lookup_is_case_insensitive_without_affecting_existing_types() -> None:
    assert get_document_type_rules("FSR").task_type == "fsr"
    assert get_document_type_rules(" hara ").task_type == "hara"
    assert get_document_type_rules("technical_solution").task_type == "technical_solution"
    assert get_document_type_rules("test_report").task_type == "test_report"
    assert get_document_type_rules("generic_document").task_type == "generic_document"


def test_fsr_rules_define_safety_requirement_boundaries() -> None:
    rules = get_document_type_rules("fsr")
    critical_claims = " ".join(rules.critical_claims).lower()
    confirmations = " ".join(rules.requires_human_confirmation).lower()

    for required in [
        "functional safety requirement",
        "safety goal linkage",
        "asil inheritance",
        "verification method",
        "requirement completeness",
        "final fsr approval",
    ]:
        assert required in critical_claims or required in confirmations

    assert "safety goals" in " ".join(rules.required_sections).lower()
    assert "functional safety requirements" in " ".join(rules.required_sections).lower()
    assert "verification" in " ".join(rules.required_sections).lower()


def test_fsr_rules_keep_sources_samples_references_and_final_status_safe() -> None:
    rules = get_document_type_rules("fsr")

    assert rules.fact_source_roles == ("source",)
    assert "sample" in rules.non_fact_source_roles
    assert "reference" in rules.non_fact_source_roles
    assert "must not prove project-specific" in rules.reference_policy.lower()
    assert "must not supply project-specific" in rules.sample_policy.lower()
    assert rules.confirmation_marker == "NEEDS_USER_CONFIRMATION"
    assert rules.default_final_status in rules.allowed_final_statuses
    assert "approved" not in rules.allowed_final_statuses
    assert "compliant" not in rules.allowed_final_statuses
    assert "validated" not in rules.allowed_final_statuses


def test_fsr_does_not_create_profile_or_tsc_artifacts() -> None:
    forbidden_paths = [
        REPO_ROOT / "profiles" / "document_types" / "fsr.yaml",
        REPO_ROOT / "ai_writing_plugin" / "document_types" / "tsc.py",
        REPO_ROOT / "profiles" / "document_types" / "tsc.yaml",
        REPO_ROOT / "skills" / "document-types" / "tsc" / "SKILL.md",
        REPO_ROOT / "examples" / "tsc_demo_fixture",
        REPO_ROOT / "ai_writing_plugin" / "fsr_pipeline.py",
        REPO_ROOT / "ai_writing_plugin" / "tsc_pipeline.py",
    ]

    for path in forbidden_paths:
        assert not path.exists(), path


def test_unknown_document_type_still_reports_supported_types() -> None:
    with pytest.raises(ValueError, match="fsr"):
        get_document_type_rules("technical_safety_concept")
