import json
import subprocess
import sys
from pathlib import Path

from ai_writing_plugin.context_telemetry import build_context_telemetry


ROOT = Path(__file__).resolve().parents[1]


def test_current_baseline_budget_does_not_hard_fail():
    report = build_context_telemetry(ROOT, task_type="hara", step="step-evidence-map")

    assert report["overall_status"] == "pass"
    assert report["budget_summary"]["hard_failures"] == []
    assert report["budgets"]["total_runtime_surface"]["status"] == "warn"
    assert report["budgets"]["active_workflow"]["status"] == "warn"
    assert report["budgets"]["active_step"]["status"] in {"pass", "warn"}


def test_constructed_over_budget_case_hard_fails():
    report = build_context_telemetry(
        ROOT,
        task_type="hara",
        step="step-evidence-map",
        budget_overrides={
            "total_runtime_surface": {"hard_limit_tokens": 1},
            "active_workflow": {"hard_limit_tokens": 1},
            "active_step": {"hard_limit_tokens": 1},
            "single_runtime_file": {"hard_limit_tokens": 1},
        },
    )

    assert report["overall_status"] == "fail"
    assert set(report["budget_summary"]["hard_failures"]) == {
        "total_runtime_surface",
        "active_workflow",
        "active_step",
        "single_runtime_file",
    }


def test_warn_status_does_not_make_budget_cli_fail():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "check-context-budget",
            "--root",
            ".",
            "--task-type",
            "hara",
            "--step",
            "step-evidence-map",
            "--total-preferred-tokens",
            "1",
            "--total-hard-limit-tokens",
            "999999",
            "--active-workflow-preferred-tokens",
            "1",
            "--active-workflow-hard-limit-tokens",
            "999999",
            "--active-step-preferred-tokens",
            "1",
            "--active-step-hard-limit-tokens",
            "999999",
            "--single-runtime-file-preferred-tokens",
            "1",
            "--single-runtime-file-hard-limit-tokens",
            "999999",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["overall_status"] == "pass"
    assert payload["budget_summary"]["hard_failures"] == []
    assert set(payload["budget_summary"]["warnings"]) == {
        "total_runtime_surface",
        "active_workflow",
        "active_step",
        "single_runtime_file",
    }


def test_hard_limit_violation_makes_budget_cli_fail():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "check-context-budget",
            "--root",
            ".",
            "--task-type",
            "hara",
            "--step",
            "step-evidence-map",
            "--total-hard-limit-tokens",
            "1",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["overall_status"] == "fail"
    assert "total_runtime_surface" in payload["budget_summary"]["hard_failures"]


def test_context_telemetry_cli_outputs_budget_report_json():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "context-telemetry",
            "--root",
            ".",
            "--task-type",
            "hara",
            "--step",
            "step-evidence-map",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "context_telemetry.v1"
    assert payload["measurements"]["active_step"]["task_type"] == "hara"
    assert payload["measurements"]["active_step"]["step"] == "step-evidence-map"
