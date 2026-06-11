from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from ai_writing_plugin.document_types.profile_loader import load_document_profile_file

from .schema import SAFE_FIELDS, SAFE_LIST_FIELDS, SAFE_MAPPING_FIELDS, SAFE_OPERATIONS, sha256_file, stable_hash


class CandidatePatchError(ValueError):
    """Raised when a candidate profile patch cannot be created or validated."""


def write_candidate_profile_package(
    *,
    run_dir: Path,
    events: list[dict[str, Any]],
    profile_path: Path,
) -> dict[str, Path]:
    learning_dir = run_dir / "learning"
    learning_dir.mkdir(parents=True, exist_ok=True)
    candidate_patch_path = learning_dir / "candidate_profile_patch.yaml"
    candidate_eval_case_path = learning_dir / "candidate_eval_case.json"

    patch = build_candidate_profile_patch(
        events=events,
        profile_path=profile_path,
        candidate_eval_case_path=candidate_eval_case_path,
    )
    candidate_patch_path.write_text(yaml.safe_dump(patch, allow_unicode=True, sort_keys=False), encoding="utf-8")

    candidate_case = build_candidate_eval_case(patch=patch, candidate_patch_path=candidate_patch_path)
    candidate_eval_case_path.write_text(json.dumps(candidate_case, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "candidate_patch_path": candidate_patch_path,
        "candidate_eval_case_path": candidate_eval_case_path,
    }


def build_candidate_profile_patch(
    *,
    events: list[dict[str, Any]],
    profile_path: Path,
    candidate_eval_case_path: Path,
) -> dict[str, Any]:
    loaded_profile = load_document_profile_file(profile_path, profile_path=str(profile_path))
    base_profile = {
        "profile_id": loaded_profile.profile.profile_id,
        "profile_version": loaded_profile.profile.profile_version,
        "profile_path": str(profile_path),
        "sha256": sha256_file(profile_path),
    }
    proposed_changes: list[dict[str, Any]] = []
    blocked_changes: list[dict[str, Any]] = []
    for event in events:
        if event.get("auto_patch_status") == "eligible":
            proposed_changes.append(change_from_event(event))
        else:
            blocked_changes.append(blocked_change_from_event(event))

    patch_seed = {
        "phase": "N7",
        "base_profile": {
            "profile_id": base_profile["profile_id"],
            "profile_version": base_profile["profile_version"],
            "sha256": base_profile["sha256"],
        },
        "source_corrections": [event["event_id"] for event in events],
        "proposed_changes": proposed_changes,
        "blocked_changes": blocked_changes,
    }
    patch_id = f"n7patch-{stable_hash(patch_seed)[:16]}"
    return {
        "patch_id": patch_id,
        "status": "proposed",
        "activation_status": "inactive",
        "auto_apply": False,
        "phase": "N7",
        "base_profile": base_profile,
        "source_corrections": [{"event_id": event["event_id"]} for event in events],
        "proposed_changes": proposed_changes,
        "blocked_changes": blocked_changes,
        "safety": {
            "requires_human_approval": True,
            "requires_eval": True,
            "allowed_without_approval": False,
            "stable_skill_update_allowed": False,
            "built_in_rules_update_allowed": False,
        },
        "candidate_eval_case": {"path": str(candidate_eval_case_path)},
        "promotion": {
            "status": "blocked_pending_eval_or_approval",
            "promoted": False,
        },
        "rollback": {"required": True},
    }


def change_from_event(event: dict[str, Any]) -> dict[str, Any]:
    change = {
        "operation": event["operation"],
        "field": event["field"],
        "value": event["value"],
        "rationale": event.get("rationale", ""),
    }
    if event["operation"] == "set_mapping_key":
        change["key"] = event["key"]
    return change


def blocked_change_from_event(event: dict[str, Any]) -> dict[str, Any]:
    blocked = change_from_event(event) if event.get("operation") in SAFE_OPERATIONS else {
        "operation": event.get("operation", ""),
        "field": event.get("field", ""),
        "value": event.get("value", ""),
        "rationale": event.get("rationale", ""),
    }
    blocked["status"] = event.get("auto_patch_status", "blocked_unsafe_auto_patch")
    blocked["reason"] = event.get("block_reason", "correction is not auto-applicable in N7")
    return blocked


def validate_candidate_eval_case(case: dict[str, Any]) -> None:
    required = {"case_id", "phase", "mode", "profile_id", "candidate_patch_path", "expected"}
    missing = sorted(required - set(case))
    if missing:
        raise CandidatePatchError(f"candidate eval case missing required field(s): {', '.join(missing)}")
    if case["phase"] != "N7":
        raise CandidatePatchError("candidate eval case phase must be N7")
    if case["mode"] != "candidate_profile_patch":
        raise CandidatePatchError("candidate eval case mode must be candidate_profile_patch")
    expected = case["expected"]
    if not isinstance(expected, dict):
        raise CandidatePatchError("candidate eval case expected must be a mapping")
    required_expected = {
        "patch_status": "inactive",
        "auto_apply": False,
        "requires_human_approval": True,
        "requires_eval": True,
        "stable_skill_update_allowed": False,
    }
    for key, value in required_expected.items():
        if expected.get(key) != value:
            raise CandidatePatchError(f"candidate eval case expected.{key} must be {value!r}")


def build_candidate_eval_case(*, patch: dict[str, Any], candidate_patch_path: Path) -> dict[str, Any]:
    case = {
        "case_id": f"candidate-eval-{patch['patch_id']}",
        "phase": "N7",
        "mode": "candidate_profile_patch",
        "profile_id": patch["base_profile"]["profile_id"],
        "candidate_patch_path": str(candidate_patch_path),
        "expected": {
            "patch_status": "inactive",
            "auto_apply": False,
            "requires_human_approval": True,
            "requires_eval": True,
            "stable_skill_update_allowed": False,
        },
    }
    validate_candidate_eval_case(case)
    return case


def validate_supported_proposed_changes(patch: dict[str, Any]) -> str:
    if patch.get("status") != "proposed" or patch.get("activation_status") != "inactive" or patch.get("auto_apply") is not False:
        return "candidate patch must be proposed, inactive, and auto_apply=false"
    safety = patch.get("safety") or {}
    if safety.get("stable_skill_update_allowed") is not False or safety.get("built_in_rules_update_allowed") is not False:
        return "candidate patch attempts to allow stable Skill or built-in rules updates"
    if patch.get("blocked_changes"):
        return "candidate patch contains blocked changes that require manual profile editing"
    for change in patch.get("proposed_changes", []):
        operation = change.get("operation")
        field = change.get("field")
        if operation not in SAFE_OPERATIONS:
            return f"unsupported operation: {operation}"
        if field not in SAFE_FIELDS:
            return f"unsupported field: {field}"
        if operation == "add_to_list" and field not in SAFE_LIST_FIELDS:
            return f"add_to_list is not supported for field: {field}"
        if operation == "set_mapping_key" and field not in SAFE_MAPPING_FIELDS:
            return f"set_mapping_key is not supported for field: {field}"
    return ""

