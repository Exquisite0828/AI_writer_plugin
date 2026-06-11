from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


NON_APPROVAL_NOTICE = (
    "Eval pass only means deterministic engineering policy checks passed. "
    "It is not professional approval, not compliance approval, not risk acceptance, "
    "and not production readiness approval."
)

DEFERRED_PROMOTION_NOTICE = (
    "Phase N6 does not implement correction harvesting, candidate profile patching, profile promotion, profile version bump, "
    "active profile update, or rollback. They are deferred to N7 or later."
)


def build_eval_report(case_results: list[Any]) -> dict[str, Any]:
    serialized_results = [serialize_case_result(result) for result in case_results]
    expectation_mismatch_count = sum(1 for result in serialized_results if not result["expectation_met"])
    passed_case_count = len(serialized_results) - expectation_mismatch_count
    failed_case_count = expectation_mismatch_count
    metric_summary = build_metric_summary(serialized_results)
    regression_failed = any(
        result["case_type"] == "positive_regression" and not result["expectation_met"]
        for result in serialized_results
    )
    return {
        "schema_version": "eval_report.v1",
        "repository_phase": "N6",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "overall_status": "fail" if expectation_mismatch_count else "pass",
        "regression_status": "fail" if regression_failed else "pass",
        "case_count": len(serialized_results),
        "passed_case_count": passed_case_count,
        "failed_case_count": failed_case_count,
        "expectation_mismatch_count": expectation_mismatch_count,
        "metric_summary": metric_summary,
        "case_results": serialized_results,
        "non_approval_notice": NON_APPROVAL_NOTICE,
        "deferred_promotion_notice": DEFERRED_PROMOTION_NOTICE,
    }


def write_eval_report(report: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "eval_report.json"
    summary_path = output_dir / "eval_summary.md"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(render_markdown_summary(report, generated_report_path=report_path), encoding="utf-8")


def render_markdown_summary(report: dict[str, Any], generated_report_path: Path | None = None) -> str:
    report_path = generated_report_path or Path("eval_report.json")
    lines = [
        "# Eval Summary",
        "",
        f"- Phase: {report['repository_phase']}",
        f"- Overall status: {report['overall_status']}",
        f"- Regression status: {report['regression_status']}",
        f"- Cases: {report['case_count']}",
        f"- Expectation mismatches: {report['expectation_mismatch_count']}",
        f"- Generated report path: {report_path}",
        "",
        "## Non-approval notice",
        "",
        report["non_approval_notice"],
        "",
        "## Case Results",
        "",
    ]
    for result in report["case_results"]:
        lines.append(
            f"- {result['case_id']}: expected={result['expected_result']} actual={result['actual_result']} "
            f"expectation_met={str(result['expectation_met']).lower()}"
        )
    lines.extend(["", "## Metric Failures", ""])
    failures = [
        (result, metric)
        for result in report["case_results"]
        for metric in result["metric_results"]
        if metric["status"] == "fail"
    ]
    if failures:
        for result, metric in failures:
            lines.append(f"- {result['case_id']} / {metric['metric_id']}: {metric['message']}")
    else:
        lines.append("No metric failures were detected.")
    lines.extend(["", "## Deferred Work", "", report["deferred_promotion_notice"], ""])
    return "\n".join(lines)


def build_metric_summary(case_results: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for result in case_results:
        for metric in result["metric_results"]:
            metric_id = metric["metric_id"]
            status = metric["status"]
            summary.setdefault(metric_id, {"pass": 0, "fail": 0})
            summary[metric_id][status] = summary[metric_id].get(status, 0) + 1
    return summary


def serialize_case_result(result: Any) -> dict[str, Any]:
    if is_dataclass(result):
        data = asdict(result)
    elif isinstance(result, dict):
        data = dict(result)
    else:
        raise TypeError(f"Unsupported case result type: {type(result)!r}")
    data["metric_results"] = [serialize_metric(metric) for metric in data["metric_results"]]
    return data


def serialize_metric(metric: Any) -> dict[str, Any]:
    if is_dataclass(metric):
        return asdict(metric)
    if isinstance(metric, dict):
        return dict(metric)
    raise TypeError(f"Unsupported metric result type: {type(metric)!r}")
