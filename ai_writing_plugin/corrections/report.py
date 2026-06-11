from __future__ import annotations

import json
from pathlib import Path
from typing import Any


NON_APPROVAL_NOTICE = (
    "Profile promotion only means an external document profile patch passed deterministic engineering gates. "
    "It is not professional approval, not compliance approval, not risk acceptance, and not final report approval."
)


def write_profile_promotion_report(report: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "profile_promotion_report.json"
    md_path = output_dir / "profile_promotion_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_profile_promotion_report(report), encoding="utf-8")
    return json_path, md_path


def build_profile_promotion_report(
    *,
    status: str,
    promoted: bool,
    candidate_patch_path: Path | None = None,
    candidate_patch_id: str = "",
    target_profile_path: Path | None = None,
    eval_report: dict[str, Any] | None = None,
    eval_report_path: Path | None = None,
    eval_report_sha256: str = "",
    approval_path: Path | None = None,
    base_profile: dict[str, Any] | None = None,
    new_profile: dict[str, Any] | None = None,
    rollback: dict[str, Any] | None = None,
    reasons: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    return {
        "schema_version": "profile_promotion_report.v1",
        "phase": "N7",
        "status": status,
        "promoted": promoted,
        "dry_run": dry_run,
        "candidate_patch": {
            "path": str(candidate_patch_path) if candidate_patch_path else "",
            "patch_id": candidate_patch_id,
        },
        "target_profile": str(target_profile_path) if target_profile_path else "",
        "eval_gate": {
            "path": str(eval_report_path) if eval_report_path else "",
            "sha256": eval_report_sha256,
            "overall_status": (eval_report or {}).get("overall_status", ""),
            "expectation_mismatch_count": (eval_report or {}).get("expectation_mismatch_count", ""),
        },
        "approval_gate": {
            "path": str(approval_path) if approval_path else "",
            "required": True,
        },
        "base_profile": base_profile or {},
        "new_profile": new_profile or {},
        "rollback": rollback or {"required": True, "prepared": False},
        "reasons": reasons or [],
        "non_approval_notice": NON_APPROVAL_NOTICE,
    }


def render_profile_promotion_report(report: dict[str, Any]) -> str:
    lines = [
        "# Profile Promotion Report",
        "",
        f"- Phase: {report['phase']}",
        f"- Status: {report['status']}",
        f"- Promoted: {str(report['promoted']).lower()}",
        f"- Dry run: {str(report['dry_run']).lower()}",
        f"- Candidate patch: {report['candidate_patch']['path']}",
        f"- Target profile: {report['target_profile']}",
        "",
        "## Gate Results",
        "",
        f"- Eval status: {report['eval_gate']['overall_status']}",
        f"- Eval report sha256: {report['eval_gate']['sha256']}",
        f"- Approval required: {str(report['approval_gate']['required']).lower()}",
        f"- Approval file: {report['approval_gate']['path']}",
        "",
        "## Reasons",
        "",
    ]
    reasons = report.get("reasons") or []
    if reasons:
        lines.extend(f"- {reason}" for reason in reasons)
    else:
        lines.append("- No blockers recorded.")
    lines.extend(
        [
            "",
            "## Rollback",
            "",
            f"- Prepared: {str(report['rollback'].get('prepared', False)).lower()}",
            f"- Metadata path: {report['rollback'].get('metadata_path', '')}",
            "",
            "## Boundary",
            "",
            report["non_approval_notice"],
            "",
        ]
    )
    return "\n".join(lines)

