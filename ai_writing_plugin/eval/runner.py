from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import yaml

from ai_writing_plugin.run_manager import WriteRunError, write_run

from .metrics import VALID_METRICS, MetricResult, evaluate_metrics
from .report import build_eval_report, write_eval_report


ALLOWED_CASE_TYPES = {"positive_regression", "positive_smoke", "negative_metric_guard"}
ALLOWED_MODES = {"run_task", "artifact_fixture"}
ALLOWED_EXPECTED_RESULTS = {"pass", "fail"}
OPTIONAL_REFERENCE_ROOTS = {"superpowers本体架构", "HARA报告生成参考资料集_EPS"}


class EvalCaseError(ValueError):
    """Raised when an eval case is invalid or unsafe."""


@dataclass(frozen=True)
class EvalCase:
    id: str
    schema_version: str
    description: str
    document_type: str
    case_type: str
    mode: str
    expected_result: str
    metrics: list[str]
    expectations: dict[str, Any]
    task_path: Path | None = None
    artifact_root: Path | None = None


@dataclass(frozen=True)
class EvalCaseResult:
    case_id: str
    document_type: str
    case_type: str
    mode: str
    expected_result: str
    actual_result: str
    expectation_met: bool
    artifact_root: str
    metric_results: list[MetricResult]


def load_eval_cases(cases_path: Path, *, repo_root: Path) -> list[EvalCase]:
    if not cases_path.exists():
        raise EvalCaseError(f"Cases path not found: {cases_path}")
    if cases_path.is_file():
        return [load_eval_case(cases_path, repo_root=repo_root)]
    case_files = sorted([*cases_path.glob("*.yaml"), *cases_path.glob("*.yml"), *cases_path.glob("*.json")])
    if not case_files:
        raise EvalCaseError(f"No eval case files found in {cases_path}")
    return [load_eval_case(case_file, repo_root=repo_root) for case_file in case_files]


def load_eval_case(case_path: Path, *, repo_root: Path) -> EvalCase:
    try:
        if case_path.suffix.lower() == ".json":
            loaded = json.loads(case_path.read_text(encoding="utf-8"))
        else:
            loaded = yaml.safe_load(case_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise EvalCaseError(f"Invalid eval case file {case_path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise EvalCaseError(f"Eval case root must be a mapping: {case_path}")

    required = {"id", "schema_version", "description", "document_type", "case_type", "mode", "expected_result", "metrics", "expectations"}
    missing = sorted(required - set(loaded))
    if missing:
        raise EvalCaseError(f"Eval case missing required field(s): {', '.join(missing)}")

    case_id = require_string(loaded, "id")
    schema_version = require_string(loaded, "schema_version")
    description = require_string(loaded, "description")
    document_type = require_string(loaded, "document_type")
    case_type = require_string(loaded, "case_type")
    mode = require_string(loaded, "mode")
    expected_result = require_string(loaded, "expected_result")
    metrics = loaded["metrics"]
    expectations = loaded["expectations"]

    if case_type not in ALLOWED_CASE_TYPES:
        raise EvalCaseError(f"Invalid case_type for {case_id}: {case_type}")
    if mode not in ALLOWED_MODES:
        raise EvalCaseError(f"Invalid mode for {case_id}: {mode}")
    if expected_result not in ALLOWED_EXPECTED_RESULTS:
        raise EvalCaseError(f"Invalid expected_result for {case_id}: {expected_result}")
    if not isinstance(metrics, list) or not metrics or not all(isinstance(metric, str) and metric.strip() for metric in metrics):
        raise EvalCaseError(f"metrics must be a non-empty string list for {case_id}")
    unknown_metrics = sorted(set(metrics) - VALID_METRICS)
    if unknown_metrics:
        raise EvalCaseError(f"Unknown metric id(s) for {case_id}: {', '.join(unknown_metrics)}")
    if not isinstance(expectations, dict):
        raise EvalCaseError(f"expectations must be a mapping for {case_id}")

    task_path = None
    artifact_root = None
    if mode == "run_task":
        if "task_path" not in loaded:
            raise EvalCaseError(f"run_task case missing task_path: {case_id}")
        task_path = validate_repo_relative_path(loaded["task_path"], repo_root=repo_root, field_name="task_path", allow_runs=False)
        if not task_path.exists():
            raise EvalCaseError(f"task_path not found for {case_id}: {loaded['task_path']}")
    if mode == "artifact_fixture":
        if "artifact_root" not in loaded:
            raise EvalCaseError(f"artifact_fixture case missing artifact_root: {case_id}")
        artifact_root = validate_repo_relative_path(loaded["artifact_root"], repo_root=repo_root, field_name="artifact_root", allow_runs=False)
        if not artifact_root.exists():
            raise EvalCaseError(f"artifact_root not found for {case_id}: {loaded['artifact_root']}")

    return EvalCase(
        id=case_id,
        schema_version=schema_version,
        description=description,
        document_type=document_type,
        case_type=case_type,
        mode=mode,
        expected_result=expected_result,
        metrics=list(metrics),
        expectations=dict(expectations),
        task_path=task_path,
        artifact_root=artifact_root,
    )


def run_eval_cases(
    *,
    cases_path: Path,
    output_dir: Path,
    repo_root: Path,
    case_ids: list[str] | None = None,
    expected_result_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    cases = load_eval_cases(cases_path, repo_root=repo_root)
    if case_ids:
        requested = set(case_ids)
        cases = [case for case in cases if case.id in requested]
        missing = requested - {case.id for case in cases}
        if missing:
            raise EvalCaseError(f"Requested eval case(s) not found: {', '.join(sorted(missing))}")
    output_dir.mkdir(parents=True, exist_ok=True)
    case_results = [
        run_one_case(
            case,
            output_dir=output_dir,
            repo_root=repo_root,
            expected_result_override=(expected_result_overrides or {}).get(case.id),
        )
        for case in cases
    ]
    report = build_eval_report(case_results)
    write_eval_report(report, output_dir)
    return report


def run_one_case(
    case: EvalCase,
    *,
    output_dir: Path,
    repo_root: Path,
    expected_result_override: str | None = None,
) -> EvalCaseResult:
    if case.mode == "run_task":
        if not case.task_path:
            raise EvalCaseError(f"run_task case missing resolved task_path: {case.id}")
        case_runs_dir = output_dir / "artifacts" / case.id
        try:
            artifact_root = write_run(task_file=case.task_path, runs_dir=case_runs_dir)
        except WriteRunError as exc:
            raise EvalCaseError(f"write-run failed for eval case {case.id}: {exc}") from exc
    else:
        if not case.artifact_root:
            raise EvalCaseError(f"artifact_fixture case missing resolved artifact_root: {case.id}")
        artifact_root = case.artifact_root

    evaluation = evaluate_metrics(
        artifact_root=artifact_root,
        metric_ids=case.metrics,
        document_type=case.document_type,
        expectations=case.expectations,
    )
    expected_result = expected_result_override or case.expected_result
    if expected_result not in ALLOWED_EXPECTED_RESULTS:
        raise EvalCaseError(f"Invalid expected result override for {case.id}: {expected_result}")
    return EvalCaseResult(
        case_id=case.id,
        document_type=case.document_type,
        case_type=case.case_type,
        mode=case.mode,
        expected_result=expected_result,
        actual_result=evaluation.actual_result,
        expectation_met=evaluation.actual_result == expected_result,
        artifact_root=str(artifact_root),
        metric_results=evaluation.metric_results,
    )


def validate_repo_relative_path(value: object, *, repo_root: Path, field_name: str, allow_runs: bool) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise EvalCaseError(f"{field_name} must be a non-empty string")
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts:
        raise EvalCaseError(f"unsafe path in {field_name}: {value}")
    if raw.parts and raw.parts[0] in OPTIONAL_REFERENCE_ROOTS:
        raise EvalCaseError(f"unsafe path in {field_name}: optional local reference folder is not allowed")
    if raw.parts and raw.parts[0] == "runs" and not allow_runs:
        raise EvalCaseError(f"unsafe path in {field_name}: historical runs path is not allowed")
    resolved = (repo_root / raw).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise EvalCaseError(f"unsafe path in {field_name}: {value}") from exc
    return resolved


def require_string(data: dict[str, Any], field_name: str) -> str:
    value = data[field_name]
    if not isinstance(value, str) or not value.strip():
        raise EvalCaseError(f"{field_name} must be a non-empty string")
    return value.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ai_writing_plugin.eval.runner")
    parser.add_argument("--cases", required=True, help="Eval case file or directory.")
    parser.add_argument("--output", required=True, help="Directory for eval_report.json and eval_summary.md.")
    parser.add_argument("--case", action="append", dest="case_ids", help="Run only the selected case id. May be repeated.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path.cwd()
    try:
        report = run_eval_cases(
            cases_path=Path(args.cases),
            output_dir=Path(args.output),
            repo_root=repo_root,
            case_ids=args.case_ids,
        )
    except EvalCaseError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Eval overall status: {report['overall_status']}")
    print(f"Cases: {report['case_count']}")
    print(f"Expectation mismatches: {report['expectation_mismatch_count']}")
    print(f"Report: {Path(args.output) / 'eval_report.json'}")
    return 0 if report["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
