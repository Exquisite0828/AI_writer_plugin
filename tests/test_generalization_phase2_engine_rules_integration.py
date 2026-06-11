import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.document_types import HARA_RULES


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_TASK = REPO_ROOT / "examples" / "hara_demo_fixture" / "task.yaml"

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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def demo_run(tmp_path_factory: pytest.TempPathFactory) -> Path:
    runs_dir = tmp_path_factory.mktemp("phase2-runs")
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


def test_phase2_rules_context_helper_resolves_task_brief_and_run(demo_run: Path) -> None:
    from ai_writing_plugin.document_types.context import get_rules_for_run, get_rules_for_task_brief, get_rules_for_task_type

    assert get_rules_for_task_type("hara") is HARA_RULES
    assert get_rules_for_task_brief(read_json(demo_run / "task_brief.json")) is HARA_RULES
    assert get_rules_for_run(demo_run) is HARA_RULES


def test_phase2_final_report_uses_document_type_rules(demo_run: Path) -> None:
    final_report = (demo_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (demo_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    revision_plan = read_json(demo_run / "revision_plan.json")
    combined = f"{final_report}\n{delivery_summary}"

    assert HARA_RULES.display_name in combined
    assert f"Status: {HARA_RULES.default_final_status}" in final_report
    assert revision_plan["summary"]["status"] == HARA_RULES.default_final_status
    assert revision_plan["summary"]["status"] in HARA_RULES.allowed_final_statuses
    assert "不是合格人工批准记录" in final_report
    assert "formal compliance approval" not in combined.lower()
    assert "official compliance approval" not in combined.lower()
    assert "open" in combined.lower() or "unresolved" in combined.lower() or "pending" in combined.lower()


def test_phase2_confirmation_marker_and_critical_claim_policy_are_rules_driven(demo_run: Path) -> None:
    marker = HARA_RULES.confirmation_marker
    draft = (demo_run / "draft" / "full_draft.md").read_text(encoding="utf-8")
    final_review = (demo_run / "review" / "final_review.md").read_text(encoding="utf-8")
    verify_report = read_json(demo_run / "verify" / "verify_report.json")
    final_report = (demo_run / "final" / "final_report.md").read_text(encoding="utf-8")
    combined = f"{final_review}\n{json.dumps(verify_report, ensure_ascii=False)}\n{final_report}"

    assert marker in draft
    assert marker in final_review
    assert marker in json.dumps(verify_report, ensure_ascii=False)
    for claim in HARA_RULES.critical_claims:
        assert claim in combined
    assert HARA_RULES.requires_human_confirmation == HARA_RULES.critical_claims
    assert "approved conclusion" not in combined.lower()


def test_phase2_forbidden_final_claims_and_final_status_are_rules_driven(demo_run: Path) -> None:
    verify_report = read_json(demo_run / "verify" / "verify_report.json")
    revision_plan = read_json(demo_run / "revision_plan.json")
    final_report = (demo_run / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (demo_run / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined_lower = f"{final_report}\n{delivery_summary}".lower()

    assert verify_report["document_type"]["task_type"] == HARA_RULES.task_type
    assert set(verify_report["document_type"]["forbidden_final_claims"]) == set(HARA_RULES.forbidden_final_claims)
    assert revision_plan["summary"]["status"] in HARA_RULES.allowed_final_statuses
    critical_claims = {claim.lower() for claim in HARA_RULES.critical_claims}
    for forbidden_claim in HARA_RULES.forbidden_final_claims:
        if forbidden_claim.lower() in critical_claims:
            continue
        assert forbidden_claim.lower() not in combined_lower


def test_phase2_source_policy_boundaries_preserved(demo_run: Path) -> None:
    inventory = read_json(demo_run / "inputs" / "input_inventory.json")
    source_index = read_json(demo_run / "knowledge" / "source_index.json")
    evidence_map = read_json(demo_run / "plans" / "evidence_map.json")
    citation_plan = read_json(demo_run / "plans" / "citation_plan.json")

    non_fact_roles = set(HARA_RULES.non_fact_source_roles)
    assert non_fact_roles >= {"sample", "reference", "expected_output_shape"}
    assert all(file["is_fact_source"] is False for file in inventory["files"] if file["role"] in non_fact_roles)
    assert all(source["source_role"] != "sample" for source in source_index["sources"])
    assert all(
        candidate["source_role"] != "sample"
        for question in evidence_map["questions"]
        for candidate in question["evidence_candidates"]
    )
    assert all(
        detail["source_role"] != "sample" and not (detail["source_role"] == "reference" and detail["usage"] == "fact_support")
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    )


def test_phase2_candidate_update_policy_preserved(demo_run: Path) -> None:
    candidate_profile = (demo_run / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    candidate_patch = (demo_run / "learning" / "candidate_skill_patch.md").read_text(encoding="utf-8")
    promotion_report = (demo_run / "learning" / "promotion_report.md").read_text(encoding="utf-8")

    assert HARA_RULES.candidate_learning_policy in candidate_profile
    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "rollback_supported: true" in candidate_profile
    assert candidate_patch
    assert "Stable skill overwritten: no" in promotion_report
    assert "Candidate activated: no" in promotion_report


def test_phase2_artifact_contract_is_preserved(demo_run: Path) -> None:
    for relative_path in REQUIRED_ARTIFACTS:
        assert (demo_run / relative_path).exists(), relative_path
