from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.corrections.schema import CorrectionValidationError, normalize_correction_event


FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_valid_correction_event_gets_deterministic_event_id() -> None:
    raw = yaml.safe_load((FIXTURES / "valid_add_critical_claim.yaml").read_text(encoding="utf-8"))

    first = normalize_correction_event(raw)
    second = normalize_correction_event(raw)

    assert first == second
    assert first["event_id"].startswith("corr-")
    assert first["auto_patch_status"] == "eligible"
    assert first["field"] == "critical_claims"
    assert first["operation"] == "add_to_list"


@pytest.mark.parametrize("field", ["profile_id", "field", "operation", "value"])
def test_correction_event_rejects_missing_required_fields(field: str) -> None:
    raw = yaml.safe_load((FIXTURES / "valid_add_critical_claim.yaml").read_text(encoding="utf-8"))
    raw.pop(field)

    with pytest.raises(CorrectionValidationError, match=field):
        normalize_correction_event(raw)


def test_correction_event_rejects_unknown_correction_type() -> None:
    raw = yaml.safe_load((FIXTURES / "valid_add_critical_claim.yaml").read_text(encoding="utf-8"))
    raw["correction_type"] = "invent_new_document_type"

    with pytest.raises(CorrectionValidationError, match="correction_type"):
        normalize_correction_event(raw)


@pytest.mark.parametrize(
    "target_path",
    [
        "skills/writing-core/SKILL.md",
        "ai_writing_plugin/document_types/hara.py",
    ],
)
def test_correction_event_rejects_skill_and_builtin_rule_targets(target_path: str) -> None:
    raw = yaml.safe_load((FIXTURES / "valid_add_critical_claim.yaml").read_text(encoding="utf-8"))
    raw["target_path"] = target_path

    with pytest.raises(CorrectionValidationError, match="unsafe target"):
        normalize_correction_event(raw)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sample_policy", "Sample documents may be used as project fact sources."),
        ("reference_policy", "Reference materials prove project facts."),
    ],
)
def test_policy_relaxation_events_are_blocked_from_auto_patch(field: str, value: str) -> None:
    raw = yaml.safe_load((FIXTURES / "valid_add_critical_claim.yaml").read_text(encoding="utf-8"))
    raw.update(
        {
            "correction_type": "sample_policy_guard" if field == "sample_policy" else "reference_policy_guard",
            "field": field,
            "operation": "replace_policy_text",
            "value": value,
        }
    )

    event = normalize_correction_event(raw)

    assert event["auto_patch_status"] == "blocked_unsafe_auto_patch"
    assert "not auto-applicable" in event["block_reason"]

