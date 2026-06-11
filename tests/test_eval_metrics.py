from pathlib import Path

from ai_writing_plugin.eval.metrics import evaluate_metrics


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "evals" / "fixtures"


def test_metrics_pass_on_minimal_policy_compliant_fixture() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "positive_policy_compliant",
        metric_ids=[
            "material_classification",
            "source_tier_policy",
            "template_extraction",
            "evidence_mapping",
            "sample_misuse",
            "reference_misuse",
            "critical_claim_policy",
            "forbidden_final_claim",
            "final_status_policy",
            "candidate_update_inactive",
            "cross_document_leakage",
        ],
        document_type="technical_solution",
        expectations={"forbidden_terms": ["ASIL", "S/E/C", "safety goal", "hazardous event"]},
    )

    assert result.actual_result == "pass"
    assert all(metric.status == "pass" for metric in result.metric_results)


def test_sample_misuse_metric_detects_sample_as_fact_support() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "negative_sample_misuse",
        metric_ids=["sample_misuse", "source_tier_policy"],
        document_type="generic_document",
        expectations={"expected_failures": ["sample_misuse"]},
    )

    assert result.actual_result == "fail"
    assert metric_status(result, "sample_misuse") == "fail"
    assert any("T4_SAMPLE_STYLE_ONLY" in finding.get("source_tier", "") for finding in metric_findings(result, "sample_misuse"))


def test_reference_misuse_metric_detects_reference_as_project_fact() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "negative_reference_misuse",
        metric_ids=["reference_misuse", "source_tier_policy"],
        document_type="generic_document",
        expectations={"expected_failures": ["reference_misuse"]},
    )

    assert result.actual_result == "fail"
    assert metric_status(result, "reference_misuse") == "fail"


def test_critical_claim_metric_detects_unsupported_finalized_claim() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "negative_unsupported_critical_claim",
        metric_ids=["critical_claim_policy", "source_tier_policy"],
        document_type="technical_solution",
        expectations={"expected_failures": ["critical_claim_policy"]},
    )

    assert result.actual_result == "fail"
    assert metric_status(result, "critical_claim_policy") == "fail"


def test_forbidden_final_claim_metric_allows_guardrail_but_rejects_approval() -> None:
    guardrail = evaluate_metrics(
        artifact_root=FIXTURES / "positive_policy_compliant",
        metric_ids=["forbidden_final_claim"],
        document_type="technical_solution",
        expectations={},
    )
    negative = evaluate_metrics(
        artifact_root=FIXTURES / "negative_forbidden_final_claim",
        metric_ids=["forbidden_final_claim"],
        document_type="technical_solution",
        expectations={"expected_failures": ["forbidden_final_claim"]},
    )

    assert metric_status(guardrail, "forbidden_final_claim") == "pass"
    assert metric_status(negative, "forbidden_final_claim") == "fail"


def test_final_status_metric_rejects_approval_like_status() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "negative_final_status_approval",
        metric_ids=["final_status_policy"],
        document_type="generic_document",
        expectations={"expected_failures": ["final_status_policy"]},
    )

    assert result.actual_result == "fail"
    assert metric_status(result, "final_status_policy") == "fail"


def test_candidate_update_metric_rejects_active_candidate() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "negative_candidate_update_active",
        metric_ids=["candidate_update_inactive"],
        document_type="generic_document",
        expectations={"expected_failures": ["candidate_update_inactive"]},
    )

    assert result.actual_result == "fail"
    assert metric_status(result, "candidate_update_inactive") == "fail"


def test_cross_document_leakage_metric_detects_hara_terms_in_non_hara_doc() -> None:
    result = evaluate_metrics(
        artifact_root=FIXTURES / "negative_cross_document_leakage",
        metric_ids=["cross_document_leakage"],
        document_type="technical_solution",
        expectations={"forbidden_terms": ["ASIL", "severity rating", "safety goal"]},
    )

    assert result.actual_result == "fail"
    assert metric_status(result, "cross_document_leakage") == "fail"


def metric_status(result, metric_id: str) -> str:
    return next(metric.status for metric in result.metric_results if metric.metric_id == metric_id)


def metric_findings(result, metric_id: str) -> list[dict]:
    return next(metric.findings for metric in result.metric_results if metric.metric_id == metric_id)
