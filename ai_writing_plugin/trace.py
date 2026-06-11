from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_HITL_GATES = [
    "task_goal_confirmation",
    "material_classification_confirmation",
    "outline_l1_confirmation",
    "evidence_confirmation",
    "final_delivery_confirmation",
    "candidate_update_confirmation",
]

HITL_STAGE_ALIASES = {
    "ingest_confirmation": "material_classification_confirmation",
    "outline_confirmation": "outline_l1_confirmation",
}

STAGE_ARTIFACTS = {
    "ingest": [
        "manifest.json",
        "task_brief.json",
        "inputs/input_inventory.json",
        "knowledge/source_index.json",
        "knowledge/knowledge_gaps.md",
    ],
    "outline": ["plans/template_structure.json", "plans/outline_l1.md"],
    "evidence": ["plans/research_questions.json", "plans/evidence_map.json", "plans/unresolved_questions.md"],
    "planning": ["plans/citation_plan.json", "plans/outline_final.md", "plans/section_tasks.json", "plans/writing_plan.md"],
    "draft": ["draft/full_draft.md"],
    "review": ["review/review_report.json", "review/final_review.md", "verify/verify_report.json", "verify/failures.md"],
    "finalize": ["revision_plan.json", "revised/full_draft.md", "final/final_report.md", "final/delivery_summary.md"],
    "learning": [
        "trace/session_trace.jsonl",
        "trace/hitl_decisions.jsonl",
        "learning/run_summary.md",
        "learning/reusable_patterns.md",
        "learning/candidate_profile_update.yaml",
        "learning/candidate_skill_patch.md",
        "learning/promotion_report.md",
    ],
}


def ensure_trace_dir(run_dir: Path) -> Path:
    trace_dir = run_dir / "trace"
    trace_dir.mkdir(parents=True, exist_ok=True)
    return trace_dir


def append_session_event(run_dir: Path, event: dict[str, Any]) -> None:
    record = normalize_session_event(run_dir, event)
    append_jsonl(ensure_trace_dir(run_dir) / "session_trace.jsonl", record)


def append_hitl_decision(run_dir: Path, decision: dict[str, Any]) -> dict[str, Any]:
    record = normalize_hitl_decision(run_dir, decision)
    append_jsonl(ensure_trace_dir(run_dir) / "hitl_decisions.jsonl", record)
    return record


def build_reconstructed_session_trace(run_dir: Path) -> list[dict[str, Any]]:
    run_id = load_run_id(run_dir)
    records: list[dict[str, Any]] = []
    for stage, artifact_paths in STAGE_ARTIFACTS.items():
        existing = [artifact_path for artifact_path in artifact_paths if (run_dir / artifact_path).exists()]
        for artifact_path in existing:
            records.append(
                {
                    "timestamp": utc_timestamp(),
                    "run_id": run_id,
                    "stage": stage,
                    "event": "artifact_created",
                    "artifact": artifact_path,
                    "status": "completed",
                    "source": "reconstructed_from_artifacts",
                }
            )
        records.append(
            {
                "timestamp": utc_timestamp(),
                "run_id": run_id,
                "stage": stage,
                "event": "phase_completed",
                "artifact": "",
                "status": "completed",
                "source": "reconstructed_from_artifacts",
            }
        )
    return records


def build_default_hitl_gates(run_dir: Path) -> list[dict[str, Any]]:
    run_id = load_run_id(run_dir)
    return [
        {
            "timestamp": utc_timestamp(),
            "run_id": run_id,
            "stage": stage,
            "decision": "not_collected_in_noninteractive_run",
            "user_comment": "",
            "affected_sections": [],
            "next_action": "requires_user_confirmation",
            "requires_user_confirmation": True,
            "status": "pending",
        }
        for stage in DEFAULT_HITL_GATES
    ]


def load_existing_hitl_decisions(run_dir: Path) -> list[dict[str, Any]]:
    path = ensure_trace_dir(run_dir) / "hitl_decisions.jsonl"
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            loaded = json.loads(line)
            if isinstance(loaded, dict):
                records.append(loaded)
    return records


def ensure_default_hitl_gates(run_dir: Path) -> None:
    existing = load_existing_hitl_decisions(run_dir)
    existing_stages = {canonical_hitl_stage(str(record.get("stage", ""))) for record in existing}
    for record in build_default_hitl_gates(run_dir):
        if record["stage"] not in existing_stages:
            append_jsonl(ensure_trace_dir(run_dir) / "hitl_decisions.jsonl", record)
            existing_stages.add(record["stage"])


def write_session_trace(run_dir: Path, records: list[dict[str, Any]]) -> None:
    write_jsonl(ensure_trace_dir(run_dir) / "session_trace.jsonl", records)


def normalize_session_event(run_dir: Path, event: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(event)
    normalized.setdefault("timestamp", utc_timestamp())
    normalized.setdefault("run_id", load_run_id(run_dir))
    normalized.setdefault("stage", "unknown")
    normalized.setdefault("event", "artifact_created")
    normalized.setdefault("artifact", "")
    normalized.setdefault("status", "completed")
    normalized.setdefault("source", "write_run")
    return normalized


def normalize_hitl_decision(run_dir: Path, decision: dict[str, Any]) -> dict[str, Any]:
    affected_sections = decision.get("affected_sections", [])
    if isinstance(affected_sections, str):
        affected_sections = [section.strip() for section in affected_sections.split(",") if section.strip()]
    stage = canonical_hitl_stage(str(decision.get("stage", "")))
    normalized = {
        "timestamp": decision.get("timestamp", utc_timestamp()),
        "run_id": decision.get("run_id", load_run_id(run_dir)),
        "stage": stage,
        "decision": decision.get("decision", "pending_user_confirmation"),
        "user_comment": decision.get("user_comment", decision.get("comment", "")),
        "affected_sections": affected_sections,
        "next_action": decision.get("next_action", "requires_user_confirmation"),
        "requires_user_confirmation": bool(decision.get("requires_user_confirmation", True)),
        "status": decision.get("status", "recorded"),
    }
    return normalized


def canonical_hitl_stage(stage: str) -> str:
    return HITL_STAGE_ALIASES.get(stage, stage)


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(record, ensure_ascii=False, sort_keys=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{encoded}\n")


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False, sort_keys=True) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_run_id(run_dir: Path) -> str:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return run_dir.name
    loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
    return str(loaded.get("run_id", run_dir.name))


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
