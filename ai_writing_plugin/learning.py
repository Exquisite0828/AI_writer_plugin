from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .document_types.base import DocumentTypeRules
from .document_types.context import get_rules_for_task_brief
from .models import ArtifactRecord, InputInventory, Manifest, TaskBrief
from .trace import (
    DEFAULT_HITL_GATES,
    append_hitl_decision,
    build_reconstructed_session_trace,
    canonical_hitl_stage,
    ensure_default_hitl_gates,
    load_existing_hitl_decisions,
    write_session_trace,
)


class LearningRunError(Exception):
    """Raised when Phase 8 learning artifacts cannot be generated."""


@dataclass(frozen=True)
class LearningRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class LearningInputs:
    manifest: Manifest
    task_brief: TaskBrief
    inventory: InputInventory
    knowledge_gaps: str
    unresolved_questions: str
    citation_plan: dict[str, Any]
    full_draft: str
    review_report: dict[str, Any]
    final_review: str
    verify_report: dict[str, Any]
    failures: str
    revision_plan: dict[str, Any]
    revised_full_draft: str
    change_log: str
    final_report: str
    delivery_summary: str


PHASE_8_ARTIFACTS = [
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/reusable_patterns.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
    "learning/promotion_report.md",
]

REQUIRED_PHASE_7_PATHS = [
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/knowledge_gaps.md",
    "plans/unresolved_questions.md",
    "plans/citation_plan.json",
    "draft/full_draft.md",
    "review/review_report.json",
    "review/final_review.md",
    "verify/verify_report.json",
    "verify/failures.md",
    "revision_plan.json",
    "revised/full_draft.md",
    "revised/change_log.md",
    "final/final_report.md",
    "final/delivery_summary.md",
]


def learning_existing_run(run_dir: str | Path) -> LearningRunResult:
    run_path = Path(run_dir)
    generated_at = utc_timestamp()
    inputs = load_phase_8_inputs(run_path)

    trace_dir = run_path / "trace"
    learning_dir = run_path / "learning"
    trace_dir.mkdir(parents=True, exist_ok=True)
    learning_dir.mkdir(parents=True, exist_ok=True)

    ensure_default_hitl_gates(run_path)
    rules = get_rules_for_task_brief(inputs.task_brief.model_dump())
    (learning_dir / "run_summary.md").write_text(build_run_summary(run_path, inputs, rules), encoding="utf-8")
    (learning_dir / "reusable_patterns.md").write_text(build_reusable_patterns(run_path, inputs, rules), encoding="utf-8")
    (learning_dir / "candidate_profile_update.yaml").write_text(
        build_candidate_profile_update(run_path, inputs, rules),
        encoding="utf-8",
    )
    (learning_dir / "candidate_skill_patch.md").write_text(
        build_candidate_skill_patch(run_path, inputs, rules),
        encoding="utf-8",
    )
    (learning_dir / "promotion_report.md").write_text(build_promotion_report(run_path, inputs, rules), encoding="utf-8")
    write_session_trace(run_path, build_reconstructed_session_trace(run_path))

    update_manifest_for_phase_8(run_path, inputs.manifest, generated_at, PHASE_8_ARTIFACTS)
    return LearningRunResult(artifact_paths=PHASE_8_ARTIFACTS)


def record_hitl_decision(
    run_dir: str | Path,
    stage: str,
    decision: str,
    comment: str,
    affected_sections: list[str],
    next_action: str,
) -> dict[str, Any]:
    run_path = Path(run_dir)
    if not run_path.exists() or not run_path.is_dir():
        raise LearningRunError(f"Run directory not found: {run_path}")
    if not (run_path / "manifest.json").exists():
        raise LearningRunError(f"Required manifest.json not found: {run_path / 'manifest.json'}")
    return append_hitl_decision(
        run_path,
        {
            "stage": stage,
            "decision": decision,
            "user_comment": comment,
            "affected_sections": affected_sections,
            "next_action": next_action,
            "requires_user_confirmation": decision not in {"approved"},
            "status": "recorded",
        },
    )


def load_phase_8_inputs(run_dir: Path) -> LearningInputs:
    if not run_dir.exists():
        raise LearningRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise LearningRunError(f"Run path is not a directory: {run_dir}")

    missing = [relative_path for relative_path in REQUIRED_PHASE_7_PATHS if not (run_dir / relative_path).exists()]
    if missing:
        first_missing = missing[0]
        raise LearningRunError(f"Cannot run learning: missing {first_missing}. Run must complete Phase 7 first.")

    manifest = validate_json_model(run_dir / "manifest.json", Manifest)
    task_brief = validate_json_model(run_dir / "task_brief.json", TaskBrief)
    rules = get_rules_for_task_brief(task_brief.model_dump())
    allowed_statuses = {*rules.allowed_final_statuses, "completed_with_candidate_updates_proposed"}
    if manifest.phase not in {"phase_7", "phase_8"} or manifest.status not in allowed_statuses:
        raise LearningRunError("Cannot run learning: run must complete Phase 7 before Phase 8 learning.")

    return LearningInputs(
        manifest=manifest,
        task_brief=task_brief,
        inventory=validate_json_model(run_dir / "inputs" / "input_inventory.json", InputInventory),
        knowledge_gaps=(run_dir / "knowledge" / "knowledge_gaps.md").read_text(encoding="utf-8"),
        unresolved_questions=(run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8"),
        citation_plan=read_json(run_dir / "plans" / "citation_plan.json"),
        full_draft=(run_dir / "draft" / "full_draft.md").read_text(encoding="utf-8"),
        review_report=read_json(run_dir / "review" / "review_report.json"),
        final_review=(run_dir / "review" / "final_review.md").read_text(encoding="utf-8"),
        verify_report=read_json(run_dir / "verify" / "verify_report.json"),
        failures=(run_dir / "verify" / "failures.md").read_text(encoding="utf-8"),
        revision_plan=read_json(run_dir / "revision_plan.json"),
        revised_full_draft=(run_dir / "revised" / "full_draft.md").read_text(encoding="utf-8"),
        change_log=(run_dir / "revised" / "change_log.md").read_text(encoding="utf-8"),
        final_report=(run_dir / "final" / "final_report.md").read_text(encoding="utf-8"),
        delivery_summary=(run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8"),
    )


def build_run_summary(run_dir: Path, inputs: LearningInputs, rules: DocumentTypeRules) -> str:
    review_summary = inputs.review_report.get("summary", {})
    verify_summary = inputs.verify_report.get("summary", {})
    lines = [
        "# 运行摘要",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "Status: completed_with_candidate_updates_proposed",
        "",
        "## 执行的 workflow",
        "",
        "- ingest",
        "- outline",
        "- evidence",
        "- planning",
        "- draft",
        "- review",
        "- finalize",
        "- learning",
        "",
        "## 关键 artifacts",
        "",
        *[f"- {artifact.path}" for artifact in inputs.manifest.artifacts],
        "- trace/session_trace.jsonl",
        "- trace/hitl_decisions.jsonl",
        "- learning/run_summary.md",
        "- learning/reusable_patterns.md",
        "- learning/candidate_profile_update.yaml",
        "- learning/candidate_skill_patch.md",
        "- learning/promotion_report.md",
        "",
        "## 审查与验证摘要",
        "",
        f"- 审查状态：{inputs.review_report.get('status', 'unknown')}",
        f"- P0 审查项：{review_summary.get('p0_items', 0)}",
        f"- P1 审查项：{review_summary.get('p1_items', 0)}",
        f"- 验证状态：{inputs.verify_report.get('status', 'unknown')}",
        f"- Verification final readiness：{verify_summary.get('final_readiness', 'unknown')}",
        "",
        "## 最终交付摘要",
        "",
        f"- 文档类型：{rules.display_name}",
        f"- 最终交付状态保持 {rules.default_final_status}。",
        "- final/final_report.md 和 final/delivery_summary.md 是交付包的权威 artifact。",
        "",
        "## 人工确认状态",
        "",
        *human_confirmation_status_lines(run_dir),
        "",
        f"- {rules.confirmation_marker} 标记仍保持 pending。",
        f"- {professional_judgment_label(rules, plural=True)} 在批准前需要人工确认。",
        "- 非交互式 HITL gate 不会被视为 approved。",
        "",
        "## 继续带入的开放问题",
        "",
        *open_issue_lines(inputs),
        "",
        "## 生成的 candidate updates",
        "",
        "- candidate_profile_update.yaml",
        "- candidate_skill_patch.md",
        "- promotion_report.md",
        "",
        "## 不会自动应用的内容",
        "",
        "candidate update 或 Skill patch 不会自动应用。",
        "stable Skill 不会被自动覆盖。",
        "",
    ]
    return "\n".join(lines)


def human_confirmation_status_lines(run_dir: Path) -> list[str]:
    records_by_stage: dict[str, list[dict[str, Any]]] = {stage: [] for stage in DEFAULT_HITL_GATES}
    for record in load_existing_hitl_decisions(run_dir):
        stage = canonical_hitl_stage(str(record.get("stage", "")))
        if stage in records_by_stage:
            records_by_stage[stage].append(record)
    return [f"- {stage}: {hitl_gate_status(records_by_stage[stage])}" for stage in DEFAULT_HITL_GATES]


def hitl_gate_status(records: list[dict[str, Any]]) -> str:
    if not records:
        return "missing"
    decisions = {str(record.get("decision", "")) for record in records}
    if any(decision not in {"not_collected_in_noninteractive_run", "pending_user_confirmation"} for decision in decisions):
        return "recorded"
    if "pending_user_confirmation" in decisions:
        return "pending_user_confirmation"
    if "not_collected_in_noninteractive_run" in decisions:
        return "not_collected_in_noninteractive_run"
    return "recorded"


def build_reusable_patterns(run_dir: Path, inputs: LearningInputs, rules: DocumentTypeRules) -> str:
    lines = [
        "# Reusable Patterns",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "## Document Type",
        "",
        f"{rules.display_name}.",
        "",
        "## Reusable Workflow Patterns",
        "",
        "- Preserve a deterministic chain from input inventory to final delivery.",
        "- Carry knowledge gaps, unresolved questions, and weak evidence into final delivery.",
        f"- Keep final delivery open when {rules.display_name} confirmations remain pending.",
        "",
        "## Reusable Review Patterns",
        "",
        f"- Treat unconfirmed {professional_judgment_label(rules)} as a blocker.",
        f"- Keep {rules.confirmation_marker} where any critical claim is unresolved.",
        "- Carry unsupported and weak evidence into the delivery summary.",
        "",
        "## Critical Claims Requiring Confirmation",
        "",
        *[f"- {claim}" for claim in rules.critical_claims],
        "",
        "## Reusable Evidence Rules",
        "",
        "- Do not use sample documents as fact sources.",
        "- sample documents are not fact sources.",
        "- expected_output_shape is not a fact source.",
        f"- {rules.reference_policy}",
        f"- {professional_judgment_label(rules, plural=True)} cannot be reused as finalized conclusions.",
        "",
        "## Non-Reusable Facts",
        "",
        "The following must not be reused as facts in future runs:",
        "- project-specific source facts",
        "- sample document facts",
        "- expected output shape content",
        f"- unconfirmed {rules.display_name} ratings",
        "- unconfirmed critical claims",
        "",
        "## Human Confirmation Rules",
        "",
        f"- Human confirmation is required before approving {professional_judgment_label(rules, plural=True)}.",
        f"- pending and {rules.confirmation_marker} markers remain until real user decisions are recorded.",
        "",
    ]
    return "\n".join(lines)


def build_candidate_profile_update(run_dir: Path, inputs: LearningInputs, rules: DocumentTypeRules) -> str:
    run_id = inputs.manifest.run_id
    return "\n".join(
        [
            f"profile_update_id: candidate-profile-update-{run_id}",
            f"source_run_id: {run_id}",
            f"document_type: {rules.task_type}",
            f"document_type_display_name: {rules.display_name}",
            "status: proposed",
            "active: false",
            "auto_applied: false",
            "requires_user_approval: true",
            "rollback_supported: true",
            f"candidate_learning_policy: {rules.candidate_learning_policy}",
            f"confirmation_marker: {rules.confirmation_marker}",
            "",
            "candidate_update_state:",
            "  current: proposed",
            "  allowed_next_states:",
            "    - evaluated",
            "    - approved",
            "    - active",
            "    - rolled_back",
            "",
            "updates:",
            "  document_type_rules:",
            "    critical_claims:",
            *[f"      - {claim}" for claim in rules.critical_claims],
            "    review_focus:",
            *[f"      - {focus}" for focus in rules.review_focus],
            "  workflow:",
            "    preserve_unresolved_questions_in_final_report: true",
            "    require_material_classification_confirmation: true",
            "    require_evidence_confirmation_for_critical_sections: true",
            "    keep_final_status_open_when_confirmations_pending: true",
            "  review:",
            "    flag_unconfirmed_professional_judgment_as_blocker: true",
            "    flag_sample_as_fact_source_as_p0: true",
            "    carry_weak_evidence_to_delivery_summary: true",
            "  style:",
            "    include_delivery_limitations_section: true",
            "    include_next_required_human_actions_section: true",
            "",
            "guardrails:",
            "  sample_is_fact_source: false",
            "  expected_output_shape_is_fact_source: false",
            "  professional_judgments_require_human_confirmation: true",
            "  stable_skill_overwrite_allowed: false",
            "",
            "approval:",
            "  approved_by_user: false",
            "  approval_record: null",
            "  applied_to_profile: false",
            "",
        ]
    )


def build_candidate_skill_patch(run_dir: Path, inputs: LearningInputs, rules: DocumentTypeRules) -> str:
    return "\n".join(
        [
            "# Candidate Skill Patch",
            "",
            f"Run id: {inputs.manifest.run_id}",
            "",
            "Status: proposed_only",
            "",
            "## Target",
            "",
            "Candidate target:",
            f"- skills/document-types/{rules.task_type}/SKILL.md",
            f"- Document type display name: {rules.display_name}",
            "",
            "This patch has not been applied.",
            "This patch is not applied.",
            "No stable skill was overwritten.",
            "This candidate requires user approval before any promotion.",
            "",
            "## Proposed Additions",
            "",
            "- Preserve input inventory, source index, evidence map, citation plan, review, verification, revision, final delivery, trace, and learning artifacts.",
            "- Keep candidate updates proposed until a user explicitly approves them.",
            "",
            "## Guardrails To Preserve",
            "",
            "- Do not use sample documents as fact sources.",
            "- Do not use expected output shape as fact sources.",
            f"- {rules.reference_policy}",
            f"- Do not finalize {professional_judgment_label(rules, plural=True)} without human confirmation.",
            f"- Keep {rules.confirmation_marker} for critical claims.",
            "",
            "## Critical Claims",
            "",
            *[f"- {claim}" for claim in rules.critical_claims],
            "",
            "## Proposed Review Rules",
            "",
            "- Flag sample or expected-output-shape fact-source misuse.",
            "- Carry weak evidence, unsupported content, and knowledge gaps to final delivery.",
            f"- Keep {professional_judgment_label(rules, plural=True)} pending until real HITL decisions are recorded.",
            "",
            "## Required Evaluation Before Promotion",
            "",
            "- Review candidate_profile_update.yaml.",
            "- Review this candidate_skill_patch.md.",
            "- Confirm that no stable skill overwrite is required.",
            f"- Confirm that {professional_judgment_label(rules, plural=True)} remain pending without human confirmation.",
            "",
            "## Rollback Note",
            "",
            "If promoted later and found harmful, this candidate must be reversible through a future rollback mechanism.",
            "",
        ]
    )


def build_promotion_report(run_dir: Path, inputs: LearningInputs, rules: DocumentTypeRules) -> str:
    return "\n".join(
        [
            "# Promotion Report",
            "",
            f"Run id: {inputs.manifest.run_id}",
            "",
            "## Candidate State",
            "",
            "Current state: proposed",
            f"Document type: {rules.display_name}",
            f"Candidate learning policy: {rules.candidate_learning_policy}",
            "",
            "## Basic Evaluation",
            "",
            "- Required learning artifacts generated: yes",
            "- Candidate profile update generated: yes",
            "- Candidate skill patch generated: yes",
            "- Stable skill overwritten: no",
            "- Candidate activated: no",
            "",
            "## Promotion Decision",
            "",
            "Not promoted automatically.",
            "",
            "## Required User Action",
            "",
            "A user must inspect the candidate profile update and candidate skill patch before approving any promotion.",
            "",
            "## Allowed Future States",
            "",
            "proposed -> evaluated -> approved -> active -> rolled_back",
            "",
            "## Rollback",
            "",
            "Rollback must be supported if a future approved candidate is activated and later found harmful.",
            "",
        ]
    )


def professional_judgment_label(rules: DocumentTypeRules, plural: bool = False) -> str:
    key = "professional_judgments" if plural else "professional_judgment"
    fallback = "professional judgments" if plural else "professional judgment"
    return rules.terminology.get(key, fallback)


def open_issue_lines(inputs: LearningInputs) -> list[str]:
    tasks = inputs.revision_plan.get("tasks", [])
    if not tasks:
        return ["- No revision tasks were recorded."]
    lines = []
    for task in tasks:
        if task.get("result") in {"pending", "carried_forward", "unresolved"} or task.get("requires_user_confirmation"):
            lines.append(
                f"- {task.get('revision_task_id')} | {task.get('category')} | {task.get('result')} | {task.get('notes')}"
            )
    return lines or ["- No open issue was carried forward by revision_plan.json."]


def update_manifest_for_phase_8(
    run_dir: Path,
    manifest: Manifest,
    generated_at: str,
    artifact_paths: list[str],
) -> None:
    new_records = [
        ArtifactRecord(path=artifact_path, kind=artifact_kind(artifact_path), created_at=generated_at)
        for artifact_path in artifact_paths
    ]
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status="completed_with_candidate_updates_proposed",
        phase="phase_8",
        artifacts=upsert_artifacts(manifest.artifacts, new_records),
        profile=manifest.profile,
    )
    write_json(run_dir / "manifest.json", updated_manifest.model_dump(exclude_defaults=True, exclude_none=True))


def artifact_kind(artifact_path: str) -> str:
    return {
        "trace/session_trace.jsonl": "session_trace",
        "trace/hitl_decisions.jsonl": "hitl_decisions",
        "learning/run_summary.md": "run_summary",
        "learning/reusable_patterns.md": "reusable_patterns",
        "learning/candidate_profile_update.yaml": "candidate_profile_update",
        "learning/candidate_skill_patch.md": "candidate_skill_patch",
        "learning/promotion_report.md": "promotion_report",
    }[artifact_path]


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
        raise LearningRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise LearningRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise LearningRunError(f"Required artifact not found: {path}") from exc
    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise LearningRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LearningRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise LearningRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise LearningRunError(f"Required artifact not found: {path}") from exc
    if not isinstance(loaded, dict):
        raise LearningRunError(f"Invalid JSON artifact: {path}: root must be an object")
    return loaded


def write_json(path: Path, data: dict[str, Any]) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(f"{encoded}\n", encoding="utf-8")


def format_validation_error(exc: ValidationError) -> str:
    messages: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        messages.append(f"{location}: {error['msg']}")
    return "; ".join(messages)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
