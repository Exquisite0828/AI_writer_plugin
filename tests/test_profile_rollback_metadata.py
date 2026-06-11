import shutil
from pathlib import Path

import yaml

from ai_writing_plugin.corrections.harvester import harvest_corrections
from ai_writing_plugin.corrections.promotion import promote_profile
from ai_writing_plugin.corrections.schema import sha256_file


FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_successful_promotion_writes_rollback_metadata_and_previous_backup(tmp_path: Path) -> None:
    profile_path = tmp_path / "document_profile.yaml"
    shutil.copyfile(FIXTURES / "external_profile_base.yaml", profile_path)
    before_hash = sha256_file(profile_path)
    run_dir = tmp_path / "run"
    harvest_corrections(run_dir, FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    patch_path = run_dir / "learning" / "candidate_profile_patch.yaml"
    approval_path = write_approval(tmp_path, patch_path, profile_path)

    promote_profile(
        run_dir=run_dir,
        candidate_patch_path=patch_path,
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=profile_path,
        output_dir=run_dir / "learning",
        apply=True,
    )

    metadata = yaml.safe_load((run_dir / "learning" / "profile_rollback_metadata.yaml").read_text(encoding="utf-8"))
    backup_path = Path(metadata["previous_profile"]["content_backup_path"])

    assert metadata["promotion_id"].startswith("promotion-")
    assert metadata["rollback_id"].startswith("rollback-")
    assert metadata["previous_profile"]["path"] == str(profile_path)
    assert metadata["previous_profile"]["version"] == "0.1.0"
    assert metadata["previous_profile"]["sha256"] == before_hash
    assert metadata["new_profile"]["version"] == "0.1.1"
    assert metadata["new_profile"]["sha256"] == sha256_file(profile_path)
    assert metadata["rollback_requires_human_approval"] is True
    assert metadata["stable_skill_touched"] is False
    assert metadata["built_in_rules_touched"] is False
    assert backup_path.exists()
    assert sha256_file(backup_path) == before_hash


def write_approval(tmp_path: Path, patch_path: Path, profile_path: Path) -> Path:
    patch = yaml.safe_load(patch_path.read_text(encoding="utf-8"))
    data = {
        "approval_id": "approval-test",
        "approval_status": "approved",
        "approved_by": "human-reviewer",
        "approved_candidate_patch_id": patch["patch_id"],
        "approved_base_profile_sha256": patch["base_profile"]["sha256"],
        "approved_eval_report_sha256": sha256_file(FIXTURES / "eval_report_pass.json"),
        "approved_target_profile_path": str(profile_path),
        "approval_scope": "profile_patch_only",
        "explicit_approval_text": "I approve this candidate profile patch for promotion.",
        "rollback_required": True,
        "stable_skill_update_approved": False,
        "professional_approval_granted": False,
    }
    approval_path = tmp_path / "approval.yaml"
    approval_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return approval_path

