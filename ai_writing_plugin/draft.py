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
    Manifest,
    SectionTask,
    SectionTasksArtifact,
    SourceIndex,
    TaskBrief,
)


class DraftRunError(Exception):
    """Raised when Phase 5 conservative drafting cannot complete."""


@dataclass(frozen=True)
class DraftRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class Phase5Inputs:
    manifest: Manifest
    task_brief: TaskBrief
    source_index: SourceIndex
    citation_plan: CitationPlanArtifact
    section_tasks: SectionTasksArtifact
    knowledge_gaps: str
    unresolved_questions: str


@dataclass(frozen=True)
class SectionDraft:
    task: SectionTask
    relative_path: str
    content: str


PHASE_4_REQUIRED_ERROR = "draft-run requires a writing-planned Phase 4 run"
SECTION_TASKS_REQUIRED_ERROR = "section_tasks is required"
CITATION_PLAN_REQUIRED_ERROR = "citation_plan is required for conservative drafting"
SOURCE_INDEX_REQUIRED_ERROR = "source_index is required for source support traceability"
NO_SECTION_TASKS_ERROR = "no section tasks available for drafting"
INVALID_DRAFT_OUTPUT_PATH_ERROR = "invalid draft output path"
TASK_SEPARATOR = "\u00b7"
PHASE_4_REQUIRED_PATHS = [
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/knowledge_gaps.md",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
    "plans/outline_final.md",
    "plans/writing_plan.md",
]


def draft_existing_run(run_dir: str | Path) -> DraftRunResult:
    run_path = Path(run_dir)
    generated_at = utc_timestamp()
    inputs = load_phase_5_inputs(run_path)
    rules = get_rules_for_task_brief(inputs.task_brief.model_dump())
    citation_sections = {section.section_id: section for section in inputs.citation_plan.sections}
    source_by_id = {source.source_id: source for source in inputs.source_index.sources}

    validate_source_traceability(inputs.citation_plan, source_by_id)
    output_paths = validate_task_output_paths(run_path, inputs.section_tasks.tasks)

    section_drafts: list[SectionDraft] = []
    for task in sorted(inputs.section_tasks.tasks, key=lambda item: (item.order, item.task_id)):
        citation_section = citation_sections.get(task.section_id)
        if citation_section is None:
            raise DraftRunError(f"citation_plan section missing for task: {task.task_id}")
        validate_task_evidence(task, citation_section)
        section_drafts.append(
            SectionDraft(
                task=task,
                relative_path=task.future_output_path,
                content=render_section_draft(task, citation_section, inputs, rules),
            )
        )

    draft_dir = run_path / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    for section_draft in section_drafts:
        output_path = output_paths[section_draft.relative_path]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(section_draft.content, encoding="utf-8")

    full_draft = render_full_draft(inputs, section_drafts, rules)
    (draft_dir / "full_draft.md").write_text(full_draft, encoding="utf-8")

    artifact_paths = [section.relative_path for section in section_drafts] + ["draft/full_draft.md"]
    update_manifest(run_path, inputs.manifest, generated_at, artifact_paths)
    return DraftRunResult(artifact_paths=artifact_paths)


def load_phase_5_inputs(run_dir: Path) -> Phase5Inputs:
    if not run_dir.exists():
        raise DraftRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise DraftRunError(f"Run path is not a directory: {run_dir}")

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise DraftRunError(f"Required manifest.json not found: {manifest_path}")
    manifest = validate_json_model(manifest_path, Manifest)
    if manifest.phase not in {"phase_4", "phase_5"} or manifest.status not in {"writing_planned", "drafted"}:
        raise DraftRunError(PHASE_4_REQUIRED_ERROR)

    section_tasks_path = run_dir / "plans" / "section_tasks.json"
    if not section_tasks_path.exists():
        raise DraftRunError(SECTION_TASKS_REQUIRED_ERROR)
    citation_plan_path = run_dir / "plans" / "citation_plan.json"
    if not citation_plan_path.exists():
        raise DraftRunError(CITATION_PLAN_REQUIRED_ERROR)
    source_index_path = run_dir / "knowledge" / "source_index.json"
    if not source_index_path.exists():
        raise DraftRunError(SOURCE_INDEX_REQUIRED_ERROR)

    missing_phase_4_paths = [relative_path for relative_path in PHASE_4_REQUIRED_PATHS if not (run_dir / relative_path).exists()]
    if missing_phase_4_paths:
        raise DraftRunError(PHASE_4_REQUIRED_ERROR)

    task_brief = validate_json_model(run_dir / "task_brief.json", TaskBrief)
    source_index = validate_json_model(source_index_path, SourceIndex)
    citation_plan = validate_json_model(citation_plan_path, CitationPlanArtifact)
    section_tasks = validate_json_model(section_tasks_path, SectionTasksArtifact)
    if not section_tasks.tasks:
        raise DraftRunError(NO_SECTION_TASKS_ERROR)

    knowledge_gaps = (run_dir / "knowledge" / "knowledge_gaps.md").read_text(encoding="utf-8")
    unresolved_questions = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")

    return Phase5Inputs(
        manifest=manifest,
        task_brief=task_brief,
        source_index=source_index,
        citation_plan=citation_plan,
        section_tasks=section_tasks,
        knowledge_gaps=knowledge_gaps,
        unresolved_questions=unresolved_questions,
    )


def validate_source_traceability(citation_plan: CitationPlanArtifact, source_by_id: dict[str, Any]) -> None:
    for section in citation_plan.sections:
        for detail in section.evidence_details:
            source = source_by_id.get(detail.source_id)
            if source is None:
                raise DraftRunError(f"source_id not found in source_index: {detail.source_id}")
            if detail.file_id != source.file_id:
                raise DraftRunError(f"source traceability mismatch for evidence: {detail.evidence_id}")
            if detail.source_role != source.source_role:
                raise DraftRunError(f"source traceability mismatch for evidence: {detail.evidence_id}")
            if detail.is_fact_source != source.is_fact_source:
                raise DraftRunError(f"source traceability mismatch for evidence: {detail.evidence_id}")


def validate_task_output_paths(run_dir: Path, tasks: list[SectionTask]) -> dict[str, Path]:
    draft_root = (run_dir / "draft").resolve()
    output_paths: dict[str, Path] = {}
    for task in tasks:
        relative_path = Path(task.future_output_path)
        if relative_path.is_absolute() or not relative_path.parts or relative_path.parts[0] != "draft":
            raise DraftRunError(INVALID_DRAFT_OUTPUT_PATH_ERROR)
        output_path = (run_dir / relative_path).resolve()
        try:
            output_path.relative_to(draft_root)
        except ValueError as exc:
            raise DraftRunError(INVALID_DRAFT_OUTPUT_PATH_ERROR) from exc
        if output_path == draft_root or output_path.suffix != ".md":
            raise DraftRunError(INVALID_DRAFT_OUTPUT_PATH_ERROR)
        output_paths[task.future_output_path] = output_path
    return output_paths


def validate_task_evidence(task: SectionTask, citation_section: CitationPlanSection) -> None:
    section_allowed = set(citation_section.allowed_evidence)
    detail_ids = {detail.evidence_id for detail in citation_section.evidence_details}
    missing = [evidence_id for evidence_id in task.allowed_evidence if evidence_id not in section_allowed or evidence_id not in detail_ids]
    if missing:
        raise DraftRunError(f"task allowed_evidence not found in citation_plan: {task.task_id}: {', '.join(missing)}")


def render_section_draft(
    task: SectionTask,
    citation_section: CitationPlanSection,
    inputs: Phase5Inputs,
    rules: DocumentTypeRules,
) -> str:
    details = evidence_details_for_task(task, citation_section)
    source_support = render_source_support(task, details, rules)
    draft_body = render_draft_body(task, citation_section, details, inputs, rules)
    confirmation = render_confirmation_section(task, citation_section, details, rules)
    limitations = render_limitations(task, citation_section, inputs)
    marker = rules.confirmation_marker
    judgment_label = professional_judgment_label(rules)
    lines = [
        f"# {task.section_title}",
        "",
        f"Task id: {task.task_id}",
        f"Section id: {task.section_id}",
        "Draft status: conservative_draft",
        f"Evidence status: {task.evidence_status}",
        f"Writing mode: {task.writing_mode}",
        f"Requires human confirmation: {str(task.requires_human_confirmation).lower()}",
        "Future review required: true",
        "",
        "## 来源支持",
        "",
        *source_support,
        "",
        "## 草稿正文",
        "",
        *draft_body,
        "",
        f"## {marker}",
        "",
        *confirmation,
        "",
        "## 限制和开放问题",
        "",
        *limitations,
        "",
        "## 草稿边界说明",
        "",
        "本章节是基于 section_tasks.json 和 citation_plan.json 生成的保守草稿。",
        "它只使用当前 section task 携带的 allowed evidence ids。",
        "不会输出缺少支持的专业结论。",
        f"不会形成最终 {judgment_label}。",
        "审查和验证推迟到 Phase 6。",
        "",
    ]
    return "\n".join(lines)


def evidence_details_for_task(task: SectionTask, citation_section: CitationPlanSection) -> list[CitationEvidenceDetail]:
    details_by_id = {detail.evidence_id: detail for detail in citation_section.evidence_details}
    return [details_by_id[evidence_id] for evidence_id in task.allowed_evidence if evidence_id in details_by_id]


def render_source_support(
    task: SectionTask,
    details: list[CitationEvidenceDetail],
    rules: DocumentTypeRules,
) -> list[str]:
    summary = task.provenance_summary or {}
    tiers = summary.get("source_tiers") or []
    first_detail = details[0] if details else None
    lines: list[str] = [
        f"- 声明状态：{summary.get('claim_status', 'unsupported')}",
        f"- 证据状态：{summary.get('evidence_status', task.evidence_status)}",
        f"- 来源层级：{', '.join(tiers) if tiers else 'NO_SOURCE'}",
        f"- 来源 ID：{first_detail.source_id if first_detail else 'NO_SOURCE'}",
        f"- 证据 ID：{first_detail.evidence_id if first_detail else 'NO_EVIDENCE'}",
        f"- 人工确认状态：{summary.get('human_confirmation_status', 'pending' if task.requires_human_confirmation else 'not_applicable')}",
    ]
    if not task.allowed_evidence:
        lines.append("- 本章节没有可用的 allowed evidence。")
        return lines

    for detail in details:
        lines.append(
            f"- {detail.evidence_id} | {detail.source_id} | {detail.file_id} | {detail.usage} | "
            f"confidence={detail.confidence:.2f} | source_tier={detail.source_tier or 'T5_AI_INFERENCE'} | "
            f"provenance_support_type={detail.provenance_support_type or 'inference'} | "
            f"claim_status={detail.claim_status or 'unsupported'} | "
            f"human_confirmation_status={detail.human_confirmation_status or 'not_applicable'}"
        )
        lines.append(f"  - 摘录：{detail.snippet}")
        if detail.source_role == "reference":
            lines.append(
                "  - reference evidence 仅用于方法、背景或弱支持，不能作为项目事实。"
            )
            lines.append(f"  - {rules.reference_policy}")
        elif detail.usage in {"methodology_support", "context_support", "weak_support", "human_confirmation_context"}:
            lines.append(
                "  - 此证据仅作为背景、弱支持或人工确认上下文。"
            )
    return lines


def render_draft_body(
    task: SectionTask,
    citation_section: CitationPlanSection,
    details: list[CitationEvidenceDetail],
    inputs: Phase5Inputs,
    rules: DocumentTypeRules,
) -> list[str]:
    if not details or task.writing_mode == "unsupported_stub":
        return render_unsupported_stub(task, rules)
    if task.writing_mode == "open_issue_list":
        return render_open_issue_list(task, citation_section, inputs, rules)
    if task.writing_mode == "confirmation_required" or is_hara_sensitive(task.section_title, rules):
        return render_confirmation_required(task, details, rules)
    if task.writing_mode == "conservative_candidate":
        return render_conservative_candidate(task, details, rules)
    return render_evidence_grounded_summary(task, details)


def render_evidence_grounded_summary(task: SectionTask, details: list[CitationEvidenceDetail]) -> list[str]:
    support_sentences = []
    for detail in details[:2]:
        support_sentences.append(f'allowed evidence 记录："{detail.snippet}" 来源支持：[{detail.evidence_id}]。')
    return [
        f"本章节只总结 {task.task_id} 的 allowed evidence。",
        *support_sentences,
        "文本保持保守，不添加超出已引用 source support 的事实。",
    ]


def render_conservative_candidate(
    task: SectionTask,
    details: list[CitationEvidenceDetail],
    rules: DocumentTypeRules,
) -> list[str]:
    evidence_ids = ", ".join(f"[{detail.evidence_id}]" for detail in details) or "no allowed evidence"
    first_snippet = details[0].snippet if details else "No allowed evidence available for this section."
    marker = rules.confirmation_marker
    judgment_label = professional_judgment_label(rules)
    return [
        f"{marker}: 使用这段候选语言前需要 pending human confirmation。",
        f"这是候选表达，仅有来自 {evidence_ids} 的有限支持。",
        f"候选依据：{first_snippet}",
        f"该候选内容保持 provisional，不陈述最终 {judgment_label}。",
    ]


def render_confirmation_required(
    task: SectionTask,
    details: list[CitationEvidenceDetail],
    rules: DocumentTypeRules,
) -> list[str]:
    marker = rules.confirmation_marker
    judgment_label = professional_judgment_label(rules)
    if is_rating_section(task.section_title, rules):
        evidence_ids = ", ".join(f"[{detail.evidence_id}]" for detail in details) or "No allowed evidence available"
        return [
            f"{marker}: 需要 pending human confirmation。",
            "",
            "| 候选项 | S | E | C | 结果 | 来源支持 | 确认状态 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| {task.section_title} candidate | S? | E? | C? | TBD | {evidence_ids} | {marker} pending |",
            "",
            f"不会形成最终 {judgment_label}。",
            "ASIL or risk level 在人工确认前保持 TBD。",
        ]

    rows = [
        f"{marker}: 需要 pending human confirmation。",
        "",
        "| 候选项 | 来源支持 | 确认状态 |",
        "| --- | --- | --- |",
    ]
    for detail in details[:3]:
        rows.append(f"| {task.section_title} candidate | [{detail.evidence_id}] | {marker} pending |")
    rows.extend(
        [
            "",
            "候选语言仅保留给合格人工审查者 review。",
            f"不会形成最终 {judgment_label}。",
        ]
    )
    return rows


def render_unsupported_stub(task: SectionTask, rules: DocumentTypeRules) -> list[str]:
    return [
        f"{rules.confirmation_marker}: 需要 pending evidence 或 user confirmation。",
        "本章节没有可用的 allowed evidence。",
        "当前 Phase 4 artifacts 不足以将本章节写成事实结论。",
        "不会输出缺少支持的专业结论。",
    ]


def render_open_issue_list(
    task: SectionTask,
    citation_section: CitationPlanSection,
    inputs: Phase5Inputs,
    rules: DocumentTypeRules,
) -> list[str]:
    lines = [
        "本章节只继续带入 unresolved items，不自动解决它们。",
        "",
        "| 问题类型 | 标识符 | 必需动作 | 状态 |",
        "| --- | --- | --- | --- |",
    ]
    added = False
    for question_id in citation_section.unresolved_question_ids:
        lines.append(f"| unresolved question | {question_id} | user or reviewer confirmation required | pending |")
        added = True
    for claim in citation_section.unsupported_claims:
        lines.append(f"| unsupported claim | {claim.claim_id} / {claim.question_id} | {claim.required_action} | pending |")
        added = True
    for note in citation_section.weak_evidence_notes:
        lines.append(f"| weak evidence | {note.question_id} | {note.required_action} | pending |")
        added = True
    if not added:
        lines.append("| 本章节未记录 | none | 当前 section task 无动作 | pending review |")
    lines.extend(
        [
            "",
            "知识缺口继续带入：见 knowledge/knowledge_gaps.md。",
            "未解决问题继续带入：见 plans/unresolved_questions.md。",
            f"任何需要 {professional_judgment_label(rules)} 的项目都适用 {rules.confirmation_marker}。",
        ]
    )
    return lines


def render_confirmation_section(
    task: SectionTask,
    citation_section: CitationPlanSection,
    details: list[CitationEvidenceDetail],
    rules: DocumentTypeRules,
) -> list[str]:
    needs_confirmation = task.requires_human_confirmation or task.evidence_status in {"mixed", "weak", "unsupported"} or not details
    if needs_confirmation:
        lines = [f"- {rules.confirmation_marker}: 下游报告使用前需要 pending human confirmation。"]
        for question_id in citation_section.unresolved_question_ids:
            lines.append(f"- {question_id}: pending.")
        for claim in citation_section.unsupported_claims:
            lines.append(f"- {claim.claim_id}: {claim.reason}; pending.")
        if not citation_section.unresolved_question_ids and not citation_section.unsupported_claims:
            lines.append("- 证据或 reviewer confirmation 仍保持 pending。")
        return lines
    return ["- section_tasks.json 未要求 human confirmation marker；后续 review 仍然必需。"]


def render_limitations(task: SectionTask, citation_section: CitationPlanSection, inputs: Phase5Inputs) -> list[str]:
    lines: list[str] = []
    if citation_section.unresolved_question_ids:
        lines.append(f"- 未解决问题：{', '.join(citation_section.unresolved_question_ids)}")
    for claim in citation_section.unsupported_claims:
        lines.append(f"- 继续带入 unsupported claim：{claim.claim_id} | {claim.reason} | {claim.required_action}")
    for note in citation_section.weak_evidence_notes:
        lines.append(f"- 继续带入 weak evidence：{note.question_id} | {note.required_action}")
    if not task.allowed_evidence:
        lines.append("- 本章节没有可用的 allowed evidence。")
    if not lines:
        lines.append("- 除后续 review 外，本 section task 未记录开放问题。")
    lines.append("- 知识缺口继续从 knowledge/knowledge_gaps.md 带入。")
    lines.append("- 未解决问题继续从 plans/unresolved_questions.md 带入。")
    return lines


def render_full_draft(
    inputs: Phase5Inputs,
    section_drafts: list[SectionDraft],
    rules: DocumentTypeRules,
) -> str:
    marker = rules.confirmation_marker
    judgments_label = professional_judgment_label(rules, plural=True)
    draft_title = rules.output_labels.get("draft_title", f"{rules.display_name} 保守草稿")
    lines = [
        f"# {draft_title}",
        "",
        f"Run id: {inputs.manifest.run_id}",
        f"Document type: {rules.display_name}",
        "",
        "Draft status: conservative_draft",
        "Source: section_tasks.json + citation_plan.json",
        "Not final: true",
        "",
        "## 全局草稿边界说明",
        "",
        "这是保守草稿。",
        "它仅使用 citation_plan.json 和 section_tasks.json 中允许的证据生成。",
        f"它不会形成最终 {judgments_label}。",
        f"{rules.display_name} 中需要确认、weak evidence 和 unsupported content 的内容会用 {marker} 标记。",
        "sample 和 expected-output-shape 材料不是事实证据。",
        rules.sample_policy,
        rules.reference_policy,
        "",
        "## 目录",
        "",
    ]
    for index, section_draft in enumerate(section_drafts, start=1):
        lines.append(f"{index}. {section_draft.task.task_id} {TASK_SEPARATOR} {section_draft.task.section_title}")

    lines.append("")
    for section_draft in section_drafts:
        lines.extend(["---", "", section_draft.content.rstrip(), ""])

    lines.extend(
        [
            "## 全局开放问题和必需确认",
            "",
            "### 必需确认项",
            "",
        ]
    )
    confirmation_tasks = [section.task for section in section_drafts if section.task.requires_human_confirmation]
    if confirmation_tasks:
        for task in confirmation_tasks:
            lines.append(f"- {task.task_id} | {task.section_id} | {task.section_title} | pending")
    else:
        lines.append("- section_tasks.json 未记录。")

    lines.extend(["", "### Unsupported claims", ""])
    unsupported_lines = global_unsupported_lines(inputs.citation_plan)
    lines.extend(unsupported_lines or ["- citation_plan.json 未记录。"])

    lines.extend(["", "### Weak evidence notes", ""])
    weak_lines = global_weak_lines(inputs.citation_plan)
    lines.extend(weak_lines or ["- citation_plan.json 未记录。"])

    lines.extend(
        [
            "",
            "### 继续带入的知识缺口",
            "",
            *summarize_markdown_lines(inputs.knowledge_gaps),
            "",
            "### 继续带入的未解决问题",
            "",
            *summarize_markdown_lines(inputs.unresolved_questions),
            "",
            "## 阶段边界说明",
            "",
            "Phase 5 只创建保守草稿文件。",
            "审查和验证推迟到 Phase 6。",
            "修订和最终交付推迟到后续阶段。",
            "Claude Code /write integration 推迟到 Phase 8。",
            "",
        ]
    )
    return "\n".join(lines)


def global_unsupported_lines(citation_plan: CitationPlanArtifact) -> list[str]:
    lines: list[str] = []
    for section in citation_plan.sections:
        for claim in section.unsupported_claims:
            lines.append(f"- {claim.claim_id} | {section.section_id} | {claim.question_id} | {claim.reason} | pending")
    return lines


def global_weak_lines(citation_plan: CitationPlanArtifact) -> list[str]:
    lines: list[str] = []
    for section in citation_plan.sections:
        for note in section.weak_evidence_notes:
            lines.append(f"- {note.question_id} | {section.section_id} | weak evidence | {note.required_action} | pending")
    return lines


def summarize_markdown_lines(text: str) -> list[str]:
    result: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "role=sample" in line or "role=expected_output_shape" in line:
            continue
        if line.startswith("#"):
            result.append(f"- {line.lstrip('#').strip()}")
        elif line.startswith("-"):
            result.append(line)
        if len(result) >= 12:
            break
    return result or ["- None recorded."]


def is_hara_sensitive(section_title: str, rules: DocumentTypeRules) -> bool:
    lowered = section_title.lower()
    return any(marker in lowered for marker in sensitive_title_markers(rules))


def is_rating_section(section_title: str, rules: DocumentTypeRules) -> bool:
    lowered = section_title.lower()
    return any(marker in lowered for marker in rating_title_markers(rules))


def sensitive_title_markers(rules: DocumentTypeRules) -> tuple[str, ...]:
    configured = rules.terminology.get("sensitive_title_markers", "")
    return tuple(marker for marker in configured.split("|") if marker)


def rating_title_markers(rules: DocumentTypeRules) -> tuple[str, ...]:
    configured = rules.terminology.get("rating_title_markers", "s/e/c|rating|asil|risk")
    return tuple(marker for marker in configured.split("|") if marker)


def professional_judgment_label(rules: DocumentTypeRules, plural: bool = False) -> str:
    key = "professional_judgments" if plural else "professional_judgment"
    fallback = "professional judgments" if plural else "professional judgment"
    return rules.terminology.get(key, fallback)


def update_manifest(run_dir: Path, manifest: Manifest, generated_at: str, artifact_paths: list[str]) -> None:
    new_records = [
        ArtifactRecord(path=artifact_path, kind=artifact_kind(artifact_path), created_at=generated_at)
        for artifact_path in artifact_paths
    ]
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status="drafted",
        phase="phase_5",
        artifacts=upsert_artifacts(manifest.artifacts, new_records),
        profile=manifest.profile,
    )
    write_json(run_dir / "manifest.json", updated_manifest.model_dump(exclude_defaults=True, exclude_none=True))


def artifact_kind(artifact_path: str) -> str:
    if artifact_path == "draft/full_draft.md":
        return "full_draft"
    return "section_draft"


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
        raise DraftRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise DraftRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise DraftRunError(f"Required artifact not found: {path}") from exc

    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise DraftRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


def format_validation_error(exc: ValidationError) -> str:
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        messages.append(f"{location}: {error['msg']}")
    return "; ".join(messages)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(f"{encoded}\n", encoding="utf-8")
