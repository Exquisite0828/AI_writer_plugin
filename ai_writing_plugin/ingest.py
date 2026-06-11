from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import (
    InputDeclaration,
    InputFileRecord,
    InputInventory,
    InputInventorySummary,
    SourceIndex,
    SourceIndexSummary,
    SourceRecord,
    TaskBrief,
)
from .provenance import build_provenance_index, source_tier_for_role, support_capabilities_for_tier
from .text_readers import SUPPORTED_FORMATS, read_supported_text


@dataclass(frozen=True)
class IngestResult:
    input_count: int
    artifact_paths: list[str]


def ingest_inputs(
    run_id: str,
    task_file: Path,
    run_dir: Path,
    inputs: list[InputDeclaration],
    generated_at: str,
    task_brief: TaskBrief,
) -> IngestResult:
    input_dir = run_dir / "inputs"
    knowledge_dir = run_dir / "knowledge"
    input_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    records: list[InputFileRecord] = []
    extracted_text_by_file_id: dict[str, str] = {}

    for index, declaration in enumerate(inputs, start=1):
        file_id = f"FILE-{index:03d}"
        record, extracted_text = build_file_record(file_id, task_file, declaration)
        records.append(record)
        if extracted_text is not None:
            extracted_text_by_file_id[file_id] = extracted_text

    inventory = InputInventory(
        run_id=run_id,
        generated_at=generated_at,
        files=records,
        summary=build_inventory_summary(records),
    )
    source_index = build_source_index(run_id, generated_at, records, extracted_text_by_file_id)
    provenance_index = build_provenance_index(
        run_id=run_id,
        generated_at=generated_at,
        task_brief=task_brief,
        inventory=inventory,
        source_index=source_index,
        hitl_trace_path=run_dir / "trace" / "hitl_decisions.jsonl",
    )

    write_json(input_dir / "input_inventory.json", inventory.model_dump())
    write_json(knowledge_dir / "source_index.json", source_index.model_dump())
    write_json(knowledge_dir / "provenance_index.json", provenance_index)
    write_knowledge_gaps(knowledge_dir / "knowledge_gaps.md", records)

    return IngestResult(
        input_count=len(records),
        artifact_paths=[
            "inputs/input_inventory.json",
            "knowledge/source_index.json",
            "knowledge/provenance_index.json",
            "knowledge/knowledge_gaps.md",
        ],
    )


def build_file_record(file_id: str, task_file: Path, declaration: InputDeclaration) -> tuple[InputFileRecord, str | None]:
    declared_path = declaration.path
    resolved_path = task_file.parent / declared_path
    file_format = resolved_path.suffix.lower().lstrip(".")
    title = declaration.title or resolved_path.stem
    is_fact_source = declaration.role == "source"

    parse_status = "parsed"
    error_message = ""
    extracted_text: str | None = None

    if not resolved_path.exists():
        parse_status = "missing"
        error_message = "File not found"
    elif file_format not in SUPPORTED_FORMATS:
        parse_status = "unsupported"
        error_message = f"Unsupported format: {file_format or 'none'}"
    else:
        try:
            extracted_text = read_supported_text(resolved_path, file_format)
        except Exception as exc:
            parse_status = "failed"
            error_message = str(exc)

    return (
        InputFileRecord(
            file_id=file_id,
            path=declared_path,
            role=declaration.role,
            format=file_format,
            parse_status=parse_status,
            is_fact_source=is_fact_source,
            title=title,
            notes=declaration.notes,
            error_message=error_message,
        ),
        extracted_text if parse_status == "parsed" else None,
    )


def build_inventory_summary(records: list[InputFileRecord]) -> InputInventorySummary:
    return InputInventorySummary(
        total_files=len(records),
        parsed_files=count_status(records, "parsed"),
        missing_files=count_status(records, "missing"),
        unsupported_files=count_status(records, "unsupported"),
        failed_files=count_status(records, "failed"),
        fact_source_files=sum(1 for record in records if record.is_fact_source),
        parsed_fact_source_files=sum(1 for record in records if record.is_fact_source and record.parse_status == "parsed"),
        non_fact_source_files=sum(1 for record in records if not record.is_fact_source),
        parsed_non_fact_source_files=sum(
            1 for record in records if not record.is_fact_source and record.parse_status == "parsed"
        ),
    )


def count_status(records: list[InputFileRecord], status: str) -> int:
    return sum(1 for record in records if record.parse_status == status)


def build_source_index(
    run_id: str,
    generated_at: str,
    records: list[InputFileRecord],
    extracted_text_by_file_id: dict[str, str],
) -> SourceIndex:
    sources: list[SourceRecord] = []

    for record in records:
        if record.parse_status != "parsed" or record.role not in {"source", "reference"}:
            continue

        extracted_text = extracted_text_by_file_id.get(record.file_id, "")
        for chunk in chunk_text(extracted_text, record.title, record.format):
            source_id = f"SRC-{len(sources) + 1:03d}"
            source_tier = source_tier_for_role(record.role)
            capabilities = support_capabilities_for_tier(source_tier)
            sources.append(
                SourceRecord(
                    source_id=source_id,
                    file_id=record.file_id,
                    path=record.path,
                    title=record.title,
                    section=chunk["section"],
                    anchor=chunk["anchor"],
                    text=chunk["text"],
                    keywords=extract_keywords(chunk["text"]),
                    source_role=record.role,
                    is_fact_source=record.is_fact_source,
                    source_tier=source_tier,
                    can_support_project_fact=capabilities["can_support_project_fact"],
                    can_support_methodology=capabilities["can_support_methodology"],
                    can_support_style=capabilities["can_support_style"],
                    can_support_critical_claim=capabilities["can_support_critical_claim"],
                    source_date=None,
                    owner=None,
                    char_start=chunk["char_start"],
                    char_end=chunk["char_end"],
                )
            )

    return SourceIndex(
        run_id=run_id,
        generated_at=generated_at,
        sources=sources,
        summary=SourceIndexSummary(
            total_sources=len(sources),
            fact_sources=sum(1 for source in sources if source.is_fact_source),
            reference_sources=sum(1 for source in sources if source.source_role == "reference"),
            skipped_files=sum(1 for record in records if record.file_id not in {source.file_id for source in sources}),
        ),
    )


def chunk_text(text: str, default_section: str, file_format: str) -> list[dict[str, Any]]:
    if file_format == "md":
        markdown_chunks = chunk_markdown(text, default_section)
        if markdown_chunks:
            return markdown_chunks

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    if not paragraphs and text.strip():
        paragraphs = [text.strip()]

    chunks: list[dict[str, Any]] = []
    current_parts: list[str] = []
    current_start: int | None = None
    search_from = 0

    for paragraph in paragraphs:
        paragraph_start = text.find(paragraph, search_from)
        if paragraph_start < 0:
            paragraph_start = search_from

        candidate = "\n\n".join([*current_parts, paragraph]) if current_parts else paragraph
        if current_parts and len(candidate) > 1200:
            chunk_text_value = "\n\n".join(current_parts)
            chunks.append(make_chunk(default_section, f"#chunk-{len(chunks) + 1:03d}", chunk_text_value, current_start or 0))
            current_parts = [paragraph]
            current_start = paragraph_start
        else:
            if not current_parts:
                current_start = paragraph_start
            current_parts.append(paragraph)

        search_from = paragraph_start + len(paragraph)

    if current_parts:
        chunk_text_value = "\n\n".join(current_parts)
        chunks.append(make_chunk(default_section, f"#chunk-{len(chunks) + 1:03d}", chunk_text_value, current_start or 0))

    return chunks


def chunk_markdown(text: str, default_section: str) -> list[dict[str, Any]]:
    heading_matches = list(re.finditer(r"(?m)^(#{1,6})\s+(.+?)\s*$", text))
    if not heading_matches:
        return []

    chunks: list[dict[str, Any]] = []
    for index, match in enumerate(heading_matches):
        start = match.start()
        end = heading_matches[index + 1].start() if index + 1 < len(heading_matches) else len(text)
        section = match.group(2).strip() or default_section
        body = text[start:end].strip()
        if not body or is_heading_only_chunk(body):
            continue
        chunks.append(make_chunk(section, slug_anchor(section, len(chunks) + 1), body, start))
    return chunks


def is_heading_only_chunk(text: str) -> bool:
    lines = text.strip().splitlines()
    if not lines:
        return True
    if not re.match(r"^#{1,6}\s+.+$", lines[0].strip()):
        return False
    return not any(line.strip() for line in lines[1:])


def make_chunk(section: str, anchor: str, text: str, start: int) -> dict[str, Any]:
    return {
        "section": section,
        "anchor": anchor,
        "text": text,
        "char_start": start,
        "char_end": start + len(text),
    }


def slug_anchor(section: str, index: int) -> str:
    slug = section.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return f"#{slug or f'chunk-{index:03d}'}"


def extract_keywords(text: str) -> list[str]:
    keywords: list[str] = []
    for match in re.finditer(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower()):
        keyword = match.group(0)
        if keyword not in keywords:
            keywords.append(keyword)
        if len(keywords) == 8:
            break
    return keywords


def write_knowledge_gaps(path: Path, records: list[InputFileRecord]) -> None:
    lines: list[str] = ["# Knowledge Gaps", ""]
    append_missing(lines, records)
    append_unsupported(lines, records)
    append_failed(lines, records)
    append_non_fact_source_exclusions(lines, records)
    lines.extend(
        [
            "## Notes for next phases",
            "",
            "- Template parsing is deferred to Phase 2.",
            "- Evidence mapping is deferred to Phase 3.",
            "- Samples and expected output shape must not be used as factual evidence.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def append_missing(lines: list[str], records: list[InputFileRecord]) -> None:
    lines.extend(["## Missing files", ""])
    missing = [record for record in records if record.parse_status == "missing"]
    if not missing:
        lines.extend(["None.", ""])
        return
    for record in missing:
        lines.append(f"- {record.file_id} | {record.path} | role={record.role} | title={record.title}")
    lines.append("")


def append_unsupported(lines: list[str], records: list[InputFileRecord]) -> None:
    lines.extend(["## Unsupported files", ""])
    unsupported = [record for record in records if record.parse_status == "unsupported"]
    if not unsupported:
        lines.extend(["None.", ""])
        return
    for record in unsupported:
        lines.append(f"- {record.file_id} | {record.path} | format={record.format} | role={record.role}")
    lines.append("")


def append_failed(lines: list[str], records: list[InputFileRecord]) -> None:
    lines.extend(["## Failed files", ""])
    failed = [record for record in records if record.parse_status == "failed"]
    if not failed:
        lines.extend(["None.", ""])
        return
    for record in failed:
        lines.append(f"- {record.file_id} | {record.path} | error={record.error_message}")
    lines.append("")


def append_non_fact_source_exclusions(lines: list[str], records: list[InputFileRecord]) -> None:
    lines.extend(["## Non-fact-source materials excluded from factual indexing", ""])
    excluded_roles = {"template", "checklist", "sample", "expected_output_shape"}
    excluded = [record for record in records if record.role in excluded_roles]
    if not excluded:
        lines.extend(["None.", ""])
        return
    for record in excluded:
        lines.append(f"- {record.file_id} | {record.path} | role={record.role} | is_fact_source=false")
    lines.append("")


def write_json(path: Path, data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(f"{encoded}\n", encoding="utf-8")
