import json
import subprocess
import sys
from pathlib import Path

from ai_writing_plugin.eval.runner import run_eval_cases


REPO_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = REPO_ROOT / "tests" / "evals" / "cases"


def test_runner_executes_artifact_fixture_case_and_writes_report(tmp_path: Path) -> None:
    report = run_eval_cases(
        cases_path=CASES_DIR,
        output_dir=tmp_path / "eval-output",
        repo_root=REPO_ROOT,
        case_ids=["negative_sample_misuse"],
    )

    assert report["overall_status"] == "pass"
    assert report["case_count"] == 1
    assert report["case_results"][0]["actual_result"] == "fail"
    assert report["case_results"][0]["expectation_met"] is True
    assert (tmp_path / "eval-output" / "eval_report.json").exists()
    assert (tmp_path / "eval-output" / "eval_summary.md").exists()


def test_runner_executes_run_task_case(tmp_path: Path) -> None:
    report = run_eval_cases(
        cases_path=CASES_DIR,
        output_dir=tmp_path / "eval-output",
        repo_root=REPO_ROOT,
        case_ids=["generic_document_smoke"],
    )

    assert report["overall_status"] == "pass"
    case_result = report["case_results"][0]
    assert case_result["case_id"] == "generic_document_smoke"
    assert case_result["mode"] == "run_task"
    assert case_result["actual_result"] == "pass"
    assert case_result["expectation_met"] is True
    assert Path(case_result["artifact_root"]).exists()


def test_runner_reports_expectation_mismatch(tmp_path: Path) -> None:
    report = run_eval_cases(
        cases_path=CASES_DIR,
        output_dir=tmp_path / "eval-output",
        repo_root=REPO_ROOT,
        case_ids=["negative_sample_misuse"],
        expected_result_overrides={"negative_sample_misuse": "pass"},
    )

    assert report["overall_status"] == "fail"
    assert report["expectation_mismatch_count"] == 1
    assert report["case_results"][0]["expectation_met"] is False


def test_module_entrypoint_smoke(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin.eval.runner",
            "--cases",
            str(CASES_DIR),
            "--output",
            str(tmp_path / "manual"),
            "--case",
            "negative_sample_misuse",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads((tmp_path / "manual" / "eval_report.json").read_text(encoding="utf-8"))
    assert report["expectation_mismatch_count"] == 0
    assert "not professional approval" in report["non_approval_notice"]
