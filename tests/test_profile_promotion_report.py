import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from ai_writing_plugin.corrections.harvester import harvest_corrections
from ai_writing_plugin.corrections.promotion import promote_profile
from ai_writing_plugin.corrections.schema import sha256_file


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_successful_promotion_updates_only_explicit_external_profile_and_reports_boundary(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package)

    report = promote_profile(
        run_dir=package["run_dir"],
        candidate_patch_path=package["patch_path"],
        eval_report_path=FIXTURES / "eval_report_pass.json",
        approval_path=approval_path,
        target_profile_path=package["profile_path"],
        output_dir=package["run_dir"] / "learning",
        apply=True,
    )

    updated = yaml.safe_load(package["profile_path"].read_text(encoding="utf-8"))
    assert report["status"] == "promoted"
    assert report["promoted"] is True
    assert updated["profile_version"] == "0.1.1"
    assert "data retention period" in updated["critical_claims"]
    assert sha256_file(FIXTURES / "external_profile_base.yaml") == package["fixture_hash"]
    report_json = json.loads((package["run_dir"] / "learning" / "profile_promotion_report.json").read_text(encoding="utf-8"))
    report_md = (package["run_dir"] / "learning" / "profile_promotion_report.md").read_text(encoding="utf-8")
    assert report_json["status"] == "promoted"
    assert "not professional approval" in report_json["non_approval_notice"]
    assert "not professional approval" in report_md
    assert (package["run_dir"] / "learning" / "profile_rollback_metadata.yaml").exists()
    assert (package["run_dir"] / "learning" / "rollback_previous_profile.yaml").exists()


def test_profile_promote_cli_dry_run_and_apply(tmp_path: Path) -> None:
    dry_run_package = make_package(tmp_path / "dry")
    dry_approval = write_approval(tmp_path / "dry", dry_run_package)
    dry_result = run_promote_cli(dry_run_package, dry_approval, apply=False)

    assert dry_result.returncode == 0, dry_result.stderr
    dry_report = json.loads((dry_run_package["run_dir"] / "learning" / "profile_promotion_report.json").read_text(encoding="utf-8"))
    assert dry_report["status"] == "dry_run_ready_to_promote"
    assert sha256_file(dry_run_package["profile_path"]) == dry_run_package["profile_before_hash"]

    apply_package = make_package(tmp_path / "apply")
    apply_approval = write_approval(tmp_path / "apply", apply_package)
    apply_result = run_promote_cli(apply_package, apply_approval, apply=True)

    assert apply_result.returncode == 0, apply_result.stderr
    apply_report = json.loads((apply_package["run_dir"] / "learning" / "profile_promotion_report.json").read_text(encoding="utf-8"))
    updated = yaml.safe_load(apply_package["profile_path"].read_text(encoding="utf-8"))
    assert apply_report["status"] == "promoted"
    assert updated["profile_version"] == "0.1.1"
    assert "data retention period" in updated["critical_claims"]


def test_profile_promote_cli_blocked_returns_nonzero_and_does_not_modify_profile(tmp_path: Path) -> None:
    package = make_package(tmp_path)
    approval_path = write_approval(tmp_path, package, eval_report_path=FIXTURES / "eval_report_fail.json")

    result = run_promote_cli(package, approval_path, eval_report=FIXTURES / "eval_report_fail.json", apply=False)

    assert result.returncode == 1
    assert sha256_file(package["profile_path"]) == package["profile_before_hash"]
    report = json.loads((package["run_dir"] / "learning" / "profile_promotion_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "blocked_eval_failed"


def make_package(tmp_path: Path) -> dict[str, object]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    profile_path = tmp_path / "document_profile.yaml"
    shutil.copyfile(FIXTURES / "external_profile_base.yaml", profile_path)
    run_dir = tmp_path / "run"
    harvest_corrections(run_dir, FIXTURES / "valid_add_critical_claim.yaml", profile_path)
    return {
        "run_dir": run_dir,
        "profile_path": profile_path,
        "patch_path": run_dir / "learning" / "candidate_profile_patch.yaml",
        "profile_before_hash": sha256_file(profile_path),
        "fixture_hash": sha256_file(FIXTURES / "external_profile_base.yaml"),
    }


def write_approval(
    tmp_path: Path,
    package: dict[str, object],
    *,
    eval_report_path: Path = FIXTURES / "eval_report_pass.json",
) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    patch = yaml.safe_load(Path(package["patch_path"]).read_text(encoding="utf-8"))
    data = {
        "approval_id": "approval-test",
        "approval_status": "approved",
        "approved_by": "human-reviewer",
        "approved_candidate_patch_id": patch["patch_id"],
        "approved_base_profile_sha256": patch["base_profile"]["sha256"],
        "approved_eval_report_sha256": sha256_file(eval_report_path),
        "approved_target_profile_path": str(package["profile_path"]),
        "approval_scope": "profile_patch_only",
        "explicit_approval_text": "I approve this candidate profile patch for promotion.",
        "rollback_required": True,
        "stable_skill_update_approved": False,
        "professional_approval_granted": False,
    }
    approval_path = tmp_path / "approval.yaml"
    approval_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return approval_path


def run_promote_cli(
    package: dict[str, object],
    approval_path: Path,
    *,
    eval_report: Path = FIXTURES / "eval_report_pass.json",
    apply: bool,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-m",
        "ai_writing_plugin",
        "profile-promote",
        "--run-dir",
        str(package["run_dir"]),
        "--candidate-patch",
        str(package["patch_path"]),
        "--eval-report",
        str(eval_report),
        "--approval",
        str(approval_path),
        "--target-profile",
        str(package["profile_path"]),
        "--output-dir",
        str(Path(package["run_dir"]) / "learning"),
    ]
    if apply:
        command.append("--apply")
    return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)

