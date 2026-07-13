import hashlib
import json
import os
from pathlib import Path

import pytest

import ai_writing_plugin.stage_review_issues as stage_review_issues
from ai_writing_plugin.stage_gate_results import build_stage_gate_result
from ai_writing_plugin.stage_review_issues import (
    StageReviewIssueError,
    build_issues_index,
    issue_detail_path,
    issues_index_path,
    summarize_issues_index,
    validate_issue_detail,
    validate_issues_index,
)


def write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path: str, digest: str) -> dict:
    return {"path": path, "sha256": digest}


def source_issue(
    issue_id: str,
    severity: str,
    *,
    title: str | None = None,
    category: str = "missing_evidence",
    detail: str = "Full review detail that must stay out of the index.",
) -> dict:
    return {
        "issue_id": issue_id,
        "severity": severity,
        "category": category,
        "title": title or f"{issue_id} short title",
        "summary": f"{issue_id} compact summary.",
        "detail": detail,
        "recommendation": "Revise the cited artifact using traceable evidence refs.",
        "rationale": "The review finding is grounded in metadata refs only.",
        "location_refs": [{"path": "artifacts/report.md", "section": "1"}],
    }


def public_source_issue(run_dir: Path, issue_id: str = "P1-001") -> dict:
    artifact_path = run_dir / "artifacts" / "report.md"
    write(artifact_path, "artifact body")
    return {
        "issue_id": issue_id,
        "severity": "P1",
        "category": "missing_evidence",
        "title": f"{issue_id} short title",
        "summary": f"{issue_id} compact summary.",
        "location_refs": [{"path": "artifacts/report.md", "section": "1"}],
        "artifact_refs": [
            ref("artifacts/report.md", sha256_file(artifact_path)),
        ],
        "recommendation": "Revise the artifact using traceable evidence refs.",
        "rationale": "The review finding is grounded in the referenced artifact.",
    }


def write_public_source(run_dir: Path, issues: list[dict]) -> Path:
    path = run_dir / "stage_reviews" / "ingest" / "issues.json"
    write(path, json.dumps({"issues": issues}, ensure_ascii=False))
    return path


def build_sample_index(run_dir: Path, issues: list[dict] | None = None) -> dict:
    write(run_dir / "artifacts" / "report.md", "artifact body")
    artifact_ref = ref("artifacts/report.md", sha256_file(run_dir / "artifacts" / "report.md"))
    issue_payloads = issues or [source_issue("P1-001", "P1")]
    for issue in issue_payloads:
        issue.setdefault("artifact_refs", [artifact_ref])
    return build_issues_index(run_dir, "ingest", issues=issue_payloads)


def test_build_issues_index_creates_index_and_issue_detail_files(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"

    payload = build_sample_index(
        run_dir,
        [
            source_issue("P1-001", "P1"),
            source_issue("P3-001", "P3", category="style"),
        ],
    )

    assert issues_index_path(run_dir, "ingest").is_file()
    assert issue_detail_path(run_dir, "ingest", "P1-001").is_file()
    assert issue_detail_path(run_dir, "ingest", "P3-001").is_file()
    assert payload["issue_count"] == 2
    assert payload["blocking_issues_count"] == 1
    assert validate_issues_index(payload, run_dir=run_dir) == payload


def test_issues_index_contains_only_short_fields(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_sample_index(
        run_dir,
        [source_issue("P0-001", "P0", detail="SECRET DETAIL MUST NOT ENTER INDEX")],
    )

    item = payload["issues"][0]
    assert set(item) == {"issue_id", "severity", "category", "short_title", "issue_ref"}
    assert "SECRET DETAIL MUST NOT ENTER INDEX" not in json.dumps(payload)
    assert "detail" not in item
    assert "body" not in item
    assert "```" not in json.dumps(payload)


def test_validate_issues_index_rejects_body_like_fields(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_sample_index(run_dir)
    payload["issues"][0]["body"] = "large issue body"

    with pytest.raises(StageReviewIssueError, match="body-like|unexpected"):
        validate_issues_index(payload)


def test_validate_issues_index_rejects_bad_issue_ref_path(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_sample_index(run_dir)
    payload["issues"][0]["issue_ref"]["path"] = "stage_reviews/ingest/issues.json"

    with pytest.raises(StageReviewIssueError, match="issue_ref path"):
        validate_issues_index(payload)


def test_validate_issues_index_rejects_hash_mismatch(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_sample_index(run_dir)
    detail_path = issue_detail_path(run_dir, "ingest", "P1-001")
    detail_payload = read_json(detail_path)
    detail_payload["summary"] = "Changed after the index was built."
    write(detail_path, json.dumps(detail_payload))

    with pytest.raises(StageReviewIssueError, match="sha256 mismatch"):
        validate_issues_index(payload, run_dir=run_dir)


def test_validate_issue_detail_rejects_artifact_body_fields(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir)
    detail_payload = read_json(issue_detail_path(run_dir, "ingest", "P1-001"))
    detail_payload["artifact_body"] = "full artifact body"

    with pytest.raises(StageReviewIssueError, match="body-like|unexpected"):
        validate_issue_detail(detail_payload)


def test_summarize_issues_index_returns_top_n_only(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    issues = [source_issue(f"P3-{index:03d}", "P3") for index in range(8)]
    payload = build_sample_index(run_dir, issues)

    summary = summarize_issues_index(payload, limit=3)

    assert summary["issue_count"] == 8
    assert summary["returned_issue_count"] == 3
    assert len(summary["issues"] ) == 3


def test_summarize_issues_index_prioritizes_p0_and_p1(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_sample_index(
        run_dir,
        [
            source_issue("P3-001", "P3"),
            source_issue("P2-001", "P2"),
            source_issue("P1-001", "P1"),
            source_issue("P0-001", "P0"),
            source_issue("INFO-001", "info"),
        ],
    )

    summary = summarize_issues_index(payload, limit=2)

    assert [item["issue_id"] for item in summary["issues"]] == ["P0-001", "P1-001"]


def test_summarize_issues_index_does_not_read_issue_detail_files(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir)
    issue_detail_path(run_dir, "ingest", "P1-001").unlink()

    summary = summarize_issues_index(issues_index_path(run_dir, "ingest"), limit=5)

    assert summary["issue_count"] == 1
    assert summary["issues"][0]["issue_id"] == "P1-001"


def test_missing_issue_detail_file_fails_closed_when_index_references_it(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_sample_index(run_dir)
    issue_detail_path(run_dir, "ingest", "P1-001").unlink()

    with pytest.raises(StageReviewIssueError, match="does not exist"):
        validate_issues_index(payload, run_dir=run_dir)


def test_public_source_build_is_strict_and_run_contained(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    source_path = write_public_source(run_dir, [public_source_issue(run_dir)])

    payload = build_issues_index(
        run_dir,
        "ingest",
        source_path=source_path.relative_to(run_dir),
    )

    assert payload["issue_count"] == 1
    assert validate_issues_index(payload, run_dir=run_dir) == payload


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload.update({"extra": True}), "unexpected fields"),
        (lambda payload: payload["issues"][0].update({"extra": True}), "unexpected fields"),
        (lambda payload: payload["issues"][0].pop("rationale"), "missing required fields"),
        (lambda payload: payload["issues"][0].update({"severity": "critical"}), "invalid severity"),
    ],
)
def test_public_source_rejects_unknown_missing_and_invalid_fields(tmp_path, mutate, message):
    run_dir = tmp_path / "runs" / "demo-run"
    source = {"issues": [public_source_issue(run_dir)]}
    mutate(source)
    source_path = run_dir / "stage_reviews" / "ingest" / "issues.json"
    write(source_path, json.dumps(source))

    with pytest.raises(StageReviewIssueError, match=message):
        build_issues_index(run_dir, "ingest", source_path=source_path)

    assert not issues_index_path(run_dir, "ingest").exists()
    assert not issue_detail_path(run_dir, "ingest", "P1-001").exists()


def test_public_source_rejects_paths_outside_run_and_bad_artifact_hash(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    issue = public_source_issue(run_dir)
    outside_source = tmp_path / "outside.json"
    write(outside_source, json.dumps({"issues": [issue]}))

    with pytest.raises(StageReviewIssueError, match="escapes run_dir"):
        build_issues_index(run_dir, "ingest", source_path=outside_source)

    issue["artifact_refs"][0]["sha256"] = "0" * 64
    source_path = write_public_source(run_dir, [issue])
    with pytest.raises(StageReviewIssueError, match="sha256 mismatch"):
        build_issues_index(run_dir, "ingest", source_path=source_path)

    assert not issues_index_path(run_dir, "ingest").exists()


def test_public_source_rejects_duplicate_ids_and_escaping_artifact_ref(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    first = public_source_issue(run_dir)
    duplicate_source = write_public_source(run_dir, [first, dict(first)])

    with pytest.raises(StageReviewIssueError, match="duplicate issue_id"):
        build_issues_index(run_dir, "ingest", source_path=duplicate_source)

    escaping = public_source_issue(run_dir)
    escaping["artifact_refs"] = [{"path": "../outside.md", "sha256": "0" * 64}]
    escaping_source = write_public_source(run_dir, [escaping])
    with pytest.raises(StageReviewIssueError, match="must not contain '..'"):
        build_issues_index(run_dir, "ingest", source_path=escaping_source)

    assert not issues_index_path(run_dir, "ingest").exists()


def test_existing_issue_set_requires_explicit_overwrite_and_replaces_stale_details(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    replacement = source_issue("P2-NEW", "P2")

    with pytest.raises(StageReviewIssueError, match="already exists"):
        build_issues_index(run_dir, "ingest", issues=[replacement])

    payload = build_issues_index(
        run_dir,
        "ingest",
        issues=[replacement],
        overwrite=True,
    )

    assert [item["issue_id"] for item in payload["issues"]] == ["P2-NEW"]
    assert not issue_detail_path(run_dir, "ingest", "P1-OLD").exists()
    assert issue_detail_path(run_dir, "ingest", "P2-NEW").is_file()


@pytest.mark.parametrize(
    "metadata_path",
    [
        "orchestration/context_packages/ingest/step-review.json",
        "orchestration/review_context_packages/ingest.json",
        "orchestration/progress_ledger.json",
        "stage_reviews/ingest/decision.json",
        "orchestration/stage_gate_results/ingest.json",
    ],
)
def test_overwrite_rejects_issue_refs_in_active_metadata(tmp_path, metadata_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    index_relative = "stage_reviews/ingest/issues_index.json"
    write(
        run_dir / metadata_path,
        json.dumps(
            {
                "active_ref": {
                    "path": index_relative,
                    "sha256": sha256_file(run_dir / index_relative),
                }
            }
        ),
    )

    with pytest.raises(StageReviewIssueError, match="active metadata"):
        build_issues_index(
            run_dir,
            "ingest",
            issues=[source_issue("P2-NEW", "P2")],
            overwrite=True,
        )

    assert read_json(issues_index_path(run_dir, "ingest"))["issues"][0]["issue_id"] == "P1-OLD"


def test_overwrite_rejects_active_issue_detail_ref(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    detail_relative = "stage_reviews/ingest/issues/P1-OLD.json"
    write(
        run_dir / "orchestration" / "progress_ledger.json",
        json.dumps(
            {
                "active_ref": {
                    "path": detail_relative,
                    "sha256": sha256_file(run_dir / detail_relative),
                }
            }
        ),
    )

    with pytest.raises(StageReviewIssueError, match="active metadata"):
        build_issues_index(
            run_dir,
            "ingest",
            issues=[source_issue("P2-NEW", "P2")],
            overwrite=True,
        )


def test_overwrite_rejects_issue_set_referenced_by_a_ledger_bound_review_result(
    tmp_path,
):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    index_relative = "stage_reviews/ingest/issues_index.json"
    review_relative = (
        "orchestration/review_results/ingest/step-input-materials.json"
    )
    review_path = run_dir / review_relative
    write(
        review_path,
        json.dumps(
            {
                "review_package_paths": [index_relative],
                "review_package_hashes": {
                    index_relative: sha256_file(run_dir / index_relative)
                },
            }
        ),
    )
    write(
        run_dir / "orchestration/progress_ledger.json",
        json.dumps(
            {
                "review_result_ref": {
                    "path": review_relative,
                    "sha256": sha256_file(review_path),
                }
            }
        ),
    )

    with pytest.raises(StageReviewIssueError, match="active metadata"):
        build_issues_index(
            run_dir,
            "ingest",
            issues=[source_issue("P2-NEW", "P2")],
            overwrite=True,
        )


def test_overwrite_follows_a_gate_bound_noncanonical_decision_ref(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    index_relative = "stage_reviews/ingest/issues_index.json"
    decision_relative = "custom-bindings/gate-decision.payload"
    decision_path = run_dir / decision_relative
    write(
        decision_path,
        json.dumps(
            {
                "stage": "ingest",
                "decision": "accepted",
                "decision_scope": "stage_review_gate_only",
                "professional_approval": False,
                "issues_index_ref": {
                    "path": index_relative,
                    "sha256": sha256_file(run_dir / index_relative),
                },
                "notes": "Accept this stage review gate only.",
            }
        ),
    )
    build_stage_gate_result(
        run_dir=run_dir,
        stage="ingest",
        decision_path=decision_path,
    )

    with pytest.raises(StageReviewIssueError, match="active metadata"):
        build_issues_index(
            run_dir,
            "ingest",
            issues=[source_issue("P2-NEW", "P2")],
            overwrite=True,
        )


def test_overwrite_follows_a_gate_bound_noncanonical_review_result_ref(tmp_path):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    index_relative = "stage_reviews/ingest/issues_index.json"
    review_relative = "custom-bindings/gate-review-result.payload"
    review_path = run_dir / review_relative
    write(
        review_path,
        json.dumps(
            {
                "kind": "review_result",
                "schema_version": 1,
                "run_id": "demo-run",
                "stage": "ingest",
                "step": "step-input-materials",
                "status": "done",
                "review_package_paths": [index_relative],
                "review_package_hashes": {
                    index_relative: sha256_file(run_dir / index_relative),
                },
                "summary": "Review completed against the current issue set.",
                "blocking_issues_count": 0,
                "next_gate_status": "needs_user_decision",
            }
        ),
    )
    build_stage_gate_result(
        run_dir=run_dir,
        stage="ingest",
        review_result_paths=[review_path],
    )

    with pytest.raises(StageReviewIssueError, match="active metadata"):
        build_issues_index(
            run_dir,
            "ingest",
            issues=[source_issue("P2-NEW", "P2")],
            overwrite=True,
        )


def test_failed_overwrite_restores_old_index_and_details_without_partial_new_files(
    tmp_path,
    monkeypatch,
):
    run_dir = tmp_path / "runs" / "demo-run"
    build_sample_index(run_dir, [source_issue("P1-OLD", "P1")])
    index_path = issues_index_path(run_dir, "ingest")
    old_detail_path = issue_detail_path(run_dir, "ingest", "P1-OLD")
    old_index_bytes = index_path.read_bytes()
    old_detail_bytes = old_detail_path.read_bytes()
    real_replace = os.replace
    candidate_replaces = 0

    def fail_once_mid_commit(source, destination):
        nonlocal candidate_replaces
        if ".issues-build-" in str(source):
            candidate_replaces += 1
            if candidate_replaces == 2:
                raise OSError("simulated mid-commit failure")
        return real_replace(source, destination)

    monkeypatch.setattr(stage_review_issues.os, "replace", fail_once_mid_commit)

    with pytest.raises(StageReviewIssueError, match="simulated mid-commit failure"):
        build_issues_index(
            run_dir,
            "ingest",
            issues=[
                source_issue("P2-NEW", "P2"),
                source_issue("P3-NEW", "P3"),
            ],
            overwrite=True,
        )

    assert index_path.read_bytes() == old_index_bytes
    assert old_detail_path.read_bytes() == old_detail_bytes
    assert not issue_detail_path(run_dir, "ingest", "P2-NEW").exists()
    assert not issue_detail_path(run_dir, "ingest", "P3-NEW").exists()
