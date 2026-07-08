import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.context_packages import ContextPackageError, validate_step_context_package
from ai_writing_plugin.progress_ledger import ProgressLedgerError, validate_progress_ledger
from ai_writing_plugin.short_results import ShortResultError, validate_step_result
from ai_writing_plugin.step_worker_dispatch import (
    StepWorkerDispatchError,
    validate_step_worker_dispatch,
)


ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def create_repo_and_run(tmp_path: Path) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    run_dir = tmp_path / "runs" / "demo-run"
    step = "step-input-materials"

    write(repo_root / "skills" / step / "SKILL.md", "wrapper")
    write(repo_root / "skills" / "workflow-steps" / step / "SKILL.md", "canonical")
    write(repo_root / "skills" / "document-types" / "hara" / "SKILL.md", "doctype")
    write(run_dir / "task_brief.json", '{"task_type":"hara"}')
    write(run_dir / "manifest.json", "{}")
    return repo_root, run_dir


def write_valid_step_result(run_dir: Path) -> Path:
    step = "step-input-materials"
    payload = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": step,
        "status": "done",
        "artifact_paths": ["manifest.json"],
        "artifact_hashes": {"manifest.json": sha256_file(run_dir / "manifest.json")},
        "summary": "Step completed and artifacts were written.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }
    path = run_dir / "orchestration" / "step_results" / f"{step}.json"
    write(path, json.dumps(payload, ensure_ascii=False))
    return path


def test_runtime_metadata_cli_contract_round_trip(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    step = "step-input-materials"

    init = run_cli("init-progress-ledger", "--run-dir", str(run_dir))
    assert init.returncode == 0, init.stderr

    prepare = run_cli(
        "prepare-step-worker-dispatch",
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--step",
        step,
        "--task-type",
        "hara",
    )
    assert prepare.returncode == 0, prepare.stderr

    package_path = run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    dispatch_path = run_dir / "orchestration/worker_dispatches/ingest/step-input-materials.json"
    ledger_path = run_dir / "orchestration/progress_ledger.json"

    validations = [
        run_cli(
            "validate-step-context-package",
            "--path",
            str(package_path),
            "--repo-root",
            str(repo_root),
            "--run-dir",
            str(run_dir),
        ),
        run_cli(
            "validate-step-worker-dispatch",
            "--path",
            str(dispatch_path),
            "--repo-root",
            str(repo_root),
            "--run-dir",
            str(run_dir),
        ),
        run_cli(
            "validate-progress-ledger",
            "--path",
            str(ledger_path),
            "--run-dir",
            str(run_dir),
        ),
    ]
    for result in validations:
        assert result.returncode == 0, result.stderr

    step_result = write_valid_step_result(run_dir)
    validate_step = run_cli(
        "validate-step-result",
        "--path",
        str(step_result),
        "--run-dir",
        str(run_dir),
    )
    assert validate_step.returncode == 0, validate_step.stderr

    complete = run_cli(
        "complete-step-worker-dispatch",
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--step",
        step,
        "--step-result",
        str(step_result),
    )
    assert complete.returncode == 0, complete.stderr

    review_package = run_cli(
        "build-review-context-package",
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--step",
        step,
    )
    assert review_package.returncode == 0, review_package.stderr
    review_package_path = run_dir / "orchestration/review_context_packages/ingest.json"

    validate_review_package = run_cli(
        "validate-review-context-package",
        "--path",
        str(review_package_path),
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
    )
    assert validate_review_package.returncode == 0, validate_review_package.stderr
    review_payload = read_json(review_package_path)
    assert review_payload["schema_version"] == 2
    assert review_payload["context_package_refs"] == [
        {
            "path": "orchestration/context_packages/ingest/step-input-materials.json",
            "sha256": sha256_file(package_path),
        }
    ]


def test_run_ref_mutation_after_dispatch_fails_closed(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    step = "step-input-materials"

    init = run_cli("init-progress-ledger", "--run-dir", str(run_dir))
    assert init.returncode == 0, init.stderr

    prepare = run_cli(
        "prepare-step-worker-dispatch",
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--step",
        step,
        "--task-type",
        "hara",
    )
    assert prepare.returncode == 0, prepare.stderr

    write(run_dir / "task_brief.json", '{"task_type":"hara","mutated":true}')
    step_result = write_valid_step_result(run_dir)
    package_path = run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    dispatch_path = run_dir / "orchestration/worker_dispatches/ingest/step-input-materials.json"

    validate_package = run_cli(
        "validate-step-context-package",
        "--path",
        str(package_path),
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
    )
    assert validate_package.returncode == 2
    assert "run ref sha256 mismatch: task_brief.json" in validate_package.stderr

    validate_dispatch = run_cli(
        "validate-step-worker-dispatch",
        "--path",
        str(dispatch_path),
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
    )
    assert validate_dispatch.returncode == 2
    assert "run ref sha256 mismatch: task_brief.json" in validate_dispatch.stderr

    complete = run_cli(
        "complete-step-worker-dispatch",
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--step",
        step,
        "--step-result",
        str(step_result),
    )
    assert complete.returncode == 2
    assert "run ref sha256 mismatch: task_brief.json" in complete.stderr


def test_plan10_real_run_drift_shapes_remain_invalid():
    with pytest.raises(ContextPackageError, match="unexpected fields"):
        validate_step_context_package(
            {
                "step": "step-input-materials",
                "stage": "ingest",
                "run_id": "demo-run",
                "run_dir": "/tmp/demo-run",
                "task_type": "hara",
                "files": {},
            }
        )

    with pytest.raises(StepWorkerDispatchError, match="unexpected fields"):
        validate_step_worker_dispatch(
            {
                "kind": "step_worker_dispatch",
                "schema_version": 1,
                "run_id": "demo-run",
                "stage": "ingest",
                "step": "step-input-materials",
                "created_at": "2026-07-08T00:00:00+00:00",
                "context_package_path": "orchestration/context_packages/ingest/step-input-materials.json",
                "step_result_path": "orchestration/step_results/step-input-materials.json",
                "subagent_state_dir": "subagent/step-input-materials",
                "task_type": "hara",
                "instruction": "inline worker instruction",
            }
        )

    with pytest.raises(ProgressLedgerError, match="unexpected fields"):
        validate_progress_ledger(
            {
                "kind": "progress_ledger",
                "schema_version": 1,
                "run_id": "demo-run",
                "created_at": "2026-07-08T00:00:00+00:00",
                "updated_at": "2026-07-08T00:00:00+00:00",
                "entries": [],
                "task_type": "hara",
                "current_stage": "ingest",
                "current_step": "step-input-materials",
                "stages": {},
            }
        )


def test_step_result_status_completed_is_rejected():
    payload = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": "step-input-materials",
        "status": "completed",
        "artifact_paths": ["manifest.json"],
        "artifact_hashes": {"manifest.json": "0" * 64},
        "summary": "Step completed and artifacts were written.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }

    with pytest.raises(ShortResultError, match="invalid status"):
        validate_step_result(payload)
