import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_until_draft_done(tmp_path: Path) -> Path:
    from ai_writing_plugin.run_manager import draft_run, evidence_run, ingest_run, outline_run, plan_run

    run_dir = ingest_run(task_file=FIXTURE_TASK, runs_dir=tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    plan_run(run_dir)
    draft_run(run_dir)
    return run_dir


def review_unit_ids(run_dir: Path, stage: str = "draft") -> list[str]:
    units = read_json(run_dir / "stage_reviews" / stage / "review_units.json")
    return [unit["unit_id"] for unit in units["units"]]


def valid_issues_payload(run_id: str, stage: str, unit_ids: list[str]) -> dict:
    issue_unit_id = unit_ids[0]
    return {
        "schema_version": 1,
        "kind": "stage_review_issues",
        "run_id": run_id,
        "stage": stage,
        "reviewer": "claude_code",
        "status": "issues_found",
        "not_professional_approval": True,
        "reviewed_unit_ids": unit_ids,
        "unchecked_unit_ids": [],
        "issues": [
            {
                "issue_id": "SRI-001",
                "unit_id": issue_unit_id,
                "severity": "P2",
                "category": "artifact_quality",
                "title": "Draft has repeated wording",
                "description": "The draft is readable, but one paragraph repeats the same limitation twice.",
                "related_artifacts": ["draft/full_draft.md"],
                "related_sections": ["SEC-001"],
                "requires_user_review": False,
                "requires_hitl": False,
                "safe_auto_fix_eligible": False,
                "recommendation": "Ask the user whether the duplicate wording should be reduced in a later manual revision.",
                "proposed_action": "Ask the user whether the duplicate wording should be reduced in a later manual revision.",
                "forbidden_auto_fix_reason": "",
            }
        ],
    }


def prepare_validated_stage_review(tmp_path: Path, stage: str = "draft") -> tuple[Path, str]:
    from ai_writing_plugin.stage_review import prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage=stage)
    unit_ids = review_unit_ids(run_dir, stage)
    write_json(run_dir / "stage_reviews" / stage / "issues.json", valid_issues_payload(run_id, stage, unit_ids))
    validate_stage_review(run_dir=run_dir, stage=stage)
    return run_dir, run_id


def test_prepare_stage_review_package_for_draft_is_advisory_and_does_not_mutate_artifacts(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import prepare_stage_review

    run_dir = run_until_draft_done(tmp_path)
    manifest_before = read_json(run_dir / "manifest.json")
    run_state_before = read_json(run_dir / "run_state.json")
    draft_path = run_dir / "draft" / "full_draft.md"
    draft_hash_before = sha256(draft_path)

    result = prepare_stage_review(run_dir=run_dir, stage="draft")

    review_dir = run_dir / "stage_reviews" / "draft"
    context = read_json(review_dir / "review_context.json")
    prompt = (review_dir / "review_prompt.md").read_text(encoding="utf-8").lower()
    schema = read_json(review_dir / "issues_schema.json")
    review_units = read_json(review_dir / "review_units.json")
    manifest_after = read_json(run_dir / "manifest.json")
    run_state_after = read_json(run_dir / "run_state.json")

    assert result["status"] == "prepared_for_claude_review"
    assert result["artifacts"] == [
        "stage_reviews/draft/review_context.json",
        "stage_reviews/draft/review_prompt.md",
        "stage_reviews/draft/issues_schema.json",
        "stage_reviews/draft/review_units.json",
    ]
    assert context["kind"] == "stage_review_context"
    assert context["not_professional_approval"] is True
    assert context["stage"] == "draft"
    assert context["phase"] == "phase_5"
    assert context["review_units_path"] == "stage_reviews/draft/review_units.json"
    assert context["review_unit_count"] == len(review_units["units"])
    assert context["review_unit_policy"] == {
        "coverage_required": True,
        "partial_review_allowed": False,
        "unknown_unit_id_allowed": False,
    }
    assert context["run"]["manifest_path"] == "manifest.json"
    assert context["run"]["task_brief_path"] == "task_brief.json"
    assert context["run"]["run_state_path"] == "run_state.json"
    assert context["stage_outputs"]
    assert context["stage_outputs"][0]["path"] == "draft/full_draft.md"
    assert context["stage_outputs"][0]["sha256"] == draft_hash_before
    assert len(context["stage_outputs"][0]["excerpt"]) <= 4000
    assert all(not Path(item["path"]).is_absolute() for item in context["stage_outputs"])
    assert "do not modify artifacts" in prompt
    assert "sample is not fact source" in prompt
    assert "not professional approval" in prompt
    assert "review_units.json" in prompt
    assert "unit_id" in prompt
    assert "reviewed_unit_ids" in prompt
    assert "unchecked_unit_ids" in prompt
    assert schema["kind"] == "stage_review_issues_schema"
    assert schema["schema_version"] == 1
    assert "reviewed_unit_ids" in schema["required_top_level_fields"]
    assert "unchecked_unit_ids" in schema["required_top_level_fields"]
    assert "unit_id" in schema["required_issue_fields"]
    assert review_units["kind"] == "stage_review_units"
    assert review_units["schema_version"] == 1
    assert review_units["run_id"] == context["run_id"]
    assert review_units["stage"] == "draft"
    assert review_units["source_artifacts"] == ["draft/full_draft.md"]
    assert review_units["units"]
    unit_ids_before = [unit["unit_id"] for unit in review_units["units"]]
    assert all(unit["required"] is True for unit in review_units["units"])
    assert all(unit["status"] == "pending" for unit in review_units["units"])
    assert all(unit["artifact_path"] == "draft/full_draft.md" for unit in review_units["units"])
    assert all(unit["unit_id"] and unit["unit_type"] and unit["required_checks"] for unit in review_units["units"])
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids_after = [unit["unit_id"] for unit in read_json(review_dir / "review_units.json")["units"]]
    assert unit_ids_after == unit_ids_before

    assert manifest_after == manifest_before
    assert run_state_after["stages"] == run_state_before["stages"]
    assert all("stage_reviews/" not in artifact["path"] for artifact in manifest_after["artifacts"])
    assert not (run_dir / "trace" / "session_trace.jsonl").exists()
    assert sha256(draft_path) == draft_hash_before


def test_prepare_stage_review_unknown_stage_fails_without_creating_tsc_artifact(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review

    run_dir = run_until_draft_done(tmp_path)

    with pytest.raises(StageReviewError, match="Unknown stage"):
        prepare_stage_review(run_dir=run_dir, stage="tsc")

    assert not (run_dir / "stage_reviews" / "tsc").exists()


def test_validate_stage_review_accepts_valid_issues_and_writes_report(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids = review_unit_ids(run_dir)
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", valid_issues_payload(run_id, "draft", unit_ids))

    report = validate_stage_review(run_dir=run_dir, stage="draft")
    saved_report = read_json(run_dir / "stage_reviews" / "draft" / "validation_report.json")

    assert report["status"] == "valid"
    assert saved_report == report
    assert report["kind"] == "stage_review_validation_report"
    assert report["not_professional_approval"] is True
    assert report["issue_count"] == 1
    assert report["errors"] == []
    assert report["coverage_summary"] == {
        "required_unit_count": len(unit_ids),
        "reviewed_unit_count": len(unit_ids),
        "unchecked_unit_count": 0,
        "issue_unit_count": 1,
        "coverage_complete": True,
    }
    assert report["unit_validation"] == {
        "missing_reviewed_unit_ids": [],
        "unknown_reviewed_unit_ids": [],
        "unknown_unchecked_unit_ids": [],
        "unknown_issue_unit_ids": [],
        "overlapping_reviewed_and_unchecked_unit_ids": [],
    }
    assert "safe_auto_fix_eligible is advisory only in S1; no patch applied." in report["warnings"]


def test_validate_stage_review_rejects_professional_approval_wording(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    payload = valid_issues_payload(run_id, "draft", review_unit_ids(run_dir))
    payload["issues"][0]["description"] = "This draft is professionally approved and compliance approved."
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="approval"):
        validate_stage_review(run_dir=run_dir, stage="draft")

    report = read_json(run_dir / "stage_reviews" / "draft" / "validation_report.json")
    assert report["status"] == "invalid"
    assert report["errors"]


def test_validate_stage_review_rejects_missing_top_level_reviewer(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    payload = valid_issues_payload(run_id, "draft", review_unit_ids(run_dir))
    payload.pop("reviewer")
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="reviewer"):
        validate_stage_review(run_dir=run_dir, stage="draft")


def test_validate_stage_review_rejects_high_risk_auto_fix(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    payload = valid_issues_payload(run_id, "draft", review_unit_ids(run_dir))
    payload["issues"][0]["severity"] = "P1"
    payload["issues"][0]["category"] = "critical_claim"
    payload["issues"][0]["requires_user_review"] = True
    payload["issues"][0]["safe_auto_fix_eligible"] = True
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="safe_auto_fix_eligible"):
        validate_stage_review(run_dir=run_dir, stage="draft")


@pytest.mark.parametrize(
    "bad_text",
    [
        "The sample can be used as fact source for this project.",
        "The reference proves project fact and can close the pending claim.",
    ],
)
def test_validate_stage_review_rejects_sample_or_reference_fact_source_claims(tmp_path: Path, bad_text: str) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    payload = valid_issues_payload(run_id, "draft", review_unit_ids(run_dir))
    payload["issues"][0]["description"] = bad_text
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="fact source|project fact"):
        validate_stage_review(run_dir=run_dir, stage="draft")


def test_stage_review_cli_prepare_and_validate(tmp_path: Path) -> None:
    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]

    prepare_result = subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "prepare-stage-review", "--run", str(run_dir), "--stage", "draft"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert prepare_result.returncode == 0, prepare_result.stderr
    assert "Stage review package prepared" in prepare_result.stdout
    assert "not professional approval" in prepare_result.stdout

    unit_ids = review_unit_ids(run_dir)
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", valid_issues_payload(run_id, "draft", unit_ids))
    validate_result = subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "validate-stage-review", "--run", str(run_dir), "--stage", "draft"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert validate_result.returncode == 0, validate_result.stderr
    assert "Stage review issues validated" in validate_result.stdout
    assert "does not apply fixes" in validate_result.stdout


def test_stage_review_cli_invalid_issues_returns_nonzero(tmp_path: Path) -> None:
    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    from ai_writing_plugin.stage_review import prepare_stage_review

    prepare_stage_review(run_dir=run_dir, stage="draft")
    payload = valid_issues_payload(run_id, "draft", review_unit_ids(run_dir))
    payload["status"] = "professionally_approved"
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    result = subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "validate-stage-review", "--run", str(run_dir), "--stage", "draft"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Stage review issues invalid" in result.stderr


def test_validate_stage_review_rejects_missing_unit_coverage(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids = review_unit_ids(run_dir)
    payload = valid_issues_payload(run_id, "draft", unit_ids[:-1])
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="missing required review unit coverage"):
        validate_stage_review(run_dir=run_dir, stage="draft")

    report = read_json(run_dir / "stage_reviews" / "draft" / "validation_report.json")
    assert report["status"] == "invalid"
    assert report["coverage_summary"]["coverage_complete"] is False
    assert report["unit_validation"]["missing_reviewed_unit_ids"] == [unit_ids[-1]]


def test_validate_stage_review_rejects_unknown_reviewed_unit(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids = review_unit_ids(run_dir)
    payload = valid_issues_payload(run_id, "draft", unit_ids + ["unknown.unit"])
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="unknown reviewed unit"):
        validate_stage_review(run_dir=run_dir, stage="draft")


def test_validate_stage_review_rejects_unknown_issue_unit(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids = review_unit_ids(run_dir)
    payload = valid_issues_payload(run_id, "draft", unit_ids)
    payload["issues"][0]["unit_id"] = "unknown.unit"
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="unknown issue unit"):
        validate_stage_review(run_dir=run_dir, stage="draft")


def test_validate_stage_review_rejects_unchecked_units(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids = review_unit_ids(run_dir)
    payload = valid_issues_payload(run_id, "draft", unit_ids)
    payload["unchecked_unit_ids"] = [unit_ids[0]]
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="unchecked_unit_ids must be empty"):
        validate_stage_review(run_dir=run_dir, stage="draft")


def test_validate_stage_review_rejects_reviewed_and_unchecked_overlap(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, prepare_stage_review, validate_stage_review

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")
    unit_ids = review_unit_ids(run_dir)
    payload = valid_issues_payload(run_id, "draft", unit_ids)
    payload["unchecked_unit_ids"] = [unit_ids[0]]
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)

    with pytest.raises(StageReviewError, match="overlap"):
        validate_stage_review(run_dir=run_dir, stage="draft")


def test_record_stage_review_decision_writes_gate_only_decision_without_mutating_professional_artifacts(
    tmp_path: Path,
) -> None:
    from ai_writing_plugin.stage_review import record_stage_review_decision

    run_dir, run_id = prepare_validated_stage_review(tmp_path)
    manifest_before = read_json(run_dir / "manifest.json")
    run_state_before = read_json(run_dir / "run_state.json")
    draft_path = run_dir / "draft" / "full_draft.md"
    draft_hash_before = sha256(draft_path)
    issues_hash = sha256(run_dir / "stage_reviews" / "draft" / "issues.json")
    validation_hash = sha256(run_dir / "stage_reviews" / "draft" / "validation_report.json")

    decision_path = record_stage_review_decision(
        run_dir=run_dir,
        stage="draft",
        decision="accepted",
        notes="Reviewed after Claude-assisted stage review.",
    )

    decision = read_json(decision_path)
    manifest_after = read_json(run_dir / "manifest.json")
    run_state_after = read_json(run_dir / "run_state.json")

    assert decision_path == run_dir / "stage_reviews" / "draft" / "decision.json"
    assert decision == {
        "kind": "stage_review_decision",
        "schema_version": 1,
        "run_id": run_id,
        "stage": "draft",
        "decision": "accepted",
        "decision_scope": "stage_review_gate_only",
        "professional_approval": False,
        "allow_next_stage": True,
        "decided_by": "user",
        "decision_source": "cli",
        "notes": "Reviewed after Claude-assisted stage review.",
        "created_at": decision["created_at"],
        "validation_report_path": "stage_reviews/draft/validation_report.json",
        "issues_path": "stage_reviews/draft/issues.json",
        "validation_status_at_decision": "valid",
        "coverage_complete_at_decision": True,
        "validation_report_sha256": validation_hash,
        "issues_sha256": issues_hash,
    }
    assert decision["created_at"].endswith("Z")
    assert manifest_after == manifest_before
    assert run_state_after["stages"] == run_state_before["stages"]
    assert sha256(draft_path) == draft_hash_before
    assert all("stage_reviews/" not in artifact["path"] for artifact in manifest_after["artifacts"])


def test_record_stage_review_decision_rejects_missing_invalid_and_incomplete_validation(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import (
        StageReviewError,
        prepare_stage_review,
        record_stage_review_decision,
        validate_stage_review,
    )

    run_dir = run_until_draft_done(tmp_path)
    run_id = read_json(run_dir / "manifest.json")["run_id"]
    prepare_stage_review(run_dir=run_dir, stage="draft")

    with pytest.raises(StageReviewError, match="validation_report.json missing"):
        record_stage_review_decision(run_dir=run_dir, stage="draft", decision="accepted")

    payload = valid_issues_payload(run_id, "draft", review_unit_ids(run_dir))
    payload["status"] = "professionally_approved"
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", payload)
    with pytest.raises(StageReviewError):
        validate_stage_review(run_dir=run_dir, stage="draft")
    with pytest.raises(StageReviewError, match="validation_report status must be valid"):
        record_stage_review_decision(run_dir=run_dir, stage="draft", decision="accepted")

    unit_ids = review_unit_ids(run_dir)
    write_json(run_dir / "stage_reviews" / "draft" / "issues.json", valid_issues_payload(run_id, "draft", unit_ids))
    validate_stage_review(run_dir=run_dir, stage="draft")
    report_path = run_dir / "stage_reviews" / "draft" / "validation_report.json"
    report = read_json(report_path)
    report["coverage_summary"]["coverage_complete"] = False
    write_json(report_path, report)
    with pytest.raises(StageReviewError, match="coverage_complete must be true"):
        record_stage_review_decision(run_dir=run_dir, stage="draft", decision="accepted")


def test_record_stage_review_decision_requires_issues_json_and_skipped_notes(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, record_stage_review_decision

    run_dir, _run_id = prepare_validated_stage_review(tmp_path)

    with pytest.raises(StageReviewError, match="notes must be non-empty"):
        record_stage_review_decision(run_dir=run_dir, stage="draft", decision="skipped")

    (run_dir / "stage_reviews" / "draft" / "issues.json").unlink()
    with pytest.raises(StageReviewError, match="issues.json missing"):
        record_stage_review_decision(run_dir=run_dir, stage="draft", decision="accepted")


def test_check_stage_review_gate_passes_for_accepted_and_skipped_decisions(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import check_stage_review_gate, record_stage_review_decision

    accepted_run_dir, _run_id = prepare_validated_stage_review(tmp_path / "accepted")
    record_stage_review_decision(run_dir=accepted_run_dir, stage="draft", decision="accepted")
    accepted_result = check_stage_review_gate(run_dir=accepted_run_dir, stage="draft")
    assert accepted_result["status"] == "passed"
    assert accepted_result["decision"] == "accepted"
    assert accepted_result["professional_approval"] is False

    skipped_run_dir, _run_id = prepare_validated_stage_review(tmp_path / "skipped")
    record_stage_review_decision(
        run_dir=skipped_run_dir,
        stage="draft",
        decision="skipped",
        notes="User explicitly skipped this advisory gate.",
    )
    skipped_result = check_stage_review_gate(run_dir=skipped_run_dir, stage="draft")
    assert skipped_result["status"] == "passed"
    assert skipped_result["decision"] == "skipped"


@pytest.mark.parametrize("decision", ["needs_revision", "blocked"])
def test_check_stage_review_gate_fails_for_blocking_decisions(tmp_path: Path, decision: str) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, check_stage_review_gate, record_stage_review_decision

    run_dir, _run_id = prepare_validated_stage_review(tmp_path)
    record_stage_review_decision(run_dir=run_dir, stage="draft", decision=decision)

    with pytest.raises(StageReviewError, match=decision):
        check_stage_review_gate(run_dir=run_dir, stage="draft")


def test_check_stage_review_gate_fails_when_decision_missing(tmp_path: Path) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, check_stage_review_gate

    run_dir, _run_id = prepare_validated_stage_review(tmp_path)

    with pytest.raises(StageReviewError, match="decision.json missing"):
        check_stage_review_gate(run_dir=run_dir, stage="draft")


@pytest.mark.parametrize(
    ("mutation", "expected_message"),
    [
        ("validation_report", "validation_report_sha256 mismatch"),
        ("issues", "issues_sha256 mismatch"),
        ("professional_approval", "professional_approval must be false"),
    ],
)
def test_check_stage_review_gate_rejects_hash_mismatch_and_professional_approval(
    tmp_path: Path,
    mutation: str,
    expected_message: str,
) -> None:
    from ai_writing_plugin.stage_review import StageReviewError, check_stage_review_gate, record_stage_review_decision

    run_dir, _run_id = prepare_validated_stage_review(tmp_path)
    record_stage_review_decision(run_dir=run_dir, stage="draft", decision="accepted")

    if mutation == "validation_report":
        report_path = run_dir / "stage_reviews" / "draft" / "validation_report.json"
        report = read_json(report_path)
        report["warnings"].append("changed after decision")
        write_json(report_path, report)
    elif mutation == "issues":
        issues_path = run_dir / "stage_reviews" / "draft" / "issues.json"
        issues = read_json(issues_path)
        issues["issues"][0]["title"] = "Changed after decision"
        write_json(issues_path, issues)
    else:
        decision_path = run_dir / "stage_reviews" / "draft" / "decision.json"
        decision_doc = read_json(decision_path)
        decision_doc["professional_approval"] = True
        write_json(decision_path, decision_doc)

    with pytest.raises(StageReviewError, match=expected_message):
        check_stage_review_gate(run_dir=run_dir, stage="draft")


def test_stage_review_decision_cli_record_and_check_smoke(tmp_path: Path) -> None:
    run_dir, _run_id = prepare_validated_stage_review(tmp_path)

    record_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "record-stage-review-decision",
            "--run",
            str(run_dir),
            "--stage",
            "draft",
            "--decision",
            "accepted",
            "--notes",
            "Reviewed.",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert record_result.returncode == 0, record_result.stderr
    assert "Recorded stage review gate decision: accepted" in record_result.stdout
    assert "not professional approval" in record_result.stdout

    check_result = subprocess.run(
        [sys.executable, "-m", "ai_writing_plugin", "check-stage-review-gate", "--run", str(run_dir), "--stage", "draft"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert check_result.returncode == 0, check_result.stderr
    assert "Stage review gate check passed for draft" in check_result.stdout
    assert "does not indicate professional approval" in check_result.stdout


def test_stage_review_docs_describe_s1_runtime_assistance_boundary() -> None:
    contracts = (REPO_ROOT / "docs" / "CURRENT_ARTIFACT_CONTRACTS.md").read_text(encoding="utf-8")
    runbook = (REPO_ROOT / "docs" / "RUNBOOK.md").read_text(encoding="utf-8")
    command = (REPO_ROOT / "commands" / "write.md").read_text(encoding="utf-8")
    troubleshooting = (REPO_ROOT / "docs" / "TROUBLESHOOTING.md").read_text(encoding="utf-8")
    combined = f"{contracts}\n{runbook}\n{command}\n{troubleshooting}"

    for required in [
        "prepare-stage-review",
        "validate-stage-review",
        "record-stage-review-decision",
        "check-stage-review-gate",
        "stage_reviews/<stage>/review_context.json",
        "stage_reviews/<stage>/issues_schema.json",
        "stage_reviews/<stage>/review_units.json",
        "stage_reviews/<stage>/decision.json",
        "stage_reviews/<stage>/validation_report.json",
        "stage_review_gate_only",
        "reviewed_unit_ids",
        "unchecked_unit_ids",
        "coverage_complete",
        "not professional approval",
        "does not apply fixes",
        "does not indicate professional approval",
    ]:
        assert required in combined

    assert "stage_reviews/` 是可选 runtime assistance artifact directory" in contracts
    assert "`manifest.artifacts`" in contracts
    assert "不改变 `run_state.json` lifecycle" in runbook
