from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .profile_loader import (
    DocumentProfile,
    DocumentProfileValidationError,
    load_document_profile_file,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCUMENT_PROFILE_BLOCK = re.compile(
    r"^```yaml[ \t]+document_profile[ \t]*\r?\n(?P<body>.*?)^```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
METADATA_TASK_TYPE = re.compile(r"^Target task_type:\s*(?P<task_type>[A-Za-z0-9_.-]+)\s*$", re.MULTILINE)

REQUIRED_PROFILE_FIELDS = (
    "profile_id",
    "profile_version",
    "task_type",
    "display_name",
    "description",
    "default_sections",
    "required_sections",
    "optional_sections",
    "critical_claims",
    "requires_human_confirmation",
    "forbidden_final_claims",
    "confirmation_marker",
    "fact_source_roles",
    "non_fact_source_roles",
    "reference_policy",
    "sample_policy",
    "default_final_status",
    "allowed_final_statuses",
    "review_focus",
    "verification_focus",
    "candidate_learning_policy",
    "terminology",
    "output_labels",
)

APPROVAL_LIKE_STATUSES = {
    "approved",
    "validated",
    "compliant",
    "production_ready",
    "production ready",
    "risk_accepted",
    "risk accepted",
}

REFERENCE_FACT_ALLOW_PHRASES = (
    "reference materials may prove",
    "reference materials can prove",
    "reference may prove",
    "reference can prove",
    "reference inputs may prove",
    "reference inputs can prove",
    "reference materials are fact sources",
    "reference is a fact source",
    "reference can be used as fact",
    "reference may be used as fact",
)

SAMPLE_FACT_ALLOW_PHRASES = (
    "sample documents may prove",
    "sample documents can prove",
    "sample may prove",
    "sample can prove",
    "sample inputs may prove",
    "sample inputs can prove",
    "sample documents are fact sources",
    "sample is a fact source",
    "sample can be used as fact",
    "sample may be used as fact",
)


@dataclass(frozen=True)
class ProfileFromSpecResult:
    success: bool
    output_dir: Path
    manifest: dict[str, Any]
    promotion_blockers: list[str] = field(default_factory=list)


def generate_profile_from_spec(
    spec_path: Path | str,
    output_dir: Path | str,
    *,
    force: bool = False,
    dry_run: bool = False,
    no_skeletons: bool = False,
) -> ProfileFromSpecResult:
    spec = Path(spec_path)
    output = Path(output_dir)
    blockers: list[str] = []
    profile_data: dict[str, Any] | None = None

    unsafe_output = validate_output_dir(output)
    if unsafe_output:
        return failed_result(spec, output, [unsafe_output], dry_run=True)

    try:
        spec_text = spec.read_text(encoding="utf-8")
    except FileNotFoundError:
        return write_failure_manifest(spec, output, [f"spec file not found: {spec}"], dry_run=dry_run, force=force)
    except UnicodeDecodeError as exc:
        return write_failure_manifest(spec, output, [f"spec encoding error: {exc}"], dry_run=dry_run, force=force)

    blocks = DOCUMENT_PROFILE_BLOCK.findall(spec_text)
    if not blocks:
        return write_failure_manifest(
            spec,
            output,
            ["document_profile YAML block not found; use docs/DOCUMENT_PROFILE_SPEC_TEMPLATE.md"],
            dry_run=dry_run,
            force=force,
        )
    if len(blocks) > 1:
        return write_failure_manifest(
            spec,
            output,
            ["multiple document_profile YAML blocks found; keep exactly one block and request human review"],
            dry_run=dry_run,
            force=force,
        )

    try:
        loaded_yaml = yaml.safe_load(blocks[0])
    except yaml.YAMLError as exc:
        return write_failure_manifest(spec, output, [f"document_profile YAML parse error: {exc}"], dry_run=dry_run, force=force)
    if not isinstance(loaded_yaml, dict):
        return write_failure_manifest(spec, output, ["document_profile block root must be a mapping"], dry_run=dry_run, force=force)
    profile_data = dict(loaded_yaml)

    blockers.extend(validate_required_fields(profile_data))
    blockers.extend(validate_metadata_task_type(spec_text, profile_data))
    blockers.extend(validate_n3_policy_boundaries(profile_data))

    if blockers:
        return write_failure_manifest(spec, output, blockers, profile_data=profile_data, dry_run=dry_run, force=force)

    try:
        DocumentProfile.model_validate(profile_data)
    except ValidationError as exc:
        errors = [f"N2 document_profile validation failed: {error['loc']}: {error['msg']}" for error in exc.errors()]
        return write_failure_manifest(spec, output, errors, profile_data=profile_data, dry_run=dry_run, force=force)

    if dry_run:
        manifest = build_manifest(
            spec,
            output,
            profile_data=profile_data,
            validation_status="passed",
            promotion_blockers=[],
        )
        return ProfileFromSpecResult(success=True, output_dir=output, manifest=manifest, promotion_blockers=[])

    prepare_output_dir(output, force=force)
    profile_path = output / "document_profile.yaml"
    profile_path.write_text(yaml.safe_dump(profile_data, allow_unicode=True, sort_keys=False), encoding="utf-8")

    try:
        loaded = load_document_profile_file(profile_path, profile_path=profile_path.as_posix(), expected_task_type=profile_data["task_type"])
    except DocumentProfileValidationError as exc:
        try:
            profile_path.unlink()
        except FileNotFoundError:
            pass
        return write_failure_manifest(
            spec,
            output,
            [f"N2 document_profile validation failed: {error}" for error in exc.errors],
            profile_data=profile_data,
            dry_run=False,
            force=True,
        )

    manifest = build_manifest(
        spec,
        output,
        profile_data=loaded.profile.model_dump(),
        validation_status="passed",
        promotion_blockers=[],
    )
    write_json(output / "candidate_manifest.json", manifest)
    write_readme(output, loaded.profile.model_dump())
    if not no_skeletons:
        write_fixture_skeleton(output, loaded.profile.model_dump())
        write_eval_skeleton(output, loaded.profile.model_dump())
    return ProfileFromSpecResult(success=True, output_dir=output, manifest=manifest, promotion_blockers=[])


def validate_required_fields(profile_data: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field_name in REQUIRED_PROFILE_FIELDS:
        if field_name not in profile_data:
            blockers.append(f"{field_name} is required in document_profile block")
    return blockers


def validate_metadata_task_type(spec_text: str, profile_data: dict[str, Any]) -> list[str]:
    match = METADATA_TASK_TYPE.search(spec_text)
    if not match:
        return []
    metadata_task_type = match.group("task_type").strip()
    profile_task_type = profile_data.get("task_type")
    if isinstance(profile_task_type, str) and profile_task_type.strip() == metadata_task_type:
        return []
    return [f"task_type metadata mismatch: spec={metadata_task_type} profile={profile_task_type}"]


def validate_n3_policy_boundaries(profile_data: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    default_status = normalize_string(profile_data.get("default_final_status"))
    allowed_statuses = profile_data.get("allowed_final_statuses")

    if default_status in APPROVAL_LIKE_STATUSES:
        blockers.append(f"final status is approval-like and unsafe: {default_status}")
    if isinstance(allowed_statuses, list):
        for status in allowed_statuses:
            normalized = normalize_string(status)
            if normalized in APPROVAL_LIKE_STATUSES:
                blockers.append(f"allowed final status is approval-like and unsafe: {normalized}")
    else:
        blockers.append("allowed_final_statuses is required and must be a list")

    reference_policy = normalize_string(profile_data.get("reference_policy"))
    if any(phrase in reference_policy for phrase in REFERENCE_FACT_ALLOW_PHRASES):
        blockers.append("reference_policy must not allow reference materials to prove project-specific facts")

    sample_policy = normalize_string(profile_data.get("sample_policy"))
    if any(phrase in sample_policy for phrase in SAMPLE_FACT_ALLOW_PHRASES):
        blockers.append("sample_policy must not allow sample documents to prove project-specific facts")

    return blockers


def validate_output_dir(output_dir: Path) -> str | None:
    try:
        resolved = output_dir.resolve()
        repo_root = REPO_ROOT.resolve()
    except OSError as exc:
        return f"unsafe output path: {exc}"

    if resolved == repo_root:
        return "unsafe output path: repository root is not a candidate output directory"
    if output_dir.suffix.lower() in {".yaml", ".yml", ".py", ".md"}:
        if is_relative_to(resolved, repo_root / "profiles" / "document_types"):
            return "active profile output path is unsafe"
        return "unsafe output path: output-dir must be a directory, not a product file"
    if is_relative_to(resolved, repo_root / "profiles" / "document_types"):
        return "active profile output path is unsafe"
    for protected in ["skills", "ai_writing_plugin", "commands", "examples"]:
        if is_relative_to(resolved, repo_root / protected):
            return f"unsafe output path: cannot write candidate package under {protected}/"
    if is_relative_to(resolved, repo_root / "docs" / "archive"):
        return "unsafe output path: cannot write candidate package under docs/archive/"
    return None


def write_failure_manifest(
    spec_path: Path,
    output_dir: Path,
    blockers: list[str],
    *,
    profile_data: dict[str, Any] | None = None,
    dry_run: bool,
    force: bool,
) -> ProfileFromSpecResult:
    if dry_run:
        return failed_result(spec_path, output_dir, blockers, profile_data=profile_data, dry_run=True)
    prepare_output_dir(output_dir, force=force)
    result = failed_result(spec_path, output_dir, blockers, profile_data=profile_data, dry_run=False)
    write_json(output_dir / "candidate_manifest.json", result.manifest)
    return result


def failed_result(
    spec_path: Path,
    output_dir: Path,
    blockers: list[str],
    *,
    profile_data: dict[str, Any] | None = None,
    dry_run: bool,
) -> ProfileFromSpecResult:
    manifest = build_manifest(
        spec_path,
        output_dir,
        profile_data=profile_data or {},
        validation_status="failed",
        promotion_blockers=blockers,
    )
    if dry_run:
        manifest["dry_run"] = True
    return ProfileFromSpecResult(success=False, output_dir=output_dir, manifest=manifest, promotion_blockers=blockers)


def build_manifest(
    spec_path: Path,
    output_dir: Path,
    *,
    profile_data: dict[str, Any],
    validation_status: str,
    promotion_blockers: list[str],
) -> dict[str, Any]:
    return {
        "phase": "N3",
        "status": "candidate",
        "activation_status": "inactive",
        "source_spec_path": str(spec_path),
        "generated_profile_path": str(output_dir / "document_profile.yaml"),
        "validation_status": validation_status,
        "profile_task_type": profile_data.get("task_type", ""),
        "profile_id": profile_data.get("profile_id", ""),
        "profile_version": profile_data.get("profile_version", ""),
        "promotion_blockers": promotion_blockers,
        "human_review_required": True,
        "may_overwrite_active_profile": False,
        "may_modify_stable_skill": False,
    }


def prepare_output_dir(output_dir: Path, *, force: bool) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"output-dir must be a directory: {output_dir}")
    if output_dir.exists() and any(output_dir.iterdir()) and not force:
        raise ValueError(f"output-dir is not empty; pass --force to overwrite candidate files: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_readme(output_dir: Path, profile_data: dict[str, Any]) -> None:
    readme = f"""# Candidate Document Profile Package

Status: candidate
Activation status: inactive
Profile task type: {profile_data["task_type"]}
Profile id: {profile_data["profile_id"]}
Profile version: {profile_data["profile_version"]}

This package was generated by Phase N3 from a Markdown Spec. It is not an active profile and must not be copied into `profiles/document_types/` without human review and a future explicit promotion process.

Human review is required before using this profile for a real writing task. The generated fixture skeleton contains placeholders only and must be replaced with project-specific source material.
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")


def write_fixture_skeleton(output_dir: Path, profile_data: dict[str, Any]) -> None:
    fixture_dir = output_dir / "fixture_skeleton"
    inputs_dir = fixture_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    task = {
        "task_type": profile_data["task_type"],
        "task_title": f"{profile_data['display_name']} demo fixture skeleton",
        "display_name": profile_data["display_name"],
        "document_profile_path": "../document_profile.yaml",
        "target_audience": "TODO: replace with intended reviewer audience",
        "output_format": "markdown",
        "strict_template": True,
        "allow_inference": False,
        "requires_human_confirmation": list(profile_data["requires_human_confirmation"]),
        "inputs": [
            {"path": "inputs/source.md", "role": "source", "title": "TODO source material"},
            {"path": "inputs/template.md", "role": "template", "title": "TODO template"},
            {"path": "inputs/checklist.md", "role": "checklist", "title": "TODO checklist"},
            {"path": "inputs/reference.md", "role": "reference", "title": "TODO reference"},
            {"path": "inputs/sample.md", "role": "sample", "title": "TODO sample"},
        ],
    }
    (fixture_dir / "task.yaml").write_text(yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (inputs_dir / "source.md").write_text(
        "# TODO Source Material\n\nThis is a skeleton. Replace with project-specific source material before running.\n",
        encoding="utf-8",
    )
    (inputs_dir / "template.md").write_text(
        "# TODO Template\n\nThis is a skeleton. Replace with the document template before running.\n",
        encoding="utf-8",
    )
    (inputs_dir / "checklist.md").write_text(
        "# TODO Checklist\n\nThis is a skeleton. Replace with review checklist items before running.\n",
        encoding="utf-8",
    )
    (inputs_dir / "reference.md").write_text(
        "# TODO Reference\n\nThis is a skeleton. Reference material does not prove project facts.\n",
        encoding="utf-8",
    )
    (inputs_dir / "sample.md").write_text(
        "# TODO Sample\n\nThis is a skeleton. The sample is not a fact source and must only guide structure or style.\n",
        encoding="utf-8",
    )


def write_eval_skeleton(output_dir: Path, profile_data: dict[str, Any]) -> None:
    eval_dir = output_dir / "eval_skeleton"
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "README.md").write_text(
        "# Smoke-Test Guidance\n\nThis directory is guidance only. It is not an N6 eval harness.\n",
        encoding="utf-8",
    )
    smoke_plan = f"""# Candidate Profile Smoke-Test Plan

This guidance is for `{profile_data["task_type"]}` candidate profile review only. It does not create an eval runner or an `ai_writing_plugin/eval/` framework.

- Confirm the candidate profile loads through the N2 document profile loader.
- Confirm sample inputs are not treated as fact sources.
- Confirm reference inputs do not prove project facts.
- Confirm unsupported critical claims retain NEEDS_USER_CONFIRMATION.
- Confirm final status remains non-approval.
- Confirm candidate updates remain inactive.
- Confirm no cross-document terminology leakage appears.
- Replace fixture TODO content before attempting a full demo run.
"""
    (eval_dir / "smoke_test_plan.md").write_text(smoke_plan, encoding="utf-8")


def normalize_string(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
        return True
    except ValueError:
        return False
