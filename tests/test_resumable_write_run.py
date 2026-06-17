import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "examples" / "hara_minimal_fixture"
FIXTURE_TASK = FIXTURE_DIR / "task.yaml"
CUSTOM_PROFILE_TASK = REPO_ROOT / "examples" / "custom_technical_note_profile_demo_fixture" / "task.yaml"

STAGES = ["ingest", "outline", "evidence", "planning", "draft", "review", "finalize", "learning"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def copy_hara_fixture(tmp_path: Path) -> Path:
    fixture_copy = tmp_path / "hara_fixture"
    shutil.copytree(FIXTURE_DIR, fixture_copy)
    return fixture_copy / "task.yaml"


def parse_run_dir(stdout: str) -> Path:
    for line in stdout.splitlines():
        if line.startswith("Run: "):
            return Path(line.removeprefix("Run: ").strip())
        if line.startswith("Created run: "):
            return Path(line.removeprefix("Created run: ").strip())
    raise AssertionError(f"run directory not found in stdout:\n{stdout}")


def ingest_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import ingest_run

    return ingest_run(task_file=task_path, runs_dir=runs_dir)


def outline_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import outline_run

    return outline_run(run_dir=run_dir)


def evidence_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import evidence_run

    return evidence_run(run_dir=run_dir)


def plan_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import plan_run

    return plan_run(run_dir=run_dir)


def draft_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import draft_run

    return draft_run(run_dir=run_dir)


def review_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import review_run

    return review_run(run_dir=run_dir)


def finalize_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import finalize_run

    return finalize_run(run_dir=run_dir)


def learning_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import learning_run

    return learning_run(run_dir=run_dir)


def resume_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import resume_run

    return resume_run(run_dir=run_dir)


def run_until_planning_done(tmp_path: Path, task_path: Path | None = None) -> Path:
    run_dir = ingest_run(task_path or FIXTURE_TASK, tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    return run_dir


def run_until_finalized(tmp_path: Path) -> Path:
    run_dir = run_until_planning_done(tmp_path)
    draft_run(run_dir)
    review_run(run_dir)
    finalize_run(run_dir)
    return run_dir


def test_write_run_creates_completed_run_state(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import write_run

    run_dir = write_run(FIXTURE_TASK, tmp_path / "runs")
    state = read_json(run_dir / "run_state.json")
    manifest = read_json(run_dir / "manifest.json")

    assert state["schema_version"] == 1
    assert state["run_id"] == manifest["run_id"]
    assert state["status"] == "completed"
    assert [stage["name"] for stage in state["stage_order"]] == STAGES
    assert set(state["stages"]) == set(STAGES)
    assert all(state["stages"][stage]["status"] == "done" for stage in STAGES)
    assert "run_state.json" not in [artifact["path"] for artifact in manifest["artifacts"]]
    assert not (run_dir / ".run_state.lock").exists()


def test_stage_commands_update_run_state_without_phase_8_trace(tmp_path: Path) -> None:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    state = read_json(run_dir / "run_state.json")
    assert state["status"] == "running"
    assert state["stages"]["ingest"]["status"] == "done"
    assert state["stages"]["outline"]["status"] == "pending"

    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    state = read_json(run_dir / "run_state.json")

    assert state["stages"]["outline"]["status"] == "done"
    assert state["stages"]["evidence"]["status"] == "done"
    assert state["stages"]["planning"]["status"] == "done"
    assert state["stages"]["draft"]["status"] == "pending"
    assert not (run_dir / "trace" / "session_trace.jsonl").exists()


def test_resume_from_pending_stage_completes_remaining_workflow(tmp_path: Path) -> None:
    run_dir = run_until_planning_done(tmp_path)
    before = read_json(run_dir / "run_state.json")
    assert before["stages"]["draft"]["status"] == "pending"

    resumed = resume_run(run_dir)
    state = read_json(resumed / "run_state.json")

    assert resumed == run_dir
    assert state["status"] == "completed"
    assert all(state["stages"][stage]["status"] == "done" for stage in STAGES)
    assert (run_dir / "final" / "final_report.md").exists()
    assert (run_dir / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8").count("active: false") >= 1


def test_resume_run_cli_completes_remaining_workflow(tmp_path: Path) -> None:
    run_dir = run_until_planning_done(tmp_path)

    result = subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "resume-run", "--run", str(run_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    state = read_json(run_dir / "run_state.json")

    assert result.returncode == 0, result.stderr
    assert "Resumed run:" in result.stdout
    assert "Status: completed" in result.stdout
    assert "不表示 professional approval" in result.stdout
    assert state["status"] == "completed"
    assert all(state["stages"][stage]["status"] == "done" for stage in STAGES)


def test_resume_recovers_stale_lock_with_dead_pid(tmp_path: Path) -> None:
    run_dir = run_until_planning_done(tmp_path)
    state = read_json(run_dir / "run_state.json")
    state["status"] = "running"
    state["stages"]["draft"]["status"] = "running"
    write_json(run_dir / "run_state.json", state)
    write_json(
        run_dir / ".run_state.lock",
        {"pid": 99999999, "created_at": "2000-01-01T00:00:00Z", "command": "pytest stale lock"},
    )

    resume_run(run_dir)
    state = read_json(run_dir / "run_state.json")

    assert state["status"] == "completed"
    assert state["stages"]["draft"]["status"] == "done"
    assert state["stages"]["draft"]["interrupted_at"]
    assert state["stages"]["draft"]["interrupt_reason"] == "stale_lock_recovery"
    assert not (run_dir / ".run_state.lock").exists()


def test_resume_fails_when_lock_pid_is_alive(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ResumeRunError

    run_dir = run_until_planning_done(tmp_path)
    write_json(
        run_dir / ".run_state.lock",
        {"pid": os.getpid(), "created_at": "2000-01-01T00:00:00Z", "command": "pytest live lock"},
    )

    with pytest.raises(ResumeRunError, match="another process"):
        resume_run(run_dir)


def test_resume_fails_when_task_hash_changed(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ResumeRunError

    task_path = copy_hara_fixture(tmp_path)
    run_dir = run_until_planning_done(tmp_path, task_path=task_path)
    task_path.write_text(task_path.read_text(encoding="utf-8") + "\n# changed after run creation\n", encoding="utf-8")

    with pytest.raises(ResumeRunError, match="task.*hash mismatch"):
        resume_run(run_dir)


def test_resume_fails_when_external_profile_hash_changed(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ResumeRunError

    run_dir = ingest_run(CUSTOM_PROFILE_TASK, tmp_path / "runs")
    state = read_json(run_dir / "run_state.json")
    state["profile_sha256"] = "0" * 64
    write_json(run_dir / "run_state.json", state)

    with pytest.raises(ResumeRunError, match="profile.*hash mismatch"):
        resume_run(run_dir)


def test_resume_fails_for_non_resumable_old_run(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ResumeRunError, init_run

    run_dir = init_run(FIXTURE_TASK, tmp_path / "runs")

    with pytest.raises(ResumeRunError, match="not a resumable run"):
        resume_run(run_dir)


def test_dirty_done_stage_fails_safely_without_rewind(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import ResumeRunError

    run_dir = run_until_planning_done(tmp_path)
    (run_dir / "plans" / "evidence_map.json").unlink()

    with pytest.raises(ResumeRunError, match="completed stage evidence is dirty"):
        resume_run(run_dir)

    state = read_json(run_dir / "run_state.json")
    assert state["stages"]["evidence"]["status"] == "dirty"
    assert "automatic upstream rewind is not supported in v1" in state["stages"]["evidence"]["dirty_reason"]
    assert not (run_dir / "draft" / "full_draft.md").exists()


def test_resume_preserves_source_sample_reference_hitl_boundaries(tmp_path: Path) -> None:
    run_dir = run_until_planning_done(tmp_path)

    resume_run(run_dir)

    inventory = read_json(run_dir / "inputs" / "input_inventory.json")
    source_index = read_json(run_dir / "knowledge" / "source_index.json")
    citation_plan = read_json(run_dir / "plans" / "citation_plan.json")
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8").lower()
    profile_update = (run_dir / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    indexed_file_ids = {source["file_id"] for source in source_index["sources"]}
    sample_records = [record for record in inventory["files"] if record["role"] in {"sample", "expected_output_shape"}]

    assert sample_records
    assert all(record["is_fact_source"] is False for record in sample_records)
    assert all(record["file_id"] not in indexed_file_ids for record in sample_records)
    assert "sample" not in json.dumps(citation_plan).lower() or "fact_support" not in json.dumps(citation_plan).lower()
    assert "approval" not in final_report
    assert "status: proposed" in profile_update
    assert "active: false" in profile_update
    assert "auto_applied: false" in profile_update


def test_invalid_profile_fail_safe_still_writes_session_trace(tmp_path: Path) -> None:
    task_path = tmp_path / "task.yaml"
    task_path.write_text(
        """\
task_type: custom_technical_note
task_title: Invalid external profile run
target_audience: reviewer
output_format: markdown
strict_template: true
allow_inference: false
document_profile_path: tests/fixtures/document_profiles/invalid_sample_fact_source.yaml
requires_human_confirmation:
  - deployment risk
""",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "write-run",
            "--task",
            str(task_path),
            "--runs-dir",
            str(tmp_path / "runs"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    run_dir = next((tmp_path / "runs").iterdir())
    trace = (run_dir / "trace" / "session_trace.jsonl").read_text(encoding="utf-8")
    assert "document_profile_validation" in trace
    assert not (run_dir / "run_state.json").exists()
