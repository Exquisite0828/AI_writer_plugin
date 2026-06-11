import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_TASK = REPO_ROOT / "examples" / "hara_demo_fixture" / "task.yaml"
MINIMAL_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

STALE_DELIVERY_PHRASES = [
    "Not Done In This Phase",
    "Claude Code /write integration",
    "trace/session_trace.jsonl",
    "learning/run_summary.md",
    "learning/candidate_profile_update.yaml",
    "plugin.json",
    "root-level commands/ or skills/",
]

DEFERRED_PHASE_NOTES = [
    "Template parsing is deferred to Phase 2",
    "Evidence mapping is deferred to Phase 3",
    "Notes for next phases",
]

UNSAFE_FINAL_CLAIMS = [
    "final ASIL is",
    "risk is acceptable",
    "safety goal is approved",
    "final HARA conclusion",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_write(task_path: Path, tmp_path: Path) -> Path:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "write-run",
            "--task",
            str(task_path),
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


def weak_or_unsupported_evidence_questions(run_dir: Path) -> list[dict]:
    evidence_map = read_json(run_dir / "plans" / "evidence_map.json")
    return [
        question
        for question in evidence_map["questions"]
        if question["status"] in {"weak", "unsupported", "unresolved", "needs_confirmation", "requires_human_confirmation"}
    ]


def test_demo_fixture_final_outputs_use_generic_hygiene(tmp_path: Path) -> None:
    run_dir = run_write(DEMO_TASK, tmp_path)
    final_report_path = run_dir / "final" / "final_report.md"
    delivery_summary_path = run_dir / "final" / "delivery_summary.md"
    final_report = final_report_path.read_text(encoding="utf-8")
    delivery_summary = delivery_summary_path.read_text(encoding="utf-8")
    combined = f"{final_report}\n{delivery_summary}"

    assert final_report_path.exists()
    assert delivery_summary_path.exists()

    for phrase in STALE_DELIVERY_PHRASES:
        assert phrase not in delivery_summary
    assert "finalized_with_open_items" in delivery_summary
    assert "合格人工审查" in delivery_summary
    assert "candidate update 保持 proposed / inactive" in delivery_summary

    evidence_issues = weak_or_unsupported_evidence_questions(run_dir)
    assert evidence_issues
    for issue in evidence_issues:
        assert issue["question_id"] in final_report
        assert issue["section_id"] in final_report
        assert issue["status"] in final_report
    assert "No unsupported, weak evidence, missing, or unresolved task was found in review_report.json." not in final_report

    for phrase in DEFERRED_PHASE_NOTES:
        assert phrase not in combined
    assert "本次运行未发现 missing、unsupported 或 failed 输入材料。" in final_report
    assert "本次运行未发现 missing 或 unsupported 输入材料。" in delivery_summary
    assert "missing_item_definition.md" not in combined
    assert "unsupported_reference.pdf" not in combined
    assert "Missing or unsupported materials remain open knowledge gaps" not in combined
    assert "Missing materials and unsupported formats are preserved as open delivery limitations" not in combined

    assert "sample_hara.md" in combined
    assert "role=sample | is_fact_source=false" in combined
    assert "NEEDS_USER_CONFIRMATION" in combined
    assert "S? / E? / C?" in combined
    assert "ASIL candidate remains TBD" in combined

    for unsafe_claim in UNSAFE_FINAL_CLAIMS:
        assert unsafe_claim.lower() not in combined.lower()


def test_minimal_fixture_real_gaps_are_preserved(tmp_path: Path) -> None:
    run_dir = run_write(MINIMAL_TASK, tmp_path)
    final_report = (run_dir / "final" / "final_report.md").read_text(encoding="utf-8")
    delivery_summary = (run_dir / "final" / "delivery_summary.md").read_text(encoding="utf-8")
    combined = f"{final_report}\n{delivery_summary}"
    combined_lower = combined.lower()

    assert "missing_item_definition.md" in combined
    assert "unsupported_reference.pdf" in combined
    assert "No missing, unsupported, or failed input materials were found in this run." not in combined
    assert "No missing or unsupported input materials were found in this run." not in combined
    assert "Missing 或 unsupported 输入材料仍作为开放知识缺口保留。" in delivery_summary

    assert "sample_hara.md" in combined
    assert "expected_output_shape.md" in combined
    assert "role=sample | is_fact_source=false" in combined
    assert "role=expected_output_shape | is_fact_source=false" in combined

    for unsafe_claim in UNSAFE_FINAL_CLAIMS:
        assert unsafe_claim.lower() not in combined_lower
