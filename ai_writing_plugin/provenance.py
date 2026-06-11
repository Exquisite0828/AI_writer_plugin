from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from .document_types.base import DocumentTypeRules


SOURCE_TIER_POLICY = {
    "T0_HITL": "Human confirmation.",
    "T1_PROJECT_SOURCE": "Project source that may support project facts.",
    "T2_TEMPLATE_CHECKLIST": "Template/checklist constraint for structure, review, or quality gates.",
    "T3_REFERENCE_METHODOLOGY": "Reference methodology or general background.",
    "T4_SAMPLE_STYLE_ONLY": "Sample style or expected-output shape only.",
    "T5_AI_INFERENCE": "AI summary, generated text, unknown source, or inference-only support.",
}

VALID_SOURCE_TIERS = set(SOURCE_TIER_POLICY)

ROLE_TO_TIER = {
    "source": "T1_PROJECT_SOURCE",
    "template": "T2_TEMPLATE_CHECKLIST",
    "checklist": "T2_TEMPLATE_CHECKLIST",
    "reference": "T3_REFERENCE_METHODOLOGY",
    "sample": "T4_SAMPLE_STYLE_ONLY",
    "expected_output_shape": "T4_SAMPLE_STYLE_ONLY",
    "hitl": "T0_HITL",
    "human_confirmation": "T0_HITL",
    "generated": "T5_AI_INFERENCE",
    "inferred": "T5_AI_INFERENCE",
    "unknown": "T5_AI_INFERENCE",
}

TIER_CAPABILITIES = {
    "T0_HITL": {
        "can_support_project_fact": True,
        "can_support_methodology": False,
        "can_support_style": False,
        "can_support_critical_claim": True,
    },
    "T1_PROJECT_SOURCE": {
        "can_support_project_fact": True,
        "can_support_methodology": False,
        "can_support_style": False,
        "can_support_critical_claim": True,
    },
    "T2_TEMPLATE_CHECKLIST": {
        "can_support_project_fact": False,
        "can_support_methodology": False,
        "can_support_style": False,
        "can_support_critical_claim": False,
    },
    "T3_REFERENCE_METHODOLOGY": {
        "can_support_project_fact": False,
        "can_support_methodology": True,
        "can_support_style": False,
        "can_support_critical_claim": False,
    },
    "T4_SAMPLE_STYLE_ONLY": {
        "can_support_project_fact": False,
        "can_support_methodology": False,
        "can_support_style": True,
        "can_support_critical_claim": False,
    },
    "T5_AI_INFERENCE": {
        "can_support_project_fact": False,
        "can_support_methodology": False,
        "can_support_style": False,
        "can_support_critical_claim": False,
    },
}

EVIDENCE_STATUS_BY_TIER = {
    "T0_HITL": "hitl_confirmed",
    "T1_PROJECT_SOURCE": "project_source_supported",
    "T2_TEMPLATE_CHECKLIST": "template_or_checklist_only",
    "T3_REFERENCE_METHODOLOGY": "reference_methodology_only",
    "T4_SAMPLE_STYLE_ONLY": "sample_style_only",
    "T5_AI_INFERENCE": "ai_inference_only",
}


def source_tier_for_role(role: str | None) -> str:
    if role is None:
        return "T5_AI_INFERENCE"
    return ROLE_TO_TIER.get(str(role).strip().lower(), "T5_AI_INFERENCE")


def support_capabilities_for_tier(source_tier: str | None) -> dict[str, bool]:
    return dict(TIER_CAPABILITIES.get(source_tier or "", TIER_CAPABILITIES["T5_AI_INFERENCE"]))


def source_tier_for_source(source: Any) -> str:
    existing = _value(source, "source_tier")
    if existing in VALID_SOURCE_TIERS:
        return existing
    return source_tier_for_role(_value(source, "source_role") or _value(source, "role"))


def evidence_status_for_tier(source_tier: str | None) -> str:
    return EVIDENCE_STATUS_BY_TIER.get(source_tier or "", "ai_inference_only")


def evidence_status_for_support(source_support: list[dict[str, Any]]) -> str:
    tiers = {support.get("source_tier") for support in source_support if support.get("source_tier")}
    if not tiers:
        return "missing"
    if "T0_HITL" in tiers:
        return "hitl_confirmed"
    if "T1_PROJECT_SOURCE" in tiers:
        return "project_source_supported"
    if tiers <= {"T2_TEMPLATE_CHECKLIST"}:
        return "template_or_checklist_only"
    if tiers <= {"T3_REFERENCE_METHODOLOGY"}:
        return "reference_methodology_only"
    if tiers <= {"T4_SAMPLE_STYLE_ONLY"}:
        return "sample_style_only"
    if tiers <= {"T5_AI_INFERENCE"}:
        return "ai_inference_only"
    return "mixed_but_insufficient"


def provenance_support_type(source_tier: str | None, usage: str | None = None) -> str:
    if source_tier == "T0_HITL":
        return "hitl_confirmation"
    if source_tier == "T1_PROJECT_SOURCE":
        return "project_fact"
    if source_tier == "T2_TEMPLATE_CHECKLIST":
        return "structure_constraint"
    if source_tier == "T3_REFERENCE_METHODOLOGY":
        return "methodology"
    if source_tier == "T4_SAMPLE_STYLE_ONLY":
        return "style_only"
    return "inference"


def human_confirmation_status(required: bool, source_support: list[dict[str, Any]]) -> str:
    if any(support.get("source_tier") == "T0_HITL" for support in source_support):
        return "confirmed"
    if required:
        return "pending"
    if source_support:
        return "not_required"
    return "not_applicable"


def claim_status_for_support(
    claim_category: str,
    source_support: list[dict[str, Any]],
    requires_human_confirmation: bool,
    hitl_decisions: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    del claim_category
    hitl_support = [
        support
        for support in source_support
        if support.get("source_tier") == "T0_HITL" or support.get("support_type") == "hitl_confirmation"
    ]
    if hitl_decisions:
        hitl_support = [*hitl_support, *hitl_decisions]

    evidence_status = evidence_status_for_support(source_support)
    if hitl_support:
        return {
            "claim_status": "hitl_confirmed",
            "evidence_status": "hitl_confirmed",
            "human_confirmation_status": "confirmed",
            "blocking_reason": "",
        }
    if requires_human_confirmation:
        return {
            "claim_status": "needs_confirmation",
            "evidence_status": evidence_status,
            "human_confirmation_status": "pending",
            "blocking_reason": "human_confirmation_required",
        }
    if any(
        support.get("source_tier") == "T1_PROJECT_SOURCE"
        and support.get("support_type", "project_fact") == "project_fact"
        for support in source_support
    ):
        return {
            "claim_status": "supported",
            "evidence_status": evidence_status,
            "human_confirmation_status": "not_required",
            "blocking_reason": "",
        }
    if not source_support:
        return {
            "claim_status": "unsupported",
            "evidence_status": "missing",
            "human_confirmation_status": "not_applicable",
            "blocking_reason": "missing_project_source",
        }
    if any(support.get("source_tier") in {"T2_TEMPLATE_CHECKLIST", "T3_REFERENCE_METHODOLOGY"} for support in source_support):
        return {
            "claim_status": "weak",
            "evidence_status": evidence_status,
            "human_confirmation_status": "not_required",
            "blocking_reason": "insufficient_project_source",
        }
    return {
        "claim_status": "unsupported",
        "evidence_status": evidence_status,
        "human_confirmation_status": "not_applicable",
        "blocking_reason": "unsupported_source_tier",
    }


def claim_requires_human_confirmation(
    claim_category: str,
    required_claims: Iterable[str],
) -> bool:
    claim = normalize_text(claim_category)
    claim_tokens = set(claim.split())
    for required in required_claims:
        normalized_required = normalize_text(required)
        if not normalized_required:
            continue
        if claim == normalized_required or claim in normalized_required or normalized_required in claim:
            return True
        required_tokens = set(normalized_required.split())
        if claim_tokens and claim_tokens <= required_tokens:
            return True
    return False


def build_provenance_index(
    *,
    run_id: str,
    generated_at: str,
    task_brief: Any,
    inventory: Any,
    source_index: Any,
    hitl_trace_path: Path | None = None,
) -> dict[str, Any]:
    chunk_sources_by_file_id: dict[str, list[Any]] = {}
    for source in getattr(source_index, "sources", []):
        chunk_sources_by_file_id.setdefault(source.file_id, []).append(source)

    entries: list[dict[str, Any]] = []
    for record in inventory.files:
        indexed_chunks = chunk_sources_by_file_id.get(record.file_id, [])
        if indexed_chunks:
            for source in indexed_chunks:
                entries.append(provenance_entry_for_record(record, source=source))
        else:
            entries.append(provenance_entry_for_record(record, source=None))

    profile = getattr(task_brief, "profile", None)
    return {
        "schema_version": "n4.provenance_index.v1",
        "run_id": run_id,
        "generated_at": generated_at,
        "task_type": task_brief.task_type,
        "document_type_display_name": task_brief.display_name or task_brief.task_type,
        "profile_id": getattr(profile, "profile_id", None) if profile else None,
        "profile_version": getattr(profile, "profile_version", None) if profile else None,
        "profile_source": getattr(profile, "profile_source", "builtin") if profile else "builtin",
        "source_tier_policy": SOURCE_TIER_POLICY,
        "sources": entries,
        "hitl_sources": load_hitl_sources(hitl_trace_path),
    }


def provenance_entry_for_record(record: Any, source: Any | None) -> dict[str, Any]:
    tier = source_tier_for_role(record.role)
    capabilities = support_capabilities_for_tier(tier)
    if source is not None:
        source_id = source.source_id
        section = source.section
        anchor = source.anchor
        source_indexed = True
    else:
        source_id = record.file_id
        section = ""
        anchor = ""
        source_indexed = False
    notes: list[str] = []
    if record.role in {"sample", "expected_output_shape"}:
        notes.append("style_only_not_fact_source")
    if record.role == "reference":
        notes.append("methodology_only_not_project_fact")
    if record.role in {"template", "checklist"}:
        notes.append("structure_or_review_constraint_only")
    if record.parse_status != "parsed":
        notes.append(f"parse_status={record.parse_status}")
    return {
        "source_id": source_id,
        "file_id": record.file_id,
        "path": record.path,
        "title": record.title,
        "role": record.role,
        "source_tier": tier,
        **capabilities,
        "source_date": None,
        "owner": None,
        "notes": notes,
        "parse_status": record.parse_status,
        "is_fact_source": record.is_fact_source,
        "source_indexed": source_indexed,
        "section": section,
        "anchor": anchor,
    }


def build_claim_support_matrix(
    *,
    run_id: str,
    generated_at: str,
    task_brief: Any,
    rules: DocumentTypeRules,
    citation_plan: Any,
    hitl_trace_path: Path | None = None,
) -> dict[str, Any]:
    profile = getattr(task_brief, "profile", None)
    required_claims = [*rules.requires_human_confirmation, *getattr(task_brief, "requires_human_confirmation", [])]
    all_details = [
        (section, detail)
        for section in citation_plan.sections
        for detail in section.evidence_details
    ]
    hitl_sources = load_hitl_sources(hitl_trace_path)
    claims = []
    for claim_category in rules.critical_claims:
        required = claim_requires_human_confirmation(claim_category, required_claims)
        support = source_support_for_claim(claim_category, all_details)
        claim_hitl = hitl_for_claim(claim_category, hitl_sources)
        support = [*support, *claim_hitl]
        status = claim_status_for_support(claim_category, support, required, claim_hitl)
        claims.append(
            {
                "claim_category": claim_category,
                "required_human_confirmation": required,
                "claim_status": status["claim_status"],
                "evidence_status": status["evidence_status"],
                "human_confirmation_status": status["human_confirmation_status"],
                "source_support": support,
                "blocking_reason": status["blocking_reason"],
                "notes": claim_notes(status, support),
            }
        )

    return {
        "schema_version": "n4.claim_support_matrix.v1",
        "run_id": run_id,
        "generated_at": generated_at,
        "task_type": rules.task_type,
        "profile_id": getattr(profile, "profile_id", None) if profile else None,
        "profile_version": getattr(profile, "profile_version", None) if profile else None,
        "profile_source": getattr(profile, "profile_source", "builtin") if profile else "builtin",
        "confirmation_marker": rules.confirmation_marker,
        "claims": claims,
        "summary": claim_matrix_summary(claims),
    }


def source_support_for_claim(
    claim_category: str,
    all_details: list[tuple[Any, Any]],
) -> list[dict[str, Any]]:
    claim_terms = meaningful_terms(claim_category)
    matched: list[dict[str, Any]] = []
    for section, detail in all_details:
        haystack = " ".join(
            [
                getattr(section, "section_title", ""),
                getattr(detail, "question_id", ""),
                " ".join(getattr(detail, "matched_terms", [])),
                getattr(detail, "snippet", ""),
            ]
        ).lower()
        if claim_terms and not any(term in haystack for term in claim_terms):
            continue
        matched.append(source_support_for_detail(detail))
    return dedupe_support(matched)


def source_support_for_detail(detail: Any) -> dict[str, Any]:
    source_tier = source_tier_for_source(detail)
    support_type = getattr(detail, "provenance_support_type", None) or provenance_support_type(
        source_tier,
        getattr(detail, "usage", None),
    )
    confidence = float(getattr(detail, "confidence", 0.0) or 0.0)
    if source_tier in {"T0_HITL", "T1_PROJECT_SOURCE"} and support_type in {"hitl_confirmation", "project_fact"}:
        support_strength = "strong" if confidence >= 0.5 or source_tier == "T0_HITL" else "weak"
    elif source_tier in {"T2_TEMPLATE_CHECKLIST", "T3_REFERENCE_METHODOLOGY"}:
        support_strength = "weak"
    else:
        support_strength = "unknown"
    return {
        "source_id": getattr(detail, "source_id", ""),
        "file_id": getattr(detail, "file_id", ""),
        "source_tier": source_tier,
        "evidence_id": getattr(detail, "evidence_id", ""),
        "support_type": support_type,
        "support_strength": support_strength,
    }


def source_support_for_task(evidence_details: list[Any]) -> list[dict[str, Any]]:
    return [source_support_for_detail(detail) for detail in evidence_details]


def claim_notes(status: dict[str, str], source_support: list[dict[str, Any]]) -> list[str]:
    notes: list[str] = []
    if status["claim_status"] == "needs_confirmation":
        notes.append("claim remains open until HITL confirmation is recorded")
    if status["evidence_status"] == "missing":
        notes.append("no matching project source support found")
    if any(support.get("source_tier") == "T3_REFERENCE_METHODOLOGY" for support in source_support):
        notes.append("reference support is methodology-only")
    if any(support.get("source_tier") == "T4_SAMPLE_STYLE_ONLY" for support in source_support):
        notes.append("sample support is style-only")
    return notes


def claim_matrix_summary(claims: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "total_claims": len(claims),
        "hitl_confirmed_claims": sum(1 for claim in claims if claim["claim_status"] == "hitl_confirmed"),
        "supported_claims": sum(1 for claim in claims if claim["claim_status"] == "supported"),
        "needs_confirmation_claims": sum(1 for claim in claims if claim["claim_status"] == "needs_confirmation"),
        "weak_claims": sum(1 for claim in claims if claim["claim_status"] == "weak"),
        "unsupported_claims": sum(1 for claim in claims if claim["claim_status"] == "unsupported"),
        "pending_human_confirmations": sum(
            1 for claim in claims if claim["human_confirmation_status"] == "pending"
        ),
    }


def build_provenance_verify_facts(
    *,
    provenance_index: Mapping[str, Any] | None,
    claim_support_matrix: Mapping[str, Any] | None,
    final_report_text: str | None = None,
    delivery_summary_text: str | None = None,
    external_profile_expected: bool = False,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    facts: dict[str, dict[str, Any]] = {}
    items: list[dict[str, Any]] = []
    provenance = dict(provenance_index or {})
    matrix = dict(claim_support_matrix or {})

    sources = list(provenance.get("sources", []))
    claims = list(matrix.get("claims", []))
    pending_claims = [claim for claim in claims if claim.get("human_confirmation_status") == "pending"]

    facts["provenance_index_exists"] = fact(
        bool(provenance_index),
        "provenance_index.json exists.",
        "knowledge/provenance_index.json is missing.",
        ["knowledge/provenance_index.json"],
    )
    facts["source_tier_policy_valid"] = fact(
        valid_source_tier_policy(provenance),
        "Source tier policy is present and valid.",
        "Source tier policy is missing required N4 tiers or contains invalid source_tier values.",
        ["knowledge/provenance_index.json"],
    )
    sample_failures = [
        source for source in sources
        if source.get("role") in {"sample", "expected_output_shape"}
        and (source.get("source_tier") != "T4_SAMPLE_STYLE_ONLY" or source.get("can_support_project_fact"))
    ]
    sample_support_failures = [
        support
        for claim in claims
        for support in claim.get("source_support", [])
        if support.get("source_tier") == "T4_SAMPLE_STYLE_ONLY" and support.get("support_type") == "project_fact"
    ]
    facts["sample_tier_is_style_only"] = fact(
        not sample_failures and not sample_support_failures,
        "Sample and expected-output-shape entries remain style-only.",
        "Sample or expected-output-shape support is being treated as project fact support.",
        ["knowledge/provenance_index.json", "plans/claim_support_matrix.json"],
    )
    reference_failures = [
        source for source in sources
        if source.get("role") == "reference"
        and (source.get("source_tier") != "T3_REFERENCE_METHODOLOGY" or source.get("can_support_project_fact"))
    ]
    reference_support_failures = [
        support
        for claim in claims
        for support in claim.get("source_support", [])
        if support.get("source_tier") == "T3_REFERENCE_METHODOLOGY" and support.get("support_type") == "project_fact"
    ]
    facts["reference_tier_is_methodology_only"] = fact(
        not reference_failures and not reference_support_failures,
        "Reference entries remain methodology-only.",
        "Reference support is being treated as project fact support.",
        ["knowledge/provenance_index.json", "plans/claim_support_matrix.json"],
    )

    critical_failures = critical_claim_failures(claims)
    facts["critical_claim_source_tier_sufficient"] = fact(
        not critical_failures,
        "Critical claims marked supported have sufficient T0/T1 support.",
        "; ".join(critical_failures[:3]) or "Critical claim support is insufficient.",
        ["plans/claim_support_matrix.json"],
    )
    hidden_confirmation_failures = hidden_required_confirmation_failures(claims)
    facts["required_human_confirmation_not_hidden"] = fact(
        not hidden_confirmation_failures,
        "Required human confirmations remain pending or HITL-confirmed.",
        "; ".join(hidden_confirmation_failures[:3]) or "Required human confirmation is hidden.",
        ["plans/claim_support_matrix.json"],
    )
    facts["final_report_has_provenance_summary"] = text_fact_any(
        final_report_text,
        ["## 溯源摘要", "## Provenance Summary"],
        "Final report contains provenance summary.",
        "Final report is missing provenance summary.",
        ["final/final_report.md"],
    )
    delivery_has_open_confirmations = not pending_claims or (
        delivery_summary_text is not None
        and contains_any_literal(delivery_summary_text, ["## 开放确认项", "## Open Confirmations"])
    )
    if delivery_summary_text is None:
        facts["final_delivery_has_open_confirmations"] = {
            "status": "skipped",
            "details": "Phase 7 delivery summary is not available yet.",
            "related_artifacts": ["final/delivery_summary.md"],
            "review_item_ids": [],
        }
    else:
        facts["final_delivery_has_open_confirmations"] = fact(
            delivery_has_open_confirmations,
            "Delivery summary exposes open confirmations when pending claims exist.",
            "Delivery summary hides pending critical-claim confirmations.",
            ["final/delivery_summary.md", "plans/claim_support_matrix.json"],
        )
    profile_recorded = (not external_profile_expected) or bool(
        provenance.get("profile_id")
        and provenance.get("profile_version")
        and matrix.get("profile_id")
        and matrix.get("profile_version")
    )
    facts["profile_version_recorded_when_available"] = fact(
        profile_recorded,
        "Profile id/version are recorded when applicable.",
        "External profile metadata is missing from provenance artifacts.",
        ["knowledge/provenance_index.json", "plans/claim_support_matrix.json"],
    )

    for check_name in [
        "sample_tier_is_style_only",
        "reference_tier_is_methodology_only",
        "critical_claim_source_tier_sufficient",
        "required_human_confirmation_not_hidden",
        "final_report_has_provenance_summary",
        "final_delivery_has_open_confirmations",
        "profile_version_recorded_when_available",
    ]:
        if facts[check_name]["status"] == "failed":
            items.append(
                {
                    "severity": "P0",
                    "category": "provenance_policy_violation",
                    "section_id": "",
                    "task_id": "",
                    "artifact": facts[check_name]["related_artifacts"][0],
                    "description": facts[check_name]["details"],
                    "evidence_ids": [],
                    "suggested_fix": "Repair provenance source tier, claim support, or final visibility before final use.",
                    "status": "open",
                    "blocks_final": True,
                }
            )

    return facts, items


def valid_source_tier_policy(provenance: Mapping[str, Any]) -> bool:
    policy = provenance.get("source_tier_policy")
    if not isinstance(policy, Mapping) or not VALID_SOURCE_TIERS <= set(policy):
        return False
    for source in provenance.get("sources", []):
        if source.get("source_tier") not in VALID_SOURCE_TIERS:
            return False
    return True


def critical_claim_failures(claims: list[Mapping[str, Any]]) -> list[str]:
    failures: list[str] = []
    for claim in claims:
        status = claim.get("claim_status")
        support = list(claim.get("source_support", []))
        if status == "supported":
            has_allowed_support = any(
                item.get("source_tier") == "T1_PROJECT_SOURCE"
                and item.get("support_type") == "project_fact"
                for item in support
            )
            if not has_allowed_support:
                failures.append(f"{claim.get('claim_category')}: supported without T1 project_fact support")
            if any(
                item.get("source_tier") in {"T3_REFERENCE_METHODOLOGY", "T4_SAMPLE_STYLE_ONLY", "T5_AI_INFERENCE"}
                and item.get("support_type") == "project_fact"
                for item in support
            ):
                failures.append(f"{claim.get('claim_category')}: non-project tier marked project_fact")
        if status == "hitl_confirmed" and not any(item.get("source_tier") == "T0_HITL" for item in support):
            failures.append(f"{claim.get('claim_category')}: hitl_confirmed without T0 support")
    return failures


def hidden_required_confirmation_failures(claims: list[Mapping[str, Any]]) -> list[str]:
    failures: list[str] = []
    for claim in claims:
        if not claim.get("required_human_confirmation"):
            continue
        has_hitl = any(support.get("source_tier") == "T0_HITL" for support in claim.get("source_support", []))
        if has_hitl:
            continue
        if claim.get("claim_status") != "needs_confirmation" or claim.get("human_confirmation_status") != "pending":
            failures.append(f"{claim.get('claim_category')}: required HITL is not exposed as pending")
    return failures


def fact(
    condition: bool,
    pass_details: str,
    fail_details: str,
    artifacts: list[str],
    fail_status: str = "failed",
) -> dict[str, Any]:
    return {
        "status": "passed" if condition else fail_status,
        "details": pass_details if condition else fail_details,
        "related_artifacts": artifacts,
        "review_item_ids": [],
    }


def text_fact(
    text: str | None,
    required_text: str,
    pass_details: str,
    fail_details: str,
    artifacts: list[str],
) -> dict[str, Any]:
    if text is None:
        return {
            "status": "skipped",
            "details": "Phase 7 final artifact is not available yet.",
            "related_artifacts": artifacts,
            "review_item_ids": [],
        }
    return fact(required_text in text, pass_details, fail_details, artifacts)


def text_fact_any(
    text: str | None,
    required_texts: list[str],
    pass_details: str,
    fail_details: str,
    artifacts: list[str],
) -> dict[str, Any]:
    if text is None:
        return {
            "status": "skipped",
            "details": "Phase 7 final artifact is not available yet.",
            "related_artifacts": artifacts,
            "review_item_ids": [],
        }
    return fact(contains_any_literal(text, required_texts), pass_details, fail_details, artifacts)


def contains_any_literal(text: str, literals: list[str]) -> bool:
    return any(literal in text for literal in literals)


def load_hitl_sources(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    sources: list[dict[str, Any]] = []
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeDecodeError):
        return []
    for index, line in enumerate(lines, start=1):
        try:
            loaded = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(loaded, dict):
            continue
        decision_id = str(loaded.get("decision_id") or f"HITL-{index:03d}")
        sources.append(
            {
                "source_id": decision_id,
                "source_tier": "T0_HITL",
                "support_type": "hitl_confirmation",
                "support_strength": "strong",
                "decision": str(loaded.get("decision", "")),
                "claim_category": str(loaded.get("claim_category") or loaded.get("stage") or ""),
                "comment": str(loaded.get("comment", "")),
            }
        )
    return sources


def hitl_for_claim(claim_category: str, hitl_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claim_terms = meaningful_terms(claim_category)
    matched: list[dict[str, Any]] = []
    for source in hitl_sources:
        haystack = " ".join(
            [source.get("claim_category", ""), source.get("decision", ""), source.get("comment", "")]
        ).lower()
        if not claim_terms or any(term in haystack for term in claim_terms):
            matched.append(source)
    return matched


def meaningful_terms(text: str) -> list[str]:
    terms = [term for term in re.findall(r"[a-z][a-z0-9_-]{2,}", text.lower()) if term not in STOP_TERMS]
    return dedupe(terms)


def normalize_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def dedupe_support(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = (
            str(item.get("source_id", "")),
            str(item.get("file_id", "")),
            str(item.get("evidence_id", "")),
            str(item.get("support_type", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _value(item: Any, key: str) -> Any:
    if isinstance(item, Mapping):
        return item.get(key)
    return getattr(item, key, None)


STOP_TERMS = {
    "and",
    "the",
    "for",
    "with",
    "final",
    "claim",
    "claims",
    "status",
    "conclusion",
    "decision",
    "recommendation",
    "acceptance",
}
