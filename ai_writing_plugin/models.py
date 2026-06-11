from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


InputRole = Literal["source", "template", "checklist", "reference", "sample", "expected_output_shape"]
ParseStatus = Literal["parsed", "missing", "unsupported", "failed"]
SourceRole = Literal["source", "reference"]
TemplateStructureStatus = Literal["parsed", "fallback"]
EvidenceStatus = Literal["supported", "weak", "unsupported"]
QuestionType = Literal[
    "scope",
    "input_summary",
    "hazard",
    "hazardous_event",
    "rating",
    "safety_goal",
    "open_issue",
    "general",
]
QuestionPriority = Literal["high", "medium", "low"]
ExpectedEvidenceRole = Literal[
    "source",
    "reference",
    "source_or_reference",
    "source_and_human_confirmation",
    "gap_or_user_confirmation",
]
EvidenceSupportType = Literal["direct", "methodology", "context", "weak_keyword"]
SectionEvidenceStatus = Literal["supported", "mixed", "weak", "unsupported"]
CitationSlotStatus = Literal["filled", "weak", "unsupported", "requires_human_confirmation"]
CitationEvidenceUsage = Literal[
    "fact_support",
    "methodology_support",
    "context_support",
    "weak_support",
    "human_confirmation_context",
]
ClaimType = Literal[
    "scope",
    "input_summary",
    "hazard_candidate",
    "hazardous_event_candidate",
    "rating_candidate",
    "safety_goal_candidate",
    "open_issue",
    "methodology_context",
    "general",
]
UnsupportedClaimReason = Literal[
    "no_evidence",
    "weak_evidence",
    "requires_human_confirmation",
    "methodology_only",
    "missing_material",
]
RequiredAction = Literal[
    "mark_NEEDS_USER_CONFIRMATION",
    "mark_NEEDS_USER_CONFIRMATION_or_omit_final_conclusion",
    "omit_from_draft",
    "ask_user_for_confirmation",
]
TaskType = Literal["prose", "table", "issue_list", "summary"]
WritingMode = Literal[
    "evidence_grounded_summary",
    "conservative_candidate",
    "confirmation_required",
    "unsupported_stub",
    "open_issue_list",
]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileMetadata(StrictBaseModel):
    profile_id: str
    profile_version: str
    profile_source: str
    profile_path: str = ""
    validation_status: str
    validation_errors: list[str] = Field(default_factory=list)

    @field_validator("profile_id", "profile_version", "profile_source", "validation_status", mode="before")
    @classmethod
    def validate_non_empty_profile_string(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped

    @field_validator("profile_path", mode="before")
    @classmethod
    def validate_profile_path(cls, value: object) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ValueError("profile_path must be a string")
        return value.strip()


class TaskConfig(StrictBaseModel):
    task_type: str
    task_title: str
    display_name: str | None = None
    target_audience: str
    output_format: str
    strict_template: bool
    allow_inference: bool
    critical_claims: list[str] = Field(default_factory=list)
    requires_human_confirmation: list[str]
    document_profile_path: str | None = None
    inputs: list["InputDeclaration"] = Field(default_factory=list)

    @field_validator("task_type", "task_title", "target_audience", "output_format", mode="before")
    @classmethod
    def validate_non_empty_string(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")

        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped

    @field_validator("display_name", mode="before")
    @classmethod
    def validate_optional_display_name(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("display_name must be a non-empty string when provided")
        stripped = value.strip()
        if not stripped:
            raise ValueError("display_name must be a non-empty string when provided")
        return stripped

    @field_validator("document_profile_path", mode="before")
    @classmethod
    def validate_optional_document_profile_path(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("document_profile_path must be a non-empty string when provided")
        stripped = value.strip()
        if not stripped:
            raise ValueError("document_profile_path must be a non-empty string when provided")
        return stripped

    @field_validator("critical_claims", mode="before")
    @classmethod
    def validate_critical_claims_list(cls, value: object) -> object:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("critical_claims must be a list")
        return value

    @field_validator("critical_claims")
    @classmethod
    def validate_critical_claim_items(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("critical_claims items must be non-empty strings")
            stripped = item.strip()
            if not stripped:
                raise ValueError("critical_claims items must be non-empty strings")
            cleaned.append(stripped)
        return cleaned

    @field_validator("requires_human_confirmation", mode="before")
    @classmethod
    def validate_confirmation_list(cls, value: object) -> object:
        if not isinstance(value, list):
            raise ValueError("requires_human_confirmation must be a list")
        if not value:
            raise ValueError("requires_human_confirmation must not be empty")
        return value

    @field_validator("requires_human_confirmation")
    @classmethod
    def validate_confirmation_items(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("requires_human_confirmation items must be non-empty strings")
            stripped = item.strip()
            if not stripped:
                raise ValueError("requires_human_confirmation items must be non-empty strings")
            cleaned.append(stripped)
        return cleaned


class InputDeclaration(StrictBaseModel):
    path: str
    role: InputRole
    title: str | None = None
    notes: str = ""

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("path must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError("path must be a non-empty string")
        return stripped

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("title must be a string")
        stripped = value.strip()
        return stripped or None

    @field_validator("notes", mode="before")
    @classmethod
    def validate_notes(cls, value: object) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ValueError("notes must be a string")
        return value.strip()


class TaskBrief(StrictBaseModel):
    run_id: str
    task_type: str
    task_title: str
    display_name: str | None = None
    target_audience: str
    output_format: str
    strict_template: bool
    allow_inference: bool
    critical_claims: list[str] = Field(default_factory=list)
    requires_human_confirmation: list[str]
    document_profile_path: str | None = None
    profile: ProfileMetadata | None = None


class ArtifactRecord(StrictBaseModel):
    path: str
    kind: str
    created_at: str


class Manifest(StrictBaseModel):
    run_id: str
    task_file: str
    created_at: str
    status: str
    phase: str
    artifacts: list[ArtifactRecord]
    profile: ProfileMetadata | None = None


class InputFileRecord(StrictBaseModel):
    file_id: str
    path: str
    role: InputRole
    format: str
    parse_status: ParseStatus
    is_fact_source: bool
    title: str
    notes: str
    error_message: str


class InputInventorySummary(StrictBaseModel):
    total_files: int
    parsed_files: int
    missing_files: int
    unsupported_files: int
    failed_files: int
    fact_source_files: int
    parsed_fact_source_files: int
    non_fact_source_files: int
    parsed_non_fact_source_files: int


class InputInventory(StrictBaseModel):
    run_id: str
    generated_at: str
    files: list[InputFileRecord]
    summary: InputInventorySummary


class SourceRecord(StrictBaseModel):
    source_id: str
    file_id: str
    path: str
    title: str
    section: str
    anchor: str
    text: str
    keywords: list[str]
    source_role: SourceRole
    is_fact_source: bool
    source_tier: str = ""
    can_support_project_fact: bool = False
    can_support_methodology: bool = False
    can_support_style: bool = False
    can_support_critical_claim: bool = False
    source_date: str | None = None
    owner: str | None = None
    char_start: int
    char_end: int


class SourceIndexSummary(StrictBaseModel):
    total_sources: int
    fact_sources: int
    reference_sources: int
    skipped_files: int


class SourceIndex(StrictBaseModel):
    run_id: str
    generated_at: str
    sources: list[SourceRecord]
    summary: SourceIndexSummary


class TemplateSource(StrictBaseModel):
    file_id: str | None
    path: str
    title: str
    format: str
    parse_status: str


class TemplateNode(StrictBaseModel):
    node_id: str
    title: str
    level: int
    order: int
    parent_id: str | None
    children: list[str]
    required: bool
    optional: bool
    intent: str
    source_line: int
    anchor: str


class OutlineSection(StrictBaseModel):
    section_id: str
    template_node_id: str
    title: str
    order: int
    required: bool
    intent: str
    anchor: str
    needs_human_confirmation: bool


class TemplateStructureSummary(StrictBaseModel):
    total_nodes: int
    l1_sections: int
    required_sections: int
    optional_sections: int
    fallback_used: bool
    warnings_count: int


class TemplateStructure(StrictBaseModel):
    run_id: str
    generated_at: str
    status: TemplateStructureStatus
    template_source: TemplateSource
    fallback_used: bool
    fallback_reason: str
    document_title: str
    nodes: list[TemplateNode]
    outline_sections: list[OutlineSection]
    warnings: list[str]
    summary: TemplateStructureSummary


class ResearchQuestion(StrictBaseModel):
    question_id: str
    section_id: str
    section_title: str
    question: str
    question_type: QuestionType
    requires_human_confirmation: bool
    priority: QuestionPriority
    expected_evidence_role: ExpectedEvidenceRole
    status: EvidenceStatus

    @field_validator("question_id", "section_id", "section_title", "question", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class ResearchQuestionsSummary(StrictBaseModel):
    total_questions: int
    supported_questions: int
    weak_questions: int
    unsupported_questions: int
    human_confirmation_required: int
    sections_covered: int


class ResearchQuestionsArtifact(StrictBaseModel):
    run_id: str
    generated_at: str
    questions: list[ResearchQuestion]
    summary: ResearchQuestionsSummary
    warnings: list[str]


class EvidenceCandidate(StrictBaseModel):
    evidence_id: str
    source_id: str
    file_id: str
    source_role: SourceRole
    is_fact_source: bool
    source_tier: str = ""
    evidence_status: str = ""
    can_support_project_fact: bool = False
    can_support_critical_claim: bool = False
    human_confirmation_status: str = "not_applicable"
    provenance_support_type: str = ""
    support_type: EvidenceSupportType
    confidence: float = Field(ge=0, le=1)
    snippet: str
    matched_terms: list[str]

    @field_validator("evidence_id", "source_id", "file_id", "snippet", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped

    @field_validator("matched_terms")
    @classmethod
    def validate_matched_terms(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("matched_terms items must be non-empty strings")
            stripped = item.strip()
            if not stripped:
                raise ValueError("matched_terms items must be non-empty strings")
            cleaned.append(stripped)
        if not cleaned:
            raise ValueError("matched_terms must not be empty")
        return cleaned


class EvidenceQuestionMap(StrictBaseModel):
    question_id: str
    section_id: str
    section_title: str
    question: str
    evidence_candidates: list[EvidenceCandidate]
    status: EvidenceStatus
    requires_human_confirmation: bool
    unresolved_reason: str | None

    @field_validator("question_id", "section_id", "section_title", "question", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class EvidenceMapSummary(StrictBaseModel):
    total_questions: int
    questions_with_candidates: int
    supported_questions: int
    weak_questions: int
    unsupported_questions: int
    total_evidence_candidates: int
    fact_source_candidates: int
    reference_candidates: int
    human_confirmation_required: int


class EvidenceMapArtifact(StrictBaseModel):
    run_id: str
    generated_at: str
    questions: list[EvidenceQuestionMap]
    summary: EvidenceMapSummary
    warnings: list[str]


class CitationEvidenceDetail(StrictBaseModel):
    evidence_id: str
    question_id: str
    source_id: str
    file_id: str
    source_role: SourceRole
    is_fact_source: bool
    source_tier: str = ""
    evidence_status: str = ""
    can_support_project_fact: bool = False
    can_support_critical_claim: bool = False
    human_confirmation_status: str = "not_applicable"
    provenance_support_type: str = ""
    claim_status: str = ""
    support_type: EvidenceSupportType
    confidence: float = Field(ge=0, le=1)
    usage: CitationEvidenceUsage
    snippet: str
    matched_terms: list[str]

    @field_validator("evidence_id", "question_id", "source_id", "file_id", "snippet", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class CitationSlot(StrictBaseModel):
    slot_id: str
    section_id: str
    question_id: str
    claim_type: ClaimType
    description: str
    allowed_evidence: list[str]
    status: CitationSlotStatus
    required_for_draft: bool
    instruction: str

    @field_validator("slot_id", "section_id", "question_id", "description", "instruction", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class UnsupportedClaim(StrictBaseModel):
    claim_id: str
    section_id: str
    question_id: str
    description: str
    reason: UnsupportedClaimReason
    required_action: RequiredAction

    @field_validator("claim_id", "section_id", "question_id", "description", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class WeakEvidenceNote(StrictBaseModel):
    question_id: str
    note: str
    required_action: RequiredAction

    @field_validator("question_id", "note", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class CitationPlanSection(StrictBaseModel):
    section_id: str
    section_title: str
    order: int
    question_ids: list[str]
    allowed_evidence: list[str]
    evidence_details: list[CitationEvidenceDetail]
    citation_slots: list[CitationSlot]
    unsupported_claims: list[UnsupportedClaim]
    weak_evidence_notes: list[WeakEvidenceNote]
    requires_human_confirmation: bool
    evidence_status: SectionEvidenceStatus
    unresolved_question_ids: list[str]
    notes: list[str]

    @field_validator("section_id", "section_title", mode="before")
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped


class CitationPlanSummary(StrictBaseModel):
    total_sections: int
    sections_supported: int
    sections_mixed: int
    sections_weak: int
    sections_unsupported: int
    total_citation_slots: int
    filled_slots: int
    weak_slots: int
    unsupported_slots: int
    human_confirmation_slots: int
    total_allowed_evidence: int
    fact_support_evidence: int
    methodology_or_context_evidence: int


class CitationPlanArtifact(StrictBaseModel):
    run_id: str
    generated_at: str
    sections: list[CitationPlanSection]
    summary: CitationPlanSummary
    warnings: list[str]


class SectionTask(StrictBaseModel):
    task_id: str
    section_id: str
    section_title: str
    order: int
    task_title: str
    task_type: TaskType
    writing_goal: str
    writing_mode: WritingMode
    allowed_evidence: list[str]
    required_citation_slots: list[str]
    evidence_status: SectionEvidenceStatus
    requires_human_confirmation: bool
    unresolved_question_ids: list[str]
    forbidden_sources: list[str]
    word_limit: int = Field(ge=200, le=500)
    must_include: list[str]
    must_not_include: list[str]
    confirmation_markers: list[str]
    future_output_path: str
    source_support_requirements: str
    source_support: list[dict[str, Any]] = Field(default_factory=list)
    provenance_summary: dict[str, Any] = Field(default_factory=dict)
    notes: list[str]

    @field_validator(
        "task_id",
        "section_id",
        "section_title",
        "task_title",
        "writing_goal",
        "future_output_path",
        "source_support_requirements",
        mode="before",
    )
    @classmethod
    def validate_required_text(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped

    @field_validator("forbidden_sources")
    @classmethod
    def validate_forbidden_sources(cls, value: list[str]) -> list[str]:
        required = {"sample", "expected_output_shape", "template", "checklist"}
        if not required <= set(value):
            raise ValueError("forbidden_sources must include sample, expected_output_shape, template, and checklist")
        return value


class SectionTasksSummary(StrictBaseModel):
    total_tasks: int
    supported_tasks: int
    mixed_or_weak_tasks: int
    unsupported_tasks: int
    human_confirmation_required: int


class SectionTasksArtifact(StrictBaseModel):
    run_id: str
    generated_at: str
    tasks: list[SectionTask]
    summary: SectionTasksSummary
    warnings: list[str]
