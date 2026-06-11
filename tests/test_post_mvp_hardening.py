import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

CANONICAL_HITL_GATES = [
    "task_goal_confirmation",
    "material_classification_confirmation",
    "outline_l1_confirmation",
    "evidence_confirmation",
    "final_delivery_confirmation",
    "candidate_update_confirmation",
]

FORBIDDEN_APPROVAL_DECISIONS = {
    "approved",
    "final_approved",
    "candidate_update_approved",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_until_phase_5(tmp_path: Path) -> Path:
    from ai_writing_plugin.run_manager import draft_run, evidence_run, ingest_run, outline_run, plan_run

    run_dir = ingest_run(task_file=FIXTURE_TASK, runs_dir=tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    draft_run(run_dir)
    return run_dir


def run_until_phase_7(tmp_path: Path) -> Path:
    from ai_writing_plugin.run_manager import finalize_run, review_run

    run_dir = run_until_phase_5(tmp_path)
    review_run(run_dir)
    finalize_run(run_dir)
    return run_dir


def record_hitl(run_dir: Path, stage: str, decision: str = "approved_with_issues") -> None:
    from ai_writing_plugin.learning import record_hitl_decision

    record_hitl_decision(
        run_dir=run_dir,
        stage=stage,
        decision=decision,
        comment=f"{stage} confirmed by test.",
        affected_sections=["SEC-003", "SEC-005"],
        next_action="continue_with_confirmation_marker",
    )


def check_by_id(verify_report: dict, check_id: str) -> dict:
    return next(check for check in verify_report["checks"] if check["check_id"] == check_id)


def test_allowed_early_hitl_trace_does_not_fail_phase_6_or_finalize(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import finalize_run, review_run

    run_dir = run_until_phase_5(tmp_path)
    record_hitl(run_dir, "material_classification_confirmation", decision="approved")

    review_run(run_dir)

    review_report = read_json(run_dir / "review" / "review_report.json")
    verify_report = read_json(run_dir / "verify" / "verify_report.json")
    failures = (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")

    assert not [
        item
        for item in review_report["items"]
        if item["category"] == "phase_boundary_violation" and item["artifact"] == "trace/hitl_decisions.jsonl"
    ]
    assert check_by_id(verify_report, "CHK-019")["status"] == "passed"
    assert "trace/hitl_decisions.jsonl" not in failures

    finalize_run(run_dir)
    revision_plan_text = json.dumps(read_json(run_dir / "revision_plan.json"), ensure_ascii=False)
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")

    assert "phase_boundary_violation" not in revision_plan_text
    assert "CHK-019" not in revision_plan_text
    assert "CHK-019" not in final_report
    assert "CHK-019" not in delivery_summary


@pytest.mark.parametrize("forbidden_relative_path", ["trace/session_trace.jsonl", "learning/run_summary.md"])
def test_forbidden_future_artifacts_still_fail_phase_6_boundary(tmp_path: Path, forbidden_relative_path: str) -> None:
    from ai_writing_plugin.run_manager import review_run

    run_dir = run_until_phase_5(tmp_path)
    forbidden_path = run_dir / forbidden_relative_path
    forbidden_path.parent.mkdir(parents=True, exist_ok=True)
    forbidden_path.write_text("{}\n", encoding="utf-8")

    review_run(run_dir)

    review_report = read_json(run_dir / "review" / "review_report.json")
    verify_report = read_json(run_dir / "verify" / "verify_report.json")

    assert any(
        item["category"] == "phase_boundary_violation" and item["artifact"] == forbidden_relative_path
        for item in review_report["items"]
    )
    assert check_by_id(verify_report, "CHK-019")["status"] in {"failed", "blocked"}


def test_malformed_early_hitl_trace_still_fails_phase_6_boundary(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import review_run

    run_dir = run_until_phase_5(tmp_path)
    hitl_path = run_dir / "trace" / "hitl_decisions.jsonl"
    hitl_path.parent.mkdir(parents=True, exist_ok=True)
    hitl_path.write_text("{not valid json}\n", encoding="utf-8")

    review_run(run_dir)

    review_report = read_json(run_dir / "review" / "review_report.json")
    assert any(
        item["category"] == "phase_boundary_violation" and item["artifact"] == "trace/hitl_decisions.jsonl"
        for item in review_report["items"]
    )


def test_learning_run_preserves_real_hitl_records_and_summarizes_all_gates(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import learning_run

    run_dir = run_until_phase_7(tmp_path)
    for stage in CANONICAL_HITL_GATES:
        record_hitl(run_dir, stage)

    learning_run(run_dir)

    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")
    stage_counts = Counter(decision["stage"] for decision in decisions)
    run_summary = (run_dir / "learning" / "run_summary.md").read_text(encoding="utf-8")

    for stage in CANONICAL_HITL_GATES:
        assert stage_counts[stage] == 1
        assert f"- {stage}: recorded" in run_summary
    assert "## 人工确认状态" in run_summary


def test_learning_run_deduplicates_existing_alias_hitl_stages_without_rewriting_raw_records(tmp_path: Path) -> None:
    from ai_writing_plugin.run_manager import learning_run

    run_dir = run_until_phase_7(tmp_path)
    trace_dir = run_dir / "trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    alias_records = [
        {
            "timestamp": "2026-06-02T00:00:00Z",
            "run_id": run_dir.name,
            "stage": "ingest_confirmation",
            "decision": "approved",
            "user_comment": "Legacy ingest alias.",
            "affected_sections": [],
            "next_action": "continue_to_outline",
            "requires_user_confirmation": False,
            "status": "recorded",
        },
        {
            "timestamp": "2026-06-02T00:00:00Z",
            "run_id": run_dir.name,
            "stage": "outline_confirmation",
            "decision": "approved_with_issues",
            "user_comment": "Legacy outline alias.",
            "affected_sections": ["SEC-003"],
            "next_action": "continue_to_evidence",
            "requires_user_confirmation": True,
            "status": "recorded",
        },
    ]
    (trace_dir / "hitl_decisions.jsonl").write_text(
        "".join(f"{json.dumps(record, sort_keys=True)}\n" for record in alias_records),
        encoding="utf-8",
    )

    learning_run(run_dir)

    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")
    stages = [decision["stage"] for decision in decisions]
    run_summary = (run_dir / "learning" / "run_summary.md").read_text(encoding="utf-8")

    assert "ingest_confirmation" in stages
    assert "outline_confirmation" in stages
    assert stages.count("material_classification_confirmation") == 0
    assert stages.count("outline_l1_confirmation") == 0
    assert "- material_classification_confirmation: recorded" in run_summary
    assert "- outline_l1_confirmation: recorded" in run_summary


def test_record_hitl_accepts_aliases_and_writes_canonical_stage_names(tmp_path: Path) -> None:
    run_dir = run_until_phase_5(tmp_path)

    record_hitl(run_dir, "ingest_confirmation", decision="approved")
    record_hitl(run_dir, "outline_confirmation")

    stages = [decision["stage"] for decision in read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")]
    assert stages == ["material_classification_confirmation", "outline_l1_confirmation"]


def test_noninteractive_write_run_still_avoids_fake_approval(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "write-run",
            "--task",
            str(FIXTURE_TASK),
            "--runs-dir",
            str(tmp_path / "runs"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    run_dir = next(Path(line.removeprefix("Run: ").strip()) for line in result.stdout.splitlines() if line.startswith("Run: "))
    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")

    assert {decision["decision"] for decision in decisions}.isdisjoint(FORBIDDEN_APPROVAL_DECISIONS)


def test_write_command_hardening_contract() -> None:
    command = (REPO_ROOT / "commands" / "write.md").read_text(encoding="utf-8")

    assert 'PYTHON=".venv/bin/python"' in command
    assert "$PYTHON -m ai_writing_plugin" in command
    assert "python3 -m ai_writing_plugin" not in command
    assert "python -m ai_writing_plugin" not in command
    assert "/Users/" not in command
    assert "AI_Ancoder_writer_plugin" not in command
    assert "python3 -m venv .venv" in command
    for gate in CANONICAL_HITL_GATES:
        assert gate in command
        gate_position = command.index(gate)
        assert command.rfind("record-hitl", 0, gate_position) != -1
