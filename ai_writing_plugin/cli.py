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
from .progress_ledger import (
    ProgressLedgerError,
    init_progress_ledger,
    progress_ledger_path,
    record_step_progress,
    validate_progress_ledger,
)
from .run_scaffold import RunScaffoldError, init_run
from .short_results import (
    ShortResultError,
    validate_review_result,
    validate_step_result,
)
from .step_worker_dispatch import (
    StepWorkerDispatchError,
    complete_step_worker_dispatch,
    prepare_step_worker_dispatch,
    step_worker_dispatch_path,
    validate_step_worker_dispatch,
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

    progress_ledger_init = subparsers.add_parser(
        "init-progress-ledger",
        help="Create an empty ProgressLedger for a run.",
    )
    progress_ledger_init.add_argument("--run-dir", required=True, help="Run directory.")
    progress_ledger_init.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the existing progress ledger.",
    )

    progress_ledger_recorder = subparsers.add_parser(
        "record-step-progress",
        help="Upsert one step entry in the ProgressLedger.",
    )
    progress_ledger_recorder.add_argument("--run-dir", required=True, help="Run directory.")
    progress_ledger_recorder.add_argument("--stage", required=True, help="Workflow stage.")
    progress_ledger_recorder.add_argument("--step", required=True, help="Workflow step.")
    progress_ledger_recorder.add_argument("--status", required=True, help="Ledger status.")
    progress_ledger_recorder.add_argument(
        "--context-package",
        help="Run-relative or run-contained absolute StepContextPackage path.",
    )
    progress_ledger_recorder.add_argument(
        "--step-result",
        help="Run-relative or run-contained absolute StepResult path.",
    )
    progress_ledger_recorder.add_argument(
        "--review-result",
        help="Run-relative or run-contained absolute ReviewResult path.",
    )

    progress_ledger_validator = subparsers.add_parser(
        "validate-progress-ledger",
        help="Validate a compact ProgressLedger JSON file.",
    )
    progress_ledger_validator.add_argument(
        "--path",
        required=True,
        help="Path to progress ledger JSON.",
    )
    progress_ledger_validator.add_argument(
        "--run-dir",
        help="Optional run directory for ref existence, sha256, and delegated checks.",
    )

    step_worker_dispatch_prepare = subparsers.add_parser(
        "prepare-step-worker-dispatch",
        help="Prepare an ingest-stage StepWorkerDispatch pilot file.",
    )
    step_worker_dispatch_prepare.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing commands/ and skills/.",
    )
    step_worker_dispatch_prepare.add_argument("--run-dir", required=True, help="Run directory.")
    step_worker_dispatch_prepare.add_argument("--stage", required=True, help="Workflow stage.")
    step_worker_dispatch_prepare.add_argument("--step", required=True, help="Workflow step.")
    step_worker_dispatch_prepare.add_argument("--task-type", required=True, help="Task type.")
    step_worker_dispatch_prepare.add_argument(
        "--input-ref",
        action="append",
        default=[],
        help="Additional run-relative artifact path to include in the context package.",
    )
    step_worker_dispatch_prepare.add_argument(
        "--overwrite-package",
        action="store_true",
        help="Overwrite the existing context package.",
    )
    step_worker_dispatch_prepare.add_argument(
        "--overwrite-dispatch",
        action="store_true",
        help="Overwrite the existing worker dispatch.",
    )

    step_worker_dispatch_complete = subparsers.add_parser(
        "complete-step-worker-dispatch",
        help="Complete an ingest-stage StepWorkerDispatch and update the ProgressLedger.",
    )
    step_worker_dispatch_complete.add_argument("--run-dir", required=True, help="Run directory.")
    step_worker_dispatch_complete.add_argument("--stage", required=True, help="Workflow stage.")
    step_worker_dispatch_complete.add_argument("--step", required=True, help="Workflow step.")
    step_worker_dispatch_complete.add_argument(
        "--step-result",
        required=True,
        help="Run-relative or run-contained absolute StepResult path.",
    )
    step_worker_dispatch_complete.add_argument(
        "--review-result",
        help="Run-relative or run-contained absolute ReviewResult path.",
    )
    step_worker_dispatch_complete.add_argument(
        "--status",
        help="Optional completion status override.",
    )

    step_worker_dispatch_validator = subparsers.add_parser(
        "validate-step-worker-dispatch",
        help="Validate a compact StepWorkerDispatch JSON file.",
    )
    step_worker_dispatch_validator.add_argument(
        "--path",
        required=True,
        help="Path to worker dispatch JSON.",
    )
    step_worker_dispatch_validator.add_argument(
        "--repo-root",
        help="Optional repository root for context package instruction ref checks.",
    )
    step_worker_dispatch_validator.add_argument(
        "--run-dir",
        help="Optional run directory for ref existence, sha256, and delegated checks.",
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

    if args.command == "init-progress-ledger":
        try:
            init_progress_ledger(
                run_dir=Path(args.run_dir),
                overwrite=args.overwrite,
            )
        except (OSError, ProgressLedgerError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print(progress_ledger_path(Path(args.run_dir)))
        return 0

    if args.command == "record-step-progress":
        try:
            record_step_progress(
                run_dir=Path(args.run_dir),
                stage=args.stage,
                step=args.step,
                status=args.status,
                context_package=Path(args.context_package) if args.context_package else None,
                step_result=Path(args.step_result) if args.step_result else None,
                review_result=Path(args.review_result) if args.review_result else None,
            )
        except (OSError, json.JSONDecodeError, ProgressLedgerError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print(progress_ledger_path(Path(args.run_dir)))
        return 0

    if args.command == "validate-progress-ledger":
        try:
            payload = load_json(Path(args.path))
            validate_progress_ledger(
                payload,
                run_dir=Path(args.run_dir) if args.run_dir else None,
            )
        except (
            OSError,
            json.JSONDecodeError,
            ShortResultError,
            ProgressLedgerError,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print("progress ledger valid")
        return 0

    if args.command == "prepare-step-worker-dispatch":
        try:
            prepare_step_worker_dispatch(
                repo_root=Path(args.repo_root),
                run_dir=Path(args.run_dir),
                stage=args.stage,
                step=args.step,
                task_type=args.task_type,
                input_refs=args.input_ref,
                overwrite_package=args.overwrite_package,
                overwrite_dispatch=args.overwrite_dispatch,
            )
        except (
            OSError,
            json.JSONDecodeError,
            ContextPackageError,
            ProgressLedgerError,
            StepWorkerDispatchError,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print(step_worker_dispatch_path(Path(args.run_dir), args.stage, args.step))
        return 0

    if args.command == "complete-step-worker-dispatch":
        try:
            complete_step_worker_dispatch(
                run_dir=Path(args.run_dir),
                stage=args.stage,
                step=args.step,
                step_result=Path(args.step_result),
                review_result=Path(args.review_result) if args.review_result else None,
                status=args.status,
            )
        except (
            OSError,
            json.JSONDecodeError,
            ShortResultError,
            ProgressLedgerError,
            StepWorkerDispatchError,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print(progress_ledger_path(Path(args.run_dir)))
        return 0

    if args.command == "validate-step-worker-dispatch":
        try:
            payload = load_json(Path(args.path))
            validate_step_worker_dispatch(
                payload,
                repo_root=Path(args.repo_root) if args.repo_root else None,
                run_dir=Path(args.run_dir) if args.run_dir else None,
            )
        except (
            OSError,
            json.JSONDecodeError,
            ShortResultError,
            ContextPackageError,
            ProgressLedgerError,
            StepWorkerDispatchError,
        ) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

        print("step worker dispatch valid")
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ShortResultError("result JSON must be an object")
    return payload
