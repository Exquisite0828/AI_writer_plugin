import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.document_types import get_document_type_rules


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = REPO_ROOT / "examples" / "technical_solution_zh_demo_fixture"
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
    "review/final_review.md",
    "final/final_report.md",
    "final/delivery_summary.md",
    "learning/run_summary.md",
    "learning/candidate_skill_patch.md",
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
    "Hazard identification",
    "Hazardous event analysis",
]

SAMPLE_ONLY_CLAIMS = [
    "架构已批准",
    "上线无风险",
    "系统不存在安全风险",
    "最终成本已经锁定",
    "性能目标已经保证",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def technical_solution_zh_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    runs_dir = tmp_path_factory.mktemp("technical-solution-zh-runs")
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


def test_technical_solution_zh_fixture_uses_current_task_schema() -> None:
    expected_inputs = {
        "inputs/system_context.md": "source",
        "inputs/requirements.md": "source",
        "inputs/solution_template.md": "template",
        "inputs/checklist.md": "checklist",
        "inputs/architecture_reference.md": "reference",
        "inputs/sample_solution.md": "sample",
    }

    task = yaml.safe_load(DEMO_TASK.read_text(encoding="utf-8"))
    assert task["task_type"] == "technical_solution"
    assert "中文" in task["task_title"]
    assert "performance target" in task["requires_human_confirmation"]
    assert "security boundary" in task["requires_human_confirmation"]
    assert {item["path"]: item["role"] for item in task["inputs"]} == expected_inputs
    for relative_path in expected_inputs:
        assert (DEMO_DIR / relative_path).exists(), relative_path


def test_technical_solution_zh_run_artifact_set_and_task_type(technical_solution_zh_run: Path) -> None:
    rules = get_document_type_rules("technical_solution")
    manifest = read_json(technical_solution_zh_run / "manifest.json")
    task_brief = read_json(technical_solution_zh_run / "task_brief.json")

    for relative_path in REQUIRED_ARTIFACTS:
        assert (technical_solution_zh_run / relative_path).exists(), relative_path
    assert task_brief["task_type"] == rules.task_type
    assert manifest["run_id"].endswith(rules.task_type)
    assert manifest["status"] == "completed_with_candidate_updates_proposed"


def test_technical_solution_zh_outputs_do_not_leak_hara_terms(technical_solution_zh_run: Path) -> None:
    for relative_path in USER_FACING_OUTPUTS:
        text = (technical_solution_zh_run / relative_path).read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_HARA_LEAKAGE:
            assert forbidden not in text, f"{forbidden!r} leaked into {relative_path}"


def test_technical_solution_zh_sample_and_reference_are_not_fact_sources(technical_solution_zh_run: Path) -> None:
    inventory = read_json(technical_solution_zh_run / "inputs" / "input_inventory.json")
    source_index = read_json(technical_solution_zh_run / "knowledge" / "source_index.json")
    evidence_map = read_json(technical_solution_zh_run / "plans" / "evidence_map.json")
    citation_plan = read_json(technical_solution_zh_run / "plans" / "citation_plan.json")
    final_report = (technical_solution_zh_run / "final" / "final_report.md").read_text(encoding="utf-8")
    draft = (technical_solution_zh_run / "draft" / "full_draft.md").read_text(encoding="utf-8")
    combined = f"{draft}\n{final_report}"

    sample_files = [file for file in inventory["files"] if file["path"].endswith("sample_solution.md")]
    reference_files = [file for file in inventory["files"] if file["path"].endswith("architecture_reference.md")]
    assert sample_files
    assert reference_files
    assert all(file["role"] == "sample" and file["is_fact_source"] is False for file in sample_files)
    assert all(file["role"] == "reference" and file["is_fact_source"] is False for file in reference_files)
    assert all(source["source_role"] != "sample" for source in source_index["sources"])
    assert any(
        source["path"].endswith("architecture_reference.md")
        and source["source_role"] == "reference"
        and source["is_fact_source"] is False
        for source in source_index["sources"]
    )
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
        assert sample_claim not in combined


def test_technical_solution_zh_critical_claims_and_candidate_updates_stay_conservative(
    technical_solution_zh_run: Path,
) -> None:
    rules = get_document_type_rules("technical_solution")
    verify_report = read_json(technical_solution_zh_run / "verify" / "verify_report.json")
    revision_plan = read_json(technical_solution_zh_run / "revision_plan.json")
    final_report = (technical_solution_zh_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (technical_solution_zh_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    candidate_profile = (technical_solution_zh_run / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    promotion_report = (technical_solution_zh_run / "learning" / "promotion_report.md").read_text(encoding="utf-8")
    combined = f"{json.dumps(verify_report, ensure_ascii=False)}\n{final_report}\n{delivery_summary}".lower()

    assert rules.confirmation_marker.lower() in combined
    for claim in rules.requires_human_confirmation:
        assert claim in combined
    for forbidden in rules.forbidden_final_claims:
        assert forbidden not in f"{final_report}\n{delivery_summary}".lower()
    assert verify_report["document_type"]["task_type"] == rules.task_type
    assert revision_plan["summary"]["status"] in rules.allowed_final_statuses
    assert f"Status: {rules.default_final_status}" in final_report
    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "Stable skill overwritten: no" in promotion_report
