from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .run_state import STAGE_ORDER, STAGE_REGISTRY, validate_output_path


EXCERPT_CHAR_LIMIT = 4000
STAGE_REVIEW_SCHEMA_VERSION = 1

STAGE_REVIEW_DECISIONS = {"accepted", "needs_revision", "blocked", "skipped"}
STAGE_REVIEW_PASSING_DECISIONS = {"accepted", "skipped"}
STAGE_REVIEW_DECISION_SCOPE = "stage_review_gate_only"
EXPECTED_DECISION_FIELDS = {
    "kind",
    "schema_version",
    "run_id",
    "stage",
    "decision",
    "decision_scope",
    "professional_approval",
    "allow_next_stage",
    "decided_by",
    "decision_source",
    "notes",
    "created_at",
    "validation_report_path",
    "issues_path",
    "validation_status_at_decision",
    "coverage_complete_at_decision",
    "validation_report_sha256",
    "issues_sha256",
}

ISSUE_STATUSES = {
    "no_issues",
    "issues_found",
    "blocked_needs_user_review",
    "invalid_review_result",
}
ISSUE_SEVERITIES = {"P0", "P1", "P2", "P3"}
ISSUE_CATEGORIES = {
    "artifact_quality",
    "schema_or_contract",
    "source_policy",
    "critical_claim",
    "hitl_required",
    "cross_type_leakage",
    "template_alignment",
    "checklist_alignment",
    "citation_or_evidence",
    "final_status_policy",
    "candidate_update_policy",
    "formatting",
    "other",
}
HIGH_RISK_CATEGORIES = {
    "source_policy",
    "critical_claim",
    "hitl_required",
    "citation_or_evidence",
    "final_status_policy",
    "candidate_update_policy",
}
ADVISORY_SAFE_FIX_WARNING = "safe_auto_fix_eligible is advisory only in S1; no patch applied."
REVIEW_UNIT_POLICY = {
    "coverage_required": True,
    "partial_review_allowed": False,
    "unknown_unit_id_allowed": False,
}

FORBIDDEN_APPROVAL_PHRASES = (
    "approved",
    "validated",
    "compliant",
    "approval",
    "professionally approved",
    "professional approval",
    "compliance approved",
    "safety approved",
    "production ready compliance",
    "approved for production",
    "ready for production",
)
FORBIDDEN_APPROVAL_STATUSES = {
    "approved",
    "validated",
    "compliant",
    "professionally_approved",
    "safety_approved",
}
SAMPLE_REFERENCE_FACT_CLAIMS = (
    "sample can be used as fact source",
    "sample can be used as a fact source",
    "sample is fact source",
    "sample is a fact source",
    "sample as fact source",
    "sample proves project fact",
    "sample proves a project fact",
    "reference proves project fact",
    "reference proves a project fact",
    "reference proves project-specific fact",
    "reference can prove project fact",
    "reference can prove a project fact",
    "reference is fact source",
    "reference is project-specific fact support",
)
STABLE_PROFILE_SKILL_ACTIONS = (
    "modify stable profile",
    "update stable profile",
    "overwrite stable profile",
    "modify stable skill",
    "update stable skill",
    "overwrite stable skill",
    "apply candidate profile",
    "activate candidate update",
)
NEEDS_CONFIRMATION_DELETE_ACTIONS = (
    "remove needs_user_confirmation",
    "delete needs_user_confirmation",
    "drop needs_user_confirmation",
    "remove the needs_user_confirmation",
    "delete the needs_user_confirmation",
)

FORBIDDEN_ACTIONS = [
    "do_not_add_project_facts",
    "do_not_treat_sample_as_fact_source",
    "do_not_remove_needs_user_confirmation",
    "do_not_write_professional_approval",
    "do_not_modify_artifacts",
]

EXPECTED_ISSUE_FIELDS = {
    "issue_id",
    "unit_id",
    "severity",
    "category",
    "title",
    "description",
    "related_artifacts",
    "related_sections",
    "requires_user_review",
    "requires_hitl",
    "safe_auto_fix_eligible",
    "recommendation",
    "proposed_action",
    "forbidden_auto_fix_reason",
}
EXPECTED_TOP_LEVEL_ISSUE_FIELDS = {
    "schema_version",
    "kind",
    "run_id",
    "stage",
    "reviewer",
    "status",
    "not_professional_approval",
    "reviewed_unit_ids",
    "unchecked_unit_ids",
    "issues",
}

STAGE_REQUIRED_CHECKS = {
    "ingest": [
        "material_role_boundary",
        "sample_not_fact_source",
        "reference_not_project_fact_source",
        "missing_or_unsupported_input",
    ],
    "outline": [
        "template_alignment",
        "missing_required_section",
        "scope_clarity",
        "no_irrelevant_document_type_leakage",
    ],
    "evidence": [
        "evidence_boundary",
        "source_support",
        "unsupported_critical_claim",
        "sample_not_fact_source",
        "reference_not_project_fact_source",
    ],
    "planning": [
        "citation_integrity",
        "forbidden_source_boundary",
        "critical_claim_confirmation_policy",
        "writing_task_clarity",
    ],
    "draft": [
        "evidence_boundary",
        "unsupported_critical_claim",
        "sample_not_fact_source",
        "reference_not_project_fact_source",
        "clarity",
        "open_items_visibility",
    ],
    "review": [
        "issue_specificity",
        "severity_consistency",
        "verification_boundary",
        "no_approval_semantics",
    ],
    "finalize": [
        "open_items_visibility",
        "final_status_boundary",
        "no_professional_approval",
        "critical_claim_pending_visibility",
    ],
    "learning": [
        "candidate_inactive",
        "no_stable_profile_modification",
        "no_stable_skill_modification",
        "no_professional_approval",
        "rollback_visibility",
    ],
}

STAGE_REVIEW_FOCUS = {
    "ingest": [
        "Check material role classification.",
        "Check source/sample/reference separation.",
        "Check missing materials are explicit.",
        "Check optional local reference folders are not required.",
    ],
    "outline": [
        "Check template coverage.",
        "Check required sections are represented.",
        "Check cross-document-type terminology leakage.",
        "Check the outline is not empty or perfunctory.",
    ],
    "evidence": [
        "Check research questions cover critical claims.",
        "Check evidence_map distinguishes supported, weak, and unsupported claims.",
        "Check sample is not used as fact evidence.",
        "Check reference does not prove project facts.",
    ],
    "planning": [
        "Check citation_plan only uses allowed evidence.",
        "Check section_tasks clearly forbid sample-derived facts.",
        "Check critical claim confirmation policy is preserved.",
        "Check unsupported claims are not planned as definitive conclusions.",
    ],
    "draft": [
        "Check the draft is readable and non-empty.",
        "Check critical claims preserve NEEDS_USER_CONFIRMATION where needed.",
        "Check source support is clear.",
        "Check sample/reference fact misuse is absent.",
        "Check approval wording is absent.",
    ],
    "review": [
        "Check review reports cover template, checklist, evidence, and final review concerns.",
        "Check verify_report failures are not ignored.",
        "Check P0/P1 issues are explicit.",
        "Check unconfirmed items remain visible.",
    ],
    "finalize": [
        "Check final_report explains inputs, outputs, limitations, and open items.",
        "Check delivery_summary is clear.",
        "Check final status is not professional approval.",
        "Check critical claims are not automatically confirmed.",
    ],
    "learning": [
        "Check candidate_profile_update remains proposed/inactive.",
        "Check candidate_skill_patch does not overwrite stable Skill files.",
        "Check promotion_report is not approval.",
        "Check rollback, evaluation, and human approval status are clear.",
    ],
}

STAGE_CONTEXT_ARTIFACTS = {
    "ingest": [],
    "outline": [
        "inputs/input_inventory.json",
        "knowledge/source_index.json",
        "knowledge/provenance_index.json",
        "knowledge/knowledge_gaps.md",
    ],
    "evidence": [
        "plans/template_structure.json",
        "plans/outline_l1.md",
        "knowledge/source_index.json",
        "knowledge/provenance_index.json",
    ],
    "planning": [
        "plans/research_questions.json",
        "plans/evidence_map.json",
        "plans/unresolved_questions.md",
        "knowledge/source_index.json",
        "knowledge/provenance_index.json",
    ],
    "draft": [
        "plans/citation_plan.json",
        "plans/claim_support_matrix.json",
        "plans/outline_final.md",
        "plans/section_tasks.json",
        "plans/writing_plan.md",
        "plans/evidence_map.json",
    ],
    "review": [
        "draft/full_draft.md",
        "plans/section_tasks.json",
        "plans/citation_plan.json",
        "plans/claim_support_matrix.json",
    ],
    "finalize": [
        "review/review_report.json",
        "review/template_review.md",
        "review/checklist_review.md",
        "review/evidence_review.md",
        "review/final_review.md",
        "verify/verify_report.json",
        "verify/failures.md",
    ],
    "learning": [
        "final/final_report.md",
        "final/delivery_summary.md",
        "verify/verify_report.json",
        "trace/hitl_decisions.jsonl",
    ],
}


class StageReviewError(Exception):
    """Raised when a stage review package or issue result is invalid."""


def prepare_stage_review(run_dir: str | Path, stage: str) -> dict[str, Any]:
    run_path = Path(run_dir)
    ensure_supported_stage(stage)
    ensure_run_dir(run_path)
    manifest = read_json_object(run_path / "manifest.json", "manifest")
    task_brief = read_json_object(run_path / "task_brief.json", "task_brief")
    run_id = validate_run_metadata(manifest, task_brief)
    state = read_optional_run_state(run_path)
    if state is not None:
        validate_run_state_for_stage(state, run_id, stage)

    stage_outputs = [
        summarize_artifact(run_path, relative_path, "stage_output", required=True)
        for relative_path in STAGE_REGISTRY[stage]["required_outputs"]
    ]
    context_artifacts = [
        summarize_artifact(run_path, relative_path, "upstream_context", required=False)
        for relative_path in STAGE_CONTEXT_ARTIFACTS[stage]
    ]

    review_dir = run_path / "stage_reviews" / stage
    review_dir.mkdir(parents=True, exist_ok=True)
    review_units = build_review_units(run_path, stage, run_id)
    expected_outputs = [
        f"stage_reviews/{stage}/claude_review.md",
        f"stage_reviews/{stage}/issues.json",
    ]
    context = {
        "schema_version": STAGE_REVIEW_SCHEMA_VERSION,
        "kind": "stage_review_context",
        "run_id": run_id,
        "stage": stage,
        "phase": STAGE_REGISTRY[stage]["phase"],
        "generated_at": utc_timestamp(),
        "status": "prepared_for_claude_review",
        "not_professional_approval": True,
        "run": {
            "manifest_path": "manifest.json",
            "task_brief_path": "task_brief.json",
            "run_state_path": "run_state.json" if state is not None else None,
            "task_type": task_brief.get("task_type"),
            "profile": task_brief.get("profile") or manifest.get("profile"),
        },
        "stage_outputs": stage_outputs,
        "context_artifacts": context_artifacts,
        "review_units_path": f"stage_reviews/{stage}/review_units.json",
        "review_unit_count": len(review_units["units"]),
        "review_unit_policy": REVIEW_UNIT_POLICY,
        "review_focus": STAGE_REVIEW_FOCUS[stage],
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "expected_outputs": expected_outputs,
    }
    issues_schema = build_issues_schema(stage)

    write_json(review_dir / "review_context.json", context)
    write_json(review_dir / "issues_schema.json", issues_schema)
    write_json(review_dir / "review_units.json", review_units)
    (review_dir / "review_prompt.md").write_text(render_review_prompt(context, issues_schema), encoding="utf-8")

    artifacts = [
        f"stage_reviews/{stage}/review_context.json",
        f"stage_reviews/{stage}/review_prompt.md",
        f"stage_reviews/{stage}/issues_schema.json",
        f"stage_reviews/{stage}/review_units.json",
    ]
    return {
        "run_id": run_id,
        "stage": stage,
        "status": "prepared_for_claude_review",
        "review_dir": f"stage_reviews/{stage}",
        "artifacts": artifacts,
    }


def validate_stage_review(run_dir: str | Path, stage: str, issues_file: str | Path | None = None) -> dict[str, Any]:
    run_path = Path(run_dir)
    ensure_supported_stage(stage)
    ensure_run_dir(run_path)
    manifest = read_json_object(run_path / "manifest.json", "manifest")
    task_brief = read_json_object(run_path / "task_brief.json", "task_brief")
    run_id = validate_run_metadata(manifest, task_brief)

    review_dir = run_path / "stage_reviews" / stage
    review_dir.mkdir(parents=True, exist_ok=True)
    issues_path = Path(issues_file) if issues_file is not None else review_dir / "issues.json"
    errors: list[str] = []
    issues_payload: dict[str, Any] | None = None
    issue_count = 0
    blocking_issue_count = 0
    coverage_summary = empty_coverage_summary()
    unit_validation = empty_unit_validation()

    try:
        loaded = json.loads(issues_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            issues_payload = loaded
        else:
            errors.append("issues.json root must be an object")
    except FileNotFoundError:
        errors.append(f"issues.json missing: {issues_path}")
    except UnicodeDecodeError as exc:
        errors.append(f"issues.json invalid encoding: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"issues.json invalid JSON: {exc}")

    if issues_payload is not None:
        payload_errors, issue_count, blocking_issue_count = validate_issues_payload(issues_payload, run_id, stage)
        errors.extend(payload_errors)
        coverage_errors, coverage_summary, unit_validation = validate_review_unit_coverage(run_path, stage, run_id, issues_payload)
        errors.extend(coverage_errors)
    else:
        unit_errors, required_unit_ids, _all_unit_ids = load_review_unit_ids(run_path, stage, run_id)
        errors.extend(unit_errors)
        coverage_summary["required_unit_count"] = len(required_unit_ids)

    report = {
        "schema_version": STAGE_REVIEW_SCHEMA_VERSION,
        "kind": "stage_review_validation_report",
        "run_id": run_id,
        "stage": stage,
        "status": "valid" if not errors else "invalid",
        "generated_at": utc_timestamp(),
        "not_professional_approval": True,
        "issue_count": issue_count,
        "blocking_issue_count": blocking_issue_count,
        "coverage_summary": coverage_summary,
        "unit_validation": unit_validation,
        "warnings": [ADVISORY_SAFE_FIX_WARNING],
        "errors": errors,
    }
    write_json(review_dir / "validation_report.json", report)
    if errors:
        raise StageReviewError("Stage review issues invalid: " + "; ".join(errors))
    return report


def record_stage_review_decision(
    run_dir: str | Path,
    stage: str,
    decision: str,
    notes: str = "",
    decided_by: str = "user",
) -> Path:
    run_path = Path(run_dir)
    ensure_supported_stage(stage)
    ensure_run_dir(run_path)
    run_id = load_run_id(run_path)
    if decision not in STAGE_REVIEW_DECISIONS:
        raise StageReviewError(f"decision must be one of {sorted(STAGE_REVIEW_DECISIONS)}")
    if decision == "skipped" and not notes.strip():
        raise StageReviewError("notes must be non-empty when decision is skipped")
    if not isinstance(decided_by, str) or not decided_by.strip():
        raise StageReviewError("decided_by must be a non-empty string")
    if len(decided_by.strip()) > 120:
        raise StageReviewError("decided_by must be 120 characters or fewer")
    if not isinstance(notes, str):
        raise StageReviewError("notes must be a string")

    review_dir = run_path / "stage_reviews" / stage
    validation_report_path = review_dir / "validation_report.json"
    issues_path = review_dir / "issues.json"
    validation_report = load_gate_ready_validation_report(run_path, stage, run_id)
    if not issues_path.exists():
        raise StageReviewError(f"issues.json missing: {issues_path}")
    if not issues_path.is_file():
        raise StageReviewError(f"issues.json is not a file: {issues_path}")

    decision_path = review_dir / "decision.json"
    decision_doc = {
        "kind": "stage_review_decision",
        "schema_version": STAGE_REVIEW_SCHEMA_VERSION,
        "run_id": run_id,
        "stage": stage,
        "decision": decision,
        "decision_scope": STAGE_REVIEW_DECISION_SCOPE,
        "professional_approval": False,
        "allow_next_stage": decision in STAGE_REVIEW_PASSING_DECISIONS,
        "decided_by": decided_by.strip(),
        "decision_source": "cli",
        "notes": notes,
        "created_at": utc_timestamp(),
        "validation_report_path": f"stage_reviews/{stage}/validation_report.json",
        "issues_path": f"stage_reviews/{stage}/issues.json",
        "validation_status_at_decision": validation_report["status"],
        "coverage_complete_at_decision": validation_report["coverage_summary"]["coverage_complete"],
        "validation_report_sha256": file_sha256(validation_report_path),
        "issues_sha256": file_sha256(issues_path),
    }
    write_json(decision_path, decision_doc)
    return decision_path


def check_stage_review_gate(run_dir: str | Path, stage: str) -> dict[str, Any]:
    run_path = Path(run_dir)
    ensure_supported_stage(stage)
    ensure_run_dir(run_path)
    run_id = load_run_id(run_path)
    load_gate_ready_validation_report(run_path, stage, run_id)

    review_dir = run_path / "stage_reviews" / stage
    decision_path = review_dir / "decision.json"
    decision_doc = read_json_object(decision_path, "decision")
    errors = validate_decision_schema(decision_doc, run_id, stage)

    validation_report_path = review_dir / "validation_report.json"
    issues_path = review_dir / "issues.json"
    if not issues_path.exists():
        errors.append(f"issues.json missing: {issues_path}")
    elif not issues_path.is_file():
        errors.append(f"issues.json is not a file: {issues_path}")

    if not errors:
        if decision_doc["validation_report_sha256"] != file_sha256(validation_report_path):
            errors.append("validation_report_sha256 mismatch")
        if decision_doc["issues_sha256"] != file_sha256(issues_path):
            errors.append("issues_sha256 mismatch")

    decision = decision_doc.get("decision")
    if not errors and decision not in STAGE_REVIEW_PASSING_DECISIONS:
        errors.append(f"decision is {decision}")

    if errors:
        raise StageReviewError("; ".join(errors))

    return {
        "schema_version": STAGE_REVIEW_SCHEMA_VERSION,
        "kind": "stage_review_gate_check",
        "run_id": run_id,
        "stage": stage,
        "status": "passed",
        "decision": decision,
        "decision_scope": STAGE_REVIEW_DECISION_SCOPE,
        "professional_approval": False,
        "allow_next_stage": True,
        "validation_report_path": f"stage_reviews/{stage}/validation_report.json",
        "issues_path": f"stage_reviews/{stage}/issues.json",
    }


def build_review_units(run_dir: Path, stage: str, run_id: str) -> dict[str, Any]:
    source_artifacts = list(STAGE_REGISTRY[stage]["required_outputs"])
    units: list[dict[str, Any]] = []
    warnings: list[str] = []
    sequence = 1
    for relative_path in source_artifacts:
        artifact_units, artifact_warnings = build_review_units_for_artifact(run_dir, stage, relative_path, sequence)
        units.extend(artifact_units)
        warnings.extend(artifact_warnings)
        sequence += len(artifact_units)

    if not units:
        fallback_path = source_artifacts[0] if source_artifacts else f"{stage}/unknown"
        units.append(
            make_review_unit(
                stage=stage,
                relative_path=fallback_path,
                unit_type="fallback_artifact_review",
                sequence=1,
                locator=fallback_path,
                title="Fallback artifact review",
                required_checks=["artifact_presence", "parse_failure_visibility", "open_items_visibility"],
                note="No deterministic review units could be extracted; fallback unit created.",
            )
        )
        warnings.append("No deterministic review units could be extracted; fallback unit created.")

    return {
        "kind": "stage_review_units",
        "schema_version": STAGE_REVIEW_SCHEMA_VERSION,
        "run_id": run_id,
        "stage": stage,
        "created_at": utc_timestamp(),
        "source_artifacts": source_artifacts,
        "unit_policy": REVIEW_UNIT_POLICY,
        "warnings": warnings,
        "units": units,
    }


def build_review_units_for_artifact(
    run_dir: Path,
    stage: str,
    relative_path: str,
    start_sequence: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    path = run_dir / relative_path
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [
            make_review_unit(
                stage=stage,
                relative_path=relative_path,
                unit_type="fallback_artifact_review",
                sequence=start_sequence,
                locator=relative_path,
                title="Fallback artifact review",
                required_checks=["artifact_presence", "parse_failure_visibility", "open_items_visibility"],
                note="Artifact is not readable as UTF-8.",
            )
        ], [f"{relative_path}: unreadable_non_utf8"]

    suffix = path.suffix.lower()
    if suffix == ".md":
        return build_markdown_review_units(stage, relative_path, text, start_sequence), warnings
    if suffix == ".json":
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError as exc:
            return [
                make_review_unit(
                    stage=stage,
                    relative_path=relative_path,
                    unit_type="fallback_artifact_review",
                    sequence=start_sequence,
                    locator=relative_path,
                    title="Fallback artifact review",
                    required_checks=["artifact_presence", "parse_failure_visibility", "open_items_visibility"],
                    note=f"JSON parse failure: {exc}",
                )
            ], [f"{relative_path}: JSON parse failure: {exc}"]
        return build_json_review_units(stage, relative_path, loaded, start_sequence), warnings
    if suffix == ".jsonl":
        return build_jsonl_review_units(stage, relative_path, text, start_sequence), warnings
    return [
        make_review_unit(
            stage=stage,
            relative_path=relative_path,
            unit_type=artifact_unit_type(stage, relative_path, "artifact_review"),
            sequence=start_sequence,
            locator=relative_path,
            title=relative_path,
            required_checks=STAGE_REQUIRED_CHECKS[stage],
        )
    ], warnings


def build_markdown_review_units(stage: str, relative_path: str, text: str, start_sequence: int) -> list[dict[str, Any]]:
    headings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append((line_number, match.group(2).strip()))

    unit_type = artifact_unit_type(stage, relative_path, "markdown_section")
    if not headings:
        return [
            make_review_unit(
                stage=stage,
                relative_path=relative_path,
                unit_type=unit_type,
                sequence=start_sequence,
                locator=relative_path,
                title=Path(relative_path).name,
                required_checks=STAGE_REQUIRED_CHECKS[stage],
                note="No markdown headings found; entire artifact is one review unit.",
            )
        ]

    return [
        make_review_unit(
            stage=stage,
            relative_path=relative_path,
            unit_type=unit_type,
            sequence=start_sequence + index,
            locator=f"line {line_number}",
            title=title,
            required_checks=STAGE_REQUIRED_CHECKS[stage],
        )
        for index, (line_number, title) in enumerate(headings)
    ]


def build_json_review_units(stage: str, relative_path: str, loaded: Any, start_sequence: int) -> list[dict[str, Any]]:
    list_entries = list(iter_json_list_entries(loaded))
    unit_type = artifact_unit_type(stage, relative_path, "json_entry")
    if not list_entries:
        return [
            make_review_unit(
                stage=stage,
                relative_path=relative_path,
                unit_type=unit_type,
                sequence=start_sequence,
                locator="$",
                title=Path(relative_path).name,
                required_checks=STAGE_REQUIRED_CHECKS[stage],
                note="No JSON list entries found; whole JSON artifact is one review unit.",
            )
        ]
    return [
        make_review_unit(
            stage=stage,
            relative_path=relative_path,
            unit_type=unit_type,
            sequence=start_sequence + index,
            locator=json_path,
            title=infer_json_unit_title(item, json_path),
            required_checks=STAGE_REQUIRED_CHECKS[stage],
        )
        for index, (json_path, item) in enumerate(list_entries)
    ]


def build_jsonl_review_units(stage: str, relative_path: str, text: str, start_sequence: int) -> list[dict[str, Any]]:
    unit_type = artifact_unit_type(stage, relative_path, "jsonl_entry")
    units: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        units.append(
            make_review_unit(
                stage=stage,
                relative_path=relative_path,
                unit_type=unit_type,
                sequence=start_sequence + len(units),
                locator=f"line {line_number}",
                title=f"{Path(relative_path).name} line {line_number}",
                required_checks=STAGE_REQUIRED_CHECKS[stage],
            )
        )
    if not units:
        units.append(
            make_review_unit(
                stage=stage,
                relative_path=relative_path,
                unit_type=unit_type,
                sequence=start_sequence,
                locator=relative_path,
                title=Path(relative_path).name,
                required_checks=STAGE_REQUIRED_CHECKS[stage],
                note="No JSONL entries found; entire artifact is one review unit.",
            )
        )
    return units


def iter_json_list_entries(value: Any, path: str = "$") -> list[tuple[str, Any]]:
    entries: list[tuple[str, Any]] = []
    if isinstance(value, list):
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]"
            entries.append((item_path, item))
            entries.extend(iter_json_list_entries(item, item_path))
        return entries
    if isinstance(value, dict):
        for key, item in value.items():
            entries.extend(iter_json_list_entries(item, f"{path}.{key}"))
    return entries


def infer_json_unit_title(item: Any, json_path: str) -> str:
    if isinstance(item, dict):
        for key in ("title", "section_title", "section_id", "claim_id", "question_id", "file_id", "source_id", "check_id", "id"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return json_path


def make_review_unit(
    *,
    stage: str,
    relative_path: str,
    unit_type: str,
    sequence: int,
    locator: str,
    title: str,
    required_checks: list[str],
    note: str | None = None,
) -> dict[str, Any]:
    unit = {
        "unit_id": make_unit_id(stage, relative_path, unit_type, sequence),
        "required": True,
        "status": "pending",
        "artifact_path": relative_path,
        "unit_type": unit_type,
        "locator": locator,
        "title": title,
        "required_checks": required_checks,
    }
    if note:
        unit["decomposition_note"] = note
    return unit


def make_unit_id(stage: str, relative_path: str, unit_type: str, sequence: int) -> str:
    safe_artifact = re.sub(r"[^a-z0-9]+", ".", relative_path.lower()).strip(".")
    safe_unit_type = re.sub(r"[^a-z0-9]+", "_", unit_type.lower()).strip("_")
    return f"{stage}.{safe_artifact}.{safe_unit_type}.{sequence:03d}"


def artifact_unit_type(stage: str, relative_path: str, default: str) -> str:
    path = relative_path
    if stage == "ingest":
        if path == "inputs/input_inventory.json":
            return "input_material"
        if path == "knowledge/source_index.json":
            return "source_index_entry"
    if stage == "outline":
        if path.endswith("template_structure.json"):
            return "template_section"
        return "outline_section"
    if stage == "evidence":
        if path.endswith("evidence_map.json"):
            return "evidence_mapping"
        return "unresolved_question" if path.endswith(".md") else default
    if stage == "planning":
        if path.endswith("citation_plan.json"):
            return "citation_plan_entry"
        if path.endswith("section_tasks.json"):
            return "section_task"
        if path.endswith("claim_support_matrix.json"):
            return "claim_support_entry"
    if stage == "draft":
        return "markdown_section"
    if stage == "review":
        if path.endswith("review_report.json"):
            return "review_item"
        if path.endswith("verify_report.json"):
            return "verification_check"
        return "markdown_section"
    if stage == "finalize":
        if path.endswith("final_report.md"):
            return "final_report_section"
        if path.endswith("delivery_summary.md"):
            return "delivery_summary"
        if path.endswith("change_log.md"):
            return "change_log"
    if stage == "learning":
        if path.endswith("candidate_profile_update.yaml"):
            return "candidate_profile_update"
        if path.endswith("candidate_skill_patch.md"):
            return "candidate_skill_patch"
        if path.endswith("promotion_report.md"):
            return "promotion_report"
        return "learning_summary"
    return default


def empty_coverage_summary() -> dict[str, Any]:
    return {
        "required_unit_count": 0,
        "reviewed_unit_count": 0,
        "unchecked_unit_count": 0,
        "issue_unit_count": 0,
        "coverage_complete": False,
    }


def empty_unit_validation() -> dict[str, list[str]]:
    return {
        "missing_reviewed_unit_ids": [],
        "unknown_reviewed_unit_ids": [],
        "unknown_unchecked_unit_ids": [],
        "unknown_issue_unit_ids": [],
        "overlapping_reviewed_and_unchecked_unit_ids": [],
    }


def load_review_unit_ids(run_dir: Path, stage: str, run_id: str) -> tuple[list[str], set[str], set[str]]:
    review_units_path = run_dir / "stage_reviews" / stage / "review_units.json"
    try:
        review_units = read_json_object(review_units_path, "review_units")
    except StageReviewError as exc:
        return [str(exc)], set(), set()

    errors: list[str] = []
    if review_units.get("schema_version") != STAGE_REVIEW_SCHEMA_VERSION:
        errors.append("review_units.json schema_version must be 1")
    if review_units.get("kind") != "stage_review_units":
        errors.append("review_units.json kind must be stage_review_units")
    if review_units.get("run_id") != run_id:
        errors.append("review_units.json run_id mismatch")
    if review_units.get("stage") != stage:
        errors.append("review_units.json stage mismatch")
    units = review_units.get("units")
    if not isinstance(units, list) or not units:
        errors.append("review_units.json units must be a non-empty list")
        return errors, set(), set()

    all_unit_ids: set[str] = set()
    required_unit_ids: set[str] = set()
    for index, unit in enumerate(units, start=1):
        if not isinstance(unit, dict):
            errors.append(f"review unit {index} must be an object")
            continue
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id:
            errors.append(f"review unit {index} unit_id must be a non-empty string")
            continue
        if unit_id in all_unit_ids:
            errors.append(f"duplicate review unit_id: {unit_id}")
        all_unit_ids.add(unit_id)
        if unit.get("required") is True:
            required_unit_ids.add(unit_id)
        for field in ("artifact_path", "unit_type", "locator", "title"):
            if not isinstance(unit.get(field), str) or not unit[field].strip():
                errors.append(f"{unit_id} {field} must be a non-empty string")
        if not isinstance(unit.get("required_checks"), list) or not all(
            isinstance(check, str) and check for check in unit.get("required_checks", [])
        ):
            errors.append(f"{unit_id} required_checks must be a non-empty list of strings")
        if unit.get("status") != "pending":
            errors.append(f"{unit_id} status must be pending")
        artifact_path = unit.get("artifact_path")
        if isinstance(artifact_path, str) and not is_safe_relative_path(artifact_path):
            errors.append(f"{unit_id} artifact_path must be a safe relative path")

    return errors, required_unit_ids, all_unit_ids


def validate_review_unit_coverage(
    run_dir: Path,
    stage: str,
    run_id: str,
    issues_payload: dict[str, Any],
) -> tuple[list[str], dict[str, Any], dict[str, list[str]]]:
    errors, required_unit_ids, all_unit_ids = load_review_unit_ids(run_dir, stage, run_id)
    unit_validation = empty_unit_validation()

    reviewed_unit_ids = list_field_as_set(issues_payload.get("reviewed_unit_ids"))
    unchecked_unit_ids = list_field_as_set(issues_payload.get("unchecked_unit_ids"))
    issue_unit_ids = {
        issue.get("unit_id")
        for issue in issues_payload.get("issues", [])
        if isinstance(issue, dict) and isinstance(issue.get("unit_id"), str)
    }

    unit_validation["missing_reviewed_unit_ids"] = sorted(required_unit_ids - reviewed_unit_ids)
    unit_validation["unknown_reviewed_unit_ids"] = sorted(reviewed_unit_ids - all_unit_ids)
    unit_validation["unknown_unchecked_unit_ids"] = sorted(unchecked_unit_ids - all_unit_ids)
    unit_validation["unknown_issue_unit_ids"] = sorted(issue_unit_ids - all_unit_ids)
    unit_validation["overlapping_reviewed_and_unchecked_unit_ids"] = sorted(reviewed_unit_ids & unchecked_unit_ids)

    if unit_validation["missing_reviewed_unit_ids"]:
        errors.append(
            "missing required review unit coverage: "
            + ", ".join(unit_validation["missing_reviewed_unit_ids"])
        )
    if unit_validation["unknown_reviewed_unit_ids"]:
        errors.append("unknown reviewed unit ids: " + ", ".join(unit_validation["unknown_reviewed_unit_ids"]))
    if unit_validation["unknown_unchecked_unit_ids"]:
        errors.append("unknown unchecked unit ids: " + ", ".join(unit_validation["unknown_unchecked_unit_ids"]))
    if unit_validation["unknown_issue_unit_ids"]:
        errors.append("unknown issue unit ids: " + ", ".join(unit_validation["unknown_issue_unit_ids"]))
    if unit_validation["overlapping_reviewed_and_unchecked_unit_ids"]:
        errors.append(
            "reviewed and unchecked unit ids overlap: "
            + ", ".join(unit_validation["overlapping_reviewed_and_unchecked_unit_ids"])
        )
    if unchecked_unit_ids:
        errors.append("unchecked_unit_ids must be empty in S1R: " + ", ".join(sorted(unchecked_unit_ids)))

    coverage_complete = not any(unit_validation.values()) and not unchecked_unit_ids and not errors
    coverage_summary = {
        "required_unit_count": len(required_unit_ids),
        "reviewed_unit_count": len(reviewed_unit_ids),
        "unchecked_unit_count": len(unchecked_unit_ids),
        "issue_unit_count": len(issue_unit_ids),
        "coverage_complete": coverage_complete,
    }
    return errors, coverage_summary, unit_validation


def list_field_as_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def ensure_supported_stage(stage: str) -> None:
    if stage not in STAGE_ORDER:
        raise StageReviewError(f"Unknown stage: {stage}. Supported stages: {', '.join(STAGE_ORDER)}")


def ensure_run_dir(run_dir: Path) -> None:
    if not run_dir.exists():
        raise StageReviewError(f"run_dir missing: {run_dir}")
    if not run_dir.is_dir():
        raise StageReviewError(f"run_dir is not a directory: {run_dir}")


def load_run_id(run_dir: Path) -> str:
    manifest = read_json_object(run_dir / "manifest.json", "manifest")
    task_brief = read_json_object(run_dir / "task_brief.json", "task_brief")
    return validate_run_metadata(manifest, task_brief)


def validate_run_metadata(manifest: dict[str, Any], task_brief: dict[str, Any]) -> str:
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise StageReviewError("manifest.json missing run_id")
    if task_brief.get("run_id") != run_id:
        raise StageReviewError("run_id mismatch between manifest.json and task_brief.json")
    return run_id


def read_optional_run_state(run_dir: Path) -> dict[str, Any] | None:
    state_path = run_dir / "run_state.json"
    if not state_path.exists():
        return None
    return read_json_object(state_path, "run_state")


def validate_run_state_for_stage(state: dict[str, Any], run_id: str, stage: str) -> None:
    if state.get("run_id") != run_id:
        raise StageReviewError("run_id mismatch between manifest.json and run_state.json")
    stages = state.get("stages")
    if not isinstance(stages, dict) or stage not in stages:
        raise StageReviewError(f"run_state.json does not contain stage: {stage}")
    status = stages[stage].get("status")
    if status != "done":
        raise StageReviewError(f"stage {stage} is not complete; current status is {status}")


def load_gate_ready_validation_report(run_dir: Path, stage: str, run_id: str) -> dict[str, Any]:
    validation_report = read_json_object(run_dir / "stage_reviews" / stage / "validation_report.json", "validation_report")
    errors: list[str] = []
    if validation_report.get("schema_version") != STAGE_REVIEW_SCHEMA_VERSION:
        errors.append("validation_report schema_version must be 1")
    if validation_report.get("kind") != "stage_review_validation_report":
        errors.append("validation_report kind must be stage_review_validation_report")
    if validation_report.get("run_id") != run_id:
        errors.append("validation_report run_id mismatch")
    if validation_report.get("stage") != stage:
        errors.append("validation_report stage mismatch")
    if validation_report.get("status") != "valid":
        errors.append("validation_report status must be valid")
    if validation_report.get("not_professional_approval") is not True:
        errors.append("validation_report not_professional_approval must be true")
    coverage_summary = validation_report.get("coverage_summary")
    if not isinstance(coverage_summary, dict):
        errors.append("validation_report coverage_summary must be an object")
    elif coverage_summary.get("coverage_complete") is not True:
        errors.append("coverage_complete must be true")
    if errors:
        raise StageReviewError("; ".join(errors))
    return validation_report


def validate_decision_schema(decision_doc: dict[str, Any], run_id: str, stage: str) -> list[str]:
    errors: list[str] = []
    missing_fields = sorted(EXPECTED_DECISION_FIELDS - set(decision_doc))
    if missing_fields:
        errors.append(f"decision.json missing required fields: {', '.join(missing_fields)}")
    if decision_doc.get("schema_version") != STAGE_REVIEW_SCHEMA_VERSION:
        errors.append("decision schema_version must be 1")
    if decision_doc.get("kind") != "stage_review_decision":
        errors.append("decision kind must be stage_review_decision")
    if decision_doc.get("run_id") != run_id:
        errors.append("decision run_id mismatch")
    if decision_doc.get("stage") != stage:
        errors.append("decision stage mismatch")
    decision = decision_doc.get("decision")
    if decision not in STAGE_REVIEW_DECISIONS:
        errors.append(f"decision must be one of {sorted(STAGE_REVIEW_DECISIONS)}")
    if decision_doc.get("decision_scope") != STAGE_REVIEW_DECISION_SCOPE:
        errors.append(f"decision_scope must be {STAGE_REVIEW_DECISION_SCOPE}")
    if decision_doc.get("professional_approval") is not False:
        errors.append("professional_approval must be false")
    expected_allow_next = decision in STAGE_REVIEW_PASSING_DECISIONS
    if decision in STAGE_REVIEW_DECISIONS and decision_doc.get("allow_next_stage") is not expected_allow_next:
        errors.append(f"allow_next_stage must be {str(expected_allow_next).lower()} for decision {decision}")
    decided_by = decision_doc.get("decided_by")
    if not isinstance(decided_by, str) or not decided_by.strip():
        errors.append("decided_by must be a non-empty string")
    elif len(decided_by.strip()) > 120:
        errors.append("decided_by must be 120 characters or fewer")
    if decision_doc.get("decision_source") != "cli":
        errors.append("decision_source must be cli")
    notes = decision_doc.get("notes")
    if not isinstance(notes, str):
        errors.append("notes must be a string")
    elif decision == "skipped" and not notes.strip():
        errors.append("notes must be non-empty when decision is skipped")
    created_at = decision_doc.get("created_at")
    if not isinstance(created_at, str) or not created_at.strip():
        errors.append("created_at must be a non-empty string")
    if decision_doc.get("validation_report_path") != f"stage_reviews/{stage}/validation_report.json":
        errors.append("validation_report_path mismatch")
    if decision_doc.get("issues_path") != f"stage_reviews/{stage}/issues.json":
        errors.append("issues_path mismatch")
    if decision_doc.get("validation_status_at_decision") != "valid":
        errors.append("validation_status_at_decision must be valid")
    if decision_doc.get("coverage_complete_at_decision") is not True:
        errors.append("coverage_complete_at_decision must be true")
    for field in ("validation_report_sha256", "issues_sha256"):
        value = decision_doc.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} must be a non-empty string")
    return errors


def summarize_artifact(run_dir: Path, relative_path: str, kind: str, *, required: bool) -> dict[str, Any]:
    if not is_safe_relative_path(relative_path):
        raise StageReviewError(f"unsafe artifact path: {relative_path}")
    path = run_dir / relative_path
    if required:
        problem = validate_output_path(path, relative_path)
        if problem:
            raise StageReviewError(f"stage output invalid: {problem}")
    if not path.exists():
        return {
            "path": relative_path,
            "kind": kind,
            "missing": True,
            "readable": False,
            "sha256": None,
            "size_bytes": 0,
            "excerpt": "",
            "error": "missing",
        }
    if not path.is_file():
        return {
            "path": relative_path,
            "kind": kind,
            "missing": False,
            "readable": False,
            "sha256": None,
            "size_bytes": 0,
            "excerpt": "",
            "error": "not_a_file",
        }

    size_bytes = path.stat().st_size
    digest = file_sha256(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {
            "path": relative_path,
            "kind": kind,
            "missing": False,
            "readable": False,
            "sha256": digest,
            "size_bytes": size_bytes,
            "excerpt": "",
            "error": "unreadable_non_utf8",
        }

    return {
        "path": relative_path,
        "kind": kind,
        "missing": False,
        "readable": True,
        "sha256": digest,
        "size_bytes": size_bytes,
        "excerpt": text[:EXCERPT_CHAR_LIMIT],
    }


def build_issues_schema(stage: str) -> dict[str, Any]:
    return {
        "schema_version": STAGE_REVIEW_SCHEMA_VERSION,
        "kind": "stage_review_issues_schema",
        "stage": stage,
        "issues_kind": "stage_review_issues",
        "required_top_level_fields": sorted(EXPECTED_TOP_LEVEL_ISSUE_FIELDS),
        "allowed_statuses": sorted(ISSUE_STATUSES),
        "forbidden_statuses": sorted(FORBIDDEN_APPROVAL_STATUSES),
        "allowed_severities": sorted(ISSUE_SEVERITIES),
        "allowed_categories": sorted(ISSUE_CATEGORIES),
        "high_risk_categories": sorted(HIGH_RISK_CATEGORIES),
        "required_issue_fields": sorted(EXPECTED_ISSUE_FIELDS),
        "s1_policy": {
            "safe_auto_fix_eligible": "advisory only; S1 does not apply patches",
            "high_risk_categories_require_user_review": True,
            "high_risk_categories_must_not_be_safe_auto_fix_eligible": True,
            "not_professional_approval_required": True,
        },
        "s1r_review_unit_policy": {
            "review_units_path": f"stage_reviews/{stage}/review_units.json",
            "reviewed_unit_ids_required": True,
            "unchecked_unit_ids_required": True,
            "issue_unit_id_required": True,
            "coverage_required": True,
            "partial_review_allowed": False,
            "unknown_unit_id_allowed": False,
        },
    }


def render_review_prompt(context: dict[str, Any], issues_schema: dict[str, Any]) -> str:
    stage = context["stage"]
    stage_outputs = "\n".join(f"- {item['path']}" for item in context["stage_outputs"]) or "- none"
    context_artifacts = "\n".join(f"- {item['path']}" for item in context["context_artifacts"]) or "- none"
    review_focus = "\n".join(f"- {item}" for item in context["review_focus"])
    forbidden_actions = "\n".join(f"- {item}" for item in context["forbidden_actions"])
    expected_outputs = "\n".join(f"- {item}" for item in context["expected_outputs"])
    categories = ", ".join(issues_schema["allowed_categories"])
    statuses = ", ".join(issues_schema["allowed_statuses"])

    return "\n".join(
        [
            f"# Stage Review Prompt: {stage}",
            "",
            "This package is for Claude Code assisted semantic review.",
            "It is advisory only and is not professional approval.",
            "Do not modify artifacts in this run. Do not add project facts.",
            "sample is not fact source. reference is not project-specific fact support.",
            "If a point requires factual or professional judgment, mark it as requires_user_review or HITL required.",
            "You must read review_units.json and review every required unit by unit_id.",
            "Do not summarize the whole stage without unit-level coverage.",
            "",
            "## Run",
            "",
            f"- run_id: {context['run_id']}",
            f"- stage: {stage}",
            f"- phase: {context['phase']}",
            f"- task_type: {context['run'].get('task_type')}",
            "",
            "## Stage Outputs",
            "",
            stage_outputs,
            "",
            "## Upstream Context Artifacts",
            "",
            context_artifacts,
            "",
            "## Review Focus",
            "",
            review_focus,
            "",
            "## Forbidden Actions",
            "",
            forbidden_actions,
            "- Do not write professional approval, safety approval, compliance approval, or production readiness approval.",
            "- Do not remove NEEDS_USER_CONFIRMATION.",
            "- Do not modify stable profiles or Skill files.",
            "",
            "## Expected Outputs",
            "",
            expected_outputs,
            "",
            "## Review Unit Coverage",
            "",
            f"- review_units_path: {context['review_units_path']}",
            f"- review_unit_count: {context['review_unit_count']}",
            "- Add every checked required unit_id to reviewed_unit_ids.",
            "- unchecked_unit_ids must be empty for S1R validation to pass.",
            "- If any required unit cannot be reviewed, list it in unchecked_unit_ids with a reason in claude_review.md.",
            "- Each issue must include a known unit_id from review_units.json.",
            "- The validation step fails for missing coverage, unknown unit_id, unchecked units, or reviewed/unchecked overlap.",
            "",
            "## issues.json Schema Summary",
            "",
            f"- kind: stage_review_issues",
            f"- schema_version: {STAGE_REVIEW_SCHEMA_VERSION}",
            "- required top-level fields include reviewed_unit_ids and unchecked_unit_ids.",
            "- required issue fields include unit_id.",
            f"- allowed status values: {statuses}",
            f"- allowed severity values: {', '.join(sorted(ISSUE_SEVERITIES))}",
            f"- allowed category values: {categories}",
            "- high-risk categories require requires_user_review=true and safe_auto_fix_eligible=false.",
            "- safe_auto_fix_eligible is advisory only in S1; no patch will be applied.",
            "",
            "Generate claude_review.md and issues.json only under this stage review directory.",
            "This S1 workflow does not approve, fix, patch, or rewrite professional artifacts.",
            "",
        ]
    )


def validate_issues_payload(payload: dict[str, Any], run_id: str, stage: str) -> tuple[list[str], int, int]:
    errors: list[str] = []
    missing_top_level_fields = sorted(EXPECTED_TOP_LEVEL_ISSUE_FIELDS - set(payload))
    if missing_top_level_fields:
        errors.append(f"issues.json missing required fields: {', '.join(missing_top_level_fields)}")
    if payload.get("schema_version") != STAGE_REVIEW_SCHEMA_VERSION:
        errors.append("schema_version must be 1")
    if payload.get("kind") != "stage_review_issues":
        errors.append("kind must be stage_review_issues")
    if payload.get("run_id") != run_id:
        errors.append("run_id mismatch")
    if payload.get("stage") != stage:
        errors.append("stage mismatch")

    status = payload.get("status")
    if not isinstance(status, str) or status not in ISSUE_STATUSES:
        errors.append(f"status must be one of {sorted(ISSUE_STATUSES)}")
    if isinstance(status, str) and contains_forbidden_status_or_approval(status):
        errors.append(f"status uses forbidden approval wording: {status}")
    reviewer = payload.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        errors.append("reviewer must be a non-empty string")
    if payload.get("not_professional_approval") is not True:
        errors.append("not_professional_approval must be true")
    validate_string_list(payload.get("reviewed_unit_ids"), "reviewed_unit_ids", "issues.json", errors)
    validate_string_list(payload.get("unchecked_unit_ids"), "unchecked_unit_ids", "issues.json", errors)

    issues = payload.get("issues")
    if not isinstance(issues, list):
        errors.append("issues must be a list")
        return errors, 0, 0

    seen_issue_ids: set[str] = set()
    blocking_issue_count = 0
    for index, issue in enumerate(issues, start=1):
        if not isinstance(issue, dict):
            errors.append(f"issue {index} must be an object")
            continue
        issue_id = issue.get("issue_id")
        issue_label = issue_id if isinstance(issue_id, str) and issue_id else f"issue {index}"
        missing_fields = sorted(EXPECTED_ISSUE_FIELDS - set(issue))
        if missing_fields:
            errors.append(f"{issue_label} missing required fields: {', '.join(missing_fields)}")

        if not isinstance(issue_id, str) or not issue_id:
            errors.append(f"issue {index} issue_id must be a non-empty string")
        elif issue_id in seen_issue_ids:
            errors.append(f"duplicate issue_id: {issue_id}")
        else:
            seen_issue_ids.add(issue_id)
        unit_id = issue.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id:
            errors.append(f"{issue_label} unit_id must be a non-empty string")

        severity = issue.get("severity")
        if severity not in ISSUE_SEVERITIES:
            errors.append(f"{issue_label} severity must be one of {sorted(ISSUE_SEVERITIES)}")
        if severity == "P0":
            blocking_issue_count += 1

        category = issue.get("category")
        if category not in ISSUE_CATEGORIES:
            errors.append(f"{issue_label} category must be one of {sorted(ISSUE_CATEGORIES)}")

        validate_bool_field(issue, "requires_user_review", issue_label, errors)
        validate_bool_field(issue, "requires_hitl", issue_label, errors)
        validate_bool_field(issue, "safe_auto_fix_eligible", issue_label, errors)

        if category in HIGH_RISK_CATEGORIES:
            if issue.get("safe_auto_fix_eligible") is True:
                errors.append(f"{issue_label} high-risk category must set safe_auto_fix_eligible=false")
            if issue.get("requires_user_review") is not True:
                errors.append(f"{issue_label} high-risk category must set requires_user_review=true")

        validate_string_list(issue.get("related_artifacts"), "related_artifacts", issue_label, errors)
        validate_string_list(issue.get("related_sections"), "related_sections", issue_label, errors)
        for related_path in issue.get("related_artifacts") if isinstance(issue.get("related_artifacts"), list) else []:
            if isinstance(related_path, str) and not is_safe_relative_path(related_path):
                errors.append(f"{issue_label} related_artifacts must be safe relative paths: {related_path}")

        text = issue_text(issue)
        text_errors = validate_issue_text(text, issue_label)
        errors.extend(text_errors)

    return errors, len(issues), blocking_issue_count


def validate_bool_field(issue: dict[str, Any], field: str, issue_label: str, errors: list[str]) -> None:
    if field in issue and not isinstance(issue[field], bool):
        errors.append(f"{issue_label} {field} must be a boolean")


def validate_string_list(value: Any, field: str, issue_label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{issue_label} {field} must be a list of strings")


def issue_text(issue: dict[str, Any]) -> str:
    fields = ["title", "description", "recommendation", "proposed_action", "forbidden_auto_fix_reason"]
    values = [issue.get(field) for field in fields if isinstance(issue.get(field), str)]
    return "\n".join(values).lower()


def validate_issue_text(text: str, issue_label: str) -> list[str]:
    errors: list[str] = []
    for phrase in FORBIDDEN_APPROVAL_PHRASES:
        if phrase in text:
            errors.append(f"{issue_label} uses forbidden approval wording: {phrase}")
    for phrase in SAMPLE_REFERENCE_FACT_CLAIMS:
        if phrase in text:
            errors.append(f"{issue_label} violates source policy: {phrase}")
    for phrase in STABLE_PROFILE_SKILL_ACTIONS:
        if phrase in text:
            errors.append(f"{issue_label} must not request stable profile or Skill modification: {phrase}")
    for phrase in NEEDS_CONFIRMATION_DELETE_ACTIONS:
        if phrase in text:
            errors.append(f"{issue_label} must not request direct removal of NEEDS_USER_CONFIRMATION: {phrase}")
    return errors


def contains_forbidden_status_or_approval(value: str) -> bool:
    normalized = value.lower().strip()
    return normalized in FORBIDDEN_APPROVAL_STATUSES or any(phrase in normalized for phrase in FORBIDDEN_APPROVAL_PHRASES)


def is_safe_relative_path(value: str) -> bool:
    if not value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StageReviewError(f"{label}.json missing: {path}") from exc
    except UnicodeDecodeError as exc:
        raise StageReviewError(f"{label}.json invalid encoding: {path}") from exc
    except json.JSONDecodeError as exc:
        raise StageReviewError(f"{label}.json invalid JSON: {exc}") from exc
    if not isinstance(loaded, dict):
        raise StageReviewError(f"{label}.json root must be an object")
    return loaded


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(f"{encoded}\n", encoding="utf-8")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
