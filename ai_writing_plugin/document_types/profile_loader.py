from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator

from .base import DocumentTypeRules


REPO_ROOT = Path(__file__).resolve().parents[2]

SEQUENCE_FIELDS = (
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

NON_EMPTY_SEQUENCE_FIELDS = (
    "default_sections",
    "required_sections",
    "critical_claims",
    "requires_human_confirmation",
    "forbidden_final_claims",
    "fact_source_roles",
    "non_fact_source_roles",
    "allowed_final_statuses",
    "review_focus",
    "verification_focus",
)


class DocumentProfileValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class DocumentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: str
    profile_version: str
    task_type: str
    display_name: str
    description: str

    default_sections: list[str]
    required_sections: list[str]
    optional_sections: list[str]

    critical_claims: list[str]
    requires_human_confirmation: list[str]
    forbidden_final_claims: list[str]
    confirmation_marker: str

    fact_source_roles: list[str]
    non_fact_source_roles: list[str]
    reference_policy: str
    sample_policy: str

    default_final_status: str
    allowed_final_statuses: list[str]

    review_focus: list[str]
    verification_focus: list[str]
    candidate_learning_policy: str

    terminology: dict[str, str]
    output_labels: dict[str, str]

    @field_validator(
        "profile_id",
        "profile_version",
        "task_type",
        "display_name",
        "description",
        "confirmation_marker",
        "reference_policy",
        "sample_policy",
        "default_final_status",
        "candidate_learning_policy",
        mode="before",
    )
    @classmethod
    def validate_non_empty_string(cls, value: object, info) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{info.field_name} must be a non-empty string")
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return stripped

    @field_validator(*SEQUENCE_FIELDS, mode="before")
    @classmethod
    def validate_sequence(cls, value: object, info) -> object:
        if not isinstance(value, list):
            raise ValueError(f"{info.field_name} must be a list")
        if info.field_name in NON_EMPTY_SEQUENCE_FIELDS and not value:
            raise ValueError(f"{info.field_name} must not be empty")
        return value

    @field_validator(*SEQUENCE_FIELDS)
    @classmethod
    def validate_sequence_items(cls, value: list[str], info) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError(f"{info.field_name} items must be non-empty strings")
            stripped = item.strip()
            if not stripped:
                raise ValueError(f"{info.field_name} items must be non-empty strings")
            cleaned.append(stripped)
        return cleaned

    @field_validator("terminology", "output_labels", mode="before")
    @classmethod
    def validate_string_mapping(cls, value: object, info) -> dict[str, str]:
        if not isinstance(value, dict):
            raise ValueError(f"{info.field_name} must be a mapping")
        cleaned: dict[str, str] = {}
        for key, item in value.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"{info.field_name} keys must be non-empty strings")
            if not isinstance(item, str):
                raise ValueError(f"{info.field_name} values must be strings")
            cleaned[key.strip()] = item.strip()
        return cleaned

    @model_validator(mode="after")
    def validate_policy_boundaries(self) -> "DocumentProfile":
        errors: list[str] = []
        fact_roles = {role.lower() for role in self.fact_source_roles}
        non_fact_roles = {role.lower() for role in self.non_fact_source_roles}

        if "sample" in fact_roles:
            errors.append("fact_source_roles must not include sample")
        if "sample" not in non_fact_roles:
            errors.append("non_fact_source_roles must include sample")
        if self.default_final_status not in self.allowed_final_statuses:
            errors.append("default_final_status must be one of allowed_final_statuses")
        if not policy_blocks_fact_source(self.sample_policy, "sample"):
            errors.append("sample_policy must state that sample is not a project fact source")
        if not policy_blocks_fact_source(self.reference_policy, "reference"):
            errors.append("reference_policy must state that reference is not a project fact source")

        if errors:
            raise ValueError("; ".join(errors))
        return self

    def to_rules(self) -> DocumentTypeRules:
        return DocumentTypeRules(
            task_type=self.task_type,
            display_name=self.display_name,
            description=self.description,
            default_sections=tuple(self.default_sections),
            required_sections=tuple(self.required_sections),
            optional_sections=tuple(self.optional_sections),
            critical_claims=tuple(self.critical_claims),
            requires_human_confirmation=tuple(self.requires_human_confirmation),
            forbidden_final_claims=tuple(self.forbidden_final_claims),
            confirmation_marker=self.confirmation_marker,
            fact_source_roles=tuple(self.fact_source_roles),
            non_fact_source_roles=tuple(self.non_fact_source_roles),
            reference_policy=self.reference_policy,
            sample_policy=self.sample_policy,
            default_final_status=self.default_final_status,
            allowed_final_statuses=tuple(self.allowed_final_statuses),
            review_focus=tuple(self.review_focus),
            verification_focus=tuple(self.verification_focus),
            candidate_learning_policy=self.candidate_learning_policy,
            terminology=dict(self.terminology),
            output_labels=dict(self.output_labels),
        )


@dataclass(frozen=True)
class LoadedDocumentProfile:
    profile: DocumentProfile
    profile_path: str

    def to_rules(self) -> DocumentTypeRules:
        return self.profile.to_rules()

    def metadata(self, validation_status: str = "passed") -> dict[str, Any]:
        return {
            "profile_id": self.profile.profile_id,
            "profile_version": self.profile.profile_version,
            "profile_source": "external",
            "profile_path": self.profile_path,
            "validation_status": validation_status,
        }


def load_document_profile(
    profile_path: str,
    expected_task_type: str | None = None,
    repo_root: Path = REPO_ROOT,
) -> LoadedDocumentProfile:
    resolved_path, normalized_path = resolve_profile_path(profile_path, repo_root)
    return load_document_profile_file(
        resolved_path,
        profile_path=normalized_path,
        expected_task_type=expected_task_type,
    )


def load_document_profile_file(
    path: Path,
    profile_path: str,
    expected_task_type: str | None = None,
) -> LoadedDocumentProfile:
    errors: list[str] = []
    try:
        loaded_yaml = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise DocumentProfileValidationError([f"profile file not found: {profile_path}"])
    except yaml.YAMLError as exc:
        raise DocumentProfileValidationError([f"profile YAML parse error: {profile_path}: {exc}"]) from exc
    except UnicodeDecodeError as exc:
        raise DocumentProfileValidationError([f"profile encoding error: {profile_path}: {exc}"]) from exc

    if not isinstance(loaded_yaml, dict):
        raise DocumentProfileValidationError([f"profile root must be a mapping: {profile_path}"])

    try:
        profile = DocumentProfile.model_validate(loaded_yaml)
    except ValidationError as exc:
        raise DocumentProfileValidationError(format_validation_errors(exc)) from exc

    if expected_task_type and profile.task_type != expected_task_type:
        errors.append(f"task_type mismatch: task.yaml={expected_task_type} profile={profile.task_type}")
    if errors:
        raise DocumentProfileValidationError(errors)
    return LoadedDocumentProfile(profile=profile, profile_path=profile_path)


def resolve_profile_path(profile_path: str, repo_root: Path = REPO_ROOT) -> tuple[Path, str]:
    if not isinstance(profile_path, str) or not profile_path.strip():
        raise DocumentProfileValidationError(["document_profile_path must be a non-empty repository-relative path"])
    normalized = profile_path.strip()
    path = Path(normalized)
    if path.is_absolute():
        raise DocumentProfileValidationError(["document_profile_path must not be absolute"])
    if ".." in path.parts:
        raise DocumentProfileValidationError(["document_profile_path must not contain .."])
    if not path.parts:
        raise DocumentProfileValidationError(["document_profile_path must not be empty"])
    return repo_root / path, path.as_posix()


def format_validation_errors(exc: ValidationError) -> list[str]:
    errors: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        message = error["msg"]
        errors.append(f"{location}: {message}" if location else message)
    return errors


def policy_blocks_fact_source(policy: str, subject: str) -> bool:
    lowered = policy.lower()
    has_subject = subject in lowered
    has_fact_boundary = "fact" in lowered
    has_blocking_language = any(phrase in lowered for phrase in ["must not", "not ", "cannot", "can't", "no "])
    return has_subject and has_fact_boundary and has_blocking_language
