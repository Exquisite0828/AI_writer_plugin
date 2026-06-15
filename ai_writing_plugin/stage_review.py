from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from .run_state import STAGE_ORDER, STAGE_REGISTRY, validate_output_path


EXCERPT_CHAR_LIMIT = 4000
STAGE_REVIEW_SCHEMA_VERSION = 1

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
    "severity",
    "category",
    "title",
    "description",
    "related_artifacts",
    "related_sections",
    "requires_user_review",
    "requires_hitl",
    "safe_auto_fix_eligible",
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
    "issues",
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
        "review_focus": STAGE_REVIEW_FOCUS[stage],
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "expected_outputs": expected_outputs,
    }
    issues_schema = build_issues_schema(stage)

    write_json(review_dir / "review_context.json", context)
    write_json(review_dir / "issues_schema.json", issues_schema)
    (review_dir / "review_prompt.md").write_text(render_review_prompt(context, issues_schema), encoding="utf-8")

    artifacts = [
        f"stage_reviews/{stage}/review_context.json",
        f"stage_reviews/{stage}/review_prompt.md",
        f"stage_reviews/{stage}/issues_schema.json",
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
        "warnings": [ADVISORY_SAFE_FIX_WARNING],
        "errors": errors,
    }
    write_json(review_dir / "validation_report.json", report)
    if errors:
        raise StageReviewError("Stage review issues invalid: " + "; ".join(errors))
    return report


def ensure_supported_stage(stage: str) -> None:
    if stage not in STAGE_ORDER:
        raise StageReviewError(f"Unknown stage: {stage}. Supported stages: {', '.join(STAGE_ORDER)}")


def ensure_run_dir(run_dir: Path) -> None:
    if not run_dir.exists():
        raise StageReviewError(f"run_dir missing: {run_dir}")
    if not run_dir.is_dir():
        raise StageReviewError(f"run_dir is not a directory: {run_dir}")


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
            "## issues.json Schema Summary",
            "",
            f"- kind: stage_review_issues",
            f"- schema_version: {STAGE_REVIEW_SCHEMA_VERSION}",
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
    fields = ["title", "description", "proposed_action", "forbidden_auto_fix_reason"]
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
