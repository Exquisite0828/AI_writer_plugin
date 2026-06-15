from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .document_types import get_document_type_rules
from .document_types.base import DocumentTypeRules
from .document_types.profile_loader import DocumentProfileValidationError, load_document_profile
from .draft import draft_existing_run
from .evidence import evidence_existing_run
from .finalize import finalize_existing_run
from .ingest import ingest_inputs
from .learning import LearningRunError, learning_existing_run, record_hitl_decision
from .models import ArtifactRecord, Manifest, ProfileMetadata, TaskBrief, TaskConfig
from .outline import outline_existing_run
from .planning import plan_existing_run
from .review import review_existing_run
from .run_state import (
    RunStateError,
    create_run_state,
    resume_run as resume_existing_run,
    run_checkpointed_stage,
    state_exists,
)
from .stage_review import StageReviewError, require_previous_stage_review_gate
from .trace import write_jsonl


class InitRunError(Exception):
    """Raised when Phase 0 run initialization cannot complete."""


class WriteRunError(Exception):
    """Raised when the full Phase 0-8 write helper cannot complete."""


class ResumeRunError(Exception):
    """Raised when a resumable run cannot continue."""


@dataclass(frozen=True)
class PreparedTaskRules:
    rules: DocumentTypeRules
    profile: ProfileMetadata | None


def init_run(task_file: str | Path, runs_dir: str | Path = "runs") -> Path:
    task_path = Path(task_file)
    output_root = Path(runs_dir)
    task_config = load_task_config(task_path)
    try:
        prepared_rules = prepare_task_rules(task_config)
    except DocumentProfileValidationError as exc:
        raise InitRunError(f"Invalid document profile: {'; '.join(exc.errors)}") from exc

    run_id, run_dir = create_unique_run_dir(output_root, task_config.task_type)

    created_at = utc_timestamp()
    task_brief = build_task_brief(run_id, task_config, prepared_rules)
    artifacts = [
        ArtifactRecord(path="manifest.json", kind="manifest", created_at=created_at),
        ArtifactRecord(path="task_brief.json", kind="task_brief", created_at=created_at),
    ]
    manifest = Manifest(
        run_id=run_id,
        task_file=str(task_path),
        created_at=created_at,
        status="initialized",
        phase="phase_0",
        artifacts=artifacts,
        profile=prepared_rules.profile,
    )

    write_json(run_dir / "task_brief.json", task_brief.model_dump(exclude_defaults=True, exclude_none=True))
    write_json(run_dir / "manifest.json", manifest.model_dump(exclude_defaults=True, exclude_none=True))
    return run_dir


def ingest_run(task_file: str | Path, runs_dir: str | Path = "runs") -> Path:
    task_path = Path(task_file)
    output_root = Path(runs_dir)
    task_config = load_task_config(task_path)

    if not task_config.document_profile_path:
        prepared_rules = prepare_task_rules(task_config)
        return ingest_valid_task(task_path, output_root, task_config, prepared_rules)

    run_id, run_dir = create_unique_run_dir(output_root, task_config.task_type)
    created_at = utc_timestamp()
    try:
        prepared_rules = prepare_task_rules(task_config)
    except DocumentProfileValidationError as exc:
        write_invalid_document_profile_run(
            run_dir=run_dir,
            run_id=run_id,
            task_path=task_path,
            task_config=task_config,
            created_at=created_at,
            errors=exc.errors,
        )
        raise InitRunError(f"Invalid document profile: {'; '.join(exc.errors)}") from exc
    return ingest_valid_task(task_path, output_root, task_config, prepared_rules, run_id=run_id, run_dir=run_dir, created_at=created_at)


def ingest_valid_task(
    task_path: Path,
    output_root: Path,
    task_config: TaskConfig,
    prepared_rules: PreparedTaskRules,
    run_id: str | None = None,
    run_dir: Path | None = None,
    created_at: str | None = None,
) -> Path:
    if run_id is None or run_dir is None:
        run_id, run_dir = create_unique_run_dir(output_root, task_config.task_type)
    created_at = created_at or utc_timestamp()
    task_brief = build_task_brief(run_id, task_config, prepared_rules)
    write_json(run_dir / "task_brief.json", task_brief.model_dump(exclude_defaults=True, exclude_none=True))

    ingest_inputs(
        run_id=run_id,
        task_file=task_path,
        run_dir=run_dir,
        inputs=task_config.inputs,
        generated_at=created_at,
        task_brief=task_brief,
    )

    artifacts = [
        ArtifactRecord(path="manifest.json", kind="manifest", created_at=created_at),
        ArtifactRecord(path="task_brief.json", kind="task_brief", created_at=created_at),
        ArtifactRecord(path="inputs/input_inventory.json", kind="input_inventory", created_at=created_at),
        ArtifactRecord(path="knowledge/source_index.json", kind="source_index", created_at=created_at),
        ArtifactRecord(path="knowledge/provenance_index.json", kind="provenance_index", created_at=created_at),
        ArtifactRecord(path="knowledge/knowledge_gaps.md", kind="knowledge_gaps", created_at=created_at),
    ]
    manifest = Manifest(
        run_id=run_id,
        task_file=str(task_path),
        created_at=created_at,
        status="ingested",
        phase="phase_1",
        artifacts=artifacts,
        profile=prepared_rules.profile,
    )
    write_json(run_dir / "manifest.json", manifest.model_dump(exclude_defaults=True, exclude_none=True))
    create_run_state(run_dir, task_path, task_config)
    return run_dir


def outline_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "outline", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "outline", outline_existing_run)
    else:
        outline_existing_run(run_path)
    return run_path


def evidence_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "evidence", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "evidence", evidence_existing_run)
    else:
        evidence_existing_run(run_path)
    return run_path


def plan_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "planning", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "planning", plan_existing_run)
    else:
        plan_existing_run(run_path)
    return run_path


def draft_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "draft", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "draft", draft_existing_run)
    else:
        draft_existing_run(run_path)
    return run_path


def review_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "review", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "review", review_existing_run)
    else:
        review_existing_run(run_path)
    return run_path


def finalize_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "finalize", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "finalize", finalize_existing_run)
    else:
        finalize_existing_run(run_path)
    return run_path


def learning_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    require_stage_review_gate_or_raise(run_path, "learning", require_stage_review_gates)
    if state_exists(run_path):
        run_checkpointed_stage_or_raise(run_path, "learning", learning_existing_run)
    else:
        learning_existing_run(run_path)
    return run_path


def require_stage_review_gate_or_raise(run_path: Path, stage: str, required: bool) -> None:
    if not required:
        return
    try:
        require_previous_stage_review_gate(run_path, stage)
    except StageReviewError as exc:
        raise ResumeRunError(str(exc)) from exc


def run_checkpointed_stage_or_raise(run_path: Path, stage: str, runner) -> None:
    try:
        run_checkpointed_stage(run_path, stage, runner)
    except RunStateError as exc:
        raise ResumeRunError(str(exc)) from exc


def resume_run(run_dir: str | Path, require_stage_review_gates: bool = False) -> Path:
    run_path = Path(run_dir)
    stage_runners = {
        "ingest": ingest_stage_resume_not_supported,
        "outline": outline_existing_run,
        "evidence": evidence_existing_run,
        "planning": plan_existing_run,
        "draft": draft_existing_run,
        "review": review_existing_run,
        "finalize": finalize_existing_run,
        "learning": learning_existing_run,
    }
    try:
        if require_stage_review_gates:
            return resume_existing_run(
                run_path,
                stage_runners,
                before_stage=lambda path, stage: require_previous_stage_review_gate(path, stage),
                max_stages=1,
            )
        return resume_existing_run(run_path, stage_runners)
    except StageReviewError as exc:
        raise ResumeRunError(str(exc)) from exc
    except Exception as exc:
        raise ResumeRunError(str(exc)) from exc


def ingest_stage_resume_not_supported(run_dir: Path) -> None:
    raise ResumeRunError(
        f"resume-run failed: ingest stage is not resumable for partial run {run_dir}; start a new write-run"
    )


def record_hitl(
    run_dir: str | Path,
    stage: str,
    decision: str,
    comment: str,
    affected_sections: list[str],
    next_action: str,
) -> dict[str, Any]:
    return record_hitl_decision(
        run_dir=Path(run_dir),
        stage=stage,
        decision=decision,
        comment=comment,
        affected_sections=affected_sections,
        next_action=next_action,
    )


def write_run(
    task_file: str | Path,
    runs_dir: str | Path = "runs",
    require_stage_review_gates: bool = False,
) -> Path:
    try:
        run_path = ingest_run(task_file=task_file, runs_dir=runs_dir)
    except InitRunError as exc:
        raise WriteRunError(f"write-run failed at ingest: {exc}") from exc
    if require_stage_review_gates:
        return run_path

    stage_runners = [
        ("outline", outline_run),
        ("evidence", evidence_run),
        ("planning", plan_run),
        ("draft", draft_run),
        ("review", review_run),
        ("finalize", finalize_run),
        ("learning", learning_run),
    ]
    for stage, runner in stage_runners:
        try:
            runner(run_path)
        except (Exception,) as exc:
            raise WriteRunError(f"write-run failed at {stage}: {exc}") from exc
    return run_path


def prepare_task_rules(task_config: TaskConfig) -> PreparedTaskRules:
    if task_config.document_profile_path:
        loaded_profile = load_document_profile(
            task_config.document_profile_path,
            expected_task_type=task_config.task_type,
        )
        return PreparedTaskRules(
            rules=loaded_profile.to_rules(),
            profile=ProfileMetadata.model_validate(loaded_profile.metadata()),
        )

    try:
        return PreparedTaskRules(rules=get_document_type_rules(task_config.task_type), profile=None)
    except ValueError as exc:
        raise InitRunError(f"{exc}; provide document_profile_path for external task types") from exc


def build_task_brief(
    run_id: str,
    task_config: TaskConfig,
    prepared_rules: PreparedTaskRules | None = None,
) -> TaskBrief:
    rules = prepared_rules.rules if prepared_rules else None
    profile = prepared_rules.profile if prepared_rules else None
    return TaskBrief(
        run_id=run_id,
        task_type=task_config.task_type,
        task_title=task_config.task_title,
        display_name=task_config.display_name or (rules.display_name if profile else None),
        target_audience=task_config.target_audience,
        output_format=task_config.output_format,
        strict_template=task_config.strict_template,
        allow_inference=task_config.allow_inference,
        critical_claims=task_config.critical_claims or (list(rules.critical_claims) if profile else []),
        requires_human_confirmation=task_config.requires_human_confirmation,
        document_profile_path=task_config.document_profile_path,
        profile=profile,
    )


def write_invalid_document_profile_run(
    run_dir: Path,
    run_id: str,
    task_path: Path,
    task_config: TaskConfig,
    created_at: str,
    errors: list[str],
) -> None:
    profile_metadata = ProfileMetadata(
        profile_id="unknown",
        profile_version="unknown",
        profile_source="external",
        profile_path=task_config.document_profile_path or "",
        validation_status="failed",
        validation_errors=errors,
    )
    task_brief = build_task_brief(
        run_id,
        task_config,
        PreparedTaskRules(rules=invalid_profile_placeholder_rules(task_config), profile=profile_metadata),
    )
    artifact_records = [
        ArtifactRecord(path="manifest.json", kind="manifest", created_at=created_at),
        ArtifactRecord(path="task_brief.json", kind="task_brief", created_at=created_at),
        ArtifactRecord(path="verify/verify_report.json", kind="verify_report", created_at=created_at),
        ArtifactRecord(path="verify/failures.md", kind="failures", created_at=created_at),
        ArtifactRecord(path="trace/session_trace.jsonl", kind="session_trace", created_at=created_at),
    ]
    manifest = Manifest(
        run_id=run_id,
        task_file=str(task_path),
        created_at=created_at,
        status="blocked_invalid_document_profile",
        phase="phase_0",
        artifacts=artifact_records,
        profile=profile_metadata,
    )

    verify_dir = run_dir / "verify"
    trace_dir = run_dir / "trace"
    verify_dir.mkdir(parents=True, exist_ok=True)
    trace_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "task_brief.json", task_brief.model_dump(exclude_defaults=True, exclude_none=True))
    write_json(run_dir / "manifest.json", manifest.model_dump(exclude_defaults=True, exclude_none=True))
    verify_report = build_invalid_profile_verify_report(run_id, created_at, task_config, profile_metadata, errors)
    write_json(verify_dir / "verify_report.json", verify_report)
    (verify_dir / "failures.md").write_text(render_invalid_profile_failures(run_id, task_config, errors), encoding="utf-8")
    write_jsonl(
        trace_dir / "session_trace.jsonl",
        [
            {
                "timestamp": created_at,
                "run_id": run_id,
                "stage": "ingest",
                "event": "document_profile_validation",
                "artifact": task_config.document_profile_path or "",
                "status": "failed",
                "source": "write_run",
                "errors": errors,
            }
        ],
    )


def invalid_profile_placeholder_rules(task_config: TaskConfig) -> DocumentTypeRules:
    return DocumentTypeRules(
        task_type=task_config.task_type,
        display_name=task_config.display_name or task_config.task_type,
        description="Invalid external document profile placeholder.",
        default_sections=("Invalid Document Profile",),
        required_sections=("invalid document profile",),
        optional_sections=(),
        critical_claims=tuple(task_config.critical_claims or task_config.requires_human_confirmation),
        requires_human_confirmation=tuple(task_config.requires_human_confirmation),
        forbidden_final_claims=("approval",),
        confirmation_marker="NEEDS_USER_CONFIRMATION",
        fact_source_roles=("source",),
        non_fact_source_roles=("sample", "template", "checklist", "reference", "expected_output_shape"),
        reference_policy="Reference materials must not prove project-specific facts.",
        sample_policy="Sample documents must not supply project facts.",
        default_final_status="blocked_pending_confirmation",
        allowed_final_statuses=("blocked_pending_confirmation",),
        review_focus=("document profile validation",),
        verification_focus=("document profile validation",),
        candidate_learning_policy="No candidate update is applied when document profile validation fails.",
        terminology={},
        output_labels={},
    )


def build_invalid_profile_verify_report(
    run_id: str,
    generated_at: str,
    task_config: TaskConfig,
    profile_metadata: ProfileMetadata,
    errors: list[str],
) -> dict[str, Any]:
    details = "profile validation failure: " + "; ".join(errors)
    return {
        "run_id": run_id,
        "generated_at": generated_at,
        "document_type": {
            "task_type": task_config.task_type,
            "display_name": task_config.display_name or task_config.task_type,
            "profile": profile_metadata.model_dump(exclude_defaults=True),
        },
        "status": "failed",
        "summary": {
            "passed": 0,
            "failed": 1,
            "blocked": 0,
            "warnings": 0,
            "total_checks": 1,
            "final_readiness": "blocked_invalid_document_profile",
        },
        "checks": [
            {
                "check_id": "PROFILE-001",
                "name": "document_profile_validation",
                "status": "failed",
                "severity": "P0",
                "details": details,
                "related_artifacts": [task_config.document_profile_path or ""],
                "review_item_ids": [],
            }
        ],
        "blocking_failures": [details],
        "warnings": [],
    }


def render_invalid_profile_failures(run_id: str, task_config: TaskConfig, errors: list[str]) -> str:
    lines = [
        "# 验证失败项",
        "",
        f"Run id: {run_id}",
        "",
        "## 摘要",
        "",
        "- 验证状态：failed",
        "- 失败检查数：1",
        "- 阻塞检查数：0",
        "- Warnings: 0",
        "",
        "## Document profile validation",
        "",
        f"- Profile path: {task_config.document_profile_path or ''}",
        "- Result: profile validation failure",
        "",
        "## 错误",
        "",
        *[f"- {error}" for error in errors],
        "",
        "## 边界说明",
        "",
        "- 本次运行没有 fallback 到 generic_document 或任何 built-in rules。",
        "- 未尝试生成 final report。",
        "- 修正文档 document_profile.yaml 后再重新运行。",
        "",
    ]
    return "\n".join(lines)


def load_task_config(task_path: Path) -> TaskConfig:
    if not task_path.exists():
        raise InitRunError(f"Task file not found: {task_path}")
    if not task_path.is_file():
        raise InitRunError(f"Task file is not a file: {task_path}")

    try:
        loaded = yaml.safe_load(task_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise InitRunError(f"Invalid YAML in task config: {task_path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise InitRunError(f"Invalid task config encoding: {task_path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise InitRunError("Invalid task config: YAML root must be a mapping")

    try:
        return TaskConfig.model_validate(loaded)
    except ValidationError as exc:
        raise InitRunError(f"Invalid task config: {format_validation_error(exc)}") from exc


def format_validation_error(exc: ValidationError) -> str:
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        messages.append(f"{location}: {error['msg']}")
    return "; ".join(messages)


def create_unique_run_dir(runs_dir: Path, task_type: str) -> tuple[str, Path]:
    base_run_id = make_base_run_id(task_type)
    suffix = 1

    while True:
        run_id = base_run_id if suffix == 1 else f"{base_run_id}-{suffix}"
        run_dir = runs_dir / run_id
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
            return run_id, run_dir
        except FileExistsError:
            suffix += 1


def make_base_run_id(task_type: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    safe_task_type = sanitize_task_type(task_type)
    return f"{timestamp}-{safe_task_type}"


def sanitize_task_type(task_type: str) -> str:
    normalized = task_type.strip().lower()
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r"[^a-z0-9._-]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-._")
    return normalized or "task"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(f"{encoded}\n", encoding="utf-8")
