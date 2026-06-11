import json
import shutil
from pathlib import Path

import yaml

from ai_writing_plugin.corrections.harvester import harvest_corrections
from ai_writing_plugin.corrections.schema import sha256_file


FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_candidate_profile_patch_is_inactive_deterministic_and_safe(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    before_hash = sha256_file(profile_path)

    first = harvest_corrections(tmp_path / "run-a", FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    second = harvest_corrections(tmp_path / "run-b", FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    patch_a = yaml.safe_load(first["candidate_patch_path"].read_text(encoding="utf-8"))
    patch_b = yaml.safe_load(second["candidate_patch_path"].read_text(encoding="utf-8"))

    assert patch_a["patch_id"] == patch_b["patch_id"]
    assert patch_a["status"] == "proposed"
    assert patch_a["activation_status"] == "inactive"
    assert patch_a["auto_apply"] is False
    assert patch_a["base_profile"]["profile_id"] == "customer_demo.custom_technical_note"
    assert patch_a["base_profile"]["profile_version"] == "0.1.0"
    assert patch_a["base_profile"]["profile_path"] == str(profile_path)
    assert patch_a["base_profile"]["sha256"] == before_hash
    assert patch_a["safety"]["stable_skill_update_allowed"] is False
    assert patch_a["safety"]["built_in_rules_update_allowed"] is False
    assert patch_a["promotion"]["promoted"] is False
    assert patch_a["proposed_changes"] == [
        {
            "operation": "add_to_list",
            "field": "critical_claims",
            "value": "data retention period",
            "rationale": "User indicated this must be treated as a critical claim.",
        }
    ]
    assert sha256_file(profile_path) == before_hash


def test_high_risk_policy_correction_is_not_auto_applicable(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    result = harvest_corrections(
        tmp_path / "run",
        FIXTURES / "invalid_modify_sample_policy_to_fact_source.yaml",
        profile_path,
    )
    patch = yaml.safe_load(result["candidate_patch_path"].read_text(encoding="utf-8"))

    assert patch["proposed_changes"] == []
    assert patch["blocked_changes"][0]["field"] == "sample_policy"
    assert patch["blocked_changes"][0]["status"] == "blocked_unsafe_auto_patch"
    assert patch["auto_apply"] is False


def test_candidate_patch_does_not_write_skill_or_builtin_rule_targets(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    result = harvest_corrections(tmp_path / "run", FIXTURES / "valid_terminology_update.yaml", profile_path)
    patch = yaml.safe_load(result["candidate_patch_path"].read_text(encoding="utf-8"))

    assert all("Skill.md" not in json.dumps(change) for change in patch["proposed_changes"])
    assert patch["safety"]["stable_skill_update_allowed"] is False
    assert patch["safety"]["built_in_rules_update_allowed"] is False


def copy_profile(tmp_path: Path) -> Path:
    profile_path = tmp_path / "document_profile.yaml"
    shutil.copyfile(FIXTURES / "external_profile_base.yaml", profile_path)
    return profile_path

