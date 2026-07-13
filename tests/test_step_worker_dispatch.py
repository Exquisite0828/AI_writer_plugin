import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import ai_writing_plugin.step_worker_dispatch as step_worker_dispatch_module
from ai_writing_plugin.context_packages import ContextPackageError, build_step_context_package
from ai_writing_plugin.input_refs import build_input_refs, write_input_refs
from ai_writing_plugin.progress_ledger import (
    ProgressLedgerError,
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


def test_complete_dispatch_help_describes_status_as_assertion_not_override():
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "complete-step-worker-dispatch",
            "--help",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert completed.returncode == 0
    assert "consistency assertion" in completed.stdout
    assert "completion status override" not in completed.stdout


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
    task_path = repo_root / "examples" / "hara_minimal" / "task.yaml"
    source_path = repo_root / "examples" / "hara_minimal" / "inputs" / "source.md"
    write(task_path, "task_type: hara\n")
    write(source_path, "source")
    write_input_refs(
        run_dir,
        build_input_refs(
            run_id="demo-run",
            task_path=task_path,
            task={"task_type": "hara", "inputs": [{"path": "inputs/source.md", "role": "source"}]},
            repo_root=repo_root,
        ),
    )
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
            "no_input_body": True,
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
    context_package = read_json(package_path)
    assert context_package["input_refs_ref"] == {
        "path": "input_refs.json",
        "sha256": sha256_file(run_dir / "input_refs.json"),
    }
    encoded_dispatch = json.dumps(payload, ensure_ascii=False)
    assert "source body" not in encoded_dispatch
    assert "input_materials" not in encoded_dispatch

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


def test_prepare_dispatch_propagates_all_validated_upstream_artifacts_in_workflow_order(
    tmp_path,
):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prior_artifacts = []

    for index, (stage, step) in enumerate(
        (
            (stage, step)
            for stage, steps in WORKFLOW_STAGE_STEPS.items()
            for step in steps
        ),
        start=1,
    ):
        explicit_refs = [prior_artifacts[-1]] if prior_artifacts else []
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage=stage,
            step=step,
            task_type="hara",
            input_refs=explicit_refs,
        )

        package = read_json(
            run_dir
            / "orchestration"
            / "context_packages"
            / stage
            / f"{step}.json"
        )
        expected_refs = ["task_brief.json"]
        if step == DEFAULT_STEP or prior_artifacts:
            expected_refs.append("manifest.json")
        expected_refs.extend(prior_artifacts)
        assert [item["path"] for item in package["run_refs"]] == expected_refs

        artifact_path = run_dir / "artifacts" / f"{index:02d}-{step}.md"
        write(artifact_path, f"artifact for {step}\n")
        artifact_ref = artifact_path.relative_to(run_dir).as_posix()
        artifact_paths = [artifact_ref]
        if step == DEFAULT_STEP:
            artifact_paths = [
                "input_refs.json",
                "task_brief.json",
                "manifest.json",
                artifact_ref,
            ]
        step_result = run_dir / "orchestration" / "step_results" / f"{step}.json"
        write(
            step_result,
            json.dumps(
                {
                    "kind": "step_result",
                    "schema_version": 1,
                    "run_id": "demo-run",
                    "stage": stage,
                    "step": step,
                    "status": "done",
                    "artifact_paths": artifact_paths,
                    "artifact_hashes": {
                        path: sha256_file(run_dir / path) for path in artifact_paths
                    },
                    "summary": "Step completed and reported one unique artifact.",
                    "blocking_issues_count": 0,
                    "next_gate_status": "pending_user_confirmation",
                }
            ),
        )
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage=stage,
            step=step,
            step_result=step_result,
        )
        prior_artifacts.append(artifact_ref)


def test_prepare_dispatch_fails_closed_when_an_upstream_artifact_hash_is_stale(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    artifact_path = run_dir / "artifacts" / "step-one.md"
    write(artifact_path, "original\n")
    artifact_ref = artifact_path.relative_to(run_dir).as_posix()
    step_result = run_dir / "orchestration" / "step_results" / f"{DEFAULT_STEP}.json"
    write(
        step_result,
        json.dumps(
            {
                "kind": "step_result",
                "schema_version": 1,
                "run_id": "demo-run",
                "stage": "ingest",
                "step": DEFAULT_STEP,
                "status": "done",
                "artifact_paths": [artifact_ref],
                "artifact_hashes": {artifact_ref: sha256_file(artifact_path)},
                "summary": "Step completed and reported one unique artifact.",
                "blocking_issues_count": 0,
                "next_gate_status": "pending_user_confirmation",
            }
        ),
    )
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        step_result=step_result,
    )
    write(artifact_path, "changed after completion\n")

    with pytest.raises(ProgressLedgerError, match="sha256 mismatch"):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step="step-material-inventory",
            task_type="hara",
        )


def test_prepare_rejects_prebuilt_package_that_lacks_automatic_upstream_refs(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    upstream_artifact = run_dir / "artifacts" / "step-one.md"
    write(upstream_artifact, "upstream\n")
    step_result = write_step_result(run_dir, DEFAULT_STEP)
    step_payload = read_json(step_result)
    artifact_ref = upstream_artifact.relative_to(run_dir).as_posix()
    step_payload["artifact_paths"].append(artifact_ref)
    step_payload["artifact_hashes"][artifact_ref] = sha256_file(upstream_artifact)
    write(step_result, json.dumps(step_payload))
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        step_result=step_result,
    )

    package_path = (
        run_dir
        / "orchestration"
        / "context_packages"
        / "ingest"
        / "step-material-inventory.json"
    )
    build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-material-inventory",
        task_type="hara",
    )
    before_package = package_path.read_bytes()

    with pytest.raises(StepWorkerDispatchError, match="overwrite-package"):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step="step-material-inventory",
            task_type="hara",
        )

    assert package_path.read_bytes() == before_package
    assert not step_worker_dispatch_path(
        run_dir, "ingest", "step-material-inventory"
    ).exists()

    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-material-inventory",
        task_type="hara",
        overwrite_package=True,
    )
    rebuilt = read_json(package_path)
    assert [item["path"] for item in rebuilt["run_refs"]] == [
        "task_brief.json",
        "manifest.json",
        artifact_ref,
    ]


def test_preparing_multiple_ingest_dispatches_keeps_earlier_dispatches_valid(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepared_paths = []

    for step in WORKFLOW_STAGE_STEPS["ingest"]:
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=step,
            task_type="hara",
        )
        prepared_paths.append(step_worker_dispatch_path(run_dir, "ingest", step))

    assert len(read_json(progress_ledger_path(run_dir))["entries"]) == 3
    for dispatch_path in prepared_paths:
        dispatch = read_json(dispatch_path)
        assert validate_step_worker_dispatch(
            dispatch,
            repo_root=repo_root,
            run_dir=run_dir,
        ) == dispatch


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


@pytest.mark.parametrize("result_kind", ["step", "review"])
def test_complete_rejects_noncanonical_result_paths_without_writes(tmp_path, result_kind):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    canonical_step = write_step_result(run_dir, DEFAULT_STEP)
    noncanonical_step = run_dir / "orchestration" / "step_results" / "alternate.json"
    write(noncanonical_step, canonical_step.read_text(encoding="utf-8"))
    canonical_review = write_review_result(run_dir, DEFAULT_STEP)
    noncanonical_review = run_dir / "orchestration" / "review_results" / "ingest" / "alternate.json"
    write(noncanonical_review, canonical_review.read_text(encoding="utf-8"))
    ledger_path = progress_ledger_path(run_dir)
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    before_ledger = ledger_path.read_bytes()
    before_dispatch = dispatch_path.read_bytes()

    with pytest.raises(StepWorkerDispatchError, match="canonical dispatch result path"):
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            step_result=noncanonical_step if result_kind == "step" else canonical_step,
            review_result=noncanonical_review if result_kind == "review" else None,
        )

    assert ledger_path.read_bytes() == before_ledger
    assert dispatch_path.read_bytes() == before_dispatch


@pytest.mark.parametrize("with_review", [False, True], ids=("step-result", "review-result"))
def test_complete_rejects_status_that_conflicts_with_authoritative_result_without_writes(
    tmp_path,
    with_review,
):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    step_result = write_step_result(run_dir, DEFAULT_STEP)
    review_result = (
        write_review_result(run_dir, DEFAULT_STEP, status="needs_revision")
        if with_review
        else None
    )
    ledger_path = progress_ledger_path(run_dir)
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    before_ledger = ledger_path.read_bytes()
    before_dispatch = dispatch_path.read_bytes()

    conflicting_status = "done" if with_review else "blocked"
    with pytest.raises(StepWorkerDispatchError, match="status.*match"):
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            step_result=step_result,
            review_result=review_result,
            status=conflicting_status,
        )

    assert ledger_path.read_bytes() == before_ledger
    assert dispatch_path.read_bytes() == before_dispatch


def test_complete_accepts_matching_status_as_a_noop_assertion(tmp_path):
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
        step_result=step_result,
        review_result=review_result,
        status="needs_revision",
    )

    entry = ledger["entries"][0]
    assert entry["status"] == "needs_revision"
    assert entry["blocking_issues_count"] == 1
    assert entry["next_gate_status"] == "needs_user_decision"


def test_complete_cannot_drop_an_existing_review_binding_by_omitting_review_result(tmp_path):
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
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        step_result=step_result,
        review_result=review_result,
    )
    ledger_path = progress_ledger_path(run_dir)
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    before_ledger = ledger_path.read_bytes()
    before_dispatch = dispatch_path.read_bytes()

    with pytest.raises(StepWorkerDispatchError, match="existing ReviewResult"):
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            step_result=step_result,
        )

    assert ledger_path.read_bytes() == before_ledger
    assert dispatch_path.read_bytes() == before_dispatch


def test_complete_rolls_back_ledger_when_dispatch_write_fails(tmp_path, monkeypatch):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    step_result = write_step_result(run_dir, DEFAULT_STEP)
    ledger_path = progress_ledger_path(run_dir)
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    before_ledger = ledger_path.read_bytes()
    before_dispatch = dispatch_path.read_bytes()
    original_write_json = step_worker_dispatch_module.write_json

    def fail_dispatch_write(path, payload):
        if path == dispatch_path:
            raise OSError("injected dispatch write failure")
        original_write_json(path, payload)

    monkeypatch.setattr(step_worker_dispatch_module, "write_json", fail_dispatch_write)

    with pytest.raises(OSError, match="injected dispatch write failure"):
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            step_result=step_result,
        )

    assert ledger_path.read_bytes() == before_ledger
    assert dispatch_path.read_bytes() == before_dispatch


def test_complete_rejects_reused_step_result_after_reported_artifact_changes(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    artifact_path = run_dir / "artifacts" / "input-check.md"
    write(artifact_path, "initial\n")
    artifact_ref = artifact_path.relative_to(run_dir).as_posix()
    step_result = run_dir / "orchestration" / "step_results" / f"{DEFAULT_STEP}.json"
    write(
        step_result,
        json.dumps(
            {
                "kind": "step_result",
                "schema_version": 1,
                "run_id": "demo-run",
                "stage": "ingest",
                "step": DEFAULT_STEP,
                "status": "done",
                "artifact_paths": [artifact_ref],
                "artifact_hashes": {artifact_ref: sha256_file(artifact_path)},
                "summary": "Step completed and artifacts were written.",
                "blocking_issues_count": 0,
                "next_gate_status": "pending_user_confirmation",
            }
        ),
    )
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        step_result=step_result,
    )

    write(artifact_path, "changed by an invalid review worker\n")
    with pytest.raises(StepWorkerDispatchError, match="sha256 mismatch"):
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            step_result=step_result,
        )


def test_upstream_redispatch_invalidates_downstream_metadata_before_artifact_revision(
    tmp_path,
):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    first_step = DEFAULT_STEP
    second_step = "step-material-inventory"

    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=first_step,
        task_type="hara",
    )
    upstream_artifact = run_dir / "artifacts" / "upstream.md"
    write(upstream_artifact, "version one\n")
    upstream_ref = upstream_artifact.relative_to(run_dir).as_posix()
    first_result = write_step_result(run_dir, first_step)
    first_payload = read_json(first_result)
    first_payload["artifact_paths"].append(upstream_ref)
    first_payload["artifact_hashes"][upstream_ref] = sha256_file(upstream_artifact)
    write(first_result, json.dumps(first_payload))
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=first_step,
        step_result=first_result,
    )

    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=second_step,
        task_type="hara",
    )
    second_result = write_step_result(run_dir, second_step)
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=second_step,
        step_result=second_result,
    )
    second_context = (
        run_dir
        / "orchestration"
        / "context_packages"
        / "ingest"
        / f"{second_step}.json"
    )
    second_dispatch = step_worker_dispatch_path(run_dir, "ingest", second_step)
    assert upstream_ref in [item["path"] for item in read_json(second_context)["run_refs"]]

    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=first_step,
        task_type="hara",
        overwrite_package=True,
        overwrite_dispatch=True,
    )

    ledger_after_reset = read_json(progress_ledger_path(run_dir))
    assert all(entry["step"] != second_step for entry in ledger_after_reset["entries"])
    assert not second_context.exists()
    assert not second_dispatch.exists()

    write(upstream_artifact, "version two\n")
    revised_payload = read_json(first_result)
    revised_payload["artifact_hashes"][upstream_ref] = sha256_file(upstream_artifact)
    write(first_result, json.dumps(revised_payload))
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=first_step,
        step_result=first_result,
    )

    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=second_step,
        task_type="hara",
    )
    rebuilt_context = read_json(second_context)
    rebuilt_ref = next(
        item for item in rebuilt_context["run_refs"] if item["path"] == upstream_ref
    )
    assert rebuilt_ref["sha256"] == sha256_file(upstream_artifact)


def test_failed_upstream_redispatch_restores_downstream_metadata(tmp_path, monkeypatch):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    first_step = DEFAULT_STEP
    second_step = "step-material-inventory"

    for step in (first_step, second_step):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=step,
            task_type="hara",
        )
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=write_step_result(run_dir, step),
        )

    first_context = (
        run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    )
    first_dispatch = step_worker_dispatch_path(run_dir, "ingest", first_step)
    second_context = (
        run_dir / "orchestration/context_packages/ingest/step-material-inventory.json"
    )
    second_dispatch = step_worker_dispatch_path(run_dir, "ingest", second_step)
    ledger_path = progress_ledger_path(run_dir)
    snapshots = {
        path: path.read_bytes()
        for path in (
            first_context,
            first_dispatch,
            second_context,
            second_dispatch,
            ledger_path,
        )
    }
    original_write_json = step_worker_dispatch_module.write_json

    def fail_final_dispatch_write(path, payload):
        if path == first_dispatch and payload.get("kind") == "step_worker_dispatch":
            raise OSError("injected redispatch write failure")
        original_write_json(path, payload)

    monkeypatch.setattr(
        step_worker_dispatch_module,
        "write_json",
        fail_final_dispatch_write,
    )

    with pytest.raises(OSError, match="injected redispatch write failure"):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=first_step,
            task_type="hara",
            overwrite_package=True,
            overwrite_dispatch=True,
        )

    for path, content in snapshots.items():
        assert path.read_bytes() == content


def test_failed_redispatch_prepare_restores_existing_metadata(tmp_path):
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
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        step_result=step_result,
        review_result=review_result,
    )

    package_path = run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    ledger_path = progress_ledger_path(run_dir)
    before = {
        package_path: package_path.read_bytes(),
        dispatch_path: dispatch_path.read_bytes(),
        ledger_path: ledger_path.read_bytes(),
    }

    with pytest.raises(ContextPackageError, match="run ref does not exist"):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            task_type="hara",
            input_refs=["stage_reviews/ingest/missing.json"],
            overwrite_package=True,
            overwrite_dispatch=True,
        )

    for path, content in before.items():
        assert path.read_bytes() == content


def test_redispatch_rejects_an_invalid_existing_dispatch_without_writes(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    dispatch_path = step_worker_dispatch_path(run_dir, "ingest", DEFAULT_STEP)
    package_path = (
        run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    )
    ledger_path = progress_ledger_path(run_dir)
    before_package = package_path.read_bytes()
    before_ledger = ledger_path.read_bytes()
    dispatch_path.write_text("{not json", encoding="utf-8")
    before_dispatch = dispatch_path.read_bytes()

    with pytest.raises(StepWorkerDispatchError, match="invalid JSON"):
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=DEFAULT_STEP,
            task_type="hara",
            overwrite_package=True,
            overwrite_dispatch=True,
        )

    assert package_path.read_bytes() == before_package
    assert ledger_path.read_bytes() == before_ledger
    assert dispatch_path.read_bytes() == before_dispatch


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


def test_run_dir_validation_requires_matching_context_package_hash_but_allows_stale_ledger_hash(tmp_path):
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
    assert validate_step_worker_dispatch(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload

    payload["context_package_ref"]["sha256"] = VALID_HASH
    assert_invalid(payload, "sha256 mismatch", run_dir=run_dir)


def test_run_dir_validation_requires_canonical_context_package_ref_path(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    canonical_path = run_dir / payload["context_package_ref"]["path"]
    alternate_path = run_dir / "orchestration/context_packages/ingest/alternate.json"
    write(alternate_path, canonical_path.read_text(encoding="utf-8"))
    payload["context_package_ref"] = {
        "path": "orchestration/context_packages/ingest/alternate.json",
        "sha256": sha256_file(alternate_path),
    }

    assert_invalid(payload, "canonical", repo_root=repo_root, run_dir=run_dir)


def test_run_dir_validation_requires_canonical_progress_ledger_ref_path(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    canonical_path = progress_ledger_path(run_dir)
    alternate_path = run_dir / "orchestration/alternate_progress_ledger.json"
    write(alternate_path, canonical_path.read_text(encoding="utf-8"))
    payload["progress_ledger_ref"] = {
        "path": "orchestration/alternate_progress_ledger.json",
        "sha256": sha256_file(alternate_path),
    }

    assert_invalid(payload, "canonical", repo_root=repo_root, run_dir=run_dir)


def test_run_dir_validation_requires_ledger_entry_bound_to_dispatch_context(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    ledger_path = progress_ledger_path(run_dir)
    ledger = read_json(ledger_path)
    ledger["entries"] = []
    write(ledger_path, json.dumps(ledger))

    assert_invalid(
        payload,
        "ledger entry.*context_package_ref",
        repo_root=repo_root,
        run_dir=run_dir,
    )


def test_run_dir_validation_rejects_unbound_ledger_context_package_ref(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    ledger_path = progress_ledger_path(run_dir)
    ledger = read_json(ledger_path)
    ledger["entries"][0]["context_package_ref"] = None
    write(ledger_path, json.dumps(ledger))

    assert_invalid(
        payload,
        "ledger entry.*context_package_ref",
        repo_root=repo_root,
        run_dir=run_dir,
    )


def test_run_dir_validation_requires_progress_ledger_ref_to_exist(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    progress_ledger_path(run_dir).unlink()

    assert_invalid(payload, "run path does not exist", repo_root=repo_root, run_dir=run_dir)


def test_run_dir_validation_requires_progress_ledger_ref_to_be_valid_ledger(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    payload = prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=DEFAULT_STEP,
        task_type="hara",
    )
    write(progress_ledger_path(run_dir), "{}")

    assert_invalid(payload, "missing required fields", repo_root=repo_root, run_dir=run_dir)


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
