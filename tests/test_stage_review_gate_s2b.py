import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_run_dir(stdout: str) -> Path:
    for line in stdout.splitlines():
        if line.startswith("Run: "):
            return Path(line.removeprefix("Run: ").strip())
    raise AssertionError(f"Run line not found in stdout:\n{stdout}")


def review_unit_ids(run_dir: Path, stage: str) -> list[str]:
    units = read_json(run_dir / "stage_reviews" / stage / "review_units.json")
    return [unit["unit_id"] for unit in units["units"]]


def valid_no_issue_payload(run_id: str, stage: str, unit_ids: list[str]) -> dict:
    return {
        "schema_version": 1,
        "kind": "stage_review_issues",
        "run_id": run_id,
        "stage": stage,
        "reviewer": "claude_code",
        "status": "no_issues",
        "not_professional_approval": True,
        "reviewed_unit_ids": unit_ids,
        "unchecked_unit_ids": [],
        "issues": [],
    }


def prepare_valid_gate(run_dir: Path, stage: str, decision: str = "accepted") -> None:
    from ai_writing_plugin.stage_review import (
        prepare_stage_review,
        record_stage_review_decision,
        validate_stage_review,
    )

    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage=stage)
    unit_ids = review_unit_ids(run_dir, stage)
    write_json(run_dir / "stage_reviews" / stage / "issues.json", valid_no_issue_payload(run_id, stage, unit_ids))
    validate_stage_review(run_dir=run_dir, stage=stage)
    record_stage_review_decision(
        run_dir=run_dir,
        stage=stage,
        decision=decision,
        notes="Engineering S2B test.",
    )


def test_default_write_run_remains_full_non_gated(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import write_run

    run_dir = write_run(FIXTURE_TASK, runs_dir=tmp_path / "runs")
    state = read_json(run_dir / "run_state.json")

    assert state["status"] == "completed"
    assert all(stage["status"] == "done" for stage in state["stages"].values())


def test_gated_write_run_completes_ingest_only(tmp_path: Path) -> None:
    result = run_cli(
        [
            "write-run",
            "--task",
            str(FIXTURE_TASK),
            "--runs-dir",
            str(tmp_path / "runs"),
            "--require-stage-review-gates",
        ]
    )

    assert result.returncode == 0, result.stderr
    assert "Gated write run started." in result.stdout
    assert "Ingest completed only." in result.stdout
    assert "not professional approval" in result.stdout
    run_dir = parse_run_dir(result.stdout)
    state = read_json(run_dir / "run_state.json")
    assert state["status"] == "running"
    assert state["stages"]["ingest"]["status"] == "done"
    assert state["stages"]["outline"]["status"] == "pending"
    assert not (run_dir / "plans" / "template_structure.json").exists()


def test_gated_resume_missing_previous_gate_fails_without_executing_stage(tmp_path: Path) -> None:
    start = run_cli(
        [
            "write-run",
            "--task",
            str(FIXTURE_TASK),
            "--runs-dir",
            str(tmp_path / "runs"),
            "--require-stage-review-gates",
        ]
    )
    assert start.returncode == 0, start.stderr
    run_dir = parse_run_dir(start.stdout)

    result = run_cli(["resume-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 1
    assert "Stage review gate required before outline" in result.stderr
    assert "previous stage ingest gate is not passed" in result.stderr
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["outline"]["status"] == "pending"
    assert not (run_dir / "plans" / "template_structure.json").exists()


def test_gated_resume_executes_one_stage_after_previous_gate_passes(tmp_path: Path) -> None:
    start = run_cli(
        [
            "write-run",
            "--task",
            str(FIXTURE_TASK),
            "--runs-dir",
            str(tmp_path / "runs"),
            "--require-stage-review-gates",
        ]
    )
    assert start.returncode == 0, start.stderr
    run_dir = parse_run_dir(start.stdout)
    prepare_valid_gate(run_dir, "ingest")

    result = run_cli(["resume-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 0, result.stderr
    assert "Gated resume step completed." in result.stdout
    assert "Only one deterministic stage was executed." in result.stdout
    state = read_json(run_dir / "run_state.json")
    assert state["status"] == "running"
    assert state["stages"]["outline"]["status"] == "done"
    assert state["stages"]["evidence"]["status"] == "pending"
    assert (run_dir / "plans" / "template_structure.json").exists()
    assert not (run_dir / "plans" / "research_questions.json").exists()


def test_gated_resume_requires_new_gate_for_next_stage(tmp_path: Path) -> None:
    start = run_cli(
        [
            "write-run",
            "--task",
            str(FIXTURE_TASK),
            "--runs-dir",
            str(tmp_path / "runs"),
            "--require-stage-review-gates",
        ]
    )
    assert start.returncode == 0, start.stderr
    run_dir = parse_run_dir(start.stdout)
    prepare_valid_gate(run_dir, "ingest")
    first_step = run_cli(["resume-run", "--run", str(run_dir), "--require-stage-review-gates"])
    assert first_step.returncode == 0, first_step.stderr

    result = run_cli(["resume-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 1
    assert "Stage review gate required before evidence" in result.stderr
    assert "previous stage outline gate is not passed" in result.stderr
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["evidence"]["status"] == "pending"
    assert not (run_dir / "plans" / "research_questions.json").exists()


def test_single_stage_command_without_flag_remains_non_gated(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ingest_run

    run_dir = ingest_run(FIXTURE_TASK, runs_dir=tmp_path / "runs")

    result = run_cli(["outline-run", "--run", str(run_dir)])

    assert result.returncode == 0, result.stderr
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["outline"]["status"] == "done"


def test_single_stage_command_with_flag_requires_previous_gate(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ingest_run

    run_dir = ingest_run(FIXTURE_TASK, runs_dir=tmp_path / "runs")

    result = run_cli(["outline-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 1
    assert "Stage review gate required before outline" in result.stderr
    assert "previous stage ingest gate is not passed" in result.stderr
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["outline"]["status"] == "pending"


def test_single_stage_command_with_flag_runs_after_previous_gate_passes(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ingest_run

    run_dir = ingest_run(FIXTURE_TASK, runs_dir=tmp_path / "runs")
    prepare_valid_gate(run_dir, "ingest")

    result = run_cli(["outline-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 0, result.stderr
    assert "Stage review gate enforcement was enabled for this step." in result.stdout
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["outline"]["status"] == "done"


def test_s2b_rejects_non_passing_decision_before_stage_command(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ingest_run

    run_dir = ingest_run(FIXTURE_TASK, runs_dir=tmp_path / "runs")
    prepare_valid_gate(run_dir, "ingest", decision="needs_revision")

    result = run_cli(["outline-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 1
    assert "decision is needs_revision" in result.stderr
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["outline"]["status"] == "pending"


def test_s2b_rejects_post_decision_issues_hash_mismatch(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ingest_run

    run_dir = ingest_run(FIXTURE_TASK, runs_dir=tmp_path / "runs")
    prepare_valid_gate(run_dir, "ingest")
    issues_path = run_dir / "stage_reviews" / "ingest" / "issues.json"
    issues = read_json(issues_path)
    issues["reviewer"] = "changed_after_decision"
    write_json(issues_path, issues)

    result = run_cli(["outline-run", "--run", str(run_dir), "--require-stage-review-gates"])

    assert result.returncode == 1
    assert "issues_sha256 mismatch" in result.stderr
    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["outline"]["status"] == "pending"
