import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

TRACE_ARTIFACTS = {
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
}

LEARNING_ARTIFACTS = {
    "learning/run_summary.md",
    "learning/reusable_patterns.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
    "learning/promotion_report.md",
}

PHASE_8_ARTIFACTS = TRACE_ARTIFACTS | LEARNING_ARTIFACTS

WRITE_RUN_KEY_ARTIFACTS = {
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/knowledge_gaps.md",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
    "plans/citation_plan.json",
    "plans/outline_final.md",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
    "draft/full_draft.md",
    "review/review_report.json",
    "verify/verify_report.json",
    "revision_plan.json",
    "revised/full_draft.md",
    "final/final_report.md",
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
    "learning/promotion_report.md",
}

DEFAULT_HITL_GATES = {
    "task_goal_confirmation",
    "material_classification_confirmation",
    "outline_l1_confirmation",
    "evidence_confirmation",
    "final_delivery_confirmation",
    "candidate_update_confirmation",
}

REQUIRED_TRACE_STAGES = {
    "ingest",
    "outline",
    "evidence",
    "planning",
    "draft",
    "review",
    "finalize",
    "learning",
}

FORBIDDEN_APPROVAL_DECISIONS = {
    "approved",
    "final_approved",
    "candidate_update_approved",
}

FORBIDDEN_HARA_APPROVAL_CLAIMS = [
    "hazard approved",
    "ASIL approved",
    "risk accepted",
    "safety goal approved",
    "final acceptability approved",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines, f"{path} is empty"
    return [json.loads(line) for line in lines]


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
    import ai_writing_plugin.run_manager as run_manager

    runner = getattr(run_manager, "learning_run", None)
    assert runner is not None, "learning_run is not implemented"
    return runner(run_dir=run_dir)


def run_until_phase_6(tmp_path: Path) -> Path:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    draft_run(run_dir)
    review_run(run_dir)
    return run_dir


def run_until_phase_7(tmp_path: Path) -> Path:
    run_dir = run_until_phase_6(tmp_path)
    finalize_run(run_dir)
    return run_dir


def run_until_phase_8(tmp_path: Path) -> Path:
    run_dir = run_until_phase_7(tmp_path)
    learning_run(run_dir)
    return run_dir


def cli_learning_run(run_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "learning-run", "--run", str(run_dir)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def cli_record_hitl(
    run_dir: Path,
    stage: str = "outline_l1_confirmation",
    decision: str = "approved_with_issues",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "record-hitl",
            "--run",
            str(run_dir),
            "--stage",
            stage,
            "--decision",
            decision,
            "--comment",
            "Keep unsupported sections marked.",
            "--affected-sections",
            "SEC-003,SEC-005",
            "--next-action",
            "continue_with_confirmation_marker",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def cli_write_run(task_path: Path, runs_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "write-run",
            "--task",
            str(task_path),
            "--runs-dir",
            str(runs_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def parse_run_dir_from_stdout(stdout: str) -> Path:
    for line in stdout.splitlines():
        if line.startswith("Run: "):
            return Path(line.removeprefix("Run: ").strip())
        if line.startswith("Created run: "):
            return Path(line.removeprefix("Created run: ").strip())
    raise AssertionError(f"run directory not found in stdout:\n{stdout}")


def test_learning_run_requires_phase_7_run(tmp_path: Path) -> None:
    run_dir = run_until_phase_6(tmp_path)

    result = cli_learning_run(run_dir)

    assert result.returncode != 0
    assert any(marker in result.stderr for marker in ["revision_plan.json", "final/final_report.md", "final/delivery_summary.md"])
    assert not (run_dir / "trace").exists()
    assert not (run_dir / "learning").exists()


def test_learning_run_creates_trace_artifacts(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)

    for relative_path in TRACE_ARTIFACTS:
        path = run_dir / relative_path
        assert path.exists(), relative_path
        assert path.read_text(encoding="utf-8").strip()


def test_session_trace_jsonl_is_parseable_and_covers_stages(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    records = read_jsonl(run_dir / "trace" / "session_trace.jsonl")

    stages = {record["stage"] for record in records}
    assert REQUIRED_TRACE_STAGES <= stages
    for record in records:
        assert {"timestamp", "run_id", "stage", "event", "status"} <= set(record)
        assert record["run_id"] == read_json(run_dir / "manifest.json")["run_id"]


def test_hitl_decisions_jsonl_is_parseable_and_has_default_gates(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")

    stages = {decision["stage"] for decision in decisions}
    assert DEFAULT_HITL_GATES <= stages
    for decision in decisions:
        assert {
            "timestamp",
            "run_id",
            "stage",
            "decision",
            "user_comment",
            "affected_sections",
            "next_action",
            "requires_user_confirmation",
            "status",
        } <= set(decision)
        assert isinstance(decision["affected_sections"], list)


def test_noninteractive_hitl_does_not_fake_approval(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")

    decision_values = {decision["decision"] for decision in decisions}
    assert decision_values.isdisjoint(FORBIDDEN_APPROVAL_DECISIONS)
    assert "not_collected_in_noninteractive_run" in decision_values or "pending_user_confirmation" in decision_values


def test_record_hitl_appends_real_decision_and_learning_preserves_it(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)

    result = cli_record_hitl(run_dir)
    assert result.returncode == 0, result.stderr
    learning_run(run_dir)

    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")
    matching = [
        decision
        for decision in decisions
        if decision["stage"] == "outline_l1_confirmation" and decision["decision"] == "approved_with_issues"
    ]
    assert matching
    assert matching[-1]["user_comment"] == "Keep unsupported sections marked."
    assert matching[-1]["affected_sections"] == ["SEC-003", "SEC-005"]
    assert matching[-1]["next_action"] == "continue_with_confirmation_marker"


def test_learning_artifacts_are_generated(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)

    for relative_path in LEARNING_ARTIFACTS:
        path = run_dir / relative_path
        assert path.exists(), relative_path
        assert path.read_text(encoding="utf-8").strip()


def test_run_summary_is_chinese_first_and_keeps_machine_status(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    summary = (run_dir / "learning" / "run_summary.md").read_text(encoding="utf-8")

    assert summary.startswith("# 运行摘要")
    for heading in ["执行的 workflow", "关键 artifacts", "审查与验证摘要", "最终交付摘要", "人工确认状态"]:
        assert heading in summary
    assert "Status: completed_with_candidate_updates_proposed" in summary
    assert "candidate update 或 Skill patch 不会自动应用" in summary


def test_candidate_profile_update_is_proposed_and_inactive(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    profile = (run_dir / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")

    for required in [
        "status: proposed",
        "active: false",
        "auto_applied: false",
        "requires_user_approval: true",
        "rollback_supported: true",
        "stable_skill_overwrite_allowed: false",
    ]:
        assert required in profile
    for forbidden in ["status: active", "active: true", "auto_applied: true", "approved_by_user: true"]:
        assert forbidden not in profile


def test_candidate_skill_patch_is_not_applied(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    patch = (run_dir / "learning" / "candidate_skill_patch.md").read_text(encoding="utf-8")

    assert "proposed_only" in patch
    assert "not applied" in patch
    assert "No stable skill was overwritten" in patch
    assert "requires user approval" in patch
    stable_hara_skill = REPO_ROOT / "skills" / "document-types" / "hara" / "SKILL.md"
    assert stable_hara_skill.exists()
    stable_text = stable_hara_skill.read_text(encoding="utf-8")
    assert "Candidate Skill Patch" not in stable_text
    assert "proposed_only" not in stable_text
    assert str(run_dir.name) not in stable_text


def test_promotion_report_does_not_promote_automatically(tmp_path: Path) -> None:
    run_dir = run_until_phase_8(tmp_path)
    report = (run_dir / "learning" / "promotion_report.md").read_text(encoding="utf-8")

    for required in [
        "Current state: proposed",
        "Not promoted automatically",
        "Candidate activated: no",
        "Stable skill overwritten: no",
    ]:
        assert required in report
    for forbidden in ["Current state: active", "Promoted automatically", "Candidate activated: yes", "Stable skill overwritten: yes"]:
        assert forbidden not in report


def test_learning_run_updates_manifest_and_is_idempotent(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)

    learning_run(run_dir)
    first_decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")
    learning_run(run_dir)

    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]
    decisions = read_jsonl(run_dir / "trace" / "hitl_decisions.jsonl")

    assert manifest["phase"] == "phase_8"
    assert manifest["status"] == "completed_with_candidate_updates_proposed"
    for artifact_path in PHASE_8_ARTIFACTS:
        assert artifact_paths.count(artifact_path) == 1
    default_gate_records = [
        decision for decision in decisions if decision["stage"] in DEFAULT_HITL_GATES and decision["decision"] == "not_collected_in_noninteractive_run"
    ]
    assert len(default_gate_records) == len(DEFAULT_HITL_GATES)
    assert len(decisions) == len(first_decisions)


def test_write_run_creates_full_mvp_artifacts_and_reports_run_dir(tmp_path: Path) -> None:
    result = cli_write_run(FIXTURE_TASK, tmp_path / "runs")

    assert result.returncode == 0, result.stderr
    assert "写作流程已完成" in result.stdout
    assert "completed_with_candidate_updates_proposed" in result.stdout
    assert "生成的 artifacts" in result.stdout
    run_dir = parse_run_dir_from_stdout(result.stdout)
    assert run_dir.exists()
    for artifact_path in WRITE_RUN_KEY_ARTIFACTS:
        assert (run_dir / artifact_path).exists(), artifact_path


def test_write_run_creates_independent_runs(tmp_path: Path) -> None:
    first = cli_write_run(FIXTURE_TASK, tmp_path / "runs")
    second = cli_write_run(FIXTURE_TASK, tmp_path / "runs")

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    first_run = parse_run_dir_from_stdout(first.stdout)
    second_run = parse_run_dir_from_stdout(second.stdout)
    assert first_run != second_run
    assert first_run.exists()
    assert second_run.exists()


def test_sample_and_expected_output_are_not_promoted_as_reusable_facts(tmp_path: Path) -> None:
    run_dir = parse_run_dir_from_stdout(cli_write_run(FIXTURE_TASK, tmp_path / "runs").stdout)
    reusable = (run_dir / "learning" / "reusable_patterns.md").read_text(encoding="utf-8")
    profile = (run_dir / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    patch = (run_dir / "learning" / "candidate_skill_patch.md").read_text(encoding="utf-8")
    combined_lower = f"{reusable}\n{profile}\n{patch}".lower()

    assert "sample_hara.md (fact source)" not in combined_lower
    assert "expected_output_shape.md (fact source)" not in combined_lower
    assert "sample documents as fact sources" in reusable
    assert "expected_output_shape" in reusable
    assert "sample_is_fact_source: false" in profile
    assert "expected_output_shape_is_fact_source: false" in profile
    assert "Do not use sample documents as fact sources." in patch
    assert "Do not use expected output shape as fact sources." in patch


def test_hara_professional_judgments_remain_unapproved_in_learning(tmp_path: Path) -> None:
    run_dir = parse_run_dir_from_stdout(cli_write_run(FIXTURE_TASK, tmp_path / "runs").stdout)
    learning_text = "\n".join(
        [
            (run_dir / "learning" / "run_summary.md").read_text(encoding="utf-8"),
            (run_dir / "learning" / "reusable_patterns.md").read_text(encoding="utf-8"),
            (run_dir / "learning" / "candidate_skill_patch.md").read_text(encoding="utf-8"),
        ]
    )
    learning_lower = learning_text.lower()

    for claim in FORBIDDEN_HARA_APPROVAL_CLAIMS:
        assert claim.lower() not in learning_lower
    assert "human confirmation" in learning_lower
    assert "needs_user_confirmation" in learning_lower
    assert "pending" in learning_lower
