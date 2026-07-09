from __future__ import annotations

import hashlib
import json
import mimetypes
import re
from pathlib import Path, PurePosixPath
from typing import Any

from .short_results import RUN_ID_RE, SHA256_RE


SCHEMA_VERSION = "input_refs.v1"
CREATED_BY = "ai_writing_plugin.input_refs"
ALLOWED_ROLES = {
    "task",
    "source",
    "template",
    "sample",
    "profile",
    "rubric",
    "instruction",
    "reference",
    "other",
}
ALLOWED_READ_POLICIES = {
    "allowed",
    "summary_only",
    "metadata_only",
    "blocked",
}
ALLOWED_PATH_KINDS = {"repo_relative", "external"}
BODY_LIKE_KEYS = {
    "artifact_body",
    "body",
    "canonical_text",
    "content",
    "excerpt",
    "full_text",
    "raw",
    "source_body",
    "task_body",
    "text",
}
INPUT_REFS_FIELDS = {
    "schema_version",
    "run_id",
    "created_by",
    "constraints",
    "task_ref",
    "input_materials",
    "warnings",
}
CONSTRAINT_FIELDS = {
    "paths_and_hashes_only",
    "no_inline_body",
    "examples_opt_in_only",
    "sample_is_not_fact_source",
    "deterministic_no_timestamps",
}
FIXED_CONSTRAINTS = {
    "paths_and_hashes_only": True,
    "no_inline_body": True,
    "examples_opt_in_only": True,
    "sample_is_not_fact_source": True,
    "deterministic_no_timestamps": True,
}
TASK_REF_FIELDS = {
    "path",
    "path_kind",
    "sha256",
    "size_bytes",
    "role",
    "read_policy",
    "fact_source_allowed",
}
MATERIAL_FIELDS = {
    "material_id",
    "role",
    "path",
    "path_kind",
    "sha256",
    "size_bytes",
    "mime_type",
    "read_policy",
    "fact_source_allowed",
    "selected_by",
}
GLOB_CHARS_RE = re.compile(r"[*?\[]")
SAMPLE_PATH_MARKERS = {
    "example",
    "examples",
    "expected",
    "expected-output",
    "expected-outputs",
    "expected_output",
    "expected_outputs",
    "sample",
    "samples",
}


class InputRefsError(ValueError):
    """Raised when input reference metadata is invalid or cannot be built."""


def input_refs_path(run_dir: Path | str) -> Path:
    return Path(run_dir) / "input_refs.json"


def build_input_refs(
    *,
    run_id: str,
    task_path: Path | str,
    task: dict[str, Any],
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    validate_run_id(run_id)
    if not isinstance(task, dict):
        raise InputRefsError("task must be a mapping")

    task_file = Path(task_path).expanduser().resolve()
    if not task_file.is_file():
        raise InputRefsError(f"task file does not exist: {task_path}")

    repo = Path(repo_root).expanduser().resolve() if repo_root is not None else None
    warnings: list[str] = []
    task_ref = build_file_ref(
        path=task_file,
        repo_root=repo,
        role="task",
        read_policy="metadata_only",
        fact_source_allowed=False,
    )

    raw_inputs = task.get("inputs")
    materials: list[dict[str, Any]] = []
    if raw_inputs is None or raw_inputs == []:
        warnings.append("no explicit input materials declared; input_materials is empty")
    else:
        if not isinstance(raw_inputs, list):
            raise InputRefsError("inputs must be a list")
        for raw_item in raw_inputs:
            materials.append(
                build_material_ref(
                    raw_item,
                    task_dir=task_file.parent,
                    repo_root=repo,
                    warnings=warnings,
                )
            )

    materials.sort(key=lambda item: (item["role"], item["path"]))
    for index, material in enumerate(materials, start=1):
        material["material_id"] = f"input-{index:03d}"

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "created_by": CREATED_BY,
        "constraints": dict(FIXED_CONSTRAINTS),
        "task_ref": task_ref,
        "input_materials": materials,
        "warnings": warnings,
    }
    validate_input_refs(payload, repo_root=repo)
    return payload


def build_material_ref(
    raw_item: Any,
    *,
    task_dir: Path,
    repo_root: Path | None,
    warnings: list[str],
) -> dict[str, Any]:
    if isinstance(raw_item, str):
        item = {"path": raw_item}
    elif isinstance(raw_item, dict):
        item = dict(raw_item)
    else:
        raise InputRefsError("input material entries must be strings or objects")

    reject_body_like_keys(item)
    raw_path = require_string(item.get("path"), "input material path")
    validate_declared_path(raw_path)
    material_path = resolve_declared_path(raw_path, task_dir)
    if not material_path.is_file():
        raise InputRefsError(f"input material does not exist: {raw_path}")

    raw_role = item.get("role")
    if raw_role is None:
        role = "other"
        warnings.append(
            f"input material {raw_path} has no role; using role=other and summary_only"
        )
    else:
        role = require_string(raw_role, "input material role")
    validate_role(role)

    manifest_path, path_kind = normalize_manifest_path(material_path, repo_root)
    sample_like = is_sample_like_path(manifest_path) or role == "sample"
    read_policy = material_read_policy(item.get("read_policy"), role, sample_like)
    requested_fact_source = item.get("fact_source_allowed")
    fact_source_allowed = material_fact_source_allowed(
        requested_fact_source,
        role,
        sample_like,
    )

    if sample_like and requested_fact_source is True:
        warnings.append(
            f"input material {raw_path} is sample/example/expected-output; "
            "fact_source_allowed forced to false"
        )
    if sample_like and item.get("read_policy") == "allowed":
        warnings.append(
            f"input material {raw_path} is sample/example/expected-output; "
            "read_policy forced to summary_only"
        )

    return {
        "material_id": "",
        "role": role,
        "path": manifest_path,
        "path_kind": path_kind,
        "sha256": file_sha256(material_path),
        "size_bytes": material_path.stat().st_size,
        "mime_type": guess_mime_type(material_path),
        "read_policy": read_policy,
        "fact_source_allowed": fact_source_allowed,
        "selected_by": "task",
    }


def build_file_ref(
    *,
    path: Path,
    repo_root: Path | None,
    role: str,
    read_policy: str,
    fact_source_allowed: bool,
) -> dict[str, Any]:
    validate_role(role)
    validate_read_policy(read_policy)
    manifest_path, path_kind = normalize_manifest_path(path, repo_root)
    return {
        "path": manifest_path,
        "path_kind": path_kind,
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
        "role": role,
        "read_policy": read_policy,
        "fact_source_allowed": fact_source_allowed,
    }


def write_input_refs(
    run_dir: Path | str,
    payload: dict[str, Any],
    *,
    overwrite: bool = False,
) -> Path:
    validate_input_refs(payload)
    path = input_refs_path(run_dir)
    if path.exists() and not overwrite:
        raise InputRefsError(f"input_refs already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def validate_input_refs(
    payload: dict[str, Any],
    *,
    repo_root: Path | str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InputRefsError("input_refs payload must be a JSON object")
    reject_body_like_keys(payload)
    validate_exact_fields(payload, INPUT_REFS_FIELDS)
    validate_literal(payload["schema_version"], SCHEMA_VERSION, "schema_version")
    validate_literal(payload["created_by"], CREATED_BY, "created_by")
    validate_run_id(payload["run_id"])
    validate_constraints(payload["constraints"])

    repo = Path(repo_root).expanduser().resolve() if repo_root is not None else None
    validate_task_ref(payload["task_ref"], repo)
    validate_materials(payload["input_materials"], repo)
    validate_warnings(payload["warnings"])
    return payload


def validate_task_ref(value: Any, repo_root: Path | None) -> None:
    if not isinstance(value, dict):
        raise InputRefsError("task_ref must be an object")
    validate_exact_fields(value, TASK_REF_FIELDS)
    validate_literal(value["role"], "task", "task_ref.role")
    validate_literal(value["read_policy"], "metadata_only", "task_ref.read_policy")
    validate_literal(value["fact_source_allowed"], False, "task_ref.fact_source_allowed")
    validate_file_ref(value, repo_root, "task_ref")


def validate_materials(value: Any, repo_root: Path | None) -> None:
    if not isinstance(value, list):
        raise InputRefsError("input_materials must be a list")
    seen_ids: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise InputRefsError("input_materials entries must be objects")
        validate_exact_fields(item, MATERIAL_FIELDS)
        material_id = item["material_id"]
        if not isinstance(material_id, str) or not material_id:
            raise InputRefsError("material_id must be a non-empty string")
        if material_id in seen_ids:
            raise InputRefsError(f"duplicate material_id: {material_id}")
        seen_ids.add(material_id)
        validate_role(item["role"])
        validate_read_policy(item["read_policy"])
        if item["selected_by"] != "task":
            raise InputRefsError("selected_by must be task")
        if not isinstance(item["mime_type"], str) or not item["mime_type"]:
            raise InputRefsError("mime_type must be a non-empty string")
        if is_sample_like_path(item["path"]) and item["fact_source_allowed"] is True:
            raise InputRefsError(
                "sample/example/expected-output paths cannot be fact_source_allowed=true"
            )
        if item["role"] == "sample" and item["fact_source_allowed"] is True:
            raise InputRefsError("sample materials cannot be fact_source_allowed=true")
        validate_file_ref(item, repo_root, f"input_materials.{material_id}")


def validate_file_ref(value: dict[str, Any], repo_root: Path | None, field: str) -> None:
    path = require_string(value.get("path"), f"{field}.path")
    path_kind = require_string(value.get("path_kind"), f"{field}.path_kind")
    if path_kind not in ALLOWED_PATH_KINDS:
        raise InputRefsError(f"{field}.path_kind is not allowed: {path_kind!r}")
    validate_manifest_path(path, path_kind, field)
    digest = require_string(value.get("sha256"), f"{field}.sha256")
    if not SHA256_RE.match(digest):
        raise InputRefsError(f"invalid sha256 for {path}")
    size = value.get("size_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise InputRefsError(f"{field}.size_bytes must be a non-negative integer")
    if not isinstance(value.get("fact_source_allowed"), bool):
        raise InputRefsError(f"{field}.fact_source_allowed must be true or false")

    candidate = resolve_manifest_path(path, path_kind, repo_root)
    if candidate is None:
        return
    if not candidate.is_file():
        raise InputRefsError(f"{field} path does not exist: {path}")
    if candidate.stat().st_size != size:
        raise InputRefsError(f"size_bytes mismatch for {path}")
    actual_digest = file_sha256(candidate)
    if actual_digest != digest:
        raise InputRefsError(f"sha256 mismatch for {path}")


def validate_manifest_path(path: str, path_kind: str, field: str) -> None:
    if GLOB_CHARS_RE.search(path):
        raise InputRefsError(f"glob patterns are not allowed in {field}.path: {path!r}")
    if "\\" in path:
        raise InputRefsError(f"{field}.path must use POSIX separators: {path!r}")
    if path_kind == "repo_relative":
        validate_posix_relative_path(path, field)
    elif path_kind == "external":
        if not Path(path).is_absolute():
            raise InputRefsError(f"{field}.path must be absolute for external refs")


def validate_declared_path(path: str) -> None:
    if not path:
        raise InputRefsError("input material path must be non-empty")
    if GLOB_CHARS_RE.search(path):
        raise InputRefsError(f"glob patterns are not allowed in input path: {path!r}")
    if "\\" in path:
        raise InputRefsError(f"input material path must use POSIX separators: {path!r}")
    if not Path(path).is_absolute():
        validate_posix_relative_path(path, "input material")


def validate_posix_relative_path(path: str, field: str) -> None:
    if not path or path.startswith("/") or path.startswith("~"):
        raise InputRefsError(f"{field}.path must be a relative POSIX path: {path!r}")
    parts = PurePosixPath(path).parts
    if any(part == ".." for part in parts):
        raise InputRefsError(f"{field}.path must not contain '..': {path!r}")
    if any(part in {"", "."} for part in parts):
        raise InputRefsError(f"{field}.path must not contain empty or dot parts: {path!r}")


def resolve_declared_path(path: str, task_dir: Path) -> Path:
    raw = Path(path)
    if raw.is_absolute():
        return raw.expanduser().resolve()
    return (task_dir / path).resolve()


def normalize_manifest_path(path: Path, repo_root: Path | None) -> tuple[str, str]:
    resolved = path.expanduser().resolve()
    if repo_root is not None and resolved.is_relative_to(repo_root):
        return resolved.relative_to(repo_root).as_posix(), "repo_relative"
    return str(resolved), "external"


def resolve_manifest_path(
    path: str,
    path_kind: str,
    repo_root: Path | None,
) -> Path | None:
    if path_kind == "external":
        return Path(path).expanduser().resolve()
    if repo_root is None:
        return None
    candidate = (repo_root / path).resolve()
    if not candidate.is_relative_to(repo_root):
        raise InputRefsError(f"repo_relative path escapes repo_root: {path}")
    return candidate


def material_read_policy(raw_value: Any, role: str, sample_like: bool) -> str:
    if raw_value is not None:
        read_policy = require_string(raw_value, "read_policy")
        validate_read_policy(read_policy)
    elif role == "source" and not sample_like:
        read_policy = "allowed"
    elif role in {"template", "profile", "rubric", "instruction", "reference"}:
        read_policy = "summary_only"
    else:
        read_policy = "summary_only"
    if sample_like and read_policy == "allowed":
        return "summary_only"
    return read_policy


def material_fact_source_allowed(raw_value: Any, role: str, sample_like: bool) -> bool:
    if raw_value is not None and not isinstance(raw_value, bool):
        raise InputRefsError("fact_source_allowed must be true or false")
    if sample_like:
        return False
    if raw_value is not None:
        return bool(raw_value) and role == "source"
    return role == "source"


def is_sample_like_path(path: str) -> bool:
    normalized_parts = {part.lower() for part in PurePosixPath(path).parts}
    return bool(normalized_parts & SAMPLE_PATH_MARKERS)


def guess_mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "text/markdown"
    if suffix == ".txt":
        return "text/plain"
    if suffix in {".yaml", ".yml"}:
        return "application/x-yaml"
    if suffix == ".json":
        return "application/json"
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or "application/octet-stream"


def reject_body_like_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if isinstance(key, str) and key.lower() in BODY_LIKE_KEYS:
                raise InputRefsError(f"body-like field is not allowed: {key}")
            reject_body_like_keys(nested)
    elif isinstance(value, list):
        for item in value:
            reject_body_like_keys(item)


def validate_constraints(value: Any) -> None:
    if not isinstance(value, dict):
        raise InputRefsError("constraints must be an object")
    validate_exact_fields(value, CONSTRAINT_FIELDS)
    for key in CONSTRAINT_FIELDS:
        if value[key] is not True:
            raise InputRefsError(f"constraints.{key} must be true")


def validate_warnings(value: Any) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise InputRefsError("warnings must be a list of strings")


def validate_role(value: Any) -> None:
    if not isinstance(value, str) or value not in ALLOWED_ROLES:
        raise InputRefsError(f"role is not allowed: {value!r}")


def validate_read_policy(value: Any) -> None:
    if not isinstance(value, str) or value not in ALLOWED_READ_POLICIES:
        raise InputRefsError(f"read_policy is not allowed: {value!r}")


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise InputRefsError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise InputRefsError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise InputRefsError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise InputRefsError("run_id must be a safe non-empty run id")


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise InputRefsError(f"{field} must be a non-empty string")
    return value


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
