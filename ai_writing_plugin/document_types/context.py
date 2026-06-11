from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from . import get_document_type_rules
from .base import DocumentTypeRules
from .profile_loader import load_document_profile


def get_rules_for_task_type(task_type: str | None) -> DocumentTypeRules:
    return get_document_type_rules(task_type)


def get_rules_for_task_brief(task_brief: Mapping[str, Any]) -> DocumentTypeRules:
    document_profile_path = clean_optional_string(task_brief.get("document_profile_path"))
    if document_profile_path:
        return load_document_profile(
            document_profile_path,
            expected_task_type=clean_optional_string(task_brief.get("task_type")),
        ).to_rules()

    rules = get_document_type_rules(task_brief.get("task_type"))
    if rules.task_type != "generic_document":
        return rules

    display_name = clean_optional_string(task_brief.get("display_name")) or rules.display_name
    task_critical_claims = clean_string_list(task_brief.get("critical_claims"))
    task_confirmations = clean_string_list(task_brief.get("requires_human_confirmation"))
    critical_claims = dedupe([*rules.critical_claims, *task_critical_claims])
    requires_human_confirmation = dedupe(
        [
            *rules.requires_human_confirmation,
            *task_confirmations,
            *task_critical_claims,
        ]
    )
    output_labels = {
        **rules.output_labels,
        "draft_title": f"{display_name} 保守草稿",
        "final_report_title": f"{display_name} 最终交付包",
        "open_items_heading": f"{display_name} 开放确认项",
        "confirmation_heading": f"{display_name} 开放确认项",
    }
    terminology = {
        **rules.terminology,
        "professional_judgment": f"{display_name} critical claim",
        "professional_judgments": f"{display_name} critical claims",
        "critical_claims_label": f"{display_name} critical claims",
        "critical_judgment_label": f"{display_name} critical claims",
        "confirmation_heading": f"{display_name} 开放确认项",
        "final_package_title": f"{display_name} 最终交付包",
    }
    return replace(
        rules,
        display_name=display_name,
        critical_claims=tuple(critical_claims),
        requires_human_confirmation=tuple(requires_human_confirmation),
        output_labels=output_labels,
        terminology=terminology,
    )


def get_rules_for_run(run_dir: str | Path) -> DocumentTypeRules:
    task_brief_path = Path(run_dir) / "task_brief.json"
    task_brief = json.loads(task_brief_path.read_text(encoding="utf-8"))
    if not isinstance(task_brief, dict):
        raise ValueError(f"Invalid task_brief.json: root must be an object: {task_brief_path}")
    return get_rules_for_task_brief(task_brief)


def clean_optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def clean_string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if stripped:
            cleaned.append(stripped)
    return cleaned


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(item)
    return result
