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
    InputFileRecord,
    InputInventory,
    Manifest,
    OutlineSection,
    TaskBrief,
    TemplateNode,
    TemplateSource,
    TemplateStructure,
    TemplateStructureSummary,
)


class OutlineRunError(Exception):
    """Raised when Phase 2 outline generation cannot complete."""


@dataclass(frozen=True)
class OutlineRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class MarkdownHeading:
    level: int
    title: str
    source_line: int


PHASE_2_ARTIFACTS = [
    ArtifactRecord(path="plans/template_structure.json", kind="template_structure", created_at=""),
    ArtifactRecord(path="plans/outline_l1.md", kind="outline_l1", created_at=""),
]


def outline_existing_run(run_dir: str | Path) -> OutlineRunResult:
    run_path = Path(run_dir)
    manifest, task_brief, inventory = load_phase_2_inputs(run_path)
    rules = get_rules_for_task_brief(task_brief.model_dump())
    generated_at = utc_timestamp()

    template_structure = build_template_structure(
        run_dir=run_path,
        manifest=manifest,
        inventory=inventory,
        generated_at=generated_at,
        rules=rules,
    )

    plans_dir = run_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    write_json(plans_dir / "template_structure.json", template_structure.model_dump())
    (plans_dir / "outline_l1.md").write_text(render_outline_l1(template_structure), encoding="utf-8")

    update_manifest(run_path, manifest, generated_at)
    return OutlineRunResult(artifact_paths=["plans/template_structure.json", "plans/outline_l1.md"])


def load_phase_2_inputs(run_dir: Path) -> tuple[Manifest, TaskBrief, InputInventory]:
    if not run_dir.exists():
        raise OutlineRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise OutlineRunError(f"Run path is not a directory: {run_dir}")

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise OutlineRunError(f"Required manifest.json not found: {manifest_path}")
    manifest = validate_json_model(manifest_path, Manifest)

    if manifest.phase not in {"phase_1", "phase_2"}:
        raise OutlineRunError(f"Run phase must be phase_1 or phase_2 before outline-run; got {manifest.phase}")

    task_brief_path = run_dir / "task_brief.json"
    if not task_brief_path.exists():
        raise OutlineRunError(f"Required task_brief.json not found: {task_brief_path}")
    task_brief = validate_json_model(task_brief_path, TaskBrief)

    inventory_path = run_dir / "inputs" / "input_inventory.json"
    if not inventory_path.exists():
        raise OutlineRunError(f"Required input_inventory.json not found: {inventory_path}")
    inventory = validate_json_model(inventory_path, InputInventory)

    return manifest, task_brief, inventory


def validate_json_model(path: Path, model_class: type[Any]) -> Any:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise OutlineRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise OutlineRunError(f"Invalid encoding in {path}: {exc}") from exc

    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise OutlineRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


def build_template_structure(
    run_dir: Path,
    manifest: Manifest,
    inventory: InputInventory,
    generated_at: str,
    rules: DocumentTypeRules,
) -> TemplateStructure:
    template_records = [record for record in inventory.files if record.role == "template"]
    selected_template = select_template(template_records)
    warnings: list[str] = []

    if selected_template is None:
        return build_fallback_structure(
            run_id=manifest.run_id,
            generated_at=generated_at,
            fallback_reason=determine_fallback_reason(template_records),
            warnings=warnings,
            rules=rules,
        )

    ignored_templates = [record for record in template_records if record is not selected_template and is_usable_template(record)]
    for ignored in ignored_templates:
        warnings.append(f"Ignored additional template input: {ignored.file_id} | {ignored.path}")

    task_path = resolve_task_file(manifest.task_file)
    template_path = task_path.parent / selected_template.path
    if not template_path.exists():
        return build_fallback_structure(
            run_id=manifest.run_id,
            generated_at=generated_at,
            fallback_reason="template missing",
            warnings=warnings,
            rules=rules,
        )

    template_text = template_path.read_text(encoding="utf-8")
    headings = parse_markdown_headings(template_text)
    if not headings:
        return build_fallback_structure(
            run_id=manifest.run_id,
            generated_at=generated_at,
            fallback_reason="template has no markdown headings",
            warnings=warnings,
            rules=rules,
        )

    nodes = build_template_nodes(headings, rules)
    outline_sections, document_title = build_outline_sections(nodes, rules)
    template_source = TemplateSource(
        file_id=selected_template.file_id,
        path=selected_template.path,
        title=selected_template.title,
        format=selected_template.format,
        parse_status=selected_template.parse_status,
    )

    return build_structure(
        run_id=manifest.run_id,
        generated_at=generated_at,
        status="parsed",
        template_source=template_source,
        fallback_used=False,
        fallback_reason="",
        document_title=document_title,
        nodes=nodes,
        outline_sections=outline_sections,
        warnings=warnings,
    )


def select_template(template_records: list[InputFileRecord]) -> InputFileRecord | None:
    for record in template_records:
        if is_usable_template(record):
            return record
    return None


def is_usable_template(record: InputFileRecord) -> bool:
    return record.role == "template" and record.parse_status == "parsed" and record.format == "md"


def determine_fallback_reason(template_records: list[InputFileRecord]) -> str:
    if not template_records:
        return "no template declared"

    first = template_records[0]
    if first.parse_status == "missing":
        return "template missing"
    if first.parse_status == "unsupported":
        return "template unsupported"
    if first.parse_status == "failed":
        return "template failed"
    if first.parse_status == "parsed" and first.format != "md":
        return "template format not supported for outline"
    return "no usable markdown template"


def resolve_task_file(task_file: str) -> Path:
    task_path = Path(task_file)
    if task_path.is_absolute():
        return task_path
    return Path.cwd() / task_path


def parse_markdown_headings(text: str) -> list[MarkdownHeading]:
    headings: list[MarkdownHeading] = []
    in_fence = False

    for line_number, line in enumerate(text.splitlines(), start=1):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match:
            continue
        title = match.group(2).strip()
        if not title:
            continue
        headings.append(MarkdownHeading(level=len(match.group(1)), title=title, source_line=line_number))

    return headings


def build_template_nodes(headings: list[MarkdownHeading], rules: DocumentTypeRules) -> list[TemplateNode]:
    node_data: list[dict[str, Any]] = []
    stack: list[dict[str, Any]] = []
    used_anchors: set[str] = set()

    for order, heading in enumerate(headings, start=1):
        while stack and stack[-1]["level"] >= heading.level:
            stack.pop()

        parent = stack[-1] if stack else None
        node_id = f"TPL-{order:03d}"
        optional = is_optional_title(heading.title)
        anchor = slug_anchor(heading.title, node_id, used_anchors)
        node = {
            "node_id": node_id,
            "title": heading.title,
            "level": heading.level,
            "order": order,
            "parent_id": parent["node_id"] if parent else None,
            "children": [],
            "required": not optional,
            "optional": optional,
            "intent": infer_intent(heading.title, rules),
            "source_line": heading.source_line,
            "anchor": anchor,
        }
        if parent:
            parent["children"].append(node_id)
        node_data.append(node)
        stack.append(node)

    return [TemplateNode.model_validate(node) for node in node_data]


def build_outline_sections(nodes: list[TemplateNode], rules: DocumentTypeRules) -> tuple[list[OutlineSection], str]:
    level_one_nodes = [node for node in nodes if node.level == 1]
    nodes_by_id = {node.node_id: node for node in nodes}

    if len(level_one_nodes) == 1 and level_one_nodes[0].children:
        document_title = level_one_nodes[0].title
        selected_nodes = [nodes_by_id[node_id] for node_id in level_one_nodes[0].children]
    else:
        min_level = min(node.level for node in nodes)
        document_title = ""
        selected_nodes = [node for node in nodes if node.level == min_level]

    sections: list[OutlineSection] = []
    for order, node in enumerate(selected_nodes, start=1):
        sections.append(
            OutlineSection(
                section_id=f"SEC-{order:03d}",
                template_node_id=node.node_id,
                title=node.title,
                order=order,
                required=node.required,
                intent=node.intent,
                anchor=node.anchor,
                needs_human_confirmation=needs_human_confirmation(node.title, rules),
            )
        )
    return sections, document_title


def build_fallback_structure(
    run_id: str,
    generated_at: str,
    fallback_reason: str,
    warnings: list[str],
    rules: DocumentTypeRules,
) -> TemplateStructure:
    headings = [
        MarkdownHeading(level=1, title=title, source_line=0)
        for title in rules.default_sections
    ]
    nodes = build_template_nodes(headings, rules)
    outline_sections, _document_title = build_outline_sections(nodes, rules)
    return build_structure(
        run_id=run_id,
        generated_at=generated_at,
        status="fallback",
        template_source=TemplateSource(file_id=None, path="", title="", format="", parse_status=""),
        fallback_used=True,
        fallback_reason=fallback_reason,
        document_title=f"{rules.display_name} fallback outline",
        nodes=nodes,
        outline_sections=outline_sections,
        warnings=warnings,
    )


def build_structure(
    run_id: str,
    generated_at: str,
    status: str,
    template_source: TemplateSource,
    fallback_used: bool,
    fallback_reason: str,
    document_title: str,
    nodes: list[TemplateNode],
    outline_sections: list[OutlineSection],
    warnings: list[str],
) -> TemplateStructure:
    return TemplateStructure(
        run_id=run_id,
        generated_at=generated_at,
        status=status,
        template_source=template_source,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        document_title=document_title,
        nodes=nodes,
        outline_sections=outline_sections,
        warnings=warnings,
        summary=TemplateStructureSummary(
            total_nodes=len(nodes),
            l1_sections=len(outline_sections),
            required_sections=sum(1 for section in outline_sections if section.required),
            optional_sections=sum(1 for section in outline_sections if not section.required),
            fallback_used=fallback_used,
            warnings_count=len(warnings),
        ),
    )


def is_optional_title(title: str) -> bool:
    lowered = title.lower()
    optional_markers = ["optional", "if applicable", "可选", "选填", "如适用"]
    return any(marker in lowered for marker in optional_markers)


def infer_intent(title: str, rules: DocumentTypeRules) -> str:
    lowered = title.lower()
    if any(marker in lowered for marker in ["purpose", "scope", "目标", "范围"]):
        return "说明文档目标、适用范围和边界。"
    if any(marker in lowered for marker in ["input", "assumption", "输入", "假设"]):
        return "汇总输入材料、约束和假设。"
    if rules.task_type == "hara":
        if any(marker in lowered for marker in ["item definition", "系统定义", "相关项定义"]):
            return "概述目标系统、功能边界和相关输入依据。"
        if any(marker in lowered for marker in ["operational", "mode", "场景", "工况"]):
            return "描述运行场景、使用模式和适用条件。"
        if any(marker in lowered for marker in ["hazard", "危害"]):
            return "组织危害识别相关内容，并保留人工确认边界。"
        if any(marker in lowered for marker in ["rating", "s/e/c", "asil", "risk", "风险"]):
            return "组织风险评级候选内容，并标记后续需要人工确认。"
        if any(marker in lowered for marker in ["safety goal", "安全目标"]):
            return "组织安全目标候选内容，并标记后续需要人工确认。"
    if any(marker in lowered for marker in ["risk", "风险"]):
        return "汇总风险、限制、开放问题和需要人工确认的内容。"
    if any(marker in lowered for marker in ["decision", "approval", "acceptance", "确认", "批准"]):
        return "汇总决策边界和需要人工确认的内容。"
    if any(marker in lowered for marker in ["open issue", "unresolved", "待确认"]):
        return "汇总未解决问题和需要人工确认的内容。"
    if any(marker in lowered for marker in ["review", "summary", "总结"]):
        return "汇总审查结论、限制和后续处理事项。"
    return "按模板要求组织该章节内容，并保持后续证据约束。"


def needs_human_confirmation(title: str, rules: DocumentTypeRules) -> bool:
    lowered = title.lower()
    markers = list(sensitive_title_markers(rules))
    if rules.task_type == "hara":
        markers.extend(["危害", "风险", "安全目标"])
    return any(marker in lowered for marker in markers)


def sensitive_title_markers(rules: DocumentTypeRules) -> tuple[str, ...]:
    configured = rules.terminology.get("sensitive_title_markers", "")
    return tuple(marker for marker in configured.split("|") if marker)


def slug_anchor(title: str, fallback: str, used_anchors: set[str]) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        slug = fallback.lower()

    candidate = f"#{slug}"
    suffix = 2
    while candidate in used_anchors:
        candidate = f"#{slug}-{suffix}"
        suffix += 1
    used_anchors.add(candidate)
    return candidate


def render_outline_l1(template_structure: TemplateStructure) -> str:
    lines: list[str] = [
        "# Outline L1",
        "",
        f"Run id: {template_structure.run_id}",
        f"Status: {template_structure.status}",
        f"Template source: {template_structure.template_source.path or 'fallback'}",
    ]

    if template_structure.fallback_used:
        lines.extend(["", f"Fallback note: {template_structure.fallback_reason}"])

    lines.extend(["", "## L1 Sections", ""])
    for section in template_structure.outline_sections:
        lines.extend(
            [
                f"## {section.section_id}. {section.title}",
                f"Required: {str(section.required).lower()}",
                f"Intent: {section.intent}",
                f"Template anchor: {section.anchor}",
                f"Human confirmation: {human_confirmation_note(section)}",
                "",
            ]
        )

    lines.extend(["## Warnings", ""])
    if template_structure.warnings:
        lines.extend(f"- {warning}" for warning in template_structure.warnings)
    else:
        lines.append("None.")

    lines.extend(
        [
            "",
            "## Phase boundary note",
            "",
            "- Phase 2 only creates template structure and L1 outline.",
            "- Evidence mapping is deferred to Phase 3.",
            "- Citation planning and section tasks are deferred to later phases.",
            "- Draft generation is not performed in Phase 2.",
            "- Sample documents are not used as factual sources.",
            "",
        ]
    )
    return "\n".join(lines)


def human_confirmation_note(section: OutlineSection) -> str:
    if section.needs_human_confirmation:
        return "required before final professional conclusion"
    return "not required for structure"


def update_manifest(run_dir: Path, manifest: Manifest, generated_at: str) -> None:
    new_records = [
        ArtifactRecord(path=record.path, kind=record.kind, created_at=generated_at)
        for record in PHASE_2_ARTIFACTS
    ]
    updated_artifacts = upsert_artifacts(manifest.artifacts, new_records)
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status="outlined",
        phase="phase_2",
        artifacts=updated_artifacts,
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
