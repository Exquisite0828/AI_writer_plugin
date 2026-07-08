from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any


RUNTIME_PROMPT_DIRS = ("commands", "skills")
METRIC_MODES = ("total", "active-workflow", "active-step")
ACTIVE_WORKFLOW_STEPS = (
    "step-input-materials",
    "step-material-inventory",
    "step-source-index",
    "step-template-outline",
    "step-research-questions",
    "step-evidence-map",
    "step-conservative-draft",
    "step-review",
    "step-verification",
    "step-revision",
    "step-final-report",
    "step-run-summary",
    "step-candidate-profile-update",
)
HOTSPOT_PATTERNS = {
    "main_agent_execution": "主执行上下文",
    "subagent": "subagent",
    "stage_review": "stage_reviews",
    "artifact_contract": "CURRENT_ARTIFACT_CONTRACTS",
    "examples_boundary": "examples/",
}


def collect_context_metrics(
    root: Path | str,
    *,
    generated_at: str | None = None,
    largest_limit: int = 20,
    mode: str = "total",
    task_type: str | None = None,
    step: str | None = None,
) -> dict[str, Any]:
    repo_root = Path(root).expanduser().resolve()
    validate_metric_request(mode, task_type, step)

    total_paths = runtime_markdown_files(repo_root)
    total_file_map = {path: analyze_file(path, repo_root) for path in total_paths}
    selected_paths = select_runtime_markdown_files(
        repo_root,
        mode=mode,
        task_type=task_type,
        step=step,
        total_paths=total_paths,
    )
    files = [total_file_map[path] for path in selected_paths if path in total_file_map]
    files.sort(key=lambda item: item["path"])

    by_category = build_category_totals(files)
    total_bytes = sum(item["bytes"] for item in files)
    estimated_tokens = sum(item["estimated_tokens"] for item in files)
    total_runtime_estimated_tokens = sum(
        item["estimated_tokens"] for item in total_file_map.values()
    )
    selected_rel_paths = {item["path"] for item in files}
    excluded_document_type_files = [
        item
        for item in total_file_map.values()
        if item["category"] == "document_type" and item["path"] not in selected_rel_paths
    ]
    largest_files = sorted(files, key=lambda item: (-item["bytes"], item["path"]))[
        :largest_limit
    ]

    return {
        "generated_at": generated_at or utc_now(),
        "root": str(repo_root),
        "scope": list(RUNTIME_PROMPT_DIRS),
        "mode": mode,
        "task_type": task_type,
        "step": step,
        "token_estimation": "ceil(character_count / 4); trend metric only, not provider billing",
        "total_files": len(files),
        "total_bytes": total_bytes,
        "estimated_tokens": estimated_tokens,
        "total_runtime_estimated_tokens": total_runtime_estimated_tokens,
        "active_reduction_vs_total": calculate_reduction(
            total_runtime_estimated_tokens,
            estimated_tokens,
        ),
        "excluded_document_type_files": len(excluded_document_type_files),
        "excluded_document_type_bytes": sum(
            item["bytes"] for item in excluded_document_type_files
        ),
        "by_category": by_category,
        "largest_files": largest_files,
        "hotspot_patterns": collect_hotspot_patterns(files),
        "files": files,
    }


def runtime_markdown_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for dirname in RUNTIME_PROMPT_DIRS:
        base = repo_root / dirname
        if base.is_dir():
            paths.extend(sorted(base.rglob("*.md")))
    return paths


def validate_metric_request(
    mode: str,
    task_type: str | None,
    step: str | None,
) -> None:
    if mode not in METRIC_MODES:
        raise ValueError(f"invalid mode: {mode!r}")
    if mode in {"active-workflow", "active-step"} and not task_type:
        raise ValueError("task_type is required for active metrics")
    if mode == "active-step" and not step:
        raise ValueError("step is required for active-step metrics")
    if step is not None and step not in ACTIVE_WORKFLOW_STEPS:
        raise ValueError(f"invalid step for active metrics: {step!r}")


def select_runtime_markdown_files(
    repo_root: Path,
    *,
    mode: str,
    task_type: str | None,
    step: str | None,
    total_paths: list[Path],
) -> list[Path]:
    if mode == "total":
        return list(total_paths)
    if mode == "active-workflow":
        assert task_type is not None
        return existing_paths(repo_root, active_workflow_relative_paths(task_type))
    assert task_type is not None
    assert step is not None
    return existing_paths(repo_root, active_step_relative_paths(task_type, step))


def active_workflow_relative_paths(task_type: str) -> list[str]:
    paths = active_common_relative_paths()
    for step in ACTIVE_WORKFLOW_STEPS:
        paths.append(f"skills/{step}/SKILL.md")
        paths.append(f"skills/workflow-steps/{step}/SKILL.md")
    paths.append(f"skills/document-types/{task_type}/SKILL.md")
    for step in ACTIVE_WORKFLOW_STEPS:
        paths.append(f"skills/document-types/{task_type}/steps/{step}.md")
    return unique_preserving_order(paths)


def active_step_relative_paths(task_type: str, step: str) -> list[str]:
    return unique_preserving_order(
        [
            *active_common_relative_paths(),
            f"skills/{step}/SKILL.md",
            f"skills/workflow-steps/{step}/SKILL.md",
            f"skills/document-types/{task_type}/SKILL.md",
            f"skills/document-types/{task_type}/steps/{step}.md",
        ]
    )


def active_common_relative_paths() -> list[str]:
    return [
        "commands/write.md",
        "skills/workflow-orchestrator/SKILL.md",
        "skills/writing-core/SKILL.md",
    ]


def existing_paths(repo_root: Path, relative_paths: list[str]) -> list[Path]:
    paths: list[Path] = []
    for relative_path in relative_paths:
        path = repo_root / relative_path
        if path.is_file():
            paths.append(path)
    return paths


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value not in seen:
            unique_values.append(value)
            seen.add(value)
    return unique_values


def calculate_reduction(total_tokens: int, active_tokens: int) -> float:
    if total_tokens <= 0:
        return 0.0
    return round((total_tokens - active_tokens) / total_tokens, 6)


def analyze_file(path: Path, repo_root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    encoded = text.encode("utf-8")
    relative_path = path.relative_to(repo_root).as_posix()
    return {
        "path": relative_path,
        "category": categorize_runtime_prompt(relative_path),
        "bytes": len(encoded),
        "characters": len(text),
        "word_count": len(text.split()),
        "estimated_tokens": estimate_tokens(text),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "hotspot_counts": count_hotspots(text),
    }


def categorize_runtime_prompt(relative_path: str) -> str:
    if relative_path.startswith("commands/"):
        return "command"
    if relative_path == "skills/workflow-orchestrator/SKILL.md":
        return "workflow_orchestrator"
    if relative_path == "skills/writing-core/SKILL.md":
        return "writing_core"
    if relative_path.startswith("skills/workflow-steps/"):
        return "workflow_step"
    if relative_path.startswith("skills/document-types/"):
        return "document_type"
    if relative_path.startswith("skills/step-"):
        return "step_wrapper"
    return "skill_other"


def build_category_totals(files: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    categories: dict[str, dict[str, int]] = {}
    for item in files:
        category = item["category"]
        totals = categories.setdefault(
            category,
            {"file_count": 0, "bytes": 0, "estimated_tokens": 0},
        )
        totals["file_count"] += 1
        totals["bytes"] += item["bytes"]
        totals["estimated_tokens"] += item["estimated_tokens"]
    return dict(sorted(categories.items()))


def collect_hotspot_patterns(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals = {name: 0 for name in HOTSPOT_PATTERNS}
    for item in files:
        for name, count in item["hotspot_counts"].items():
            totals[name] += count
    return [
        {
            "id": name,
            "pattern": HOTSPOT_PATTERNS[name],
            "occurrences": totals[name],
        }
        for name in sorted(totals)
    ]


def count_hotspots(text: str) -> dict[str, int]:
    lowered = text.lower()
    counts: dict[str, int] = {}
    for name, pattern in HOTSPOT_PATTERNS.items():
        candidate = lowered if pattern.isascii() else text
        needle = pattern.lower() if pattern.isascii() else pattern
        counts[name] = candidate.count(needle)
    return counts


def estimate_tokens(text: str) -> int:
    return ceil(len(text) / 4)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ai_writing_plugin.context_metrics",
        description="Measure runtime prompt context size for commands/ and skills/.",
    )
    parser.add_argument("--root", default=".", help="Repository root to inspect.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full metrics payload as JSON.",
    )
    parser.add_argument(
        "--largest-limit",
        type=int,
        default=20,
        help="Number of largest files to include in the metrics payload.",
    )
    parser.add_argument(
        "--mode",
        choices=METRIC_MODES,
        default="total",
        help="Metrics mode: total runtime surface or active context estimate.",
    )
    parser.add_argument(
        "--task-type",
        help="Task type used for active-workflow or active-step modes.",
    )
    parser.add_argument(
        "--step",
        help="Workflow step used for active-step mode.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        metrics = collect_context_metrics(
            Path(args.root),
            largest_limit=args.largest_limit,
            mode=args.mode,
            task_type=args.task_type,
            step=args.step,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    print(f"mode: {metrics['mode']}")
    print(f"runtime prompt files: {metrics['total_files']}")
    print(f"runtime prompt bytes: {metrics['total_bytes']}")
    print(f"estimated tokens: {metrics['estimated_tokens']}")
    print(f"total runtime estimated tokens: {metrics['total_runtime_estimated_tokens']}")
    print(f"active reduction vs total: {metrics['active_reduction_vs_total']}")
    print("largest files:")
    for item in metrics["largest_files"]:
        print(f"- {item['path']}: {item['bytes']} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
