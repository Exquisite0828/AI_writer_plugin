from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.document_types import get_document_type_rules


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERIC_PROFILE = "profiles/document_types/generic_document.yaml"
CUSTOM_PROFILE = "profiles/document_types/customer_demo/custom_technical_note.yaml"


def test_valid_document_profile_loads() -> None:
    from ai_writing_plugin.document_types.profile_loader import load_document_profile

    loaded = load_document_profile(CUSTOM_PROFILE, expected_task_type="custom_technical_note")

    assert loaded.profile.profile_id == "customer_demo.custom_technical_note"
    assert loaded.profile.profile_version == "0.1.0"
    assert loaded.profile.task_type == "custom_technical_note"
    assert loaded.profile_path == CUSTOM_PROFILE


def test_document_profile_converts_to_rules() -> None:
    from ai_writing_plugin.document_types.profile_loader import load_document_profile

    loaded = load_document_profile(CUSTOM_PROFILE, expected_task_type="custom_technical_note")
    rules = loaded.to_rules()

    assert rules.task_type == "custom_technical_note"
    assert rules.display_name == "Custom Technical Note"
    assert "deployment risk" in rules.critical_claims
    assert "compatibility claim" in rules.requires_human_confirmation
    assert "sample not fact source" in rules.verification_focus
    assert rules.default_final_status == "ready_for_human_review"
    assert "Sample documents may guide structure" in rules.sample_policy


def test_generic_document_profile_loads_as_external_mirror() -> None:
    from ai_writing_plugin.document_types.profile_loader import load_document_profile

    loaded = load_document_profile(GENERIC_PROFILE, expected_task_type="generic_document")
    rules = loaded.to_rules()
    built_in = get_document_type_rules("generic_document")

    assert loaded.profile.profile_id == "built_in_mirror.generic_document"
    assert rules.task_type == built_in.task_type
    assert rules.display_name == built_in.display_name
    assert set(built_in.critical_claims) <= set(rules.critical_claims)


def test_document_profile_rejects_missing_required_fields(tmp_path: Path) -> None:
    from ai_writing_plugin.document_types.profile_loader import DocumentProfileValidationError, load_document_profile_file

    profile_path = tmp_path / "missing_required.yaml"
    profile_path.write_text(
        yaml.safe_dump(
            {
                "profile_id": "test.missing",
                "profile_version": "0.1.0",
                "task_type": "custom_technical_note",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(DocumentProfileValidationError) as exc_info:
        load_document_profile_file(profile_path, profile_path="tests/generated/missing_required.yaml")

    assert "critical_claims" in "\n".join(exc_info.value.errors)


def test_document_profile_rejects_sample_as_fact_source() -> None:
    from ai_writing_plugin.document_types.profile_loader import DocumentProfileValidationError, load_document_profile

    with pytest.raises(DocumentProfileValidationError) as exc_info:
        load_document_profile("tests/fixtures/document_profiles/invalid_sample_fact_source.yaml")

    message = "\n".join(exc_info.value.errors)
    assert "fact_source_roles" in message
    assert "sample" in message


def test_document_profile_rejects_invalid_final_status(tmp_path: Path) -> None:
    from ai_writing_plugin.document_types.profile_loader import DocumentProfileValidationError, load_document_profile_file

    profile = yaml.safe_load((REPO_ROOT / CUSTOM_PROFILE).read_text(encoding="utf-8"))
    profile["default_final_status"] = "approved"
    profile_path = tmp_path / "invalid_status.yaml"
    profile_path.write_text(yaml.safe_dump(profile), encoding="utf-8")

    with pytest.raises(DocumentProfileValidationError) as exc_info:
        load_document_profile_file(profile_path, profile_path="tests/generated/invalid_status.yaml")

    assert "default_final_status" in "\n".join(exc_info.value.errors)


def test_document_profile_rejects_task_type_mismatch() -> None:
    from ai_writing_plugin.document_types.profile_loader import DocumentProfileValidationError, load_document_profile

    with pytest.raises(DocumentProfileValidationError) as exc_info:
        load_document_profile(CUSTOM_PROFILE, expected_task_type="another_type")

    assert "task_type mismatch" in "\n".join(exc_info.value.errors)


def test_document_profile_rejects_unsafe_profile_path() -> None:
    from ai_writing_plugin.document_types.profile_loader import DocumentProfileValidationError, load_document_profile

    with pytest.raises(DocumentProfileValidationError):
        load_document_profile("../profiles/document_types/customer_demo/custom_technical_note.yaml")

    with pytest.raises(DocumentProfileValidationError):
        load_document_profile("/tmp/custom_technical_note.yaml")


def test_unknown_task_type_requires_profile_path(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import WriteRunError, write_run

    task_path = tmp_path / "task.yaml"
    task_path.write_text(
        """\
task_type: unknown_customer_type
task_title: Unknown type without external profile
target_audience: reviewer
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - final decision
""",
        encoding="utf-8",
    )

    with pytest.raises(WriteRunError) as exc_info:
        write_run(task_path, tmp_path / "runs")

    message = str(exc_info.value)
    assert "Unsupported document type" in message
    assert "document_profile_path" in message


def test_built_in_document_types_still_resolve_without_external_profile() -> None:
    for task_type in ["hara", "technical_solution", "test_report", "generic_document"]:
        rules = get_document_type_rules(task_type)
        assert rules.task_type == task_type
