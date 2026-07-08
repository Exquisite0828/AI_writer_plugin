import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.stage_gate_results import (
    StageGateResultError,
    build_stage_gate_result,
    stage_gate_result_path,
    validate_stage_gate_result,
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


def write_review_result(
    run_dir: Path,
    step: str = "step-input-materials",
    *,
    status: str = "done",
    blocking_issues_count: int = 0,
) -> Path:
    payload = {
        "kind": "review_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": step,
        "status": status,
        "review_package_paths": ["stage_reviews/ingest/issues.json"],
        "review_package_hashes": {
            "stage_reviews/ingest/issues.json": sha256_text("{}"),
        },
        "summary": "Review package complete and ready for user gate.",
        "blocking_issues_count": blocking_issues_count,
        "next_gate_status": "pending_user_confirmation",
    }
    path = run_dir / "orchestration" / "review_results" / "ingest" / f"{step}.json"
    write(path, json.dumps(payload))
    return path


def valid_result(**overrides):
    payload = {
        "kind": "stage_gate_result",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "status": "accepted",
        "decision_ref": ref("stage_reviews/ingest/decision.json"),
        "review_result_refs": [
            ref("orchestration/review_results/ingest/step-input-materials.json")
        ],
        "summary": "Stage gate accepted.",
        "blocking_issues_count": 0,
        "next_gate_status": "can_continue",
        "created_at": "2026-07-08T00:00:00+00:00",
    }
    payload.update(overrides)
    return payload


def assert_invalid(payload, expected_message: str, **kwargs):
    with pytest.raises(StageGateResultError, match=expected_message):
        validate_stage_gate_result(payload, **kwargs)


def test_build_stage_gate_result_from_decision_and_review_results(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    write(run_dir / "stage_reviews" / "ingest" / "issues.json", "{}")
    decision = {
        "stage": "ingest",
        "decision": "accepted",
        "decision_scope": "stage_review_gate_only",
        "professional_approval": False,
        "notes": "用户确认本 stage 可以继续。",
    }
    decision_path = run_dir / "stage_reviews" / "ingest" / "decision.json"
    write(decision_path, json.dumps(decision, ensure_ascii=False))
    review_result = write_review_result(run_dir)

    payload = build_stage_gate_result(
        run_dir=run_dir,
        stage="ingest",
        decision_path=decision_path,
        review_result_paths=[review_result.relative_to(run_dir).as_posix()],
    )

    result_path = stage_gate_result_path(run_dir, "ingest")
    assert result_path == run_dir / "orchestration/stage_gate_results/ingest.json"
    assert result_path.is_file()
    assert read_json(result_path) == payload
    assert payload["status"] == "accepted"
    assert payload["decision_ref"] == {
        "path": "stage_reviews/ingest/decision.json",
        "sha256": sha256_file(decision_path),
    }
    assert payload["review_result_refs"] == [
        {
            "path": "orchestration/review_results/ingest/step-input-materials.json",
            "sha256": sha256_file(review_result),
        }
    ]
    assert payload["summary"] == "用户确认本 stage 可以继续。"
    assert payload["blocking_issues_count"] == 0
    assert payload["next_gate_status"] == "can_continue"
    assert validate_stage_gate_result(payload, run_dir=run_dir) == payload


def test_accepts_valid_stage_gate_result_without_reading_bodies():
    payload = valid_result()

    assert validate_stage_gate_result(payload) == payload


@pytest.mark.parametrize(
    "field",
    ["content", "text", "issues_body", "review_units_body", "decision_body", "extra"],
)
def test_rejects_unknown_or_body_like_fields(field):
    payload = valid_result()
    payload[field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "override, message",
    [
        ({"stage": "unknown"}, "invalid stage"),
        ({"status": "done"}, "invalid status"),
        ({"summary": "x" * 601}, "summary must be at most 600 characters"),
        ({"summary": "```json\n{}\n```"}, "summary must not contain code fences"),
        ({"blocking_issues_count": -1}, "blocking_issues_count"),
        ({"created_at": "not-a-date"}, "created_at"),
    ],
)
def test_rejects_invalid_scalar_fields(override, message):
    assert_invalid(valid_result(**override), message)


@pytest.mark.parametrize(
    "status, expected_gate",
    [
        ("accepted", "can_continue"),
        ("skipped", "can_continue"),
        ("needs_revision", "needs_revision"),
        ("blocked", "blocked"),
        ("pending_user_confirmation", "pending_user_confirmation"),
    ],
)
def test_next_gate_status_matches_stage_gate_status(status, expected_gate):
    payload = valid_result(status=status, next_gate_status=expected_gate)

    assert validate_stage_gate_result(payload) == payload


@pytest.mark.parametrize(
    "status, wrong_gate",
    [
        ("accepted", "blocked"),
        ("needs_revision", "can_continue"),
        ("pending_user_confirmation", "can_continue"),
    ],
)
def test_rejects_next_gate_status_that_disagrees_with_status(status, wrong_gate):
    payload = valid_result(status=status, next_gate_status=wrong_gate)

    assert_invalid(payload, "next_gate_status")


@pytest.mark.parametrize(
    "bad_ref, message",
    [
        (ref("/absolute.json"), "relative POSIX path"),
        (ref("../outside.json"), "must not contain '..'"),
        (ref("plans\\decision.json"), "must use POSIX separators"),
        (ref("runs/demo-run/stage_reviews/ingest/decision.json"), "must not start with runs/"),
        (ref("examples/demo/task.yaml"), "outside runtime result boundary"),
        (ref("docs/maintainers/PLAN.md"), "outside runtime result boundary"),
        (ref("contracts/CURRENT_ARTIFACT_CONTRACTS.md"), "outside runtime result boundary"),
    ],
)
def test_rejects_refs_outside_run_boundary(bad_ref, message):
    payload = valid_result(decision_ref=bad_ref)

    assert_invalid(payload, message)


def test_run_dir_validation_rejects_hash_mismatch_and_wrong_review_stage(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    write(run_dir / "stage_reviews" / "ingest" / "issues.json", "{}")
    decision_path = run_dir / "stage_reviews" / "ingest" / "decision.json"
    write(decision_path, '{"decision":"accepted","notes":"ok"}')
    review_result = write_review_result(run_dir)
    payload = valid_result(
        decision_ref=ref("stage_reviews/ingest/decision.json", sha256_file(decision_path)),
        review_result_refs=[
            ref(
                "orchestration/review_results/ingest/step-input-materials.json",
                sha256_file(review_result),
            )
        ],
    )
    assert validate_stage_gate_result(payload, run_dir=run_dir) == payload

    payload["review_result_refs"][0]["sha256"] = VALID_HASH
    assert_invalid(payload, "sha256 mismatch", run_dir=run_dir)


def test_cli_builds_validates_and_reports_invalid_result(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    write(run_dir / "stage_reviews" / "ingest" / "issues.json", "{}")
    decision_path = run_dir / "stage_reviews" / "ingest" / "decision.json"
    write(decision_path, '{"decision":"needs_revision","notes":"needs update"}')
    review_result = write_review_result(
        run_dir,
        status="needs_revision",
        blocking_issues_count=1,
    )

    build = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "build-stage-gate-result",
            "--run-dir",
            str(run_dir),
            "--stage",
            "ingest",
            "--decision",
            str(decision_path),
            "--review-result",
            str(review_result.relative_to(run_dir)),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert build.returncode == 0, build.stderr
    result_path = stage_gate_result_path(run_dir, "ingest")
    assert build.stdout.strip() == str(result_path)

    payload = read_json(result_path)
    assert payload["status"] == "needs_revision"
    assert payload["blocking_issues_count"] == 1
    assert payload["next_gate_status"] == "needs_revision"

    validate = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-stage-gate-result",
            "--path",
            str(result_path),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert validate.returncode == 0, validate.stderr
    assert validate.stdout.strip() == "stage gate result valid"

    payload["status"] = "done"
    write(result_path, json.dumps(payload))
    invalid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-stage-gate-result",
            "--path",
            str(result_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode == 2
    assert "invalid status" in invalid.stderr
