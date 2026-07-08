import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.context_packages import build_step_context_package
from ai_writing_plugin.progress_ledger import (
    init_progress_ledger,
    progress_ledger_path,
)
from ai_writing_plugin.step_worker_dispatch import (
    StepWorkerDispatchError,
    complete_step_worker_dispatch,
    prepare_step_worker_dispatch,
    step_worker_dispatch_path,
    validate_step_worker_dispatch,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_HASH = "0" * 64
DEFAULT_STAGE = "ingest"
DEFAULT_STEP = "step-input-materials"
WORKFLOW_STAGE_STEPS = {
    "ingest": [
        "step-input-materials",
        "step-material-inventory",
        "step-source-index",
    ],
    "outline": ["step-template-outline"],
    "evidence_planning": [
        "step-research-questions",
        "step-evidence-map",
    ],
    "draft": ["step-conservative-draft"],
    "review": [
        "step-review",
        "step-verification",
    ],
    "finalize": [
        "step-revision",
        "step-final-report",
    ],
    "learning": [
        "step-run-summary",
        "step-candidate-profile-update",
    ],
}
ALL_WORKFLOW_STEPS = [
    step for steps in WORKFLOW_STAGE_STEPS.values() for step in steps
]


def write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path: str, digest: str = VALID_HASH) -> dict:
    return {"path": path, "sha256": digest}


def create_repo_and_run(tmp_path: Path):
    repo_root = tmp_path / "repo"
    run_dir = tmp_path / "runs" / "demo-run"

    for step in ALL_WORKFLOW_STEPS:
        write(repo_root / "skills" / step / "SKILL.md", f"{step} wrapper")
        write(
            repo_root / "skills" / "workflow-steps" / step / "SKILL.md",
            f"{step} canonical",
        )

    write(repo_root / "skills" / "document-types" / "hara" / "SKILL.md", "doctype")
    write(run_dir / "task_brief.json", '{"task_type":"hara"}')
    write(run_dir / "manifest.json", "{}")
    for stage in WORKFLOW_STAGE_STEPS:
        write(run_dir / "stage_reviews" / stage / "issues.json", "{}")
    init_progress_ledger(run_dir)
    return repo_root, run_dir


def write_step_result(
    run_dir: Path,
    step: str,
    *,
    stage: str = DEFAULT_STAGE,
    status: str = "done",
) -> Path:
    payload = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": stage,
        "step": step,
        "status": status,
        "artifact_paths": ["manifest.json"],
        "artifact_hashes": {"manifest.json": sha256_text("{}")},
        "summary": "Step completed and artifacts were written.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }
    path = run_dir / "orchestration" / "step_results" / f"{step}.json"
    write(path, json.dumps(payload))
    return path


def write_review_result(
    run_dir: Path,
    step: str,
    *,
    stage: str = DEFAULT_STAGE,
    status: str = "done",
) -> Path:
    payload = {
        "kind": "review_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": stage,
        "step": step,
        "status": status,
        "review_package_paths": [f"stage_reviews/{stage}/issues.json"],
        "review_package_hashes": {
            f"stage_reviews/{stage}/issues.json": sha256_text("{}"),
        },
        "summary": "Review package complete and ready for user gate.",
        "blocking_issues_count": 1 if status == "needs_revision" else 0,
        "next_gate_status": "needs_user_decision",
    }
    path = run_dir / "orchestration" / "review_results" / stage / f"{step}.json"
    write(path, json.dumps(payload))
    return path


def valid_dispatch(**overrides):
    stage = overrides.pop("stage", DEFAULT_STAGE)
    step = overrides.pop("step", DEFAULT_STEP)
    payload = {
        "kind": "step_worker_dispatch",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": stage,
        "step": step,
        "created_at": "2026-07-08T00:00:00+00:00",
        "context_package_ref": ref(
            f"orchestration/context_packages/{stage}/{step}.json"
        ),
        "progress_ledger_ref": ref("orchestration/progress_ledger.json"),
        "result_paths": {
            "step_result": f"orchestration/step_results/{step}.json",
            "review_result": f"orchestration/review_results/{stage}/{step}.json",
        },
        "constraints": {
            "package_path_only": True,
            "worker_reads_refs": True,
            "main_agent_reads_short_results_only": True,
            "no_artifact_body": True,
        },
    }
    payload.update(overrides)
    return payload


def assert_invalid(payload, expected_message: str, **kwargs):
    with pytest.raises(StepWorkerDispatchError, match=expected_message):
        validate_step_worker_dispatch(payload, **kwargs)


def test_prepare_step_worker_dispatch_writes_canonical_dispatch_and_updates_ledger(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)

    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )

    dispatch_path = (
        run_dir / "orchestration" / "worker_dispatches" / "ingest" / f"{DEFAULT_STEP}.json"
    )
    package_path = (
        run_dir / "orchestration" / "context_packages" / "ingest" / f"{DEFAULT_STEP}.json"
    )
    ledger_path = progress_ledger_path(run_dir)

    assert step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP) == dispatch_path
    assert dispatch_path.is_file()
    assert package_path.is_file()
    assert read_json(dispatch_path) == payload
    assert payload["context_package_ref"] == {
        "path": "orchestration/context_packages/ingest/step-input-materials.json",
        "sha256": sha256_file(package_path),
    }
    assert payload["progress_ledger_ref"] == {
        "path": "orchestration/progress_ledger.json",
        "sha256": sha256_file(ledger_path),
    }

    ledger = read_json(ledger_path)
    entry = ledger["entries"][0]
    assert entry["stage"] == "ingest"
    assert entry["step"] == DEFAULT_STEP
    assert entry["status"] == "context_ready"
    assert entry["context_package_ref"]["path"] == payload["context_package_ref"]["path"]


def test_prepare_step_worker_dispatch_reuses_existing_context_package(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    package = build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )

    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )

    assert read_json(
        run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    ) == package
    assert payload["context_package_ref"]["sha256"] == sha256_file(
        run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    )


def test_prepare_step_worker_dispatch_requires_existing_progress_ledger(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    progress_ledger_path(run_dir).unlink()

    with pytest.raises(StepWorkerDispatchError, match="progress ledger does not exist"):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            task_type="hara",
        )


@pytest.mark.parametrize(
    "stage, step",
    [
        (stage, step)
        for stage, steps in WORKFLOW_STAGE_STEPS.items()
        for step in steps
    ],
)
def test_prepare_step_worker_dispatch_supports_all_workflow_steps(tmp_path, stage, step):
    repo_root, run_dir = create_repo_and_run(tmp_path)

    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage=stage,
        step=step,
        task_type="hara",
    )

    assert payload["stage"] == stage
    assert payload["step"] == step
    assert payload["context_package_ref"]["path"] == (
        f"orchestration/context_packages/{stage}/{step}.json"
    )
    assert payload["result_paths"] == {
        "step_result": f"orchestration/step_results/{step}.json",
        "review_result": f"orchestration/review_results/{stage}/{step}.json",
    }
    assert step_worker_dispatch_path(run_dir, stage, step).is_file()
    ledger = read_json(progress_ledger_path(run_dir))
    assert ledger["entries"][0]["stage"] == stage
    assert ledger["entries"][0]["step"] == step
    assert ledger["entries"][0]["status"] == "context_ready"


def test_complete_step_worker_dispatch_updates_ledger_from_short_results(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    step_result = write_step_result(run_dir, DEFAULT_STEP)
    review_result = write_review_result(run_dir, DEFAULT_STEP, status="needs_revision")

    ledger = complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        step_result=step_result.relative_to(run_dir).as_posix(),
        review_result=review_result,
    )

    entry = ledger["entries"][0]
    assert entry["status"] == "needs_revision"
    assert entry["step_result_ref"] == {
        "path": "orchestration/step_results/step-input-materials.json",
        "sha256": sha256_file(step_result),
    }
    assert entry["review_result_ref"] == {
        "path": "orchestration/review_results/ingest/step-input-materials.json",
        "sha256": sha256_file(review_result),
    }
    assert entry["blocking_issues_count"] == 1
    assert entry["next_gate_status"] == "needs_user_decision"
    dispatch = read_json(step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP))
    assert validate_step_worker_dispatch(dispatch, repo_root=repo_root, run_dir=run_dir) == dispatch


@pytest.mark.parametrize(
    "stage, step, message",
    [
        ("ingest", "step-final-report", "stage-step pair"),
        ("draft", "step-template-outline", "stage-step pair"),
    ],
)
def test_rejects_stage_step_mismatches(tmp_path, stage, step, message):
    repo_root, run_dir = create_repo_and_run(tmp_path)

    with pytest.raises(StepWorkerDispatchError, match=message):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage=stage,
            step=step,
            task_type="hara",
        )


@pytest.mark.parametrize(
    "field",
    ["content", "text", "artifact_body", "result_body", "package_body", "instructions"],
)
def test_rejects_unknown_or_body_like_fields(field):
    payload = valid_dispatch()
    payload[field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "bad_ref, message",
    [
        (ref("/absolute.json"), "relative POSIX path"),
        (ref("../outside.json"), "must not contain '..'"),
        (ref("plans\\dispatch.json"), "must use POSIX separators"),
        (ref("runs/demo-run/orchestration/progress_ledger.json"), "must not start with runs/"),
        (ref("examples/demo/task.yaml"), "outside runtime result boundary"),
        (ref("docs/maintainers/PLAN.md"), "outside runtime result boundary"),
        (ref("contracts/CURRENT_ARTIFACT_CONTRACTS.md"), "outside runtime result boundary"),
    ],
)
def test_rejects_refs_outside_run_boundary(bad_ref, message):
    payload = valid_dispatch(progress_ledger_ref=bad_ref)

    assert_invalid(payload, message)


def test_run_dir_validation_requires_matching_ref_hashes(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    assert validate_step_worker_dispatch(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload

    payload["progress_ledger_ref"]["sha256"] = VALID_HASH
    assert_invalid(payload, "sha256 mismatch", run_dir=run_dir)


def test_run_dir_validation_delegates_to_context_package_validator(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    package_path = run_dir / payload["context_package_ref"]["path"]
    package = read_json(package_path)
    package["constraints"] = {"paths_and_hashes_only": True}
    write(package_path, json.dumps(package))
    payload["context_package_ref"]["sha256"] = sha256_file(package_path)

    assert_invalid(payload, "constraints", repo_root=repo_root, run_dir=run_dir)


def test_cli_prepares_completes_and_validates_dispatch(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)

    prepare = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "prepare-step-worker-dispatch",
            "--repo-root",
            str(repo_root),
            "--run-dir",
            str(run_dir),
            "--stage",
            "ingest",
            "--step",
            DEFAULT_STEP,
            "--task-type",
            "hara",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert prepare.returncode == 0, prepare.stderr
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    assert prepare.stdout.strip() == str(dispatch_path)

    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-step-worker-dispatch",
            "--path",
            str(dispatch_path),
            "--repo-root",
            str(repo_root),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert validate.returncode == 0, validate.stderr
    assert validate.stdout.strip() == "step worker dispatch valid"

    step_result = write_step_result(run_dir, DEFAULT_STEP)
    review_result = write_review_result(run_dir, DEFAULT_STEP)
    complete = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "complete-step-worker-dispatch",
            "--run-dir",
            str(run_dir),
            "--stage",
            "ingest",
            "--step",
            DEFAULT_STEP,
            "--step-result",
            str(step_result),
            "--review-result",
            str(review_result.relative_to(run_dir)),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert complete.returncode == 0, complete.stderr
    assert complete.stdout.strip() == str(progress_ledger_path(run_dir))
    assert read_json(progress_ledger_path(run_dir))["entries"][0]["status"] == "done"

    dispatch = read_json(dispatch_path)
    dispatch["stage"] = "outline"
    write(dispatch_path, json.dumps(dispatch))
    invalid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-step-worker-dispatch",
            "--path",
            str(dispatch_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode == 2
    assert "stage-step pair" in invalid.stderr
