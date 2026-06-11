import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
L3_DEMOS = [
    ("hara", REPO_ROOT / "examples" / "hara_demo_fixture" / "task.yaml"),
    ("technical_solution", REPO_ROOT / "examples" / "technical_solution_demo_fixture" / "task.yaml"),
    ("test_report", REPO_ROOT / "examples" / "test_report_demo_fixture" / "task.yaml"),
]
CUSTOM_PROFILE_TASK = REPO_ROOT / "examples" / "custom_technical_note_profile_demo_fixture" / "task.yaml"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import write_run

    return write_run(task_file=task_path, runs_dir=runs_dir)


@pytest.mark.parametrize(
    ("role", "expected_tier"),
    [
        ("source", "T1_PROJECT_SOURCE"),
        ("template", "T2_TEMPLATE_CHECKLIST"),
        ("checklist", "T2_TEMPLATE_CHECKLIST"),
        ("reference", "T3_REFERENCE_METHODOLOGY"),
        ("sample", "T4_SAMPLE_STYLE_ONLY"),
        ("expected_output_shape", "T4_SAMPLE_STYLE_ONLY"),
        ("generated", "T5_AI_INFERENCE"),
        ("unknown", "T5_AI_INFERENCE"),
    ],
)
def test_source_tier_mapping_is_deterministic(role: str, expected_tier: str) -> None:
    from ai_writing_plugin.provenance import source_tier_for_role

    assert source_tier_for_role(role) == expected_tier
    if role in {"generated", "unknown"}:
        assert source_tier_for_role(role) != "T1_PROJECT_SOURCE"


def test_source_tier_capabilities_restrict_non_fact_sources() -> None:
    from ai_writing_plugin.provenance import support_capabilities_for_tier

    t0 = support_capabilities_for_tier("T0_HITL")
    t1 = support_capabilities_for_tier("T1_PROJECT_SOURCE")
    t2 = support_capabilities_for_tier("T2_TEMPLATE_CHECKLIST")
    t3 = support_capabilities_for_tier("T3_REFERENCE_METHODOLOGY")
    t4 = support_capabilities_for_tier("T4_SAMPLE_STYLE_ONLY")
    t5 = support_capabilities_for_tier("T5_AI_INFERENCE")

    assert t0["can_support_critical_claim"] is True
    assert t1["can_support_project_fact"] is True
    assert t2["can_support_project_fact"] is False
    assert t3["can_support_project_fact"] is False
    assert t4["can_support_project_fact"] is False
    assert t4["can_support_critical_claim"] is False
    assert t5["can_support_project_fact"] is False
    assert t5["can_support_critical_claim"] is False


def test_claim_status_respects_hitl_and_source_tier_policy() -> None:
    from ai_writing_plugin.provenance import claim_status_for_support

    t1_support = [{"source_tier": "T1_PROJECT_SOURCE", "support_type": "project_fact"}]
    t3_support = [{"source_tier": "T3_REFERENCE_METHODOLOGY", "support_type": "methodology"}]
    t4_support = [{"source_tier": "T4_SAMPLE_STYLE_ONLY", "support_type": "style_only"}]
    t0_support = [{"source_tier": "T0_HITL", "support_type": "hitl_confirmation"}]

    assert claim_status_for_support("architecture decision", t1_support, False)["claim_status"] == "supported"

    required = claim_status_for_support("architecture decision", t1_support, True)
    assert required["claim_status"] == "needs_confirmation"
    assert required["human_confirmation_status"] == "pending"

    hitl = claim_status_for_support("architecture decision", t0_support, True)
    assert hitl["claim_status"] == "hitl_confirmed"
    assert hitl["human_confirmation_status"] == "confirmed"

    assert claim_status_for_support("architecture decision", t3_support, False)["claim_status"] != "supported"
    assert claim_status_for_support("architecture decision", t4_support, False)["claim_status"] == "unsupported"
    assert claim_status_for_support("architecture decision", [], False)["claim_status"] == "unsupported"


@pytest.mark.parametrize(("task_type", "task_path"), L3_DEMOS)
def test_l3_demo_runs_create_provenance_artifacts(tmp_path: Path, task_type: str, task_path: Path) -> None:
    from ai_writing_plugin.document_types.context import get_rules_for_task_type

    run_dir = write_run(task_path, tmp_path / f"{task_type}-runs")
    rules = get_rules_for_task_type(task_type)

    provenance_index = read_json(run_dir / "knowledge" / "provenance_index.json")
    claim_matrix = read_json(run_dir / "plans" / "claim_support_matrix.json")
    source_index = read_json(run_dir / "knowledge" / "source_index.json")
    evidence_map = read_json(run_dir / "plans" / "evidence_map.json")
    citation_plan = read_json(run_dir / "plans" / "citation_plan.json")
    section_tasks = read_json(run_dir / "plans" / "section_tasks.json")
    verify_report = read_json(run_dir / "verify" / "verify_report.json")
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")

    assert provenance_index["schema_version"] == "n4.provenance_index.v1"
    assert claim_matrix["schema_version"] == "n4.claim_support_matrix.v1"
    assert provenance_index["source_tier_policy"]["T1_PROJECT_SOURCE"]
    assert {artifact["path"] for artifact in read_json(run_dir / "manifest.json")["artifacts"]} >= {
        "knowledge/provenance_index.json",
        "plans/claim_support_matrix.json",
    }

    by_role = {}
    for source in provenance_index["sources"]:
        by_role.setdefault(source["role"], set()).add(source["source_tier"])
        assert source["source_id"]
        assert "can_support_project_fact" in source
        assert "can_support_critical_claim" in source
    assert by_role["source"] == {"T1_PROJECT_SOURCE"}
    assert by_role["reference"] == {"T3_REFERENCE_METHODOLOGY"}
    assert by_role["sample"] == {"T4_SAMPLE_STYLE_ONLY"}

    assert all(source["source_tier"] in {"T1_PROJECT_SOURCE", "T3_REFERENCE_METHODOLOGY"} for source in source_index["sources"])

    candidates = [
        candidate
        for question in evidence_map["questions"]
        for candidate in question["evidence_candidates"]
    ]
    assert candidates
    assert all("source_tier" in candidate for candidate in candidates)
    assert all("evidence_status" in candidate for candidate in candidates)
    assert all("can_support_project_fact" in candidate for candidate in candidates)

    details = [
        detail
        for section in citation_plan["sections"]
        for detail in section["evidence_details"]
    ]
    assert details
    assert all("source_tier" in detail for detail in details)
    assert all("provenance_support_type" in detail for detail in details)
    assert not any(
        detail["source_tier"] in {"T3_REFERENCE_METHODOLOGY", "T4_SAMPLE_STYLE_ONLY"}
        and detail["provenance_support_type"] == "project_fact"
        for detail in details
    )

    assert all("source_support" in task for task in section_tasks["tasks"])
    assert all("sample" in task["forbidden_sources"] for task in section_tasks["tasks"])

    matrix_claims = {claim["claim_category"]: claim for claim in claim_matrix["claims"]}
    for claim in rules.critical_claims:
        assert claim in matrix_claims
    for claim in claim_matrix["claims"]:
        assert claim["claim_status"] in {"hitl_confirmed", "supported", "needs_confirmation", "weak", "unsupported", "not_applicable"}
        assert claim["human_confirmation_status"] in {"confirmed", "pending", "not_required", "not_applicable"}
        if claim["required_human_confirmation"] and not any(
            support["source_tier"] == "T0_HITL" for support in claim["source_support"]
        ):
            assert claim["claim_status"] == "needs_confirmation"
            assert claim["human_confirmation_status"] == "pending"
        if claim["claim_status"] == "supported":
            assert any(support["source_tier"] == "T1_PROJECT_SOURCE" for support in claim["source_support"])
            assert all(support["source_tier"] not in {"T4_SAMPLE_STYLE_ONLY", "T5_AI_INFERENCE"} for support in claim["source_support"])

    check_names = {check["name"] for check in verify_report["checks"]}
    assert {
        "provenance_index_exists",
        "source_tier_policy_valid",
        "sample_tier_is_style_only",
        "reference_tier_is_methodology_only",
        "critical_claim_source_tier_sufficient",
        "required_human_confirmation_not_hidden",
        "final_report_has_provenance_summary",
        "final_delivery_has_open_confirmations",
    } <= check_names

    assert "## 溯源摘要" in final_report
    assert "## 溯源摘要" in delivery_summary
    if any(claim["human_confirmation_status"] == "pending" for claim in claim_matrix["claims"]):
        assert "## 开放确认项" in delivery_summary
    combined = f"{final_report}\n{delivery_summary}"
    assert "声明状态：" in combined
    assert "证据状态：" in combined
    assert "来源层级：" in combined
    assert "人工确认状态：" in combined
    assert "sample 材料仅作为风格/结构参考" in combined
    assert "reference 材料仅作为方法/背景参考" in combined


def test_external_profile_provenance_records_profile_metadata(tmp_path: Path) -> None:
    run_dir = write_run(CUSTOM_PROFILE_TASK, tmp_path / "custom-runs")

    provenance_index = read_json(run_dir / "knowledge" / "provenance_index.json")
    claim_matrix = read_json(run_dir / "plans" / "claim_support_matrix.json")

    assert provenance_index["profile_id"] == "customer_demo.custom_technical_note"
    assert provenance_index["profile_version"] == "0.1.0"
    assert provenance_index["profile_source"] == "external"
    assert claim_matrix["profile_id"] == "customer_demo.custom_technical_note"
    assert claim_matrix["profile_version"] == "0.1.0"
    assert "customer_demo.custom_technical_note@0.1.0" in (
        run_dir / "final" / "final_report.md"
    ).read_text(encoding="utf-8")


def test_verify_facts_reject_critical_claim_supported_by_sample_only() -> None:
    from ai_writing_plugin.provenance import build_provenance_verify_facts
    from ai_writing_plugin.verify import build_verify_report

    matrix = {
        "schema_version": "n4.claim_support_matrix.v1",
        "claims": [
            {
                "claim_category": "architecture decision",
                "required_human_confirmation": False,
                "claim_status": "supported",
                "evidence_status": "sample_style_only",
                "human_confirmation_status": "not_required",
                "source_support": [
                    {
                        "source_id": "FILE-999",
                        "source_tier": "T4_SAMPLE_STYLE_ONLY",
                        "evidence_id": "EVD-999",
                        "support_type": "project_fact",
                        "support_strength": "strong",
                    }
                ],
                "blocking_reason": "",
                "notes": [],
            }
        ],
    }
    provenance_index = {
        "schema_version": "n4.provenance_index.v1",
        "source_tier_policy": {"T4_SAMPLE_STYLE_ONLY": "Sample style only"},
        "sources": [
            {
                "source_id": "FILE-999",
                "role": "sample",
                "source_tier": "T4_SAMPLE_STYLE_ONLY",
                "can_support_project_fact": False,
                "can_support_critical_claim": False,
            }
        ],
        "profile_id": None,
        "profile_version": None,
    }

    facts, _review_items = build_provenance_verify_facts(
        provenance_index=provenance_index,
        claim_support_matrix=matrix,
        final_report_text="## 溯源摘要\n",
        delivery_summary_text="## 溯源摘要\n## 开放确认项\n",
        external_profile_expected=False,
    )
    verify_report = build_verify_report(
        run_id="RUN-N4",
        generated_at="2026-06-07T00:00:00Z",
        facts=facts,
        review_items=[],
        final_readiness="blocked",
    )

    critical_check = next(check for check in verify_report["checks"] if check["name"] == "critical_claim_source_tier_sufficient")
    assert critical_check["status"] == "failed"
    assert verify_report["status"] == "failed"
