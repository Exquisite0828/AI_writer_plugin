from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from ai_writing_plugin.document_types.profile_loader import DocumentProfileValidationError, load_document_profile_file
from ai_writing_plugin.trace import write_jsonl

from .patch import write_candidate_profile_package
from .report import build_profile_promotion_report, write_profile_promotion_report
from .schema import CorrectionValidationError, normalize_correction_event


class CorrectionHarvestError(ValueError):
    """Raised when correction harvesting cannot complete."""


def harvest_corrections(run_dir: Path, corrections_path: Path, profile_path: Path) -> dict[str, Any]:
    run_dir = Path(run_dir)
    corrections_path = Path(corrections_path)
    profile_path = Path(profile_path)
    try:
        loaded_profile = load_document_profile_file(profile_path, profile_path=str(profile_path))
    except DocumentProfileValidationError as exc:
        raise CorrectionHarvestError(f"profile validation failed: {'; '.join(exc.errors)}") from exc

    raw_events = load_correction_inputs(corrections_path)
    events: list[dict[str, Any]] = []
    try:
        for raw_event in raw_events:
            event = normalize_correction_event(raw_event)
            if event["profile_id"] != loaded_profile.profile.profile_id:
                raise CorrectionValidationError("profile_id does not match target profile")
            if event["profile_version"] != loaded_profile.profile.profile_version:
                raise CorrectionValidationError("profile_version does not match target profile")
            events.append(event)
    except CorrectionValidationError as exc:
        raise CorrectionHarvestError(str(exc)) from exc

    trace_dir = run_dir / "trace"
    learning_dir = run_dir / "learning"
    trace_dir.mkdir(parents=True, exist_ok=True)
    learning_dir.mkdir(parents=True, exist_ok=True)
    correction_events_path = trace_dir / "correction_events.jsonl"
    write_jsonl(correction_events_path, events)

    package_paths = write_candidate_profile_package(run_dir=run_dir, events=events, profile_path=profile_path)
    initial_report = build_profile_promotion_report(
        status="blocked_pending_eval_or_approval",
        promoted=False,
        candidate_patch_path=package_paths["candidate_patch_path"],
        target_profile_path=profile_path,
        reasons=["Promotion requires explicit human approval and passing N6 eval report."],
    )
    write_profile_promotion_report(initial_report, learning_dir)
    return {
        "run_dir": run_dir,
        "correction_events_path": correction_events_path,
        "candidate_patch_path": package_paths["candidate_patch_path"],
        "candidate_eval_case_path": package_paths["candidate_eval_case_path"],
        "events": events,
    }


def load_correction_inputs(corrections_path: Path) -> list[dict[str, Any]]:
    if not corrections_path.exists():
        raise CorrectionHarvestError(f"corrections file not found: {corrections_path}")
    try:
        if corrections_path.suffix.lower() == ".jsonl":
            loaded = [json.loads(line) for line in corrections_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        elif corrections_path.suffix.lower() == ".json":
            loaded = json.loads(corrections_path.read_text(encoding="utf-8"))
        else:
            loaded = yaml.safe_load(corrections_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, yaml.YAMLError, UnicodeDecodeError) as exc:
        raise CorrectionHarvestError(f"corrections parse failure: {corrections_path}: {exc}") from exc

    if isinstance(loaded, dict):
        for key in ["corrections", "events"]:
            if key in loaded:
                nested = loaded[key]
                if not isinstance(nested, list):
                    raise CorrectionHarvestError(f"{key} must be a list in corrections file: {corrections_path}")
                return require_event_mappings(nested, corrections_path)
        return [loaded]
    if isinstance(loaded, list):
        return require_event_mappings(loaded, corrections_path)
    raise CorrectionHarvestError(f"corrections root must be a mapping or list: {corrections_path}")


def require_event_mappings(events: list[Any], corrections_path: Path) -> list[dict[str, Any]]:
    if not events:
        raise CorrectionHarvestError(f"corrections file must contain at least one event: {corrections_path}")
    if not all(isinstance(event, dict) for event in events):
        raise CorrectionHarvestError(f"all correction events must be mappings: {corrections_path}")
    return [dict(event) for event in events]

