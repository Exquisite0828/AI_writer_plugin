import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "examples" / "custom_technical_note_profile_demo_fixture"
DEMO_TASK = DEMO_DIR / "task.yaml"

REQUIRED_ARTIFACTS = [
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/provenance_index.json",
    "knowledge/knowledge_gaps.md",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
    "plans/citation_plan.json",
    "plans/claim_support_matrix.json",
    "plans/outline_final.md",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
    "draft/full_draft.md",
    "review/review_report.json",
    "review/checklist_review.md",
    "review/final_review.md",
    "verify/verify_report.json",
    "verify/failures.md",
    "revision_plan.json",
    "revised/full_draft.md",
    "revised/change_log.md",
    "final/final_report.md",
    "final/delivery_summary.md",
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/reusable_patterns.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
    "learning/promotion_report.md",
]

PLANNING_OUTPUTS = [
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/citation_plan.json",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
]

FORBIDDEN_HARA_LEAKAGE = [
    "HARA",
    "ASIL",
    "S/E/C",
    "severity rating",
    "exposure rating",
    "controllability rating",
    "hazardous event",
    "safety goal",
    "HARA professional judgment",
]

SAMPLE_ONLY_CLAIMS = [
    "the implementation is approved",
    "compatibility is validated for all gateway versions",
    "the deployment is production ready",
    "no deployment risk exists",
    "cost is final",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def custom_profile_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    runs_dir = tmp_path_factory.mktemp("custom-profile-runs")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "write-run",
            "--task",
            str(DEMO_TASK),
            "--runs-dir",
            str(runs_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return Path(next(line.removeprefix("Run: ").strip() for line in result.stdout.splitlines() if line.startswith("Run: ")))


def test_external_profile_task_yaml_is_explicit_and_safe() -> None:
    task = yaml.safe_load(DEMO_TASK.read_text(encoding="utf-8"))

    assert task["task_type"] == "custom_technical_note"
    assert task["document_profile_path"] == "profiles/document_types/customer_demo/custom_technical_note.yaml"
    assert not Path(task["document_profile_path"]).is_absolute()
    assert ".." not in Path(task["document_profile_path"]).parts
    assert {item["path"]: item["role"] for item in task["inputs"]} == {
        "inputs/source.md": "source",
        "inputs/template.md": "template",
        "inputs/checklist.md": "checklist",
        "inputs/reference.md": "reference",
        "inputs/sample.md": "sample",
    }


def test_external_profile_demo_full_run(custom_profile_run: Path) -> None:
    manifest = read_json(custom_profile_run / "manifest.json")
    task_brief = read_json(custom_profile_run / "task_brief.json")
    final_report = (custom_profile_run / "final" / "final_report.md").read_text(encoding="utf-8")

    for relative_path in REQUIRED_ARTIFACTS:
        assert (custom_profile_run / relative_path).exists(), relative_path
    assert manifest["run_id"].endswith("custom_technical_note")
    assert manifest["status"] == "completed_with_candidate_updates_proposed"
    assert task_brief["task_type"] == "custom_technical_note"
    assert task_brief["display_name"] == "Custom Technical Note"
    assert "Final Custom Technical Note Package" in final_report


def test_external_profile_artifacts_record_profile_id_and_version(custom_profile_run: Path) -> None:
    manifest = read_json(custom_profile_run / "manifest.json")
    task_brief = read_json(custom_profile_run / "task_brief.json")
    verify_report = read_json(custom_profile_run / "verify" / "verify_report.json")

    for artifact in [manifest, task_brief]:
        assert artifact["profile"]["profile_id"] == "customer_demo.custom_technical_note"
        assert artifact["profile"]["profile_version"] == "0.1.0"
        assert artifact["profile"]["profile_source"] == "external"
        assert artifact["profile"]["profile_path"] == "profiles/document_types/customer_demo/custom_technical_note.yaml"
        assert artifact["profile"]["validation_status"] == "passed"
    assert verify_report["document_type"]["task_type"] == "custom_technical_note"
    assert verify_report["document_type"]["display_name"] == "Custom Technical Note"
    assert "deployment risk" in verify_report["document_type"]["critical_claims"]
    assert "deployment is production ready" in verify_report["document_type"]["forbidden_final_claims"]


def test_external_profile_sample_not_fact_source(custom_profile_run: Path) -> None:
    inventory = read_json(custom_profile_run / "inputs" / "input_inventory.json")
    source_index = read_json(custom_profile_run / "knowledge" / "source_index.json")
    evidence_map = read_json(custom_profile_run / "plans" / "evidence_map.json")
    citation_plan = read_json(custom_profile_run / "plans" / "citation_plan.json")
    section_tasks = read_json(custom_profile_run / "plans" / "section_tasks.json")
    draft = (custom_profile_run / "draft" / "full_draft.md").read_text(encoding="utf-8")
    final_report = (custom_profile_run / "final" / "final_report.md").read_text(encoding="utf-8")
    combined_lower = f"{draft}\n{final_report}".lower()

    sample_files = [file for file in inventory["files"] if file["path"].endswith("sample.md")]
    assert sample_files
    assert all(file["role"] == "sample" and file["is_fact_source"] is False for file in sample_files)
    assert all(source["source_role"] != "sample" for source in source_index["sources"])
    assert all(
        candidate["source_role"] != "sample"
        for question in evidence_map["questions"]
        for candidate in question["evidence_candidates"]
    )
    assert all(
        detail["source_role"] != "sample"
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    )
    assert all("sample" in task["forbidden_sources"] for task in section_tasks["tasks"])
    for sample_claim in SAMPLE_ONLY_CLAIMS:
        assert sample_claim not in combined_lower


def test_external_profile_reference_not_project_fact_source(custom_profile_run: Path) -> None:
    inventory = read_json(custom_profile_run / "inputs" / "input_inventory.json")
    citation_plan = read_json(custom_profile_run / "plans" / "citation_plan.json")

    reference_files = [file for file in inventory["files"] if file["path"].endswith("reference.md")]
    assert reference_files
    assert all(file["role"] == "reference" and file["is_fact_source"] is False for file in reference_files)
    assert all(
        not (detail["source_role"] == "reference" and detail["usage"] == "fact_support")
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    )


def test_external_profile_critical_claims_require_confirmation(custom_profile_run: Path) -> None:
    unresolved = (custom_profile_run / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")
    final_review = (custom_profile_run / "review" / "final_review.md").read_text(encoding="utf-8")
    verify_report = read_json(custom_profile_run / "verify" / "verify_report.json")
    final_report = (custom_profile_run / "final" / "final_report.md").read_text(encoding="utf-8")
    hitl_trace = (custom_profile_run / "trace" / "hitl_decisions.jsonl").read_text(encoding="utf-8")
    combined = f"{unresolved}\n{final_review}\n{json.dumps(verify_report, ensure_ascii=False)}\n{final_report}\n{hitl_trace}"
    combined_lower = combined.lower()

    assert "NEEDS_USER_CONFIRMATION" in combined
    assert "pending" in hitl_trace
    for claim in ["final deployment decision", "compatibility claim", "deployment risk", "cost or schedule commitment"]:
        assert claim in combined_lower


def test_external_profile_candidate_update_inactive(custom_profile_run: Path) -> None:
    candidate_profile = (custom_profile_run / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    promotion_report = (custom_profile_run / "learning" / "promotion_report.md").read_text(encoding="utf-8")

    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "Candidate activated: no" in promotion_report
    assert "Stable skill overwritten: no" in promotion_report


def test_external_profile_final_report_not_approval(custom_profile_run: Path) -> None:
    final_report = (custom_profile_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (custom_profile_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    revision_plan = read_json(custom_profile_run / "revision_plan.json")
    deliverable_lower = f"{final_report}\n{delivery_summary}".lower()

    assert "Status: ready_for_human_review" in final_report
    assert revision_plan["summary"]["status"] == "ready_for_human_review"
    assert "implementation is approved" not in deliverable_lower
    assert "compatibility is validated" not in deliverable_lower
    assert "deployment is production ready" not in deliverable_lower
    assert "no deployment risk exists" not in deliverable_lower


def test_external_profile_planning_outputs_do_not_leak_hara_terms(custom_profile_run: Path) -> None:
    for relative_path in PLANNING_OUTPUTS:
        text = (custom_profile_run / relative_path).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_HARA_LEAKAGE:
            assert forbidden not in text, f"{forbidden!r} leaked into {relative_path}"


def test_invalid_profile_writes_failures_and_verify_report(tmp_path: Path) -> None:
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
    runs_dir = tmp_path / "runs"
    result = subprocess.run(
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

    assert result.returncode != 0
    run_dirs = list(runs_dir.iterdir())
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    manifest = read_json(run_dir / "manifest.json")
    task_brief = read_json(run_dir / "task_brief.json")
    verify_report = read_json(run_dir / "verify" / "verify_report.json")
    failures = (run_dir / "verify" / "failures.md").read_text(encoding="utf-8")
    trace = (run_dir / "trace" / "session_trace.jsonl").read_text(encoding="utf-8")

    assert manifest["status"] == "blocked_invalid_document_profile"
    assert manifest["profile"]["validation_status"] == "failed"
    assert task_brief["profile"]["validation_status"] == "failed"
    assert verify_report["status"] in {"failed", "blocked"}
    assert "document_profile_validation" in json.dumps(verify_report)
    assert "profile validation failure" in failures.lower()
    assert "fact_source_roles" in failures
    assert "sample" in failures
    assert "document_profile_validation" in trace
    assert not (run_dir / "final" / "final_report.md").exists()
