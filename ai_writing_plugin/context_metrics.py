from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any


RUNTIME_PROMPT_DIRS = ("commands", "skills")
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
) -> dict[str, Any]:
    repo_root = Path(root).expanduser().resolve()
    files = [analyze_file(path, repo_root) for path in runtime_markdown_files(repo_root)]
    files.sort(key=lambda item: item["path"])

    by_category = build_category_totals(files)
    total_bytes = sum(item["bytes"] for item in files)
    estimated_tokens = sum(item["estimated_tokens"] for item in files)
    largest_files = sorted(files, key=lambda item: (-item["bytes"], item["path"]))[
        :largest_limit
    ]

    return {
        "generated_at": generated_at or utc_now(),
        "root": str(repo_root),
        "scope": list(RUNTIME_PROMPT_DIRS),
        "token_estimation": "ceil(character_count / 4); trend metric only, not provider billing",
        "total_files": len(files),
        "total_bytes": total_bytes,
        "estimated_tokens": estimated_tokens,
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


def analyze_file(path: Path, repo_root: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    encoded = text.encode("utf-8")
    relative_path = path.relative_to(repo_root).as_posix()
    return {
        "path": relative_path,
        "category": categorize_runtime_prompt(relative_path),
        "bytes": len(encoded),
        "characters": len(text),
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    metrics = collect_context_metrics(
        Path(args.root),
        largest_limit=args.largest_limit,
    )
    if args.json:
        print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    print(f"runtime prompt files: {metrics['total_files']}")
    print(f"runtime prompt bytes: {metrics['total_bytes']}")
    print(f"estimated tokens: {metrics['estimated_tokens']}")
    print("largest files:")
    for item in metrics["largest_files"]:
        print(f"- {item['path']}: {item['bytes']} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
