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
    reset_step_for_redispatch,
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


WORKFLOW_STAGE_STEPS = {
    "ingest": (
        "step-input-materials",
        "step-material-inventory",
        "step-source-index",
    ),
    "outline": ("step-template-outline",),
    "evidence_planning": (
        "step-research-questions",
        "step-evidence-map",
    ),
    "draft": ("step-conservative-draft",),
    "review": (
        "step-review",
        "step-verification",
    ),
    "finalize": (
        "step-revision",
        "step-final-report",
    ),
    "learning": (
        "step-run-summary",
        "step-candidate-profile-update",
    ),
}
WORKFLOW_STEP_ORDER = tuple(
    (stage, step)
    for stage, steps in WORKFLOW_STAGE_STEPS.items()
    for step in steps
)
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
    "no_input_body": True,
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
    validate_workflow_stage_step(stage, step)
    run_id = run_dir.name
    validate_run_id(run_id)

    dispatch_path = step_worker_dispatch_path(run_dir, stage, step)
    dispatch_existed = dispatch_path.exists()
    if dispatch_path.exists() and not overwrite_dispatch:
        raise StepWorkerDispatchError(f"step worker dispatch already exists: {dispatch_path}")

    ledger_path = progress_ledger_path(run_dir)
    if not ledger_path.is_file():
        raise StepWorkerDispatchError(f"progress ledger does not exist: {ledger_path}")
    validated_ledger = load_json(ledger_path)
    validate_progress_ledger(validated_ledger, run_dir=run_dir)

    package_path = context_package_path(run_dir, stage, step)
    existing_package_payload: dict[str, Any] | None = None
    if package_path.exists():
        existing_package_payload = load_json(package_path)
        validate_step_context_package(
            existing_package_payload,
            repo_root=repo_root,
            run_dir=run_dir,
        )
        if (
            existing_package_payload["run_id"],
            existing_package_payload["stage"],
            existing_package_payload["step"],
            existing_package_payload["task_type"],
        ) != (run_id, stage, step, task_type):
            raise StepWorkerDispatchError(
                "existing context package identity must match the dispatch invocation"
            )

    if dispatch_existed:
        existing_dispatch_payload = load_json(dispatch_path)
        validate_step_worker_dispatch(
            existing_dispatch_payload,
            repo_root=repo_root,
            run_dir=run_dir,
        )
        if (
            existing_dispatch_payload["run_id"],
            existing_dispatch_payload["stage"],
            existing_dispatch_payload["step"],
        ) != (run_id, stage, step):
            raise StepWorkerDispatchError(
                "existing dispatch identity must match the redispatch invocation"
            )

    upstream_input_refs = collect_upstream_artifact_refs(
        validated_ledger,
        run_dir=run_dir,
        stage=stage,
        step=step,
    )
    default_refs = ["task_brief.json"]
    if step == "step-input-materials":
        default_refs.append("manifest.json")
    preserved_refs: list[str] = []
    if existing_package_payload is not None:
        preserved_refs = [
            item["path"]
            for item in existing_package_payload["run_refs"]
            if item["path"] not in default_refs and item["path"] != "input_refs.json"
        ]
    merged_input_refs = list(
        dict.fromkeys(
            path
            for path in upstream_input_refs + preserved_refs + list(input_refs or [])
            if path != "input_refs.json"
        )
    )
    expected_run_refs = list(dict.fromkeys(default_refs + merged_input_refs))

    if existing_package_payload is not None and not overwrite_package:
        actual_run_refs = [item["path"] for item in existing_package_payload["run_refs"]]
        if actual_run_refs != expected_run_refs:
            raise StepWorkerDispatchError(
                "existing context package does not match the current dispatch inputs; "
                "rerun with --overwrite-package"
            )

    is_redispatch = dispatch_existed and overwrite_dispatch
    downstream_pairs = (
        WORKFLOW_STEP_ORDER[WORKFLOW_STEP_ORDER.index((stage, step)) + 1 :]
        if is_redispatch
        else ()
    )
    transaction_paths = {package_path, ledger_path, dispatch_path}
    for downstream_stage, downstream_step in downstream_pairs:
        transaction_paths.add(
            context_package_path(run_dir, downstream_stage, downstream_step)
        )
        transaction_paths.add(
            step_worker_dispatch_path(run_dir, downstream_stage, downstream_step)
        )
    backups = {
        path: path.read_bytes() if path.exists() else None for path in transaction_paths
    }

    try:
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
                input_refs=merged_input_refs,
                overwrite=overwrite_package,
            )

        if is_redispatch:
            reset_ledger = reset_step_for_redispatch(
                run_dir=run_dir,
                stage=stage,
                step=step,
                context_package=package_path,
                validated_ledger=validated_ledger,
            )
            downstream_keys = set(downstream_pairs)
            reset_ledger["entries"] = [
                entry
                for entry in reset_ledger["entries"]
                if (entry["stage"], entry["step"]) not in downstream_keys
            ]
            validate_progress_ledger(reset_ledger, run_dir=run_dir)
            write_json(ledger_path, reset_ledger)
            for downstream_stage, downstream_step in downstream_pairs:
                downstream_context = context_package_path(
                    run_dir, downstream_stage, downstream_step
                )
                downstream_dispatch = step_worker_dispatch_path(
                    run_dir, downstream_stage, downstream_step
                )
                if downstream_context.exists():
                    downstream_context.unlink()
                if downstream_dispatch.exists():
                    downstream_dispatch.unlink()
        else:
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

        write_json(dispatch_path, payload)
        return payload
    except Exception:
        for path, content in backups.items():
            restore_file(path, content)
        raise


def complete_step_worker_dispatch(
    run_dir: Path | str,
    stage: str,
    step: str,
    step_result: Path | str,
    review_result: Path | str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    run_dir = Path(run_dir).expanduser().resolve()
    validate_workflow_stage_step(stage, step)

    dispatch_path = step_worker_dispatch_path(run_dir, stage, step)
    if not dispatch_path.is_file():
        raise StepWorkerDispatchError(f"step worker dispatch does not exist: {dispatch_path}")
    dispatch_payload = load_json(dispatch_path)
    validate_step_worker_dispatch(dispatch_payload, run_dir=run_dir)

    step_result_path = resolve_run_path(run_dir, step_result)
    step_result_ref = step_result_path.relative_to(run_dir).as_posix()
    if step_result_ref != dispatch_payload["result_paths"]["step_result"]:
        raise StepWorkerDispatchError(
            "StepResult must use the canonical dispatch result path"
        )
    step_payload = validate_step_result(load_json(step_result_path), run_dir=run_dir)
    if step_payload["stage"] != stage or step_payload["step"] != step:
        raise StepWorkerDispatchError("StepResult stage and step must match dispatch")

    authoritative_status = step_payload["status"]
    review_result_path: Path | None = None
    if review_result is not None:
        review_result_path = resolve_run_path(run_dir, review_result)
        review_result_ref = review_result_path.relative_to(run_dir).as_posix()
        if review_result_ref != dispatch_payload["result_paths"]["review_result"]:
            raise StepWorkerDispatchError(
                "ReviewResult must use the canonical dispatch result path"
            )
        review_payload = validate_review_result(load_json(review_result_path), run_dir=run_dir)
        if review_payload["stage"] != stage or review_payload["step"] != step:
            raise StepWorkerDispatchError("ReviewResult stage and step must match dispatch")
        authoritative_status = review_payload["status"]

    ledger_path = progress_ledger_path(run_dir)
    ledger_payload = load_json(ledger_path)
    validate_progress_ledger(ledger_payload, run_dir=run_dir)
    existing_entry = next(
        (
            entry
            for entry in ledger_payload["entries"]
            if entry["stage"] == stage and entry["step"] == step
        ),
        None,
    )
    if (
        review_result_path is None
        and existing_entry is not None
        and existing_entry["review_result_ref"] is not None
    ):
        raise StepWorkerDispatchError(
            "existing ReviewResult binding requires an explicit review-cycle reset"
        )

    if status is not None and status != authoritative_status:
        raise StepWorkerDispatchError(
            "completion status must match the authoritative StepResult or ReviewResult status"
        )

    final_status = authoritative_status
    validate_completion_status(final_status)
    ledger_backup = ledger_path.read_bytes()
    dispatch_backup = dispatch_path.read_bytes()
    try:
        ledger = record_step_progress(
            run_dir=run_dir,
            stage=stage,
            step=step,
            status=final_status,
            step_result=step_result_path,
            review_result=review_result_path,
        )
        dispatch_payload["progress_ledger_ref"] = build_ref_or_raise(
            run_dir,
            ledger_path,
        )
        validate_step_worker_dispatch(dispatch_payload, run_dir=run_dir)
        write_json(dispatch_path, dispatch_payload)
        return ledger
    except Exception as exc:
        restore_file(ledger_path, ledger_backup)
        restore_file(dispatch_path, dispatch_backup)
        if isinstance(exc, ProgressLedgerError):
            raise StepWorkerDispatchError(str(exc)) from exc
        raise


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
    validate_workflow_stage_step(payload["stage"], payload["step"])
    validate_timestamp(payload["created_at"], "created_at")
    context_package_ref = validate_ref(payload["context_package_ref"], "context_package_ref")
    progress_ledger_ref = validate_ref(payload["progress_ledger_ref"], "progress_ledger_ref")
    validate_result_paths(payload["result_paths"], payload["stage"], payload["step"])
    validate_constraints(payload["constraints"])

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise StepWorkerDispatchError("run_id must match run_dir name")
        expected_context_path = (
            f"orchestration/context_packages/{payload['stage']}/{payload['step']}.json"
        )
        if context_package_ref["path"] != expected_context_path:
            raise StepWorkerDispatchError(
                "context_package_ref must use the canonical path for the dispatch stage and step"
            )
        if progress_ledger_ref["path"] != "orchestration/progress_ledger.json":
            raise StepWorkerDispatchError(
                "progress_ledger_ref must use the canonical progress ledger path"
            )
        validate_ref_file(context_package_ref, run_root)
        context_payload = validate_context_package_ref(
            context_package_ref,
            repo_root=repo_root,
            run_dir=run_root,
        )
        if (
            context_payload["run_id"] != payload["run_id"]
            or context_payload["stage"] != payload["stage"]
            or context_payload["step"] != payload["step"]
        ):
            raise StepWorkerDispatchError(
                "StepContextPackage run, stage, and step must match dispatch"
            )
        # ProgressLedger is mutable orchestration state; dispatch stores a live pointer.
        validate_ref_path_exists(progress_ledger_ref, run_root)
        ledger_payload = validate_progress_ledger_ref(progress_ledger_ref, run_root)
        ledger_entry = next(
            (
                entry
                for entry in ledger_payload["entries"]
                if entry["stage"] == payload["stage"]
                and entry["step"] == payload["step"]
            ),
            None,
        )
        if (
            ledger_entry is None
            or ledger_entry["context_package_ref"] != context_package_ref
        ):
            raise StepWorkerDispatchError(
                "progress ledger entry context_package_ref must match dispatch"
            )

    return payload


def validate_workflow_stage_step(stage: Any, step: Any) -> None:
    if not isinstance(stage, str) or stage not in WORKFLOW_STAGE_STEPS:
        raise StepWorkerDispatchError(f"invalid stage: {stage!r}")
    if not isinstance(step, str):
        raise StepWorkerDispatchError(f"invalid step: {step!r}")
    if step not in WORKFLOW_STAGE_STEPS[stage]:
        raise StepWorkerDispatchError(
            f"invalid stage-step pair: stage={stage!r}, step={step!r}"
        )


def collect_upstream_artifact_refs(
    ledger: dict[str, Any],
    *,
    run_dir: Path,
    stage: str,
    step: str,
) -> list[str]:
    target_index = WORKFLOW_STEP_ORDER.index((stage, step))
    entries = {
        (entry["stage"], entry["step"]): entry for entry in ledger["entries"]
    }
    paths: list[str] = []
    excluded_paths = {"input_refs.json", "task_brief.json"}

    for upstream_stage, upstream_step in WORKFLOW_STEP_ORDER[:target_index]:
        entry = entries.get((upstream_stage, upstream_step))
        if entry is None or entry["step_result_ref"] is None:
            continue
        result_ref = entry["step_result_ref"]
        result_path = resolve_run_path(run_dir, result_ref["path"])
        if file_sha256(result_path) != result_ref["sha256"]:
            raise StepWorkerDispatchError(
                f"sha256 mismatch for {result_ref['path']}"
            )
        result_payload = validate_step_result(load_json(result_path), run_dir=run_dir)
        if (
            result_payload["stage"] != upstream_stage
            or result_payload["step"] != upstream_step
        ):
            raise StepWorkerDispatchError(
                "upstream StepResult stage and step must match the ProgressLedger entry"
            )
        for artifact_path in result_payload["artifact_paths"]:
            if artifact_path not in excluded_paths and artifact_path not in paths:
                paths.append(artifact_path)
    return paths


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


def validate_ref_path_exists(ref: dict[str, str], run_dir: Path) -> None:
    resolve_run_path(run_dir, ref["path"])


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


def restore_file(path: Path, content: bytes | None) -> None:
    if content is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


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
