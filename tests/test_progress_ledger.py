import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.context_packages import build_step_context_package
from ai_writing_plugin.progress_ledger import (
    ProgressLedgerError,
    init_progress_ledger,
    progress_ledger_path,
    record_step_progress,
    validate_progress_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_HASH = "0" * 64


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

    write(repo_root / "skills" / "step-input-materials" / "SKILL.md", "wrapper")
    write(
        repo_root / "skills" / "workflow-steps" / "step-input-materials" / "SKILL.md",
        "canonical",
    )
    write(run_dir / "task_brief.json", '{"task_type":"hara"}')
    write(run_dir / "manifest.json", "{}")
    write(run_dir / "stage_reviews" / "ingest" / "issues.json", "{}")

    package = build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        task_type="hara",
    )
    package_path = run_dir / "orchestration/context_packages/ingest/step-input-materials.json"

    step_result = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": "step-input-materials",
        "status": "done",
        "artifact_paths": ["manifest.json"],
        "artifact_hashes": {"manifest.json": sha256_text("{}")},
        "summary": "Step completed and artifacts were written.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }
    step_result_path = run_dir / "orchestration/step_results/step-input-materials.json"
    write(step_result_path, json.dumps(step_result))

    review_result = {
        "kind": "review_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": "step-input-materials",
        "status": "done",
        "review_package_paths": ["stage_reviews/ingest/issues.json"],
        "review_package_hashes": {
            "stage_reviews/ingest/issues.json": sha256_text("{}"),
        },
        "summary": "Review package complete and ready for user gate.",
        "blocking_issues_count": 1,
        "next_gate_status": "needs_user_decision",
    }
    review_result_path = run_dir / "orchestration/review_results/ingest/step-input-materials.json"
    write(review_result_path, json.dumps(review_result))

    return repo_root, run_dir, package, package_path, step_result_path, review_result_path


def valid_ledger(**overrides):
    payload = {
        "kind": "progress_ledger",
        "schema_version": 1,
        "run_id": "demo-run",
        "created_at": "2026-07-08T00:00:00+00:00",
        "updated_at": "2026-07-08T00:00:00+00:00",
        "entries": [
            {
                "stage": "ingest",
                "step": "step-input-materials",
                "status": "done",
                "updated_at": "2026-07-08T00:00:00+00:00",
                "context_package_ref": ref(
                    "orchestration/context_packages/ingest/step-input-materials.json"
                ),
                "step_result_ref": ref(
                    "orchestration/step_results/step-input-materials.json"
                ),
                "review_result_ref": ref(
                    "orchestration/review_results/ingest/step-input-materials.json"
                ),
                "blocking_issues_count": 0,
                "next_gate_status": "pending_user_confirmation",
            }
        ],
    }
    payload.update(overrides)
    return payload


def assert_invalid(payload, expected_message: str, *, run_dir=None):
    with pytest.raises(ProgressLedgerError, match=expected_message):
        validate_progress_ledger(payload, run_dir=run_dir)


def test_init_progress_ledger_writes_fixed_path_and_empty_entries(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"

    payload = init_progress_ledger(run_dir)

    ledger_path = run_dir / "orchestration" / "progress_ledger.json"
    assert progress_ledger_path(run_dir) == ledger_path
    assert ledger_path.is_file()
    assert read_json(ledger_path) == payload
    assert payload["kind"] == "progress_ledger"
    assert payload["schema_version"] == 1
    assert payload["run_id"] == "demo-run"
    assert payload["entries"] == []


def test_init_progress_ledger_refuses_existing_file_unless_overwrite(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    init_progress_ledger(run_dir)

    with pytest.raises(ProgressLedgerError, match="already exists"):
        init_progress_ledger(run_dir)

    payload = init_progress_ledger(run_dir, overwrite=True)
    assert payload["entries"] == []


def test_record_step_progress_upserts_entry_with_run_relative_refs(tmp_path):
    _, run_dir, _, package_path, step_result_path, review_result_path = create_repo_and_run(
        tmp_path
    )
    init_progress_ledger(run_dir)

    payload = record_step_progress(
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        status="done",
        context_package=package_path,
        step_result=step_result_path.relative_to(run_dir).as_posix(),
        review_result=review_result_path,
    )

    assert len(payload["entries"]) == 1
    entry = payload["entries"][0]
    assert entry["stage"] == "ingest"
    assert entry["step"] == "step-input-materials"
    assert entry["status"] == "done"
    assert entry["context_package_ref"] == {
        "path": "orchestration/context_packages/ingest/step-input-materials.json",
        "sha256": sha256_file(package_path),
    }
    assert entry["step_result_ref"] == {
        "path": "orchestration/step_results/step-input-materials.json",
        "sha256": sha256_file(step_result_path),
    }
    assert entry["review_result_ref"] == {
        "path": "orchestration/review_results/ingest/step-input-materials.json",
        "sha256": sha256_file(review_result_path),
    }
    assert entry["blocking_issues_count"] == 1
    assert entry["next_gate_status"] == "needs_user_decision"
    assert read_json(progress_ledger_path(run_dir)) == payload


def test_record_step_progress_updates_existing_entry_in_place(tmp_path):
    _, run_dir, _, package_path, step_result_path, _ = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)

    record_step_progress(
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        status="context_ready",
        context_package=package_path,
    )
    payload = record_step_progress(
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        status="done",
        step_result=step_result_path,
    )

    assert len(payload["entries"]) == 1
    entry = payload["entries"][0]
    assert entry["status"] == "done"
    assert entry["context_package_ref"]["path"].endswith("step-input-materials.json")
    assert entry["step_result_ref"]["path"] == "orchestration/step_results/step-input-materials.json"


@pytest.mark.parametrize(
    "field",
    ["content", "text", "artifact_body", "result_body", "package_body", "instructions"],
)
def test_rejects_unknown_or_body_like_top_level_fields(field):
    payload = valid_ledger()
    payload[field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "field",
    ["content", "text", "artifact_body", "result_body", "package_body", "instructions"],
)
def test_rejects_unknown_or_body_like_entry_fields(field):
    payload = valid_ledger()
    payload["entries"][0][field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "entry_override, message",
    [
        ({"stage": "unknown"}, "invalid stage"),
        ({"step": "step-not-real"}, "invalid step"),
        ({"status": "finished"}, "invalid status"),
        ({"blocking_issues_count": -1}, "blocking_issues_count"),
        ({"next_gate_status": ""}, "next_gate_status"),
    ],
)
def test_rejects_invalid_entry_scalars(entry_override, message):
    payload = valid_ledger()
    payload["entries"][0].update(entry_override)

    assert_invalid(payload, message)


def test_rejects_duplicate_step_entries():
    first = valid_ledger()["entries"][0]
    payload = valid_ledger(entries=[first, dict(first)])

    assert_invalid(payload, "duplicate ledger entry")


@pytest.mark.parametrize(
    "bad_ref, message",
    [
        (ref("/absolute.json"), "relative POSIX path"),
        (ref("../outside.json"), "must not contain '..'"),
        (ref("plans\\outline.json"), "must use POSIX separators"),
        (ref("runs/demo-run/orchestration/step_results/x.json"), "must not start with runs/"),
        (ref("examples/demo/task.yaml"), "outside runtime result boundary"),
        (ref("docs/maintainers/PLAN.md"), "outside runtime result boundary"),
        (ref("contracts/CURRENT_ARTIFACT_CONTRACTS.md"), "outside runtime result boundary"),
    ],
)
def test_rejects_refs_outside_run_boundary(bad_ref, message):
    payload = valid_ledger()
    payload["entries"][0]["step_result_ref"] = bad_ref

    assert_invalid(payload, message)


def test_run_dir_validation_requires_existing_files_and_matching_hashes(tmp_path):
    _, run_dir, _, package_path, step_result_path, review_result_path = create_repo_and_run(
        tmp_path
    )
    payload = valid_ledger(
        entries=[
            {
                **valid_ledger()["entries"][0],
                "context_package_ref": ref(
                    "orchestration/context_packages/ingest/step-input-materials.json",
                    sha256_file(package_path),
                ),
                "step_result_ref": ref(
                    "orchestration/step_results/step-input-materials.json",
                    sha256_file(step_result_path),
                ),
                "review_result_ref": ref(
                    "orchestration/review_results/ingest/step-input-materials.json",
                    sha256_file(review_result_path),
                ),
                "blocking_issues_count": 1,
                "next_gate_status": "needs_user_decision",
            }
        ],
    )

    assert validate_progress_ledger(payload, run_dir=run_dir) == payload

    missing = valid_ledger(
        entries=[
            {
                **payload["entries"][0],
                "step_result_ref": ref("orchestration/step_results/missing.json"),
            }
        ]
    )
    assert_invalid(missing, "ref path does not exist", run_dir=run_dir)

    wrong_hash = valid_ledger(
        entries=[
            {
                **payload["entries"][0],
                "step_result_ref": ref(
                    "orchestration/step_results/step-input-materials.json",
                    VALID_HASH,
                ),
            }
        ]
    )
    assert_invalid(wrong_hash, "sha256 mismatch", run_dir=run_dir)


def test_record_step_progress_delegates_to_context_package_and_result_validators(tmp_path):
    _, run_dir, _, package_path, step_result_path, _ = create_repo_and_run(tmp_path)
    init_progress_ledger(run_dir)
    bad_result = read_json(step_result_path)
    bad_result["status"] = "finished"
    write(step_result_path, json.dumps(bad_result))

    with pytest.raises(ProgressLedgerError, match="invalid status"):
        record_step_progress(
            run_dir=run_dir,
            stage="ingest",
            step="step-input-materials",
            status="done",
            context_package=package_path,
            step_result=step_result_path,
        )


def test_cli_initializes_records_and_validates_progress_ledger(tmp_path):
    _, run_dir, _, package_path, step_result_path, review_result_path = create_repo_and_run(
        tmp_path
    )

    init_cmd = [
        sys.executable,
        "-m",
        "ai_writing_plugin",
        "init-progress-ledger",
        "--run-dir",
        str(run_dir),
    ]
    first = subprocess.run(init_cmd, cwd=ROOT, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    assert first.stdout.strip() == str(progress_ledger_path(run_dir))

    second = subprocess.run(init_cmd, cwd=ROOT, text=True, capture_output=True)
    assert second.returncode == 2
    assert "already exists" in second.stderr

    overwrite = subprocess.run(
        init_cmd + ["--overwrite"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert overwrite.returncode == 0, overwrite.stderr

    record = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "record-step-progress",
            "--run-dir",
            str(run_dir),
            "--stage",
            "ingest",
            "--step",
            "step-input-materials",
            "--status",
            "done",
            "--context-package",
            str(package_path),
            "--step-result",
            str(step_result_path.relative_to(run_dir)),
            "--review-result",
            str(review_result_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert record.returncode == 0, record.stderr
    assert record.stdout.strip() == str(progress_ledger_path(run_dir))

    valid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-progress-ledger",
            "--path",
            str(progress_ledger_path(run_dir)),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert valid.returncode == 0, valid.stderr
    assert valid.stdout.strip() == "progress ledger valid"

    ledger = read_json(progress_ledger_path(run_dir))
    ledger["entries"][0]["status"] = "finished"
    write(progress_ledger_path(run_dir), json.dumps(ledger))
    invalid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-progress-ledger",
            "--path",
            str(progress_ledger_path(run_dir)),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode == 2
    assert "invalid status" in invalid.stderr
