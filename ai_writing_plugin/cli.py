from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .run_scaffold import RunScaffoldError, init_run


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

    parser.error(f"unsupported command: {args.command}")
    return 2
