import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.review_context_packages import (
    ReviewContextPackageError,
    build_review_context_package,
    review_context_package_path,
    validate_review_context_package,
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


def valid_package(**overrides):
    payload = {
        "kind": "review_context_package",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "steps": STEPS,
        "created_at": "2026-07-08T00:00:00+00:00",
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
    repo_root = tmp_path / "repo"
    run_dir = tmp_path / "runs" / "demo-run"
    write(repo_root / "commands" / "write.md", "command")
    write(run_dir / "manifest.json", "{}")
    for step in STEPS:
        write_step_result(run_dir, step)

    stage_review_dir = run_dir / "stage_reviews" / "ingest"
    write(stage_review_dir / "review_prompt.md", "prompt")
    write(stage_review_dir / "review_units.json", '{"units":[]}')
    write(stage_review_dir / "issues_schema.json", '{"type":"object"}')
    write(stage_review_dir / "review_context.json", '{"stage":"ingest"}')
    write(stage_review_dir / "issues.json", '{"not":"included in context package"}')

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
    assert [item["path"] for item in payload["stage_review_refs"]] == [
        "stage_reviews/ingest/review_prompt.md",
        "stage_reviews/ingest/review_units.json",
        "stage_reviews/ingest/issues_schema.json",
        "stage_reviews/ingest/review_context.json",
    ]
    assert "stage_reviews/ingest/issues.json" not in [
        item["path"] for item in payload["stage_review_refs"]
    ]
    assert payload["step_result_refs"][0]["sha256"] == sha256_file(
        run_dir / "orchestration/step_results/step-input-materials.json"
    )
    assert validate_review_context_package(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload


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


def test_rejects_stage_review_refs_outside_allowlist():
    payload = valid_package(
        stage_review_refs=[
            ref("stage_reviews/ingest/issues.json"),
        ]
    )

    assert_invalid(payload, "stage_review_refs path is not allowed")


def test_run_dir_validation_requires_matching_hashes_and_step_result_payload(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    write(run_dir / "manifest.json", "{}")
    for step in STEPS:
        write_step_result(run_dir, step)
    write(run_dir / "stage_reviews" / "ingest" / "review_prompt.md", "prompt")

    payload = valid_package(
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
    assert validate_review_context_package(payload, run_dir=run_dir) == payload

    payload["step_result_refs"][0]["sha256"] = VALID_HASH
    assert_invalid(payload, "sha256 mismatch", run_dir=run_dir)


def test_cli_builds_validates_and_reports_invalid_package(tmp_path):
    repo_root = tmp_path / "repo"
    run_dir = tmp_path / "runs" / "demo-run"
    write(run_dir / "manifest.json", "{}")
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
