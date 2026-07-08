from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .context_metrics import collect_context_metrics


SCHEMA_VERSION = "context_telemetry.v1"
MEASUREMENT_STATUS = "estimated_static_analysis"
RUNTIME_GLOBS = ["commands/**/*.md", "skills/**/*.md"]
FORBIDDEN_DEFAULT_CONTEXT_GLOBS = [
    "docs/maintainers/**",
    "examples/**",
    "runs/**",
]
CACHE_METRICS_NOT_MEASURED = {
    "api_cache_read_ratio": None,
    "measurement_status": "not_measured",
    "reason": "No API-level cache telemetry is available in this deterministic test harness.",
}
DEFAULT_BUDGETS = {
    "total_runtime_surface": {
        "preferred_tokens": 100_000,
        "hard_limit_tokens": 150_000,
    },
    "active_workflow": {
        "preferred_tokens": 50_000,
        "hard_limit_tokens": 60_000,
    },
    "active_step": {
        "preferred_tokens": 15_000,
        "hard_limit_tokens": 20_000,
    },
    "single_runtime_file": {
        "preferred_tokens": 5_000,
        "hard_limit_tokens": 8_000,
    },
}


def build_context_telemetry(
    root: Path | str,
    *,
    task_type: str,
    step: str,
    largest_limit: int = 20,
    budget_overrides: dict[str, dict[str, int]] | None = None,
) -> dict[str, Any]:
    budgets = build_budgets(budget_overrides)
    total_metrics = collect_context_metrics(
        root,
        largest_limit=largest_limit,
        mode="total",
    )
    workflow_metrics = collect_context_metrics(
        root,
        largest_limit=largest_limit,
        mode="active-workflow",
        task_type=task_type,
    )
    step_metrics = collect_context_metrics(
        root,
        largest_limit=largest_limit,
        mode="active-step",
        task_type=task_type,
        step=step,
    )
    measurements = {
        "total_runtime_surface": measurement_for(total_metrics),
        "active_workflow": {
            **measurement_for(workflow_metrics),
            "task_type": task_type,
        },
        "active_step": {
            **measurement_for(step_metrics),
            "task_type": task_type,
            "step": step,
        },
    }
    largest_runtime_files = largest_files_for(total_metrics)
    max_file_tokens = (
        largest_runtime_files[0]["estimated_tokens"] if largest_runtime_files else 0
    )
    budget_results = {
        "total_runtime_surface": budget_result(
            budgets["total_runtime_surface"],
            measurements["total_runtime_surface"]["estimated_tokens"],
        ),
        "active_workflow": budget_result(
            budgets["active_workflow"],
            measurements["active_workflow"]["estimated_tokens"],
        ),
        "active_step": budget_result(
            budgets["active_step"],
            measurements["active_step"]["estimated_tokens"],
        ),
        "single_runtime_file": budget_result(
            budgets["single_runtime_file"],
            max_file_tokens,
        ),
    }
    apply_measurement_statuses(measurements, budget_results)
    summary = budget_summary(budget_results)

    return {
        "schema_version": SCHEMA_VERSION,
        "root": display_root(root),
        "measurement_status": MEASUREMENT_STATUS,
        "measurements": measurements,
        "budgets": budget_results,
        "budget_summary": summary,
        "largest_runtime_files": largest_runtime_files,
        "runtime_boundary": runtime_boundary(),
        "cache_metrics": dict(CACHE_METRICS_NOT_MEASURED),
        "overall_status": "fail" if summary["hard_failures"] else "pass",
    }


def build_budgets(
    overrides: dict[str, dict[str, int]] | None = None,
) -> dict[str, dict[str, int]]:
    budgets = deepcopy(DEFAULT_BUDGETS)
    if not overrides:
        return budgets
    for scope, scope_overrides in overrides.items():
        if scope not in budgets:
            raise ValueError(f"unknown context budget scope: {scope!r}")
        for key, value in scope_overrides.items():
            if key not in {"preferred_tokens", "hard_limit_tokens"}:
                raise ValueError(f"unknown context budget field: {scope}.{key}")
            if value < 0:
                raise ValueError(f"context budget value must be non-negative: {scope}.{key}")
            budgets[scope][key] = value
        if (
            "hard_limit_tokens" in scope_overrides
            and "preferred_tokens" not in scope_overrides
            and budgets[scope]["preferred_tokens"] > budgets[scope]["hard_limit_tokens"]
        ):
            budgets[scope]["preferred_tokens"] = budgets[scope]["hard_limit_tokens"]
        validate_budget(scope, budgets[scope])
    return budgets


def validate_budget(scope: str, budget: dict[str, int]) -> None:
    if budget["preferred_tokens"] > budget["hard_limit_tokens"]:
        raise ValueError(f"preferred budget exceeds hard limit for {scope}")


def measurement_for(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "estimated_tokens": metrics["estimated_tokens"],
        "file_count": metrics["total_files"],
        "status": "pass",
    }


def apply_measurement_statuses(
    measurements: dict[str, dict[str, Any]],
    budget_results: dict[str, dict[str, Any]],
) -> None:
    for scope in ("total_runtime_surface", "active_workflow", "active_step"):
        measurements[scope]["status"] = budget_results[scope]["status"]


def budget_result(budget: dict[str, int], estimated_tokens: int) -> dict[str, Any]:
    return {
        "preferred_tokens": budget["preferred_tokens"],
        "hard_limit_tokens": budget["hard_limit_tokens"],
        "estimated_tokens": estimated_tokens,
        "status": status_for(
            estimated_tokens,
            preferred_tokens=budget["preferred_tokens"],
            hard_limit_tokens=budget["hard_limit_tokens"],
        ),
    }


def status_for(
    estimated_tokens: int,
    *,
    preferred_tokens: int,
    hard_limit_tokens: int,
) -> str:
    if estimated_tokens > hard_limit_tokens:
        return "fail"
    if estimated_tokens > preferred_tokens:
        return "warn"
    return "pass"


def budget_summary(budgets: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "hard_failures": [
            scope for scope, result in budgets.items() if result["status"] == "fail"
        ],
        "warnings": [
            scope for scope, result in budgets.items() if result["status"] == "warn"
        ],
    }


def largest_files_for(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "path": item["path"],
            "estimated_tokens": item["estimated_tokens"],
            "word_count": item["word_count"],
        }
        for item in sorted(
            metrics["files"],
            key=lambda candidate: (-candidate["estimated_tokens"], candidate["path"]),
        )[: len(metrics["largest_files"])]
    ]


def runtime_boundary() -> dict[str, Any]:
    return {
        "runtime_globs": list(RUNTIME_GLOBS),
        "forbidden_default_context_globs": list(FORBIDDEN_DEFAULT_CONTEXT_GLOBS),
        "artifact_body_replay_measured": False,
        "artifact_body_replay_status": "covered_by_tests",
        "sibling_document_type_reads_measured": False,
        "sibling_document_type_status": "structurally_guarded",
        "default_runtime_surface_status": "structurally_guarded",
        "notes": [
            "Runtime static analysis is limited to commands/**/*.md and skills/**/*.md.",
            "Artifact body replay is not measured through a real Claude run in Round 1.",
            "API-level prompt cache read ratio is not available in this deterministic test harness.",
        ],
    }


def display_root(root: Path | str) -> str:
    root_path = Path(root)
    if not root_path.is_absolute():
        return root_path.as_posix()
    try:
        return root_path.resolve().relative_to(Path.cwd().resolve()).as_posix() or "."
    except ValueError:
        return root_path.name
