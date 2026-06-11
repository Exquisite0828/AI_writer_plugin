import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_6_ARTIFACTS = {
    "review/review_report.json",
    "review/template_review.md",
    "review/checklist_review.md",
    "review/evidence_review.md",
    "review/final_review.md",
    "verify/verify_report.json",
    "verify/failures.md",
}

REQUIRED_CHECKS = {
    "CHK-001": "required_phase5_artifacts_exist",
    "CHK-002": "full_draft_exists",
    "CHK-003": "section_drafts_match_section_tasks",
    "CHK-004": "template_sections_present_in_full_draft",
    "CHK-005": "draft_sections_are_in_task_order",
    "CHK-006": "citation_ids_parseable",
    "CHK-007": "citation_ids_exist_in_citation_plan",
    "CHK-008": "citation_ids_allowed_by_section_task",
    "CHK-009": "cited_sources_exist_in_source_index",
    "CHK-010": "source_support_sections_present",
    "CHK-011": "sample_not_used_as_fact_source",
    "CHK-012": "expected_output_shape_not_used_as_fact_source",
    "CHK-013": "reference_not_used_as_project_fact",
    "CHK-014": "hara_sensitive_sections_keep_confirmation_markers",
    "CHK-015": "final_hara_conclusion_phrases_absent",
    "CHK-016": "unresolved_questions_carried_forward",
    "CHK-017": "knowledge_gaps_carried_forward",
    "CHK-018": "review_artifacts_exist",
    "CHK-019": "no_later_phase_artifacts_generated",
    "CHK-020": "manifest_updated_to_phase_6",
    "CHK-021": "provenance_index_exists",
    "CHK-022": "source_tier_policy_valid",
    "CHK-023": "sample_tier_is_style_only",
    "CHK-024": "reference_tier_is_methodology_only",
    "CHK-025": "critical_claim_source_tier_sufficient",
    "CHK-026": "required_human_confirmation_not_hidden",
    "CHK-027": "final_report_has_provenance_summary",
    "CHK-028": "final_delivery_has_open_confirmations",
    "CHK-029": "profile_version_recorded_when_available",
}

LATER_PHASE_PATHS = [
    "revision_plan.json",
    "revised",
    "final",
    "trace",
    "learning",
    "revised/full_draft.md",
    "final/final_report.md",
    "trace/session_trace.jsonl",
    "learning/run_summary.md",
]

FORBIDDEN_ROOT_ENTRIES = [
    "schemas",
    "scripts",
    "agents",
    "plugin.json",
]

ALLOWED_REVIEW_STATUSES = {"passed", "passed_with_warnings", "open_blockers", "failed"}
ALLOWED_VERIFY_STATUSES = {"passed", "passed_with_warnings", "blocked", "failed"}
ALLOWED_SEVERITIES = {"P0", "P1", "P2", "Info"}
ALLOWED_ITEM_STATUSES = {"open", "acknowledged", "waived", "resolved"}
ALLOWED_CHECK_STATUSES = {"passed", "failed", "blocked", "warning", "skipped"}


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
    import ai_writing_plugin.run_manager as run_manager

    runner = getattr(run_manager, "review_run", None)
    assert runner is not None, "review_run is not implemented"
    return runner(run_dir=run_dir)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(f"{json.dumps(data, ensure_ascii=False, indent=2)}\n", encoding="utf-8")


def run_phase_4_fixture(tmp_path: Path) -> Path:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    return run_dir


def run_phase_5_fixture(tmp_path: Path) -> Path:
    run_dir = run_phase_4_fixture(tmp_path)
    draft_run(run_dir)
    return run_dir


def run_phase_6_fixture(tmp_path: Path) -> Path:
    run_dir = run_phase_5_fixture(tmp_path)
    review_run(run_dir)
    return run_dir


def cli_review_run(run_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "review-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def review_report(run_dir: Path) -> dict:
    return read_json(run_dir / "review" / "review_report.json")


def verify_report(run_dir: Path) -> dict:
    return read_json(run_dir / "verify" / "verify_report.json")


def section_tasks(run_dir: Path) -> dict:
    return read_json(run_dir / "plans" / "section_tasks.json")


def citation_plan(run_dir: Path) -> dict:
    return read_json(run_dir / "plans" / "citation_plan.json")


def inventory(run_dir: Path) -> dict:
    return read_json(run_dir / "inputs" / "input_inventory.json")


def item_categories(report: dict, category: str) -> list[dict]:
    return [item for item in report["items"] if item["category"] == category]


def p0_categories(report: dict) -> set[str]:
    return {item["category"] for item in report["items"] if item["severity"] == "P0"}


def first_task(run_dir: Path) -> dict:
    return section_tasks(run_dir)["tasks"][0]


def task_draft_path(run_dir: Path, task: dict) -> Path:
    return run_dir / task["future_output_path"]


def append_to_task_draft(run_dir: Path, task: dict, text: str) -> None:
    draft_path = task_draft_path(run_dir, task)
    draft_path.write_text(f"{draft_path.read_text(encoding='utf-8')}\n{text}\n", encoding="utf-8")


def file_id_for_role(run_dir: Path, role: str) -> str:
    return next(file["file_id"] for file in inventory(run_dir)["files"] if file["role"] == role)


def test_review_run_creates_phase_6_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)

    for relative_path in PHASE_6_ARTIFACTS:
        assert (run_dir / relative_path).exists()


def test_review_run_updates_manifest_to_phase_6(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]
    phase_5_paths = {task["future_output_path"] for task in section_tasks(run_dir)["tasks"]} | {"draft/full_draft.md"}

    assert manifest["phase"] == "phase_6"
    assert manifest["status"] == "reviewed_verified"
    assert PHASE_6_ARTIFACTS <= set(artifact_paths)
    assert phase_5_paths <= set(artifact_paths)
    assert len(artifact_paths) == len(set(artifact_paths))


def test_review_report_schema_fields_are_complete(tmp_path: Path) -> None:
    report = review_report(run_phase_6_fixture(tmp_path))
    required_item_fields = {
        "review_id",
        "severity",
        "category",
        "section_id",
        "task_id",
        "artifact",
        "description",
        "evidence_ids",
        "suggested_fix",
        "status",
        "blocks_final",
    }

    assert set(report) == {"run_id", "generated_at", "document_type", "status", "items", "summary", "warnings"}
    assert report["document_type"]["task_type"] == "hara"
    assert report["status"] in ALLOWED_REVIEW_STATUSES
    assert report["items"]
    for item in report["items"]:
        assert set(item) == required_item_fields
        assert item["review_id"].startswith("REV-")
        assert item["severity"] in ALLOWED_SEVERITIES
        assert item["status"] in ALLOWED_ITEM_STATUSES
        assert item["status"] == "open"
        assert isinstance(item["blocks_final"], bool)


def test_template_review_covers_all_outline_sections(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    template_review = (run_dir / "review" / "template_review.md").read_text(encoding="utf-8")

    assert "# 模板审查" in template_review
    assert "模板章节覆盖" in template_review
    for section in template_structure["outline_sections"]:
        assert section["section_id"] in template_review
        assert section["title"] in template_review


def test_template_review_checks_section_task_draft_mapping(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    template_review = (run_dir / "review" / "template_review.md").read_text(encoding="utf-8")
    report_text = json.dumps(review_report(run_dir), ensure_ascii=False)

    for task in section_tasks(run_dir)["tasks"]:
        assert task["task_id"] in template_review or task["task_id"] in report_text
        assert task["future_output_path"] in template_review or task["future_output_path"] in report_text


def test_checklist_review_reports_checklist_material_status(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    checklist_review = (run_dir / "review" / "checklist_review.md").read_text(encoding="utf-8")
    checklist_file = next(file for file in inventory(run_dir)["files"] if file["role"] == "checklist")

    assert "# Checklist 审查" in checklist_review
    assert "Checklist 材料状态" in checklist_review
    assert checklist_file["file_id"] in checklist_review
    assert checklist_file["path"] in checklist_review
    assert "内置草稿检查清单" in checklist_review


def test_checklist_review_checks_hara_confirmation_markers(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    checklist_review = (run_dir / "review" / "checklist_review.md").read_text(encoding="utf-8")
    final_review = (run_dir / "review" / "final_review.md").read_text(encoding="utf-8")

    assert "NEEDS_USER_CONFIRMATION" in checklist_review
    assert "HARA" in checklist_review or "human confirmation" in checklist_review
    assert "需要人工确认" in final_review
    assert item_categories(review_report(run_dir), "hara_confirmation_required")


def test_evidence_review_checks_citation_traceability(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    evidence_review = (run_dir / "review" / "evidence_review.md").read_text(encoding="utf-8")
    used_evidence = next(detail["evidence_id"] for section in citation_plan(run_dir)["sections"] for detail in section["evidence_details"])
    used_source = next(detail["source_id"] for section in citation_plan(run_dir)["sections"] for detail in section["evidence_details"])

    assert "# 证据审查" in evidence_review
    assert "引用可追溯性" in evidence_review
    assert used_evidence in evidence_review
    assert used_source in evidence_review


def test_review_run_confirms_valid_draft_evidence_ids_in_baseline(tmp_path: Path) -> None:
    report = review_report(run_phase_6_fixture(tmp_path))

    assert "invalid_citation" not in p0_categories(report)
    assert "sample_fact_source" not in p0_categories(report)
    assert "expected_output_shape_fact_source" not in p0_categories(report)


def test_hara_confirmation_blockers_are_recorded(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)
    report = review_report(run_dir)
    verify = verify_report(run_dir)
    hara_items = item_categories(report, "hara_confirmation_required")

    assert hara_items
    assert all(item["severity"] == "P1" for item in hara_items)
    assert all(item["blocks_final"] is True for item in hara_items)
    assert verify["status"] in {"blocked", "passed_with_warnings"}
    assert "需要人工确认" in (run_dir / "review" / "final_review.md").read_text(encoding="utf-8")


def test_final_review_summarizes_severity_counts(tmp_path: Path) -> None:
    final_review = (run_phase_6_fixture(tmp_path) / "review" / "final_review.md").read_text(encoding="utf-8")

    assert "# 最终审查" in final_review
    assert "审查摘要" in final_review
    assert "P0" in final_review
    assert "P1" in final_review
    assert "P2" in final_review
    assert "Info" in final_review
    assert "阻塞问题" in final_review
    assert "Final readiness" in final_review
    assert "阶段边界说明" in final_review


def test_verify_report_schema_fields_are_complete(tmp_path: Path) -> None:
    verify = verify_report(run_phase_6_fixture(tmp_path))
    required_check_fields = {
        "check_id",
        "name",
        "status",
        "severity",
        "details",
        "related_artifacts",
        "review_item_ids",
    }

    assert set(verify) == {
        "run_id",
        "generated_at",
        "document_type",
        "status",
        "summary",
        "checks",
        "blocking_failures",
        "warnings",
    }
    assert verify["document_type"]["task_type"] == "hara"
    assert verify["status"] in ALLOWED_VERIFY_STATUSES
    assert verify["checks"]
    for check in verify["checks"]:
        assert set(check) == required_check_fields
        assert check["status"] in ALLOWED_CHECK_STATUSES
        assert check["severity"] in ALLOWED_SEVERITIES


def test_verify_report_contains_required_check_ids(tmp_path: Path) -> None:
    checks = {check["check_id"]: check["name"] for check in verify_report(run_phase_6_fixture(tmp_path))["checks"]}

    assert checks == REQUIRED_CHECKS


def test_failures_md_explains_blockers(tmp_path: Path) -> None:
    failures = (run_phase_6_fixture(tmp_path) / "verify" / "failures.md").read_text(encoding="utf-8")

    assert "# 验证失败项" in failures
    assert "摘要" in failures
    assert "人工确认阻塞项" in failures
    assert "Phase 7 建议" in failures
    assert "修订推迟到 Phase 7" in failures


def test_invalid_citation_id_is_reported_as_p0(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    append_to_task_draft(run_dir, first_task(run_dir), "Injected unsupported citation [EVD-999].")

    review_run(run_dir)

    report = review_report(run_dir)
    verify = verify_report(run_dir)
    failures = (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")
    invalid_items = item_categories(report, "invalid_citation")

    assert invalid_items
    assert any(item["severity"] == "P0" and item["blocks_final"] is True for item in invalid_items)
    assert any(check["name"] == "citation_ids_exist_in_citation_plan" and check["status"] in {"failed", "blocked"} for check in verify["checks"])
    assert verify["status"] in {"blocked", "failed"}
    assert "EVD-999" in failures


def test_evidence_not_allowed_by_section_task_is_p0(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    task = first_task(run_dir)
    task_allowed = set(task["allowed_evidence"])
    other_evidence = next(
        detail["evidence_id"]
        for section in citation_plan(run_dir)["sections"]
        for detail in section["evidence_details"]
        if detail["evidence_id"] not in task_allowed
    )
    append_to_task_draft(run_dir, task, f"Injected cross-section citation [{other_evidence}].")

    review_run(run_dir)

    invalid_items = item_categories(review_report(run_dir), "invalid_citation")
    assert invalid_items
    assert any(item["severity"] == "P0" and other_evidence in item["evidence_ids"] for item in invalid_items)


def test_sample_fact_source_misuse_is_reported_as_p0(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    sample_file_id = file_id_for_role(run_dir, "sample")
    append_to_task_draft(run_dir, first_task(run_dir), f"- EVD-FAKE | SRC-FAKE | {sample_file_id} | fact_support | confidence=1.00")

    review_run(run_dir)

    items = item_categories(review_report(run_dir), "sample_fact_source")
    failures = (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")
    assert items
    assert any(item["severity"] == "P0" and item["blocks_final"] is True for item in items)
    assert "sample" in failures or sample_file_id in failures


def test_expected_output_shape_fact_source_misuse_is_reported_as_p0(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    expected_file_id = file_id_for_role(run_dir, "expected_output_shape")
    append_to_task_draft(run_dir, first_task(run_dir), f"- EVD-FAKE | SRC-FAKE | {expected_file_id} | fact_support | confidence=1.00")

    review_run(run_dir)

    items = item_categories(review_report(run_dir), "expected_output_shape_fact_source")
    assert items
    assert any(item["severity"] == "P0" and item["blocks_final"] is True for item in items)


def test_final_hara_conclusion_phrase_is_p0(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    rating_task = next(task for task in section_tasks(run_dir)["tasks"] if "S/E/C" in task["section_title"])
    append_to_task_draft(run_dir, rating_task, "The final ASIL is ASIL D.")

    review_run(run_dir)

    items = item_categories(review_report(run_dir), "final_hara_conclusion")
    verify = verify_report(run_dir)
    assert items
    assert any(item["severity"] == "P0" and item["blocks_final"] is True for item in items)
    assert any(check["name"] == "final_hara_conclusion_phrases_absent" and check["status"] in {"failed", "blocked"} for check in verify["checks"])


def test_missing_confirmation_marker_in_hara_sensitive_section_is_p0(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    hazard_task = next(task for task in section_tasks(run_dir)["tasks"] if task["section_title"] == "Hazard Identification")
    hazard_path = task_draft_path(run_dir, hazard_task)
    hazard_path.write_text(hazard_path.read_text(encoding="utf-8").replace("NEEDS_USER_CONFIRMATION", "CONFIRMATION_REMOVED"), encoding="utf-8")

    review_run(run_dir)

    items = item_categories(review_report(run_dir), "hara_confirmation_required")
    verify = verify_report(run_dir)
    assert any(item["severity"] == "P0" and item["task_id"] == hazard_task["task_id"] for item in items)
    assert any(check["name"] == "hara_sensitive_sections_keep_confirmation_markers" and check["status"] in {"failed", "blocked"} for check in verify["checks"])


def test_missing_section_draft_is_reported(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    missing_task = next(task for task in section_tasks(run_dir)["tasks"] if task["future_output_path"] == "draft/section_003.md")
    task_draft_path(run_dir, missing_task).unlink()

    review_run(run_dir)

    report = review_report(run_dir)
    verify = verify_report(run_dir)
    failures = (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")
    assert any(item["category"] == "template_mismatch" and "section_003.md" in item["artifact"] for item in report["items"])
    assert any(check["name"] == "section_drafts_match_section_tasks" and check["status"] in {"failed", "blocked"} for check in verify["checks"])
    assert "section_003.md" in failures


def test_review_run_fails_when_full_draft_missing(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    (run_dir / "draft" / "full_draft.md").unlink()

    result = cli_review_run(run_dir)

    assert result.returncode != 0
    assert "full_draft is required for review" in result.stderr
    assert not (run_dir / "review").exists()
    assert not (run_dir / "verify").exists()


def test_review_run_fails_when_citation_plan_missing(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    (run_dir / "plans" / "citation_plan.json").unlink()

    result = cli_review_run(run_dir)

    assert result.returncode != 0
    assert "section_tasks and citation_plan are required for review" in result.stderr


def test_review_run_fails_when_source_index_missing(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    (run_dir / "knowledge" / "source_index.json").unlink()

    result = cli_review_run(run_dir)

    assert result.returncode != 0
    assert "source_index is required" in result.stderr


def test_review_run_requires_phase_5_run(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    result = cli_review_run(run_dir)

    assert result.returncode != 0
    assert "review-run requires a drafted Phase 5 run" in result.stderr
    assert not (run_dir / "review").exists()
    assert not (run_dir / "verify").exists()


def test_baseline_phase5_draft_has_no_p0_review_items(tmp_path: Path) -> None:
    report = review_report(run_phase_6_fixture(tmp_path))

    assert report["summary"]["p0_items"] == 0
    assert report["summary"]["p1_items"] >= 1
    assert report["summary"]["final_readiness"] == "blocked"


def test_review_run_does_not_generate_later_phase_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)

    for relative_path in LATER_PHASE_PATHS:
        assert not (run_dir / relative_path).exists()


def test_repeated_review_run_does_not_duplicate_manifest_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)

    review_run(run_dir)
    review_run(run_dir)

    artifact_paths = [artifact["path"] for artifact in read_json(run_dir / "manifest.json")["artifacts"]]
    for artifact_path in PHASE_6_ARTIFACTS:
        assert artifact_paths.count(artifact_path) == 1


def test_review_run_cli_success(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)

    result = cli_review_run(run_dir)

    assert result.returncode == 0, result.stderr
    assert "审查和验证已完成" in result.stdout
    assert "review/review_report.json" in result.stdout
    assert "verify/verify_report.json" in result.stdout


def test_review_run_does_not_create_forbidden_root_directories() -> None:
    for entry in FORBIDDEN_ROOT_ENTRIES:
        assert not (REPO_ROOT / entry).exists()


def test_review_artifacts_are_human_readable(tmp_path: Path) -> None:
    run_dir = run_phase_6_fixture(tmp_path)

    assert "摘要" in (run_dir / "review" / "template_review.md").read_text(encoding="utf-8")
    assert "问题" in (run_dir / "review" / "template_review.md").read_text(encoding="utf-8")
    assert "摘要" in (run_dir / "review" / "checklist_review.md").read_text(encoding="utf-8")
    assert "内置草稿检查清单" in (run_dir / "review" / "checklist_review.md").read_text(encoding="utf-8")
    assert "摘要" in (run_dir / "review" / "evidence_review.md").read_text(encoding="utf-8")
    assert "引用可追溯性" in (run_dir / "review" / "evidence_review.md").read_text(encoding="utf-8")
    assert "审查摘要" in (run_dir / "review" / "final_review.md").read_text(encoding="utf-8")
    assert "建议的 Phase 7 动作" in (run_dir / "review" / "final_review.md").read_text(encoding="utf-8")
    assert "摘要" in (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")
    assert "Phase 7 建议" in (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")
