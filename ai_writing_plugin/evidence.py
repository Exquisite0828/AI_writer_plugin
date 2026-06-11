from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .document_types.base import DocumentTypeRules
from .document_types.context import get_rules_for_task_brief
from .models import (
    ArtifactRecord,
    EvidenceCandidate,
    EvidenceMapArtifact,
    EvidenceMapSummary,
    EvidenceQuestionMap,
    InputInventory,
    Manifest,
    OutlineSection,
    ResearchQuestion,
    ResearchQuestionsArtifact,
    ResearchQuestionsSummary,
    SourceIndex,
    SourceIndexSummary,
    SourceRecord,
    TaskBrief,
    TemplateStructure,
)
from .provenance import (
    evidence_status_for_tier,
    human_confirmation_status,
    provenance_support_type,
    source_tier_for_source,
    support_capabilities_for_tier,
)


class EvidenceRunError(Exception):
    """Raised when Phase 3 evidence mapping cannot complete."""


@dataclass(frozen=True)
class EvidenceRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class QuestionDraft:
    question_id: str
    section_id: str
    section_title: str
    section_intent: str
    question: str
    question_type: str
    requires_human_confirmation: bool
    priority: str
    expected_evidence_role: str


@dataclass(frozen=True)
class CandidateMatch:
    source: SourceRecord
    score: int
    confidence: float
    matched_terms: list[str]
    support_type: str


PHASE_3_ARTIFACTS = [
    ArtifactRecord(path="plans/research_questions.json", kind="research_questions", created_at=""),
    ArtifactRecord(path="plans/evidence_map.json", kind="evidence_map", created_at=""),
    ArtifactRecord(path="plans/unresolved_questions.md", kind="unresolved_questions", created_at=""),
]

OUTLINED_RUN_ERROR = "evidence-run requires an outlined Phase 2 run"

STOP_WORDS = {
    "the",
    "and",
    "or",
    "of",
    "to",
    "for",
    "in",
    "on",
    "with",
    "what",
    "which",
    "is",
    "are",
    "does",
    "do",
    "this",
    "that",
    "section",
    "report",
    "document",
    "available",
    "provide",
    "provided",
    "can",
    "any",
    "must",
    "remain",
    "enough",
}

QUESTION_TYPE_TERMS = {
    "scope": ["scope", "purpose", "boundary", "assumption", "out-of-scope"],
    "input_summary": ["item", "system", "function", "eps", "steering", "input", "output", "boundary"],
    "hazard": ["hazard", "malfunction", "failure", "loss", "unintended", "assist", "steering"],
    "hazardous_event": ["event", "operational", "situation", "mode", "scenario", "driving", "hazard"],
    "rating": ["severity", "exposure", "controllability", "asil", "risk", "rating"],
    "safety_goal": ["safety", "goal", "requirement", "mitigate", "prevent"],
    "open_issue": ["missing", "unsupported", "gap", "tbd", "unresolved"],
    "general": [],
}


def evidence_existing_run(run_dir: str | Path) -> EvidenceRunResult:
    run_path = Path(run_dir)
    generated_at = utc_timestamp()
    manifest, task_brief, _inventory, source_index, template_structure, knowledge_gaps, warnings = load_phase_3_inputs(
        run_path,
        generated_at,
    )
    rules = get_rules_for_task_brief(task_brief.model_dump())

    question_drafts = build_question_drafts(template_structure, rules)
    evidence_questions = build_evidence_questions(question_drafts, source_index, warnings)
    research_questions = build_research_questions(manifest.run_id, generated_at, evidence_questions, warnings, rules)
    evidence_map = build_evidence_map(manifest.run_id, generated_at, evidence_questions, warnings)

    plans_dir = run_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    write_json(plans_dir / "research_questions.json", research_questions.model_dump())
    write_json(plans_dir / "evidence_map.json", evidence_map.model_dump())
    (plans_dir / "unresolved_questions.md").write_text(
        render_unresolved_questions(manifest.run_id, evidence_questions, knowledge_gaps, rules),
        encoding="utf-8",
    )

    update_manifest(run_path, manifest, generated_at)
    return EvidenceRunResult(
        artifact_paths=[
            "plans/research_questions.json",
            "plans/evidence_map.json",
            "plans/unresolved_questions.md",
        ]
    )


def load_phase_3_inputs(
    run_dir: Path,
    generated_at: str,
) -> tuple[Manifest, TaskBrief, InputInventory, SourceIndex, TemplateStructure, str, list[str]]:
    if not run_dir.exists():
        raise EvidenceRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise EvidenceRunError(f"Run path is not a directory: {run_dir}")

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise EvidenceRunError(f"Required manifest.json not found: {manifest_path}")
    manifest = validate_json_model(manifest_path, Manifest)

    template_structure_path = run_dir / "plans" / "template_structure.json"
    outline_l1_path = run_dir / "plans" / "outline_l1.md"
    if manifest.phase not in {"phase_2", "phase_3"} or not template_structure_path.exists() or not outline_l1_path.exists():
        raise EvidenceRunError(OUTLINED_RUN_ERROR)

    task_brief_path = run_dir / "task_brief.json"
    if not task_brief_path.exists():
        raise EvidenceRunError(f"Required task_brief.json not found: {task_brief_path}")
    task_brief = validate_json_model(task_brief_path, TaskBrief)

    inventory_path = run_dir / "inputs" / "input_inventory.json"
    if not inventory_path.exists():
        raise EvidenceRunError(f"Required input_inventory.json not found: {inventory_path}")
    inventory = validate_json_model(inventory_path, InputInventory)

    template_structure = validate_json_model(template_structure_path, TemplateStructure)
    _ = outline_l1_path.read_text(encoding="utf-8")

    warnings: list[str] = []
    if template_structure.fallback_used:
        fallback_reason = template_structure.fallback_reason or "fallback template structure"
        warnings.append(f"fallback outline used: {fallback_reason}")

    source_index_path = run_dir / "knowledge" / "source_index.json"
    if source_index_path.exists():
        source_index = validate_json_model(source_index_path, SourceIndex)
    else:
        warnings.append("missing source_index")
        source_index = SourceIndex(
            run_id=manifest.run_id,
            generated_at=generated_at,
            sources=[],
            summary=SourceIndexSummary(total_sources=0, fact_sources=0, reference_sources=0, skipped_files=0),
        )

    if not source_index.sources:
        warnings.append("empty source_index")
    elif not any(source.source_role == "source" and source.is_fact_source for source in source_index.sources):
        warnings.append("no fact source candidates")

    knowledge_gaps_path = run_dir / "knowledge" / "knowledge_gaps.md"
    if knowledge_gaps_path.exists():
        knowledge_gaps = knowledge_gaps_path.read_text(encoding="utf-8")
    else:
        warnings.append("missing knowledge_gaps")
        knowledge_gaps = "missing knowledge_gaps"

    return manifest, task_brief, inventory, source_index, template_structure, knowledge_gaps, dedupe(warnings)


def build_question_drafts(template_structure: TemplateStructure, rules: DocumentTypeRules) -> list[QuestionDraft]:
    drafts: list[QuestionDraft] = []
    for section in sorted(template_structure.outline_sections, key=lambda item: item.order):
        for question_text in question_texts_for_section(section, rules):
            question_number = len(drafts) + 1
            question_type = infer_question_type(section.title, rules)
            requires_confirmation = section.needs_human_confirmation or requires_human_confirmation(section.title, rules)
            drafts.append(
                QuestionDraft(
                    question_id=f"Q-{question_number:03d}",
                    section_id=section.section_id,
                    section_title=section.title,
                    section_intent=section.intent,
                    question=question_text,
                    question_type=question_type,
                    requires_human_confirmation=requires_confirmation,
                    priority=priority_for_question(question_type, requires_confirmation),
                    expected_evidence_role=expected_role_for_question(question_type, requires_confirmation),
                )
            )
    return drafts


def question_texts_for_section(section: OutlineSection, rules: DocumentTypeRules) -> list[str]:
    title = section.title.lower()
    is_hara = is_hara_rules(rules)
    if "purpose" in title or "scope" in title:
        return [
            f"What is the purpose and scope of this {rules.display_name}?",
            "What system boundary is described by the input materials?",
            "Which assumptions or out-of-scope items are stated or missing?",
        ]
    if is_hara and "item definition" in title:
        return [
            "What are the main functions of the EPS item?",
            "What system inputs, outputs, and boundaries are described?",
            "What fallback, degraded, or driver takeover assumptions are available?",
        ]
    if is_hara and "hazardous" in title and "event" in title:
        return [
            "Which operational situations or modes can support hazardous event analysis?",
            "Is there enough source evidence to construct specific hazardous events?",
            "Which hazardous event candidates require human confirmation?",
        ]
    if is_hara and "hazard" in title:
        return [
            "What source material can support hazard identification for this item?",
            "Which hazard candidates require human confirmation?",
            "Which missing inputs prevent complete hazard identification?",
        ]
    if is_hara and any(marker in title for marker in ["s/e/c", "rating", "asil", "risk"]):
        return [
            "Do the input materials provide severity, exposure, or controllability rating evidence?",
            "Which S/E/C ratings must remain TBD or NEEDS_USER_CONFIRMATION?",
            "Is there enough evidence to support any final rating conclusion?",
        ]
    if is_hara and "safety goal" in title:
        return [
            "What source material can support safety goal candidates?",
            "Which safety goals can only be treated as candidates?",
            "Which safety goal decisions require human confirmation?",
        ]
    if "open issue" in title or "unresolved" in title:
        return [
            "Which required materials are missing, unsupported, or failed to parse?",
            "Which sections have weak or unsupported evidence?",
            "Which questions must be carried forward for user confirmation?",
        ]
    return [
        "What information is available to support this section?",
        "Which source chunks are relevant to this section?",
        "Which assumptions, missing inputs, or unresolved questions affect this section?",
    ]


def infer_question_type(section_title: str, rules: DocumentTypeRules) -> str:
    title = section_title.lower()
    is_hara = is_hara_rules(rules)
    if "purpose" in title or "scope" in title:
        return "scope"
    if is_hara and ("item definition" in title or "input materials" in title):
        return "input_summary"
    if is_hara and "hazardous" in title and "event" in title:
        return "hazardous_event"
    if is_hara and "hazard" in title:
        return "hazard"
    if is_hara and any(marker in title for marker in ["s/e/c", "rating", "asil", "risk"]):
        return "rating"
    if is_hara and "safety goal" in title:
        return "safety_goal"
    if "open issue" in title or "unresolved" in title:
        return "open_issue"
    return "general"


def requires_human_confirmation(section_title: str, rules: DocumentTypeRules) -> bool:
    title = section_title.lower()
    return any(marker in title for marker in sensitive_title_markers(rules))


def priority_for_question(question_type: str, requires_confirmation: bool) -> str:
    if requires_confirmation or question_type in {"scope", "input_summary", "open_issue"}:
        return "high"
    if question_type == "general":
        return "low"
    return "medium"


def expected_role_for_question(question_type: str, requires_confirmation: bool) -> str:
    if requires_confirmation:
        return "source_and_human_confirmation"
    if question_type == "open_issue":
        return "gap_or_user_confirmation"
    if question_type == "general":
        return "source_or_reference"
    return "source"


def build_evidence_questions(
    question_drafts: list[QuestionDraft],
    source_index: SourceIndex,
    warnings: list[str],
) -> list[EvidenceQuestionMap]:
    evidence_questions: list[EvidenceQuestionMap] = []
    evidence_counter = 1
    source_index_empty = not source_index.sources

    for draft in question_drafts:
        matches = [] if source_index_empty else match_evidence(draft, source_index.sources)
        candidates: list[EvidenceCandidate] = []
        for match in matches:
            source_tier = source_tier_for_source(match.source)
            capabilities = support_capabilities_for_tier(source_tier)
            candidates.append(
                EvidenceCandidate(
                    evidence_id=f"EVD-{evidence_counter:03d}",
                    source_id=match.source.source_id,
                    file_id=match.source.file_id,
                    source_role=match.source.source_role,
                    is_fact_source=match.source.is_fact_source,
                    source_tier=source_tier,
                    evidence_status=evidence_status_for_tier(source_tier),
                    can_support_project_fact=capabilities["can_support_project_fact"],
                    can_support_critical_claim=capabilities["can_support_critical_claim"],
                    human_confirmation_status=human_confirmation_status(
                        draft.requires_human_confirmation,
                        [{"source_tier": source_tier}],
                    ),
                    provenance_support_type=provenance_support_type(source_tier),
                    support_type=match.support_type,
                    confidence=match.confidence,
                    snippet=make_snippet(match.source.text),
                    matched_terms=match.matched_terms,
                )
            )
            evidence_counter += 1

        status = determine_status(candidates)
        evidence_questions.append(
            EvidenceQuestionMap(
                question_id=draft.question_id,
                section_id=draft.section_id,
                section_title=draft.section_title,
                question=draft.question,
                evidence_candidates=candidates,
                status=status,
                requires_human_confirmation=draft.requires_human_confirmation,
                unresolved_reason=determine_unresolved_reason(draft.requires_human_confirmation, status, candidates, warnings),
            )
        )
    return evidence_questions


def match_evidence(draft: QuestionDraft, sources: list[SourceRecord]) -> list[CandidateMatch]:
    terms = extract_terms(draft)
    matches: list[CandidateMatch] = []
    for source in sources:
        score, matched_terms = score_source(source, terms, draft.question_type)
        if score < 2 or not matched_terms:
            continue
        confidence = round(min(1.0, score / 10.0), 2)
        matches.append(
            CandidateMatch(
                source=source,
                score=score,
                confidence=confidence,
                matched_terms=matched_terms,
                support_type=determine_support_type(source, confidence),
            )
        )

    matches.sort(key=lambda item: (-item.score, item.source.source_id))
    return matches[:3]


def extract_terms(draft: QuestionDraft) -> list[str]:
    raw_text = " ".join([draft.section_title, draft.section_intent, draft.question])
    terms: list[str] = []
    for token in re.findall(r"[a-z][a-z0-9_-]{1,}", raw_text.lower()):
        if token in STOP_WORDS:
            continue
        terms.append(token)
    terms.extend(QUESTION_TYPE_TERMS.get(draft.question_type, []))
    return dedupe(terms)


def score_source(source: SourceRecord, terms: list[str], question_type: str) -> tuple[int, list[str]]:
    source_keywords = {keyword.lower() for keyword in source.keywords}
    title = source.title.lower()
    section = source.section.lower()
    text = source.text.lower()
    score = 0
    matched_terms: list[str] = []

    for term in terms:
        term_score = 0
        if term in source_keywords:
            term_score += 3
        if term in title:
            term_score += 2
        if term in section:
            term_score += 2
        if len(term) > 2 and term in text:
            term_score += 1
        if term_score:
            score += term_score
            matched_terms.append(term)

    if source.source_role == "source" and source.is_fact_source:
        score += 1
    if question_type in {"general", "open_issue", "rating", "hazard", "hazardous_event", "safety_goal"}:
        if source.source_role == "reference" and not source.is_fact_source:
            score += 1

    return score, dedupe(matched_terms)


def determine_support_type(source: SourceRecord, confidence: float) -> str:
    if confidence < 0.30:
        return "weak_keyword"
    if source.source_role == "source" and source.is_fact_source:
        if confidence >= 0.50:
            return "direct"
        return "context"
    if source.source_role == "reference" and not source.is_fact_source:
        return "methodology"
    return "weak_keyword"


def determine_status(candidates: list[EvidenceCandidate]) -> str:
    for candidate in candidates:
        if candidate.support_type == "direct" and candidate.confidence >= 0.50:
            return "supported"
    if candidates:
        return "weak"
    return "unsupported"


def determine_unresolved_reason(
    requires_confirmation: bool,
    status: str,
    candidates: list[EvidenceCandidate],
    warnings: list[str],
) -> str | None:
    if requires_confirmation:
        return "requires_human_confirmation"
    if status == "unsupported":
        if "empty source_index" in warnings:
            return "empty_source_index"
        return "no_matching_source_evidence"
    if status == "weak":
        if all(candidate.source_role == "reference" for candidate in candidates):
            return "only_methodology_or_context_evidence"
        return "only_methodology_or_context_evidence"
    return None


def make_snippet(text: str) -> str:
    normalized = text.strip()
    if len(normalized) <= 240:
        return normalized
    return normalized[:240].rstrip()


def build_research_questions(
    run_id: str,
    generated_at: str,
    evidence_questions: list[EvidenceQuestionMap],
    warnings: list[str],
    rules: DocumentTypeRules,
) -> ResearchQuestionsArtifact:
    research_questions: list[ResearchQuestion] = []
    draft_by_question_id = {question.question_id: question for question in evidence_questions}
    for question in evidence_questions:
        question_type = infer_question_type(question.section_title, rules)
        research_questions.append(
            ResearchQuestion(
                question_id=question.question_id,
                section_id=question.section_id,
                section_title=question.section_title,
                question=question.question,
                question_type=question_type,
                requires_human_confirmation=question.requires_human_confirmation,
                priority=priority_for_question(question_type, question.requires_human_confirmation),
                expected_evidence_role=expected_role_for_question(
                    question_type,
                    question.requires_human_confirmation,
                ),
                status=draft_by_question_id[question.question_id].status,
            )
        )

    return ResearchQuestionsArtifact(
        run_id=run_id,
        generated_at=generated_at,
        questions=research_questions,
        summary=ResearchQuestionsSummary(
            total_questions=len(research_questions),
            supported_questions=sum(1 for question in research_questions if question.status == "supported"),
            weak_questions=sum(1 for question in research_questions if question.status == "weak"),
            unsupported_questions=sum(1 for question in research_questions if question.status == "unsupported"),
            human_confirmation_required=sum(1 for question in research_questions if question.requires_human_confirmation),
            sections_covered=len({question.section_id for question in research_questions}),
        ),
        warnings=warnings,
    )


def build_evidence_map(
    run_id: str,
    generated_at: str,
    evidence_questions: list[EvidenceQuestionMap],
    warnings: list[str],
) -> EvidenceMapArtifact:
    candidates = [candidate for question in evidence_questions for candidate in question.evidence_candidates]
    return EvidenceMapArtifact(
        run_id=run_id,
        generated_at=generated_at,
        questions=evidence_questions,
        summary=EvidenceMapSummary(
            total_questions=len(evidence_questions),
            questions_with_candidates=sum(1 for question in evidence_questions if question.evidence_candidates),
            supported_questions=sum(1 for question in evidence_questions if question.status == "supported"),
            weak_questions=sum(1 for question in evidence_questions if question.status == "weak"),
            unsupported_questions=sum(1 for question in evidence_questions if question.status == "unsupported"),
            total_evidence_candidates=len(candidates),
            fact_source_candidates=sum(1 for candidate in candidates if candidate.is_fact_source),
            reference_candidates=sum(1 for candidate in candidates if candidate.source_role == "reference"),
            human_confirmation_required=sum(1 for question in evidence_questions if question.requires_human_confirmation),
        ),
        warnings=warnings,
    )


def render_unresolved_questions(
    run_id: str,
    evidence_questions: list[EvidenceQuestionMap],
    knowledge_gaps: str,
    rules: DocumentTypeRules,
) -> str:
    supported_count = sum(1 for question in evidence_questions if question.status == "supported")
    weak_questions = [question for question in evidence_questions if question.status == "weak"]
    unsupported_questions = [question for question in evidence_questions if question.status == "unsupported"]
    confirmation_questions = [question for question in evidence_questions if question.requires_human_confirmation]

    lines = [
        "# 未解决问题",
        "",
        f"Run id: {run_id}",
        f"Document type: {rules.display_name}",
        "",
        "## 摘要",
        "",
        f"- 问题总数：{len(evidence_questions)}",
        f"- Supported：{supported_count}",
        f"- Weak：{len(weak_questions)}",
        f"- Unsupported：{len(unsupported_questions)}",
        f"- 需要人工确认：{len(confirmation_questions)}",
        "",
        "## Unsupported 问题",
        "",
    ]
    append_question_list(lines, unsupported_questions, "无 unsupported 问题。")

    lines.extend(["## Weak evidence 问题", ""])
    append_question_list(lines, weak_questions, "无 weak evidence 问题。")

    lines.extend(["## 需要人工确认", ""])
    if confirmation_questions:
        for question in confirmation_questions:
            lines.append(
                f"- {question.question_id} | {question.section_id} | {question.section_title} | "
                f"仅有 candidate evidence；需要 human confirmation 和 {rules.confirmation_marker}。"
            )
    else:
        lines.append("无。")
    lines.append("")

    lines.extend(["## 从 knowledge gaps 带入的 missing / unsupported 材料", ""])
    append_knowledge_gap_summary(lines, knowledge_gaps)

    lines.extend(["## 需要 evidence 或 HITL 的 critical claims", ""])
    lines.extend(f"- {claim}" for claim in rules.critical_claims)
    lines.append("")

    lines.extend(
        [
            "## 阶段边界说明",
            "",
            "Phase 3 只创建 research questions、evidence_map 和 unresolved_questions。",
            "citation planning 推迟到 Phase 4。",
            "section tasks 和 writing plan 推迟到 Phase 4。",
            "草稿生成推迟到 Phase 5。",
            "审查和验证推迟到后续阶段。",
            rules.sample_policy,
            rules.reference_policy,
            "",
        ]
    )
    return "\n".join(lines)


def append_question_list(lines: list[str], questions: list[EvidenceQuestionMap], empty_message: str) -> None:
    if not questions:
        lines.extend([empty_message, ""])
        return
    for question in questions:
        reason = question.unresolved_reason or "needs confirmation"
        lines.append(f"- {question.question_id} | {question.section_id} | {question.section_title} | {reason}")
    lines.append("")


def append_knowledge_gap_summary(lines: list[str], knowledge_gaps: str) -> None:
    selected_lines: list[str] = []
    for line in knowledge_gaps.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if not stripped:
            continue
        if stripped.startswith("## ") and any(word in lowered for word in ["missing", "unsupported", "failed"]):
            selected_lines.append(stripped)
        elif stripped.startswith("- ") and any(word in lowered for word in ["missing", "unsupported", "failed"]):
            selected_lines.append(stripped)
    if not selected_lines and "missing knowledge_gaps" in knowledge_gaps:
        selected_lines.append("- missing knowledge_gaps")
    if not selected_lines:
        selected_lines.append("未记录 missing、unsupported 或 failed 材料。")
    lines.extend(selected_lines)
    lines.append("")


def sensitive_title_markers(rules: DocumentTypeRules) -> tuple[str, ...]:
    configured = rules.terminology.get("sensitive_title_markers", "")
    return tuple(marker for marker in configured.split("|") if marker)


def is_hara_rules(rules: DocumentTypeRules) -> bool:
    return rules.task_type == "hara"


def update_manifest(run_dir: Path, manifest: Manifest, generated_at: str) -> None:
    new_records = [
        ArtifactRecord(path=record.path, kind=record.kind, created_at=generated_at)
        for record in PHASE_3_ARTIFACTS
    ]
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status="evidence_mapped",
        phase="phase_3",
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
        raise EvidenceRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise EvidenceRunError(f"Invalid encoding in {path}: {exc}") from exc

    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise EvidenceRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


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
