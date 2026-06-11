import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_7_ARTIFACTS = {
    "revision_plan.json",
    "revised/full_draft.md",
    "revised/change_log.md",
    "final/final_report.md",
    "final/delivery_summary.md",
}

FORBIDDEN_RUN_PATHS = [
    "trace",
    "learning",
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
]

FORBIDDEN_ROOT_ENTRIES = [
    "schemas",
    "scripts",
    "agents",
    "plugin.json",
]

UNSAFE_FINAL_CLAIMS = [
    "final ASIL is",
    "risk is acceptable",
    "safety goal is approved",
    "final HARA conclusion",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    import ai_writing_plugin.run_manager as run_manager

    runner = getattr(run_manager, "finalize_run", None)
    assert runner is not None, "finalize_run is not implemented"
    return runner(run_dir=run_dir)


def run_until_phase_5(tmp_path: Path) -> Path:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    draft_run(run_dir)
    return run_dir


def run_until_phase_6(tmp_path: Path) -> Path:
    run_dir = run_until_phase_5(tmp_path)
    review_run(run_dir)
    return run_dir


def run_until_phase_7(tmp_path: Path) -> Path:
    run_dir = run_until_phase_6(tmp_path)
    finalize_run(run_dir)
    return run_dir


def cli_finalize_run(run_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "finalize-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_finalize_run_creates_phase_7_artifacts(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)

    for relative_path in PHASE_7_ARTIFACTS:
        artifact_path = run_dir / relative_path
        assert artifact_path.exists(), relative_path
        assert artifact_path.read_text(encoding="utf-8").strip()


def test_finalize_run_updates_manifest_to_phase_7(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]

    assert manifest["phase"] == "phase_7"
    assert manifest["status"] == "finalized_with_open_items"
    assert PHASE_7_ARTIFACTS <= set(artifact_paths)
    assert len(artifact_paths) == len(set(artifact_paths))


def test_revision_plan_references_review_report_items(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    review_report = read_json(run_dir / "review" / "review_report.json")
    revision_plan = read_json(run_dir / "revision_plan.json")
    important_review_items = [item for item in review_report["items"] if item["severity"] in {"P0", "P1"}]

    assert revision_plan["run_id"] == read_json(run_dir / "manifest.json")["run_id"]
    assert revision_plan["phase"] == "phase_7"
    assert revision_plan["source_artifacts"]["review_report"] == "review/review_report.json"
    assert revision_plan["summary"]["total_review_items"] == len(review_report["items"])
    assert revision_plan["summary"]["total_revision_tasks"] == len(revision_plan["tasks"])
    assert len(revision_plan["tasks"]) >= len(important_review_items)

    for task in revision_plan["tasks"]:
        assert {
            "revision_task_id",
            "severity",
            "category",
            "action",
            "requires_user_confirmation",
            "result",
        } <= set(task)


def test_hara_confirmations_remain_pending(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    revision_plan = read_json(run_dir / "revision_plan.json")
    hara_tasks = [task for task in revision_plan["tasks"] if task["category"] == "hara_confirmation_required"]
    revised = (run_dir / "revised" / "full_draft.md").read_text(encoding="utf-8")
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")

    assert "NEEDS_USER_CONFIRMATION" in revised
    assert "HARA 开放确认项" in final_report
    assert "pending" in final_report or "TBD" in final_report
    assert hara_tasks
    assert all(task["requires_user_confirmation"] is True for task in hara_tasks)
    assert all(task["result"] != "resolved" for task in hara_tasks)


def test_unsupported_and_weak_evidence_are_carried_to_final_outputs(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined = f"{final_report}\n{delivery_summary}".lower()

    assert "证据不足 / 弱证据" in final_report
    assert "剩余阻塞项" in delivery_summary
    assert "已知限制" in delivery_summary
    assert "unsupported" in combined
    assert "weak" in combined
    assert "unresolved" in combined


def test_knowledge_gaps_are_carried_into_final_outputs(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined = f"{final_report}\n{delivery_summary}"

    assert "missing_item_definition.md" in combined
    assert "unsupported_reference.pdf" in combined


def test_final_outputs_do_not_contain_unsafe_final_professional_claims(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined_lower = f"{final_report}\n{delivery_summary}".lower()

    for claim in UNSAFE_FINAL_CLAIMS:
        assert claim.lower() not in combined_lower


def test_unsafe_final_claims_in_draft_are_replaced_in_revised_draft(tmp_path: Path) -> None:
    run_dir = run_until_phase_6(tmp_path)
    draft_path = run_dir / "draft" / "full_draft.md"
    draft_path.write_text(
        draft_path.read_text(encoding="utf-8")
        + "\nThe final ASIL is ASIL D.\nRisk is acceptable.\nSafety goal is approved.\n",
        encoding="utf-8",
    )

    finalize_run(run_dir)

    revised = (run_dir / "revised" / "full_draft.md").read_text(encoding="utf-8")
    revised_lower = revised.lower()
    assert "the final asil is asil d" not in revised_lower
    assert "risk is acceptable" not in revised_lower
    assert "safety goal is approved" not in revised_lower
    assert "NEEDS_USER_CONFIRMATION: Unsupported final professional judgment omitted by Phase 7." in revised


def test_revised_draft_is_chinese_first_and_keeps_machine_status(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    revised = (run_dir / "revised" / "full_draft.md").read_text(encoding="utf-8")

    assert revised.startswith("# HARA 危害分析报告修订草稿")
    assert "Status: revised_with_open_items" in revised
    assert "## Phase 7 修订边界说明" in revised
    assert "## 已应用修订摘要" in revised
    assert "## 剩余人工确认项" in revised
    assert "## 带 Phase 7 注释的原始保守草稿" in revised


def test_delivery_summary_lists_limitations_and_workflow_scope_note(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")

    for heading in [
        "生成的内容",
        "审查 / 验证结果",
        "剩余阻塞项",
        "需要人工确认",
        "已知限制",
        "Workflow 范围说明",
    ]:
        assert heading in summary
    assert "Not Done In This Phase" not in summary
    assert "/write" not in summary
    assert "trace/session_trace.jsonl" not in summary
    assert "learning/candidate_profile_update.yaml" not in summary
    assert "candidate update 保持 proposed / inactive" in summary


def test_finalize_run_does_not_generate_trace_or_learning(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)

    for relative_path in FORBIDDEN_RUN_PATHS:
        assert not (run_dir / relative_path).exists()


def test_finalize_run_does_not_create_write_command_or_plugin_skeleton(tmp_path: Path) -> None:
    run_until_phase_7(tmp_path)
    help_result = subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "--help"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert help_result.returncode == 0
    assert "finalize-run" in help_result.stdout
    for entry in FORBIDDEN_ROOT_ENTRIES:
        assert not (REPO_ROOT / entry).exists()


def test_finalize_run_requires_phase_6_artifacts(tmp_path: Path) -> None:
    run_dir = run_until_phase_5(tmp_path)

    result = cli_finalize_run(run_dir)

    assert result.returncode != 0
    assert "review/review_report.json" in result.stderr or "Phase 6" in result.stderr
    assert not (run_dir / "revision_plan.json").exists()
    assert not (run_dir / "final").exists()


def test_finalize_run_fails_when_review_report_missing(tmp_path: Path) -> None:
    run_dir = run_until_phase_6(tmp_path)
    (run_dir / "review" / "review_report.json").unlink()

    result = cli_finalize_run(run_dir)

    assert result.returncode != 0
    assert "review/review_report.json" in result.stderr or "review_report" in result.stderr
    assert not (run_dir / "revision_plan.json").exists()


def test_finalize_run_fails_when_verify_report_missing(tmp_path: Path) -> None:
    run_dir = run_until_phase_6(tmp_path)
    (run_dir / "verify" / "verify_report.json").unlink()

    result = cli_finalize_run(run_dir)

    assert result.returncode != 0
    assert "verify/verify_report.json" in result.stderr or "verify_report" in result.stderr
    assert not (run_dir / "revision_plan.json").exists()


def test_repeated_finalize_run_is_idempotent(tmp_path: Path) -> None:
    run_dir = run_until_phase_6(tmp_path)

    finalize_run(run_dir)
    first_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    first_change_log = (run_dir / "revised" / "change_log.md").read_text(encoding="utf-8")
    finalize_run(run_dir)

    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]
    assert (run_dir / "final" / "final_report.md").read_text(encoding="utf-8") == first_report
    assert (run_dir / "revised" / "change_log.md").read_text(encoding="utf-8") == first_change_log
    for artifact_path in PHASE_7_ARTIFACTS:
        assert artifact_paths.count(artifact_path) == 1
    assert not any((run_dir / "final").glob("final_report_*.md"))


def test_finalize_run_cli_success(tmp_path: Path) -> None:
    run_dir = run_until_phase_6(tmp_path)

    result = cli_finalize_run(run_dir)

    assert result.returncode == 0, result.stderr
    assert "Finalize run completed" in result.stdout
    for artifact_path in PHASE_7_ARTIFACTS:
        assert artifact_path in result.stdout
        assert (run_dir / artifact_path).exists()


def test_full_pipeline_phase_0_to_7_cli(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    ingest_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "ingest-run",
            "--task",
            str(FIXTURE_TASK),
            "--runs-dir",
            str(runs_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ingest_result.returncode == 0, ingest_result.stderr
    run_dir = Path(next(line for line in ingest_result.stdout.splitlines() if line.startswith("Created run: ")).removeprefix("Created run: "))

    for command in ["outline-run", "evidence-run", "plan-run", "draft-run", "review-run", "finalize-run"]:
        result = subprocess.run(
            [sys.executable, "-m", "ai_writing_plugin", command, "--run", str(run_dir)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}
    assert manifest["phase"] == "phase_7"
    assert manifest["status"] == "finalized_with_open_items"
    assert PHASE_7_ARTIFACTS <= artifact_paths
    for relative_path in FORBIDDEN_RUN_PATHS:
        assert not (run_dir / relative_path).exists()


def test_baseline_final_status_is_not_fully_approved(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")

    assert manifest["status"] not in {"approved", "final_approved", "fully_approved", "accepted"}
    assert manifest["status"] == "finalized_with_open_items"
    assert "合格人工审查" in final_report
    assert "合格人工审查" in delivery_summary


def test_sample_and_expected_output_are_not_elevated_to_fact_sources(tmp_path: Path) -> None:
    run_dir = run_until_phase_7(tmp_path)
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined_lower = f"{final_report}\n{delivery_summary}".lower()

    assert "source_index.json" in combined_lower
    assert "citation_plan.json" in combined_lower
    assert "sample_hara.md (fact source)" not in combined_lower
    assert "expected_output_shape.md (fact source)" not in combined_lower
    assert "sample_hara.md" not in final_report.lower() or "non-fact" in combined_lower
    assert "expected_output_shape.md" not in final_report.lower() or "non-fact" in combined_lower


def test_phase_7_current_docs_are_present_and_synced() -> None:
    expected_docs = [
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "CURRENT_ARTIFACT_CONTRACTS.md",
        REPO_ROOT / "docs" / "RUNBOOK.md",
        REPO_ROOT / "docs" / "maintainers" / "ARCHITECTURE.md",
    ]

    for doc_path in expected_docs:
        assert doc_path.exists(), doc_path

    contracts = (REPO_ROOT / "docs" / "CURRENT_ARTIFACT_CONTRACTS.md").read_text(encoding="utf-8")
    runbook = (REPO_ROOT / "docs" / "RUNBOOK.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    for artifact_path in PHASE_7_ARTIFACTS:
        assert artifact_path in contracts
    assert "finalize-run" in runbook
    assert "历史 phase docs" in docs_index
    assert "不是当前执行指令" in docs_index
