from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .input_refs import InputRefsError, build_input_refs, file_sha256, write_input_refs


RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class RunScaffoldError(Exception):
    """Raised when Phase 0 run scaffold creation must fail closed."""


def init_run(task_path: Path, output_root: Path, run_id: str | None = None) -> Path:
    task_path = task_path.expanduser()
    output_root = output_root.expanduser()

    if not task_path.is_file():
        raise RunScaffoldError(f"task file not found: {task_path}")

    task = load_task_yaml(task_path)
    task_type = task.get("task_type")
    if not isinstance(task_type, str) or not task_type.strip():
        raise RunScaffoldError("task.yaml must declare a non-empty task_type")

    safe_run_id = run_id or generate_run_id(task_type)
    validate_run_id(safe_run_id)

    run_dir = output_root / safe_run_id
    if run_dir.exists():
        raise RunScaffoldError(f"run directory already exists: {run_dir}")

    try:
        input_refs = build_input_refs(
            run_id=safe_run_id,
            task_path=task_path,
            task=task,
            repo_root=Path.cwd(),
        )
    except InputRefsError as exc:
        raise RunScaffoldError(str(exc)) from exc

    task_brief = build_task_brief(
        run_id=safe_run_id,
        task=task,
    )

    run_dir.mkdir(parents=True)
    input_refs_file = write_input_refs(run_dir, input_refs)
    created_at = utc_now()
    manifest = build_manifest(
        run_id=safe_run_id,
        task_path=task_path,
        created_at=created_at,
        input_refs_sha256=file_sha256(input_refs_file),
    )
    write_json(run_dir / "task_brief.json", task_brief)
    write_json(run_dir / "manifest.json", manifest)

    return run_dir


def generate_run_id(task_type: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", task_type.strip()).strip("-._")
    if not slug:
        slug = "run"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{slug}-{stamp}"


def validate_run_id(run_id: str) -> None:
    if not RUN_ID_RE.match(run_id) or ".." in run_id:
        raise RunScaffoldError(
            "run_id must contain only letters, numbers, dot, underscore, or hyphen "
            "and must not contain '..'"
        )


def build_manifest(
    run_id: str,
    task_path: Path,
    created_at: str,
    input_refs_sha256: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "task_file": str(task_path.resolve()),
        "created_at": created_at,
        "status": "initialized",
        "phase": "phase_0",
        "artifacts": [
            {
                "path": "input_refs.json",
                "kind": "input_refs",
                "sha256": input_refs_sha256,
                "created_at": created_at,
            },
            {
                "path": "manifest.json",
                "kind": "manifest",
                "created_at": created_at,
            },
            {
                "path": "task_brief.json",
                "kind": "task_brief",
                "created_at": created_at,
            },
        ],
    }


def build_task_brief(run_id: str, task: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "task_type": as_string(task.get("task_type"), "task_type"),
        "task_title": as_string(task.get("task_title", ""), "task_title"),
        "target_audience": as_string(
            task.get("target_audience", ""), "target_audience"
        ),
        "output_format": as_string(task.get("output_format", "markdown"), "output_format"),
        "strict_template": as_bool(task.get("strict_template", False), "strict_template"),
        "allow_inference": as_bool(task.get("allow_inference", False), "allow_inference"),
        "requires_human_confirmation": as_string_list(
            task.get("requires_human_confirmation", []),
            "requires_human_confirmation",
        ),
    }


def load_task_yaml(task_path: Path) -> dict[str, Any]:
    text = task_path.read_text(encoding="utf-8")
    try:
        return parse_simple_yaml(text)
    except RunScaffoldError:
        raise
    except Exception as exc:  # pragma: no cover - defensive fail-closed path.
        raise RunScaffoldError(f"invalid task YAML: {exc}") from exc


def parse_simple_yaml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_list_key: str | None = None
    current_item: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0:
            current_list_key = None
            current_item = None
            if ":" not in line:
                raise RunScaffoldError(f"invalid task YAML line: {raw_line}")
            key, value = line.split(":", 1)
            key = key.strip()
            if not key:
                raise RunScaffoldError(f"invalid empty YAML key: {raw_line}")
            value = value.strip()
            if value == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = parse_scalar(value)
            continue

        if current_list_key is None:
            raise RunScaffoldError(f"unexpected indented YAML line: {raw_line}")

        if line.startswith("- "):
            item_text = line[2:].strip()
            if ":" in item_text:
                item_key, item_value = item_text.split(":", 1)
                current_item = {item_key.strip(): parse_scalar(item_value.strip())}
                data[current_list_key].append(current_item)
            else:
                current_item = None
                data[current_list_key].append(parse_scalar(item_text))
            continue

        if current_item is not None and ":" in line:
            item_key, item_value = line.split(":", 1)
            current_item[item_key.strip()] = parse_scalar(item_value.strip())
            continue

        raise RunScaffoldError(f"unsupported YAML structure: {raw_line}")

    if not isinstance(data, dict):
        raise RunScaffoldError("task YAML must be a mapping")
    return data


def parse_scalar(value: str) -> Any:
    if has_unbalanced_brackets(value):
        raise RunScaffoldError(f"invalid YAML scalar: {value}")

    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "~"}:
        return None
    if (
        (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        return value[1:-1]
    return value


def has_unbalanced_brackets(value: str) -> bool:
    pairs = {"[": "]", "{": "}"}
    stack: list[str] = []
    for char in value:
        if char in pairs:
            stack.append(pairs[char])
        elif char in pairs.values():
            if not stack or stack.pop() != char:
                return True
    return bool(stack)


def as_string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise RunScaffoldError(f"{field} must be a string")
    return value


def as_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise RunScaffoldError(f"{field} must be true or false")
    return value


def as_string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise RunScaffoldError(f"{field} must be a list of strings")
    return value


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
