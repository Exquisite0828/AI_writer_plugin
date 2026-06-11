from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .document_types.base import DocumentTypeRules
from .document_types.context import get_rules_for_task_brief
from .models import (
    ArtifactRecord,
    CitationEvidenceDetail,
    CitationPlanArtifact,
    CitationPlanSection,
    CitationPlanSummary,
    CitationSlot,
    EvidenceCandidate,
    EvidenceMapArtifact,
    EvidenceQuestionMap,
    InputInventory,
    Manifest,
    OutlineSection,
    ResearchQuestion,
    ResearchQuestionsArtifact,
    SectionTask,
    SectionTasksArtifact,
    SectionTasksSummary,
    SourceIndex,
    SourceRecord,
    TaskBrief,
    TemplateStructure,
    UnsupportedClaim,
    WeakEvidenceNote,
)
from .provenance import (
    build_claim_support_matrix,
    claim_status_for_support,
    evidence_status_for_tier,
    provenance_support_type,
    source_support_for_task,
    source_tier_for_source,
    support_capabilities_for_tier,
)


class PlanRunError(Exception):
    """Raised when Phase 4 writing planning cannot complete."""


@dataclass(frozen=True)
class PlanRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class Phase4Inputs:
    manifest: Manifest
    task_brief: TaskBrief
    inventory: InputInventory
    source_index: SourceIndex
    template_structure: TemplateStructure
    research_questions: ResearchQuestionsArtifact
    evidence_map: EvidenceMapArtifact
    unresolved_questions: str
    warnings: list[str]


PHASE_4_ARTIFACTS = [
    ArtifactRecord(path="plans/citation_plan.json", kind="citation_plan", created_at=""),
    ArtifactRecord(path="plans/claim_support_matrix.json", kind="claim_support_matrix", created_at=""),
    ArtifactRecord(path="plans/outline_final.md", kind="outline_final", created_at=""),
    ArtifactRecord(path="plans/section_tasks.json", kind="section_tasks", created_at=""),
    ArtifactRecord(path="plans/writing_plan.md", kind="writing_plan", created_at=""),
]

PHASE_3_REQUIRED_ERROR = "plan-run requires an evidence-mapped Phase 3 run"
SOURCE_INDEX_REQUIRED_ERROR = "source_index is required for citation traceability"
FORBIDDEN_SOURCES = ["sample", "expected_output_shape", "template", "checklist"]
TASK_SEPARATOR = "\u00b7"


def plan_existing_run(run_dir: str | Path) -> PlanRunResult:
    run_path = Path(run_dir)
    generated_at = utc_timestamp()
    inputs = load_phase_4_inputs(run_path)
    rules = get_rules_for_task_brief(inputs.task_brief.model_dump())

    citation_plan = build_citation_plan(inputs, generated_at, rules)
    section_tasks = build_section_tasks(inputs.manifest.run_id, generated_at, citation_plan, inputs.template_structure, rules)
    claim_support_matrix = build_claim_support_matrix(
        run_id=inputs.manifest.run_id,
        generated_at=generated_at,
        task_brief=inputs.task_brief,
        rules=rules,
        citation_plan=citation_plan,
        hitl_trace_path=run_path / "trace" / "hitl_decisions.jsonl",
    )

    plans_dir = run_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    write_json(plans_dir / "citation_plan.json", citation_plan.model_dump())
    write_json(plans_dir / "claim_support_matrix.json", claim_support_matrix)
    write_json(plans_dir / "section_tasks.json", section_tasks.model_dump())
    (plans_dir / "outline_final.md").write_text(
        render_outline_final(inputs.manifest.run_id, citation_plan, section_tasks, inputs.template_structure, rules),
        encoding="utf-8",
    )
    (plans_dir / "writing_plan.md").write_text(
        render_writing_plan(inputs.manifest.run_id, citation_plan, section_tasks, rules),
        encoding="utf-8",
    )

    update_manifest(run_path, inputs.manifest, generated_at)
    return PlanRunResult(
        artifact_paths=[
            "plans/citation_plan.json",
            "plans/claim_support_matrix.json",
            "plans/outline_final.md",
            "plans/section_tasks.json",
            "plans/writing_plan.md",
        ]
    )


def load_phase_4_inputs(run_dir: Path) -> Phase4Inputs:
    if not run_dir.exists():
        raise PlanRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise PlanRunError(f"Run path is not a directory: {run_dir}")

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise PlanRunError(f"Required manifest.json not found: {manifest_path}")
    manifest = validate_json_model(manifest_path, Manifest)

    required_phase_3_paths = [
        run_dir / "plans" / "template_structure.json",
        run_dir / "plans" / "outline_l1.md",
        run_dir / "plans" / "research_questions.json",
        run_dir / "plans" / "evidence_map.json",
        run_dir / "plans" / "unresolved_questions.md",
    ]
    if manifest.phase not in {"phase_3", "phase_4"} or any(not path.exists() for path in required_phase_3_paths):
        raise PlanRunError(PHASE_3_REQUIRED_ERROR)

    source_index_path = run_dir / "knowledge" / "source_index.json"
    if not source_index_path.exists():
        raise PlanRunError(SOURCE_INDEX_REQUIRED_ERROR)

    task_brief = validate_json_model(run_dir / "task_brief.json", TaskBrief)
    inventory = validate_json_model(run_dir / "inputs" / "input_inventory.json", InputInventory)
    source_index = validate_json_model(source_index_path, SourceIndex)
    template_structure = validate_json_model(run_dir / "plans" / "template_structure.json", TemplateStructure)
    research_questions = validate_json_model(run_dir / "plans" / "research_questions.json", ResearchQuestionsArtifact)
    evidence_map = validate_json_model(run_dir / "plans" / "evidence_map.json", EvidenceMapArtifact)
    unresolved_questions = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")
    _ = (run_dir / "plans" / "outline_l1.md").read_text(encoding="utf-8")

    warnings: list[str] = []
    if not source_index.sources:
        warnings.append("empty source_index")
    if not evidence_map.questions:
        warnings.append("empty evidence_map")

    return Phase4Inputs(
        manifest=manifest,
        task_brief=task_brief,
        inventory=inventory,
        source_index=source_index,
        template_structure=template_structure,
        research_questions=research_questions,
        evidence_map=evidence_map,
        unresolved_questions=unresolved_questions,
        warnings=warnings,
    )


def build_citation_plan(inputs: Phase4Inputs, generated_at: str, rules: DocumentTypeRules) -> CitationPlanArtifact:
    source_by_id = {source.source_id: source for source in inputs.source_index.sources}
    research_by_section = group_research_questions(inputs.research_questions.questions)
    evidence_by_question = {question.question_id: question for question in inputs.evidence_map.questions}
    evidence_seen: set[str] = set()
    warnings = list(inputs.warnings)
    sections: list[CitationPlanSection] = []
    slot_counter = 1
    unsupported_counter = 1

    for outline_section in sorted(inputs.template_structure.outline_sections, key=lambda item: item.order):
        section_questions = research_by_section.get(outline_section.section_id, [])
        if not section_questions:
            warnings.append(f"section has no questions: {outline_section.section_id}")

        requires_confirmation = section_requires_human_confirmation(outline_section, section_questions, evidence_by_question, rules)
        evidence_details: list[CitationEvidenceDetail] = []
        citation_slots: list[CitationSlot] = []
        unsupported_claims: list[UnsupportedClaim] = []
        weak_notes: list[WeakEvidenceNote] = []
        unresolved_question_ids: list[str] = []
        notes: list[str] = []

        question_details: dict[str, list[CitationEvidenceDetail]] = {}
        question_statuses: list[str] = []

        for question in section_questions:
            evidence_question = evidence_by_question.get(question.question_id)
            question_status = evidence_question.status if evidence_question else "unsupported"
            question_statuses.append(question_status)
            question_requires_confirmation = question.requires_human_confirmation or (
                evidence_question.requires_human_confirmation if evidence_question else False
            )

            details_for_question: list[CitationEvidenceDetail] = []
            for candidate in evidence_question.evidence_candidates if evidence_question else []:
                if candidate.evidence_id in evidence_seen:
                    warnings.append(f"evidence_id duplicated: {candidate.evidence_id}")
                    continue
                source = source_by_id.get(candidate.source_id)
                if source is None:
                    raise PlanRunError(f"source_id not found in source_index: {candidate.source_id}")
                detail = build_evidence_detail(candidate, question.question_id, source, question_requires_confirmation)
                evidence_seen.add(candidate.evidence_id)
                evidence_details.append(detail)
                details_for_question.append(detail)

            question_details[question.question_id] = details_for_question
            slot_status = citation_slot_status(question_status, question_requires_confirmation, details_for_question)
            citation_slots.append(
                CitationSlot(
                    slot_id=f"CIT-{slot_counter:03d}",
                    section_id=outline_section.section_id,
                    question_id=question.question_id,
                    claim_type=claim_type_for_question(question),
                    description=slot_description(question),
                    allowed_evidence=[detail.evidence_id for detail in details_for_question],
                    status=slot_status,
                    required_for_draft=True,
                    instruction=slot_instruction(slot_status, rules),
                )
            )
            slot_counter += 1

            if question_status != "supported" or question_requires_confirmation:
                unresolved_question_ids.append(question.question_id)
            if question_status == "unsupported" or question_requires_confirmation:
                unsupported_claims.append(
                    UnsupportedClaim(
                        claim_id=f"UNS-{unsupported_counter:03d}",
                        section_id=outline_section.section_id,
                        question_id=question.question_id,
                        description=unsupported_claim_description(question, question_status, question_requires_confirmation),
                        reason=unsupported_reason(question_status, question_requires_confirmation, details_for_question),
                        required_action=required_action(question_status, question_requires_confirmation, rules),
                    )
                )
                unsupported_counter += 1
            if question_status == "weak":
                weak_notes.append(
                    WeakEvidenceNote(
                        question_id=question.question_id,
                        note="Weak evidence must be carried forward as a conservative candidate, not a final fact.",
                        required_action=f"mark_{rules.confirmation_marker}_or_omit_final_conclusion",
                    )
                )

        allowed_evidence = dedupe([detail.evidence_id for detail in evidence_details])
        if not allowed_evidence:
            notes.append("section has no evidence")
            warnings.append(f"section has no evidence: {outline_section.section_id}")
        if requires_confirmation:
            notes.append("human confirmation required")
            warnings.append(f"human confirmation required: {outline_section.section_id}")

        sections.append(
            CitationPlanSection(
                section_id=outline_section.section_id,
                section_title=outline_section.title,
                order=outline_section.order,
                question_ids=[question.question_id for question in section_questions],
                allowed_evidence=allowed_evidence,
                evidence_details=evidence_details,
                citation_slots=citation_slots,
                unsupported_claims=unsupported_claims,
                weak_evidence_notes=weak_notes,
                requires_human_confirmation=requires_confirmation,
                evidence_status=section_evidence_status(question_statuses, requires_confirmation, allowed_evidence),
                unresolved_question_ids=dedupe(unresolved_question_ids),
                notes=dedupe(notes),
            )
        )

    return CitationPlanArtifact(
        run_id=inputs.manifest.run_id,
        generated_at=generated_at,
        sections=sections,
        summary=build_citation_summary(sections),
        warnings=dedupe(warnings),
    )


def group_research_questions(questions: list[ResearchQuestion]) -> dict[str, list[ResearchQuestion]]:
    grouped: dict[str, list[ResearchQuestion]] = {}
    for question in questions:
        grouped.setdefault(question.section_id, []).append(question)
    return grouped


def section_requires_human_confirmation(
    section: OutlineSection,
    questions: list[ResearchQuestion],
    evidence_by_question: dict[str, EvidenceQuestionMap],
    rules: DocumentTypeRules,
) -> bool:
    if section.needs_human_confirmation or sensitive_section(section.title, rules):
        return True
    for question in questions:
        if question.requires_human_confirmation:
            return True
        evidence_question = evidence_by_question.get(question.question_id)
        if evidence_question and evidence_question.requires_human_confirmation:
            return True
    return False


def sensitive_section(title: str, rules: DocumentTypeRules) -> bool:
    lowered = title.lower()
    return any(marker in lowered for marker in sensitive_title_markers(rules))


def build_evidence_detail(
    candidate: EvidenceCandidate,
    question_id: str,
    source: SourceRecord,
    question_requires_confirmation: bool,
) -> CitationEvidenceDetail:
    source_tier = source_tier_for_source(source)
    capabilities = support_capabilities_for_tier(source_tier)
    usage = evidence_usage(candidate, source, question_requires_confirmation)
    provenance_type = provenance_support_type(source_tier, usage)
    claim_status = claim_status_for_support(
        "",
        [{"source_tier": source_tier, "support_type": provenance_type}],
        question_requires_confirmation,
    )
    return CitationEvidenceDetail(
        evidence_id=candidate.evidence_id,
        question_id=question_id,
        source_id=candidate.source_id,
        file_id=source.file_id,
        source_role=source.source_role,
        is_fact_source=source.is_fact_source,
        source_tier=source_tier,
        evidence_status=evidence_status_for_tier(source_tier),
        can_support_project_fact=capabilities["can_support_project_fact"],
        can_support_critical_claim=capabilities["can_support_critical_claim"],
        human_confirmation_status=claim_status["human_confirmation_status"],
        provenance_support_type=provenance_type,
        claim_status=claim_status["claim_status"],
        support_type=candidate.support_type,
        confidence=candidate.confidence,
        usage=usage,
        snippet=candidate.snippet,
        matched_terms=candidate.matched_terms,
    )


def evidence_usage(candidate: EvidenceCandidate, source: SourceRecord, question_requires_confirmation: bool) -> str:
    if question_requires_confirmation:
        return "human_confirmation_context"
    if candidate.support_type == "weak_keyword":
        return "weak_support"
    if source.source_role == "source" and source.is_fact_source and candidate.support_type == "direct":
        return "fact_support"
    if source.source_role == "reference":
        if candidate.support_type == "methodology":
            return "methodology_support"
        return "context_support"
    return "context_support"


def citation_slot_status(
    question_status: str,
    question_requires_confirmation: bool,
    details_for_question: list[CitationEvidenceDetail],
) -> str:
    if question_requires_confirmation:
        return "requires_human_confirmation"
    if question_status == "unsupported" or not details_for_question:
        return "unsupported"
    if question_status == "supported" and any(detail.usage == "fact_support" for detail in details_for_question):
        return "filled"
    return "weak"


def claim_type_for_question(question: ResearchQuestion) -> str:
    mapping = {
        "scope": "scope",
        "input_summary": "input_summary",
        "hazard": "hazard_candidate",
        "hazardous_event": "hazardous_event_candidate",
        "rating": "rating_candidate",
        "safety_goal": "safety_goal_candidate",
        "open_issue": "open_issue",
        "general": "general",
    }
    return mapping.get(question.question_type, "general")


def slot_description(question: ResearchQuestion) -> str:
    return f"Use allowed evidence to address: {question.question}"


def slot_instruction(status: str, rules: DocumentTypeRules) -> str:
    if status == "requires_human_confirmation":
        return (
            f"Use only candidate evidence and mark {rules.confirmation_marker}. "
            f"Do not state final {professional_judgment_label(rules)}."
        )
    if status == "unsupported":
        return f"Do not add unsupported facts. Mark {rules.confirmation_marker} or omit the claim."
    if status == "weak":
        return "Use weak evidence conservatively and identify unresolved support limits."
    return "Use only allowed evidence. Do not add unsupported facts."


def unsupported_claim_description(
    question: ResearchQuestion,
    question_status: str,
    question_requires_confirmation: bool,
) -> str:
    if question_requires_confirmation:
        return "Final professional conclusion cannot be stated without human confirmation."
    if question_status == "unsupported":
        return f"Unsupported claim cannot be stated as fact for question {question.question_id}."
    return f"Weak claim must remain conservative for question {question.question_id}."


def unsupported_reason(
    question_status: str,
    question_requires_confirmation: bool,
    details_for_question: list[CitationEvidenceDetail],
) -> str:
    if question_requires_confirmation:
        return "requires_human_confirmation"
    if question_status == "unsupported" or not details_for_question:
        return "no_evidence"
    if all(detail.usage in {"methodology_support", "context_support"} for detail in details_for_question):
        return "methodology_only"
    return "weak_evidence"


def required_action(question_status: str, question_requires_confirmation: bool, rules: DocumentTypeRules) -> str:
    if question_requires_confirmation:
        return f"mark_{rules.confirmation_marker}_or_omit_final_conclusion"
    if question_status == "unsupported":
        return "omit_from_draft"
    return f"mark_{rules.confirmation_marker}"


def section_evidence_status(
    question_statuses: list[str],
    requires_confirmation: bool,
    allowed_evidence: list[str],
) -> str:
    if not question_statuses:
        return "unsupported"
    if requires_confirmation:
        return "mixed" if allowed_evidence or any(status == "supported" for status in question_statuses) else "unsupported"
    if all(status == "supported" for status in question_statuses):
        return "supported"
    if all(status == "unsupported" for status in question_statuses) and not allowed_evidence:
        return "unsupported"
    if any(status == "supported" for status in question_statuses):
        return "mixed"
    if allowed_evidence or any(status == "weak" for status in question_statuses):
        return "weak"
    return "unsupported"


def build_citation_summary(sections: list[CitationPlanSection]) -> CitationPlanSummary:
    slots = [slot for section in sections for slot in section.citation_slots]
    evidence_details = [detail for section in sections for detail in section.evidence_details]
    return CitationPlanSummary(
        total_sections=len(sections),
        sections_supported=sum(1 for section in sections if section.evidence_status == "supported"),
        sections_mixed=sum(1 for section in sections if section.evidence_status == "mixed"),
        sections_weak=sum(1 for section in sections if section.evidence_status == "weak"),
        sections_unsupported=sum(1 for section in sections if section.evidence_status == "unsupported"),
        total_citation_slots=len(slots),
        filled_slots=sum(1 for slot in slots if slot.status == "filled"),
        weak_slots=sum(1 for slot in slots if slot.status == "weak"),
        unsupported_slots=sum(1 for slot in slots if slot.status == "unsupported"),
        human_confirmation_slots=sum(1 for slot in slots if slot.status == "requires_human_confirmation"),
        total_allowed_evidence=sum(len(section.allowed_evidence) for section in sections),
        fact_support_evidence=sum(1 for detail in evidence_details if detail.usage == "fact_support"),
        methodology_or_context_evidence=sum(
            1 for detail in evidence_details if detail.usage in {"methodology_support", "context_support"}
        ),
    )


def build_section_tasks(
    run_id: str,
    generated_at: str,
    citation_plan: CitationPlanArtifact,
    template_structure: TemplateStructure,
    rules: DocumentTypeRules,
) -> SectionTasksArtifact:
    template_sections = {section.section_id: section for section in template_structure.outline_sections}
    tasks: list[SectionTask] = []
    for index, citation_section in enumerate(citation_plan.sections, start=1):
        template_section = template_sections[citation_section.section_id]
        writing_mode = writing_mode_for_section(citation_section)
        section_source_support = source_support_for_task(citation_section.evidence_details)
        section_claim_status = (
            "needs_confirmation"
            if citation_section.requires_human_confirmation
            else ("supported" if citation_section.evidence_status == "supported" else citation_section.evidence_status)
        )
        tasks.append(
            SectionTask(
                task_id=f"TASK-{index:03d}",
                section_id=citation_section.section_id,
                section_title=citation_section.section_title,
                order=citation_section.order,
                task_title=f"Draft {citation_section.section_title}",
                task_type=task_type_for_section(citation_section.section_title),
                writing_goal=writing_goal_for_section(citation_section.section_title, rules),
                writing_mode=writing_mode,
                allowed_evidence=citation_section.allowed_evidence,
                required_citation_slots=[slot.slot_id for slot in citation_section.citation_slots],
                evidence_status=citation_section.evidence_status,
                requires_human_confirmation=citation_section.requires_human_confirmation,
                unresolved_question_ids=citation_section.unresolved_question_ids,
                forbidden_sources=forbidden_sources_for_rules(rules),
                word_limit=300 if "open issue" in citation_section.section_title.lower() else 500,
                must_include=must_include_for_section(citation_section.section_title, rules),
                must_not_include=must_not_include_for_section(
                    citation_section.section_title,
                    citation_section.requires_human_confirmation,
                    rules,
                ),
                confirmation_markers=[rules.confirmation_marker] if citation_section.requires_human_confirmation else [],
                future_output_path=f"draft/section_{index:03d}.md",
                source_support_requirements="Every P0/P1 factual claim must cite one of the allowed evidence ids.",
                source_support=section_source_support,
                provenance_summary={
                    "claim_status": section_claim_status,
                    "evidence_status": citation_section.evidence_status,
                    "source_tiers": sorted({support["source_tier"] for support in section_source_support}),
                    "human_confirmation_status": (
                        "pending" if citation_section.requires_human_confirmation else "not_required"
                    ),
                },
                notes=task_notes(citation_section, template_section),
            )
        )

    return SectionTasksArtifact(
        run_id=run_id,
        generated_at=generated_at,
        tasks=tasks,
        summary=SectionTasksSummary(
            total_tasks=len(tasks),
            supported_tasks=sum(1 for task in tasks if task.evidence_status == "supported"),
            mixed_or_weak_tasks=sum(1 for task in tasks if task.evidence_status in {"mixed", "weak"}),
            unsupported_tasks=sum(1 for task in tasks if task.evidence_status == "unsupported"),
            human_confirmation_required=sum(1 for task in tasks if task.requires_human_confirmation),
        ),
        warnings=citation_plan.warnings,
    )


def task_type_for_section(section_title: str) -> str:
    title = section_title.lower()
    if "open issue" in title:
        return "issue_list"
    if any(marker in title for marker in ["s/e/c", "rating"]):
        return "table"
    return "prose"


def writing_mode_for_section(section: CitationPlanSection) -> str:
    title = section.section_title.lower()
    if "open issue" in title:
        return "open_issue_list"
    if section.requires_human_confirmation:
        if "safety goal" in title:
            return "conservative_candidate"
        return "confirmation_required"
    if section.evidence_status == "supported":
        return "evidence_grounded_summary"
    if section.evidence_status in {"mixed", "weak"}:
        return "conservative_candidate"
    return "unsupported_stub"


def writing_goal_for_section(section_title: str, rules: DocumentTypeRules) -> str:
    title = section_title.lower()
    if "purpose" in title or "scope" in title:
        return "Describe the document purpose, scope, input basis, and limitations using only allowed evidence."
    if "item definition" in title:
        return "Summarize the item function, system boundary, interfaces, and assumptions using only allowed evidence."
    if "open issue" in title:
        return "List unsupported, weak, and human-confirmation items that Phase 5 must carry forward."
    if any(marker in title for marker in sensitive_title_markers(rules)):
        return f"Prepare conservative candidate content with source support and {rules.confirmation_marker} markers."
    return "Prepare an evidence-grounded section using only allowed evidence and unresolved-question constraints."


def must_include_for_section(section_title: str, rules: DocumentTypeRules) -> list[str]:
    title = section_title.lower()
    marker = rules.confirmation_marker
    is_hara = is_hara_rules(rules)
    if "purpose" in title or "scope" in title:
        return ["document purpose", "scope", "input materials", "scope limitations"]
    if is_hara and "item definition" in title:
        return ["item function", "system boundary", "inputs / outputs", "assumptions"]
    if is_hara and "hazardous" in title:
        return ["operational situation candidates", "hazardous event candidates", "source support", marker]
    if is_hara and "hazard" in title:
        return ["hazard candidates", "source support", marker]
    if is_hara and any(marker in title for marker in ["s/e/c", "rating", "asil", "risk"]):
        return ["S?", "E?", "C?", "TBD", "rating support", rules.confirmation_marker]
    if is_hara and "safety goal" in title:
        return ["safety goal candidates", "source support", "human confirmation status"]
    if "open issue" in title:
        return [
            "unsupported questions",
            "weak evidence questions",
            "human confirmation required",
            "missing materials",
            "unsupported materials",
        ]
    return ["allowed evidence", "unresolved questions", "phase boundary"]


def must_not_include_for_section(section_title: str, requires_confirmation: bool, rules: DocumentTypeRules) -> list[str]:
    base = [
        "facts from sample documents",
        "facts from expected_output_shape",
        *[f"unconfirmed {claim}" for claim in rules.critical_claims],
        "unsupported professional conclusion",
    ]
    title = section_title.lower()
    is_hara = is_hara_rules(rules)
    if is_hara:
        base.append("final safety goal without human confirmation")
    if is_hara and ("purpose" in title or "scope" in title):
        base.extend(["unconfirmed ASIL", "unconfirmed hazard conclusion"])
    if is_hara and "item definition" in title:
        base.extend(["unsupported malfunction claims", "unconfirmed risk ratings"])
    if is_hara and "hazardous" in title:
        base.extend(["final hazardous event approval", "unconfirmed rating", "unconfirmed ASIL"])
    elif is_hara and "hazard" in title:
        base.extend(["final hazard validation", "final risk conclusion", "unconfirmed ASIL"])
    if is_hara and any(marker in title for marker in ["s/e/c", "rating", "asil", "risk"]):
        base.extend(["final severity rating", "final exposure rating", "final controllability rating", "final ASIL"])
    if is_hara and "safety goal" in title:
        base.extend(["final safety goal", "final acceptability conclusion"])
    if "open issue" in title:
        base.extend(["new facts", "resolved status unless backed by evidence or user decision"])
    if requires_confirmation:
        base.append("final professional conclusion")
    return dedupe(base)


def task_notes(citation_section: CitationPlanSection, template_section: OutlineSection) -> list[str]:
    notes = list(citation_section.notes)
    if not template_section.required:
        notes.append("template section is optional")
    if citation_section.unresolved_question_ids:
        notes.append("carry unresolved questions into Phase 5")
    return dedupe(notes)


def render_outline_final(
    run_id: str,
    citation_plan: CitationPlanArtifact,
    section_tasks: SectionTasksArtifact,
    template_structure: TemplateStructure,
    rules: DocumentTypeRules,
) -> str:
    template_sections = {section.section_id: section for section in template_structure.outline_sections}
    citation_by_section = {section.section_id: section for section in citation_plan.sections}
    lines = [
        "# 最终写作大纲",
        "",
        f"Run id: {run_id}",
        "",
        "Status: writing_planned",
        "",
        "## 来源 artifacts",
        "",
        "- template_structure.json",
        "- outline_l1.md",
        "- research_questions.json",
        "- evidence_map.json",
        "- citation_plan.json",
        "- unresolved_questions.md",
        "",
        "## 最终写作大纲",
        "",
    ]

    for task in section_tasks.tasks:
        citation_section = citation_by_section[task.section_id]
        template_section = template_sections[task.section_id]
        lines.extend(
            [
                f"### {task.task_id} {TASK_SEPARATOR} {task.section_title}",
                "",
                f"- Section id: {task.section_id}",
                f"- Required: {str(template_section.required).lower()}",
                f"- 证据状态：{task.evidence_status}",
                f"- Citation slots：{join_or_none(task.required_citation_slots)}",
                f"- Allowed evidence：{join_or_none(task.allowed_evidence)}",
                f"- 需要人工确认：{str(task.requires_human_confirmation).lower()}",
                f"- Writing mode：{task.writing_mode}",
                f"- 未来草稿文件：{task.future_output_path}",
                f"- 未解决问题：{join_or_none(citation_section.unresolved_question_ids)}",
                "",
            ]
        )

    lines.extend(["## 需要人工确认", ""])
    append_task_list(lines, [task for task in section_tasks.tasks if task.requires_human_confirmation], "无。")

    lines.extend(["## 继续带入的 unsupported / weak evidence", ""])
    append_task_list(
        lines,
        [task for task in section_tasks.tasks if task.evidence_status in {"mixed", "weak", "unsupported"}],
        "无。",
    )

    lines.extend(
        [
            "## 阶段边界说明",
            "",
            "Phase 4 只创建 citation_plan、outline_final、section_tasks 和 writing_plan。",
            "草稿生成推迟到 Phase 5。",
            "审查和验证推迟到后续阶段。",
            f"Phase 4 不形成最终 {professional_judgment_label(rules)}。",
            rules.sample_policy,
            "",
        ]
    )
    return "\n".join(lines)


def render_writing_plan(
    run_id: str,
    citation_plan: CitationPlanArtifact,
    section_tasks: SectionTasksArtifact,
    rules: DocumentTypeRules,
) -> str:
    lines = [
        "# 写作计划",
        "",
        f"Run id: {run_id}",
        "",
        "Status: writing_planned",
        "",
        "## 摘要",
        "",
        f"- 任务总数：{section_tasks.summary.total_tasks}",
        f"- Supported tasks：{section_tasks.summary.supported_tasks}",
        f"- Mixed / weak tasks：{section_tasks.summary.mixed_or_weak_tasks}",
        f"- Unsupported tasks：{section_tasks.summary.unsupported_tasks}",
        f"- 需要人工确认：{section_tasks.summary.human_confirmation_required}",
        "",
        "## 使用的输入",
        "",
        "- template_structure.json",
        "- outline_l1.md",
        "- research_questions.json",
        "- evidence_map.json",
        "- citation_plan.json",
        "- unresolved_questions.md",
        "",
        "## 写作顺序",
        "",
    ]
    for index, task in enumerate(section_tasks.tasks, start=1):
        lines.append(f"{index}. {task.task_id} {TASK_SEPARATOR} {task.section_title}")

    lines.extend(["", "## 任务详情", ""])
    for task in section_tasks.tasks:
        lines.extend(
            [
                f"### {task.task_id} {TASK_SEPARATOR} {task.section_title}",
                "",
                f"- Section id: {task.section_id}",
                f"- Writing mode：{task.writing_mode}",
                f"- 证据状态：{task.evidence_status}",
                f"- Allowed evidence：{join_or_none(task.allowed_evidence)}",
                f"- Required citation slots：{join_or_none(task.required_citation_slots)}",
                f"- 需要人工确认：{str(task.requires_human_confirmation).lower()}",
                f"- Must include：{join_or_none(task.must_include)}",
                f"- Must not include：{join_or_none(task.must_not_include)}",
                f"- 未来输出路径：{task.future_output_path}",
                "",
            ]
        )

    lines.extend(
        [
            "## Phase 5 引用规则",
            "",
            "- 只使用 citation_plan.json 中的 allowed evidence ids。",
            "- 不要把 sample、expected_output_shape、template 或 checklist 作为事实来源引用。",
            "- 不要把 unsupported claim 写成事实。",
            f"- 对 unresolved {professional_judgment_label(rules, plural=True)} 使用 {rules.confirmation_marker}。",
            f"- {rules.sample_policy}",
            f"- {rules.reference_policy}",
            "",
            "## 需要人工确认",
            "",
        ]
    )
    append_task_list(lines, [task for task in section_tasks.tasks if task.requires_human_confirmation], "无。")

    lines.extend(["## 继续带入的 unsupported / weak evidence", ""])
    append_carry_forward(lines, citation_plan)

    lines.extend(
        [
            "## 阶段边界说明",
            "",
            "Phase 4 停在 citation planning 和 writing task planning。",
            "Phase 4 不生成草稿文件。",
            "草稿生成从 Phase 5 开始。",
            "审查和验证推迟到 Phase 6。",
            "",
        ]
    )
    return "\n".join(lines)


def append_task_list(lines: list[str], tasks: list[SectionTask], empty_message: str) -> None:
    if not tasks:
        lines.extend([empty_message, ""])
        return
    for task in tasks:
        lines.append(f"- {task.task_id} | {task.section_id} | {task.section_title} | {task.writing_mode}")
    lines.append("")


def append_carry_forward(lines: list[str], citation_plan: CitationPlanArtifact) -> None:
    added = False
    for section in citation_plan.sections:
        for claim in section.unsupported_claims:
            lines.append(f"- {claim.question_id} | {section.section_id} | {claim.reason} | {claim.required_action}")
            added = True
        for note in section.weak_evidence_notes:
            lines.append(f"- {note.question_id} | {section.section_id} | weak_evidence | {note.required_action}")
            added = True
    if not added:
        lines.append("None.")
    lines.append("")


def forbidden_sources_for_rules(rules: DocumentTypeRules) -> list[str]:
    blocked = [role for role in rules.non_fact_source_roles if role != "reference"]
    return dedupe([*blocked, *FORBIDDEN_SOURCES])


def sensitive_title_markers(rules: DocumentTypeRules) -> tuple[str, ...]:
    configured = rules.terminology.get("sensitive_title_markers", "")
    return tuple(marker for marker in configured.split("|") if marker)


def professional_judgment_label(rules: DocumentTypeRules, plural: bool = False) -> str:
    key = "professional_judgments" if plural else "professional_judgment"
    fallback = "professional judgments" if plural else "professional judgment"
    return rules.terminology.get(key, fallback)


def is_hara_rules(rules: DocumentTypeRules) -> bool:
    return rules.task_type == "hara"


def join_or_none(values: list[str]) -> str:
    return ", ".join(values) if values else "None"


def update_manifest(run_dir: Path, manifest: Manifest, generated_at: str) -> None:
    new_records = [
        ArtifactRecord(path=record.path, kind=record.kind, created_at=generated_at)
        for record in PHASE_4_ARTIFACTS
    ]
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status="writing_planned",
        phase="phase_4",
        artifacts=upsert_artifacts(manifest.artifacts, new_records),
        profile=manifest.profile,
    )
    write_json(run_dir / "manifest.json", updated_manifest.model_dump(exclude_defaults=True, exclude_none=True))


def upsert_artifacts(
    existing_artifacts: list[ArtifactRecord],
    new_artifacts: list[ArtifactRecord],
) -> list[ArtifactRecord]:
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
        raise PlanRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise PlanRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise PlanRunError(f"Required artifact not found: {path}") from exc

    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise PlanRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


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
