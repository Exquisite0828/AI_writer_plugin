from __future__ import annotations

import hashlib
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from .document_types.profile_loader import DocumentProfileValidationError, resolve_profile_path
from .models import TaskConfig


RUN_STATE_FILENAME = "run_state.json"
RUN_STATE_LOCK_FILENAME = ".run_state.lock"
SCHEMA_VERSION = 1

STAGE_ORDER = ["ingest", "outline", "evidence", "planning", "draft", "review", "finalize", "learning"]

STAGE_REGISTRY: dict[str, dict[str, Any]] = {
    "ingest": {
        "phase": "phase_1",
        "required_outputs": [
            "manifest.json",
            "task_brief.json",
            "inputs/input_inventory.json",
            "knowledge/source_index.json",
            "knowledge/provenance_index.json",
            "knowledge/knowledge_gaps.md",
        ],
    },
    "outline": {
        "phase": "phase_2",
        "required_outputs": [
            "plans/template_structure.json",
            "plans/outline_l1.md",
        ],
    },
    "evidence": {
        "phase": "phase_3",
        "required_outputs": [
            "plans/research_questions.json",
            "plans/evidence_map.json",
            "plans/unresolved_questions.md",
        ],
    },
    "planning": {
        "phase": "phase_4",
        "required_outputs": [
            "plans/citation_plan.json",
            "plans/claim_support_matrix.json",
            "plans/outline_final.md",
            "plans/section_tasks.json",
            "plans/writing_plan.md",
        ],
    },
    "draft": {
        "phase": "phase_5",
        "required_outputs": [
            "draft/full_draft.md",
        ],
    },
    "review": {
        "phase": "phase_6",
        "required_outputs": [
            "review/review_report.json",
            "review/template_review.md",
            "review/checklist_review.md",
            "review/evidence_review.md",
            "review/final_review.md",
            "verify/verify_report.json",
            "verify/failures.md",
        ],
    },
    "finalize": {
        "phase": "phase_7",
        "required_outputs": [
            "revision_plan.json",
            "revised/full_draft.md",
            "revised/change_log.md",
            "final/final_report.md",
            "final/delivery_summary.md",
        ],
    },
    "learning": {
        "phase": "phase_8",
        "required_outputs": [
            "trace/session_trace.jsonl",
            "trace/hitl_decisions.jsonl",
            "learning/run_summary.md",
            "learning/reusable_patterns.md",
            "learning/candidate_profile_update.yaml",
            "learning/candidate_skill_patch.md",
            "learning/promotion_report.md",
        ],
    },
}


class RunStateError(Exception):
    """Raised when resumable run state cannot be read, locked, or resumed."""


@contextmanager
def run_state_lock(run_dir: Path, command: str, recover_stale: bool = True) -> Iterator[bool]:
    lock_path = run_dir / RUN_STATE_LOCK_FILENAME
    recovered_stale_lock = False

    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            lock_data = read_existing_lock(lock_path)
            pid = lock_data["pid"]
            if is_pid_alive(pid):
                raise RunStateError(
                    f"run_state lock exists and pid {pid} is alive; another process may be running this run"
                )
            if not recover_stale:
                raise RunStateError(f"run_state lock exists for dead pid {pid}")
            try:
                lock_path.unlink()
            except FileNotFoundError:
                continue
            recovered_stale_lock = True
            continue

        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump({"pid": os.getpid(), "created_at": utc_timestamp(), "command": command}, handle, indent=2)
            handle.write("\n")
        break

    try:
        yield recovered_stale_lock
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


def read_existing_lock(lock_path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(lock_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RunStateError(f"run_state lock is malformed: {lock_path}") from exc
    if not isinstance(loaded, dict):
        raise RunStateError(f"run_state lock is malformed: {lock_path}")
    pid = loaded.get("pid")
    if not isinstance(pid, int) or pid <= 0:
        raise RunStateError(f"run_state lock is malformed: {lock_path}")
    if not isinstance(loaded.get("created_at"), str) or not isinstance(loaded.get("command"), str):
        raise RunStateError(f"run_state lock is malformed: {lock_path}")
    return loaded


def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def state_exists(run_dir: str | Path) -> bool:
    return (Path(run_dir) / RUN_STATE_FILENAME).exists()


def create_run_state(run_dir: Path, task_path: Path, task_config: TaskConfig) -> dict[str, Any]:
    manifest = read_json(run_dir / "manifest.json")
    created_at = utc_timestamp()
    state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "task_file": str(task_path),
        "task_sha256": file_sha256(task_path),
        "profile_path": task_config.document_profile_path,
        "profile_sha256": profile_sha256(task_config.document_profile_path),
        "status": "running",
        "created_at": created_at,
        "updated_at": created_at,
        "stage_order": [
            {"name": stage, "phase": STAGE_REGISTRY[stage]["phase"]} for stage in STAGE_ORDER
        ],
        "stages": {
            stage: {
                "status": "pending",
                "phase": STAGE_REGISTRY[stage]["phase"],
                "required_outputs": list(STAGE_REGISTRY[stage]["required_outputs"]),
                "outputs": [],
                "started_at": None,
                "completed_at": None,
                "failed_at": None,
                "interrupted_at": None,
                "interrupt_reason": "",
                "error": "",
                "dirty_reason": "",
            }
            for stage in STAGE_ORDER
        },
    }
    mark_stage_done(state, run_dir, "ingest", STAGE_REGISTRY["ingest"]["required_outputs"])
    write_state(run_dir, state)
    return state


def load_state(run_dir: str | Path) -> dict[str, Any]:
    run_path = Path(run_dir)
    state_path = run_path / RUN_STATE_FILENAME
    if not state_path.exists():
        raise RunStateError(f"resume-run failed: {run_path} is not a resumable run; run_state.json is missing")
    try:
        loaded = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RunStateError(f"resume-run failed: invalid JSON in {state_path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise RunStateError(f"resume-run failed: invalid encoding in {state_path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise RunStateError(f"resume-run failed: invalid run_state.json root")
    if loaded.get("schema_version") != SCHEMA_VERSION:
        raise RunStateError(f"resume-run failed: unsupported run_state schema_version: {loaded.get('schema_version')}")
    if loaded.get("stage_order") is None or loaded.get("stages") is None:
        raise RunStateError("resume-run failed: invalid run_state.json: missing stage_order or stages")
    return loaded


def write_state(run_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = utc_timestamp()
    encoded = json.dumps(state, ensure_ascii=False, indent=2)
    (run_dir / RUN_STATE_FILENAME).write_text(f"{encoded}\n", encoding="utf-8")


def run_checkpointed_stage(
    run_dir: str | Path,
    stage: str,
    runner: Callable[[Path], Any],
    *,
    lock_already_held: bool = False,
    command: str | None = None,
) -> Any:
    run_path = Path(run_dir)
    if stage not in STAGE_REGISTRY:
        raise RunStateError(f"Unknown resumable stage: {stage}")

    if lock_already_held:
        state = load_state(run_path)
        validate_task_and_profile_hashes(state)
        return run_stage_with_loaded_state(run_path, state, stage, runner)

    with run_state_lock(run_path, command or f"{stage}-run") as recovered_stale_lock:
        state = load_state(run_path)
        validate_task_and_profile_hashes(state)
        mark_running_stages_interrupted(state, reason="stale_lock_recovery" if recovered_stale_lock else "unlocked_resume")
        write_state(run_path, state)
        return run_stage_with_loaded_state(run_path, state, stage, runner)


def run_stage_with_loaded_state(run_dir: Path, state: dict[str, Any], stage: str, runner: Callable[[Path], Any]) -> Any:
    mark_stage_running(state, stage)
    write_state(run_dir, state)
    try:
        result = runner(run_dir)
        output_paths = artifact_paths_from_result(result) or STAGE_REGISTRY[stage]["required_outputs"]
        validate_required_outputs(run_dir, stage, output_paths)
        mark_stage_done(state, run_dir, stage, output_paths)
        state["status"] = "completed" if all_stages_done(state) else "running"
        write_state(run_dir, state)
        return result
    except Exception as exc:
        mark_stage_failed(state, stage, exc)
        state["status"] = "failed"
        write_state(run_dir, state)
        raise


def resume_run(
    run_dir: str | Path,
    stage_runners: dict[str, Callable[[Path], Any]],
    *,
    before_stage: Callable[[Path, str], None] | None = None,
    max_stages: int | None = None,
) -> Path:
    run_path = Path(run_dir)
    if not state_exists(run_path):
        raise RunStateError(f"resume-run failed: {run_path} is not a resumable run; run_state.json is missing")

    with run_state_lock(run_path, "resume-run") as recovered_stale_lock:
        state = load_state(run_path)
        validate_task_and_profile_hashes(state)
        mark_running_stages_interrupted(state, reason="stale_lock_recovery" if recovered_stale_lock else "unlocked_resume")
        write_state(run_path, state)
        start_index = first_non_done_stage_index(run_path, state)
        if start_index is None:
            state["status"] = "completed"
            write_state(run_path, state)
            return run_path

        executed_stage_count = 0
        for stage in STAGE_ORDER[start_index:]:
            if before_stage is not None:
                before_stage(run_path, stage)
            run_checkpointed_stage(
                run_path,
                stage,
                stage_runners[stage],
                lock_already_held=True,
                command="resume-run",
            )
            executed_stage_count += 1
            if max_stages is not None and executed_stage_count >= max_stages:
                break

        state = load_state(run_path)
        state["status"] = "completed" if all_stages_done(state) else "running"
        write_state(run_path, state)
    return run_path


def first_non_done_stage_index(run_dir: Path, state: dict[str, Any]) -> int | None:
    for index, stage in enumerate(STAGE_ORDER):
        stage_state = state["stages"][stage]
        if stage_state["status"] == "done":
            dirty_reason = validate_stage_clean(run_dir, stage)
            if dirty_reason:
                mark_stage_dirty(state, stage, dirty_reason)
                state["status"] = "failed"
                write_state(run_dir, state)
                raise RunStateError(dirty_reason)
            continue
        if stage_state["status"] == "dirty":
            dirty_reason = stage_state.get("dirty_reason") or (
                f"resume-run failed: completed stage {stage} is dirty. Start a new write-run or restore the artifact; "
                "automatic upstream rewind is not supported in v1."
            )
            raise RunStateError(dirty_reason)
        return index
    return None


def validate_task_and_profile_hashes(state: dict[str, Any]) -> None:
    task_path = Path(state.get("task_file", ""))
    expected_task_hash = state.get("task_sha256")
    if not task_path.exists():
        raise RunStateError(
            f"resume-run failed: task file is missing: {task_path}. Start a new write-run or restore the original task file."
        )
    if file_sha256(task_path) != expected_task_hash:
        raise RunStateError(
            "resume-run failed: task file hash mismatch. Start a new write-run or restore the original task.yaml."
        )

    profile_path = state.get("profile_path")
    expected_profile_hash = state.get("profile_sha256")
    if profile_path:
        try:
            resolved_profile_path, _normalized = resolve_profile_path(profile_path)
        except DocumentProfileValidationError as exc:
            raise RunStateError(f"resume-run failed: profile path cannot be resolved: {'; '.join(exc.errors)}") from exc
        if not resolved_profile_path.exists():
            raise RunStateError(
                f"resume-run failed: profile file is missing: {profile_path}. Start a new write-run or restore the profile file."
            )
        if file_sha256(resolved_profile_path) != expected_profile_hash:
            raise RunStateError(
                "resume-run failed: profile file hash mismatch. Start a new write-run or restore the original document_profile.yaml."
            )


def mark_running_stages_interrupted(state: dict[str, Any], reason: str) -> None:
    for stage in STAGE_ORDER:
        stage_state = state["stages"][stage]
        if stage_state["status"] == "running":
            stage_state["status"] = "interrupted"
            stage_state["interrupted_at"] = utc_timestamp()
            stage_state["interrupt_reason"] = reason
            stage_state["error"] = ""
            state["status"] = "interrupted"


def mark_stage_running(state: dict[str, Any], stage: str) -> None:
    stage_state = state["stages"][stage]
    stage_state["status"] = "running"
    stage_state["started_at"] = utc_timestamp()
    stage_state["completed_at"] = None
    stage_state["failed_at"] = None
    stage_state["error"] = ""
    stage_state["dirty_reason"] = ""
    state["status"] = "running"


def mark_stage_done(state: dict[str, Any], run_dir: Path, stage: str, output_paths: list[str]) -> None:
    stage_state = state["stages"][stage]
    stage_state["status"] = "done"
    if not stage_state.get("started_at"):
        stage_state["started_at"] = utc_timestamp()
    stage_state["completed_at"] = utc_timestamp()
    stage_state["failed_at"] = None
    stage_state["error"] = ""
    stage_state["dirty_reason"] = ""
    stage_state["outputs"] = output_records(run_dir, output_paths)


def mark_stage_failed(state: dict[str, Any], stage: str, exc: Exception) -> None:
    stage_state = state["stages"][stage]
    stage_state["status"] = "failed"
    stage_state["failed_at"] = utc_timestamp()
    stage_state["error"] = str(exc)


def mark_stage_dirty(state: dict[str, Any], stage: str, reason: str) -> None:
    stage_state = state["stages"][stage]
    stage_state["status"] = "dirty"
    stage_state["dirty_reason"] = reason


def all_stages_done(state: dict[str, Any]) -> bool:
    return all(state["stages"][stage]["status"] == "done" for stage in STAGE_ORDER)


def artifact_paths_from_result(result: Any) -> list[str]:
    artifact_paths = getattr(result, "artifact_paths", None)
    if isinstance(artifact_paths, list) and all(isinstance(path, str) for path in artifact_paths):
        return artifact_paths
    return []


def validate_stage_clean(run_dir: Path, stage: str) -> str:
    problem = validate_required_outputs(run_dir, stage, STAGE_REGISTRY[stage]["required_outputs"], raise_on_error=False)
    if not problem:
        return ""
    return (
        f"resume-run failed: completed stage {stage} is dirty: {problem}. "
        "Start a new write-run or restore the artifact; automatic upstream rewind is not supported in v1."
    )


def validate_required_outputs(
    run_dir: Path,
    stage: str,
    output_paths: list[str],
    *,
    raise_on_error: bool = True,
) -> str:
    for relative_path in output_paths:
        path = run_dir / relative_path
        problem = validate_output_path(path, relative_path)
        if problem:
            if raise_on_error:
                raise RunStateError(f"stage {stage} output validation failed: {problem}")
            return problem
    return ""


def validate_output_path(path: Path, relative_path: str) -> str:
    if not path.exists():
        return f"{relative_path} missing"
    if not path.is_file():
        return f"{relative_path} is not a file"
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"{relative_path} invalid encoding"
    if not text.strip():
        return f"{relative_path} empty"
    if relative_path.endswith(".json"):
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            return f"{relative_path} invalid JSON: {exc}"
    if relative_path.endswith(".jsonl"):
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                return f"{relative_path} invalid JSONL at line {line_number}: {exc}"
    return ""


def output_records(run_dir: Path, output_paths: list[str]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for relative_path in output_paths:
        path = run_dir / relative_path
        if path.exists() and path.is_file():
            records.append({"path": relative_path, "sha256": file_sha256(path)})
    return records


def profile_sha256(profile_path: str | None) -> str | None:
    if not profile_path:
        return None
    resolved_profile_path, _normalized = resolve_profile_path(profile_path)
    return file_sha256(resolved_profile_path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RunStateError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise RunStateError(f"Invalid JSON object in {path}")
    return loaded


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
