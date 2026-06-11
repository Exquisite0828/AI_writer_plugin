from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .document_types import HARA_RULES
from .document_types.base import DocumentTypeRules
from .document_types.context import get_rules_for_task_brief
from .models import (
    ArtifactRecord,
    CitationEvidenceDetail,
    CitationPlanArtifact,
    InputInventory,
    Manifest,
    SectionTask,
    SectionTasksArtifact,
    SourceIndex,
    TaskBrief,
    TemplateStructure,
)
from .provenance import build_provenance_verify_facts
from .verify import build_verify_report, render_failures_md


class ReviewRunError(Exception):
    """Raised when Phase 6 review and verification cannot complete."""


@dataclass(frozen=True)
class ReviewRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class Phase6Inputs:
    manifest: Manifest
    task_brief: TaskBrief
    inventory: InputInventory
    source_index: SourceIndex
    template_structure: TemplateStructure
    citation_plan: CitationPlanArtifact
    section_tasks: SectionTasksArtifact
    provenance_index: dict[str, Any]
    claim_support_matrix: dict[str, Any]
    knowledge_gaps: str
    unresolved_questions: str
    full_draft: str
    section_drafts: dict[str, str]


REVIEW_RUN_REQUIRED_ERROR = "review-run requires a drafted Phase 5 run"
FULL_DRAFT_REQUIRED_ERROR = "full_draft is required for review"
PLAN_REQUIRED_ERROR = "section_tasks and citation_plan are required for review"
SOURCE_INDEX_REQUIRED_ERROR = "source_index is required"
TASK_SEPARATOR = "\u00b7"
CONFIRMATION_MARKER = HARA_RULES.confirmation_marker
SENSITIVE_TITLE_MARKERS = tuple(HARA_RULES.terminology["sensitive_title_markers"].split("|"))
REVIEW_ARTIFACTS = [
    "review/review_report.json",
    "review/template_review.md",
    "review/checklist_review.md",
    "review/evidence_review.md",
    "review/final_review.md",
    "verify/verify_report.json",
    "verify/failures.md",
]
PHASE_5_REQUIRED_PATHS = [
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/knowledge_gaps.md",
    "knowledge/provenance_index.json",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
    "plans/claim_support_matrix.json",
    "plans/outline_final.md",
    "plans/writing_plan.md",
]
LATER_PHASE_PATHS = [
    "revision_plan.json",
    "revised",
    "final",
    "learning",
]
ALLOWED_EARLY_TRACE_FILE = "hitl_decisions.jsonl"
FORBIDDEN_TRACE_FILES = {"session_trace.jsonl"}
FINAL_HARA_PATTERNS = tuple(pattern.lower() for pattern in HARA_RULES.forbidden_final_claims)
ALLOWED_FINAL_CONTEXTS = [
    "not a final",
    "no final",
    "remains tbd",
    "intentionally deferred",
    "deferred to",
    "must not",
    "does not make final",
]
SOURCE_SUPPORT_HEADINGS = ("## 来源支持", "## Source Support")
GLOBAL_DRAFT_BOUNDARY_HEADINGS = ("## 全局草稿边界说明", "## Global Draft Boundary Note")
GLOBAL_OPEN_CONFIRMATION_HEADINGS = (
    "## 全局开放问题和必需确认",
    "## Global Open Questions and Required Confirmations",
)
PHASE_BOUNDARY_HEADINGS = ("## 阶段边界说明", "## Phase Boundary Note")
SOURCE_SUPPORT_PATTERN = re.compile(
    r"(?m)^-\s+(?P<evidence_id>EVD-[A-Z0-9]+)\s+\|\s+(?P<source_id>SRC-[A-Z0-9]+)\s+\|\s+(?P<file_id>FILE-\d{3})\s+\|\s+(?P<usage>[a-z_]+)"
)
EVIDENCE_ID_PATTERN = re.compile(r"\bEVD-[A-Z0-9]+\b")


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def review_existing_run(run_dir: str | Path) -> ReviewRunResult:
    run_path = Path(run_dir)
    generated_at = utc_timestamp()
    inputs = load_phase_6_inputs(run_path)
    rules = get_rules_for_task_brief(inputs.task_brief.model_dump())
    analysis = analyze_run(run_path, inputs, rules)
    review_items = assign_review_ids(analysis["items"])
    review_report = build_review_report(inputs, generated_at, review_items, analysis, rules)

    review_dir = run_path / "review"
    verify_dir = run_path / "verify"
    review_dir.mkdir(parents=True, exist_ok=True)
    verify_dir.mkdir(parents=True, exist_ok=True)

    template_review = render_template_review(inputs, analysis, review_items)
    checklist_review = render_checklist_review(inputs, analysis, review_items, rules)
    evidence_review = render_evidence_review(inputs, analysis, review_items, rules)
    final_review = render_final_review(inputs, review_report, review_items, rules)

    (review_dir / "template_review.md").write_text(template_review, encoding="utf-8")
    (review_dir / "checklist_review.md").write_text(checklist_review, encoding="utf-8")
    (review_dir / "evidence_review.md").write_text(evidence_review, encoding="utf-8")
    (review_dir / "final_review.md").write_text(final_review, encoding="utf-8")
    write_json(review_dir / "review_report.json", review_report)

    bind_review_item_ids(analysis["facts"], review_items)
    verify_report = build_verify_report(
        run_id=inputs.manifest.run_id,
        generated_at=generated_at,
        facts=analysis["facts"],
        review_items=review_items,
        final_readiness=review_report["summary"]["final_readiness"],
        rules=rules,
    )
    failures_md = render_failures_md(inputs.manifest.run_id, verify_report, review_items, rules=rules)
    write_json(verify_dir / "verify_report.json", verify_report)
    (verify_dir / "failures.md").write_text(failures_md, encoding="utf-8")

    update_manifest(run_path, inputs.manifest, generated_at)
    return ReviewRunResult(artifact_paths=REVIEW_ARTIFACTS)


def load_phase_6_inputs(run_dir: Path) -> Phase6Inputs:
    if not run_dir.exists():
        raise ReviewRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise ReviewRunError(f"Run path is not a directory: {run_dir}")

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise ReviewRunError(f"Required manifest.json not found: {manifest_path}")
    manifest = validate_json_model(manifest_path, Manifest)
    if manifest.phase not in {"phase_5", "phase_6"} or manifest.status not in {"drafted", "reviewed_verified"}:
        raise ReviewRunError(REVIEW_RUN_REQUIRED_ERROR)

    citation_plan_path = run_dir / "plans" / "citation_plan.json"
    section_tasks_path = run_dir / "plans" / "section_tasks.json"
    if not citation_plan_path.exists() or not section_tasks_path.exists():
        raise ReviewRunError(PLAN_REQUIRED_ERROR)

    source_index_path = run_dir / "knowledge" / "source_index.json"
    if not source_index_path.exists():
        raise ReviewRunError(SOURCE_INDEX_REQUIRED_ERROR)

    full_draft_path = run_dir / "draft" / "full_draft.md"
    if not full_draft_path.exists():
        raise ReviewRunError(FULL_DRAFT_REQUIRED_ERROR)

    missing_phase_5_paths = [relative_path for relative_path in PHASE_5_REQUIRED_PATHS if not (run_dir / relative_path).exists()]
    if missing_phase_5_paths:
        raise ReviewRunError(REVIEW_RUN_REQUIRED_ERROR)

    task_brief = validate_json_model(run_dir / "task_brief.json", TaskBrief)
    inventory = validate_json_model(run_dir / "inputs" / "input_inventory.json", InputInventory)
    source_index = validate_json_model(source_index_path, SourceIndex)
    template_structure = validate_json_model(run_dir / "plans" / "template_structure.json", TemplateStructure)
    citation_plan = validate_json_model(citation_plan_path, CitationPlanArtifact)
    section_tasks = validate_json_model(section_tasks_path, SectionTasksArtifact)
    provenance_index = read_json(run_dir / "knowledge" / "provenance_index.json")
    claim_support_matrix = read_json(run_dir / "plans" / "claim_support_matrix.json")

    section_drafts: dict[str, str] = {}
    for task in section_tasks.tasks:
        draft_path = run_dir / task.future_output_path
        if draft_path.exists():
            section_drafts[task.future_output_path] = draft_path.read_text(encoding="utf-8")

    return Phase6Inputs(
        manifest=manifest,
        task_brief=task_brief,
        inventory=inventory,
        source_index=source_index,
        template_structure=template_structure,
        citation_plan=citation_plan,
        section_tasks=section_tasks,
        provenance_index=provenance_index,
        claim_support_matrix=claim_support_matrix,
        knowledge_gaps=(run_dir / "knowledge" / "knowledge_gaps.md").read_text(encoding="utf-8"),
        unresolved_questions=(run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8"),
        full_draft=full_draft_path.read_text(encoding="utf-8"),
        section_drafts=section_drafts,
    )


def analyze_run(run_dir: Path, inputs: Phase6Inputs, rules: DocumentTypeRules) -> dict[str, Any]:
    tasks = sorted(inputs.section_tasks.tasks, key=lambda item: (item.order, item.task_id))
    details_by_id = evidence_details_by_id(inputs.citation_plan)
    source_by_id = {source.source_id: source for source in inputs.source_index.sources}
    file_role_by_id = {file.file_id: file.role for file in inputs.inventory.files}
    facts = default_check_facts(rules)
    items: list[dict[str, Any]] = []
    citation_rows: list[dict[str, Any]] = []

    missing_section_paths: list[str] = []
    missing_headings: list[str] = []
    metadata_issues: list[str] = []
    section_positions: list[int] = []

    for task in tasks:
        draft_text = inputs.section_drafts.get(task.future_output_path)
        if draft_text is None:
            missing_section_paths.append(task.future_output_path)
            items.append(
                make_item(
                    "P1",
                    "template_mismatch",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Required section draft is missing: {task.future_output_path}.",
                    [],
                    "Regenerate the Phase 5 draft or restore the missing section draft before Phase 7.",
                )
            )
            continue

        heading = f"# {task.section_title}"
        position = inputs.full_draft.find(heading)
        section_positions.append(position)
        if position < 0:
            missing_headings.append(task.section_title)
            items.append(
                make_item(
                    "P1",
                    "template_mismatch",
                    task.section_id,
                    task.task_id,
                    "draft/full_draft.md",
                    f"Full draft is missing section heading: {task.section_title}.",
                    [],
                    "Rebuild full_draft.md from section tasks in Phase 7.",
                )
            )

        for marker in ["Task id:", "Section id:", "Draft status:", "Evidence status:"]:
            if marker not in draft_text:
                metadata_issues.append(f"{task.future_output_path} missing {marker}")
                items.append(
                    make_item(
                        "P2",
                        "formatting_issue",
                        task.section_id,
                        task.task_id,
                        task.future_output_path,
                        f"Section metadata is missing {marker}",
                        [],
                        "Restore Phase 5 section draft metadata.",
                        blocks_final=False,
                    )
                )

        if not contains_any(draft_text, SOURCE_SUPPORT_HEADINGS):
            items.append(
                make_item(
                    "P1",
                    "missing_source_support",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    "Section draft is missing source support section.",
                    [],
                    "Add source support using only task allowed evidence.",
                )
            )
        if f"## {rules.confirmation_marker}" not in draft_text:
            items.append(
                make_item(
                    "P1",
                    "checklist_gap",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Section draft is missing the {rules.confirmation_marker} section.",
                    [],
                    "Restore the confirmation section before downstream review.",
                )
            )

        analyze_task_citations(task, draft_text, details_by_id, source_by_id, items, citation_rows)
        analyze_source_support_lines(task, draft_text, file_role_by_id, items)
        analyze_hara_confirmation(task, draft_text, items, rules)
        analyze_final_hara_phrases(task, draft_text, items, rules)

    if section_positions and section_positions != sorted(section_positions):
        items.append(
            make_item(
                "P2",
                "template_mismatch",
                "",
                "",
                "draft/full_draft.md",
                "Full draft section order does not match section_tasks order.",
                [],
                "Re-merge section drafts in task order.",
                blocks_final=False,
            )
        )

    analyze_checklist(inputs, items)
    analyze_global_boundaries(inputs, items)
    analyze_reference_fact_misuse(inputs, items)
    analyze_later_phase_paths(run_dir, items)
    provenance_facts, provenance_items = build_provenance_verify_facts(
        provenance_index=inputs.provenance_index,
        claim_support_matrix=inputs.claim_support_matrix,
        final_report_text=None,
        delivery_summary_text=None,
        external_profile_expected=inputs.task_brief.profile is not None,
    )
    facts.update(provenance_facts)
    items.extend(provenance_items)

    facts["required_phase5_artifacts_exist"] = fact_from_condition(
        not missing_section_paths,
        "passed",
        "blocked",
        "All required Phase 5 draft artifacts exist.",
        f"Missing section drafts: {', '.join(missing_section_paths)}",
        ["draft/full_draft.md", *missing_section_paths],
    )
    facts["full_draft_exists"] = fact_from_condition(
        True,
        "passed",
        "failed",
        "draft/full_draft.md exists.",
        "draft/full_draft.md is missing.",
        ["draft/full_draft.md"],
    )
    facts["section_drafts_match_section_tasks"] = fact_from_condition(
        not missing_section_paths,
        "passed",
        "blocked",
        "Every section task has a section draft.",
        f"Missing section drafts: {', '.join(missing_section_paths)}",
        missing_section_paths,
    )
    facts["template_sections_present_in_full_draft"] = fact_from_condition(
        not missing_headings,
        "passed",
        "blocked",
        "All template sections are present in full_draft.md.",
        f"Missing full draft headings: {', '.join(missing_headings)}",
        ["draft/full_draft.md"],
    )
    facts["draft_sections_are_in_task_order"] = fact_from_condition(
        section_positions == sorted(section_positions),
        "passed",
        "warning",
        "Draft sections follow task order.",
        "Draft sections are not in task order.",
        ["draft/full_draft.md"],
    )
    facts["source_support_sections_present"] = fact_from_condition(
        not any(item["category"] == "missing_source_support" for item in items),
        "passed",
        "blocked",
        "All available section drafts contain source support.",
        "At least one section draft is missing source support.",
        [item["artifact"] for item in items if item["category"] == "missing_source_support"],
    )
    facts["unresolved_questions_carried_forward"] = fact_from_condition(
        "Unresolved questions carried forward" in inputs.full_draft,
        "passed",
        "blocked",
        "Unresolved questions are carried forward.",
        "Unresolved questions are not carried forward in full_draft.md.",
        ["draft/full_draft.md", "plans/unresolved_questions.md"],
    )
    facts["knowledge_gaps_carried_forward"] = fact_from_condition(
        "Knowledge gaps carried forward" in inputs.full_draft,
        "passed",
        "blocked",
        "Knowledge gaps are carried forward.",
        "Knowledge gaps are not carried forward in full_draft.md.",
        ["draft/full_draft.md", "knowledge/knowledge_gaps.md"],
    )
    facts["review_artifacts_exist"] = {
        "status": "passed",
        "details": "Review artifacts are generated by review-run.",
        "related_artifacts": [
            "review/review_report.json",
            "review/template_review.md",
            "review/checklist_review.md",
            "review/evidence_review.md",
            "review/final_review.md",
        ],
    }
    facts["manifest_updated_to_phase_6"] = {
        "status": "passed",
        "details": "Manifest is updated to phase_6 / reviewed_verified by review-run.",
        "related_artifacts": ["manifest.json"],
    }

    category_fact_map = {
        "invalid_citation": [
            ("citation_ids_exist_in_citation_plan", "not found in citation_plan"),
            ("citation_ids_allowed_by_section_task", "not allowed by section task"),
            ("cited_sources_exist_in_source_index", "missing from source_index"),
        ],
        "sample_fact_source": [("sample_not_used_as_fact_source", "")],
        "expected_output_shape_fact_source": [("expected_output_shape_not_used_as_fact_source", "")],
        "reference_fact_misuse": [("reference_not_used_as_project_fact", "")],
        confirmation_category(rules): [
            ("hara_sensitive_sections_keep_confirmation_markers", f"missing {rules.confirmation_marker}")
        ],
        final_claim_category(rules): [("final_hara_conclusion_phrases_absent", "")],
        "phase_boundary_violation": [("no_later_phase_artifacts_generated", "")],
    }
    apply_category_facts(facts, items, category_fact_map)

    return {
        "items": items,
        "facts": facts,
        "tasks": tasks,
        "citation_rows": citation_rows,
        "missing_section_paths": missing_section_paths,
        "missing_headings": missing_headings,
        "metadata_issues": metadata_issues,
        "file_role_by_id": file_role_by_id,
    }


def analyze_task_citations(
    task: SectionTask,
    draft_text: str,
    details_by_id: dict[str, CitationEvidenceDetail],
    source_by_id: dict[str, Any],
    items: list[dict[str, Any]],
    citation_rows: list[dict[str, Any]],
) -> None:
    used_ids = sorted(set(EVIDENCE_ID_PATTERN.findall(draft_text)))
    for evidence_id in used_ids:
        detail = details_by_id.get(evidence_id)
        allowed = evidence_id in set(task.allowed_evidence)
        source_exists = bool(detail and detail.source_id in source_by_id)
        citation_rows.append(
            {
                "evidence_id": evidence_id,
                "task_id": task.task_id,
                "artifact": task.future_output_path,
                "used": True,
                "allowed": allowed,
                "source_id": detail.source_id if detail else "",
                "source_exists": source_exists,
                "usage": detail.usage if detail else "",
                "status": "ok" if detail and allowed and source_exists else "invalid",
            }
        )
        if detail is None:
            items.append(
                make_item(
                    "P0",
                    "invalid_citation",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Citation id {evidence_id} is not found in citation_plan.json.",
                    [evidence_id],
                    "Remove the citation or add valid citation planning in a later phase.",
                )
            )
        elif not allowed:
            items.append(
                make_item(
                    "P0",
                    "invalid_citation",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Citation id {evidence_id} is not allowed by section task {task.task_id}.",
                    [evidence_id],
                    "Use only evidence ids listed in the task allowed_evidence.",
                )
            )
        elif not source_exists:
            items.append(
                make_item(
                    "P0",
                    "invalid_citation",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Citation id {evidence_id} references a source_id missing from source_index.json.",
                    [evidence_id],
                    "Repair source traceability before using this citation.",
                )
            )


def analyze_source_support_lines(
    task: SectionTask,
    draft_text: str,
    file_role_by_id: dict[str, str],
    items: list[dict[str, Any]],
) -> None:
    for match in SOURCE_SUPPORT_PATTERN.finditer(draft_text):
        file_id = match.group("file_id")
        usage = match.group("usage")
        role = file_role_by_id.get(file_id, "")
        evidence_id = match.group("evidence_id")
        if role == "sample" and usage == "fact_support":
            items.append(
                make_item(
                    "P0",
                    "sample_fact_source",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Sample material {file_id} is shown as fact_support.",
                    [evidence_id],
                    "Remove the sample evidence or replace it with source evidence plus human confirmation.",
                )
            )
        if role == "expected_output_shape" and usage == "fact_support":
            items.append(
                make_item(
                    "P0",
                    "expected_output_shape_fact_source",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Expected-output-shape material {file_id} is shown as fact_support.",
                    [evidence_id],
                    "Remove the expected-output-shape evidence or replace it with source evidence.",
                )
            )
        if role == "reference" and usage == "fact_support":
            items.append(
                make_item(
                    "P1",
                    "reference_fact_misuse",
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Reference material {file_id} is shown as project fact_support.",
                    [evidence_id],
                    "Use reference material only as methodology, context, weak support, or confirmation context.",
                )
            )


def analyze_hara_confirmation(
    task: SectionTask,
    draft_text: str,
    items: list[dict[str, Any]],
    rules: DocumentTypeRules,
) -> None:
    if not is_sensitive_section(task.section_title, rules) and not task.requires_human_confirmation:
        return
    evidence_ids = sorted(set(EVIDENCE_ID_PATTERN.findall(draft_text)))
    category = confirmation_category(rules)
    if rules.confirmation_marker not in draft_text:
        items.append(
            make_item(
                "P0",
                category,
                task.section_id,
                task.task_id,
                task.future_output_path,
                f"{task.section_title} requires confirmation and is missing {rules.confirmation_marker}.",
                evidence_ids,
                f"Restore {rules.confirmation_marker} before Phase 7.",
            )
        )
        return
    if task.requires_human_confirmation:
        items.append(
            make_item(
                "P1",
                category,
                task.section_id,
                task.task_id,
                task.future_output_path,
                f"{task.section_title} requires human confirmation before final use.",
                evidence_ids[:3],
                f"Keep {rules.confirmation_marker} in draft or obtain human confirmation in Phase 7.",
            )
        )


def analyze_final_hara_phrases(
    task: SectionTask,
    draft_text: str,
    items: list[dict[str, Any]],
    rules: DocumentTypeRules,
) -> None:
    category = final_claim_category(rules)
    for line in draft_text.splitlines():
        lowered = line.strip().lower()
        if not lowered or any(allowed in lowered for allowed in ALLOWED_FINAL_CONTEXTS):
            continue
        if any(pattern in lowered for pattern in forbidden_final_patterns(rules)):
            items.append(
                make_item(
                    "P0",
                    category,
                    task.section_id,
                    task.task_id,
                    task.future_output_path,
                    f"Draft contains forbidden final claim phrase: {line.strip()}",
                    sorted(set(EVIDENCE_ID_PATTERN.findall(line))),
                    "Remove forbidden final claim language and keep the item pending confirmation.",
                )
            )


def analyze_checklist(inputs: Phase6Inputs, items: list[dict[str, Any]]) -> None:
    checklist_records = [file for file in inputs.inventory.files if file.role == "checklist"]
    if not checklist_records:
        items.append(
            make_item(
                "P1",
                "checklist_gap",
                "",
                "",
                "inputs/input_inventory.json",
                "No checklist material is declared in input_inventory.json.",
                [],
                "Add or confirm checklist material before final review.",
            )
        )
        return
    for record in checklist_records:
        if record.parse_status != "parsed":
            items.append(
                make_item(
                    "P1",
                    "checklist_gap",
                    "",
                    "",
                    "inputs/input_inventory.json",
                    f"Checklist material {record.file_id} parse status is {record.parse_status}.",
                    [],
                    "Provide a parsed checklist or carry this as a Phase 7 blocker.",
                )
            )


def analyze_global_boundaries(inputs: Phase6Inputs, items: list[dict[str, Any]]) -> None:
    if not contains_any(inputs.full_draft, GLOBAL_DRAFT_BOUNDARY_HEADINGS):
        items.append(
            make_item(
                "P1",
                "missing_boundary_note",
                "",
                "",
                "draft/full_draft.md",
                "Full draft is missing global draft boundary note.",
                [],
                "Restore the global draft boundary note.",
            )
        )
    if not contains_any(inputs.full_draft, GLOBAL_OPEN_CONFIRMATION_HEADINGS):
        items.append(
            make_item(
                "P1",
                "unresolved_question",
                "",
                "",
                "draft/full_draft.md",
                "Full draft is missing global open questions and required confirmations.",
                [],
                "Carry unresolved questions forward before Phase 7.",
            )
        )


def analyze_reference_fact_misuse(inputs: Phase6Inputs, items: list[dict[str, Any]]) -> None:
    for section in inputs.citation_plan.sections:
        for detail in section.evidence_details:
            if detail.source_role == "reference" and detail.usage == "fact_support":
                items.append(
                    make_item(
                        "P1",
                        "reference_fact_misuse",
                        section.section_id,
                        "",
                        "plans/citation_plan.json",
                        f"Reference evidence {detail.evidence_id} is marked fact_support.",
                        [detail.evidence_id],
                        "Use reference material only as methodology/context/weak support.",
                    )
                )


def analyze_later_phase_paths(run_dir: Path, items: list[dict[str, Any]]) -> None:
    for relative_path in LATER_PHASE_PATHS:
        path = run_dir / relative_path
        if not path.exists():
            continue
        for artifact_path in existing_artifact_paths(run_dir, relative_path):
            append_phase_boundary_violation(items, artifact_path)
    analyze_early_trace_directory(run_dir, items)


def analyze_early_trace_directory(run_dir: Path, items: list[dict[str, Any]]) -> None:
    trace_dir = run_dir / "trace"
    if not trace_dir.exists():
        return
    if not trace_dir.is_dir():
        append_phase_boundary_violation(items, "trace")
        return

    trace_files = [path for path in trace_dir.iterdir() if not path.name.startswith(".")]
    if not trace_files:
        append_phase_boundary_violation(items, "trace")
        return

    for path in trace_files:
        relative_path = path.relative_to(run_dir).as_posix()
        if path.is_dir():
            append_phase_boundary_violation(items, relative_path)
            continue
        if path.name in FORBIDDEN_TRACE_FILES:
            append_phase_boundary_violation(items, relative_path)
            continue
        if path.name != ALLOWED_EARLY_TRACE_FILE:
            append_phase_boundary_violation(items, relative_path)
            continue
        if not valid_hitl_jsonl(path):
            append_phase_boundary_violation(
                items,
                relative_path,
                description="Phase 6 found an invalid early HITL trace artifact: trace/hitl_decisions.jsonl.",
                suggested_fix="Keep early HITL trace as valid JSONL or remove it before review-run.",
            )


def existing_artifact_paths(run_dir: Path, relative_path: str) -> list[str]:
    path = run_dir / relative_path
    if path.is_file():
        return [relative_path]
    if path.is_dir():
        children = [child.relative_to(run_dir).as_posix() for child in path.rglob("*") if not child.name.startswith(".")]
        return sorted(children) or [relative_path]
    return [relative_path]


def valid_hitl_jsonl(path: Path) -> bool:
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return False
        for line in lines:
            loaded = json.loads(line)
            if not isinstance(loaded, dict):
                return False
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return True


def append_phase_boundary_violation(
    items: list[dict[str, Any]],
    artifact: str,
    description: str | None = None,
    suggested_fix: str = "Remove later-phase artifact generation from Phase 6.",
) -> None:
    items.append(
        make_item(
            "P0",
            "phase_boundary_violation",
            "",
            "",
            artifact,
            description or f"Phase 7+ artifact exists during Phase 6: {artifact}.",
            [],
            suggested_fix,
        )
    )


def default_check_facts(rules: DocumentTypeRules) -> dict[str, dict[str, Any]]:
    if rules.task_type == "hara":
        confirmation_details = "HARA-sensitive sections keep NEEDS_USER_CONFIRMATION markers."
        final_claim_details = "No final HARA conclusion phrase was found."
    else:
        confirmation_details = rules.output_labels.get(
            "confirmation_marker_detail",
            f"{professional_judgment_label(rules, plural=True).capitalize()} keep {rules.confirmation_marker} markers.",
        )
        final_claim_details = rules.output_labels.get(
            "no_forbidden_final_claim_detail",
            "No forbidden final claim phrase was found.",
        )
    return {
        "citation_ids_parseable": {
            "status": "passed",
            "details": "All citation ids found by the deterministic parser are parseable.",
            "related_artifacts": ["draft/full_draft.md", "draft/section_*.md"],
        },
        "citation_ids_exist_in_citation_plan": {
            "status": "passed",
            "details": "All draft citation ids exist in citation_plan.json.",
            "related_artifacts": ["plans/citation_plan.json", "draft/section_*.md"],
        },
        "citation_ids_allowed_by_section_task": {
            "status": "passed",
            "details": "All section draft citation ids are allowed by section_tasks.json.",
            "related_artifacts": ["plans/section_tasks.json", "draft/section_*.md"],
        },
        "cited_sources_exist_in_source_index": {
            "status": "passed",
            "details": "All cited sources exist in source_index.json.",
            "related_artifacts": ["knowledge/source_index.json", "plans/citation_plan.json"],
        },
        "sample_not_used_as_fact_source": {
            "status": "passed",
            "details": "Sample materials are not used as fact_support.",
            "related_artifacts": ["inputs/input_inventory.json", "draft/section_*.md"],
        },
        "expected_output_shape_not_used_as_fact_source": {
            "status": "passed",
            "details": "Expected-output-shape materials are not used as fact_support.",
            "related_artifacts": ["inputs/input_inventory.json", "draft/section_*.md"],
        },
        "reference_not_used_as_project_fact": {
            "status": "passed",
            "details": "Reference evidence is not used as project fact_support.",
            "related_artifacts": ["plans/citation_plan.json", "draft/section_*.md"],
        },
        "hara_sensitive_sections_keep_confirmation_markers": {
            "status": "passed",
            "details": confirmation_details,
            "related_artifacts": ["draft/section_*.md"],
        },
        "final_hara_conclusion_phrases_absent": {
            "status": "passed",
            "details": final_claim_details,
            "related_artifacts": ["draft/section_*.md"],
        },
        "no_later_phase_artifacts_generated": {
            "status": "passed",
            "details": "No Phase 7+ artifacts were generated.",
            "related_artifacts": [],
        },
    }


def apply_category_facts(
    facts: dict[str, dict[str, Any]],
    items: list[dict[str, Any]],
    category_fact_map: dict[str, list[tuple[str, str]]],
) -> None:
    for category, checks in category_fact_map.items():
        category_items = [item for item in items if item["category"] == category]
        if not category_items:
            continue
        for check_name, phrase in checks:
            if phrase:
                normalized_phrase = phrase.lower()
                matched_items = [
                    item for item in category_items if normalized_phrase in item["description"].lower()
                ]
            else:
                matched_items = category_items
            if not matched_items:
                continue
            worst_severity = "P0" if any(item["severity"] == "P0" for item in matched_items) else "P1"
            status = "failed" if worst_severity == "P0" else "blocked"
            facts[check_name] = {
                "status": status,
                "details": "; ".join(item["description"] for item in matched_items[:3]),
                "related_artifacts": sorted({item["artifact"] for item in matched_items if item["artifact"]}),
                "review_item_ids": [],
            }


def bind_review_item_ids(facts: dict[str, dict[str, Any]], review_items: list[dict[str, Any]]) -> None:
    for fact in facts.values():
        if fact.get("review_item_ids"):
            continue
        artifacts = set(fact.get("related_artifacts", []))
        details = fact.get("details", "")
        related_by_detail = [
            item["review_id"]
            for item in review_items
            if item["description"] in details
        ]
        if related_by_detail:
            fact["review_item_ids"] = related_by_detail
            continue
        fact["review_item_ids"] = [item["review_id"] for item in review_items if item["artifact"] in artifacts]


def fact_from_condition(
    condition: bool,
    pass_status: str,
    fail_status: str,
    pass_details: str,
    fail_details: str,
    related_artifacts: list[str],
) -> dict[str, Any]:
    return {
        "status": pass_status if condition else fail_status,
        "details": pass_details if condition else fail_details,
        "related_artifacts": related_artifacts,
        "review_item_ids": [],
    }


def make_item(
    severity: str,
    category: str,
    section_id: str,
    task_id: str,
    artifact: str,
    description: str,
    evidence_ids: list[str],
    suggested_fix: str,
    blocks_final: bool | None = None,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "category": category,
        "section_id": section_id,
        "task_id": task_id,
        "artifact": artifact,
        "description": description,
        "evidence_ids": dedupe(evidence_ids),
        "suggested_fix": suggested_fix,
        "status": "open",
        "blocks_final": severity in {"P0", "P1"} if blocks_final is None else blocks_final,
    }


def assign_review_ids(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stable_items = sorted(
        dedupe_items(items),
        key=lambda item: (
            severity_sort_key(item["severity"]),
            item["category"],
            item["section_id"],
            item["task_id"],
            item["artifact"],
            item["description"],
        ),
    )
    assigned: list[dict[str, Any]] = []
    for index, item in enumerate(stable_items, start=1):
        assigned.append({"review_id": f"REV-{index:03d}", **item})
    return assigned


def severity_sort_key(severity: str) -> int:
    return {"P0": 0, "P1": 1, "P2": 2, "Info": 3}.get(severity, 9)


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = (
            item["severity"],
            item["category"],
            item["section_id"],
            item["task_id"],
            item["artifact"],
            item["description"],
            tuple(item["evidence_ids"]),
        )
        if key not in seen:
            result.append(item)
            seen.add(key)
    return result


def build_review_report(
    inputs: Phase6Inputs,
    generated_at: str,
    review_items: list[dict[str, Any]],
    analysis: dict[str, Any],
    rules: DocumentTypeRules,
) -> dict[str, Any]:
    summary = build_review_summary(review_items, analysis)
    if summary["p0_items"] or summary["p1_items"]:
        status = "open_blockers"
    elif summary["p2_items"] or summary["info_items"]:
        status = "passed_with_warnings"
    else:
        status = "passed"

    return {
        "run_id": inputs.manifest.run_id,
        "generated_at": generated_at,
        "document_type": {
            "task_type": rules.task_type,
            "display_name": rules.display_name,
            "review_focus": list(rules.review_focus),
            "critical_claims": list(rules.critical_claims),
            "forbidden_final_claims": list(rules.forbidden_final_claims),
            "confirmation_marker": rules.confirmation_marker,
            "sample_policy": rules.sample_policy,
            "reference_policy": rules.reference_policy,
        },
        "status": status,
        "items": review_items,
        "summary": summary,
        "warnings": [],
    }


def build_review_summary(review_items: list[dict[str, Any]], analysis: dict[str, Any]) -> dict[str, Any]:
    p0 = sum(1 for item in review_items if item["severity"] == "P0")
    p1 = sum(1 for item in review_items if item["severity"] == "P1")
    p2 = sum(1 for item in review_items if item["severity"] == "P2")
    info = sum(1 for item in review_items if item["severity"] == "Info")
    blocking = sum(1 for item in review_items if item["blocks_final"])
    return {
        "total_items": len(review_items),
        "p0_items": p0,
        "p1_items": p1,
        "p2_items": p2,
        "info_items": info,
        "blocking_items": blocking,
        "template_items": sum(1 for item in review_items if item["category"] == "template_mismatch"),
        "checklist_items": sum(1 for item in review_items if item["category"] == "checklist_gap"),
        "evidence_items": sum(1 for item in review_items if item["category"] in {"invalid_citation", "missing_source_support"}),
        "final_readiness": "blocked" if blocking else "ready",
        "sections_reviewed": len(analysis["tasks"]),
        "draft_sections_expected": len(analysis["tasks"]),
        "draft_sections_found": len(analysis["tasks"]) - len(analysis["missing_section_paths"]),
    }


def render_template_review(inputs: Phase6Inputs, analysis: dict[str, Any], review_items: list[dict[str, Any]]) -> str:
    missing_sections = analysis["missing_section_paths"]
    extra_sections: list[str] = []
    lines = [
        "# 模板审查",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "## 摘要",
        "",
        f"- 预期章节数：{len(inputs.template_structure.outline_sections)}",
        f"- 已找到草稿章节数：{len(analysis['tasks']) - len(missing_sections)}",
        f"- 缺失章节：{', '.join(missing_sections) if missing_sections else 'None'}",
        f"- 额外章节：{', '.join(extra_sections) if extra_sections else 'None'}",
        f"- Status: {'blocked' if missing_sections else 'checked'}",
        "",
        "## 模板章节覆盖",
        "",
        "| Section id | 章节标题 | Expected | 在 full draft 中找到 | Section draft | Status |",
        "|---|---|---:|---:|---|---|",
    ]
    tasks_by_section = {task.section_id: task for task in analysis["tasks"]}
    for section in inputs.template_structure.outline_sections:
        task = tasks_by_section.get(section.section_id)
        draft_path = task.future_output_path if task else ""
        found = section.title in inputs.full_draft
        draft_found = bool(draft_path and draft_path in inputs.section_drafts)
        status = "ok" if found and draft_found else "missing"
        task_id = task.task_id if task else "no task"
        lines.append(
            f"| {section.section_id} | {section.title} ({task_id}) | true | {str(found).lower()} | {draft_path or 'None'} | {status} |"
        )
    lines.extend(["", "## 问题", ""])
    append_issue_lines(lines, [item for item in review_items if item["category"] == "template_mismatch"], "未发现模板问题。")
    lines.extend(
        [
            "## 说明",
            "",
            "- 模板审查是 deterministic 的。",
            "- 它检查结构覆盖，不判断专业正确性。",
            "",
        ]
    )
    return "\n".join(lines)


def render_checklist_review(
    inputs: Phase6Inputs,
    analysis: dict[str, Any],
    review_items: list[dict[str, Any]],
    rules: DocumentTypeRules,
) -> str:
    checklist_records = [file for file in inputs.inventory.files if file.role == "checklist"]
    confirmation_label = professional_judgment_label(rules, plural=True)
    lines = [
        "# Checklist 审查",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "## 摘要",
        "",
        f"- 检测到的 checklist 材料数：{len(checklist_records)}",
        f"- Checklist 解析状态：{', '.join(record.parse_status for record in checklist_records) if checklist_records else 'missing'}",
        f"- 已应用 deterministic checks：global boundary、source support、{rules.confirmation_marker}、{confirmation_label}、open questions",
        f"- Status: {'blocked' if any(item['category'] == 'checklist_gap' for item in review_items) else 'checked'}",
        "",
        "## Checklist 材料状态",
        "",
        "| File id | Path | Parse status | Role | Notes |",
        "|---|---|---|---|---|",
    ]
    for record in checklist_records:
        lines.append(f"| {record.file_id} | {record.path} | {record.parse_status} | {record.role} | {record.notes or 'None'} |")
    if not checklist_records:
        lines.append("| None | None | missing | checklist | 未发现 checklist 记录 |")

    built_in_checks = [
        ("全局草稿边界说明", "passed" if contains_any(inputs.full_draft, GLOBAL_DRAFT_BOUNDARY_HEADINGS) else "blocked", "P1", "full draft boundary note"),
        ("来源支持章节", analysis["facts"]["source_support_sections_present"]["status"], "P1", "每个 section draft 应包含 source support"),
        (f"{rules.confirmation_marker} 章节", "passed", "P1", "每个 section draft 应包含 confirmation section"),
        (
            "人工确认标记",
            analysis["facts"]["hara_sensitive_sections_keep_confirmation_markers"]["status"],
            "P0",
            f"{confirmation_label} keep {rules.confirmation_marker}",
        ),
        ("全局开放问题和必需确认", "passed" if contains_any(inputs.full_draft, GLOBAL_OPEN_CONFIRMATION_HEADINGS) else "blocked", "P1", "开放问题会继续带入"),
        ("阶段边界说明", "passed" if contains_any(inputs.full_draft, PHASE_BOUNDARY_HEADINGS) else "blocked", "P1", "阶段边界明确"),
    ]
    lines.extend(["", "## 内置草稿检查清单", "", "| Check | Status | Severity | Notes |", "|---|---|---|---|"])
    for check, status, severity, notes in built_in_checks:
        lines.append(f"| {check} | {status} | {severity} | {notes} |")

    lines.extend(["", "## 问题", ""])
    append_issue_lines(
        lines,
        [
            item
            for item in review_items
            if item["category"] in {"checklist_gap", "missing_boundary_note", confirmation_category(rules)}
        ],
        "未发现 checklist 问题。",
    )
    lines.extend(
        [
            "## 说明",
            "",
            "- Phase 6 checklist review 是 deterministic 的。",
            f"- 如果无法解析原始 checklist 文本，此审查仍会应用内置 {rules.display_name} 草稿检查。",
            "",
        ]
    )
    return "\n".join(lines)


def render_evidence_review(
    inputs: Phase6Inputs,
    analysis: dict[str, Any],
    review_items: list[dict[str, Any]],
    rules: DocumentTypeRules,
) -> str:
    used_ids = sorted({row["evidence_id"] for row in analysis["citation_rows"]})
    allowed_ids = sorted({evidence_id for task in inputs.section_tasks.tasks for evidence_id in task.allowed_evidence})
    invalid_ids = sorted({row["evidence_id"] for row in analysis["citation_rows"] if row["status"] != "ok"})
    missing_source_links = sorted({row["evidence_id"] for row in analysis["citation_rows"] if not row["source_exists"]})
    sample_misuse = item_categories(review_items, "sample_fact_source")
    expected_misuse = item_categories(review_items, "expected_output_shape_fact_source")
    lines = [
        "# 证据审查",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "## 摘要",
        "",
        f"- 草稿中使用的 evidence ids：{len(used_ids)}",
        f"- citation_plan 允许的 evidence ids：{len(allowed_ids)}",
        f"- 无效 evidence ids：{', '.join(invalid_ids) if invalid_ids else 'None'}",
        f"- 缺失 source links：{', '.join(missing_source_links) if missing_source_links else 'None'}",
        f"- Sample / expected_output_shape misuse: {len(sample_misuse) + len(expected_misuse)}",
        f"- Status: {'blocked' if invalid_ids or sample_misuse or expected_misuse else 'checked'}",
        "",
        "## 引用可追溯性",
        "",
        "| Evidence id | Used in draft | Allowed | Source id | Source exists | Usage | Status |",
        "|---|---:|---:|---|---:|---|---|",
    ]
    for row in analysis["citation_rows"]:
        lines.append(
            f"| {row['evidence_id']} | true | {str(row['allowed']).lower()} | {row['source_id'] or 'missing'} | {str(row['source_exists']).lower()} | {row['usage'] or 'missing'} | {row['status']} |"
        )
    lines.extend(["", "## 来源边界检查", ""])
    lines.append(f"- sample_fact_source issues: {len(sample_misuse)}")
    lines.append(f"- expected_output_shape_fact_source issues: {len(expected_misuse)}")
    lines.append(f"- reference_fact_misuse issues: {len(item_categories(review_items, 'reference_fact_misuse'))}")
    lines.extend(["", "## 确认检查", ""])
    append_issue_lines(lines, item_categories(review_items, confirmation_category(rules)), "未发现 confirmation 问题。")
    lines.extend(["## 问题", ""])
    append_issue_lines(
        lines,
        [
            item
            for item in review_items
            if item["category"]
            in {
                "invalid_citation",
                "missing_source_support",
                "sample_fact_source",
                "expected_output_shape_fact_source",
                "reference_fact_misuse",
                final_claim_category(rules),
            }
        ],
        "未发现 evidence 问题。",
    )
    return "\n".join(lines)


def render_final_review(
    inputs: Phase6Inputs,
    review_report: dict[str, Any],
    review_items: list[dict[str, Any]],
    rules: DocumentTypeRules,
) -> str:
    summary = review_report["summary"]
    blocking_items = [item for item in review_items if item["blocks_final"]]
    non_blocking_items = [item for item in review_items if not item["blocks_final"]]
    confirmation_items = item_categories(review_items, confirmation_category(rules))
    weak_or_unsupported = [
        item for item in review_items if item["category"] in {"weak_evidence", "unsupported_claim", "unresolved_question"}
    ]
    lines = [
        "# 最终审查",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "## 审查摘要",
        "",
        f"- P0: {summary['p0_items']}",
        f"- P1: {summary['p1_items']}",
        f"- P2: {summary['p2_items']}",
        f"- Info: {summary['info_items']}",
        f"- 阻塞项：{summary['blocking_items']}",
        f"- Final readiness: {summary['final_readiness']}",
        "",
        "## 阻塞问题",
        "",
    ]
    append_issue_lines(lines, blocking_items, "未发现 blocking issues。")
    lines.extend(["## 非阻塞问题", ""])
    append_issue_lines(lines, non_blocking_items, "未发现 non-blocking issues。")
    lines.extend(["## 需要人工确认", ""])
    append_issue_lines(lines, confirmation_items, "未发现 required human confirmations。")
    lines.extend(["## Unsupported / weak evidence", ""])
    append_issue_lines(lines, weak_or_unsupported, "unsupported 和 weak evidence 已记录在 citation_plan.json。")
    lines.extend(
        [
            "## 建议的 Phase 7 动作",
            "",
            "- 将所有 P0/P1 review items 转成 revision tasks。",
            f"- 除非记录 user confirmation，否则对 {professional_judgment_label(rules, plural=True)} 保留 {rules.confirmation_marker}。",
            "- 如果 unresolved questions 仍开放，则在最终交付中保留。",
            "",
            "## 阶段边界说明",
            "",
            "Phase 6 只创建 review 和 verification artifacts。",
            "修订推迟到 Phase 7。",
            "最终交付推迟到 Phase 7。",
            "Claude Code /write integration 推迟到 Phase 8。",
            "",
        ]
    )
    return "\n".join(lines)


def append_issue_lines(lines: list[str], issues: list[dict[str, Any]], empty_message: str) -> None:
    if not issues:
        lines.extend([empty_message, ""])
        return
    for item in issues:
        evidence = ", ".join(item["evidence_ids"]) if item["evidence_ids"] else "none"
        review_id = item.get("review_id", "REV-TBD")
        lines.append(
            f"- {review_id} | {item['severity']} | {item['category']} | {item['artifact']} | {item['description']} | evidence: {evidence}"
        )
    lines.append("")


def evidence_details_by_id(citation_plan: CitationPlanArtifact) -> dict[str, CitationEvidenceDetail]:
    return {
        detail.evidence_id: detail
        for section in citation_plan.sections
        for detail in section.evidence_details
    }


def item_categories(items: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    return [item for item in items if item["category"] == category]


def is_sensitive_section(section_title: str, rules: DocumentTypeRules) -> bool:
    lowered = section_title.lower()
    return any(marker in lowered for marker in sensitive_title_markers(rules))


def sensitive_title_markers(rules: DocumentTypeRules) -> tuple[str, ...]:
    configured = rules.terminology.get("sensitive_title_markers", "|".join(SENSITIVE_TITLE_MARKERS))
    return tuple(marker for marker in configured.split("|") if marker)


def confirmation_category(rules: DocumentTypeRules) -> str:
    if rules.task_type == "hara":
        return "hara_confirmation_required"
    return "critical_claim_confirmation_required"


def final_claim_category(rules: DocumentTypeRules) -> str:
    if rules.task_type == "hara":
        return "final_hara_conclusion"
    return "forbidden_final_claim"


def forbidden_final_patterns(rules: DocumentTypeRules) -> tuple[str, ...]:
    patterns = rules.forbidden_final_claims or FINAL_HARA_PATTERNS
    return tuple(pattern.lower() for pattern in patterns)


def professional_judgment_label(rules: DocumentTypeRules, plural: bool = False) -> str:
    key = "professional_judgments" if plural else "professional_judgment"
    fallback = "professional judgments" if plural else "professional judgment"
    return rules.terminology.get(key, fallback)


def update_manifest(run_dir: Path, manifest: Manifest, generated_at: str) -> None:
    new_records = [
        ArtifactRecord(path=artifact_path, kind=artifact_kind(artifact_path), created_at=generated_at)
        for artifact_path in REVIEW_ARTIFACTS
    ]
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status="reviewed_verified",
        phase="phase_6",
        artifacts=upsert_artifacts(manifest.artifacts, new_records),
        profile=manifest.profile,
    )
    write_json(run_dir / "manifest.json", updated_manifest.model_dump(exclude_defaults=True, exclude_none=True))


def artifact_kind(artifact_path: str) -> str:
    return {
        "review/review_report.json": "review_report",
        "review/template_review.md": "template_review",
        "review/checklist_review.md": "checklist_review",
        "review/evidence_review.md": "evidence_review",
        "review/final_review.md": "final_review",
        "verify/verify_report.json": "verify_report",
        "verify/failures.md": "verification_failures",
    }[artifact_path]


def upsert_artifacts(existing_artifacts: list[ArtifactRecord], new_artifacts: list[ArtifactRecord]) -> list[ArtifactRecord]:
    new_by_path = {artifact.path: artifact for artifact in new_artifacts}
    seen_paths: set[str] = set()
    updated: list[ArtifactRecord] = []
    for artifact in existing_artifacts:
        if artifact.path in seen_paths:
            continue
        seen_paths.add(artifact.path)
        updated.append(new_by_path.get(artifact.path, artifact))
    for artifact in new_artifacts:
        if artifact.path not in seen_paths:
            updated.append(artifact)
            seen_paths.add(artifact.path)
    return updated


def validate_json_model(path: Path, model_class: type[Any]) -> Any:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ReviewRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise ReviewRunError(f"Required artifact not found: {path}") from exc
    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise ReviewRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReviewRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ReviewRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise ReviewRunError(f"Required artifact not found: {path}") from exc
    if not isinstance(loaded, dict):
        raise ReviewRunError(f"Invalid JSON object in {path}")
    return loaded


def format_validation_error(exc: ValidationError) -> str:
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        messages.append(f"{location}: {error['msg']}")
    return "; ".join(messages)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(f"{encoded}\n", encoding="utf-8")
