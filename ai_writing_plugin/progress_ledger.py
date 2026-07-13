from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context_packages import ContextPackageError, validate_step_context_package
from .short_results import (
    RUN_ID_RE,
    SHA256_RE,
    STAGES,
    STEPS,
    ShortResultError,
    validate_blocking_issues_count,
    validate_files_and_hashes,
    validate_gate_status,
    validate_result_path,
    validate_review_result,
    validate_stage,
    validate_step,
    validate_step_result,
)


LEDGER_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "created_at",
    "updated_at",
    "entries",
}
ENTRY_FIELDS = {
    "stage",
    "step",
    "status",
    "updated_at",
    "context_package_ref",
    "step_result_ref",
    "review_result_ref",
    "blocking_issues_count",
    "next_gate_status",
}
REF_FIELDS = {"path", "sha256"}
LEDGER_STATUSES = {
    "not_started",
    "context_ready",
    "running",
    "done",
    "needs_revision",
    "blocked",
    "skipped",
}


class ProgressLedgerError(ValueError):
    """Raised when ProgressLedger metadata is invalid or cannot be updated."""


def progress_ledger_path(run_dir: Path | str) -> Path:
    return Path(run_dir) / "orchestration" / "progress_ledger.json"


def init_progress_ledger(run_dir: Path | str, overwrite: bool = False) -> dict[str, Any]:
    run_dir = Path(run_dir).expanduser().resolve()
    run_id = run_dir.name
    validate_run_id(run_id)

    path = progress_ledger_path(run_dir)
    if path.exists() and not overwrite:
        raise ProgressLedgerError(f"progress ledger already exists: {path}")

    now = utc_now()
    payload: dict[str, Any] = {
        "kind": "progress_ledger",
        "schema_version": 1,
        "run_id": run_id,
        "created_at": now,
        "updated_at": now,
        "entries": [],
    }
    validate_progress_ledger(payload, run_dir=run_dir)
    write_ledger(path, payload)
    return payload


def record_step_progress(
    run_dir: Path | str,
    stage: str,
    step: str,
    status: str,
    context_package: Path | str | None = None,
    step_result: Path | str | None = None,
    review_result: Path | str | None = None,
) -> dict[str, Any]:
    run_dir = Path(run_dir).expanduser().resolve()
    path = progress_ledger_path(run_dir)
    if not path.is_file():
        raise ProgressLedgerError(f"progress ledger does not exist: {path}")

    payload = load_ledger(path)
    validate_progress_ledger(payload, run_dir=run_dir)
    validate_stage_or_raise(stage)
    validate_step_or_raise(step)
    validate_ledger_status(status)

    existing = find_entry(payload["entries"], stage, step)
    entry = dict(existing) if existing else default_entry(stage, step)
    target_run_id = run_dir.name
    authoritative_result: dict[str, Any] | None = None
    authoritative_kind: str | None = None

    if context_package is not None:
        entry["context_package_ref"] = build_ref(run_dir, context_package)
        validate_canonical_entry_ref_paths(entry, stage, step)
        validate_context_package_target(
            entry["context_package_ref"],
            run_dir,
            run_id=target_run_id,
            stage=stage,
            step=step,
            target_label="ledger target",
        )
    if step_result is not None:
        entry["step_result_ref"] = build_ref(run_dir, step_result)
        validate_canonical_entry_ref_paths(entry, stage, step)
        step_payload = validate_step_result_ref(entry["step_result_ref"], run_dir)
        validate_metadata_target(
            step_payload,
            run_id=target_run_id,
            stage=stage,
            step=step,
            kind="StepResult",
            target_label="ledger target",
        )
        authoritative_result = step_payload
        authoritative_kind = "StepResult"
    if review_result is not None:
        entry["review_result_ref"] = build_ref(run_dir, review_result)
        validate_canonical_entry_ref_paths(entry, stage, step)
        review_payload = validate_review_result_ref(entry["review_result_ref"], run_dir)
        validate_metadata_target(
            review_payload,
            run_id=target_run_id,
            stage=stage,
            step=step,
            kind="ReviewResult",
            target_label="ledger target",
        )
        authoritative_result = review_payload
        authoritative_kind = "ReviewResult"

    if authoritative_result is None:
        if entry["review_result_ref"] is not None:
            authoritative_result = validate_review_result_ref(
                entry["review_result_ref"], run_dir
            )
            authoritative_kind = "ReviewResult"
        elif entry["step_result_ref"] is not None:
            authoritative_result = validate_step_result_ref(entry["step_result_ref"], run_dir)
            authoritative_kind = "StepResult"

    if authoritative_result is not None:
        validate_metadata_target(
            authoritative_result,
            run_id=target_run_id,
            stage=stage,
            step=step,
            kind=authoritative_kind or "result",
            target_label="ledger target",
        )
        if status != authoritative_result["status"]:
            raise ProgressLedgerError(
                f"status must match authoritative {authoritative_kind}"
            )
        entry["blocking_issues_count"] = authoritative_result["blocking_issues_count"]
        entry["next_gate_status"] = authoritative_result["next_gate_status"]

    now = utc_now()
    entry["status"] = status
    entry["updated_at"] = now
    upsert_entry(payload["entries"], entry)
    payload["updated_at"] = now

    validate_progress_ledger(payload, run_dir=run_dir)
    write_ledger(path, payload)
    return payload


def reset_step_for_redispatch(
    run_dir: Path | str,
    stage: str,
    step: str,
    context_package: Path | str,
    *,
    validated_ledger: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Reset one completed step before its original worker is dispatched again."""
    run_dir = Path(run_dir).expanduser().resolve()
    path = progress_ledger_path(run_dir)
    if not path.is_file():
        raise ProgressLedgerError(f"progress ledger does not exist: {path}")

    if validated_ledger is None:
        payload = load_ledger(path)
        validate_progress_ledger(payload, run_dir=run_dir)
    else:
        payload = deepcopy(validated_ledger)

    validate_stage_or_raise(stage)
    validate_step_or_raise(step)
    existing = find_entry(payload["entries"], stage, step)
    if existing is None:
        raise ProgressLedgerError(f"ledger entry does not exist: {stage}/{step}")

    now = utc_now()
    entry = dict(existing)
    entry["status"] = "context_ready"
    entry["updated_at"] = now
    entry["context_package_ref"] = build_ref(run_dir, context_package)
    validate_context_package_ref(entry["context_package_ref"], run_dir)
    entry["step_result_ref"] = None
    entry["review_result_ref"] = None
    entry["blocking_issues_count"] = 0
    entry["next_gate_status"] = "not_recorded"
    upsert_entry(payload["entries"], entry)
    payload["updated_at"] = now

    validate_progress_ledger(payload, run_dir=run_dir)
    write_ledger(path, payload)
    return payload


def validate_progress_ledger(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProgressLedgerError("progress ledger payload must be a JSON object")

    validate_exact_fields(payload, LEDGER_FIELDS)
    validate_literal(payload["kind"], "progress_ledger", "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_timestamp(payload["created_at"], "created_at")
    validate_timestamp(payload["updated_at"], "updated_at")

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise ProgressLedgerError("run_id must match run_dir name")
    else:
        run_root = None

    entries = payload["entries"]
    if not isinstance(entries, list):
        raise ProgressLedgerError("entries must be a list")

    seen: set[tuple[str, str]] = set()
    for entry in entries:
        validate_entry(entry, run_root, payload["run_id"])
        key = (entry["stage"], entry["step"])
        if key in seen:
            raise ProgressLedgerError(f"duplicate ledger entry: {key[0]}/{key[1]}")
        seen.add(key)

    return payload


def default_entry(stage: str, step: str) -> dict[str, Any]:
    now = utc_now()
    return {
        "stage": stage,
        "step": step,
        "status": "not_started",
        "updated_at": now,
        "context_package_ref": None,
        "step_result_ref": None,
        "review_result_ref": None,
        "blocking_issues_count": 0,
        "next_gate_status": "not_recorded",
    }


def find_entry(entries: list[dict[str, Any]], stage: str, step: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry["stage"] == stage and entry["step"] == step:
            return entry
    return None


def upsert_entry(entries: list[dict[str, Any]], entry: dict[str, Any]) -> None:
    for index, existing in enumerate(entries):
        if existing["stage"] == entry["stage"] and existing["step"] == entry["step"]:
            entries[index] = entry
            return
    entries.append(entry)


def validate_entry(entry: Any, run_dir: Path | None, run_id: str) -> None:
    if not isinstance(entry, dict):
        raise ProgressLedgerError("entries must contain objects")

    validate_exact_fields(entry, ENTRY_FIELDS)
    validate_stage_or_raise(entry["stage"])
    validate_step_or_raise(entry["step"])
    validate_ledger_status(entry["status"])
    validate_timestamp(entry["updated_at"], "updated_at")
    validate_blocking_issues_or_raise(entry["blocking_issues_count"])
    validate_gate_status_or_raise(entry["next_gate_status"])

    context_package_ref = validate_ref_or_none(entry["context_package_ref"], "context_package_ref")
    step_result_ref = validate_ref_or_none(entry["step_result_ref"], "step_result_ref")
    review_result_ref = validate_ref_or_none(entry["review_result_ref"], "review_result_ref")
    validate_canonical_entry_ref_paths(entry, entry["stage"], entry["step"])

    if run_dir is not None:
        step_payload: dict[str, Any] | None = None
        review_payload: dict[str, Any] | None = None
        if context_package_ref is not None:
            validate_ref_file(context_package_ref, run_dir)
            validate_context_package_target(
                context_package_ref,
                run_dir,
                run_id=run_id,
                stage=entry["stage"],
                step=entry["step"],
                target_label="ledger entry",
            )
        if step_result_ref is not None:
            validate_ref_file(step_result_ref, run_dir)
            step_payload = validate_step_result_ref(step_result_ref, run_dir)
            validate_metadata_target(
                step_payload,
                run_id=run_id,
                stage=entry["stage"],
                step=entry["step"],
                kind="StepResult",
                target_label="ledger entry",
            )
        if review_result_ref is not None:
            validate_ref_file(review_result_ref, run_dir)
            review_payload = validate_review_result_ref(review_result_ref, run_dir)
            validate_metadata_target(
                review_payload,
                run_id=run_id,
                stage=entry["stage"],
                step=entry["step"],
                kind="ReviewResult",
                target_label="ledger entry",
            )

        authoritative_result = review_payload or step_payload
        if authoritative_result is not None:
            authoritative_kind = "ReviewResult" if review_payload is not None else "StepResult"
            validate_authoritative_entry_fields(
                entry,
                authoritative_result,
                authoritative_kind,
            )


def validate_canonical_entry_ref_paths(
    entry: dict[str, Any],
    stage: str,
    step: str,
) -> None:
    expected_paths = {
        "context_package_ref": f"orchestration/context_packages/{stage}/{step}.json",
        "step_result_ref": f"orchestration/step_results/{step}.json",
        "review_result_ref": f"orchestration/review_results/{stage}/{step}.json",
    }
    for field, expected_path in expected_paths.items():
        ref = entry[field]
        if ref is not None and ref["path"] != expected_path:
            raise ProgressLedgerError(
                f"{field} must use the canonical path for {stage}/{step}"
            )


def validate_metadata_target(
    payload: dict[str, Any],
    *,
    run_id: str,
    stage: str,
    step: str,
    kind: str,
    target_label: str,
) -> None:
    if payload["run_id"] != run_id:
        raise ProgressLedgerError(f"{kind} run_id must match {target_label}")
    if payload["stage"] != stage or payload["step"] != step:
        raise ProgressLedgerError(f"{kind} stage and step must match {target_label}")


def validate_authoritative_entry_fields(
    entry: dict[str, Any],
    authoritative_result: dict[str, Any],
    authoritative_kind: str,
) -> None:
    for field in ("status", "blocking_issues_count", "next_gate_status"):
        if entry[field] != authoritative_result[field]:
            raise ProgressLedgerError(
                f"{field} must match authoritative {authoritative_kind}"
            )


def validate_ref_or_none(value: Any, field: str) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ProgressLedgerError(f"{field} must be null or an object")
    validate_exact_fields(value, REF_FIELDS)
    path = value["path"]
    digest = value["sha256"]
    if not isinstance(path, str):
        raise ProgressLedgerError(f"{field} path must be a string")
    validate_run_relative_path(path)
    if not isinstance(digest, str) or not SHA256_RE.match(digest):
        raise ProgressLedgerError(f"invalid sha256 for {path}")
    return {"path": path, "sha256": digest}


def build_ref(run_dir: Path, path_value: Path | str) -> dict[str, str]:
    relative_path, absolute_path = normalize_run_path(run_dir, path_value)
    if not absolute_path.is_file():
        raise ProgressLedgerError(f"ref path does not exist: {relative_path}")
    return {"path": relative_path, "sha256": file_sha256(absolute_path)}


def normalize_run_path(run_dir: Path, path_value: Path | str) -> tuple[str, Path]:
    root = run_dir.expanduser().resolve()
    raw_path = Path(path_value)
    if raw_path.is_absolute():
        absolute_path = raw_path.expanduser().resolve()
        if not absolute_path.is_relative_to(root):
            raise ProgressLedgerError(f"ref path escapes run_dir: {path_value}")
        relative_path = absolute_path.relative_to(root).as_posix()
    else:
        relative_path = str(path_value)
        validate_run_relative_path(relative_path)
        absolute_path = (root / relative_path).resolve()
        if not absolute_path.is_relative_to(root):
            raise ProgressLedgerError(f"ref path escapes run_dir: {relative_path}")

    validate_run_relative_path(relative_path)
    return relative_path, absolute_path


def validate_ref_file(ref: dict[str, str], run_dir: Path) -> None:
    relative_path, absolute_path = normalize_run_path(run_dir, ref["path"])
    if relative_path != ref["path"]:
        raise ProgressLedgerError("ref path must be run-relative")
    if not absolute_path.is_file():
        raise ProgressLedgerError(f"ref path does not exist: {ref['path']}")
    digest = file_sha256(absolute_path)
    if digest != ref["sha256"]:
        raise ProgressLedgerError(f"sha256 mismatch for {ref['path']}")


def validate_context_package_ref(ref: dict[str, str], run_dir: Path) -> dict[str, Any]:
    payload = load_json_for_ref(run_dir, ref["path"])
    try:
        return validate_step_context_package(payload, run_dir=run_dir)
    except ContextPackageError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def validate_context_package_target(
    ref: dict[str, str],
    run_dir: Path,
    *,
    run_id: str,
    stage: str,
    step: str,
    target_label: str,
) -> dict[str, Any]:
    raw_payload = load_json_for_ref(run_dir, ref["path"])
    if raw_payload.get("run_id") != run_id:
        raise ProgressLedgerError(
            f"context package run_id must match {target_label}"
        )
    if raw_payload.get("stage") != stage or raw_payload.get("step") != step:
        raise ProgressLedgerError(
            f"context package stage and step must match {target_label}"
        )
    return validate_context_package_ref(ref, run_dir)


def validate_step_result_ref(ref: dict[str, str], run_dir: Path) -> dict[str, Any]:
    payload = load_json_for_ref(run_dir, ref["path"])
    try:
        validate_step_result(payload)
        validate_files_and_hashes(
            payload["artifact_paths"], payload["artifact_hashes"], run_dir
        )
        return payload
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def validate_review_result_ref(ref: dict[str, str], run_dir: Path) -> dict[str, Any]:
    payload = load_json_for_ref(run_dir, ref["path"])
    try:
        validate_review_result(payload)
        validate_files_and_hashes(
            payload["review_package_paths"],
            payload["review_package_hashes"],
            run_dir,
        )
        return payload
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def load_json_for_ref(run_dir: Path, relative_path: str) -> dict[str, Any]:
    _, absolute_path = normalize_run_path(run_dir, relative_path)
    try:
        with absolute_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProgressLedgerError(f"invalid JSON ref {relative_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProgressLedgerError(f"JSON ref must be an object: {relative_path}")
    return payload


def load_ledger(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProgressLedgerError(f"invalid progress ledger: {exc}") from exc
    if not isinstance(payload, dict):
        raise ProgressLedgerError("progress ledger payload must be a JSON object")
    return payload


def write_ledger(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise ProgressLedgerError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise ProgressLedgerError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ProgressLedgerError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise ProgressLedgerError("run_id must be a safe non-empty run id")


def validate_stage_or_raise(value: Any) -> None:
    if not isinstance(value, str) or value not in STAGES:
        raise ProgressLedgerError(f"invalid stage: {value!r}")
    try:
        validate_stage(value)
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def validate_step_or_raise(value: Any) -> None:
    if not isinstance(value, str) or value not in STEPS:
        raise ProgressLedgerError(f"invalid step: {value!r}")
    try:
        validate_step(value)
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def validate_ledger_status(value: Any) -> None:
    if not isinstance(value, str) or value not in LEDGER_STATUSES:
        raise ProgressLedgerError(f"invalid status: {value!r}")


def validate_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ProgressLedgerError(f"{field} must be a non-empty string")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ProgressLedgerError(f"{field} must be an ISO 8601 timestamp") from exc


def validate_blocking_issues_or_raise(value: Any) -> None:
    try:
        validate_blocking_issues_count(value)
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def validate_gate_status_or_raise(value: Any) -> None:
    try:
        validate_gate_status(value)
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def validate_run_relative_path(path: str) -> None:
    try:
        validate_result_path(path)
    except ShortResultError as exc:
        raise ProgressLedgerError(str(exc)) from exc


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
