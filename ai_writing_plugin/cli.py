from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .context_packages import (
    ContextPackageError,
    build_step_context_package,
    context_package_path,
    validate_step_context_package,
)
from .run_scaffold import RunScaffoldError, init_run
from .short_results import (
    ShortResultError,
    validate_review_result,
    validate_step_result,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m ai_writing_plugin")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init-run",
        help="Create only Phase 0 run artifacts for a task YAML.",
    )
    init_parser.add_argument("--task", required=True, help="Path to task.yaml.")
    init_parser.add_argument(
        "--output-root",
        default="runs",
        help="Root directory for generated run directories.",
    )
    init_parser.add_argument(
        "--run-id",
        help="Optional deterministic run id for tests or controlled runs.",
    )

    step_result_parser = subparsers.add_parser(
        "validate-step-result",
        help="Validate a compact StepResult JSON file.",
    )
    step_result_parser.add_argument("--path", required=True, help="Path to result JSON.")
    step_result_parser.add_argument(
        "--run-dir",
        help="Optional run directory for file existence and sha256 checks.",
    )

    review_result_parser = subparsers.add_parser(
        "validate-review-result",
        help="Validate a compact ReviewResult JSON file.",
    )
    review_result_parser.add_argument("--path", required=True, help="Path to result JSON.")
    review_result_parser.add_argument(
        "--run-dir",
        help="Optional run directory for file existence and sha256 checks.",
    )

    context_package_builder = subparsers.add_parser(
        "build-step-context-package",
        help="Build a compact StepContextPackage JSON file.",
    )
    context_package_builder.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing commands/ and skills/.",
    )
    context_package_builder.add_argument("--run-dir", required=True, help="Run directory.")
    context_package_builder.add_argument("--stage", required=True, help="Workflow stage.")
    context_package_builder.add_argument("--step", required=True, help="Workflow step.")
    context_package_builder.add_argument("--task-type", required=True, help="Task type.")
    context_package_builder.add_argument(
        "--input-ref",
        action="append",
        default=[],
        help="Additional run-relative artifact path to include in run_refs.",
    )
    context_package_builder.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the existing package file.",
    )

    context_package_validator = subparsers.add_parser(
        "validate-step-context-package",
        help="Validate a compact StepContextPackage JSON file.",
    )
    context_package_validator.add_argument(
        "--path",
        required=True,
        help="Path to context package JSON.",
    )
    context_package_validator.add_argument(
        "--repo-root",
        help="Optional repository root for instruction ref existence and sha256 checks.",
    )
    context_package_validator.add_argument(
        "--run-dir",
        help="Optional run directory for run ref existence and sha256 checks.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-run":
        try:
            run_dir = init_run(
                task_path=Path(args.task),
                output_root=Path(args.output_root),
                run_id=args.run_id,
            )
        except RunScaffoldError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print(run_dir)
        return 0

    if args.command == "validate-step-result":
        try:
            payload = load_json(Path(args.path))
            validate_step_result(
                payload,
                run_dir=Path(args.run_dir) if args.run_dir else None,
            )
        except (OSError, json.JSONDecodeError, ShortResultError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print("step result valid")
        return 0

    if args.command == "validate-review-result":
        try:
            payload = load_json(Path(args.path))
            validate_review_result(
                payload,
                run_dir=Path(args.run_dir) if args.run_dir else None,
            )
        except (OSError, json.JSONDecodeError, ShortResultError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print("review result valid")
        return 0

    if args.command == "build-step-context-package":
        try:
            build_step_context_package(
                repo_root=Path(args.repo_root),
                run_dir=Path(args.run_dir),
                stage=args.stage,
                step=args.step,
                task_type=args.task_type,
                input_refs=args.input_ref,
                overwrite=args.overwrite,
            )
        except (OSError, ContextPackageError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print(context_package_path(Path(args.run_dir), args.stage, args.step))
        return 0

    if args.command == "validate-step-context-package":
        try:
            payload = load_json(Path(args.path))
            validate_step_context_package(
                payload,
                repo_root=Path(args.repo_root) if args.repo_root else None,
                run_dir=Path(args.run_dir) if args.run_dir else None,
            )
        except (
            OSError,
            json.JSONDecodeError,
            ShortResultError,
            ContextPackageError,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print("step context package valid")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ShortResultError("result JSON must be an object")
    return payload
