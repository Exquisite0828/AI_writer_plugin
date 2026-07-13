import hashlib
import json
import subprocess
import sys
from pathlib import Path

from ai_writing_plugin.cli import build_parser


ROOT = Path(__file__).resolve().parents[1]


def test_cli_exposes_exactly_the_nineteen_current_commands():
    parser = build_parser()
    subparser_action = next(
        action for action in parser._actions if getattr(action, "choices", None)
    )

    assert list(subparser_action.choices) == [
        "context-telemetry",
        "check-context-budget",
        "init-run",
        "validate-step-result",
        "validate-review-result",
        "build-step-context-package",
        "validate-step-context-package",
        "init-progress-ledger",
        "record-step-progress",
        "validate-progress-ledger",
        "prepare-step-worker-dispatch",
        "complete-step-worker-dispatch",
        "validate-step-worker-dispatch",
        "build-review-context-package",
        "validate-review-context-package",
        "build-stage-review-issues",
        "validate-stage-review-issues",
        "build-stage-gate-result",
        "validate-stage-gate-result",
    ]


def write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_stage_review_issue_cli_builds_and_validates_public_source(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    artifact_path = run_dir / "artifacts" / "report.md"
    write(artifact_path, "artifact body")
    source_path = run_dir / "stage_reviews" / "ingest" / "issues.json"
    write(
        source_path,
        json.dumps(
            {
                "issues": [
                    {
                        "issue_id": "P1-001",
                        "severity": "P1",
                        "category": "missing_evidence",
                        "title": "Missing evidence",
                        "summary": "The artifact lacks a required evidence binding.",
                        "location_refs": [],
                        "artifact_refs": [
                            {
                                "path": "artifacts/report.md",
                                "sha256": sha256_file(artifact_path),
                            }
                        ],
                        "recommendation": "Bind the claim to the artifact.",
                        "rationale": "The review found a traceability gap.",
                    }
                ]
            }
        ),
    )

    build = run_cli(
        "build-stage-review-issues",
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--source",
        source_path.relative_to(run_dir).as_posix(),
    )

    assert build.returncode == 0, build.stderr
    index_path = run_dir / "stage_reviews" / "ingest" / "issues_index.json"
    assert build.stdout.strip() == str(index_path)

    validate = run_cli(
        "validate-stage-review-issues",
        "--run-dir",
        str(run_dir),
        "--path",
        index_path.relative_to(run_dir).as_posix(),
    )
    assert validate.returncode == 0, validate.stderr
    assert validate.stdout.strip() == "stage review issues valid"


def test_stage_review_issue_cli_requires_overwrite_for_existing_output(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    artifact_path = run_dir / "artifacts" / "report.md"
    write(artifact_path, "artifact body")
    source_path = run_dir / "stage_reviews" / "ingest" / "issues.json"
    issue = {
        "issue_id": "P1-001",
        "severity": "P1",
        "category": "missing_evidence",
        "title": "Missing evidence",
        "summary": "The artifact lacks a required evidence binding.",
        "location_refs": [],
        "artifact_refs": [
            {"path": "artifacts/report.md", "sha256": sha256_file(artifact_path)}
        ],
        "recommendation": "Bind the claim to the artifact.",
        "rationale": "The review found a traceability gap.",
    }
    write(source_path, json.dumps({"issues": [issue]}))
    command = (
        "build-stage-review-issues",
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--source",
        str(source_path),
    )

    first = run_cli(*command)
    second = run_cli(*command)
    overwrite = run_cli(*command, "--overwrite")

    assert first.returncode == 0, first.stderr
    assert second.returncode == 2
    assert "already exists" in second.stderr
    assert overwrite.returncode == 0, overwrite.stderr
