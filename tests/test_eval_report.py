from pathlib import Path

from ai_writing_plugin.eval.metrics import MetricEvaluation, MetricResult
from ai_writing_plugin.eval.report import build_eval_report, render_markdown_summary, write_eval_report
from ai_writing_plugin.eval.runner import EvalCaseResult


def test_eval_report_contains_required_fields_and_boundary_notices(tmp_path: Path) -> None:
    case_result = EvalCaseResult(
        case_id="negative_sample_misuse",
        document_type="generic_document",
        case_type="negative_metric_guard",
        mode="artifact_fixture",
        expected_result="fail",
        actual_result="fail",
        expectation_met=True,
        artifact_root="tests/evals/fixtures/negative_sample_misuse",
        metric_results=[
            MetricResult(
                metric_id="sample_misuse",
                status="fail",
                severity="P0",
                message="Sample/T4 source used as factual support.",
                checked_artifacts=["plans/claim_support_matrix.json"],
                findings=[{"source_tier": "T4_SAMPLE_STYLE_ONLY"}],
            )
        ],
    )

    report = build_eval_report([case_result])

    assert report["schema_version"] == "eval_report.v1"
    assert report["repository_phase"] == "N6"
    assert report["overall_status"] == "pass"
    assert report["regression_status"] == "pass"
    assert report["case_count"] == 1
    assert report["passed_case_count"] == 1
    assert report["failed_case_count"] == 0
    assert report["expectation_mismatch_count"] == 0
    assert report["metric_summary"]["sample_misuse"]["fail"] == 1
    assert "not professional approval" in report["non_approval_notice"]
    assert "not compliance approval" in report["non_approval_notice"]
    assert "not risk acceptance" in report["non_approval_notice"]
    assert "not production readiness approval" in report["non_approval_notice"]
    assert "correction harvesting" in report["deferred_promotion_notice"]
    assert "profile promotion" in report["deferred_promotion_notice"]
    assert "rollback" in report["deferred_promotion_notice"]

    output_dir = tmp_path / "report"
    write_eval_report(report, output_dir)
    assert (output_dir / "eval_report.json").exists()
    assert (output_dir / "eval_summary.md").exists()
    assert "## Non-approval notice" in (output_dir / "eval_summary.md").read_text(encoding="utf-8")


def test_markdown_summary_lists_metric_failures() -> None:
    evaluation = MetricEvaluation(
        actual_result="fail",
        metric_results=[
            MetricResult(
                metric_id="cross_document_leakage",
                status="fail",
                severity="P0",
                message="Forbidden document-type leakage found.",
                checked_artifacts=["final/final_report.md"],
                findings=[{"term": "ASIL"}],
            )
        ],
    )
    case_result = EvalCaseResult(
        case_id="negative_cross_document_leakage",
        document_type="technical_solution",
        case_type="negative_metric_guard",
        mode="artifact_fixture",
        expected_result="fail",
        actual_result=evaluation.actual_result,
        expectation_met=True,
        artifact_root="tests/evals/fixtures/negative_cross_document_leakage",
        metric_results=evaluation.metric_results,
    )

    summary = render_markdown_summary(build_eval_report([case_result]), generated_report_path=Path("runs/eval-n6/manual/eval_report.json"))

    assert "# Eval Summary" in summary
    assert "negative_cross_document_leakage" in summary
    assert "cross_document_leakage" in summary
    assert "N7 or later" in summary
