from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .short_results import (
    RUN_ID_RE,
    SHA256_RE,
    STAGES,
    ShortResultError,
    validate_result_path,
    validate_stage,
)


INDEX_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "issue_count",
    "blocking_issues_count",
    "severity_counts",
    "issues",
}
INDEX_ITEM_FIELDS = {"issue_id", "severity", "category", "short_title", "issue_ref"}
DETAIL_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "issue_id",
    "severity",
    "category",
    "title",
    "summary",
    "location_refs",
    "artifact_refs",
    "recommendation",
    "rationale",
}
SUMMARY_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "issue_count",
    "blocking_issues_count",
    "returned_issue_count",
    "limit",
    "issues",
}
REF_FIELDS = {"path", "sha256"}
SOURCE_FIELDS = {"issues"}
SOURCE_ISSUE_FIELDS = {
    "issue_id",
    "severity",
    "category",
    "title",
    "summary",
    "location_refs",
    "artifact_refs",
    "recommendation",
    "rationale",
}
SEVERITIES = {"P0", "P1", "P2", "P3", "info"}
SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "info": 4}
BLOCKING_SEVERITIES = {"P0", "P1"}
ISSUE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,79}$")
BODY_LIKE_FIELDS = {
    "artifact_body",
    "artifact_text",
    "body",
    "content",
    "description",
    "detail",
    "evidence_body",
    "evidence_text",
    "excerpt",
    "full_text",
    "issues_body",
    "markdown",
    "recommendation_long_text",
    "review_units_body",
}
ACTIVE_METADATA_SINGLE_REF_FIELDS = {
    "context_package_ref",
    "decision_ref",
    "progress_ledger_ref",
    "review_result_ref",
    "step_result_ref",
}
ACTIVE_METADATA_REF_LIST_FIELDS = {
    "context_package_refs",
    "review_result_refs",
    "step_result_refs",
}


class StageReviewIssueError(ValueError):
    """Raised when stage review issue index or detail metadata is invalid."""


def issues_index_path(run_dir: Path | str, stage: str) -> Path:
    return Path(run_dir) / "stage_reviews" / stage / "issues_index.json"


def issue_detail_path(run_dir: Path | str, stage: str, issue_id: str) -> Path:
    validate_issue_id(issue_id)
    return Path(run_dir) / "stage_reviews" / stage / "issues" / f"{issue_id}.json"


def build_issues_index(
    run_dir: Path | str,
    stage: str,
    issues: list[dict[str, Any]] | None = None,
    source_path: Path | str | None = None,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    run_root = Path(run_dir).expanduser().resolve()
    validate_stage_or_raise(stage)
    run_id = run_root.name
    validate_run_id(run_id)

    existing_paths = current_issue_set_paths(run_root, stage)
    if existing_paths and not overwrite:
        raise StageReviewIssueError(
            f"stage review issue output already exists: {issues_index_path(run_root, stage)}"
        )
    if existing_paths:
        reject_active_issue_refs(run_root, existing_paths)

    source_issues = (
        load_source_issues(run_root, source_path)
        if issues is None
        else issues
    )
    if not isinstance(source_issues, list):
        raise StageReviewIssueError("issues must be a list")

    index_items: list[dict[str, Any]] = []
    detail_payloads: dict[str, dict[str, Any]] = {}
    candidate_files: dict[Path, bytes] = {}
    for raw_issue in source_issues:
        if not isinstance(raw_issue, dict):
            raise StageReviewIssueError("issue entries must be objects")
        detail_payload = build_issue_detail_payload(raw_issue, run_id=run_id, stage=stage)
        validate_issue_detail(detail_payload, run_dir=run_root)
        detail_path = issue_detail_path(run_root, stage, detail_payload["issue_id"])
        detail_bytes = encode_json(detail_payload)
        detail_payloads[detail_payload["issue_id"]] = detail_payload
        candidate_files[detail_path] = detail_bytes
        index_items.append(
            {
                "issue_id": detail_payload["issue_id"],
                "severity": detail_payload["severity"],
                "category": detail_payload["category"],
                "short_title": coerce_short_text(
                    raw_issue.get("short_title")
                    or raw_issue.get("title")
                    or raw_issue.get("summary")
                    or detail_payload["issue_id"],
                    "short_title",
                    160,
                ),
                "issue_ref": {
                    "path": detail_path.relative_to(run_root).as_posix(),
                    "sha256": hashlib.sha256(detail_bytes).hexdigest(),
                },
            }
        )

    payload: dict[str, Any] = {
        "kind": "stage_review_issues_index",
        "schema_version": 1,
        "run_id": run_id,
        "stage": stage,
        "issue_count": len(index_items),
        "blocking_issues_count": count_blocking(index_items),
        "severity_counts": count_severities(index_items),
        "issues": index_items,
    }
    validate_candidate_issue_set(payload, detail_payloads, run_root)
    candidate_files[issues_index_path(run_root, stage)] = encode_json(payload)

    snapshot = snapshot_issue_set(run_root, stage)
    try:
        replace_issue_set(run_root, stage, candidate_files)
        validate_issues_index(payload, run_dir=run_root)
    except Exception as exc:
        try:
            restore_issue_set(run_root, stage, snapshot)
        except OSError as rollback_exc:
            raise StageReviewIssueError(
                f"failed to update stage review issues and rollback failed: {rollback_exc}"
            ) from exc
        if isinstance(exc, StageReviewIssueError):
            raise
        raise StageReviewIssueError(f"failed to update stage review issues: {exc}") from exc
    return payload


def validate_issues_index_file(
    run_dir: Path | str,
    path_value: Path | str,
) -> dict[str, Any]:
    run_root = Path(run_dir).expanduser().resolve()
    relative_path, absolute_path = normalize_run_path(run_root, path_value)
    if not absolute_path.is_file():
        raise StageReviewIssueError(f"issues index does not exist: {relative_path}")
    payload = validate_issues_index(load_json(absolute_path), run_dir=run_root)
    expected_path = issues_index_path(run_root, payload["stage"]).relative_to(run_root).as_posix()
    if relative_path != expected_path:
        raise StageReviewIssueError("issues index path must match its stage")
    return payload


def validate_issues_index(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
    *,
    validate_artifact_refs: bool = True,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StageReviewIssueError("issues index payload must be a JSON object")
    reject_body_like_fields(payload)
    validate_exact_fields(payload, INDEX_FIELDS)
    validate_literal(payload["kind"], "stage_review_issues_index", "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_stage_or_raise(payload["stage"])
    issues = validate_issue_items(payload["issues"], payload["stage"])
    validate_non_negative_int(payload["issue_count"], "issue_count")
    validate_non_negative_int(payload["blocking_issues_count"], "blocking_issues_count")
    if payload["issue_count"] != len(issues):
        raise StageReviewIssueError("issue_count must match issues length")
    expected_blocking = count_blocking(issues)
    if payload["blocking_issues_count"] != expected_blocking:
        raise StageReviewIssueError("blocking_issues_count must match P0/P1 issues")
    expected_severity_counts = count_severities(issues)
    if payload["severity_counts"] != expected_severity_counts:
        raise StageReviewIssueError("severity_counts must match issues")

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise StageReviewIssueError("run_id must match run_dir name")
        for item in issues:
            detail_path = validate_ref_file(item["issue_ref"], run_root)
            detail_payload = validate_issue_detail(
                load_json(detail_path),
                run_dir=run_root if validate_artifact_refs else None,
            )
            if (
                detail_payload["run_id"] != payload["run_id"]
                or detail_payload["stage"] != payload["stage"]
                or detail_payload["issue_id"] != item["issue_id"]
            ):
                raise StageReviewIssueError("issue detail must match index item")

    return payload


def validate_issue_detail(
    payload: dict[str, Any],
    run_dir: Path | str | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise StageReviewIssueError("issue detail payload must be a JSON object")
    reject_body_like_fields(payload)
    validate_exact_fields(payload, DETAIL_FIELDS)
    validate_literal(payload["kind"], "stage_review_issue", "kind")
    validate_literal(payload["schema_version"], 1, "schema_version")
    validate_run_id(payload["run_id"])
    validate_stage_or_raise(payload["stage"])
    validate_issue_id(payload["issue_id"])
    validate_severity(payload["severity"])
    validate_short_string(payload["category"], "category", 80)
    validate_short_string(payload["title"], "title", 240)
    validate_short_string(payload["summary"], "summary", 600)
    validate_text_field(payload["recommendation"], "recommendation", 2000)
    validate_text_field(payload["rationale"], "rationale", 2000)
    validate_metadata_list(payload["location_refs"], "location_refs")
    artifact_refs = validate_ref_list(payload["artifact_refs"], "artifact_refs")

    if run_dir is not None:
        run_root = Path(run_dir).expanduser().resolve()
        if payload["run_id"] != run_root.name:
            raise StageReviewIssueError("run_id must match run_dir name")
        for artifact_ref in artifact_refs:
            validate_ref_file(artifact_ref, run_root)

    return payload


def summarize_issues_index(payload_or_path: dict[str, Any] | Path | str, limit: int = 5) -> dict[str, Any]:
    if isinstance(payload_or_path, dict):
        payload = payload_or_path
    else:
        payload = load_json(Path(payload_or_path))
    payload = validate_issues_index(payload)
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
        raise StageReviewIssueError("limit must be a non-negative integer")

    sorted_issues = sorted(
        enumerate(payload["issues"]),
        key=lambda pair: (SEVERITY_ORDER[pair[1]["severity"]], pair[0]),
    )
    selected = [dict(item) for _, item in sorted_issues[:limit]]
    summary = {
        "kind": "stage_review_issues_summary",
        "schema_version": 1,
        "run_id": payload["run_id"],
        "stage": payload["stage"],
        "issue_count": payload["issue_count"],
        "blocking_issues_count": payload["blocking_issues_count"],
        "returned_issue_count": len(selected),
        "limit": limit,
        "issues": selected,
    }
    validate_exact_fields(summary, SUMMARY_FIELDS)
    reject_body_like_fields(summary)
    return summary


def build_ref(run_dir: Path | str, path_value: Path | str) -> dict[str, str]:
    relative_path, absolute_path = normalize_run_path(Path(run_dir), path_value)
    if not absolute_path.is_file():
        raise StageReviewIssueError(f"ref path does not exist: {relative_path}")
    return {"path": relative_path, "sha256": file_sha256(absolute_path)}


def build_issue_detail_payload(
    raw_issue: dict[str, Any],
    *,
    run_id: str,
    stage: str,
) -> dict[str, Any]:
    issue_id = raw_issue.get("issue_id") or raw_issue.get("id")
    validate_issue_id(issue_id)
    severity = raw_issue.get("severity", "info")
    validate_severity(severity)
    category = coerce_short_text(raw_issue.get("category", "uncategorized"), "category", 80)
    title = coerce_short_text(
        raw_issue.get("title")
        or raw_issue.get("short_title")
        or raw_issue.get("summary")
        or issue_id,
        "title",
        240,
    )
    summary = coerce_short_text(raw_issue.get("summary") or title, "summary", 600)
    recommendation = coerce_text(raw_issue.get("recommendation", ""), "recommendation", 2000)
    rationale = coerce_text(
        raw_issue.get("rationale") or raw_issue.get("detail") or "",
        "rationale",
        2000,
    )
    location_refs = raw_issue.get("location_refs", [])
    artifact_refs = raw_issue.get("artifact_refs", [])

    payload = {
        "kind": "stage_review_issue",
        "schema_version": 1,
        "run_id": run_id,
        "stage": stage,
        "issue_id": issue_id,
        "severity": severity,
        "category": category,
        "title": title,
        "summary": summary,
        "location_refs": location_refs,
        "artifact_refs": artifact_refs,
        "recommendation": recommendation,
        "rationale": rationale,
    }
    reject_body_like_fields(payload)
    return payload


def load_source_issues(
    run_dir: Path,
    source_path: Path | str | None,
) -> list[dict[str, Any]]:
    if source_path is None:
        return []
    relative_path, absolute_path = normalize_run_path(run_dir, source_path)
    if not absolute_path.is_file():
        raise StageReviewIssueError(f"source issues path does not exist: {relative_path}")
    payload = load_json(absolute_path)
    validate_exact_fields(payload, SOURCE_FIELDS)
    issues = payload["issues"]
    if not isinstance(issues, list):
        raise StageReviewIssueError("source issues JSON must contain an issues list")
    seen_issue_ids: set[str] = set()
    for issue in issues:
        validate_public_source_issue(issue, run_dir)
        if issue["issue_id"] in seen_issue_ids:
            raise StageReviewIssueError("issues must not contain duplicate issue_id")
        seen_issue_ids.add(issue["issue_id"])
    return issues


def validate_public_source_issue(value: Any, run_dir: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StageReviewIssueError("issue entries must be objects")
    reject_body_like_fields(value)
    validate_exact_fields(value, SOURCE_ISSUE_FIELDS)
    validate_issue_id(value["issue_id"])
    validate_severity(value["severity"])
    validate_short_string(value["category"], "category", 80)
    validate_short_string(value["title"], "title", 240)
    validate_short_string(value["summary"], "summary", 600)
    validate_metadata_list(value["location_refs"], "location_refs")
    artifact_refs = validate_ref_list(value["artifact_refs"], "artifact_refs")
    for artifact_ref in artifact_refs:
        validate_ref_file(artifact_ref, run_dir)
    validate_text_field(value["recommendation"], "recommendation", 2000)
    validate_text_field(value["rationale"], "rationale", 2000)
    return value


def validate_issue_items(value: Any, stage: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise StageReviewIssueError("issues must be a list")
    issues: list[dict[str, Any]] = []
    seen_issue_ids: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise StageReviewIssueError("issues entries must be objects")
        reject_body_like_fields(item)
        validate_exact_fields(item, INDEX_ITEM_FIELDS)
        validate_issue_id(item["issue_id"])
        if item["issue_id"] in seen_issue_ids:
            raise StageReviewIssueError("issues must not contain duplicate issue_id")
        seen_issue_ids.add(item["issue_id"])
        validate_severity(item["severity"])
        validate_short_string(item["category"], "category", 80)
        validate_short_string(item["short_title"], "short_title", 160)
        issue_ref = validate_ref(item["issue_ref"], "issue_ref")
        expected_path = f"stage_reviews/{stage}/issues/{item['issue_id']}.json"
        if issue_ref["path"] != expected_path:
            raise StageReviewIssueError("issue_ref path must point to this issue detail")
        issues.append(
            {
                "issue_id": item["issue_id"],
                "severity": item["severity"],
                "category": item["category"],
                "short_title": item["short_title"],
                "issue_ref": issue_ref,
            }
        )
    return issues


def validate_ref_list(value: Any, field: str) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise StageReviewIssueError(f"{field} must be a list")
    refs = []
    seen_paths: set[str] = set()
    for item in value:
        ref = validate_ref(item, field)
        if ref["path"] in seen_paths:
            raise StageReviewIssueError(f"{field} must not contain duplicate paths")
        seen_paths.add(ref["path"])
        refs.append(ref)
    return refs


def validate_ref(value: Any, field: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise StageReviewIssueError(f"{field} must be an object")
    validate_exact_fields(value, REF_FIELDS)
    path = value["path"]
    digest = value["sha256"]
    if not isinstance(path, str):
        raise StageReviewIssueError(f"{field} path must be a string")
    validate_run_relative_path(path)
    if not isinstance(digest, str) or not SHA256_RE.match(digest):
        raise StageReviewIssueError(f"invalid sha256 for {path}")
    return {"path": path, "sha256": digest}


def validate_ref_file(ref: dict[str, str], run_dir: Path) -> Path:
    relative_path, absolute_path = normalize_run_path(run_dir, ref["path"])
    if relative_path != ref["path"]:
        raise StageReviewIssueError("ref path must be run-relative")
    if not absolute_path.is_file():
        raise StageReviewIssueError(f"ref path does not exist: {ref['path']}")
    digest = file_sha256(absolute_path)
    if digest != ref["sha256"]:
        raise StageReviewIssueError(f"sha256 mismatch for {ref['path']}")
    return absolute_path


def normalize_run_path(run_dir: Path, path_value: Path | str) -> tuple[str, Path]:
    root = run_dir.expanduser().resolve()
    raw_path = Path(path_value)
    if raw_path.is_absolute():
        absolute_path = raw_path.expanduser().resolve()
        if not absolute_path.is_relative_to(root):
            raise StageReviewIssueError(f"ref path escapes run_dir: {path_value}")
        relative_path = absolute_path.relative_to(root).as_posix()
    else:
        relative_path = str(path_value)
        validate_run_relative_path(relative_path)
        absolute_path = (root / relative_path).resolve()
        if not absolute_path.is_relative_to(root):
            raise StageReviewIssueError(f"ref path escapes run_dir: {relative_path}")
    validate_run_relative_path(relative_path)
    return relative_path, absolute_path


def current_issue_set_paths(run_dir: Path, stage: str) -> list[Path]:
    paths: list[Path] = []
    index_path = issues_index_path(run_dir, stage)
    if index_path.is_file():
        paths.append(index_path)
    details_dir = index_path.parent / "issues"
    if details_dir.exists():
        for candidate in sorted(details_dir.rglob("*")):
            if not candidate.is_file():
                raise StageReviewIssueError(
                    f"stage review issue output contains a non-file entry: {candidate}"
                )
            paths.append(candidate)
    return paths


def reject_active_issue_refs(run_dir: Path, issue_paths: list[Path]) -> None:
    target_paths = {path.relative_to(run_dir).as_posix() for path in issue_paths}
    metadata_paths: set[Path] = set()
    metadata_paths.update(
        path
        for path in (run_dir / "orchestration" / "context_packages").rglob("*.json")
        if path.is_file()
    )
    metadata_paths.update(
        path
        for path in (run_dir / "orchestration" / "review_context_packages").glob("*.json")
        if path.is_file()
    )
    ledger_path = run_dir / "orchestration" / "progress_ledger.json"
    if ledger_path.is_file():
        metadata_paths.add(ledger_path)
    metadata_paths.update(
        path
        for path in (run_dir / "stage_reviews").glob("*/decision.json")
        if path.is_file()
    )
    metadata_paths.update(
        path
        for path in (run_dir / "orchestration" / "stage_gate_results").glob("*.json")
        if path.is_file()
    )

    for metadata_path in sorted(metadata_paths):
        payload = load_json(metadata_path)
        referenced_path = find_active_issue_ref(
            payload,
            target_paths,
            run_dir,
            visited=set(),
        )
        if referenced_path is not None:
            metadata_relative = metadata_path.relative_to(run_dir).as_posix()
            raise StageReviewIssueError(
                "stage review issue output is still referenced by active metadata "
                f"{metadata_relative}: {referenced_path}"
            )


def find_active_issue_ref(
    payload: Any,
    target_paths: set[str],
    run_dir: Path,
    *,
    visited: set[str],
) -> str | None:
    direct_match = find_referenced_path(payload, target_paths)
    if direct_match is not None:
        return direct_match

    for ref in iter_active_metadata_refs(payload):
        relative_path = ref["path"]
        if relative_path in visited:
            continue
        visited.add(relative_path)
        absolute_path = validate_ref_file(ref, run_dir)
        nested_match = find_active_issue_ref(
            load_json(absolute_path),
            target_paths,
            run_dir,
            visited=visited,
        )
        if nested_match is not None:
            return nested_match
    return None


def iter_active_metadata_refs(value: Any):
    if isinstance(value, dict):
        for field, nested in value.items():
            if field in ACTIVE_METADATA_SINGLE_REF_FIELDS:
                if nested is not None:
                    yield validate_ref(nested, field)
            elif field in ACTIVE_METADATA_REF_LIST_FIELDS:
                if not isinstance(nested, list):
                    raise StageReviewIssueError(f"{field} must be a list")
                for item in nested:
                    yield validate_ref(item, field)
            else:
                yield from iter_active_metadata_refs(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from iter_active_metadata_refs(nested)


def find_referenced_path(value: Any, target_paths: set[str]) -> str | None:
    if isinstance(value, str):
        return value if value in target_paths else None
    if isinstance(value, list):
        for item in value:
            match = find_referenced_path(item, target_paths)
            if match is not None:
                return match
    elif isinstance(value, dict):
        for item in value.values():
            match = find_referenced_path(item, target_paths)
            if match is not None:
                return match
    return None


def validate_candidate_issue_set(
    index_payload: dict[str, Any],
    detail_payloads: dict[str, dict[str, Any]],
    run_dir: Path,
) -> None:
    validate_issues_index(index_payload)
    if len(detail_payloads) != index_payload["issue_count"]:
        raise StageReviewIssueError("issues must not contain duplicate issue_id")
    for item in index_payload["issues"]:
        detail_payload = detail_payloads.get(item["issue_id"])
        if detail_payload is None:
            raise StageReviewIssueError("issue detail must match index item")
        validate_issue_detail(detail_payload, run_dir=run_dir)
        detail_bytes = encode_json(detail_payload)
        if hashlib.sha256(detail_bytes).hexdigest() != item["issue_ref"]["sha256"]:
            raise StageReviewIssueError("issue detail sha256 must match index item")


def snapshot_issue_set(run_dir: Path, stage: str) -> dict[Path, bytes]:
    return {
        path.relative_to(run_dir): path.read_bytes()
        for path in current_issue_set_paths(run_dir, stage)
    }


def replace_issue_set(
    run_dir: Path,
    stage: str,
    candidate_files: dict[Path, bytes],
) -> None:
    stage_dir = issues_index_path(run_dir, stage).parent
    stage_dir.mkdir(parents=True, exist_ok=True)
    temporary_root = Path(tempfile.mkdtemp(prefix=".issues-build-", dir=stage_dir))
    try:
        staged_files: dict[Path, Path] = {}
        for destination, content in candidate_files.items():
            relative_to_stage = destination.relative_to(stage_dir)
            staged_path = temporary_root / relative_to_stage
            staged_path.parent.mkdir(parents=True, exist_ok=True)
            staged_path.write_bytes(content)
            staged_files[destination] = staged_path

        index_path = issues_index_path(run_dir, stage)
        detail_destinations = sorted(
            path for path in candidate_files if path != index_path
        )
        details_dir = index_path.parent / "issues"
        details_dir.mkdir(parents=True, exist_ok=True)
        for destination in detail_destinations:
            destination.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged_files[destination], destination)

        expected_details = set(detail_destinations)
        for existing_detail in sorted(details_dir.rglob("*"), reverse=True):
            if existing_detail.is_file() and existing_detail not in expected_details:
                existing_detail.unlink()
            elif existing_detail.is_dir() and not any(existing_detail.iterdir()):
                existing_detail.rmdir()

        os.replace(staged_files[index_path], index_path)
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)


def restore_issue_set(
    run_dir: Path,
    stage: str,
    snapshot: dict[Path, bytes],
) -> None:
    index_path = issues_index_path(run_dir, stage)
    details_dir = index_path.parent / "issues"
    if index_path.exists():
        index_path.unlink()
    if details_dir.exists():
        shutil.rmtree(details_dir)
    for relative_path, content in snapshot.items():
        destination = run_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)


def count_blocking(issues: list[dict[str, Any]]) -> int:
    return sum(1 for item in issues if item["severity"] in BLOCKING_SEVERITIES)


def count_severities(issues: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for severity in sorted(SEVERITIES, key=lambda value: SEVERITY_ORDER[value]):
        count = sum(1 for item in issues if item["severity"] == severity)
        if count:
            counts[severity] = count
    return counts


def validate_metadata_list(value: Any, field: str) -> None:
    if not isinstance(value, list):
        raise StageReviewIssueError(f"{field} must be a list")
    reject_body_like_fields(value)


def reject_body_like_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise StageReviewIssueError("JSON object keys must be strings")
            normalized_key = key.lower()
            if normalized_key in BODY_LIKE_FIELDS or normalized_key.endswith("_body"):
                raise StageReviewIssueError(f"body-like field is not allowed: {key}")
            reject_body_like_fields(nested)
    elif isinstance(value, list):
        for item in value:
            reject_body_like_fields(item)
    elif isinstance(value, str) and "```" in value:
        raise StageReviewIssueError("stage review issue metadata must not contain code fences")


def validate_exact_fields(payload: dict[str, Any], expected_fields: set[str]) -> None:
    actual = set(payload)
    extra = sorted(actual - expected_fields)
    if extra:
        raise StageReviewIssueError(f"unexpected fields: {extra}")
    missing = sorted(expected_fields - actual)
    if missing:
        raise StageReviewIssueError(f"missing required fields: {missing}")


def validate_literal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise StageReviewIssueError(f"{field} must be {expected!r}")


def validate_run_id(value: Any) -> None:
    if not isinstance(value, str) or not RUN_ID_RE.match(value) or ".." in value:
        raise StageReviewIssueError("run_id must be a safe non-empty run id")


def validate_stage_or_raise(value: Any) -> None:
    if not isinstance(value, str) or value not in STAGES:
        raise StageReviewIssueError(f"invalid stage: {value!r}")
    try:
        validate_stage(value)
    except ShortResultError as exc:
        raise StageReviewIssueError(str(exc)) from exc


def validate_issue_id(value: Any) -> None:
    if not isinstance(value, str) or not ISSUE_ID_RE.match(value) or ".." in value:
        raise StageReviewIssueError("issue_id must be a safe string of at most 80 characters")


def validate_severity(value: Any) -> None:
    if not isinstance(value, str) or value not in SEVERITIES:
        raise StageReviewIssueError(f"invalid severity: {value!r}")


def validate_non_negative_int(value: Any, field: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StageReviewIssueError(f"{field} must be a non-negative integer")


def validate_short_string(value: Any, field: str, max_length: int) -> None:
    if not isinstance(value, str) or not value.strip():
        raise StageReviewIssueError(f"{field} must be a non-empty string")
    if len(value) > max_length:
        raise StageReviewIssueError(f"{field} must be at most {max_length} characters")
    if "```" in value:
        raise StageReviewIssueError(f"{field} must not contain code fences")


def validate_text_field(value: Any, field: str, max_length: int) -> None:
    if not isinstance(value, str):
        raise StageReviewIssueError(f"{field} must be a string")
    if len(value) > max_length:
        raise StageReviewIssueError(f"{field} must be at most {max_length} characters")


def coerce_short_text(value: Any, field: str, max_length: int) -> str:
    text = coerce_text(value, field, max_length)
    if not text.strip():
        raise StageReviewIssueError(f"{field} must be a non-empty string")
    if len(text) > max_length:
        return text[: max_length - 3].rstrip() + "..."
    return text


def coerce_text(value: Any, field: str, max_length: int) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise StageReviewIssueError(f"{field} must be a string")
    if "```" in value:
        raise StageReviewIssueError(f"{field} must not contain code fences")
    if len(value) > max_length:
        return value[: max_length - 3].rstrip() + "..."
    return value.strip()


def validate_run_relative_path(path: str) -> None:
    try:
        validate_result_path(path)
    except ShortResultError as exc:
        raise StageReviewIssueError(str(exc)) from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise StageReviewIssueError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise StageReviewIssueError(f"JSON file must contain an object: {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_json(payload))


def encode_json(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
