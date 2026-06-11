import json
import shutil
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.corrections.harvester import harvest_corrections
from ai_writing_plugin.corrections.promotion import promote_profile
from ai_writing_plugin.corrections.schema import sha256_file


FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_promotion_blocks_without_human_approval(tmp_path: Path) -> None:
    package = make_package(tmp_path)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=None,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_pending_human_approval"
    assert report["promoted"] is False


def test_promotion_blocks_missing_eval_report(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package, eval_report_path=tmp_path / "missing-eval.json")

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=tmp_path / "missing-eval.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_missing_eval"
    assert sha256_file(package["profile_path"]) == package["profile_before_hash"]


def test_promotion_blocks_failed_eval_report(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package, eval_report_path=FIXTURES / "eval_report_fail.json")

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_fail.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_eval_failed"


@pytest.mark.parametrize(
    "override",
    [
        {"approved_candidate_patch_id": "n7patch-wrong"},
        {"approved_eval_report_sha256": "0" * 64},
        {"approved_target_profile_path": "another/profile.yaml"},
    ],
)
def test_promotion_blocks_approval_mismatches(tmp_path: Path, override: dict[str, str]) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package, override=override)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_approval_mismatch"


def test_promotion_blocks_profile_hash_mismatch(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    profile = yaml.safe_load(package["profile_path"].read_text(encoding="utf-8"))
    profile["review_focus"].append("new external edit")
    package["profile_path"].write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    approval_path = write_approval(tmp_path, package)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_profile_hash_mismatch"


def test_promotion_blocks_invalid_profile_after_patch(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    patch = yaml.safe_load(package["patch_path"].read_text(encoding="utf-8"))
    patch["proposed_changes"] = [
        {
            "operation": "set_mapping_key",
            "field": "terminology",
            "key": "",
            "value": "invalid empty key",
            "rationale": "Force patched profile schema validation to fail.",
        }
    ]
    package["patch_path"].write_text(yaml.safe_dump(patch, sort_keys=False), encoding="utf-8")
    approval_path = write_approval(tmp_path, package)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_profile_validation_failed"


@pytest.mark.parametrize(
    "target_profile",
    [
        "skills/writing-core/SKILL.md",
        "ai_writing_plugin/document_types/hara.py",
    ],
)
def test_promotion_blocks_unsafe_targets(tmp_path: Path, target_profile: str) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package, override={"approved_target_profile_path": target_profile})

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=Path(target_profile),
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_unsafe_target"


def test_promotion_blocks_unsupported_operation(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    patch = yaml.safe_load(package["patch_path"].read_text(encoding="utf-8"))
    patch["proposed_changes"][0]["operation"] = "remove_from_list"
    package["patch_path"].write_text(yaml.safe_dump(patch, sort_keys=False), encoding="utf-8")
    approval_path = write_approval(tmp_path, package)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "blocked_unsupported_operation"


def test_promotion_dry_run_does_not_modify_profile(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=False,
    )

    assert report["status"] == "dry_run_ready_to_promote"
    assert report["promoted"] is False
    assert sha256_file(package["profile_path"]) == package["profile_before_hash"]


def make_package(tmp_path: Path) -> dict[str, object]:
    profile_path = tmp_path / "document_profile.yaml"
    shutil.copyfile(FIXTURES / "external_profile_base.yaml", profile_path)
    run_dir = tmp_path / "run"
    harvest_corrections(run_dir, FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    patch_path = run_dir / "learning" / "candidate_profile_patch.yaml"
    return {
        "run_dir": run_dir,
        "profile_path": profile_path,
        "patch_path": patch_path,
        "profile_before_hash": sha256_file(profile_path),
    }


def write_approval(
    tmp_path: Path,
    package: dict[str, object],
    *,
    eval_report_path: Path = FIXTURES / "eval_report_pass.json",
    override: dict[str, object] | None = None,
) -> Path:
    patch = yaml.safe_load(Path(package["patch_path"]).read_text(encoding="utf-8"))
    data = {
        "approval_id": "approval-test",
        "approval_status": "approved",
        "approved_by": "human-reviewer",
        "approved_candidate_patch_id": patch["patch_id"],
        "approved_base_profile_sha256": patch["base_profile"]["sha256"],
        "approved_eval_report_sha256": sha256_file(eval_report_path) if eval_report_path.exists() else "missing",
        "approved_target_profile_path": str(package["profile_path"]),
        "approval_scope": "profile_patch_only",
        "explicit_approval_text": "I approve this candidate profile patch for promotion.",
        "rollback_required": True,
        "stable_skill_update_approved": False,
        "professional_approval_granted": False,
    }
    data.update(override or {})
    approval_path = tmp_path / "approval.yaml"
    approval_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return approval_path

