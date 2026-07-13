from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .context_packages import ContextPackageError, validate_step_context_package
from .progress_ledger import (
    ProgressLedgerError,
    progress_ledger_path,
    validate_progress_ledger,
)
from .short_results import (
    RUN_ID_RE,
    SHA256_RE,
    STAGES,
    STEPS,
    ShortResultError,
    validate_result_path,
    validate_stage,
    validate_step,
    validate_step_result,
)
from .stage_review_issues import (
    StageReviewIssueError,
    validate_issues_index,
)
from .step_worker_dispatch import (
    StepWorkerDispatchError,
    step_worker_dispatch_path,
    validate_step_worker_dispatch,
)


PACKAGE_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "steps",
    "created_at",
    "context_package_refs",
    "step_result_refs",
    "stage_review_refs",
    "result_paths",
    "constraints",
}
REF_FIELDS = {"path", "sha256"}
RESULT_PATH_FIELDS = {"stage_gate_result"}
FIXED_CONSTRAINTS = {
    "paths_and_hashes_only": True,
    "no_artifact_body": True,
    "no_inline_review_details": True,
    "main_agent_passes_package_path_only": True,
}
ALLOWED_STAGE_REVIEW_FILES = {
    "review_prompt.md",
    "review_units.json",
    "issues_schema.json",
    "review_context.json",
    "issues_index.json",
}
STAGE_REVIEW_FILE_ORDER = [
    "review_prompt.md",
    "review_units.json",
    "issues_schema.json",
    "review_context.json",
    "issues_index.json",
]


class ReviewContextPackageError(ValueError):
    """Raised when ReviewContextPackage metadata is invalid or cannot be built."""


def review_context_package_path(run_dir: Path | str, stage: str) -> Path:
    return Path(run_dir) / "orchestration" / "review_context_packages" / f"{stage}.json"


def build_review_context_package(
    repo_root: Path | str,
    run_dir: Path | str,
    stage: str,
    steps: list[str],
    overwrite: bool = False,
) -> dict[str, Any]:
    repo_root = Path(repo_root).expanduser().resolve()
    run_dir = Path(run_dir).expanduser().resolve()
    validate_stage_or_raise(stage)
    validate_steps(steps)
    run_id = run_dir.name
    validate_run_id(run_id)

    package_path = review_context_package_path(run_dir, stage)
    if package_path.exists() and not overwrite:
        raise ReviewContextPackageError(f"review context package already exists: {package_path}")

    context_package_refs = []
    step_result_refs = []
    context_payloads: dict[str, dict[str, Any]] = {}
    for step in steps:
        context_path = run_dir / expected_context_package_path(stage, step)
        if not context_path.is_file():
            raise ReviewContextPackageError(
                f"StepContextPackage does not exist: {expected_context_package_path(stage, step)}"
            )
        context_payload = validate_step_context_package_or_raise(
            load_json(context_path),
            repo_root=repo_root,
            run_dir=run_dir,
        )
        if (
            context_payload["run_id"] != run_id
            or context_payload["stage"] != stage
            or context_payload["step"] != step
        ):
            raise ReviewContextPackageError("StepContextPackage stage and step must match package")
        context_payloads[step] = context_payload
        context_package_refs.append(build_ref(run_dir, context_path))

        result_path = run_dir / expected_step_result_path(step)
        if not result_path.is_file():
            raise ReviewContextPackageError(
                f"StepResult does not exist: {expected_step_result_path(step)}"
            )
        step_payload = validate_step_result_or_raise(load_json(result_path), run_dir=run_dir)
        if step_payload["stage"] != stage or step_payload["step"] != step:
            raise ReviewContextPackageError("StepResult stage and step must match package")
        step_result_refs.append(build_ref(run_dir, result_path))

    if overwrite:
        return reset_review_cycle_transaction(
            repo_root=repo_root,
            run_dir=run_dir,
            run_id=run_id,
            stage=stage,
            steps=steps,
            package_path=package_path,
            context_payloads=context_payloads,
            step_result_refs=step_result_refs,
        )

    stage_review_refs = []
    for filename in STAGE_REVIEW_FILE_ORDER:
        relative_path = f"stage_reviews/{stage}/{filename}"
        candidate = run_dir / relative_path
        if candidate.is_file():
            stage_review_refs.append(build_ref(run_dir, candidate))

    payload: dict[str, Any] = {
        "kind": "review_context_package",
        "schema_version": 2,
        "run_id": run_id,
        "stage": stage,
        "steps": list(steps),
        "created_at": utc_now(),
        "context_package_refs": context_package_refs,
        "step_result_refs": step_result_refs,
        "stage_review_refs": stage_review_refs,
        "result_paths": expected_result_paths(stage),
        "constraints": dict(FIXED_CONSTRAINTS),
    }
    validate_review_context_package(payload, run_dir=run_dir)

    write_json(package_path, payload)
    return payload


def reset_review_cycle_transaction(
    *,
    repo_root: Path,
    run_dir: Path,
    run_id: str,
    stage: str,
    steps: list[str],
    package_path: Path,
    context_payloads: dict[str, dict[str, Any]],
    step_result_refs: list[dict[str, str]],
) -> dict[str, Any]:
    """Atomically start a new stage review cycle at the fixed metadata paths."""
    if package_path.is_file():
        existing_package = load_json(package_path)
        validate_review_context_package(existing_package)
        if (
            existing_package["run_id"] != run_id
            or existing_package["stage"] != stage
            or existing_package["steps"] != steps
        ):
            raise ReviewContextPackageError(
                "existing review context package must match run, stage, and requested steps"
            )

    ledger_path = progress_ledger_path(run_dir)
    if not ledger_path.is_file():
        raise ReviewContextPackageError(f"progress ledger does not exist: {ledger_path}")

    try:
        ledger_payload = load_json(ledger_path)
        validate_progress_ledger(ledger_payload, run_dir=run_dir)
    except ProgressLedgerError as exc:
        raise ReviewContextPackageError(str(exc)) from exc

    omitted_bound_steps = [
        entry["step"]
        for entry in ledger_payload["entries"]
        if entry["stage"] == stage
        and entry["step_result_ref"] is not None
        and entry["step"] not in steps
    ]
    if omitted_bound_steps:
        raise ReviewContextPackageError(
            "review cycle overwrite omits StepResult-bound stage entries: "
            f"{omitted_bound_steps}"
        )

    issue_index = run_dir / f"stage_reviews/{stage}/issues_index.json"
    if issue_index.is_file():
        validate_issues_index_or_raise(
            load_json(issue_index),
            run_dir=run_dir,
            validate_artifact_refs=False,
        )

    now = utc_now()
    context_candidates: dict[str, dict[str, Any]] = {}
    context_refs: dict[str, dict[str, str]] = {}
    dispatch_paths: dict[str, Path] = {}
    dispatch_candidates: dict[str, dict[str, Any]] = {}

    for step in steps:
        candidate = deepcopy(context_payloads[step])
        candidate["run_refs"] = [
            ref
            for ref in candidate["run_refs"]
            if not ref["path"].startswith(f"stage_reviews/{stage}/")
        ]
        if candidate != context_payloads[step]:
            candidate["created_at"] = now
        validate_step_context_package_or_raise(
            candidate,
            repo_root=repo_root,
            run_dir=run_dir,
        )
        context_candidates[step] = candidate
        context_refs[step] = payload_ref(
            run_dir,
            run_dir / expected_context_package_path(stage, step),
            candidate,
        )

        dispatch_path = step_worker_dispatch_path(run_dir, stage, step)
        if not dispatch_path.is_file():
            raise ReviewContextPackageError(
                f"step worker dispatch does not exist: {dispatch_path}"
            )
        try:
            dispatch_payload = load_json(dispatch_path)
            validate_step_worker_dispatch(
                dispatch_payload,
                repo_root=repo_root,
                run_dir=run_dir,
            )
        except StepWorkerDispatchError as exc:
            raise ReviewContextPackageError(str(exc)) from exc
        dispatch_candidate = deepcopy(dispatch_payload)
        dispatch_candidate["context_package_ref"] = context_refs[step]
        dispatch_paths[step] = dispatch_path
        dispatch_candidates[step] = dispatch_candidate

    ledger_candidate = deepcopy(ledger_payload)
    entries = {
        (entry["stage"], entry["step"]): entry
        for entry in ledger_candidate["entries"]
    }
    step_results = {
        step: ref for step, ref in zip(steps, step_result_refs, strict=True)
    }
    for step in steps:
        entry = entries.get((stage, step))
        if entry is None:
            raise ReviewContextPackageError(f"ledger entry does not exist: {stage}/{step}")
        if entry["step_result_ref"] is None:
            raise ReviewContextPackageError(
                f"step result is not bound in ledger: {stage}/{step}"
            )
        if entry["step_result_ref"] != step_results[step]:
            raise ReviewContextPackageError(
                f"ledger StepResult binding does not match current result: {stage}/{step}"
            )
        step_payload = validate_step_result_or_raise(
            load_json(run_dir / step_results[step]["path"]),
            run_dir=run_dir,
        )
        entry["status"] = step_payload["status"]
        entry["updated_at"] = now
        entry["context_package_ref"] = context_refs[step]
        entry["review_result_ref"] = None
        entry["blocking_issues_count"] = step_payload["blocking_issues_count"]
        entry["next_gate_status"] = step_payload["next_gate_status"]
    ledger_candidate["updated_at"] = now
    try:
        validate_progress_ledger(ledger_candidate)
    except ProgressLedgerError as exc:
        raise ReviewContextPackageError(str(exc)) from exc

    ledger_ref = payload_ref(run_dir, ledger_path, ledger_candidate)
    for step in steps:
        dispatch_candidates[step]["progress_ledger_ref"] = ledger_ref
        try:
            validate_step_worker_dispatch(dispatch_candidates[step])
        except StepWorkerDispatchError as exc:
            raise ReviewContextPackageError(str(exc)) from exc

    payload: dict[str, Any] = {
        "kind": "review_context_package",
        "schema_version": 2,
        "run_id": run_id,
        "stage": stage,
        "steps": list(steps),
        "created_at": now,
        "context_package_refs": [context_refs[step] for step in steps],
        "step_result_refs": step_result_refs,
        "stage_review_refs": [],
        "result_paths": expected_result_paths(stage),
        "constraints": dict(FIXED_CONSTRAINTS),
    }
    validate_review_context_package(payload)

    touched_paths = [
        *(run_dir / expected_context_package_path(stage, step) for step in steps),
        *(dispatch_paths[step] for step in steps),
        ledger_path,
        package_path,
    ]
    backups = {path: path.read_bytes() if path.exists() else None for path in touched_paths}

    try:
        for step in steps:
            write_json(
                run_dir / expected_context_package_path(stage, step),
                context_candidates[step],
            )
        write_json(ledger_path, ledger_candidate)
        for step in steps:
            write_json(dispatch_paths[step], dispatch_candidates[step])
        write_json(package_path, payload)

        for step in steps:
            validate_step_context_package_or_raise(
                load_json(run_dir / expected_context_package_path(stage, step)),
                repo_root=repo_root,
                run_dir=run_dir,
            )
            try:
                validate_step_worker_dispatch(
                    load_json(dispatch_paths[step]),
                    repo_root=repo_root,
                    run_dir=run_dir,
                )
            except StepWorkerDispatchError as exc:
                raise ReviewContextPackageError(str(exc)) from exc
        try:
            validate_progress_ledger(load_json(ledger_path), run_dir=run_dir)
        except ProgressLedgerError as exc:
            raise ReviewContextPackageError(str(exc)) from exc
        validate_review_context_package(payload, repo_root=repo_root, run_dir=run_dir)
    except Exception:
        for path, content in backups.items():
            restore_file(path, content)
        raise

    return payload


def validate_review_context_package(
    payload: dict[str, Any],
    repo_root: Path | str | None = None,
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    # repo_root is intentionally unused: review packages may only point into a run.
    if repo_root is not None:
        Path(repo_root).expanduser().resolve()
    if not isinstance(payload, dict):
        raise ReviewContextPackageError("review context package payload must be a JSON object")

    validate_exact_fields(payload, PACKAGE_FIELDS)
    validate_literal(payload["kind"], "review_context_package", "kind")
    validate_literal(payload["schema_version"], 2, "schema_version")
    validate_run_id(payload["run_id"])
    validate_stage_or_raise(payload["stage"])
    steps = validate_steps(payload["steps"])
    validate_timestamp(payload["created_at"], "created_at")
    context_package_refs = validate_ref_list(
        payload["context_package_refs"],
        "context_package_refs",
    )
    step_result_refs = validate_ref_list(payload["step_result_refs"], "step_result_refs")
    stage_review_refs = validate_ref_list(payload["stage_review_refs"], "stage_review_refs")
    validate_result_paths(payload["result_paths"], payload["stage"])
    validate_constraints(payload["constraints"])

    expected_context_paths = [
        expected_context_package_path(payload["stage"], step) for step in steps
    ]
    actual_context_paths = [item["path"] for item in context_package_refs]
    if actual_context_paths != expected_context_paths:
        raise ReviewContextPackageError("context_package_refs must match steps in order")

    expected_step_paths = [expected_step_result_path(step) for step in steps]
    actual_step_paths = [item["path"] for item in step_result_refs]
    if actual_step_paths != expected_step_paths:
        raise ReviewContextPackageError("step_result_refs must match steps in order")

    for item in stage_review_refs:
        validate_stage_review_ref_path(item["path"], payload["stage"])

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise ReviewContextPackageError("run_id must match run_dir name")
        for item, step in zip(context_package_refs, steps, strict=True):
            validate_ref_file(item, run_root)
            context_payload = validate_step_context_package_or_raise(
                load_json(run_root / item["path"]),
                repo_root=repo_root,
                run_dir=run_root,
            )
            if (
                context_payload["run_id"] != payload["run_id"]
                or context_payload["stage"] != payload["stage"]
                or context_payload["step"] != step
            ):
                raise ReviewContextPackageError(
                    "StepContextPackage stage and step must match package"
                )
        for item, step in zip(step_result_refs, steps, strict=True):
            validate_ref_file(item, run_root)
            step_payload = validate_step_result_or_raise(
                load_json(run_root / item["path"]),
                run_dir=run_root,
            )
            if (
                step_payload["stage"] != payload["stage"]
                or step_payload["step"] != step
            ):
                raise ReviewContextPackageError(
                    "StepResult stage and step must match package"
                )
        for item in stage_review_refs:
            validate_ref_file(item, run_root)
            if item["path"] == f"stage_reviews/{payload['stage']}/issues_index.json":
                validate_issues_index_or_raise(
                    load_json(run_root / item["path"]),
                    run_dir=run_root,
                )

    return payload


def expected_context_package_path(stage: str, step: str) -> str:
    return f"orchestration/context_packages/{stage}/{step}.json"


def expected_step_result_path(step: str) -> str:
    return f"orchestration/step_results/{step}.json"


def expected_result_paths(stage: str) -> dict[str, str]:
    return {
        "stage_gate_result": f"orchestration/stage_gate_results/{stage}.json",
    }


def validate_steps(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ReviewContextPackageError("steps must be a non-empty list")
    if not all(isinstance(step, str) for step in value):
        raise ReviewContextPackageError("steps must be a list of strings")
    if len(value) != len(set(value)):
        raise ReviewContextPackageError("steps must not contain duplicates")
    for step in value:
        validate_step_or_raise(step)
    return list(value)


def validate_ref_list(value: Any, field: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ReviewContextPackageError(f"{field} must be a list")
    refs: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise ReviewContextPackageError(f"{field} entries must be objects")
        validate_exact_fields(item, REF_FIELDS)
        path = item["path"]
        digest = item["sha256"]
        if not isinstance(path, str):
            raise ReviewContextPackageError(f"{field} path must be a string")
        validate_run_relative_path(path)
        if path in seen_paths:
            raise ReviewContextPackageError(f"{field} must not contain duplicate paths")
        seen_paths.add(path)
        if not isinstance(digest, str) or not SHA256_RE.match(digest):
            raise ReviewContextPackageError(f"invalid sha256 for {path}")
        refs.append({"path": path, "sha256": digest})
    return refs


def validate_stage_review_ref_path(path: str, stage: str) -> None:
    validate_run_relative_path(path)
    prefix = f"stage_reviews/{stage}/"
    if not path.startswith(prefix):
        raise ReviewContextPackageError("stage_review_refs path must match package stage")
    filename = path.removeprefix(prefix)
    if filename not in ALLOWED_STAGE_REVIEW_FILES:
        raise ReviewContextPackageError(f"stage_review_refs path is not allowed: {path!r}")


def validate_result_paths(value: Any, stage: str) -> None:
    if not isinstance(value, dict) or set(value) != RESULT_PATH_FIELDS:
        raise ReviewContextPackageError("result_paths must contain stage_gate_result")
    expected = expected_result_paths(stage)
    if value != expected:
        raise ReviewContextPackageError("result_paths must match the stage")
    for path in value.values():
        validate_run_relative_path(path)


def validate_constraints(value: Any) -> None:
    if value != FIXED_CONSTRAINTS:
        raise ReviewContextPackageError("constraints must declare the fixed review boundary")


def build_ref(run_dir: Path, path_value: Path | str) -> dict[str, str]:
    relative_path, absolute_path = normalize_run_path(run_dir, path_value)
    if not absolute_path.is_file():
        raise ReviewContextPackageError(f"ref path does not exist: {relative_path}")
    return {"path": relative_path, "sha256": file_sha256(absolute_path)}


def normalize_run_path(run_dir: Path, path_value: Path | str) -> tuple[str, Path]:
    root = run_dir.expanduser().resolve()
    raw_path = Path(path_value)
    if raw_path.is_absolute():
        absolute_path = raw_path.expanduser().resolve()
        if not absolute_path.is_relative_to(root):
            raise ReviewContextPackageError(f"ref path escapes run_dir: {path_value}")
        relative_path = absolute_path.relative_to(root).as_posix()
    else:
        relative_path = str(path_value)
        validate_run_relative_path(relative_path)
        absolute_path = (root / relative_path).resolve()
        if not absolute_path.is_relative_to(root):
            raise ReviewContextPackageError(f"ref path escapes run_dir: {relative_path}")
    validate_run_relative_path(relative_path)
    return relative_path, absolute_path


def validate_ref_file(ref: dict[str, str], run_dir: Path) -> None:
    relative_path, absolute_path = normalize_run_path(run_dir, ref["path"])
    if relative_path != ref["path"]:
        raise ReviewContextPackageError("ref path must be run-relative")
    if not absolute_path.is_file():
        raise ReviewContextPackageError(f"ref path does not exist: {ref['path']}")
    digest = file_sha256(absolute_path)
    if digest != ref["sha256"]:
        raise ReviewContextPackageError(f"sha256 mismatch for {ref['path']}")


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise ReviewContextPackageError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise ReviewContextPackageError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ReviewContextPackageError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise ReviewContextPackageError("run_id must be a safe non-empty run id")


def validate_stage_or_raise(value: Any) -> None:
    if not isinstance(value, str) or value not in STAGES:
        raise ReviewContextPackageError(f"invalid stage: {value!r}")
    try:
        validate_stage(value)
    except ShortResultError as exc:
        raise ReviewContextPackageError(str(exc)) from exc


def validate_step_or_raise(value: Any) -> None:
    if not isinstance(value, str) or value not in STEPS:
        raise ReviewContextPackageError(f"invalid step: {value!r}")
    try:
        validate_step(value)
    except ShortResultError as exc:
        raise ReviewContextPackageError(str(exc)) from exc


def validate_timestamp(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReviewContextPackageError(f"{field} must be a non-empty string")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ReviewContextPackageError(f"{field} must be an ISO 8601 timestamp") from exc


def validate_run_relative_path(path: str) -> None:
    try:
        validate_result_path(path)
    except ShortResultError as exc:
        raise ReviewContextPackageError(str(exc)) from exc


def validate_step_result_or_raise(payload: dict[str, Any], run_dir: Path | str) -> dict[str, Any]:
    try:
        return validate_step_result(payload, run_dir=run_dir)
    except ShortResultError as exc:
        raise ReviewContextPackageError(str(exc)) from exc


def validate_step_context_package_or_raise(
    payload: dict[str, Any],
    repo_root: Path | str | None = None,
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    try:
        return validate_step_context_package(payload, repo_root=repo_root, run_dir=run_dir)
    except ContextPackageError as exc:
        raise ReviewContextPackageError(str(exc)) from exc


def validate_issues_index_or_raise(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
    *,
    validate_artifact_refs: bool = True,
) -> dict[str, Any]:
    try:
        return validate_issues_index(
            payload,
            run_dir=run_dir,
            validate_artifact_refs=validate_artifact_refs,
        )
    except StageReviewIssueError as exc:
        raise ReviewContextPackageError(str(exc)) from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewContextPackageError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReviewContextPackageError(f"JSON file must contain an object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def payload_ref(run_dir: Path, path: Path, payload: dict[str, Any]) -> dict[str, str]:
    relative_path, _ = normalize_run_path(run_dir, path)
    digest = hashlib.sha256(json_bytes(payload)).hexdigest()
    return {"path": relative_path, "sha256": digest}


def json_bytes(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def restore_file(path: Path, content: bytes | None) -> None:
    if content is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
