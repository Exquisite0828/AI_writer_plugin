from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .input_refs import InputRefsError, validate_input_refs
from .short_results import RUN_ID_RE, SHA256_RE, STAGES, STEPS, ShortResultError
from .short_results import validate_result_path as validate_run_relative_path


PACKAGE_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "step",
    "task_type",
    "created_at",
    "instruction_refs",
    "input_refs_ref",
    "run_refs",
    "result_paths",
    "constraints",
}
REF_FIELDS = {"path", "sha256"}
RESULT_PATH_FIELDS = {"step_result", "review_result"}
FIXED_CONSTRAINTS = {
    "paths_and_hashes_only": True,
    "no_artifact_body": True,
    "no_input_body": True,
    "no_inline_instructions": True,
}
TASK_TYPE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ContextPackageError(ValueError):
    """Raised when a StepContextPackage is invalid or cannot be built."""


def build_step_context_package(
    repo_root: Path | str,
    run_dir: Path | str,
    stage: str,
    step: str,
    task_type: str,
    input_refs: list[str] | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    repo_root = Path(repo_root).expanduser().resolve()
    run_dir = Path(run_dir).expanduser().resolve()
    validate_stage(stage)
    validate_step(step)
    validate_task_type(task_type)
    run_id = run_dir.name
    validate_run_id(run_id)

    package_path = context_package_path(run_dir, stage, step)
    if package_path.exists() and not overwrite:
        raise ContextPackageError(f"context package already exists: {package_path}")

    instruction_paths = discover_instruction_refs(task_type, step)
    instruction_refs = [
        build_repo_ref(repo_root, path, required=path.startswith("skills/step-") or path.startswith("skills/workflow-steps/"))
        for path in instruction_paths
        if (repo_root / path).is_file()
        or path.startswith("skills/step-")
        or path.startswith("skills/workflow-steps/")
    ]

    run_paths = ["task_brief.json"]
    if step == "step-input-materials":
        run_paths.append("manifest.json")
    for input_ref in input_refs or []:
        validate_run_ref_path(input_ref)
        if input_ref == "input_refs.json":
            continue
        if input_ref not in run_paths:
            run_paths.append(input_ref)
    run_refs = [build_run_ref(run_dir, path) for path in run_paths]
    input_refs_ref = build_run_ref(run_dir, "input_refs.json")

    payload: dict[str, Any] = {
        "kind": "step_context_package",
        "schema_version": 1,
        "run_id": run_id,
        "stage": stage,
        "step": step,
        "task_type": task_type,
        "created_at": utc_now(),
        "instruction_refs": instruction_refs,
        "input_refs_ref": input_refs_ref,
        "run_refs": run_refs,
        "result_paths": expected_result_paths(stage, step),
        "constraints": dict(FIXED_CONSTRAINTS),
    }
    validate_step_context_package(payload, repo_root=repo_root, run_dir=run_dir)

    package_path.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


def validate_step_context_package(
    payload: dict[str, Any],
    repo_root: Path | str | None = None,
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContextPackageError("context package payload must be a JSON object")

    validate_exact_fields(payload, PACKAGE_FIELDS)
    validate_literal(payload["kind"], "step_context_package", "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_stage(payload["stage"])
    validate_step(payload["step"])
    validate_task_type(payload["task_type"])
    validate_created_at(payload["created_at"])

    instruction_refs = validate_ref_list(
        payload["instruction_refs"],
        "instruction_refs",
        validate_instruction_ref_path,
    )
    input_refs_ref = validate_ref(
        payload["input_refs_ref"],
        "input_refs_ref",
        validate_run_ref_path,
    )
    run_refs = validate_ref_list(
        payload["run_refs"],
        "run_refs",
        validate_run_ref_path,
    )
    validate_result_paths(payload["result_paths"], payload["stage"], payload["step"])
    validate_constraints(payload["constraints"])

    if repo_root is not None:
        validate_repo_refs(instruction_refs, Path(repo_root))
    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise ContextPackageError("run_id must match run_dir name")
        validate_run_refs([input_refs_ref], run_root)
        validate_input_refs_ref(
            input_refs_ref,
            run_root,
            repo_root,
            expected_run_id=payload["run_id"],
        )
        validate_run_refs(run_refs, run_root)
    validate_instruction_ref_contract(
        instruction_refs,
        task_type=payload["task_type"],
        step=payload["step"],
    )

    return payload


def context_package_path(run_dir: Path, stage: str, step: str) -> Path:
    return run_dir / "orchestration" / "context_packages" / stage / f"{step}.json"


def discover_instruction_refs(task_type: str, step: str) -> list[str]:
    return [
        f"skills/{step}/SKILL.md",
        f"skills/workflow-steps/{step}/SKILL.md",
        f"skills/document-types/{task_type}/SKILL.md",
        f"skills/document-types/{task_type}/steps/{step}.md",
    ]


def build_repo_ref(repo_root: Path, relative_path: str, *, required: bool) -> dict[str, str]:
    validate_instruction_ref_path(relative_path)
    path = repo_root / relative_path
    if not path.is_file():
        if required:
            raise ContextPackageError(f"instruction ref does not exist: {relative_path}")
        raise ContextPackageError(f"optional instruction ref does not exist: {relative_path}")
    return {"path": relative_path, "sha256": file_sha256(path)}


def build_run_ref(run_dir: Path, relative_path: str) -> dict[str, str]:
    validate_run_ref_path(relative_path)
    path = (run_dir / relative_path).resolve()
    root = run_dir.resolve()
    if not path.is_relative_to(root):
        raise ContextPackageError(f"run ref escapes run_dir: {relative_path}")
    if not path.is_file():
        raise ContextPackageError(f"run ref does not exist: {relative_path}")
    return {"path": relative_path, "sha256": file_sha256(path)}


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise ContextPackageError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise ContextPackageError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ContextPackageError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise ContextPackageError("run_id must be a safe non-empty run id")


def validate_stage(value: Any) -> None:
    if not isinstance(value, str) or value not in STAGES:
        raise ContextPackageError(f"invalid stage: {value!r}")


def validate_step(value: Any) -> None:
    if not isinstance(value, str) or value not in STEPS:
        raise ContextPackageError(f"invalid step: {value!r}")


def validate_task_type(value: Any) -> None:
    if not isinstance(value, str) or not TASK_TYPE_RE.match(value) or ".." in value:
        raise ContextPackageError("task_type must be a safe non-empty identifier")


def validate_created_at(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ContextPackageError("created_at must be a non-empty string")
    try:
        datetime.fromisoformat(value)
    except ValueError as exc:
        raise ContextPackageError("created_at must be an ISO 8601 timestamp") from exc


def validate_ref_list(
    value: Any,
    field: str,
    path_validator,
) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ContextPackageError(f"{field} must be a list")
    refs: list[dict[str, str]] = []
    seen_paths: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise ContextPackageError(f"{field} entries must be objects")
        validate_exact_fields(item, REF_FIELDS)
        path = item["path"]
        digest = item["sha256"]
        if not isinstance(path, str):
            raise ContextPackageError(f"{field} path must be a string")
        path_validator(path)
        if path in seen_paths:
            raise ContextPackageError(f"{field} must not contain duplicate paths")
        seen_paths.add(path)
        if not isinstance(digest, str) or not SHA256_RE.match(digest):
            raise ContextPackageError(f"invalid sha256 for {path}")
        refs.append({"path": path, "sha256": digest})
    return refs


def validate_ref(
    value: Any,
    field: str,
    path_validator,
) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ContextPackageError(f"{field} must be an object")
    validate_exact_fields(value, REF_FIELDS)
    path = value["path"]
    digest = value["sha256"]
    if not isinstance(path, str):
        raise ContextPackageError(f"{field} path must be a string")
    path_validator(path)
    if not isinstance(digest, str) or not SHA256_RE.match(digest):
        raise ContextPackageError(f"invalid sha256 for {path}")
    return {"path": path, "sha256": digest}


def validate_instruction_ref_path(path: str) -> None:
    validate_posix_relative_path(path)
    if not (
        re.match(r"^skills/step-[^/]+/SKILL\.md$", path)
        or re.match(r"^skills/workflow-steps/[^/]+/SKILL\.md$", path)
        or path.startswith("skills/document-types/")
    ):
        raise ContextPackageError(f"instruction_refs path is not allowed: {path!r}")


def validate_instruction_ref_contract(
    refs: list[dict[str, str]],
    *,
    task_type: str,
    step: str,
) -> None:
    allowed_paths = discover_instruction_refs(task_type, step)
    required_paths = allowed_paths[:2]
    actual_paths = [item["path"] for item in refs]
    expected_paths = required_paths + [
        path for path in allowed_paths[2:] if path in actual_paths
    ]
    if actual_paths != expected_paths:
        raise ContextPackageError(
            "instruction_refs must match the required wrapper/canonical refs and "
            "any included optional refs for the selected task_type"
        )


def validate_run_ref_path(path: str) -> None:
    try:
        validate_run_relative_path(path)
    except ShortResultError as exc:
        raise ContextPackageError(str(exc)) from exc


def validate_posix_relative_path(path: str) -> None:
    if not path or path.startswith("/") or path.startswith("~"):
        raise ContextPackageError(f"path must be a relative POSIX path: {path!r}")
    if "\\" in path:
        raise ContextPackageError(f"path must use POSIX separators: {path!r}")
    parts = PurePosixPath(path).parts
    if any(part == ".." for part in parts):
        raise ContextPackageError(f"path must not contain '..': {path!r}")
    if any(part in {"", "."} for part in parts):
        raise ContextPackageError(f"path must not contain empty or dot parts: {path!r}")


def validate_result_paths(value: Any, stage: str, step: str) -> None:
    if not isinstance(value, dict) or set(value) != RESULT_PATH_FIELDS:
        raise ContextPackageError("result_paths must contain step_result and review_result")
    expected = expected_result_paths(stage, step)
    if value != expected:
        raise ContextPackageError("result_paths must match the stage and step")
    for path in value.values():
        validate_run_ref_path(path)


def expected_result_paths(stage: str, step: str) -> dict[str, str]:
    return {
        "step_result": f"orchestration/step_results/{step}.json",
        "review_result": f"orchestration/review_results/{stage}/{step}.json",
    }


def validate_constraints(value: Any) -> None:
    if value != FIXED_CONSTRAINTS:
        raise ContextPackageError("constraints must declare the fixed context boundary")


def validate_repo_refs(refs: list[dict[str, str]], repo_root: Path) -> None:
    root = repo_root.expanduser().resolve()
    for item in refs:
        candidate = (root / item["path"]).resolve()
        if not candidate.is_relative_to(root):
            raise ContextPackageError(f"instruction ref escapes repo_root: {item['path']}")
        if not candidate.is_file():
            raise ContextPackageError(f"instruction ref does not exist: {item['path']}")
        digest = file_sha256(candidate)
        if digest != item["sha256"]:
            raise ContextPackageError(f"instruction ref sha256 mismatch: {item['path']}")


def validate_run_refs(refs: list[dict[str, str]], run_dir: Path) -> None:
    root = run_dir.expanduser().resolve()
    for item in refs:
        candidate = (root / item["path"]).resolve()
        if not candidate.is_relative_to(root):
            raise ContextPackageError(f"run ref escapes run_dir: {item['path']}")
        if not candidate.is_file():
            raise ContextPackageError(f"run ref does not exist: {item['path']}")
        digest = file_sha256(candidate)
        if digest != item["sha256"]:
            raise ContextPackageError(f"run ref sha256 mismatch: {item['path']}")


def validate_input_refs_ref(
    ref: dict[str, str],
    run_dir: Path,
    repo_root: Path | str | None,
    *,
    expected_run_id: str,
) -> None:
    try:
        payload = load_json((run_dir.expanduser().resolve() / ref["path"]).resolve())
        validate_input_refs(
            payload,
            repo_root=Path(repo_root) if repo_root is not None else None,
        )
        if payload["run_id"] != expected_run_id:
            raise ContextPackageError(
                "input_refs_ref run_id must match context package run_id"
            )
    except (OSError, json.JSONDecodeError, InputRefsError) as exc:
        raise ContextPackageError(f"invalid input_refs_ref: {exc}") from exc


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ContextPackageError(f"JSON file must contain an object: {path}")
    return payload


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
