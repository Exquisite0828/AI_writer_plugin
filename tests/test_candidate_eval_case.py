import json
import shutil
from pathlib import Path

from ai_writing_plugin.corrections.harvester import harvest_corrections
from ai_writing_plugin.corrections.patch import validate_candidate_eval_case


FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_candidate_eval_case_is_generated_and_deterministic(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)

    first = harvest_corrections(tmp_path / "run-a", FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    second = harvest_corrections(tmp_path / "run-b", FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    case_a = json.loads(first["candidate_eval_case_path"].read_text(encoding="utf-8"))
    case_b = json.loads(second["candidate_eval_case_path"].read_text(encoding="utf-8"))

    assert case_a["case_id"] == case_b["case_id"]
    assert case_a["phase"] == "N7"
    assert case_a["mode"] == "candidate_profile_patch"
    assert case_a["candidate_patch_path"] == str(first["candidate_patch_path"])
    assert case_a["expected"] == {
        "patch_status": "inactive",
        "auto_apply": False,
        "requires_human_approval": True,
        "requires_eval": True,
        "stable_skill_update_allowed": False,
    }
    validate_candidate_eval_case(case_a)


def copy_profile(tmp_path: Path) -> Path:
    profile_path = tmp_path / "document_profile.yaml"
    shutil.copyfile(FIXTURES / "external_profile_base.yaml", profile_path)
    return profile_path

