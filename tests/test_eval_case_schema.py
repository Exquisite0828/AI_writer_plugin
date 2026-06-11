from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.eval.runner import EvalCaseError, load_eval_case, load_eval_cases


REPO_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = REPO_ROOT / "tests" / "evals" / "cases"


def test_committed_eval_cases_load_and_cover_required_ids() -> None:
    cases = load_eval_cases(CASES_DIR, repo_root=REPO_ROOT)

    assert {case.id for case in cases} == {
        "hara_l3_regression",
        "technical_solution_l3_regression",
        "test_report_l3_regression",
        "fsr_l3_regression",
        "generic_document_smoke",
        "custom_profile_smoke",
        "negative_sample_misuse",
        "negative_reference_misuse",
        "negative_unsupported_critical_claim",
        "negative_forbidden_final_claim",
        "negative_final_status_approval",
        "negative_candidate_update_active",
        "negative_cross_document_leakage",
        "fsr_negative_sample_misuse",
        "fsr_negative_reference_misuse",
        "fsr_negative_unsupported_critical_claim",
        "fsr_negative_forbidden_final_claim",
        "fsr_negative_final_status_approval",
        "fsr_negative_candidate_update_active",
        "fsr_negative_tsc_leakage",
    }
    assert {case.mode for case in cases} == {"run_task", "artifact_fixture"}
    assert all(case.expected_result in {"pass", "fail"} for case in cases)
    assert all(case.metrics for case in cases)


def test_negative_metric_guard_cases_expect_fail() -> None:
    cases = load_eval_cases(CASES_DIR, repo_root=REPO_ROOT)

    for case in cases:
        if case.case_type == "negative_metric_guard":
            assert case.expected_result == "fail"


def test_eval_case_rejects_missing_required_field(tmp_path: Path) -> None:
    case_path = write_case(tmp_path, {"id": "missing_schema_version"})

    with pytest.raises(EvalCaseError, match="schema_version"):
        load_eval_case(case_path, repo_root=REPO_ROOT)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("mode", "unknown_mode", "mode"),
        ("case_type", "unknown_case_type", "case_type"),
        ("expected_result", "maybe", "expected_result"),
        ("metrics", ["unknown_metric"], "unknown_metric"),
    ],
)
def test_eval_case_rejects_invalid_enums(tmp_path: Path, field: str, value: object, message: str) -> None:
    data = valid_artifact_case(tmp_path)
    data[field] = value
    case_path = write_case(tmp_path, data)

    with pytest.raises(EvalCaseError, match=message):
        load_eval_case(case_path, repo_root=REPO_ROOT)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_root", "/tmp/outside"),
        ("artifact_root", "../outside"),
        ("artifact_root", "runs/old-eval-output"),
        ("artifact_root", "superpowers本体架构/notes"),
        ("task_path", "/tmp/task.yaml"),
        ("task_path", "../task.yaml"),
        ("task_path", "HARA报告生成参考资料集_EPS/task.yaml"),
    ],
)
def test_eval_case_rejects_unsafe_paths(tmp_path: Path, field: str, value: str) -> None:
    data = valid_artifact_case(tmp_path)
    if field == "task_path":
        data["mode"] = "run_task"
        data.pop("artifact_root")
    data[field] = value
    case_path = write_case(tmp_path, data)

    with pytest.raises(EvalCaseError, match="unsafe path"):
        load_eval_case(case_path, repo_root=REPO_ROOT)


def valid_artifact_case(tmp_path: Path) -> dict:
    artifact_root = tmp_path / "fixture"
    artifact_root.mkdir()
    return {
        "id": "valid_case",
        "schema_version": "eval_case.v1",
        "description": "Valid case",
        "document_type": "generic_document",
        "case_type": "negative_metric_guard",
        "mode": "artifact_fixture",
        "artifact_root": str(artifact_root.relative_to(REPO_ROOT)) if artifact_root.is_relative_to(REPO_ROOT) else "tests/evals/fixtures/negative_sample_misuse",
        "expected_result": "fail",
        "metrics": ["sample_misuse"],
        "expectations": {"expected_failures": ["sample_misuse"]},
    }


def write_case(tmp_path: Path, data: dict) -> Path:
    case_path = tmp_path / "case.yaml"
    case_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return case_path
