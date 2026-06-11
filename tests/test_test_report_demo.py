import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.document_types import get_document_type_rules


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "examples" / "test_report_demo_fixture"
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

USER_FACING_OUTPUTS = [
    "draft/full_draft.md",
    "revised/full_draft.md",
    "final/final_report.md",
    "final/delivery_summary.md",
    "review/final_review.md",
    "verify/failures.md",
    "learning/run_summary.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
    "learning/promotion_report.md",
]

FORBIDDEN_LEAKAGE = [
    "HARA",
    "ASIL",
    "S/E/C",
    "hazardous event",
    "safety goal",
    "HARA professional judgment",
    "technical_solution",
    "architecture decision",
    "rollout risk acceptance",
    "architecture is approved",
]

SAMPLE_ONLY_CLAIMS = [
    "all tests passed",
    "release is approved",
    "no defects exist",
    "coverage is complete",
]

FORBIDDEN_FINAL_CONCLUSIONS = [
    "all tests passed",
    "release is approved",
    "no defects exist",
    "coverage is complete",
    "system is production ready",
    "ready for production without risk",
]

READABLE_JSON_KEYS = {"details", "message", "warnings", "blocking_failures", "description", "suggested_fix", "notes"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def readable_json_strings(value: object, key: str = "") -> list[str]:
    if isinstance(value, dict):
        strings: list[str] = []
        for child_key, child_value in value.items():
            strings.extend(readable_json_strings(child_value, child_key))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(readable_json_strings(item, key))
        return strings
    if isinstance(value, str) and key in READABLE_JSON_KEYS:
        return [value]
    return []


@pytest.fixture(scope="module")
def test_report_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    runs_dir = tmp_path_factory.mktemp("test-report-runs")
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


def test_test_report_fixture_uses_current_task_schema() -> None:
    expected_inputs = {
        "inputs/system_under_test.md": "source",
        "inputs/test_plan.md": "source",
        "inputs/test_results.csv": "source",
        "inputs/defect_summary.md": "source",
        "inputs/test_report_template.md": "template",
        "inputs/checklist.md": "checklist",
        "inputs/test_methodology_reference.md": "reference",
        "inputs/sample_test_report.md": "sample",
    }

    task = yaml.safe_load(DEMO_TASK.read_text(encoding="utf-8"))
    assert task["task_type"] == "test_report"
    assert "final pass/fail conclusion" in task["requires_human_confirmation"]
    assert "release readiness or acceptance recommendation" in task["requires_human_confirmation"]
    assert set(task) >= {"task_type", "task_title", "target_audience", "inputs"}
    assert {item["path"]: item["role"] for item in task["inputs"]} == expected_inputs
    for relative_path in expected_inputs:
        assert (DEMO_DIR / relative_path).exists(), relative_path


def test_test_report_full_run_artifact_set_and_task_type(test_report_run: Path) -> None:
    rules = get_document_type_rules("test_report")
    manifest = read_json(test_report_run / "manifest.json")
    task_brief = read_json(test_report_run / "task_brief.json")

    for relative_path in REQUIRED_ARTIFACTS:
        assert (test_report_run / relative_path).exists(), relative_path
    assert task_brief["task_type"] == rules.task_type
    assert manifest["run_id"].endswith(rules.task_type)
    assert manifest["status"] == "completed_with_candidate_updates_proposed"


def test_test_report_outputs_do_not_leak_other_document_type_terms(test_report_run: Path) -> None:
    for relative_path in USER_FACING_OUTPUTS:
        text = (test_report_run / relative_path).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_LEAKAGE:
            assert forbidden not in text, f"{forbidden!r} leaked into {relative_path}"

    for relative_path in ["review/review_report.json", "verify/verify_report.json"]:
        report = read_json(test_report_run / relative_path)
        for text in readable_json_strings(report):
            for forbidden in FORBIDDEN_LEAKAGE:
                assert forbidden not in text, f"{forbidden!r} leaked into {relative_path} readable field: {text}"


def test_test_report_input_roles_and_sample_boundary(test_report_run: Path) -> None:
    inventory = read_json(test_report_run / "inputs" / "input_inventory.json")
    source_index = read_json(test_report_run / "knowledge" / "source_index.json")
    evidence_map = read_json(test_report_run / "plans" / "evidence_map.json")
    citation_plan = read_json(test_report_run / "plans" / "citation_plan.json")
    final_report = (test_report_run / "final" / "final_report.md").read_text(encoding="utf-8")
    revised = (test_report_run / "revised" / "full_draft.md").read_text(encoding="utf-8")
    draft = (test_report_run / "draft" / "full_draft.md").read_text(encoding="utf-8")
    combined_lower = f"{draft}\n{revised}\n{final_report}".lower()

    fact_source_paths = {
        "inputs/system_under_test.md",
        "inputs/test_plan.md",
        "inputs/test_results.csv",
        "inputs/defect_summary.md",
    }
    files_by_path = {file["path"]: file for file in inventory["files"]}
    for path in fact_source_paths:
        assert files_by_path[path]["role"] == "source"
        assert files_by_path[path]["is_fact_source"] is True

    sample = files_by_path["inputs/sample_test_report.md"]
    assert sample["role"] == "sample"
    assert sample["is_fact_source"] is False
    assert files_by_path["inputs/test_report_template.md"]["is_fact_source"] is False
    assert files_by_path["inputs/checklist.md"]["is_fact_source"] is False
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
    for sample_claim in SAMPLE_ONLY_CLAIMS:
        assert sample_claim not in combined_lower


def test_test_report_reference_is_not_project_fact_source(test_report_run: Path) -> None:
    inventory = read_json(test_report_run / "inputs" / "input_inventory.json")
    source_index = read_json(test_report_run / "knowledge" / "source_index.json")
    citation_plan = read_json(test_report_run / "plans" / "citation_plan.json")

    reference_files = [file for file in inventory["files"] if file["path"].endswith("test_methodology_reference.md")]
    assert reference_files
    assert all(file["role"] == "reference" and file["is_fact_source"] is False for file in reference_files)
    assert any(
        source["path"].endswith("test_methodology_reference.md")
        and source["source_role"] == "reference"
        and source["is_fact_source"] is False
        for source in source_index["sources"]
    )
    assert all(
        not (detail["source_role"] == "reference" and detail["usage"] == "fact_support")
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    )


def test_test_report_results_and_final_conclusion_are_not_fabricated(test_report_run: Path) -> None:
    rules = get_document_type_rules("test_report")
    test_results = (DEMO_DIR / "inputs" / "test_results.csv").read_text(encoding="utf-8")
    final_review = (test_report_run / "review" / "final_review.md").read_text(encoding="utf-8")
    verify_report = read_json(test_report_run / "verify" / "verify_report.json")
    revision_plan = read_json(test_report_run / "revision_plan.json")
    final_report = (test_report_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (test_report_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined = f"{final_review}\n{json.dumps(verify_report, ensure_ascii=False)}\n{final_report}\n{delivery_summary}"
    deliverable_lower = f"{final_report}\n{delivery_summary}".lower()

    for status in ["PASS", "FAIL", "BLOCKED"]:
        assert status in test_results
    assert rules.confirmation_marker in combined
    for claim in [
        "final pass/fail conclusion",
        "release readiness or acceptance recommendation",
        "coverage sufficiency conclusion",
        "unresolved issue acceptance",
    ]:
        assert claim in combined.lower()
    assert any(task["requires_user_confirmation"] for task in revision_plan["tasks"])
    assert revision_plan["summary"]["pending_user_confirmation_tasks"] > 0
    assert f"Status: {rules.default_final_status}" in final_report
    for forbidden in FORBIDDEN_FINAL_CONCLUSIONS:
        assert forbidden not in deliverable_lower


def test_test_report_candidate_updates_stay_proposed_inactive(test_report_run: Path) -> None:
    candidate_profile = (test_report_run / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    candidate_patch = (test_report_run / "learning" / "candidate_skill_patch.md").read_text(encoding="utf-8")
    promotion_report = (test_report_run / "learning" / "promotion_report.md").read_text(encoding="utf-8")

    assert "document_type: test_report" in candidate_profile
    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "rollback_supported: true" in candidate_profile
    assert "Status: proposed_only" in candidate_patch
    assert "skills/document-types/test_report/SKILL.md" in candidate_patch
    assert "This patch has not been applied." in candidate_patch
    assert "Stable skill overwritten: no" in promotion_report
    assert "Candidate activated: no" in promotion_report
    stable_skill_path = REPO_ROOT / "skills" / "document-types" / "test_report" / "SKILL.md"
    if stable_skill_path.exists():
        stable_skill = stable_skill_path.read_text(encoding="utf-8")
        assert "Status: proposed_only" not in stable_skill
        assert "Candidate Skill Patch" not in stable_skill
        assert "Skill.md does not replace artifact contract" in stable_skill
