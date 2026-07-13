from __future__ import annotations

import hashlib
import re
from pathlib import Path, PurePosixPath
from typing import Any


STAGES = {
    "ingest",
    "outline",
    "evidence_planning",
    "draft",
    "review",
    "finalize",
    "learning",
}
STEPS = {
    "step-input-materials",
    "step-material-inventory",
    "step-source-index",
    "step-template-outline",
    "step-research-questions",
    "step-evidence-map",
    "step-conservative-draft",
    "step-review",
    "step-verification",
    "step-revision",
    "step-final-report",
    "step-run-summary",
    "step-candidate-profile-update",
}
RESULT_STATUSES = {"done", "needs_revision", "blocked", "skipped"}
STEP_RESULT_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "step",
    "status",
    "artifact_paths",
    "artifact_hashes",
    "summary",
    "blocking_issues_count",
    "next_gate_status",
}
REVIEW_RESULT_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "step",
    "status",
    "review_package_paths",
    "review_package_hashes",
    "summary",
    "blocking_issues_count",
    "next_gate_status",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
DISALLOWED_CONTEXT_PREFIXES = (
    "examples/",
    "docs/maintainers/",
    "contracts/",
)


class ShortResultError(ValueError):
    """Raised when StepResult or ReviewResult metadata is invalid."""


def validate_step_result(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    return _validate_result(
        payload,
        expected_kind="step_result",
        expected_fields=STEP_RESULT_FIELDS,
        paths_field="artifact_paths",
        hashes_field="artifact_hashes",
        run_dir=run_dir,
    )


def validate_review_result(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    return _validate_result(
        payload,
        expected_kind="review_result",
        expected_fields=REVIEW_RESULT_FIELDS,
        paths_field="review_package_paths",
        hashes_field="review_package_hashes",
        run_dir=run_dir,
    )


def _validate_result(
    payload: dict[str, Any],
    *,
    expected_kind: str,
    expected_fields: set[str],
    paths_field: str,
    hashes_field: str,
    run_dir: Path | str | None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ShortResultError("short result payload must be a JSON object")

    validate_exact_fields(payload, expected_fields)
    validate_literal(payload["kind"], expected_kind, "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_stage(payload["stage"])
    validate_step(payload["step"])
    validate_status(payload["status"])
    validate_summary(payload["summary"])
    validate_gate_status(payload["next_gate_status"])
    validate_blocking_issues_count(payload["blocking_issues_count"])

    paths = validate_path_list(payload[paths_field], paths_field)
    hashes = validate_hash_map(payload[hashes_field], hashes_field)
    if set(paths) != set(hashes):
        raise ShortResultError(f"{hashes_field} hash keys must match path list")

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise ShortResultError("run_id must match run_dir name")
        validate_files_and_hashes(paths, hashes, run_root)

    return payload


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise ShortResultError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise ShortResultError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ShortResultError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise ShortResultError("run_id must be a safe non-empty run id")


def validate_stage(value: Any) -> None:
    if not isinstance(value, str) or value not in STAGES:
        raise ShortResultError(f"invalid stage: {value!r}")


def validate_step(value: Any) -> None:
    if not isinstance(value, str) or value not in STEPS:
        raise ShortResultError(f"invalid step: {value!r}")


def validate_status(value: Any) -> None:
    if not isinstance(value, str) or value not in RESULT_STATUSES:
        raise ShortResultError(f"invalid status: {value!r}")


def validate_summary(value: Any) -> None:
    if not isinstance(value, str):
        raise ShortResultError("summary must be a string")
    if len(value) > 600:
        raise ShortResultError("summary must be at most 600 characters")
    if "```" in value:
        raise ShortResultError("summary must not contain code fences")


def validate_gate_status(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ShortResultError("next_gate_status must be a non-empty string")
    if len(value) > 120:
        raise ShortResultError("next_gate_status must be at most 120 characters")


def validate_blocking_issues_count(value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ShortResultError("blocking_issues_count must be a non-negative integer")


def validate_path_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ShortResultError(f"{field} must be a list of strings")
    if len(value) != len(set(value)):
        raise ShortResultError(f"{field} must not contain duplicate paths")
    for path in value:
        validate_result_path(path)
    return value


def validate_hash_map(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ShortResultError(f"{field} must be an object")
    for path, digest in value.items():
        validate_result_path(path)
        if not isinstance(digest, str) or not SHA256_RE.match(digest):
            raise ShortResultError(f"invalid sha256 for {path}")
    return value


def validate_result_path(path: str) -> None:
    if not path or path.startswith("/") or path.startswith("~"):
        raise ShortResultError(f"result path must be a relative POSIX path: {path!r}")
    if "\\" in path:
        raise ShortResultError(f"result path must use POSIX separators: {path!r}")
    if path.startswith("runs/"):
        raise ShortResultError(f"result path must not start with runs/: {path!r}")
    if path.startswith(DISALLOWED_CONTEXT_PREFIXES):
        raise ShortResultError(f"result path outside runtime result boundary: {path!r}")

    parts = PurePosixPath(path).parts
    if any(part == ".." for part in parts):
        raise ShortResultError(f"result path must not contain '..': {path!r}")
    if any(part in {"", "."} for part in parts):
        raise ShortResultError(f"result path must not contain empty or dot parts: {path!r}")


def validate_files_and_hashes(
    paths: list[str],
    hashes: dict[str, str],
    run_dir: Path,
) -> None:
    root = run_dir.expanduser().resolve()
    for relative_path in paths:
        candidate = (root / relative_path).resolve()
        if not candidate.is_relative_to(root):
            raise ShortResultError(f"result path escapes run_dir: {relative_path}")
        if not candidate.is_file():
            raise ShortResultError(f"result path does not exist: {relative_path}")
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != hashes[relative_path]:
            raise ShortResultError(f"sha256 mismatch for {relative_path}")
