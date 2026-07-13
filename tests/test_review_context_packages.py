import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import ai_writing_plugin.review_context_packages as review_context_packages_module
from ai_writing_plugin.context_packages import build_step_context_package
from ai_writing_plugin.input_refs import build_input_refs, write_input_refs
from ai_writing_plugin.progress_ledger import (
    init_progress_ledger,
    progress_ledger_path,
    validate_progress_ledger,
)
from ai_writing_plugin.review_context_packages import (
    ReviewContextPackageError,
    build_review_context_package,
    review_context_package_path,
    validate_review_context_package,
)
from ai_writing_plugin.short_results import validate_review_result
from ai_writing_plugin.stage_gate_results import build_stage_gate_result
from ai_writing_plugin.stage_review_issues import (
    StageReviewIssueError,
    build_issues_index,
    issue_detail_path,
    issues_index_path,
    validate_issues_index,
)
from ai_writing_plugin.step_worker_dispatch import (
    complete_step_worker_dispatch,
    prepare_step_worker_dispatch,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_HASH = "0" * 64
STEPS = ["step-input-materials", "step-material-inventory"]


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


def write_step_result(run_dir: Path, step: str) -> Path:
    payload = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": step,
        "status": "done",
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
    status: str = "done",
) -> Path:
    review_package_path = run_dir / "review" / f"{step}.md"
    write(review_package_path, f"Review for {step}.\n")
    relative_review_path = review_package_path.relative_to(run_dir).as_posix()
    payload = {
        "kind": "review_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": step,
        "status": status,
        "review_package_paths": [relative_review_path],
        "review_package_hashes": {
            relative_review_path: sha256_file(review_package_path),
        },
        "summary": "Per-step review completed and is ready for the user gate.",
        "blocking_issues_count": 1 if status == "needs_revision" else 0,
        "next_gate_status": "needs_user_decision",
    }
    path = run_dir / "orchestration" / "review_results" / "ingest" / f"{step}.json"
    write(path, json.dumps(payload))
    return path


def write_artifact_step_result(
    run_dir: Path,
    step: str,
    content: str,
) -> tuple[Path, Path]:
    artifact_path = run_dir / "artifacts" / f"{step}.md"
    write(artifact_path, content)
    artifact_ref = artifact_path.relative_to(run_dir).as_posix()
    payload = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": step,
        "status": "done",
        "artifact_paths": [artifact_ref],
        "artifact_hashes": {artifact_ref: sha256_file(artifact_path)},
        "summary": "Step completed and artifacts were written.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }
    result_path = run_dir / "orchestration" / "step_results" / f"{step}.json"
    write(result_path, json.dumps(payload))
    return artifact_path, result_path


def prepare_single_step_a2_reset(tmp_path: Path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)
    step = STEPS[0]
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=step,
        task_type="hara",
    )
    artifact_path, step_result = write_artifact_step_result(run_dir, step, "initial\n")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=step_result,
    )
    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=[step],
    )
    review_result = write_review_result(run_dir, step, status="needs_revision")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=step_result,
        review_result=review_result,
    )
    build_issues_index(
        run_dir,
        "ingest",
        issues=[
            {
                "issue_id": "P1-STALE-ARTIFACT",
                "severity": "P1",
                "category": "missing_evidence",
                "title": "Revise the cited artifact.",
                "summary": "A2 must update the artifact cited by this issue.",
                "artifact_refs": [
                    {
                        "path": artifact_path.relative_to(run_dir).as_posix(),
                        "sha256": sha256_file(artifact_path),
                    }
                ],
            }
        ],
    )
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=step,
        task_type="hara",
        input_refs=["stage_reviews/ingest/issues_index.json"],
        overwrite_package=True,
        overwrite_dispatch=True,
    )
    _, revised_result = write_artifact_step_result(run_dir, step, "revised\n")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=revised_result,
    )
    return repo_root, run_dir, step


def create_repo_and_run(tmp_path: Path):
    repo_root = tmp_path / "repo"
    run_dir = tmp_path / "runs" / "demo-run"
    for step in STEPS:
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
    return repo_root, run_dir


def write_context_packages(repo_root: Path, run_dir: Path) -> list[Path]:
    paths = []
    for step in STEPS:
        build_step_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=step,
            task_type="hara",
        )
        paths.append(run_dir / "orchestration" / "context_packages" / "ingest" / f"{step}.json")
    return paths


def valid_package(**overrides):
    payload = {
        "kind": "review_context_package",
        "schema_version": 2,
        "run_id": "demo-run",
        "stage": "ingest",
        "steps": STEPS,
        "created_at": "2026-07-08T00:00:00+00:00",
        "context_package_refs": [
            ref("orchestration/context_packages/ingest/step-input-materials.json"),
            ref("orchestration/context_packages/ingest/step-material-inventory.json"),
        ],
        "step_result_refs": [
            ref("orchestration/step_results/step-input-materials.json"),
            ref("orchestration/step_results/step-material-inventory.json"),
        ],
        "stage_review_refs": [
            ref("stage_reviews/ingest/review_prompt.md"),
            ref("stage_reviews/ingest/review_units.json"),
        ],
        "result_paths": {
            "stage_gate_result": "orchestration/stage_gate_results/ingest.json",
        },
        "constraints": {
            "paths_and_hashes_only": True,
            "no_artifact_body": True,
            "no_inline_review_details": True,
            "main_agent_passes_package_path_only": True,
        },
    }
    payload.update(overrides)
    return payload


def assert_invalid(payload, expected_message: str, **kwargs):
    with pytest.raises(ReviewContextPackageError, match=expected_message):
        validate_review_context_package(payload, **kwargs)


def test_build_review_context_package_collects_step_results_and_stage_review_refs(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    context_paths = write_context_packages(repo_root, run_dir)
    for step in STEPS:
        write_step_result(run_dir, step)

    stage_review_dir = run_dir / "stage_reviews" / "ingest"
    write(stage_review_dir / "review_prompt.md", "prompt")
    write(stage_review_dir / "review_units.json", '{"units":[]}')
    write(stage_review_dir / "issues_schema.json", '{"type":"object"}')
    write(stage_review_dir / "review_context.json", '{"stage":"ingest"}')
    write(stage_review_dir / "issues.json", '{"not":"included in context package"}')
    build_issues_index(
        run_dir,
        "ingest",
        issues=[
            {
                "issue_id": "P1-001",
                "severity": "P1",
                "category": "missing_evidence",
                "title": "Missing cited evidence.",
                "summary": "Missing cited evidence.",
            }
        ],
    )

    payload = build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=STEPS,
    )

    package_path = review_context_package_path(run_dir, "ingest")
    assert package_path == run_dir / "orchestration/review_context_packages/ingest.json"
    assert package_path.is_file()
    assert read_json(package_path) == payload
    assert [item["path"] for item in payload["step_result_refs"]] == [
        "orchestration/step_results/step-input-materials.json",
        "orchestration/step_results/step-material-inventory.json",
    ]
    assert [item["path"] for item in payload["context_package_refs"]] == [
        "orchestration/context_packages/ingest/step-input-materials.json",
        "orchestration/context_packages/ingest/step-material-inventory.json",
    ]
    assert [item["path"] for item in payload["stage_review_refs"]] == [
        "stage_reviews/ingest/review_prompt.md",
        "stage_reviews/ingest/review_units.json",
        "stage_reviews/ingest/issues_schema.json",
        "stage_reviews/ingest/review_context.json",
        "stage_reviews/ingest/issues_index.json",
    ]
    assert "stage_reviews/ingest/issues.json" not in [
        item["path"] for item in payload["stage_review_refs"]
    ]
    assert "stage_reviews/ingest/issues/P1-001.json" not in [
        item["path"] for item in payload["stage_review_refs"]
    ]
    assert payload["step_result_refs"][0]["sha256"] == sha256_file(
        run_dir / "orchestration/step_results/step-input-materials.json"
    )
    assert payload["context_package_refs"][0]["sha256"] == sha256_file(context_paths[0])
    assert validate_review_context_package(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload


@pytest.mark.parametrize(
    "selected_steps",
    ([STEPS[0]], STEPS),
    ids=("single-step-stage", "multi-step-stage"),
)
def test_per_step_review_results_rebind_ledger_and_feed_stage_gate(
    tmp_path,
    selected_steps,
):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)
    step_result_paths: dict[str, Path] = {}

    for step in selected_steps:
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=step,
            task_type="hara",
        )
        step_result_path = write_step_result(run_dir, step)
        step_result_paths[step] = step_result_path
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result_path,
        )

    package = build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=selected_steps,
    )
    assert package["steps"] == selected_steps
    assert len(package["context_package_refs"]) == len(selected_steps)
    for step, context_ref in zip(
        selected_steps,
        package["context_package_refs"],
        strict=True,
    ):
        context_package = read_json(run_dir / context_ref["path"])
        assert context_package["result_paths"]["review_result"] == (
            f"orchestration/review_results/ingest/{step}.json"
        )

    review_result_paths: list[Path] = []
    for step in selected_steps:
        review_result_path = write_review_result(run_dir, step)
        review_result_paths.append(review_result_path)
        assert validate_review_result(
            read_json(review_result_path),
            run_dir=run_dir,
        )["step"] == step
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result_paths[step],
            review_result=review_result_path,
        )

    ledger = read_json(progress_ledger_path(run_dir))
    assert validate_progress_ledger(ledger, run_dir=run_dir) == ledger
    entries_by_step = {entry["step"]: entry for entry in ledger["entries"]}
    for step, review_result_path in zip(
        selected_steps,
        review_result_paths,
        strict=True,
    ):
        entry = entries_by_step[step]
        assert entry["step_result_ref"] == {
            "path": step_result_paths[step].relative_to(run_dir).as_posix(),
            "sha256": sha256_file(step_result_paths[step]),
        }
        assert entry["review_result_ref"] == {
            "path": review_result_path.relative_to(run_dir).as_posix(),
            "sha256": sha256_file(review_result_path),
        }
        assert entry["status"] == "done"
        assert entry["blocking_issues_count"] == 0
        assert entry["next_gate_status"] == "needs_user_decision"

    gate = build_stage_gate_result(
        run_dir=run_dir,
        stage="ingest",
        review_result_paths=review_result_paths,
    )
    assert gate["status"] == "pending_user_confirmation"
    assert gate["review_result_refs"] == [
        {
            "path": path.relative_to(run_dir).as_posix(),
            "sha256": sha256_file(path),
        }
        for path in review_result_paths
    ]


def test_multi_step_revision_cycle_resets_stale_bindings_and_rebinds_latest_results(
    tmp_path,
):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    write(run_dir / "inputs" / "upstream.json", '{"version":1}')
    init_progress_ledger(run_dir)

    artifact_paths: dict[str, Path] = {}
    step_result_paths: dict[str, Path] = {}
    for step in STEPS:
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=step,
            task_type="hara",
            input_refs=["inputs/upstream.json"] if step == STEPS[1] else None,
        )
        artifact_path, step_result_path = write_artifact_step_result(
            run_dir,
            step,
            f"initial {step}\n",
        )
        artifact_paths[step] = artifact_path
        step_result_paths[step] = step_result_path
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result_path,
        )

    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=STEPS,
    )
    first_review_paths = {
        STEPS[0]: write_review_result(run_dir, STEPS[0]),
        STEPS[1]: write_review_result(
            run_dir,
            STEPS[1],
            status="needs_revision",
        ),
    }
    for step in STEPS:
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result_paths[step],
            review_result=first_review_paths[step],
        )

    build_issues_index(
        run_dir,
        "ingest",
        issues=[
            {
                "issue_id": "P1-001",
                "severity": "P1",
                "category": "missing_evidence",
                "title": "Revise the material inventory.",
                "summary": "The material inventory needs a local correction.",
            }
        ],
    )
    issue_index_ref = "stage_reviews/ingest/issues_index.json"
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=STEPS[1],
        task_type="hara",
        input_refs=[issue_index_ref],
        overwrite_package=True,
        overwrite_dispatch=True,
    )

    ledger_after_redispatch = read_json(progress_ledger_path(run_dir))
    entries = {entry["step"]: entry for entry in ledger_after_redispatch["entries"]}
    assert entries[STEPS[0]]["step_result_ref"] is not None
    assert entries[STEPS[0]]["review_result_ref"] is not None
    assert entries[STEPS[1]]["status"] == "context_ready"
    assert entries[STEPS[1]]["step_result_ref"] is None
    assert entries[STEPS[1]]["review_result_ref"] is None
    assert entries[STEPS[1]]["blocking_issues_count"] == 0
    assert entries[STEPS[1]]["next_gate_status"] == "not_recorded"

    revised_context = read_json(
        run_dir
        / "orchestration"
        / "context_packages"
        / "ingest"
        / f"{STEPS[1]}.json"
    )
    assert [item["path"] for item in revised_context["run_refs"]] == [
        "task_brief.json",
        "artifacts/step-input-materials.md",
        "inputs/upstream.json",
        issue_index_ref,
    ]

    _, revised_step_result = write_artifact_step_result(
        run_dir,
        STEPS[1],
        "revised material inventory\n",
    )
    step_result_paths[STEPS[1]] = revised_step_result
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=STEPS[1],
        step_result=revised_step_result,
    )

    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=STEPS,
        overwrite=True,
    )
    ledger_before_rereview = read_json(progress_ledger_path(run_dir))
    entries = {entry["step"]: entry for entry in ledger_before_rereview["entries"]}
    for step in STEPS:
        assert entries[step]["step_result_ref"] == {
            "path": step_result_paths[step].relative_to(run_dir).as_posix(),
            "sha256": sha256_file(step_result_paths[step]),
        }
        assert entries[step]["review_result_ref"] is None
        assert entries[step]["status"] == "done"

    context_after_reset = read_json(
        run_dir
        / "orchestration"
        / "context_packages"
        / "ingest"
        / f"{STEPS[1]}.json"
    )
    assert issue_index_ref not in [item["path"] for item in context_after_reset["run_refs"]]
    assert read_json(review_context_package_path(run_dir, "ingest"))["stage_review_refs"] == []

    second_review_paths = {
        STEPS[0]: write_review_result(run_dir, STEPS[0]),
        STEPS[1]: write_review_result(
            run_dir,
            STEPS[1],
            status="needs_revision",
        ),
    }
    for step in STEPS:
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result_paths[step],
            review_result=second_review_paths[step],
        )

    build_issues_index(
        run_dir,
        "ingest",
        issues=[
            {
                "issue_id": "P1-002",
                "severity": "P1",
                "category": "traceability",
                "title": "Revise the material inventory again.",
                "summary": "The second review found another local correction.",
            }
        ],
        overwrite=True,
    )
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=STEPS[1],
        task_type="hara",
        input_refs=[issue_index_ref],
        overwrite_package=True,
        overwrite_dispatch=True,
    )
    _, second_revised_step_result = write_artifact_step_result(
        run_dir,
        STEPS[1],
        "second revised material inventory\n",
    )
    step_result_paths[STEPS[1]] = second_revised_step_result
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=STEPS[1],
        step_result=second_revised_step_result,
    )
    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=STEPS,
        overwrite=True,
    )

    final_review_paths = [write_review_result(run_dir, step) for step in STEPS]
    for step, review_result_path in zip(STEPS, final_review_paths, strict=True):
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result_paths[step],
            review_result=review_result_path,
        )

    final_ledger = read_json(progress_ledger_path(run_dir))
    assert validate_progress_ledger(final_ledger, run_dir=run_dir) == final_ledger
    gate = build_stage_gate_result(
        run_dir=run_dir,
        stage="ingest",
        review_result_paths=final_review_paths,
    )
    assert gate["status"] == "pending_user_confirmation"
    assert [item["path"] for item in gate["review_result_refs"]] == [
        path.relative_to(run_dir).as_posix() for path in final_review_paths
    ]


def test_review_cycle_overwrite_rolls_back_all_metadata_when_final_write_fails(
    tmp_path,
    monkeypatch,
):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)
    step = STEPS[0]
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=step,
        task_type="hara",
    )
    _, step_result = write_artifact_step_result(run_dir, step, "initial\n")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=step_result,
    )
    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=[step],
    )
    review_result = write_review_result(run_dir, step, status="needs_revision")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=step_result,
        review_result=review_result,
    )
    build_issues_index(
        run_dir,
        "ingest",
        issues=[
            {
                "issue_id": "P1-ROLLBACK",
                "severity": "P1",
                "category": "rollback",
                "title": "Exercise transaction rollback.",
                "summary": "The review cycle reset must be all-or-nothing.",
            }
        ],
    )
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=step,
        task_type="hara",
        input_refs=["stage_reviews/ingest/issues_index.json"],
        overwrite_package=True,
        overwrite_dispatch=True,
    )
    _, revised_result = write_artifact_step_result(run_dir, step, "revised\n")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=revised_result,
    )
    stale_review_result = write_review_result(run_dir, step, status="needs_revision")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=revised_result,
        review_result=stale_review_result,
    )

    tracked_paths = [
        run_dir / "orchestration/context_packages/ingest/step-input-materials.json",
        run_dir / "orchestration/worker_dispatches/ingest/step-input-materials.json",
        progress_ledger_path(run_dir),
        review_context_package_path(run_dir, "ingest"),
    ]
    before = {path: path.read_bytes() for path in tracked_paths}
    original_write_json = review_context_packages_module.write_json

    def fail_review_package_write(path, payload):
        if path == review_context_package_path(run_dir, "ingest"):
            raise OSError("injected review package write failure")
        original_write_json(path, payload)

    monkeypatch.setattr(
        review_context_packages_module,
        "write_json",
        fail_review_package_write,
    )

    with pytest.raises(OSError, match="injected review package write failure"):
        build_review_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            steps=[step],
            overwrite=True,
        )

    for path, content in before.items():
        assert path.read_bytes() == content


def test_review_cycle_overwrite_rejects_malformed_existing_package_without_writes(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)
    step = STEPS[0]
    prepare_step_worker_dispatch(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step=step,
        task_type="hara",
    )
    _, step_result = write_artifact_step_result(run_dir, step, "initial\n")
    complete_step_worker_dispatch(
        run_dir=run_dir,
        stage="ingest",
        step=step,
        step_result=step_result,
    )
    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=[step],
    )
    package_path = review_context_package_path(run_dir, "ingest")
    write(package_path, "{malformed\n")
    tracked_paths = [
        run_dir / "orchestration/context_packages/ingest/step-input-materials.json",
        run_dir / "orchestration/worker_dispatches/ingest/step-input-materials.json",
        progress_ledger_path(run_dir),
        package_path,
    ]
    before = {path: path.read_bytes() for path in tracked_paths}

    with pytest.raises(ReviewContextPackageError, match="invalid JSON"):
        build_review_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            steps=[step],
            overwrite=True,
        )

    for path, content in before.items():
        assert path.read_bytes() == content


def test_review_cycle_overwrite_accepts_stale_issue_artifact_ref_after_a2(tmp_path):
    repo_root, run_dir, step = prepare_single_step_a2_reset(tmp_path)
    index_path = issues_index_path(run_dir, "ingest")

    with pytest.raises(StageReviewIssueError, match="sha256 mismatch"):
        validate_issues_index(read_json(index_path), run_dir=run_dir)

    payload = build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=[step],
        overwrite=True,
    )

    assert payload["stage_review_refs"] == []
    context = read_json(
        run_dir / f"orchestration/context_packages/ingest/{step}.json"
    )
    assert "stage_reviews/ingest/issues_index.json" not in {
        item["path"] for item in context["run_refs"]
    }


def test_review_cycle_overwrite_still_rejects_broken_issue_detail_binding(tmp_path):
    repo_root, run_dir, step = prepare_single_step_a2_reset(tmp_path)
    detail_path = issue_detail_path(run_dir, "ingest", "P1-STALE-ARTIFACT")
    detail = read_json(detail_path)
    detail["summary"] = "The detail changed without rebuilding the index."
    write(detail_path, json.dumps(detail))
    tracked_paths = [
        run_dir / f"orchestration/context_packages/ingest/{step}.json",
        run_dir / f"orchestration/worker_dispatches/ingest/{step}.json",
        progress_ledger_path(run_dir),
        review_context_package_path(run_dir, "ingest"),
    ]
    before = {path: path.read_bytes() for path in tracked_paths}

    with pytest.raises(ReviewContextPackageError, match="sha256 mismatch"):
        build_review_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            steps=[step],
            overwrite=True,
        )

    for path, content in before.items():
        assert path.read_bytes() == content


@pytest.mark.parametrize(
    "mutate",
    [
        lambda payload: payload.update({"run_id": "another-run"}),
        lambda payload: payload.update(
            {
                "steps": [STEPS[1]],
                "context_package_refs": [
                    {
                        "path": (
                            "orchestration/context_packages/ingest/"
                            f"{STEPS[1]}.json"
                        ),
                        "sha256": VALID_HASH,
                    }
                ],
                "step_result_refs": [
                    {
                        "path": f"orchestration/step_results/{STEPS[1]}.json",
                        "sha256": VALID_HASH,
                    }
                ],
            }
        ),
    ],
    ids=("run-id", "requested-steps"),
)
def test_review_cycle_overwrite_requires_existing_package_identity_without_writes(
    tmp_path,
    mutate,
):
    repo_root, run_dir, step = prepare_single_step_a2_reset(tmp_path)
    package_path = review_context_package_path(run_dir, "ingest")
    old_package = read_json(package_path)
    mutate(old_package)
    write(package_path, json.dumps(old_package))
    tracked_paths = [
        run_dir / f"orchestration/context_packages/ingest/{step}.json",
        run_dir / f"orchestration/worker_dispatches/ingest/{step}.json",
        progress_ledger_path(run_dir),
        package_path,
    ]
    before = {path: path.read_bytes() for path in tracked_paths}

    with pytest.raises(ReviewContextPackageError, match="existing review context package"):
        build_review_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            steps=[step],
            overwrite=True,
        )

    for path, content in before.items():
        assert path.read_bytes() == content


def test_review_cycle_overwrite_rejects_omitted_step_result_bound_stage_entry(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)
    for step in STEPS:
        prepare_step_worker_dispatch(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            step=step,
            task_type="hara",
        )
        _, step_result = write_artifact_step_result(run_dir, step, f"{step}\n")
        complete_step_worker_dispatch(
            run_dir=run_dir,
            stage="ingest",
            step=step,
            step_result=step_result,
        )
    build_review_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        steps=STEPS,
    )
    package_path = review_context_package_path(run_dir, "ingest")
    package_path.unlink()
    tracked_paths = [
        run_dir / f"orchestration/context_packages/ingest/{step}.json"
        for step in STEPS
    ] + [
        run_dir / f"orchestration/worker_dispatches/ingest/{step}.json"
        for step in STEPS
    ] + [progress_ledger_path(run_dir)]
    before = {path: path.read_bytes() for path in tracked_paths}

    with pytest.raises(ReviewContextPackageError, match="omits StepResult-bound"):
        build_review_context_package(
            repo_root=repo_root,
            run_dir=run_dir,
            stage="ingest",
            steps=[STEPS[0]],
            overwrite=True,
        )

    for path, content in before.items():
        assert path.read_bytes() == content


def test_accepts_valid_review_context_package_without_reading_bodies():
    payload = valid_package()

    assert validate_review_context_package(payload) == payload


@pytest.mark.parametrize(
    "field",
    ["content", "text", "artifact_body", "review_units_body", "issues_body", "instructions"],
)
def test_rejects_unknown_or_body_like_fields(field):
    payload = valid_package()
    payload[field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "override, message",
    [
        ({"stage": "unknown"}, "invalid stage"),
        ({"schema_version": 1}, "schema_version"),
        ({"steps": ["step-not-real"]}, "invalid step"),
        ({"steps": STEPS + [STEPS[0]]}, "steps must not contain duplicates"),
        ({"created_at": "not-a-date"}, "created_at"),
        ({"constraints": {"paths_and_hashes_only": True}}, "constraints"),
    ],
)
def test_rejects_invalid_scalar_fields(override, message):
    assert_invalid(valid_package(**override), message)


@pytest.mark.parametrize(
    "bad_ref, message",
    [
        (ref("/absolute.json"), "relative POSIX path"),
        (ref("../outside.json"), "must not contain '..'"),
        (ref("plans\\review.json"), "must use POSIX separators"),
        (ref("runs/demo-run/orchestration/result.json"), "must not start with runs/"),
        (ref("examples/demo/task.yaml"), "outside runtime result boundary"),
        (ref("docs/maintainers/PLAN.md"), "outside runtime result boundary"),
        (ref("contracts/CURRENT_ARTIFACT_CONTRACTS.md"), "outside runtime result boundary"),
    ],
)
def test_rejects_refs_outside_run_boundary(bad_ref, message):
    payload = valid_package(step_result_refs=[bad_ref])

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    "bad_path",
    [
        "stage_reviews/ingest/issues.json",
        "stage_reviews/ingest/issues/P1-001.json",
    ],
)
def test_rejects_stage_review_refs_outside_allowlist(bad_path):
    payload = valid_package(
        stage_review_refs=[
            ref(bad_path),
        ]
    )

    assert_invalid(payload, "stage_review_refs path is not allowed")


def test_validate_review_context_package_accepts_issues_index_with_matching_hash(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    context_paths = write_context_packages(repo_root, run_dir)
    for step in STEPS:
        write_step_result(run_dir, step)
    build_issues_index(
        run_dir,
        "ingest",
        issues=[
            {
                "issue_id": "P1-001",
                "severity": "P1",
                "category": "missing_evidence",
                "title": "Missing cited evidence.",
                "summary": "Missing cited evidence.",
            }
        ],
    )

    payload = valid_package(
        context_package_refs=[
            ref(
                "orchestration/context_packages/ingest/step-input-materials.json",
                sha256_file(context_paths[0]),
            ),
            ref(
                "orchestration/context_packages/ingest/step-material-inventory.json",
                sha256_file(context_paths[1]),
            ),
        ],
        step_result_refs=[
            ref(
                "orchestration/step_results/step-input-materials.json",
                sha256_file(run_dir / "orchestration/step_results/step-input-materials.json"),
            ),
            ref(
                "orchestration/step_results/step-material-inventory.json",
                sha256_file(run_dir / "orchestration/step_results/step-material-inventory.json"),
            ),
        ],
        stage_review_refs=[
            ref(
                "stage_reviews/ingest/issues_index.json",
                sha256_file(issues_index_path(run_dir, "ingest")),
            )
        ],
    )

    assert validate_review_context_package(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload

    payload["stage_review_refs"][0]["sha256"] = VALID_HASH
    assert_invalid(payload, "sha256 mismatch", run_dir=run_dir)


def test_run_dir_validation_requires_matching_hashes_and_step_result_payload(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    context_paths = write_context_packages(repo_root, run_dir)
    for step in STEPS:
        write_step_result(run_dir, step)
    write(run_dir / "stage_reviews" / "ingest" / "review_prompt.md", "prompt")

    payload = valid_package(
        context_package_refs=[
            ref(
                "orchestration/context_packages/ingest/step-input-materials.json",
                sha256_file(context_paths[0]),
            ),
            ref(
                "orchestration/context_packages/ingest/step-material-inventory.json",
                sha256_file(context_paths[1]),
            ),
        ],
        step_result_refs=[
            ref(
                "orchestration/step_results/step-input-materials.json",
                sha256_file(run_dir / "orchestration/step_results/step-input-materials.json"),
            ),
            ref(
                "orchestration/step_results/step-material-inventory.json",
                sha256_file(run_dir / "orchestration/step_results/step-material-inventory.json"),
            ),
        ],
        stage_review_refs=[
            ref(
                "stage_reviews/ingest/review_prompt.md",
                sha256_file(run_dir / "stage_reviews/ingest/review_prompt.md"),
            ),
        ],
    )
    assert validate_review_context_package(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload

    payload["step_result_refs"][0]["sha256"] = VALID_HASH
    assert_invalid(payload, "sha256 mismatch", run_dir=run_dir)


def test_run_dir_validation_rejects_context_package_hash_mismatch(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    context_paths = write_context_packages(repo_root, run_dir)
    for step in STEPS:
        write_step_result(run_dir, step)

    payload = valid_package(
        context_package_refs=[
            ref(
                "orchestration/context_packages/ingest/step-input-materials.json",
                VALID_HASH,
            ),
            ref(
                "orchestration/context_packages/ingest/step-material-inventory.json",
                sha256_file(context_paths[1]),
            ),
        ],
        step_result_refs=[
            ref(
                "orchestration/step_results/step-input-materials.json",
                sha256_file(run_dir / "orchestration/step_results/step-input-materials.json"),
            ),
            ref(
                "orchestration/step_results/step-material-inventory.json",
                sha256_file(run_dir / "orchestration/step_results/step-material-inventory.json"),
            ),
        ],
    )

    assert_invalid(payload, "sha256 mismatch", repo_root=repo_root, run_dir=run_dir)


def test_run_dir_validation_binds_each_step_result_payload_to_its_step(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    context_paths = write_context_packages(repo_root, run_dir)
    for step in STEPS:
        write_step_result(run_dir, step)
    first_result_path = run_dir / f"orchestration/step_results/{STEPS[0]}.json"
    first_result = read_json(first_result_path)
    first_result["step"] = STEPS[1]
    write(first_result_path, json.dumps(first_result))

    payload = valid_package(
        context_package_refs=[
            ref(
                f"orchestration/context_packages/ingest/{STEPS[0]}.json",
                sha256_file(context_paths[0]),
            ),
            ref(
                f"orchestration/context_packages/ingest/{STEPS[1]}.json",
                sha256_file(context_paths[1]),
            ),
        ],
        step_result_refs=[
            ref(
                f"orchestration/step_results/{STEPS[0]}.json",
                sha256_file(first_result_path),
            ),
            ref(
                f"orchestration/step_results/{STEPS[1]}.json",
                sha256_file(run_dir / f"orchestration/step_results/{STEPS[1]}.json"),
            ),
        ],
        stage_review_refs=[],
    )

    assert_invalid(
        payload,
        "StepResult stage and step must match package",
        repo_root=repo_root,
        run_dir=run_dir,
    )


def test_cli_builds_validates_and_reports_invalid_package(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    write_context_packages(repo_root, run_dir)
    write(run_dir / "stage_reviews" / "ingest" / "review_prompt.md", "prompt")
    for step in STEPS:
        write_step_result(run_dir, step)

    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "build-review-context-package",
            "--repo-root",
            str(repo_root),
            "--run-dir",
            str(run_dir),
            "--stage",
            "ingest",
            "--step",
            STEPS[0],
            "--step",
            STEPS[1],
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert build.returncode == 0, build.stderr
    package_path = review_context_package_path(run_dir, "ingest")
    assert build.stdout.strip() == str(package_path)

    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-review-context-package",
            "--path",
            str(package_path),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert validate.returncode == 0, validate.stderr
    assert validate.stdout.strip() == "review context package valid"

    package = read_json(package_path)
    package["stage"] = "unknown"
    write(package_path, json.dumps(package))
    invalid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-review-context-package",
            "--path",
            str(package_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode == 2
    assert "invalid stage" in invalid.stderr
