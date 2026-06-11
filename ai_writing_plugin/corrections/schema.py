from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class CorrectionValidationError(ValueError):
    """Raised when a correction or N7 candidate artifact is invalid."""


ALLOWED_CORRECTION_TYPES = {
    "required_section_missing",
    "critical_claim_missing",
    "human_confirmation_missing",
    "forbidden_final_claim_missing",
    "review_focus_missing",
    "verification_focus_missing",
    "terminology_correction",
    "output_label_correction",
    "sample_policy_guard",
    "reference_policy_guard",
    "final_status_policy_guard",
}

SAFE_LIST_FIELDS = {
    "default_sections",
    "required_sections",
    "optional_sections",
    "critical_claims",
    "requires_human_confirmation",
    "forbidden_final_claims",
    "review_focus",
    "verification_focus",
}

SAFE_MAPPING_FIELDS = {"terminology", "output_labels"}
SAFE_FIELDS = SAFE_LIST_FIELDS | SAFE_MAPPING_FIELDS

RISKY_FIELDS = {
    "sample_policy",
    "reference_policy",
    "default_final_status",
    "allowed_final_statuses",
    "fact_source_roles",
    "non_fact_source_roles",
    "candidate_learning_policy",
}

SAFE_OPERATIONS = {"add_to_list", "set_mapping_key"}
MANUAL_BLOCKED_OPERATIONS = {
    "replace_policy_text",
    "replace_list",
    "remove_from_list",
    "modify_fact_source_roles",
    "modify_non_fact_source_roles",
    "modify_sample_policy_to_fact_source",
    "modify_reference_policy_to_fact_source",
    "modify_candidate_learning_policy_to_active",
}
FORBIDDEN_TARGET_OPERATIONS = {"modify_skill_file", "modify_python_rules"}

OPTIONAL_REFERENCE_ROOTS = {"superpowers本体架构", "HARA报告生成参考资料集_EPS"}


def normalize_correction_event(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CorrectionValidationError("correction event must be a mapping")

    allowed_fields = {
        "event_id",
        "profile_id",
        "profile_version",
        "run_id",
        "artifact_path",
        "target_path",
        "correction_type",
        "field",
        "operation",
        "key",
        "value",
        "rationale",
        "source",
        "submitted_by",
        "status",
    }
    unknown = sorted(set(raw) - allowed_fields)
    if unknown:
        raise CorrectionValidationError(f"unknown correction field(s): {', '.join(unknown)}")

    profile_id = require_string(raw, "profile_id")
    profile_version = require_string(raw, "profile_version")
    correction_type = require_string(raw, "correction_type")
    field = require_string(raw, "field")
    operation = require_string(raw, "operation")
    value = require_string(raw, "value")
    rationale = optional_string(raw, "rationale")
    source = optional_string(raw, "source") or "human_correction"
    status = optional_string(raw, "status") or "submitted"

    if correction_type not in ALLOWED_CORRECTION_TYPES:
        raise CorrectionValidationError(f"invalid correction_type: {correction_type}")
    if status != "submitted":
        raise CorrectionValidationError(f"invalid status: {status}")
    if operation in FORBIDDEN_TARGET_OPERATIONS:
        raise CorrectionValidationError(f"operation is not allowed in N7: {operation}")

    target_path = optional_string(raw, "target_path")
    if target_path and is_unsafe_target_path(target_path):
        raise CorrectionValidationError(f"unsafe target path: {target_path}")

    if field in SAFE_FIELDS:
        auto_patch_status, block_reason = classify_safe_field_change(field, operation)
    elif field in RISKY_FIELDS:
        if operation not in SAFE_OPERATIONS and operation not in MANUAL_BLOCKED_OPERATIONS:
            raise CorrectionValidationError(f"operation is not allowed in N7 correction events: {operation}")
        auto_patch_status = "blocked_unsafe_auto_patch"
        block_reason = f"{field} correction is not auto-applicable in N7"
    else:
        raise CorrectionValidationError(f"field is not allowed in N7 correction events: {field}")

    if operation == "set_mapping_key":
        key = require_string(raw, "key")
    else:
        key = optional_string(raw, "key")

    normalized: dict[str, Any] = {
        "profile_id": profile_id,
        "profile_version": profile_version,
        "correction_type": correction_type,
        "field": field,
        "operation": operation,
        "value": value,
        "rationale": rationale,
        "source": source,
        "status": status,
        "auto_patch_status": auto_patch_status,
    }
    for optional in ["run_id", "artifact_path", "submitted_by", "target_path"]:
        optional_value = optional_string(raw, optional)
        if optional_value:
            normalized[optional] = optional_value
    if key:
        normalized["key"] = key
    if block_reason:
        normalized["block_reason"] = block_reason

    event_id = optional_string(raw, "event_id")
    if not event_id:
        event_id = f"corr-{stable_hash(normalized)[:16]}"
    normalized = {"event_id": event_id, **normalized}
    return normalized


def classify_safe_field_change(field: str, operation: str) -> tuple[str, str]:
    if operation in MANUAL_BLOCKED_OPERATIONS:
        return "blocked_unsafe_auto_patch", f"{operation} is not auto-applicable in N7"
    if operation not in SAFE_OPERATIONS:
        raise CorrectionValidationError(f"operation is not allowed in N7 correction events: {operation}")
    if operation == "add_to_list" and field not in SAFE_LIST_FIELDS:
        raise CorrectionValidationError(f"add_to_list is not allowed for field: {field}")
    if operation == "set_mapping_key" and field not in SAFE_MAPPING_FIELDS:
        raise CorrectionValidationError(f"set_mapping_key is not allowed for field: {field}")
    return "eligible", ""


def is_unsafe_target_path(value: str | Path) -> bool:
    path = Path(str(value))
    parts = tuple(part for part in path.parts if part not in {"/", ""})
    if ".." in parts:
        return True
    if parts and parts[0] in OPTIONAL_REFERENCE_ROOTS:
        return True
    if "examples" in parts:
        return True
    if "docs" in parts and "archive" in parts:
        return True
    if path.name == "SKILL.md" and "skills" in parts:
        return True
    if path.suffix == ".py" and "ai_writing_plugin" in parts and "document_types" in parts:
        return True
    return False


def ensure_safe_external_profile_target(path: Path) -> None:
    if is_unsafe_target_path(path):
        raise CorrectionValidationError(f"unsafe target profile path: {path}")
    if path.suffix.lower() not in {".yaml", ".yml"}:
        raise CorrectionValidationError(f"target profile must be an external YAML document_profile: {path}")


def require_string(data: dict[str, Any], field_name: str) -> str:
    if field_name not in data:
        raise CorrectionValidationError(f"{field_name} is required")
    value = data[field_name]
    if not isinstance(value, str) or not value.strip():
        raise CorrectionValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def optional_string(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise CorrectionValidationError(f"{field_name} must be a string")
    return value.strip()


def stable_hash(data: Any) -> str:
    return sha256_text(canonical_json(data))


def canonical_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
