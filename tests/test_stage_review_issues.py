import hashlib
import json
from pathlib import Path

import pytest

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
