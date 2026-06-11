from __future__ import annotations

from pathlib import Path

from ai_writing_plugin.eval.runner import load_eval_cases


REPO_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = REPO_ROOT / "tests" / "evals" / "cases"


def test_fsr_eval_cases_are_committed_and_cover_required_metrics() -> None:
    cases = {case.id: case for case in load_eval_cases(CASES_DIR, repo_root=REPO_ROOT)}
    fsr_cases = {case_id: case for case_id, case in cases.items() if case.document_type == "fsr"}

    assert set(fsr_cases) == {
        "fsr_l3_regression",
        "fsr_negative_sample_misuse",
        "fsr_negative_reference_misuse",
        "fsr_negative_unsupported_critical_claim",
        "fsr_negative_forbidden_final_claim",
        "fsr_negative_final_status_approval",
        "fsr_negative_candidate_update_active",
        "fsr_negative_tsc_leakage",
    }
    covered_metrics = {metric for case in fsr_cases.values() for metric in case.metrics}
    assert covered_metrics >= {
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
    }


def test_fsr_positive_eval_uses_demo_task_and_negative_cases_expect_fail() -> None:
    cases = {case.id: case for case in load_eval_cases(CASES_DIR, repo_root=REPO_ROOT)}
    positive = cases["fsr_l3_regression"]

    assert positive.mode == "run_task"
    assert positive.task_path == REPO_ROOT / "examples" / "fsr_demo_fixture" / "task.yaml"
    assert positive.expected_result == "pass"
    assert positive.case_type == "positive_regression"

    for case_id, case in cases.items():
        if case_id.startswith("fsr_negative_"):
            assert case.mode == "artifact_fixture"
            assert case.expected_result == "fail"
            assert case.case_type == "negative_metric_guard"


def test_no_tsc_official_artifacts_or_tests_exist() -> None:
    forbidden_paths = [
        REPO_ROOT / "ai_writing_plugin" / "document_types" / "tsc.py",
        REPO_ROOT / "examples" / "tsc_demo_fixture",
        REPO_ROOT / "skills" / "document-types" / "tsc" / "SKILL.md",
        REPO_ROOT / "profiles" / "document_types" / "tsc.yaml",
        REPO_ROOT / "ai_writing_plugin" / "tsc_pipeline.py",
    ]
    for path in forbidden_paths:
        assert not path.exists(), path

    assert not list(REPO_ROOT.glob("tests/test_tsc_*.py"))
