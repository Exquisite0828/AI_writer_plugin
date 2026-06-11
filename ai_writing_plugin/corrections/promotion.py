from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from ai_writing_plugin.document_types.profile_loader import DocumentProfile, DocumentProfileValidationError, load_document_profile_file

from .patch import validate_supported_proposed_changes
from .report import build_profile_promotion_report, write_profile_promotion_report
from .schema import CorrectionValidationError, ensure_safe_external_profile_target, sha256_file, sha256_text, stable_hash


def promote_profile(
    *,
    run_dir: Path,
    candidate_patch_path: Path,
    eval_report_path: Path,
    approval_path: Path | None,
    target_profile_path: Path,
    output_dir: Path,
    apply: bool = False,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    candidate_patch_path = Path(candidate_patch_path)
    eval_report_path = Path(eval_report_path)
    target_profile_path = Path(target_profile_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    patch = load_yaml_mapping(candidate_patch_path, "candidate patch")
    patch_id = str(patch.get("patch_id", ""))
    base_profile = dict(patch.get("base_profile") or {})

    def blocked(status: str, reason: str, *, eval_report: dict[str, Any] | None = None, eval_sha: str = "") -> dict[str, Any]:
        report = build_profile_promotion_report(
            status=status,
            promoted=False,
            candidate_patch_path=candidate_patch_path,
            candidate_patch_id=patch_id,
            target_profile_path=target_profile_path,
            eval_report=eval_report,
            eval_report_path=eval_report_path,
            eval_report_sha256=eval_sha,
            approval_path=approval_path,
            base_profile=base_profile,
            reasons=[reason],
            dry_run=False,
        )
        write_profile_promotion_report(report, output_dir)
        return report

    try:
        ensure_safe_external_profile_target(target_profile_path)
    except CorrectionValidationError as exc:
        return blocked("blocked_unsafe_target", str(exc))

    unsupported_reason = validate_supported_proposed_changes(patch)
    if unsupported_reason:
        return blocked("blocked_unsupported_operation", unsupported_reason)

    if not eval_report_path.exists():
        return blocked("blocked_missing_eval", f"eval report not found: {eval_report_path}")
    eval_sha = sha256_file(eval_report_path)
    try:
        eval_report = json.loads(eval_report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return blocked("blocked_missing_eval", f"eval report parse failure: {exc}", eval_sha=eval_sha)
    if not eval_report_passed(eval_report):
        return blocked("blocked_eval_failed", "eval report did not pass", eval_report=eval_report, eval_sha=eval_sha)

    if approval_path is None or not Path(approval_path).exists():
        return blocked(
            "blocked_pending_human_approval",
            "explicit human approval file is required",
            eval_report=eval_report,
            eval_sha=eval_sha,
        )
    approval_path = Path(approval_path)
    approval = load_yaml_mapping(approval_path, "approval")
    approval_error = validate_approval(
        approval=approval,
        patch=patch,
        eval_sha=eval_sha,
        target_profile_path=target_profile_path,
    )
    if approval_error:
        return blocked("blocked_approval_mismatch", approval_error, eval_report=eval_report, eval_sha=eval_sha)

    current_hash = sha256_file(target_profile_path)
    expected_hash = str(base_profile.get("sha256", ""))
    if current_hash != expected_hash:
        return blocked(
            "blocked_profile_hash_mismatch",
            "target profile sha256 does not match candidate patch base_profile.sha256",
            eval_report=eval_report,
            eval_sha=eval_sha,
        )

    try:
        patched_profile = apply_patch_to_profile(target_profile_path, patch)
        DocumentProfile.model_validate(patched_profile)
    except (DocumentProfileValidationError, ValidationError, ValueError) as exc:
        return blocked("blocked_profile_validation_failed", str(exc), eval_report=eval_report, eval_sha=eval_sha)

    new_profile_text = yaml.safe_dump(patched_profile, allow_unicode=True, sort_keys=False)
    new_profile_sha = sha256_text(new_profile_text)
    rollback_metadata = build_rollback_metadata(
        output_dir=output_dir,
        patch=patch,
        target_profile_path=target_profile_path,
        previous_sha=current_hash,
        new_sha=new_profile_sha,
        new_version=str(patched_profile["profile_version"]),
    )

    if not apply:
        write_rollback_artifacts(output_dir, target_profile_path, rollback_metadata)
        report = build_profile_promotion_report(
            status="dry_run_ready_to_promote",
            promoted=False,
            candidate_patch_path=candidate_patch_path,
            candidate_patch_id=patch_id,
            target_profile_path=target_profile_path,
            eval_report=eval_report,
            eval_report_path=eval_report_path,
            eval_report_sha256=eval_sha,
            approval_path=approval_path,
            base_profile=base_profile,
            new_profile={
                "path": str(target_profile_path),
                "version": patched_profile["profile_version"],
                "sha256": new_profile_sha,
            },
            rollback={"required": True, "prepared": True, "metadata_path": str(output_dir / "profile_rollback_metadata.yaml")},
            reasons=["All promotion gates passed; rerun with --apply to update the explicit external profile."],
            dry_run=True,
        )
        write_profile_promotion_report(report, output_dir)
        return report

    write_rollback_artifacts(output_dir, target_profile_path, rollback_metadata)
    target_profile_path.write_text(new_profile_text, encoding="utf-8")
    report = build_profile_promotion_report(
        status="promoted",
        promoted=True,
        candidate_patch_path=candidate_patch_path,
        candidate_patch_id=patch_id,
        target_profile_path=target_profile_path,
        eval_report=eval_report,
        eval_report_path=eval_report_path,
        eval_report_sha256=eval_sha,
        approval_path=approval_path,
        base_profile=base_profile,
        new_profile={
            "path": str(target_profile_path),
            "version": patched_profile["profile_version"],
            "sha256": sha256_file(target_profile_path),
        },
        rollback={"required": True, "prepared": True, "metadata_path": str(output_dir / "profile_rollback_metadata.yaml")},
        reasons=["External profile promotion applied after approval, eval, hash, schema, and rollback gates passed."],
        dry_run=False,
    )
    write_profile_promotion_report(report, output_dir)
    return report


def eval_report_passed(eval_report: dict[str, Any]) -> bool:
    return eval_report.get("overall_status") == "pass" and int(eval_report.get("expectation_mismatch_count", 0)) == 0


def validate_approval(
    *,
    approval: dict[str, Any],
    patch: dict[str, Any],
    eval_sha: str,
    target_profile_path: Path,
) -> str:
    checks = {
        "approval_status": "approved",
        "approved_candidate_patch_id": patch.get("patch_id"),
        "approved_base_profile_sha256": (patch.get("base_profile") or {}).get("sha256"),
        "approved_eval_report_sha256": eval_sha,
        "approved_target_profile_path": str(target_profile_path),
        "approval_scope": "profile_patch_only",
    }
    for field, expected in checks.items():
        if approval.get(field) != expected:
            return f"approval {field} mismatch"
    if approval.get("stable_skill_update_approved") is not False:
        return "approval must not approve stable Skill updates"
    if approval.get("professional_approval_granted") is not False:
        return "approval must not grant professional approval"
    if approval.get("rollback_required") is not True:
        return "approval must require rollback metadata"
    explicit_text = str(approval.get("explicit_approval_text", "")).lower()
    if "approve" not in explicit_text or "profile patch" not in explicit_text:
        return "approval text must explicitly approve this profile patch"
    return ""


def apply_patch_to_profile(target_profile_path: Path, patch: dict[str, Any]) -> dict[str, Any]:
    loaded = load_document_profile_file(target_profile_path, profile_path=str(target_profile_path))
    data = yaml.safe_load(target_profile_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("target profile root must be a mapping")
    for change in patch.get("proposed_changes", []):
        field = change["field"]
        operation = change["operation"]
        if operation == "add_to_list":
            if not isinstance(data.get(field), list):
                raise ValueError(f"profile field is not a list: {field}")
            if change.get("value") not in data[field]:
                data[field].append(change.get("value"))
        elif operation == "set_mapping_key":
            if not isinstance(data.get(field), dict):
                raise ValueError(f"profile field is not a mapping: {field}")
            data[field][change.get("key", "")] = change.get("value")
        else:
            raise ValueError(f"unsupported operation: {operation}")
    data["profile_version"] = bump_patch_version(loaded.profile.profile_version)
    return data


def bump_patch_version(version: str) -> str:
    parts = version.split(".")
    if len(parts) == 3 and all(part.isdigit() for part in parts):
        parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)
    return f"{version}.1"


def build_rollback_metadata(
    *,
    output_dir: Path,
    patch: dict[str, Any],
    target_profile_path: Path,
    previous_sha: str,
    new_sha: str,
    new_version: str,
) -> dict[str, Any]:
    base_profile = patch["base_profile"]
    promotion_seed = {
        "patch_id": patch["patch_id"],
        "target_profile_path": str(target_profile_path),
        "previous_sha": previous_sha,
        "new_sha": new_sha,
    }
    promotion_id = f"promotion-{stable_hash(promotion_seed)[:16]}"
    rollback_id = f"rollback-{stable_hash({'promotion_id': promotion_id, 'previous_sha': previous_sha})[:16]}"
    return {
        "rollback_id": rollback_id,
        "promotion_id": promotion_id,
        "profile_id": base_profile["profile_id"],
        "previous_profile": {
            "path": str(target_profile_path),
            "version": base_profile["profile_version"],
            "sha256": previous_sha,
            "content_backup_path": str(output_dir / "rollback_previous_profile.yaml"),
        },
        "new_profile": {
            "path": str(target_profile_path),
            "version": new_version,
            "sha256": new_sha,
        },
        "rollback_requires_human_approval": True,
        "stable_skill_touched": False,
        "built_in_rules_touched": False,
    }


def write_rollback_artifacts(output_dir: Path, target_profile_path: Path, rollback_metadata: dict[str, Any]) -> None:
    backup_path = output_dir / "rollback_previous_profile.yaml"
    metadata_path = output_dir / "profile_rollback_metadata.yaml"
    backup_path.write_text(target_profile_path.read_text(encoding="utf-8"), encoding="utf-8")
    metadata_path.write_text(yaml.safe_dump(rollback_metadata, allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} file not found: {path}") from exc
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise ValueError(f"{label} parse failure: {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} root must be a mapping: {path}")
    return loaded


