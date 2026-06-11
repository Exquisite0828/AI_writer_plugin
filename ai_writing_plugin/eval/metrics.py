from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


VALID_METRICS = {
    "material_classification",
    "source_tier_policy",
    "template_extraction",
    "evidence_mapping",
    "sample_misuse",
    "reference_misuse",
    "critical_claim_policy",
    "forbidden_final_claim",
    "final_status_policy",
    "candidate_update_inactive",
    "cross_document_leakage",
}

SOURCE_ROLE_TIERS = {
    "source": "T1_PROJECT_SOURCE",
    "template": "T2_TEMPLATE_CHECKLIST",
    "checklist": "T2_TEMPLATE_CHECKLIST",
    "reference": "T3_REFERENCE_METHODOLOGY",
    "sample": "T4_SAMPLE_STYLE_ONLY",
    "expected_output_shape": "T4_SAMPLE_STYLE_ONLY",
}

NON_FACT_ROLES = {"template", "checklist", "reference", "sample", "expected_output_shape"}
PROJECT_FACT_TIERS = {"T0_HITL", "T1_PROJECT_SOURCE"}
NON_FACT_TIERS = {"T2_TEMPLATE_CHECKLIST", "T3_REFERENCE_METHODOLOGY", "T4_SAMPLE_STYLE_ONLY", "T5_AI_INFERENCE"}
ALLOWED_FINAL_STATUSES = {"ready_for_human_review", "finalized_with_open_items", "blocked_pending_confirmation"}
DISALLOWED_STATUS_VALUES = {"approved", "validated", "compliant", "production_ready", "production ready"}
DEFAULT_FORBIDDEN_FINAL_CLAIMS = [
    "approved",
    "validated",
    "compliant",
    "risk accepted",
    "production ready",
    "risk-free",
    "no security risk exists",
    "performance target is guaranteed",
    "cost is final",
    "final ASIL is approved",
    "safety goal is approved",
]
GUARDRAIL_MARKERS = [
    "not approved",
    "not validated",
    "not compliant",
    "not a professional approval",
    "not professional approval",
    "not a compliance approval",
    "not compliance approval",
    "not production approval",
    "not production readiness approval",
    "does not indicate approval",
    "pending approval",
    "requires approval",
    "required before treating",
    "before treating",
    "unless explicitly approved",
    "approval-like claim is forbidden",
    "forbidden",
    "must not",
    "cannot",
]
DEFAULT_LEAKAGE_TERMS = {
    "technical_solution": ["ASIL", "S/E/C", "severity rating", "exposure rating", "controllability rating", "safety goal", "hazardous event", "HARA professional judgment"],
    "generic_document": ["ASIL", "S/E/C", "severity rating", "exposure rating", "controllability rating", "safety goal", "hazardous event"],
    "custom_technical_note": ["ASIL", "S/E/C", "severity rating", "exposure rating", "controllability rating", "safety goal", "hazardous event"],
    "test_report": ["ASIL", "S/E/C", "safety goal", "hazardous event", "final architecture decision"],
    "fsr": ["Technical Safety Concept final report", "Technical Safety Requirement table", "TSC approval statement", "technical safety mechanism completeness"],
}


@dataclass(frozen=True)
class MetricResult:
    metric_id: str
    status: str
    severity: str
    message: str
    checked_artifacts: list[str]
    findings: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class MetricEvaluation:
    actual_result: str
    metric_results: list[MetricResult]


class ArtifactReader:
    def __init__(self, root: Path):
        self.root = root

    def json(self, relative_path: str) -> tuple[Any | None, dict[str, Any] | None]:
        path = self.root / relative_path
        if not path.exists():
            return None, {"artifact": relative_path, "error": "missing artifact"}
        try:
            return json.loads(path.read_text(encoding="utf-8")), None
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            return None, {"artifact": relative_path, "error": f"parse failure: {exc}"}

    def yaml(self, relative_path: str) -> tuple[Any | None, dict[str, Any] | None]:
        path = self.root / relative_path
        if not path.exists():
            return None, {"artifact": relative_path, "error": "missing artifact"}
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")), None
        except (yaml.YAMLError, UnicodeDecodeError) as exc:
            return None, {"artifact": relative_path, "error": f"parse failure: {exc}"}

    def text(self, relative_path: str) -> str:
        path = self.root / relative_path
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ""

    def existing_texts(self, relative_paths: list[str]) -> list[tuple[str, str]]:
        return [(relative_path, self.text(relative_path)) for relative_path in relative_paths if (self.root / relative_path).exists()]


def evaluate_metrics(
    *,
    artifact_root: Path,
    metric_ids: list[str],
    document_type: str,
    expectations: dict[str, Any] | None = None,
) -> MetricEvaluation:
    expectations = expectations or {}
    reader = ArtifactReader(artifact_root)
    results: list[MetricResult] = []
    for metric_id in metric_ids:
        metric = METRIC_FUNCTIONS[metric_id]
        results.append(metric(reader, document_type, expectations))
    actual_result = "fail" if any(result.status == "fail" for result in results) else "pass"
    return MetricEvaluation(actual_result=actual_result, metric_results=results)


def metric_result(metric_id: str, checked: list[str], findings: list[dict[str, Any]], pass_message: str, fail_message: str, severity: str = "P0") -> MetricResult:
    return MetricResult(
        metric_id=metric_id,
        status="fail" if findings else "pass",
        severity=severity,
        message=fail_message if findings else pass_message,
        checked_artifacts=checked,
        findings=findings,
    )


def material_classification(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["inputs/input_inventory.json", "knowledge/source_index.json", "knowledge/provenance_index.json"]
    findings: list[dict[str, Any]] = []
    inventory, error = reader.json("inputs/input_inventory.json")
    if error:
        findings.append(error)
    else:
        for item in inventory.get("files", []):
            role = item.get("role")
            if role == "source" and not item.get("is_fact_source"):
                findings.append({"artifact": "inputs/input_inventory.json", "path": item.get("path"), "role": role, "error": "source not fact-capable"})
            if role in NON_FACT_ROLES and item.get("is_fact_source"):
                findings.append({"artifact": "inputs/input_inventory.json", "path": item.get("path"), "role": role, "error": "non-fact role marked fact source"})
            if item.get("parse_status") == "failed" and item.get("is_fact_source"):
                findings.append({"artifact": "inputs/input_inventory.json", "path": item.get("path"), "role": role, "error": "failed parse promoted to fact source"})

    source_index, source_error = reader.json("knowledge/source_index.json")
    if source_error:
        findings.append(source_error)
    else:
        for source in source_index.get("sources", []):
            role = source.get("source_role")
            if role == "sample" or source.get("source_tier") == "T4_SAMPLE_STYLE_ONLY":
                findings.append({"artifact": "knowledge/source_index.json", "source_id": source.get("source_id"), "role": role, "error": "sample present in source index"})
            if role == "reference" and source.get("is_fact_source"):
                findings.append({"artifact": "knowledge/source_index.json", "source_id": source.get("source_id"), "role": role, "error": "reference marked fact source"})

    provenance, provenance_error = reader.json("knowledge/provenance_index.json")
    if provenance_error:
        findings.append(provenance_error)
    else:
        for source in provenance.get("sources", []):
            role = source.get("role") or source.get("source_role")
            expected_tier = SOURCE_ROLE_TIERS.get(role)
            if expected_tier and source.get("source_tier") != expected_tier:
                findings.append({"artifact": "knowledge/provenance_index.json", "source_id": source.get("source_id"), "role": role, "source_tier": source.get("source_tier"), "expected_tier": expected_tier})
            if role in NON_FACT_ROLES and source.get("can_support_project_fact"):
                findings.append({"artifact": "knowledge/provenance_index.json", "source_id": source.get("source_id"), "role": role, "error": "non-fact role can support project fact"})

    return metric_result("material_classification", checked, findings, "Material roles and source tiers are consistent.", "Material classification policy violation found.")


def source_tier_policy(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["knowledge/provenance_index.json", "plans/claim_support_matrix.json", "plans/evidence_map.json", "plans/citation_plan.json"]
    findings = []
    provenance, provenance_error = reader.json("knowledge/provenance_index.json")
    if provenance_error and (reader.root / "knowledge" / "provenance_index.json").exists():
        findings.append(provenance_error)
    elif provenance:
        for source in provenance.get("sources", []):
            tier = source.get("source_tier")
            role = source.get("role") or source.get("source_role")
            if tier == "T4_SAMPLE_STYLE_ONLY" and (source.get("can_support_project_fact") or source.get("can_support_critical_claim")):
                findings.append({"artifact": "knowledge/provenance_index.json", "source_id": source.get("source_id"), "role": role, "source_tier": tier, "error": "T4 can support fact or critical claim"})
            if tier == "T3_REFERENCE_METHODOLOGY" and (source.get("can_support_project_fact") or source.get("can_support_critical_claim")):
                findings.append({"artifact": "knowledge/provenance_index.json", "source_id": source.get("source_id"), "role": role, "source_tier": tier, "error": "T3 can support project fact or critical claim"})
            if tier == "T5_AI_INFERENCE" and source.get("can_support_critical_claim"):
                findings.append({"artifact": "knowledge/provenance_index.json", "source_id": source.get("source_id"), "source_tier": tier, "error": "T5 can support critical claim"})

    matrix, matrix_error = reader.json("plans/claim_support_matrix.json")
    if matrix_error and (reader.root / "plans" / "claim_support_matrix.json").exists():
        findings.append(matrix_error)
    elif matrix:
        for claim in matrix.get("claims", []):
            support = claim.get("source_support", [])
            support_tiers = {item.get("source_tier") for item in support}
            if claim.get("claim_status") in {"supported", "hitl_confirmed"} and not (support_tiers & PROJECT_FACT_TIERS):
                findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_tiers": sorted(tier for tier in support_tiers if tier), "error": "claim supported without T0/T1"})
            if claim.get("human_confirmation_status") == "confirmed" and "T0_HITL" not in support_tiers:
                findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_tiers": sorted(tier for tier in support_tiers if tier), "error": "pending HITL treated as confirmed"})
            for item in support:
                tier = item.get("source_tier")
                support_type = item.get("support_type")
                if tier == "T4_SAMPLE_STYLE_ONLY" and support_type == "project_fact":
                    findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_tier": tier, "error": "T4 supports project fact"})
                if tier == "T3_REFERENCE_METHODOLOGY" and support_type == "project_fact":
                    findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_tier": tier, "error": "T3 supports project fact"})
                if tier == "T5_AI_INFERENCE" and claim.get("claim_status") in {"supported", "hitl_confirmed"}:
                    findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_tier": tier, "error": "T5 supports critical claim"})

    return metric_result("source_tier_policy", checked, findings, "Source tier policy is preserved.", "Source tier policy violation found.")


def template_extraction(reader: ArtifactReader, document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["plans/template_structure.json", "plans/outline_l1.md", "plans/outline_final.md", "plans/section_tasks.json"]
    findings = []
    template, template_error = reader.json("plans/template_structure.json")
    tasks, tasks_error = reader.json("plans/section_tasks.json")
    if template_error:
        findings.append(template_error)
    if tasks_error:
        findings.append(tasks_error)
    if template and template.get("fallback_used"):
        findings.append({"artifact": "plans/template_structure.json", "error": "template fallback used"})
    if template and tasks:
        section_titles = {section.get("title") for section in template.get("outline_sections", [])}
        task_titles = {task.get("section_title") for task in tasks.get("tasks", [])}
        missing_tasks = sorted(title for title in section_titles if title and title not in task_titles)
        for title in missing_tasks:
            findings.append({"artifact": "plans/section_tasks.json", "section_title": title, "error": "section task missing for template section"})
        if document_type not in {"hara", "fsr"}:
            for title in section_titles | task_titles:
                if contains_any(str(title), DEFAULT_LEAKAGE_TERMS["technical_solution"]):
                    findings.append({"artifact": "plans/template_structure.json", "section_title": title, "error": "HARA-specific section injected into non-HARA document"})

    return metric_result("template_extraction", checked, findings, "Template extraction artifacts are consistent.", "Template extraction issue found.", severity="P1")


def evidence_mapping(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["plans/research_questions.json", "plans/evidence_map.json", "plans/unresolved_questions.md", "plans/citation_plan.json", "plans/claim_support_matrix.json"]
    findings = []
    source_ids = known_source_ids(reader)
    evidence_map, evidence_error = reader.json("plans/evidence_map.json")
    citation_plan, citation_error = reader.json("plans/citation_plan.json")
    claim_matrix, matrix_error = reader.json("plans/claim_support_matrix.json")
    if evidence_error:
        findings.append(evidence_error)
    if citation_error:
        findings.append(citation_error)
    if matrix_error:
        findings.append(matrix_error)

    evidence_ids: set[str] = set()
    if evidence_map:
        for question in evidence_map.get("questions", []):
            for candidate in question.get("evidence_candidates", []):
                evidence_id = candidate.get("evidence_id")
                if evidence_id:
                    evidence_ids.add(evidence_id)
                source_id = candidate.get("source_id")
                if source_id and source_ids and source_id not in source_ids:
                    findings.append({"artifact": "plans/evidence_map.json", "evidence_id": evidence_id, "source_id": source_id, "error": "source id not traceable"})
                if candidate.get("source_tier") in {"T4_SAMPLE_STYLE_ONLY", "T3_REFERENCE_METHODOLOGY"} and candidate.get("provenance_support_type") == "project_fact":
                    findings.append({"artifact": "plans/evidence_map.json", "evidence_id": evidence_id, "source_tier": candidate.get("source_tier"), "error": "non-fact tier used as project fact evidence"})

    if citation_plan:
        for section in citation_plan.get("sections", []):
            for detail in section.get("evidence_details", []):
                evidence_id = detail.get("evidence_id")
                if evidence_ids and evidence_id not in evidence_ids:
                    findings.append({"artifact": "plans/citation_plan.json", "evidence_id": evidence_id, "error": "citation evidence id not found in evidence map"})
                if detail.get("source_tier") in {"T4_SAMPLE_STYLE_ONLY", "T3_REFERENCE_METHODOLOGY"} and detail.get("usage") == "fact_support":
                    findings.append({"artifact": "plans/citation_plan.json", "evidence_id": evidence_id, "source_tier": detail.get("source_tier"), "error": "non-fact tier used as fact support"})

    if claim_matrix:
        for claim in claim_matrix.get("claims", []):
            if claim.get("claim_status") == "supported" and not any(item.get("source_tier") in PROJECT_FACT_TIERS for item in claim.get("source_support", [])):
                findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "error": "supported claim lacks T0/T1 support"})

    return metric_result("evidence_mapping", checked, findings, "Evidence ids and support policy are traceable.", "Evidence mapping violation found.")


def sample_misuse(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["knowledge/source_index.json", "knowledge/provenance_index.json", "plans/evidence_map.json", "plans/citation_plan.json", "plans/claim_support_matrix.json", "plans/section_tasks.json", "draft/full_draft.md", "revised/full_draft.md", "final/final_report.md"]
    findings = []
    findings.extend(non_fact_tier_findings(reader, "sample_misuse", "T4_SAMPLE_STYLE_ONLY"))
    return metric_result("sample_misuse", checked, findings, "No sample/T4 source was used as factual evidence.", "Sample/T4 source used as factual support.")


def reference_misuse(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["knowledge/provenance_index.json", "plans/evidence_map.json", "plans/citation_plan.json", "plans/claim_support_matrix.json", "final/final_report.md"]
    findings = []
    findings.extend(non_fact_tier_findings(reader, "reference_misuse", "T3_REFERENCE_METHODOLOGY"))
    return metric_result("reference_misuse", checked, findings, "No reference/T3 source proved project facts or critical claims.", "Reference/T3 source used as project fact support.")


def critical_claim_policy(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["plans/claim_support_matrix.json", "final/delivery_summary.md", "final/final_report.md"]
    findings = []
    matrix, matrix_error = reader.json("plans/claim_support_matrix.json")
    if matrix_error:
        findings.append(matrix_error)
    elif matrix:
        pending_claims = []
        for claim in matrix.get("claims", []):
            support_tiers = {item.get("source_tier") for item in claim.get("source_support", [])}
            claim_status = claim.get("claim_status")
            human_status = claim.get("human_confirmation_status")
            if claim_status in {"supported", "hitl_confirmed"} and not (support_tiers & PROJECT_FACT_TIERS):
                findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_tiers": sorted(tier for tier in support_tiers if tier), "error": "critical claim finalized without T0/T1"})
            if claim.get("required_human_confirmation") and human_status == "confirmed" and "T0_HITL" not in support_tiers:
                findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "error": "human confirmation marked confirmed without T0"})
            if claim.get("required_human_confirmation") and human_status == "pending":
                pending_claims.append(claim.get("claim_category"))
        delivery_summary_text = reader.text("final/delivery_summary.md").lower()
        if pending_claims and not (
            "open confirmations" in delivery_summary_text or "开放确认项" in delivery_summary_text
        ):
            findings.append({"artifact": "final/delivery_summary.md", "claims": pending_claims, "error": "open confirmations omitted"})

    return metric_result("critical_claim_policy", checked, findings, "Critical claims remain supported or explicitly pending.", "Critical claim policy violation found.")


def forbidden_final_claim(reader: ArtifactReader, _document_type: str, expectations: dict[str, Any]) -> MetricResult:
    checked = ["final/final_report.md", "final/delivery_summary.md", "revised/full_draft.md", "review/final_review.md"]
    findings = []
    forbidden = [str(item) for item in expectations.get("forbidden_final_claims", [])] or DEFAULT_FORBIDDEN_FINAL_CLAIMS
    for artifact, text in reader.existing_texts(checked):
        for line_no, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if is_guardrail_line(lowered):
                continue
            for phrase in forbidden:
                if phrase.lower() in lowered:
                    findings.append({"artifact": artifact, "line": line_no, "term": phrase, "text": line.strip()})

    return metric_result("forbidden_final_claim", checked, findings, "No unguarded approval-like final claim was found.", "Forbidden final claim found.")


def final_status_policy(reader: ArtifactReader, _document_type: str, expectations: dict[str, Any]) -> MetricResult:
    checked = ["revision_plan.json", "final/final_report.md", "final/delivery_summary.md"]
    findings = []
    allowed = set(expectations.get("allowed_final_statuses") or ALLOWED_FINAL_STATUSES)
    statuses: list[tuple[str, str]] = []
    revision_plan, revision_error = reader.json("revision_plan.json")
    if revision_error and (reader.root / "revision_plan.json").exists():
        findings.append(revision_error)
    elif revision_plan:
        status = nested_get(revision_plan, ["summary", "status"])
        if status:
            statuses.append(("revision_plan.json", str(status)))

    for artifact in ["final/final_report.md", "final/delivery_summary.md"]:
        for line in reader.text(artifact).splitlines():
            status = extract_final_status_from_line(line)
            if status:
                statuses.append((artifact, status))

    if not statuses:
        findings.append({"artifact": "final/final_report.md", "error": "final status missing"})
    for artifact, status in statuses:
        normalized = normalize_status(status)
        if normalized in DISALLOWED_STATUS_VALUES or any(disallowed in normalized for disallowed in DISALLOWED_STATUS_VALUES):
            findings.append({"artifact": artifact, "status": status, "error": "approval-like final status"})
        elif normalized and normalized not in allowed:
            findings.append({"artifact": artifact, "status": status, "allowed": sorted(allowed), "error": "final status outside allowed set"})

    return metric_result("final_status_policy", checked, findings, "Final status stays within review/open-item states.", "Final status policy violation found.")


def candidate_update_inactive(reader: ArtifactReader, _document_type: str, _expectations: dict[str, Any]) -> MetricResult:
    checked = ["learning/candidate_profile_update.yaml", "learning/candidate_skill_patch.md", "learning/promotion_report.md"]
    findings = []
    for artifact in checked:
        path = reader.root / artifact
        if not path.exists():
            findings.append({"artifact": artifact, "error": "missing candidate update artifact"})
            continue
        text = reader.text(artifact).lower()
        if "status: active" in text or "active: true" in text or "auto_applied: true" in text or "auto-applied: true" in text:
            findings.append({"artifact": artifact, "error": "candidate update is active or auto-applied"})
        if "candidate activated: yes" in text or "stable skill overwritten: yes" in text or "auto applied: true" in text:
            findings.append({"artifact": artifact, "error": "promotion report indicates auto-application"})

    return metric_result("candidate_update_inactive", checked, findings, "Candidate updates remain proposed/inactive.", "Candidate update activation violation found.")


def cross_document_leakage(reader: ArtifactReader, document_type: str, expectations: dict[str, Any]) -> MetricResult:
    checked = [
        "plans/research_questions.json",
        "plans/evidence_map.json",
        "plans/citation_plan.json",
        "plans/section_tasks.json",
        "plans/writing_plan.md",
        "draft/full_draft.md",
        "review/final_review.md",
        "final/final_report.md",
        "final/delivery_summary.md",
    ]
    findings = []
    if document_type == "hara":
        return metric_result("cross_document_leakage", checked, findings, "HARA artifacts may contain required HARA terminology.", "Document-type leakage found.", severity="P1")
    terms = [str(item) for item in expectations.get("forbidden_terms", [])] or DEFAULT_LEAKAGE_TERMS.get(document_type, DEFAULT_LEAKAGE_TERMS["generic_document"])
    for artifact, text in reader.existing_texts(checked):
        for term in terms:
            if contains_term(text, term):
                findings.append({"artifact": artifact, "term": term})

    return metric_result("cross_document_leakage", checked, findings, "No forbidden document-type leakage was found.", "Forbidden document-type leakage found.", severity="P1")


def non_fact_tier_findings(reader: ArtifactReader, metric_id: str, tier: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    provenance, _ = reader.json("knowledge/provenance_index.json")
    if provenance:
        for source in provenance.get("sources", []):
            if source.get("source_tier") == tier and (source.get("can_support_project_fact") or source.get("can_support_critical_claim")):
                findings.append({"artifact": "knowledge/provenance_index.json", "source_id": source.get("source_id"), "source_tier": tier, "metric": metric_id, "error": "non-fact tier has project fact capability"})

    source_index, _ = reader.json("knowledge/source_index.json")
    if source_index:
        for source in source_index.get("sources", []):
            if source.get("source_tier") == tier and source.get("is_fact_source"):
                findings.append({"artifact": "knowledge/source_index.json", "source_id": source.get("source_id"), "source_tier": tier, "metric": metric_id, "error": "non-fact tier appears as fact source"})

    for artifact, item in iter_evidence_like_items(reader):
        item_tier = item.get("source_tier")
        if item_tier != tier:
            continue
        project_fact = item.get("support_type") == "project_fact" or item.get("provenance_support_type") == "project_fact" or item.get("usage") == "fact_support"
        critical = item.get("can_support_critical_claim") is True or item.get("claim_status") in {"supported", "hitl_confirmed"}
        if project_fact or critical:
            findings.append({"artifact": artifact, "source_id": item.get("source_id"), "source_tier": item_tier, "evidence_id": item.get("evidence_id"), "metric": metric_id, "error": "non-fact tier used as fact or critical support"})

    matrix, _ = reader.json("plans/claim_support_matrix.json")
    if matrix:
        for claim in matrix.get("claims", []):
            claim_has_project_fact_support = any(
                support.get("source_tier") in PROJECT_FACT_TIERS
                for support in claim.get("source_support", [])
            )
            for support in claim.get("source_support", []):
                non_fact_supports_project_fact = support.get("support_type") == "project_fact"
                non_fact_is_sole_supported_claim = (
                    claim.get("claim_status") in {"supported", "hitl_confirmed"}
                    and not claim_has_project_fact_support
                )
                if support.get("source_tier") == tier and (non_fact_supports_project_fact or non_fact_is_sole_supported_claim):
                    findings.append({"artifact": "plans/claim_support_matrix.json", "claim_category": claim.get("claim_category"), "source_id": support.get("source_id"), "source_tier": tier, "evidence_id": support.get("evidence_id"), "metric": metric_id})
    return findings


def iter_evidence_like_items(reader: ArtifactReader) -> list[tuple[str, dict[str, Any]]]:
    items: list[tuple[str, dict[str, Any]]] = []
    evidence_map, _ = reader.json("plans/evidence_map.json")
    if evidence_map:
        for question in evidence_map.get("questions", []):
            for candidate in question.get("evidence_candidates", []):
                items.append(("plans/evidence_map.json", candidate))
    citation_plan, _ = reader.json("plans/citation_plan.json")
    if citation_plan:
        for section in citation_plan.get("sections", []):
            for detail in section.get("evidence_details", []):
                items.append(("plans/citation_plan.json", detail))
    return items


def known_source_ids(reader: ArtifactReader) -> set[str]:
    source_ids: set[str] = set()
    source_index, _ = reader.json("knowledge/source_index.json")
    if source_index:
        source_ids.update(str(source.get("source_id")) for source in source_index.get("sources", []) if source.get("source_id"))
    provenance, _ = reader.json("knowledge/provenance_index.json")
    if provenance:
        source_ids.update(str(source.get("source_id")) for source in provenance.get("sources", []) if source.get("source_id"))
    return source_ids


def nested_get(data: dict[str, Any], keys: list[str]) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def normalize_status(value: str) -> str:
    return value.strip().strip(".").lower().replace("-", "_").replace(" ", "_")


def extract_final_status_from_line(line: str) -> str | None:
    stripped = line.strip()
    match = re.match(r"^status\s*:\s*([A-Za-z0-9_ -]+)$", stripped, flags=re.IGNORECASE)
    if match:
        return normalize_status(match.group(1))
    match = re.match(r"^[-*]\s*final status\s*:\s*([A-Za-z0-9_ -]+)$", stripped, flags=re.IGNORECASE)
    if match:
        return normalize_status(match.group(1))
    match = re.match(r"^final status\s*:\s*([A-Za-z0-9_ -]+)$", stripped, flags=re.IGNORECASE)
    if match:
        return normalize_status(match.group(1))
    return None


def contains_any(text: str, terms: list[str]) -> bool:
    return any(contains_term(text, term) for term in terms)


def contains_term(text: str, term: str) -> bool:
    if term.isupper() or "/" in term:
        return term in text
    return term.lower() in text.lower()


def is_guardrail_line(lowered_line: str) -> bool:
    return any(marker in lowered_line for marker in GUARDRAIL_MARKERS)


METRIC_FUNCTIONS: dict[str, Callable[[ArtifactReader, str, dict[str, Any]], MetricResult]] = {
    "material_classification": material_classification,
    "source_tier_policy": source_tier_policy,
    "template_extraction": template_extraction,
    "evidence_mapping": evidence_mapping,
    "sample_misuse": sample_misuse,
    "reference_misuse": reference_misuse,
    "critical_claim_policy": critical_claim_policy,
    "forbidden_final_claim": forbidden_final_claim,
    "final_status_policy": final_status_policy,
    "candidate_update_inactive": candidate_update_inactive,
    "cross_document_leakage": cross_document_leakage,
}
