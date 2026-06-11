from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .document_types.base import DocumentTypeRules
from .document_types.context import get_rules_for_task_brief
from .models import ArtifactRecord, InputInventory, Manifest, SourceIndex, TaskBrief
from .provenance import build_provenance_verify_facts
from .verify import build_verify_report, render_failures_md


class FinalizeRunError(Exception):
    """Raised when Phase 7 revision and final delivery cannot complete."""


@dataclass(frozen=True)
class FinalizeRunResult:
    artifact_paths: list[str]


@dataclass(frozen=True)
class FinalizeInputs:
    manifest: Manifest
    task_brief: TaskBrief
    inventory: InputInventory
    source_index: SourceIndex
    provenance_index: dict[str, Any]
    knowledge_gaps: str
    unresolved_questions: str
    evidence_map: dict[str, Any]
    citation_plan: dict[str, Any]
    claim_support_matrix: dict[str, Any]
    full_draft: str
    review_report: dict[str, Any]
    final_review: str
    verify_report: dict[str, Any]
    failures: str


PHASE_7_ARTIFACTS = [
    "revision_plan.json",
    "revised/full_draft.md",
    "revised/change_log.md",
    "final/final_report.md",
    "final/delivery_summary.md",
]

SOURCE_ARTIFACTS = {
    "draft": "draft/full_draft.md",
    "review_report": "review/review_report.json",
    "final_review": "review/final_review.md",
    "verify_report": "verify/verify_report.json",
    "failures": "verify/failures.md",
    "evidence_map": "plans/evidence_map.json",
    "citation_plan": "plans/citation_plan.json",
    "claim_support_matrix": "plans/claim_support_matrix.json",
    "unresolved_questions": "plans/unresolved_questions.md",
    "provenance_index": "knowledge/provenance_index.json",
    "knowledge_gaps": "knowledge/knowledge_gaps.md",
}

REQUIRED_PHASE_6_PATHS = [
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/provenance_index.json",
    "knowledge/knowledge_gaps.md",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
    "plans/citation_plan.json",
    "plans/claim_support_matrix.json",
    "plans/outline_final.md",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
    "draft/full_draft.md",
    "review/review_report.json",
    "review/template_review.md",
    "review/checklist_review.md",
    "review/evidence_review.md",
    "review/final_review.md",
    "verify/verify_report.json",
    "verify/failures.md",
]

OPEN_ITEM_TERMS = [
    "unsupported",
    "weak evidence",
    "unresolved",
    "missing",
    "knowledge gap",
    "citation",
    "evidence",
]

FORMAT_TERMS = ["template", "checklist", "format"]

EVIDENCE_ISSUE_STATUSES = {
    "weak",
    "unsupported",
    "unresolved",
    "needs_confirmation",
    "requires_human_confirmation",
}

EVIDENCE_RELATED_TERMS = [
    "unsupported",
    "weak",
    "missing evidence",
    "missing_source_support",
    "unresolved",
    "citation",
    "evidence",
]

MATERIAL_GAP_STATUSES = {"missing", "unsupported", "failed"}

NON_FACT_SOURCE_EXCLUSION_ROLES = {"template", "checklist", "sample", "expected_output_shape"}

ALLOWED_FINAL_CONTEXTS = [
    "not a final",
    "no final",
    "remains tbd",
    "intentionally deferred",
    "deferred to",
    "must not",
    "does not make final",
    "does not finalize",
]


def finalize_existing_run(run_dir: str | Path) -> FinalizeRunResult:
    run_path = Path(run_dir)
    generated_at = utc_timestamp()
    inputs = load_required_artifacts(run_path)
    rules = get_rules_for_task_brief(inputs.task_brief.model_dump())
    revision_plan = build_revision_plan(inputs, generated_at, rules)

    revised_dir = run_path / "revised"
    final_dir = run_path / "final"
    revised_dir.mkdir(parents=True, exist_ok=True)
    final_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_path / "revision_plan.json", revision_plan)
    (revised_dir / "full_draft.md").write_text(build_revised_draft(inputs, revision_plan, rules), encoding="utf-8")
    (revised_dir / "change_log.md").write_text(build_change_log(inputs, revision_plan, rules), encoding="utf-8")
    (final_dir / "final_report.md").write_text(build_final_report(inputs, revision_plan, rules), encoding="utf-8")
    (final_dir / "delivery_summary.md").write_text(build_delivery_summary(inputs, revision_plan, rules), encoding="utf-8")
    updated_verify_report = refresh_verify_report_for_final_outputs(run_path, inputs, generated_at, rules)
    updated_inputs = replace(
        inputs,
        verify_report=updated_verify_report,
        failures=(run_path / "verify" / "failures.md").read_text(encoding="utf-8"),
    )
    (final_dir / "final_report.md").write_text(build_final_report(updated_inputs, revision_plan, rules), encoding="utf-8")
    (final_dir / "delivery_summary.md").write_text(build_delivery_summary(updated_inputs, revision_plan, rules), encoding="utf-8")
    refresh_verify_report_for_final_outputs(run_path, updated_inputs, generated_at, rules)

    update_manifest_for_phase_7(run_path, inputs.manifest, generated_at, PHASE_7_ARTIFACTS, rules)
    return FinalizeRunResult(artifact_paths=PHASE_7_ARTIFACTS)


def load_required_artifacts(run_dir: Path) -> FinalizeInputs:
    if not run_dir.exists():
        raise FinalizeRunError(f"Run directory not found: {run_dir}")
    if not run_dir.is_dir():
        raise FinalizeRunError(f"Run path is not a directory: {run_dir}")

    missing = [relative_path for relative_path in REQUIRED_PHASE_6_PATHS if not (run_dir / relative_path).exists()]
    if missing:
        first_missing = missing[0]
        raise FinalizeRunError(f"Cannot finalize run: missing {first_missing}. Run must complete Phase 6 first.")

    manifest = validate_json_model(run_dir / "manifest.json", Manifest)
    if manifest.phase not in {"phase_6", "phase_7"} or manifest.status not in {
        "reviewed_verified",
        "finalized_with_open_items",
    }:
        raise FinalizeRunError("Cannot finalize run: run must complete Phase 6 before Phase 7 final delivery.")

    return FinalizeInputs(
        manifest=manifest,
        task_brief=validate_json_model(run_dir / "task_brief.json", TaskBrief),
        inventory=validate_json_model(run_dir / "inputs" / "input_inventory.json", InputInventory),
        source_index=validate_json_model(run_dir / "knowledge" / "source_index.json", SourceIndex),
        provenance_index=read_json(run_dir / "knowledge" / "provenance_index.json"),
        knowledge_gaps=(run_dir / "knowledge" / "knowledge_gaps.md").read_text(encoding="utf-8"),
        unresolved_questions=(run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8"),
        evidence_map=read_json(run_dir / "plans" / "evidence_map.json"),
        citation_plan=read_json(run_dir / "plans" / "citation_plan.json"),
        claim_support_matrix=read_json(run_dir / "plans" / "claim_support_matrix.json"),
        full_draft=(run_dir / "draft" / "full_draft.md").read_text(encoding="utf-8"),
        review_report=read_json(run_dir / "review" / "review_report.json"),
        final_review=(run_dir / "review" / "final_review.md").read_text(encoding="utf-8"),
        verify_report=read_json(run_dir / "verify" / "verify_report.json"),
        failures=(run_dir / "verify" / "failures.md").read_text(encoding="utf-8"),
    )


def build_revision_plan(inputs: FinalizeInputs, generated_at: str, rules: DocumentTypeRules) -> dict[str, Any]:
    review_items = list(inputs.review_report.get("items", []))
    tasks = [build_revision_task(index, item, rules) for index, item in enumerate(review_items, start=1)]
    next_index = len(tasks) + 1

    for failure_index, failure in enumerate(inputs.verify_report.get("blocking_failures", []), start=1):
        if blocking_failure_already_covered(str(failure), tasks):
            continue
        tasks.append(
            {
                "revision_task_id": f"RT-{next_index:03d}",
                "source_review_id": f"VERIFY-{failure_index:03d}",
                "severity": "P0",
                "category": "verification_blocker",
                "section_id": "",
                "task_id": "",
                "artifact": "verify/verify_report.json",
                "action": "carry_to_final_open_issues",
                "auto_applicable": True,
                "requires_user_confirmation": False,
                "result": "carried_forward",
                "notes": str(failure),
            }
        )
        next_index += 1

    pending_user_tasks = [task for task in tasks if task["requires_user_confirmation"]]
    open_item_tasks = [task for task in tasks if task["result"] in {"pending", "carried_forward", "unresolved"}]

    return {
        "run_id": inputs.manifest.run_id,
        "phase": "phase_7",
        "generated_at": generated_at,
        "status": "applied_with_open_items",
        "document_type": {
            "task_type": rules.task_type,
            "display_name": rules.display_name,
            "critical_claims": list(rules.critical_claims),
            "requires_human_confirmation": list(rules.requires_human_confirmation),
            "forbidden_final_claims": list(rules.forbidden_final_claims),
            "confirmation_marker": rules.confirmation_marker,
        },
        "source_artifacts": SOURCE_ARTIFACTS,
        "summary": {
            "total_review_items": len(review_items),
            "total_revision_tasks": len(tasks),
            "auto_applied_tasks": sum(1 for task in tasks if task["auto_applicable"] and task["result"] == "applied"),
            "pending_user_confirmation_tasks": len(pending_user_tasks),
            "carried_to_final_open_items": len(open_item_tasks),
            "status": rules.default_final_status,
        },
        "tasks": tasks,
        "open_items_policy": {
            "hara_professional_judgments_finalized": False,
            "human_confirmation_available": False,
            "final_delivery_approved": False,
            "remaining_open_items_carried_to_final_report": True,
            "document_type": rules.task_type,
            "document_type_display_name": rules.display_name,
            "critical_claims_finalized": False,
            "allowed_final_statuses": list(rules.allowed_final_statuses),
            "default_final_status": rules.default_final_status,
        },
    }


def build_revision_task(index: int, item: dict[str, Any], rules: DocumentTypeRules) -> dict[str, Any]:
    severity = str(item.get("severity", "P2"))
    category = str(item.get("category", "unknown"))
    description = str(item.get("description", ""))
    source_review_id = str(item.get("review_id") or item.get("id") or f"REV-UNKNOWN-{index:03d}")
    searchable = f"{category} {description} {item.get('suggested_fix', '')}".lower()
    requires_confirmation = any(term in searchable for term in confirmation_terms(rules))
    action = action_for_review_item(searchable, requires_confirmation, rules)

    if requires_confirmation:
        result = "pending"
    elif action in {"carry_to_final_open_issues", "mark_unresolved", "omit_unsupported_final_claim"}:
        result = "carried_forward"
    else:
        result = "applied"

    return {
        "revision_task_id": f"RT-{index:03d}",
        "source_review_id": source_review_id,
        "severity": severity,
        "category": category,
        "section_id": str(item.get("section_id", "")),
        "task_id": str(item.get("task_id", "")),
        "artifact": str(item.get("artifact", "")),
        "action": action,
        "auto_applicable": True,
        "requires_user_confirmation": requires_confirmation,
        "result": result,
        "notes": notes_for_task(action, requires_confirmation, description, rules),
    }


def action_for_review_item(searchable: str, requires_confirmation: bool, rules: DocumentTypeRules) -> str:
    if "final_hara_conclusion" in searchable or any(pattern in searchable for pattern in forbidden_final_patterns(rules)):
        return "omit_unsupported_final_claim"
    if requires_confirmation:
        return "preserve_NEEDS_USER_CONFIRMATION"
    if any(term in searchable for term in OPEN_ITEM_TERMS):
        if "unresolved" in searchable or "knowledge gap" in searchable:
            return "mark_unresolved"
        return "carry_to_final_open_issues"
    if any(term in searchable for term in FORMAT_TERMS):
        return "copy_without_change"
    return "add_boundary_note"


def notes_for_task(
    action: str,
    requires_confirmation: bool,
    description: str,
    rules: DocumentTypeRules,
) -> str:
    if requires_confirmation:
        return f"{professional_judgment_label(rules)} remains pending human confirmation."
    if action == "omit_unsupported_final_claim":
        return "Unsupported final professional claim is replaced with a confirmation marker in the revised draft."
    if action in {"carry_to_final_open_issues", "mark_unresolved"}:
        return description or "Open item is carried into final delivery."
    return f"Mechanical Phase 7 boundary handling applied without changing {rules.display_name} professional content."


def blocking_failure_already_covered(failure: str, tasks: list[dict[str, Any]]) -> bool:
    return any(task["source_review_id"] and task["source_review_id"] in failure for task in tasks)


def build_revised_draft(inputs: FinalizeInputs, revision_plan: dict[str, Any], rules: DocumentTypeRules) -> str:
    summary = revision_plan["summary"]
    sanitized_draft = sanitize_unsafe_final_claims(inputs.full_draft, rules)
    judgments_label = professional_judgment_label(rules, plural=True)
    lines = [
        f"# {rules.display_name}修订草稿",
        "",
        f"Run id: {inputs.manifest.run_id}",
        f"Document type: {rules.display_name}",
        "",
        "Status: revised_with_open_items",
        "",
        "## Phase 7 修订边界说明",
        "",
        "本修订草稿由以下 artifacts deterministic 生成：",
        "- draft/full_draft.md",
        "- review/review_report.json",
        "- review/final_review.md",
        "- verify/verify_report.json",
        "- verify/failures.md",
        "- plans/unresolved_questions.md",
        "- knowledge/knowledge_gaps.md",
        "",
        "它不替代合格人工审查。",
        f"标记处的 {judgments_label} 仍保持 pending。",
        critical_claim_boundary_sentence(rules),
        "",
        "## 已应用修订摘要",
        "",
        f"- 生成的 revision tasks：{summary['total_revision_tasks']}",
        f"- 自动应用的 mechanical revisions：{summary['auto_applied_tasks']}",
        f"- Pending human confirmations：{summary['pending_user_confirmation_tasks']}",
        f"- 带入 final report 的开放项：{summary['carried_to_final_open_items']}",
        "",
        "## 剩余人工确认项",
        "",
        *remaining_human_confirmation_lines(revision_plan, rules),
        "",
        "## 带 Phase 7 注释的原始保守草稿",
        "",
        sanitized_draft,
        "",
    ]
    return "\n".join(lines)


def build_change_log(inputs: FinalizeInputs, revision_plan: dict[str, Any], rules: DocumentTypeRules) -> str:
    lines = [
        "# Phase 7 Change Log",
        "",
        f"Run id: {inputs.manifest.run_id}",
        "",
        "## Summary",
        "",
        "- Revision plan: revision_plan.json",
        "- Revised draft: revised/full_draft.md",
        "- Final report: final/final_report.md",
        "- Delivery summary: final/delivery_summary.md",
        f"- Document type: {rules.display_name}",
        f"- Status: {rules.default_final_status}",
        "",
        "## Source Artifacts",
        "",
        *[f"- {path}" for path in SOURCE_ARTIFACTS.values()],
        "",
        "## Applied Mechanical Changes",
        "",
        "| Task ID | Source Review ID | Severity | Category | Action | Result |",
        "|---|---|---|---|---|---|",
    ]
    for task in revision_plan["tasks"]:
        lines.append(
            f"| {task['revision_task_id']} | {task['source_review_id']} | {task['severity']} | "
            f"{task['category']} | {task['action']} | {task['result']} |"
        )

    lines.extend(
        [
            "",
            "## Items Carried Forward",
            "",
            *task_bullet_lines(
                [
                    task
                    for task in revision_plan["tasks"]
                    if task["result"] in {"pending", "carried_forward", "unresolved"}
                ]
            ),
            "",
            "## Not Changed Automatically",
            "",
            f"- {professional_judgment_label(rules, plural=True)} were not finalized.",
            *critical_claim_lines(rules),
            "- Unsupported, weak, missing, or unresolved items were carried forward instead of being silently repaired.",
            "",
            "## Phase Boundary",
            "",
            "Phase 7 did not implement /write, trace, learning, candidate profile update, plugin skeleton, or HITL approval.",
            "",
        ]
    )
    return "\n".join(lines)


def build_final_report(inputs: FinalizeInputs, revision_plan: dict[str, Any], rules: DocumentTypeRules) -> str:
    final_title = rules.output_labels.get("final_report_title", f"{rules.display_name} 最终交付包")
    judgments_label = professional_judgment_label(rules, plural=True)
    lines = [
        f"# {final_title}",
        "",
        f"Run id: {inputs.manifest.run_id}",
        f"Document type: {rules.display_name}",
        "",
        f"Status: {rules.default_final_status}",
        "",
        "## 核心证据边界",
        "",
        "本最终交付包由保守草稿、审查结果、验证结果和 deterministic Phase 7 revision plan 生成。",
        "",
        "它是 review-ready artifact，不替代合格人工审查或专业批准。",
        f"标记处的 {judgments_label} 仍保持 pending。",
        critical_claim_boundary_sentence(rules),
        "此文档类型的 critical claims 包括：",
        *critical_claim_lines(rules),
        "除非记录了明确证据和 HITL 确认，否则禁止输出最终批准类结论。",
        "",
        "## 来源依据",
        "",
        "- inputs/input_inventory.json",
        "- knowledge/source_index.json",
        "- knowledge/provenance_index.json",
        "- knowledge/knowledge_gaps.md",
        "- plans/evidence_map.json",
        "- plans/citation_plan.json",
        "- plans/claim_support_matrix.json",
        "- plans/unresolved_questions.md",
        "- draft/full_draft.md",
        "- review/final_review.md",
        "- verify/verify_report.json",
        "- revised/full_draft.md",
        "",
        "## 修订后草稿",
        "",
        "查看：revised/full_draft.md",
        "",
        "## 审查摘要",
        "",
        *review_summary_lines(inputs.review_report),
        "",
        "## 验证摘要",
        "",
        *verification_summary_lines(inputs.verify_report),
        "",
        "## 溯源摘要",
        "",
        *provenance_summary_lines(inputs),
        "",
        "## Critical claim 来源支持",
        "",
        *claim_support_summary_lines(inputs, rules),
        "",
        f"## {open_items_heading(rules)}",
        "",
        *open_hara_confirmation_lines(revision_plan, rules),
        "",
        "## 证据不足 / 弱证据",
        "",
        *evidence_issue_lines(inputs),
        "",
        "## 知识缺口和不可用材料",
        "",
        *knowledge_gap_summary_lines(inputs.inventory),
        "",
        "## 剩余阻塞项",
        "",
        *remaining_blocker_lines(inputs, revision_plan),
        "",
        "## 交付限制",
        "",
        "- 本交付包不是合格人工批准记录。",
        f"- 对未解决的 {rules.display_name} 判断，{confirmation_marker_summary(rules)} 仍是权威状态标记。",
        *final_material_limitation_lines(inputs.inventory),
        f"- {rules.sample_policy}",
        f"- {rules.reference_policy}",
        "",
        "## 下一步人工动作",
        "",
        f"- 使用前必须由合格人工审查者确认 {professional_judgment_label(rules, plural=True)}。",
        "- 解决列出的材料缺口、证据不足/弱证据和未解决来源问题。",
        f"- 复核所有标记为 {confirmation_marker_summary(rules)} 的项目。",
        "",
    ]
    return "\n".join(lines)


def build_delivery_summary(inputs: FinalizeInputs, revision_plan: dict[str, Any], rules: DocumentTypeRules) -> str:
    lines = [
        "# 交付摘要",
        "",
        f"Run id: {inputs.manifest.run_id}",
        f"Document type: {rules.display_name}",
        "",
        f"Status: {rules.default_final_status}",
        "",
        "## 生成的内容",
        "",
        *[f"- {path}" for path in PHASE_7_ARTIFACTS],
        "",
        "## 使用的输入",
        "",
        *input_lines(inputs.inventory),
        "",
        "## 审查 / 验证结果",
        "",
        f"- 审查状态：{inputs.review_report.get('status', 'unknown')}",
        f"- 验证状态：{inputs.verify_report.get('status', 'unknown')}",
        f"- 修订任务数：{revision_plan['summary']['total_revision_tasks']}",
        f"- 继续带入最终交付的开放项：{revision_plan['summary']['carried_to_final_open_items']}",
        "",
        "## 溯源摘要",
        "",
        *provenance_summary_lines(inputs),
        "",
        "## 开放确认项",
        "",
        *open_confirmation_lines(inputs, rules),
        "",
        "## 剩余阻塞项",
        "",
        *remaining_blocker_lines(inputs, revision_plan),
        "",
        "## 需要人工确认",
        "",
        *open_hara_confirmation_lines(revision_plan, rules),
        "",
        "## 已知限制",
        "",
        f"- 当前交付状态为 {rules.default_final_status}，不是专业批准。",
        f"- 在将 {rules.display_name} 判断视为已确认前，必须完成合格人工审查。",
        *delivery_evidence_limitation_lines(inputs),
        *delivery_material_limitation_lines(inputs.inventory),
        "",
        "## Workflow 范围说明",
        "",
        "本交付摘要由 finalization step 生成。",
        "当 learning-run 或 write-run 生成 trace / learning artifacts 时，它们会存放在 trace/ 和 learning/ 下。",
        "candidate update 保持 proposed / inactive，除非后续被明确批准。",
        "",
        "## 建议下一步",
        "",
        f"在将任何 {professional_judgment_label(rules)} 视为已确认前，必须完成合格人工审查。",
        "",
    ]
    return "\n".join(lines)


def provenance_summary_lines(inputs: FinalizeInputs) -> list[str]:
    sources = list(inputs.provenance_index.get("sources", []))
    hitl_sources = list(inputs.provenance_index.get("hitl_sources", []))
    tier_counts = {
        "T1_PROJECT_SOURCE": 0,
        "T2_TEMPLATE_CHECKLIST": 0,
        "T3_REFERENCE_METHODOLOGY": 0,
        "T4_SAMPLE_STYLE_ONLY": 0,
        "T5_AI_INFERENCE": 0,
    }
    seen_file_tiers: set[tuple[str, str]] = set()
    for source in sources:
        file_id = str(source.get("file_id", source.get("source_id", "")))
        tier = str(source.get("source_tier", "T5_AI_INFERENCE"))
        key = (file_id, tier)
        if key in seen_file_tiers:
            continue
        seen_file_tiers.add(key)
        if tier in tier_counts:
            tier_counts[tier] += 1
    summary = inputs.claim_support_matrix.get("summary", {})
    return [
        f"- T0 HITL 人工确认：{len(hitl_sources)}",
        f"- T1 project source 使用数量：{tier_counts['T1_PROJECT_SOURCE']}",
        f"- T2 template/checklist 约束使用数量：{tier_counts['T2_TEMPLATE_CHECKLIST']}",
        f"- T3 reference methodology 使用数量：{tier_counts['T3_REFERENCE_METHODOLOGY']}",
        f"- T4 sample style-only 输入数量：{tier_counts['T4_SAMPLE_STYLE_ONLY']}，未作为事实支持。",
        f"- T5 AI inference-only 声明：{summary.get('unsupported_claims', 0)} 个 unsupported；如存在均需确认。",
        f"- Pending human confirmations：{summary.get('pending_human_confirmations', 0)}",
        f"- Profile version：{profile_version_label(inputs)}",
        "- sample 材料仅作为风格/结构参考，未作为事实支持。",
        "- reference 材料仅作为方法/背景参考，未作为项目事实支持。",
    ]


def claim_support_summary_lines(inputs: FinalizeInputs, rules: DocumentTypeRules) -> list[str]:
    claims = list(inputs.claim_support_matrix.get("claims", []))
    if not claims:
        return ["未生成 critical claim support matrix 条目。"]
    lines: list[str] = []
    for claim in claims:
        support = list(claim.get("source_support", []))
        source_tiers = sorted({str(item.get("source_tier", "T5_AI_INFERENCE")) for item in support})
        source_ids = [str(item.get("source_id", "NO_SOURCE")) for item in support if item.get("source_id")]
        evidence_ids = [str(item.get("evidence_id", "NO_EVIDENCE")) for item in support if item.get("evidence_id")]
        lines.extend(
            [
                f"- 声明状态：{claim.get('claim_category', 'unknown')} => {claim.get('claim_status', 'unsupported')}",
                f"  - 证据状态：{claim.get('evidence_status', 'missing')}",
                f"  - 来源层级：{', '.join(source_tiers) if source_tiers else 'NO_SOURCE'}",
                f"  - 来源 ID：{', '.join(source_ids) if source_ids else 'NO_SOURCE'}",
                f"  - 证据 ID：{', '.join(evidence_ids) if evidence_ids else 'NO_EVIDENCE'}",
                f"  - 人工确认状态：{claim.get('human_confirmation_status', 'not_applicable')}",
                f"  - Profile version：{profile_version_label(inputs)}",
            ]
        )
        if claim.get("human_confirmation_status") == "pending":
            lines.append(f"  - 必需标记：{rules.confirmation_marker}")
    return lines


def open_confirmation_lines(inputs: FinalizeInputs, rules: DocumentTypeRules) -> list[str]:
    pending_claims = [
        claim
        for claim in inputs.claim_support_matrix.get("claims", [])
        if claim.get("human_confirmation_status") == "pending"
    ]
    if not pending_claims:
        return ["无。"]
    lines: list[str] = []
    for claim in pending_claims:
        lines.append(
            f"- {claim.get('claim_category', 'unknown')}: {rules.confirmation_marker}, "
            f"claim_status={claim.get('claim_status', 'needs_confirmation')}, "
            f"human_confirmation_status={claim.get('human_confirmation_status', 'pending')}"
        )
    return lines


def profile_version_label(inputs: FinalizeInputs) -> str:
    profile_id = inputs.provenance_index.get("profile_id")
    profile_version = inputs.provenance_index.get("profile_version")
    if profile_id and profile_version:
        return f"{profile_id}@{profile_version}"
    return f"builtin@{inputs.task_brief.task_type}"


def refresh_verify_report_for_final_outputs(
    run_dir: Path,
    inputs: FinalizeInputs,
    generated_at: str,
    rules: DocumentTypeRules,
) -> dict[str, Any]:
    facts_by_name = {
        check["name"]: {
            "status": check["status"],
            "details": check["details"],
            "related_artifacts": check.get("related_artifacts", []),
            "review_item_ids": check.get("review_item_ids", []),
        }
        for check in inputs.verify_report.get("checks", [])
    }
    provenance_facts, _provenance_items = build_provenance_verify_facts(
        provenance_index=inputs.provenance_index,
        claim_support_matrix=inputs.claim_support_matrix,
        final_report_text=(run_dir / "final" / "final_report.md").read_text(encoding="utf-8"),
        delivery_summary_text=(run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8"),
        external_profile_expected=inputs.task_brief.profile is not None,
    )
    facts_by_name.update(provenance_facts)
    review_items = list(inputs.review_report.get("items", []))
    final_readiness = inputs.review_report.get("summary", {}).get("final_readiness", "blocked")
    updated_verify_report = build_verify_report(
        run_id=inputs.manifest.run_id,
        generated_at=generated_at,
        facts=facts_by_name,
        review_items=review_items,
        final_readiness=final_readiness,
        rules=rules,
    )
    write_json(run_dir / "verify" / "verify_report.json", updated_verify_report)
    (run_dir / "verify" / "failures.md").write_text(
        render_failures_md(inputs.manifest.run_id, updated_verify_report, review_items, rules=rules),
        encoding="utf-8",
    )
    return updated_verify_report


def sanitize_unsafe_final_claims(text: str, rules: DocumentTypeRules) -> str:
    revised_lines: list[str] = []
    for line in text.splitlines():
        lowered = line.strip().lower()
        if lowered and any(pattern in lowered for pattern in forbidden_final_patterns(rules)) and not any(
            allowed in lowered for allowed in ALLOWED_FINAL_CONTEXTS
        ):
            revised_lines.append(safe_replacement_line(rules))
        else:
            revised_lines.append(line)
    return "\n".join(revised_lines)


def remaining_human_confirmation_lines(revision_plan: dict[str, Any], rules: DocumentTypeRules) -> list[str]:
    tasks = [task for task in revision_plan["tasks"] if task["requires_user_confirmation"]]
    if not tasks:
        return ["- review_report.json 中未发现确认任务。"]
    return [
        f"- {rules.display_name} 敏感项目中的 {rules.confirmation_marker} 仍保持 pending。",
        *domain_placeholder_lines(rules),
        *task_bullet_lines(tasks),
    ]


def open_hara_confirmation_lines(revision_plan: dict[str, Any], rules: DocumentTypeRules) -> list[str]:
    tasks = [task for task in revision_plan["tasks"] if task["requires_user_confirmation"]]
    if not tasks:
        return [
            "- 未发现需要确认的审查任务。",
            f"- revised draft 中的 {rules.confirmation_marker} 仍约束任何专业判断。",
            *domain_placeholder_lines(rules, include_where_present=True),
        ]
    return [
        f"- {rules.confirmation_marker} 项仍保持 pending。",
        *domain_placeholder_lines(rules),
        *task_bullet_lines(tasks),
    ]


def confirmation_terms(rules: DocumentTypeRules) -> tuple[str, ...]:
    terms = [
        rules.task_type,
        rules.display_name,
        rules.confirmation_marker,
        professional_judgment_label(rules),
        professional_judgment_label(rules, plural=True),
        *rules.critical_claims,
        *rules.requires_human_confirmation,
    ]
    return tuple(dedupe([term.lower() for term in terms if term]))


def forbidden_final_patterns(rules: DocumentTypeRules) -> tuple[str, ...]:
    return tuple(pattern.lower() for pattern in rules.forbidden_final_claims)


def safe_replacement_line(rules: DocumentTypeRules) -> str:
    return f"{rules.confirmation_marker}: Unsupported final professional judgment omitted by Phase 7."


def professional_judgment_label(rules: DocumentTypeRules, plural: bool = False) -> str:
    key = "professional_judgments" if plural else "professional_judgment"
    fallback = "professional judgments" if plural else "professional judgment"
    return rules.terminology.get(key, fallback)


def open_items_heading(rules: DocumentTypeRules) -> str:
    return rules.output_labels.get("open_items_heading", "开放确认项")


def confirmation_marker_summary(rules: DocumentTypeRules) -> str:
    markers = [rules.confirmation_marker, "pending", "TBD"]
    if rules.task_type == "hara":
        markers.extend(["S? / E? / C?", "ASIL candidate remains TBD"])
    return ", ".join(markers)


def domain_placeholder_lines(rules: DocumentTypeRules, include_where_present: bool = False) -> list[str]:
    if rules.task_type != "hara":
        return [f"- {professional_judgment_label(rules, plural=True)} 在确认前保持 unresolved。"]
    if include_where_present:
        return ["- 如存在 rating placeholder，则 S? / E? / C? 保持不变；ASIL candidate 在确认前保持 TBD。"]
    return ["- Rating placeholders 保持 S? / E? / C?，ASIL candidate 保持 TBD。"]


def critical_claim_boundary_sentence(rules: DocumentTypeRules) -> str:
    claims = ", ".join(rules.critical_claims)
    return (
        "对于此文档类型列出的 critical claims，engine 不会在缺少证据或 HITL 确认时将其最终确认："
        f"{claims}。"
    )


def critical_claim_lines(rules: DocumentTypeRules) -> list[str]:
    return [f"- {claim}" for claim in rules.critical_claims]


def forbidden_claim_lines(rules: DocumentTypeRules) -> list[str]:
    return [f"- {claim}" for claim in rules.forbidden_final_claims]


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def evidence_issue_lines(inputs: FinalizeInputs) -> list[str]:
    issues = collect_evidence_issues(inputs)
    if not issues:
        return [
            "在 evidence_map.json、unresolved_questions.md、citation_plan.json、review_report.json 或 "
            "verify_report.json 中未发现 unsupported 或 weak evidence 问题。"
        ]
    return [
        "以下证据问题由 evidence planning、citation planning、review 或 verification 继续带入：",
        "",
        *[format_evidence_issue(issue) for issue in issues],
    ]


def collect_evidence_issues(inputs: FinalizeInputs) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add_issue(
        issue_id: object,
        section_id: object,
        status: object,
        title: object,
        detail: object,
        source: str,
    ) -> None:
        normalized_status = normalize_status(status)
        if not normalized_status:
            return
        normalized_id = clean_text(issue_id) or "UNSPECIFIED"
        normalized_section = clean_text(section_id) or "UNSPECIFIED"
        key = (normalized_id, normalized_section, normalized_status)
        if key in seen:
            return
        seen.add(key)
        issues.append(
            {
                "issue_id": normalized_id,
                "section_id": normalized_section,
                "status": normalized_status,
                "title": clean_text(title) or source,
                "detail": clean_text(detail) or "Evidence issue carried forward.",
                "source": source,
            }
        )

    collect_evidence_map_issues(inputs.evidence_map, add_issue)
    collect_unresolved_question_issues(inputs.unresolved_questions, add_issue)
    collect_citation_plan_issues(inputs.citation_plan, add_issue)
    collect_review_report_evidence_issues(inputs.review_report, add_issue)
    collect_verify_report_evidence_issues(inputs.verify_report, add_issue)
    return issues


def collect_evidence_map_issues(evidence_map: dict[str, Any], add_issue: Any) -> None:
    questions = evidence_map.get("questions", [])
    if not isinstance(questions, list):
        return
    for question in questions:
        if not isinstance(question, dict):
            continue
        status = first_present(question, ["status", "evidence_status", "support_status"])
        if normalize_status(status) not in EVIDENCE_ISSUE_STATUSES:
            continue
        add_issue(
            question.get("question_id"),
            question.get("section_id"),
            status,
            question.get("section_title"),
            question.get("unresolved_reason") or question.get("question") or "Evidence issue carried forward.",
            "evidence_map.json",
        )


def collect_unresolved_question_issues(unresolved_questions: str, add_issue: Any) -> None:
    current_status = ""
    for raw_line in unresolved_questions.splitlines():
        line = raw_line.strip()
        lowered = line.lower()
        if lowered.startswith("## "):
            if "unsupported" in lowered and "question" in lowered:
                current_status = "unsupported"
            elif "weak" in lowered and "evidence" in lowered:
                current_status = "weak"
            elif "human confirmation" in lowered:
                current_status = "requires_human_confirmation"
            elif "missing" in lowered or "phase boundary" in lowered:
                current_status = ""
            continue
        if not current_status or not line.startswith("- "):
            continue
        if lowered in {"- none.", "- no unsupported questions.", "- no weak evidence questions."}:
            continue
        parts = [part.strip() for part in line[2:].split("|")]
        if len(parts) >= 4:
            add_issue(parts[0], parts[1], current_status, parts[2], parts[3], "unresolved_questions.md")
        elif any(term in lowered for term in EVIDENCE_RELATED_TERMS):
            add_issue("UNRESOLVED", "", current_status, "unresolved_questions.md", line[2:], "unresolved_questions.md")


def collect_citation_plan_issues(citation_plan: dict[str, Any], add_issue: Any) -> None:
    sections = citation_plan.get("sections", [])
    if not isinstance(sections, list):
        return
    for section in sections:
        if not isinstance(section, dict):
            continue
        section_id = section.get("section_id")
        section_title = section.get("section_title")
        for claim in safe_list(section.get("unsupported_claims")):
            if not isinstance(claim, dict):
                continue
            add_issue(
                claim.get("question_id") or claim.get("claim_id"),
                claim.get("section_id") or section_id,
                claim.get("reason") or "unsupported",
                section_title,
                claim.get("description") or claim.get("required_action"),
                "citation_plan.json",
            )
        for note in safe_list(section.get("weak_evidence_notes")):
            if not isinstance(note, dict):
                continue
            add_issue(
                note.get("question_id"),
                section_id,
                "weak",
                section_title,
                note.get("note") or note.get("required_action"),
                "citation_plan.json",
            )
        for slot in safe_list(section.get("citation_slots")):
            if not isinstance(slot, dict):
                continue
            status = slot.get("status")
            if normalize_status(status) not in EVIDENCE_ISSUE_STATUSES:
                continue
            add_issue(
                slot.get("question_id") or slot.get("slot_id"),
                slot.get("section_id") or section_id,
                status,
                section_title,
                slot.get("description") or slot.get("instruction"),
                "citation_plan.json",
            )


def collect_review_report_evidence_issues(review_report: dict[str, Any], add_issue: Any) -> None:
    items = review_report.get("items", [])
    if not isinstance(items, list):
        return
    for item in items:
        if not isinstance(item, dict):
            continue
        searchable = " ".join(
            clean_text(item.get(field))
            for field in ["category", "description", "suggested_fix", "artifact"]
        ).lower()
        if not any(term in searchable for term in EVIDENCE_RELATED_TERMS):
            continue
        add_issue(
            item.get("review_id") or item.get("id"),
            item.get("section_id") or item.get("task_id"),
            item.get("category") or item.get("severity"),
            item.get("artifact") or "review_report.json",
            item.get("description") or item.get("suggested_fix"),
            "review_report.json",
        )


def collect_verify_report_evidence_issues(verify_report: dict[str, Any], add_issue: Any) -> None:
    checks = verify_report.get("checks", [])
    if not isinstance(checks, list):
        return
    for check in checks:
        if not isinstance(check, dict):
            continue
        status = clean_text(check.get("status")).lower()
        if status not in {"failed", "blocked", "warning"}:
            continue
        searchable = " ".join(
            clean_text(check.get(field))
            for field in ["name", "details", "related_artifacts"]
        ).lower()
        if not any(term in searchable for term in EVIDENCE_RELATED_TERMS):
            continue
        related = ", ".join(clean_text(item) for item in safe_list(check.get("related_artifacts")) if clean_text(item))
        add_issue(
            check.get("check_id"),
            related,
            status,
            check.get("name") or "verify_report.json",
            check.get("details"),
            "verify_report.json",
        )


def format_evidence_issue(issue: dict[str, str]) -> str:
    return (
        f"- {issue['issue_id']} | {issue['section_id']} | {issue['status']} | "
        f"{issue['title']} | {issue['detail']}"
    )


def normalize_status(value: object) -> str:
    status = clean_text(value).lower().replace(" ", "_").replace("-", "_")
    if status == "weak_evidence":
        return "weak"
    if status == "missing_source_support":
        return "missing_evidence"
    return status


def first_present(data: dict[str, Any], keys: list[str]) -> object:
    for key in keys:
        value = data.get(key)
        if clean_text(value):
            return value
    return ""


def safe_list(value: object) -> list[Any]:
    return value if isinstance(value, list) else []


def clean_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(clean_text(item) for item in value if clean_text(item))
    return str(value).strip()


def knowledge_gap_summary_lines(inventory: InputInventory) -> list[str]:
    missing = [file for file in inventory.files if file.parse_status == "missing"]
    unsupported = [file for file in inventory.files if file.parse_status == "unsupported"]
    failed = [file for file in inventory.files if file.parse_status == "failed"]
    non_fact_exclusions = [
        file
        for file in inventory.files
        if file.role in NON_FACT_SOURCE_EXCLUSION_ROLES and file.is_fact_source is False
    ]

    lines: list[str] = []
    if not missing and not unsupported and not failed:
        lines.extend(["本次运行未发现 missing、unsupported 或 failed 输入材料。", ""])
    else:
        lines.extend(material_gap_section_lines("Missing files：", missing, "missing"))
        lines.extend(material_gap_section_lines("Unsupported files：", unsupported, "unsupported"))
        lines.extend(material_gap_section_lines("Failed files：", failed, "failed"))
        lines.append("")

    lines.append("已从事实索引中排除的 non-fact-source 材料：")
    if non_fact_exclusions:
        for file in non_fact_exclusions:
            lines.append(f"- {file.file_id} | {file.path} | role={file.role} | is_fact_source=false")
    else:
        lines.append("- 无。")
    return lines


def material_gap_section_lines(heading: str, files: list[Any], status: str) -> list[str]:
    lines = [heading]
    if not files:
        lines.append("- 无。")
        return lines
    for file in files:
        if status == "missing":
            lines.append(f"- {file.file_id} | {file.path}")
        elif status == "unsupported":
            lines.append(f"- {file.file_id} | {file.path} | format={file.format}")
        else:
            detail = f" | error={file.error_message}" if file.error_message else ""
            lines.append(f"- {file.file_id} | {file.path}{detail}")
    return lines


def inventory_has_material_gaps(inventory: InputInventory) -> bool:
    return any(file.parse_status in MATERIAL_GAP_STATUSES for file in inventory.files)


def final_material_limitation_lines(inventory: InputInventory) -> list[str]:
    if inventory_has_material_gaps(inventory):
        return ["- Missing、unsupported 或 failed 输入材料会作为开放交付限制保留。"]
    return ["- 本次运行未发现 missing、unsupported 或 failed 输入材料。"]


def delivery_material_limitation_lines(inventory: InputInventory) -> list[str]:
    if inventory_has_material_gaps(inventory):
        return ["- Missing 或 unsupported 输入材料仍作为开放知识缺口保留。"]
    return ["- 本次运行未发现 missing 或 unsupported 输入材料。"]


def delivery_evidence_limitation_lines(inputs: FinalizeInputs) -> list[str]:
    if collect_evidence_issues(inputs):
        return ["- Unsupported、weak 或 unresolved 证据项会按上游 artifact 记录继续保持开放。"]
    return [
        "- 在 evidence_map.json、unresolved_questions.md、citation_plan.json、review_report.json 或 "
        "verify_report.json 中未发现 unsupported 或 weak evidence 问题。"
    ]


def remaining_blocker_lines(inputs: FinalizeInputs, revision_plan: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    blocker_tasks = [task for task in revision_plan["tasks"] if task["result"] in {"pending", "carried_forward", "unresolved"}]
    lines.extend(task_bullet_lines(blocker_tasks))

    blocking_failures = inputs.verify_report.get("blocking_failures", [])
    if blocking_failures:
        lines.append("- Verification blocking failures：")
        lines.extend([f"  - {failure}" for failure in blocking_failures])

    if not lines:
        return ["- Phase 6 review 或 verification 未报告剩余阻塞项。"]
    return lines


def review_summary_lines(review_report: dict[str, Any]) -> list[str]:
    summary = review_report.get("summary", {})
    return [
        f"- 审查状态：{review_report.get('status', 'unknown')}",
        f"- 审查项总数：{summary.get('total_items', len(review_report.get('items', [])))}",
        f"- P0: {summary.get('p0_items', 0)}",
        f"- P1: {summary.get('p1_items', 0)}",
        f"- P2: {summary.get('p2_items', 0)}",
        f"- Info: {summary.get('info_items', 0)}",
        f"- 阻塞项：{summary.get('blocking_items', 0)}",
        f"- Readiness：{summary.get('final_readiness', 'unknown')}",
    ]


def verification_summary_lines(verify_report: dict[str, Any]) -> list[str]:
    summary = verify_report.get("summary", {})
    return [
        f"- 验证状态：{verify_report.get('status', 'unknown')}",
        f"- 通过检查数：{summary.get('passed', 0)}",
        f"- 失败检查数：{summary.get('failed', 0)}",
        f"- 阻塞检查数：{summary.get('blocked', 0)}",
        f"- Warnings：{summary.get('warnings', 0)}",
        f"- Final readiness：{summary.get('final_readiness', 'unknown')}",
    ]


def input_lines(inventory: InputInventory) -> list[str]:
    lines: list[str] = []
    for file in inventory.files:
        source_status = "fact source" if file.is_fact_source else "non-fact input"
        lines.append(f"- {file.path} | role={file.role} | parse_status={file.parse_status} | {source_status}")
    return lines


def task_bullet_lines(tasks: list[dict[str, Any]]) -> list[str]:
    if not tasks:
        return ["- None recorded."]
    lines = []
    for task in tasks:
        lines.append(
            f"- {task['revision_task_id']} | {task['source_review_id']} | {task['severity']} | "
            f"{task['category']} | {task['action']} | {task['result']} | {task['notes']}"
        )
    return lines


def markdown_excerpt_lines(text: str) -> list[str]:
    stripped = text.strip()
    if not stripped:
        return ["- No content was recorded."]
    return stripped.splitlines()


def update_manifest_for_phase_7(
    run_dir: Path,
    manifest: Manifest,
    generated_at: str,
    artifact_paths: list[str],
    rules: DocumentTypeRules,
) -> None:
    new_records = [
        ArtifactRecord(path=artifact_path, kind=artifact_kind(artifact_path), created_at=generated_at)
        for artifact_path in artifact_paths
    ]
    updated_manifest = Manifest(
        run_id=manifest.run_id,
        task_file=manifest.task_file,
        created_at=manifest.created_at,
        status=rules.default_final_status,
        phase="phase_7",
        artifacts=upsert_artifacts(manifest.artifacts, new_records),
        profile=manifest.profile,
    )
    write_json(run_dir / "manifest.json", updated_manifest.model_dump(exclude_defaults=True, exclude_none=True))


def artifact_kind(artifact_path: str) -> str:
    return {
        "revision_plan.json": "revision_plan",
        "revised/full_draft.md": "revised_full_draft",
        "revised/change_log.md": "revision_change_log",
        "final/final_report.md": "final_report",
        "final/delivery_summary.md": "delivery_summary",
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
        raise FinalizeRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise FinalizeRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise FinalizeRunError(f"Required artifact not found: {path}") from exc
    try:
        return model_class.model_validate(loaded)
    except ValidationError as exc:
        raise FinalizeRunError(f"Invalid artifact contract for {path}: {format_validation_error(exc)}") from exc


def read_json(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise FinalizeRunError(f"Invalid JSON in {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise FinalizeRunError(f"Invalid encoding in {path}: {exc}") from exc
    except FileNotFoundError as exc:
        raise FinalizeRunError(f"Required artifact not found: {path}") from exc
    if not isinstance(loaded, dict):
        raise FinalizeRunError(f"Invalid JSON artifact: {path}: root must be an object")
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
