from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.document_types import get_document_type_rules


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "examples" / "fsr_demo_fixture"
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

SAMPLE_ONLY_CLAIMS = [
    "FSR-SAMPLE-999",
    "ASIL D is confirmed by sample",
    "all requirements are approved",
    "no open safety requirement remains",
]

FORBIDDEN_TSC_LEAKAGE = [
    "Technical Safety Concept final report",
    "Technical Safety Requirement table",
    "TSC approval statement",
    "technical safety mechanism completeness",
]

FORBIDDEN_FINAL_CLAIMS = [
    "FSR set is approved",
    "functional safety requirements are approved",
    "requirements are complete and compliant",
    "safety goals are fully satisfied",
    "ASIL inheritance is validated",
    "verification method is sufficient",
    "no open safety issue remains",
    "ready for production release",
    "risk is accepted",
    "compliance is confirmed",
]

GUARDRAIL_MARKERS = (
    "not approved",
    "not compliant",
    "not a professional approval",
    "forbidden",
    "must not",
    "cannot",
    "requires approval",
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fsr_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    runs_dir = tmp_path_factory.mktemp("fsr-runs")
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


def test_fsr_fixture_uses_current_task_schema_and_boundaries() -> None:
    expected_inputs = {
        "inputs/item_definition_source.md": "source",
        "inputs/safety_goals_source.md": "source",
        "inputs/hara_summary_source.md": "source",
        "inputs/fsr_template.md": "template",
        "inputs/fsr_checklist.md": "checklist",
        "inputs/fsr_reference.md": "reference",
        "inputs/fsr_sample.md": "sample",
    }

    task = yaml.safe_load(DEMO_TASK.read_text(encoding="utf-8"))
    assert task["task_type"] == "fsr"
    assert set(task) >= {"task_type", "task_title", "target_audience", "inputs"}
    assert task["display_name"] == "FSR 功能安全需求文档"
    assert task["strict_template"] is True
    assert task["allow_inference"] is False
    assert "requirement completeness and sufficiency conclusion" in task["requires_human_confirmation"]
    assert "final FSR approval or compliance conclusion" in task["requires_human_confirmation"]
    assert {item["path"]: item["role"] for item in task["inputs"]} == expected_inputs
    for relative_path in expected_inputs:
        assert (DEMO_DIR / relative_path).exists(), relative_path


def test_fsr_full_run_artifact_set_and_task_type(fsr_run: Path) -> None:
    rules = get_document_type_rules("fsr")
    manifest = read_json(fsr_run / "manifest.json")
    task_brief = read_json(fsr_run / "task_brief.json")

    for relative_path in REQUIRED_ARTIFACTS:
        assert (fsr_run / relative_path).exists(), relative_path
    assert task_brief["task_type"] == rules.task_type
    assert task_brief["display_name"] == rules.display_name
    assert manifest["run_id"].endswith(rules.task_type)
    assert manifest["status"] == "completed_with_candidate_updates_proposed"


def test_fsr_source_sample_reference_boundary(fsr_run: Path) -> None:
    inventory = read_json(fsr_run / "inputs" / "input_inventory.json")
    source_index = read_json(fsr_run / "knowledge" / "source_index.json")
    evidence_map = read_json(fsr_run / "plans" / "evidence_map.json")
    citation_plan = read_json(fsr_run / "plans" / "citation_plan.json")
    combined_lower = "\n".join((fsr_run / path).read_text(encoding="utf-8") for path in USER_FACING_OUTPUTS).lower()

    fact_source_paths = {
        "inputs/item_definition_source.md",
        "inputs/safety_goals_source.md",
        "inputs/hara_summary_source.md",
    }
    files_by_path = {file["path"]: file for file in inventory["files"]}
    for path in fact_source_paths:
        assert files_by_path[path]["role"] == "source"
        assert files_by_path[path]["is_fact_source"] is True

    assert files_by_path["inputs/fsr_sample.md"]["role"] == "sample"
    assert files_by_path["inputs/fsr_sample.md"]["is_fact_source"] is False
    assert files_by_path["inputs/fsr_reference.md"]["role"] == "reference"
    assert files_by_path["inputs/fsr_reference.md"]["is_fact_source"] is False
    assert files_by_path["inputs/fsr_template.md"]["is_fact_source"] is False
    assert files_by_path["inputs/fsr_checklist.md"]["is_fact_source"] is False
    assert all(source["source_role"] != "sample" for source in source_index["sources"])
    assert all(
        not (candidate["source_role"] == "sample" and candidate["provenance_support_type"] == "project_fact")
        for question in evidence_map["questions"]
        for candidate in question["evidence_candidates"]
    )
    assert all(
        not (detail["source_role"] in {"sample", "reference"} and detail["usage"] == "fact_support")
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    )
    for sample_claim in SAMPLE_ONLY_CLAIMS:
        assert sample_claim.lower() not in combined_lower


def test_fsr_critical_claims_stay_evidence_aware_and_pending_when_needed(fsr_run: Path) -> None:
    rules = get_document_type_rules("fsr")
    matrix = read_json(fsr_run / "plans" / "claim_support_matrix.json")
    revision_plan = read_json(fsr_run / "revision_plan.json")
    final_report = (fsr_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (fsr_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined = f"{json.dumps(matrix, ensure_ascii=False)}\n{json.dumps(revision_plan, ensure_ascii=False)}\n{final_report}\n{delivery_summary}".lower()

    for claim in [
        "functional safety requirement",
        "safety goal linkage",
        "asil inheritance",
        "verification method",
        "requirement completeness",
    ]:
        assert claim in combined
    assert rules.confirmation_marker in final_report
    assert "开放确认项" in delivery_summary
    assert any(task["requires_user_confirmation"] for task in revision_plan["tasks"])
    assert revision_plan["summary"]["pending_user_confirmation_tasks"] > 0
    assert f"Status: {rules.default_final_status}" in final_report


def test_fsr_final_report_has_no_unguarded_professional_approval_or_tsc_leakage(fsr_run: Path) -> None:
    for relative_path in USER_FACING_OUTPUTS:
        text = (fsr_run / relative_path).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_TSC_LEAKAGE:
            assert forbidden not in text, f"{forbidden!r} leaked into {relative_path}"

    deliverables = "\n".join(
        (fsr_run / relative_path).read_text(encoding="utf-8")
        for relative_path in ["final/final_report.md", "final/delivery_summary.md", "revised/full_draft.md", "review/final_review.md"]
    )
    for line in deliverables.splitlines():
        lowered = line.lower()
        if any(marker in lowered for marker in GUARDRAIL_MARKERS):
            continue
        for forbidden in FORBIDDEN_FINAL_CLAIMS:
            assert forbidden.lower() not in lowered, f"{forbidden!r} found in line: {line}"


def test_fsr_candidate_updates_stay_proposed_inactive(fsr_run: Path) -> None:
    candidate_profile = (fsr_run / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    candidate_patch = (fsr_run / "learning" / "candidate_skill_patch.md").read_text(encoding="utf-8")
    promotion_report = (fsr_run / "learning" / "promotion_report.md").read_text(encoding="utf-8")

    assert "document_type: fsr" in candidate_profile
    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "rollback_supported: true" in candidate_profile
    assert "Status: proposed_only" in candidate_patch
    assert "skills/document-types/fsr/SKILL.md" in candidate_patch
    assert "This patch has not been applied." in candidate_patch
    assert "Stable skill overwritten: no" in promotion_report
    assert "Candidate activated: no" in promotion_report
