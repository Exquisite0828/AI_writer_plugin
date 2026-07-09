from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .short_results import (
    RUN_ID_RE,
    SHA256_RE,
    STAGES,
    ShortResultError,
    validate_blocking_issues_count,
    validate_result_path,
    validate_review_result,
    validate_stage,
    validate_summary,
)
from .stage_review_issues import (
    StageReviewIssueError,
    issues_index_path,
    validate_issues_index,
)


RESULT_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "status",
    "decision_ref",
    "review_result_refs",
    "summary",
    "blocking_issues_count",
    "next_gate_status",
    "created_at",
}
REF_FIELDS = {"path", "sha256"}
GATE_STATUSES = {
    "accepted",
    "needs_revision",
    "blocked",
    "skipped",
    "pending_user_confirmation",
}
NEXT_GATE_BY_STATUS = {
    "accepted": "can_continue",
    "skipped": "can_continue",
    "needs_revision": "needs_revision",
    "blocked": "blocked",
    "pending_user_confirmation": "pending_user_confirmation",
}
DEFAULT_SUMMARY_BY_STATUS = {
    "accepted": "Stage gate accepted.",
    "skipped": "Stage gate skipped by explicit user decision.",
    "needs_revision": "Stage gate requires revision.",
    "blocked": "Stage gate is blocked.",
    "pending_user_confirmation": "Stage gate is pending user confirmation.",
}


class StageGateResultError(ValueError):
    """Raised when StageGateResult metadata is invalid or cannot be built."""


def stage_gate_result_path(run_dir: Path | str, stage: str) -> Path:
    return Path(run_dir) / "orchestration" / "stage_gate_results" / f"{stage}.json"


def build_stage_gate_result(
    run_dir: Path | str,
    stage: str,
    decision_path: Path | str | None = None,
    review_result_paths: list[Path | str] | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    run_dir = Path(run_dir).expanduser().resolve()
    validate_stage_or_raise(stage)
    run_id = run_dir.name
    validate_run_id(run_id)

    decision_payload: dict[str, Any] | None = None
    decision_ref: dict[str, str] | None = None
    if decision_path is not None:
        resolved_decision = resolve_run_path(run_dir, decision_path)
        decision_ref = build_ref(run_dir, resolved_decision)
        decision_payload = load_json(resolved_decision)

    final_status = status or status_from_decision(decision_payload)
    validate_gate_status_value(final_status)

    review_refs = []
    blocking_issues_count = 0
    for review_result_path in review_result_paths or []:
        resolved_review = resolve_run_path(run_dir, review_result_path)
        review_payload = validate_review_result_or_raise(
            load_json(resolved_review),
            run_dir=run_dir,
        )
        if review_payload["stage"] != stage:
            raise StageGateResultError("ReviewResult stage must match stage gate")
        blocking_issues_count += review_payload["blocking_issues_count"]
        review_refs.append(build_ref(run_dir, resolved_review))

    summary = summary_from_decision(decision_payload, final_status)
    payload: dict[str, Any] = {
        "kind": "stage_gate_result",
        "schema_version": 1,
        "run_id": run_id,
        "stage": stage,
        "status": final_status,
        "decision_ref": decision_ref,
        "review_result_refs": review_refs,
        "summary": summary,
        "blocking_issues_count": blocking_issues_count,
        "next_gate_status": NEXT_GATE_BY_STATUS[final_status],
        "created_at": utc_now(),
    }
    validate_stage_gate_result(payload, run_dir=run_dir)

    write_json(stage_gate_result_path(run_dir, stage), payload)
    return payload


def validate_stage_gate_result(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StageGateResultError("stage gate result payload must be a JSON object")

    validate_exact_fields(payload, RESULT_FIELDS)
    validate_literal(payload["kind"], "stage_gate_result", "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_stage_or_raise(payload["stage"])
    validate_gate_status_value(payload["status"])
    validate_summary_or_raise(payload["summary"])
    validate_blocking_issues_count_or_raise(payload["blocking_issues_count"])
    validate_timestamp(payload["created_at"], "created_at")
    validate_next_gate_status(payload["status"], payload["next_gate_status"])
    decision_ref = validate_ref_or_none(payload["decision_ref"], "decision_ref")
    review_result_refs = validate_ref_list(payload["review_result_refs"], "review_result_refs")

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise StageGateResultError("run_id must match run_dir name")
        if decision_ref is not None:
            validate_ref_file(decision_ref, run_root)
            decision_payload = load_json(run_root / decision_ref["path"])
            validate_decision_matches_status(decision_payload, payload["stage"], payload["status"])
            validate_decision_issue_binding(decision_payload, run_root, payload["stage"])
        for item in review_result_refs:
            validate_ref_file(item, run_root)
            review_payload = validate_review_result_or_raise(
                load_json(run_root / item["path"]),
                run_dir=run_root,
            )
            if review_payload["stage"] != payload["stage"]:
                raise StageGateResultError("ReviewResult stage must match stage gate")

    return payload


def status_from_decision(decision_payload: dict[str, Any] | None) -> str:
    if decision_payload is None:
        return "pending_user_confirmation"
    decision = decision_payload.get("decision")
    if isinstance(decision, str) and decision in GATE_STATUSES:
        return decision
    raise StageGateResultError("decision.json must contain a valid decision")


def summary_from_decision(decision_payload: dict[str, Any] | None, status: str) -> str:
    notes = decision_payload.get("notes") if decision_payload else None
    if isinstance(notes, str) and notes.strip():
        summary = notes.strip()
    else:
        summary = DEFAULT_SUMMARY_BY_STATUS[status]
    validate_summary_or_raise(summary)
    return summary


def validate_decision_matches_status(
    decision_payload: dict[str, Any],
    stage: str,
    status: str,
) -> None:
    if "stage" in decision_payload and decision_payload["stage"] != stage:
        raise StageGateResultError("decision stage must match stage gate")
    if "decision" in decision_payload and decision_payload["decision"] != status:
        raise StageGateResultError("decision must match stage gate status")


def validate_decision_issue_binding(
    decision_payload: dict[str, Any],
    run_dir: Path,
    stage: str,
) -> None:
    if decision_payload.get("professional_approval") is True:
        raise StageGateResultError("professional_approval must not be true")

    decision_scope = decision_payload.get("decision_scope")
    if decision_scope is not None and decision_scope != "stage_review_gate_only":
        raise StageGateResultError("decision_scope must be stage_review_gate_only")

    expected_path = f"stage_reviews/{stage}/issues_index.json"
    index_path = issues_index_path(run_dir, stage)
    if index_path.is_file():
        issues_index_ref = decision_payload.get("issues_index_ref")
        if issues_index_ref is None:
            raise StageGateResultError("decision must include issues_index_ref")
        ref = validate_ref(issues_index_ref, "issues_index_ref")
        if ref["path"] != expected_path:
            raise StageGateResultError("issues_index_ref path must match stage issues_index")
        validate_ref_file(ref, run_dir)
        validate_issues_index_or_raise(load_json(index_path), run_dir=run_dir)
    elif "issues_index_ref" in decision_payload:
        ref = validate_ref(decision_payload["issues_index_ref"], "issues_index_ref")
        validate_ref_file(ref, run_dir)


def validate_ref_list(value: Any, field: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise StageGateResultError(f"{field} must be a list")
    refs: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for item in value:
        ref = validate_ref(item, field)
        if ref["path"] in seen_paths:
            raise StageGateResultError(f"{field} must not contain duplicate paths")
        seen_paths.add(ref["path"])
        refs.append(ref)
    return refs


def validate_ref_or_none(value: Any, field: str) -> dict[str, str] | None:
    if value is None:
        return None
    return validate_ref(value, field)


def validate_ref(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise StageGateResultError(f"{field} must be an object")
    validate_exact_fields(value, REF_FIELDS)
    path = value["path"]
    digest = value["sha256"]
    if not isinstance(path, str):
        raise StageGateResultError(f"{field} path must be a string")
    validate_run_relative_path(path)
    if not isinstance(digest, str) or not SHA256_RE.match(digest):
        raise StageGateResultError(f"invalid sha256 for {path}")
    return {"path": path, "sha256": digest}


def build_ref(run_dir: Path, path_value: Path | str) -> dict[str, str]:
    relative_path, absolute_path = normalize_run_path(run_dir, path_value)
    if not absolute_path.is_file():
        raise StageGateResultError(f"ref path does not exist: {relative_path}")
    return {"path": relative_path, "sha256": file_sha256(absolute_path)}


def normalize_run_path(run_dir: Path, path_value: Path | str) -> tuple[str, Path]:
    root = run_dir.expanduser().resolve()
    raw_path = Path(path_value)
    if raw_path.is_absolute():
        absolute_path = raw_path.expanduser().resolve()
        if not absolute_path.is_relative_to(root):
            raise StageGateResultError(f"ref path escapes run_dir: {path_value}")
        relative_path = absolute_path.relative_to(root).as_posix()
    else:
        relative_path = str(path_value)
        validate_run_relative_path(relative_path)
        absolute_path = (root / relative_path).resolve()
        if not absolute_path.is_relative_to(root):
            raise StageGateResultError(f"ref path escapes run_dir: {relative_path}")
    validate_run_relative_path(relative_path)
    return relative_path, absolute_path


def resolve_run_path(run_dir: Path, path_value: Path | str) -> Path:
    relative_path, absolute_path = normalize_run_path(run_dir, path_value)
    if not absolute_path.is_file():
        raise StageGateResultError(f"run path does not exist: {relative_path}")
    return absolute_path


def validate_ref_file(ref: dict[str, str], run_dir: Path) -> None:
    relative_path, absolute_path = normalize_run_path(run_dir, ref["path"])
    if relative_path != ref["path"]:
        raise StageGateResultError("ref path must be run-relative")
    if not absolute_path.is_file():
        raise StageGateResultError(f"ref path does not exist: {ref['path']}")
    digest = file_sha256(absolute_path)
    if digest != ref["sha256"]:
        raise StageGateResultError(f"sha256 mismatch for {ref['path']}")


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise StageGateResultError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise StageGateResultError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise StageGateResultError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise StageGateResultError("run_id must be a safe non-empty run id")


def validate_stage_or_raise(value: Any) -> None:
    if not isinstance(value, str) or value not in STAGES:
        raise StageGateResultError(f"invalid stage: {value!r}")
    try:
        validate_stage(value)
    except ShortResultError as exc:
        raise StageGateResultError(str(exc)) from exc


def validate_gate_status_value(value: Any) -> None:
    if not isinstance(value, str) or value not in GATE_STATUSES:
        raise StageGateResultError(f"invalid status: {value!r}")


def validate_next_gate_status(status: str, value: Any) -> None:
    expected = NEXT_GATE_BY_STATUS[status]
    if value != expected:
        raise StageGateResultError(
            f"next_gate_status must be {expected!r} when status is {status!r}"
        )


def validate_summary_or_raise(value: Any) -> None:
    try:
        validate_summary(value)
    except ShortResultError as exc:
        raise StageGateResultError(str(exc)) from exc


def validate_blocking_issues_count_or_raise(value: Any) -> None:
    try:
        validate_blocking_issues_count(value)
    except ShortResultError as exc:
        raise StageGateResultError(str(exc)) from exc


def validate_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise StageGateResultError(f"{field} must be a non-empty string")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise StageGateResultError(f"{field} must be an ISO 8601 timestamp") from exc


def validate_run_relative_path(path: str) -> None:
    try:
        validate_result_path(path)
    except ShortResultError as exc:
        raise StageGateResultError(str(exc)) from exc


def validate_review_result_or_raise(payload: dict[str, Any], run_dir: Path | str) -> dict[str, Any]:
    try:
        return validate_review_result(payload, run_dir=run_dir)
    except ShortResultError as exc:
        raise StageGateResultError(str(exc)) from exc


def validate_issues_index_or_raise(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    try:
        return validate_issues_index(payload, run_dir=run_dir)
    except StageReviewIssueError as exc:
        raise StageGateResultError(str(exc)) from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise StageGateResultError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise StageGateResultError(f"JSON file must contain an object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
