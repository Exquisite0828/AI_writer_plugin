from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


_SEQUENCE_FIELDS = (
    "default_sections",
    "required_sections",
    "optional_sections",
    "critical_claims",
    "requires_human_confirmation",
    "forbidden_final_claims",
    "fact_source_roles",
    "non_fact_source_roles",
    "allowed_final_statuses",
    "review_focus",
    "verification_focus",
)


@dataclass(frozen=True)
class DocumentTypeRules:
    task_type: str
    display_name: str
    description: str

    default_sections: tuple[str, ...]
    required_sections: tuple[str, ...]
    optional_sections: tuple[str, ...]

    critical_claims: tuple[str, ...]
    requires_human_confirmation: tuple[str, ...]
    forbidden_final_claims: tuple[str, ...]
    confirmation_marker: str

    fact_source_roles: tuple[str, ...]
    non_fact_source_roles: tuple[str, ...]
    reference_policy: str
    sample_policy: str

    default_final_status: str
    allowed_final_statuses: tuple[str, ...]

    review_focus: tuple[str, ...]
    verification_focus: tuple[str, ...]
    candidate_learning_policy: str

    terminology: Mapping[str, str] = field(default_factory=dict)
    output_labels: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field_name in _SEQUENCE_FIELDS:
            object.__setattr__(self, field_name, tuple(getattr(self, field_name)))
        object.__setattr__(self, "terminology", MappingProxyType(dict(self.terminology)))
        object.__setattr__(self, "output_labels", MappingProxyType(dict(self.output_labels)))
