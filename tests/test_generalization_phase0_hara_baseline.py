import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_DOC = REPO_ROOT / "docs" / "baselines" / "HARA_MVP_BASELINE.md"
DEMO_TASK = REPO_ROOT / "examples" / "hara_demo_fixture" / "task.yaml"

REQUIRED_ARTIFACTS = [
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
    "review/final_review.md",
    "verify/verify_report.json",
    "verify/failures.md",
    "revision_plan.json",
    "revised/full_draft.md",
    "revised/change_log.md",
    "final/final_report.md",
    "final/delivery_summary.md",
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/reusable_patterns.md",
    "learning/candidate_profile_update.yaml",
    "learning/candidate_skill_patch.md",
    "learning/promotion_report.md",
]

UNSAFE_APPROVAL_CLAIMS = [
    "final ASIL is",
    "risk is acceptable",
    "safety goal is approved",
    "formal compliance approval",
    "official compliance approval",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_demo_fixture(tmp_path: Path) -> Path:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "write-run",
            "--task",
            str(DEMO_TASK),
            "--runs-dir",
            str(tmp_path / "runs"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return Path(next(line.removeprefix("Run: ").strip() for line in result.stdout.splitlines() if line.startswith("Run: ")))


def test_generalization_phase0_hara_baseline_is_recorded_and_regression_safe(tmp_path: Path) -> None:
    assert BASELINE_DOC.exists(), "Generalization Phase 0 baseline document is required"

    run_dir = run_demo_fixture(tmp_path)

    for relative_path in REQUIRED_ARTIFACTS:
        assert (run_dir / relative_path).exists(), relative_path

    inventory = read_json(run_dir / "inputs" / "input_inventory.json")
    sample_files = [file for file in inventory["files"] if file["role"] in {"sample", "expected_output_shape"}]
    assert sample_files
    assert all(file["is_fact_source"] is False for file in sample_files)

    source_index = read_json(run_dir / "knowledge" / "source_index.json")
    indexed_paths = {source["path"]: source for source in source_index["sources"]}
    if "inputs/sample_hara.md" in indexed_paths:
        assert indexed_paths["inputs/sample_hara.md"]["is_fact_source"] is False
    assert all(
        not source["path"].endswith("sample_hara.md") or source["is_fact_source"] is False
        for source in source_index["sources"]
    )

    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined_lower = f"{final_report}\n{delivery_summary}".lower()
    assert "needs_user_confirmation" in combined_lower
    assert "合格人工审查" in f"{final_report}\n{delivery_summary}"
    for unsafe_claim in UNSAFE_APPROVAL_CLAIMS:
        assert unsafe_claim not in combined_lower

    candidate_profile = (run_dir / "learning" / "candidate_profile_update.yaml").read_text(encoding="utf-8")
    assert "status: proposed" in candidate_profile
    assert "active: false" in candidate_profile
    assert "auto_applied: false" in candidate_profile
    assert "stable_skill_overwrite_allowed: false" in candidate_profile

    promotion_report = (run_dir / "learning" / "promotion_report.md").read_text(encoding="utf-8")
    assert "Stable skill overwritten: no" in promotion_report

    baseline_text = BASELINE_DOC.read_text(encoding="utf-8")
    assert "Phase 0" in baseline_text
    assert "document_types" in baseline_text
    assert "does not introduce document type generalization" in baseline_text
