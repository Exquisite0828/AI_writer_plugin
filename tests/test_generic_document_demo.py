import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.document_types import get_document_type_rules


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "examples" / "generic_document_demo_fixture"
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

USER_FACING_OUTPUTS = [
    "draft/full_draft.md",
    "review/final_review.md",
    "final/final_report.md",
    "final/delivery_summary.md",
    "learning/run_summary.md",
    "learning/candidate_skill_patch.md",
]

FORBIDDEN_DOMAIN_LEAKAGE = [
    "HARA",
    "ASIL",
    "S/E/C",
    "severity rating",
    "exposure rating",
    "controllability rating",
    "hazardous event",
    "safety goal",
    "HARA professional judgment",
    "technical solution approval",
    "test pass rate",
    "release test verdict",
]

SAMPLE_ONLY_CLAIMS = [
    "the migration is approved",
    "the migration is production ready",
    "the cost is final",
    "the compliance review is complete",
    "the rollback plan has no unresolved risk",
]

TEMPLATE_SECTIONS = [
    "Background and Scope",
    "Confirmed Source Facts",
    "Proposed Approach",
    "Risks and Open Questions",
    "Decision and Human Confirmations",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def generic_document_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    runs_dir = tmp_path_factory.mktemp("generic-document-runs")
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


def test_generic_document_fixture_uses_current_task_schema() -> None:
    expected_inputs = {
        "inputs/source.md": "source",
        "inputs/template.md": "template",
        "inputs/checklist.md": "checklist",
        "inputs/reference.md": "reference",
        "inputs/sample.md": "sample",
    }

    task = yaml.safe_load(DEMO_TASK.read_text(encoding="utf-8"))
    assert task["task_type"] == "generic_document"
    assert task["display_name"] == "Migration Decision Memo"
    assert "final decision recommendation" in task["critical_claims"]
    assert "final decision recommendation" in task["requires_human_confirmation"]
    assert set(task) >= {
        "task_type",
        "task_title",
        "display_name",
        "target_audience",
        "critical_claims",
        "requires_human_confirmation",
        "inputs",
    }
    assert {item["path"]: item["role"] for item in task["inputs"]} == expected_inputs
    for relative_path in expected_inputs:
        assert (DEMO_DIR / relative_path).exists(), relative_path


def test_generic_document_rules_registered() -> None:
    rules = get_document_type_rules("generic_document")

    assert rules.task_type == "generic_document"
    assert rules.display_name == "Generic Document"
    assert rules.default_final_status == "ready_for_human_review"
    assert "final decision recommendation" in rules.critical_claims
    assert "approval or acceptance conclusion" in rules.requires_human_confirmation
    assert "must not prove project-specific facts" in rules.reference_policy
    assert "must not supply project-specific facts" in rules.sample_policy


def test_generic_document_full_run_artifact_set_and_display_name(generic_document_run: Path) -> None:
    manifest = read_json(generic_document_run / "manifest.json")
    task_brief = read_json(generic_document_run / "task_brief.json")
    final_report = (generic_document_run / "final" / "final_report.md").read_text(encoding="utf-8")
    run_summary = (generic_document_run / "learning" / "run_summary.md").read_text(encoding="utf-8")

    for relative_path in REQUIRED_ARTIFACTS:
        assert (generic_document_run / relative_path).exists(), relative_path
    assert task_brief["task_type"] == "generic_document"
    assert task_brief["display_name"] == "Migration Decision Memo"
    assert "final decision recommendation" in task_brief["critical_claims"]
    assert manifest["run_id"].endswith("generic_document")
    assert manifest["status"] == "completed_with_candidate_updates_proposed"
    assert "Migration Decision Memo" in final_report
    assert "Migration Decision Memo" in run_summary


def test_generic_document_uses_template_sections(generic_document_run: Path) -> None:
    template_structure = read_json(generic_document_run / "plans" / "template_structure.json")
    section_tasks = read_json(generic_document_run / "plans" / "section_tasks.json")
    writing_plan = (generic_document_run / "plans" / "writing_plan.md").read_text(encoding="utf-8")
    draft = (generic_document_run / "draft" / "full_draft.md").read_text(encoding="utf-8")

    extracted_sections = [section["title"] for section in template_structure["outline_sections"]]
    task_sections = [task["section_title"] for task in section_tasks["tasks"]]
    for section in TEMPLATE_SECTIONS:
        assert section in extracted_sections
        assert section in task_sections
        assert section in writing_plan
        assert section in draft


def test_generic_document_checklist_is_recognized_and_reviewed(generic_document_run: Path) -> None:
    inventory = read_json(generic_document_run / "inputs" / "input_inventory.json")
    checklist_review = (generic_document_run / "review" / "checklist_review.md").read_text(encoding="utf-8")

    checklist_files = [file for file in inventory["files"] if file["path"].endswith("checklist.md")]
    assert checklist_files
    assert all(file["role"] == "checklist" and file["is_fact_source"] is False for file in checklist_files)
    assert "Checklist 材料状态" in checklist_review
    assert "inputs/checklist.md" in checklist_review
    assert "已应用 deterministic checks" in checklist_review
    assert "Migration Decision Memo critical claims" in checklist_review


def test_generic_document_sample_and_reference_are_not_fact_sources(generic_document_run: Path) -> None:
    inventory = read_json(generic_document_run / "inputs" / "input_inventory.json")
    source_index = read_json(generic_document_run / "knowledge" / "source_index.json")
    evidence_map = read_json(generic_document_run / "plans" / "evidence_map.json")
    citation_plan = read_json(generic_document_run / "plans" / "citation_plan.json")
    draft = (generic_document_run / "draft" / "full_draft.md").read_text(encoding="utf-8")
    final_report = (generic_document_run / "final" / "final_report.md").read_text(encoding="utf-8")
    combined_lower = f"{draft}\n{final_report}".lower()

    sample_files = [file for file in inventory["files"] if file["path"].endswith("sample.md")]
    reference_files = [file for file in inventory["files"] if file["path"].endswith("reference.md")]
    assert sample_files
    assert reference_files
    assert all(file["role"] == "sample" and file["is_fact_source"] is False for file in sample_files)
    assert all(file["role"] == "reference" and file["is_fact_source"] is False for file in reference_files)
    assert all(source["source_role"] != "sample" for source in source_index["sources"])
    assert all(
        candidate["source_role"] != "sample"
        for question in evidence_map["questions"]
        for candidate in question["evidence_candidates"]
    )
    assert all(
        not (detail["source_role"] == "reference" and detail["usage"] == "fact_support")
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    )
    for sample_claim in SAMPLE_ONLY_CLAIMS:
        assert sample_claim not in combined_lower


def test_generic_document_critical_claims_require_confirmation(generic_document_run: Path) -> None:
    final_review = (generic_document_run / "review" / "final_review.md").read_text(encoding="utf-8")
    verify_report = read_json(generic_document_run / "verify" / "verify_report.json")
    final_report = (generic_document_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (generic_document_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined = f"{final_review}\n{json.dumps(verify_report, ensure_ascii=False)}\n{final_report}\n{delivery_summary}"
    combined_lower = combined.lower()

    assert "NEEDS_USER_CONFIRMATION" in combined
    for claim in [
        "final decision recommendation",
        "release readiness conclusion",
        "compliance conclusion",
        "cost or schedule commitment",
    ]:
        assert claim in combined_lower
    assert verify_report["document_type"]["task_type"] == "generic_document"
    assert verify_report["document_type"]["display_name"] == "Migration Decision Memo"


def test_generic_document_outputs_do_not_leak_other_domain_terms(generic_document_run: Path) -> None:
    for relative_path in [*PLANNING_OUTPUTS, *USER_FACING_OUTPUTS]:
        text = (generic_document_run / relative_path).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_DOMAIN_LEAKAGE:
            assert forbidden not in text, f"{forbidden!r} leaked into {relative_path}"


def test_generic_document_final_status_and_candidate_updates_stay_conservative(generic_document_run: Path) -> None:
    final_report = (generic_document_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (generic_document_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    revision_plan = read_json(generic_document_run / "revision_plan.json")
    candidate_profile = (generic_document_run / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    promotion_report = (generic_document_run / "learning" / "promotion_report.md").read_text(encoding="utf-8")

    assert final_report.startswith("# Migration Decision Memo 最终交付包")
    assert "Status: ready_for_human_review" in final_report
    assert "## 核心证据边界" in final_report
    assert "ready_for_human_review" in delivery_summary
    assert revision_plan["summary"]["status"] == "ready_for_human_review"
    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "Stable skill overwritten: no" in promotion_report
    assert "Candidate activated: no" in promotion_report
