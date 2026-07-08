import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.short_results import (
    ShortResultError,
    validate_review_result,
    validate_step_result,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_HASH = "0" * 64


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def valid_step_result(**overrides):
    payload = {
        "kind": "step_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": "step-input-materials",
        "status": "done",
        "artifact_paths": ["manifest.json", "task_brief.json"],
        "artifact_hashes": {
            "manifest.json": VALID_HASH,
            "task_brief.json": VALID_HASH,
        },
        "summary": "Step completed and artifacts were written.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }
    payload.update(overrides)
    return payload


def valid_review_result(**overrides):
    payload = {
        "kind": "review_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": "step-input-materials",
        "status": "done",
        "review_package_paths": [
            "stage_reviews/ingest/review_prompt.md",
            "stage_reviews/ingest/review_units.json",
            "stage_reviews/ingest/issues.json",
        ],
        "review_package_hashes": {
            "stage_reviews/ingest/review_prompt.md": VALID_HASH,
            "stage_reviews/ingest/review_units.json": VALID_HASH,
            "stage_reviews/ingest/issues.json": VALID_HASH,
        },
        "summary": "Review package complete and ready for user gate.",
        "blocking_issues_count": 0,
        "next_gate_status": "pending_user_confirmation",
    }
    payload.update(overrides)
    return payload


def assert_invalid(payload, expected_message: str, *, review: bool = False, run_dir=None):
    validator = validate_review_result if review else validate_step_result
    with pytest.raises(ShortResultError, match=expected_message):
        validator(payload, run_dir=run_dir)


def test_accepts_valid_step_and_review_results_without_reading_artifacts():
    assert validate_step_result(valid_step_result()) == valid_step_result()
    assert validate_review_result(valid_review_result()) == valid_review_result()


@pytest.mark.parametrize(
    "field",
    ["content", "text", "artifact_bodies", "review_details", "extra"],
)
def test_rejects_unknown_or_body_like_fields(field):
    payload = valid_step_result()
    payload[field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "override, message",
    [
        ({"stage": "unknown"}, "invalid stage"),
        ({"step": "step-not-real"}, "invalid step"),
        ({"status": "finished"}, "invalid status"),
        ({"summary": "x" * 601}, "summary must be at most 600 characters"),
        ({"summary": "```markdown\nbody\n```"}, "summary must not contain code fences"),
        ({"blocking_issues_count": -1}, "blocking_issues_count"),
    ],
)
def test_rejects_invalid_scalar_fields(override, message):
    assert_invalid(valid_step_result(**override), message)


@pytest.mark.parametrize(
    "bad_path, message",
    [
        ("/absolute.md", "relative POSIX path"),
        ("../outside.md", "must not contain '..'"),
        ("plans\\outline.md", "must use POSIX separators"),
        ("runs/demo-run/manifest.json", "must not start with runs/"),
        ("examples/demo/task.yaml", "outside runtime result boundary"),
        ("docs/maintainers/PLAN.md", "outside runtime result boundary"),
        ("contracts/CURRENT_ARTIFACT_CONTRACTS.md", "outside runtime result boundary"),
    ],
)
def test_rejects_paths_outside_runtime_result_boundary(bad_path, message):
    payload = valid_step_result(
        artifact_paths=[bad_path],
        artifact_hashes={bad_path: VALID_HASH},
    )

    assert_invalid(payload, message)


def test_rejects_hashes_that_do_not_exactly_match_path_list():
    payload = valid_step_result(
        artifact_paths=["manifest.json"],
        artifact_hashes={"task_brief.json": VALID_HASH},
    )

    assert_invalid(payload, "hash keys must match path list")


def test_rejects_invalid_sha256_values():
    payload = valid_step_result(
        artifact_paths=["manifest.json"],
        artifact_hashes={"manifest.json": "ABC"},
    )

    assert_invalid(payload, "invalid sha256")


def test_run_dir_validation_requires_existing_files_and_matching_hashes(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    manifest = run_dir / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}", encoding="utf-8")

    payload = valid_step_result(
        artifact_paths=["manifest.json"],
        artifact_hashes={"manifest.json": sha256_text("{}")},
    )

    assert validate_step_result(payload, run_dir=run_dir) == payload

    missing_payload = valid_step_result(
        artifact_paths=["missing.json"],
        artifact_hashes={"missing.json": VALID_HASH},
    )
    assert_invalid(missing_payload, "result path does not exist", run_dir=run_dir)

    wrong_hash = valid_step_result(
        artifact_paths=["manifest.json"],
        artifact_hashes={"manifest.json": VALID_HASH},
    )
    assert_invalid(wrong_hash, "sha256 mismatch", run_dir=run_dir)


def test_review_result_uses_review_package_fields_only():
    payload = valid_review_result(artifact_paths=["manifest.json"])

    assert_invalid(payload, "unexpected fields", review=True)


def test_cli_validates_step_and_review_results(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    artifact = run_dir / "manifest.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{}", encoding="utf-8")
    step_payload = valid_step_result(
        artifact_paths=["manifest.json"],
        artifact_hashes={"manifest.json": sha256_text("{}")},
    )
    step_path = tmp_path / "step_result.json"
    write_json(step_path, step_payload)

    review_file = run_dir / "stage_reviews" / "ingest" / "issues.json"
    review_file.parent.mkdir(parents=True)
    review_file.write_text("{}", encoding="utf-8")
    review_payload = valid_review_result(
        review_package_paths=["stage_reviews/ingest/issues.json"],
        review_package_hashes={
            "stage_reviews/ingest/issues.json": sha256_text("{}"),
        },
    )
    review_path = tmp_path / "review_result.json"
    write_json(review_path, review_payload)

    step_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-step-result",
            "--path",
            str(step_path),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert step_result.returncode == 0, step_result.stderr
    assert step_result.stdout.strip() == "step result valid"

    review_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-review-result",
            "--path",
            str(review_path),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert review_result.returncode == 0, review_result.stderr
    assert review_result.stdout.strip() == "review result valid"


def test_cli_returns_2_for_invalid_result(tmp_path):
    result_path = tmp_path / "step_result.json"
    write_json(result_path, valid_step_result(status="finished"))

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-step-result",
            "--path",
            str(result_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "invalid status" in result.stderr
