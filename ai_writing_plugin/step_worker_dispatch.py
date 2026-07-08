from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context_packages import (
    ContextPackageError,
    build_step_context_package,
    context_package_path,
    expected_result_paths,
    validate_step_context_package,
)
from .progress_ledger import (
    ProgressLedgerError,
    build_ref,
    progress_ledger_path,
    record_step_progress,
    validate_progress_ledger,
)
from .short_results import (
    RESULT_STATUSES,
    RUN_ID_RE,
    SHA256_RE,
    ShortResultError,
    validate_result_path,
    validate_review_result,
    validate_step_result,
)


PILOT_STAGE = "ingest"
PILOT_STEPS = {
    "step-input-materials",
    "step-material-inventory",
    "step-source-index",
}
DISPATCH_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "step",
    "created_at",
    "context_package_ref",
    "progress_ledger_ref",
    "result_paths",
    "constraints",
}
REF_FIELDS = {"path", "sha256"}
RESULT_PATH_FIELDS = {"step_result", "review_result"}
FIXED_CONSTRAINTS = {
    "package_path_only": True,
    "worker_reads_refs": True,
    "main_agent_reads_short_results_only": True,
    "no_artifact_body": True,
}


class StepWorkerDispatchError(ValueError):
    """Raised when StepWorkerDispatch metadata is invalid or cannot be updated."""


def step_worker_dispatch_path(run_dir: Path | str, stage: str, step: str) -> Path:
    return Path(run_dir) / "orchestration" / "worker_dispatches" / stage / f"{step}.json"


def prepare_step_worker_dispatch(
    repo_root: Path | str,
    run_dir: Path | str,
    stage: str,
    step: str,
    task_type: str,
    input_refs: list[str] | None = None,
    overwrite_package: bool = False,
    overwrite_dispatch: bool = False,
) -> dict[str, Any]:
    repo_root = Path(repo_root).expanduser().resolve()
    run_dir = Path(run_dir).expanduser().resolve()
    validate_pilot_scope(stage, step)
    run_id = run_dir.name
    validate_run_id(run_id)

    dispatch_path = step_worker_dispatch_path(run_dir, stage, step)
    if dispatch_path.exists() and not overwrite_dispatch:
        raise StepWorkerDispatchError(f"step worker dispatch already exists: {dispatch_path}")

    ledger_path = progress_ledger_path(run_dir)
    if not ledger_path.is_file():
        raise StepWorkerDispatchError(f"progress ledger does not exist: {ledger_path}")
    validate_progress_ledger(load_json(ledger_path), run_dir=run_dir)

    package_path = context_package_path(run_dir, stage, step)
    if package_path.exists() and not overwrite_package:
        package_payload = load_json(package_path)
        validate_step_context_package(package_payload, repo_root=repo_root, run_dir=run_dir)
    else:
        build_step_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage=stage,
            step=step,
            task_type=task_type,
            input_refs=input_refs,
            overwrite=overwrite_package,
        )

    record_step_progress(
        run_dir=run_dir,
        stage=stage,
        step=step,
        status="context_ready",
        context_package=package_path,
    )

    payload: dict[str, Any] = {
        "kind": "step_worker_dispatch",
        "schema_version": 1,
        "run_id": run_id,
        "stage": stage,
        "step": step,
        "created_at": utc_now(),
        "context_package_ref": build_ref_or_raise(run_dir, package_path),
        "progress_ledger_ref": build_ref_or_raise(run_dir, ledger_path),
        "result_paths": expected_result_paths(stage, step),
        "constraints": dict(FIXED_CONSTRAINTS),
    }
    validate_step_worker_dispatch(payload, repo_root=repo_root, run_dir=run_dir)

    dispatch_path.parent.mkdir(parents=True, exist_ok=True)
    dispatch_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def complete_step_worker_dispatch(
    run_dir: Path | str,
    stage: str,
    step: str,
    step_result: Path | str,
    review_result: Path | str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    run_dir = Path(run_dir).expanduser().resolve()
    validate_pilot_scope(stage, step)

    dispatch_path = step_worker_dispatch_path(run_dir, stage, step)
    if not dispatch_path.is_file():
        raise StepWorkerDispatchError(f"step worker dispatch does not exist: {dispatch_path}")
    validate_step_worker_dispatch(load_json(dispatch_path), run_dir=run_dir)

    step_result_path = resolve_run_path(run_dir, step_result)
    step_payload = validate_step_result(load_json(step_result_path), run_dir=run_dir)
    if step_payload["stage"] != stage or step_payload["step"] != step:
        raise StepWorkerDispatchError("StepResult stage and step must match dispatch")

    final_status = status or step_payload["status"]
    review_result_path: Path | None = None
    if review_result is not None:
        review_result_path = resolve_run_path(run_dir, review_result)
        review_payload = validate_review_result(load_json(review_result_path), run_dir=run_dir)
        if review_payload["stage"] != stage or review_payload["step"] != step:
            raise StepWorkerDispatchError("ReviewResult stage and step must match dispatch")
        if status is None:
            final_status = review_payload["status"]

    validate_completion_status(final_status)
    try:
        ledger = record_step_progress(
            run_dir=run_dir,
            stage=stage,
            step=step,
            status=final_status,
            step_result=step_result_path,
            review_result=review_result_path,
        )
    except ProgressLedgerError as exc:
        raise StepWorkerDispatchError(str(exc)) from exc
    dispatch_payload = load_json(dispatch_path)
    dispatch_payload["progress_ledger_ref"] = build_ref_or_raise(
        run_dir,
        progress_ledger_path(run_dir),
    )
    validate_step_worker_dispatch(dispatch_payload, run_dir=run_dir)
    write_json(dispatch_path, dispatch_payload)
    return ledger


def validate_step_worker_dispatch(
    payload: dict[str, Any],
    repo_root: Path | str | None = None,
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StepWorkerDispatchError("step worker dispatch payload must be a JSON object")

    validate_exact_fields(payload, DISPATCH_FIELDS)
    validate_literal(payload["kind"], "step_worker_dispatch", "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_pilot_scope(payload["stage"], payload["step"])
    validate_timestamp(payload["created_at"], "created_at")
    context_package_ref = validate_ref(payload["context_package_ref"], "context_package_ref")
    progress_ledger_ref = validate_ref(payload["progress_ledger_ref"], "progress_ledger_ref")
    validate_result_paths(payload["result_paths"], payload["stage"], payload["step"])
    validate_constraints(payload["constraints"])

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise StepWorkerDispatchError("run_id must match run_dir name")
        validate_ref_file(context_package_ref, run_root)
        validate_context_package_ref(context_package_ref, repo_root=repo_root, run_dir=run_root)
        validate_ref_file(progress_ledger_ref, run_root)
        validate_progress_ledger_ref(progress_ledger_ref, run_root)

    return payload


def validate_pilot_scope(stage: Any, step: Any) -> None:
    if stage != PILOT_STAGE or step not in PILOT_STEPS:
        raise StepWorkerDispatchError(
            "ingest worker pilot only supports stage='ingest' and steps "
            "step-input-materials, step-material-inventory, step-source-index"
        )


def validate_ref(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise StepWorkerDispatchError(f"{field} must be an object")
    validate_exact_fields(value, REF_FIELDS)
    path = value["path"]
    digest = value["sha256"]
    if not isinstance(path, str):
        raise StepWorkerDispatchError(f"{field} path must be a string")
    validate_run_relative_path(path)
    if not isinstance(digest, str) or not SHA256_RE.match(digest):
        raise StepWorkerDispatchError(f"invalid sha256 for {path}")
    return {"path": path, "sha256": digest}


def validate_ref_file(ref: dict[str, str], run_dir: Path) -> None:
    candidate = resolve_run_path(run_dir, ref["path"])
    digest = file_sha256(candidate)
    if digest != ref["sha256"]:
        raise StepWorkerDispatchError(f"sha256 mismatch for {ref['path']}")


def validate_context_package_ref(
    ref: dict[str, str],
    *,
    repo_root: Path | str | None,
    run_dir: Path,
) -> dict[str, Any]:
    try:
        return validate_step_context_package(
            load_json(run_dir / ref["path"]),
            repo_root=Path(repo_root) if repo_root else None,
            run_dir=run_dir,
        )
    except ContextPackageError as exc:
        raise StepWorkerDispatchError(str(exc)) from exc


def validate_progress_ledger_ref(ref: dict[str, str], run_dir: Path) -> dict[str, Any]:
    try:
        return validate_progress_ledger(load_json(run_dir / ref["path"]), run_dir=run_dir)
    except ProgressLedgerError as exc:
        raise StepWorkerDispatchError(str(exc)) from exc


def validate_result_paths(value: Any, stage: str, step: str) -> None:
    if not isinstance(value, dict) or set(value) != RESULT_PATH_FIELDS:
        raise StepWorkerDispatchError("result_paths must contain step_result and review_result")
    expected = expected_result_paths(stage, step)
    if value != expected:
        raise StepWorkerDispatchError("result_paths must match the stage and step")
    for path in value.values():
        validate_run_relative_path(path)


def validate_constraints(value: Any) -> None:
    if value != FIXED_CONSTRAINTS:
        raise StepWorkerDispatchError("constraints must declare the fixed worker boundary")


def validate_completion_status(value: Any) -> None:
    if not isinstance(value, str) or value not in RESULT_STATUSES:
        raise StepWorkerDispatchError(f"invalid completion status: {value!r}")


def build_ref_or_raise(run_dir: Path, path: Path | str) -> dict[str, str]:
    try:
        return build_ref(run_dir, path)
    except ProgressLedgerError as exc:
        raise StepWorkerDispatchError(str(exc)) from exc


def resolve_run_path(run_dir: Path, path_value: Path | str) -> Path:
    root = run_dir.expanduser().resolve()
    raw_path = Path(path_value)
    if raw_path.is_absolute():
        candidate = raw_path.expanduser().resolve()
        if not candidate.is_relative_to(root):
            raise StepWorkerDispatchError(f"run path escapes run_dir: {path_value}")
    else:
        validate_run_relative_path(str(path_value))
        candidate = (root / str(path_value)).resolve()
        if not candidate.is_relative_to(root):
            raise StepWorkerDispatchError(f"run path escapes run_dir: {path_value}")
    if not candidate.is_file():
        relative = candidate.relative_to(root).as_posix() if candidate.is_relative_to(root) else str(path_value)
        raise StepWorkerDispatchError(f"run path does not exist: {relative}")
    return candidate


def validate_run_relative_path(path: str) -> None:
    try:
        validate_result_path(path)
    except ShortResultError as exc:
        raise StepWorkerDispatchError(str(exc)) from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise StepWorkerDispatchError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise StepWorkerDispatchError(f"JSON file must contain an object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise StepWorkerDispatchError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise StepWorkerDispatchError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise StepWorkerDispatchError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise StepWorkerDispatchError("run_id must be a safe non-empty run id")


def validate_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise StepWorkerDispatchError(f"{field} must be a non-empty string")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise StepWorkerDispatchError(f"{field} must be an ISO 8601 timestamp") from exc


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
