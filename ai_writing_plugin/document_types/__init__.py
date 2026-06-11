from __future__ import annotations

from .base import DocumentTypeRules
from .fsr import FSR_RULES
from .generic_document import GENERIC_DOCUMENT_RULES
from .hara import HARA_RULES
from .test_report import TEST_REPORT_RULES
from .technical_solution import TECHNICAL_SOLUTION_RULES


_RULES_BY_TASK_TYPE: dict[str, DocumentTypeRules] = {
    HARA_RULES.task_type: HARA_RULES,
    TECHNICAL_SOLUTION_RULES.task_type: TECHNICAL_SOLUTION_RULES,
    TEST_REPORT_RULES.task_type: TEST_REPORT_RULES,
    FSR_RULES.task_type: FSR_RULES,
    GENERIC_DOCUMENT_RULES.task_type: GENERIC_DOCUMENT_RULES,
}


def get_document_type_rules(task_type: str | None) -> DocumentTypeRules:
    normalized_task_type = (task_type or "hara").strip().lower()
    normalized_task_type = normalized_task_type or "hara"
    try:
        return _RULES_BY_TASK_TYPE[normalized_task_type]
    except KeyError as exc:
        supported = ", ".join(supported_document_types())
        raise ValueError(f"Unsupported document type: {task_type}. Supported document types: {supported}") from exc


def supported_document_types() -> tuple[str, ...]:
    return tuple(_RULES_BY_TASK_TYPE)


from .context import get_rules_for_run, get_rules_for_task_brief, get_rules_for_task_type


__all__ = [
    "DocumentTypeRules",
    "FSR_RULES",
    "GENERIC_DOCUMENT_RULES",
    "HARA_RULES",
    "TEST_REPORT_RULES",
    "TECHNICAL_SOLUTION_RULES",
    "get_document_type_rules",
    "get_rules_for_run",
    "get_rules_for_task_brief",
    "get_rules_for_task_type",
    "supported_document_types",
]
