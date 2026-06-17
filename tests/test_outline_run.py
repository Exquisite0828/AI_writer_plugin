import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_0_ARTIFACTS = {"manifest.json", "task_brief.json"}
PHASE_1_ARTIFACTS = {
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/provenance_index.json",
    "knowledge/knowledge_gaps.md",
}
PHASE_2_ARTIFACTS = PHASE_1_ARTIFACTS | {
    "plans/template_structure.json",
    "plans/outline_l1.md",
}
RUNTIME_CONTROL_ARTIFACTS = {"run_state.json"}
PHASE_3_ARTIFACTS = [
    "plans/outline_final.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/citation_plan.json",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
    "draft/full_draft.md",
    "draft/section_001.md",
    "review/final_review.md",
    "verify/verify_report.json",
    "revised/full_draft.md",
    "final/final_report.md",
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/candidate_profile_update.yaml",
]


def init_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import init_run

    return init_run(task_file=task_path, runs_dir=runs_dir)


def ingest_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import ingest_run

    return ingest_run(task_file=task_path, runs_dir=runs_dir)


def outline_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import outline_run

    return outline_run(run_dir=run_dir)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_files(run_dir: Path) -> set[str]:
    return {path.relative_to(run_dir).as_posix() for path in run_dir.rglob("*") if path.is_file()}


def generated_professional_artifacts(run_dir: Path) -> set[str]:
    return generated_files(run_dir) - RUNTIME_CONTROL_ARTIFACTS


def run_phase_2_fixture(tmp_path: Path) -> Path:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    return outline_run(run_dir)


def inventory_by_path(run_dir: Path) -> dict[str, dict]:
    inventory = read_json(run_dir / "inputs" / "input_inventory.json")
    return {record["path"]: record for record in inventory["files"]}


def make_task_fixture(tmp_path: Path, template_content: str | None) -> Path:
    fixture_dir = tmp_path / "fixture"
    input_dir = fixture_dir / "inputs"
    input_dir.mkdir(parents=True)
    if template_content is not None:
        (input_dir / "template.md").write_text(template_content, encoding="utf-8")
    task_path = fixture_dir / "task.yaml"
    task_path.write_text(
        """\
task_type: hara
task_title: Fallback HARA
target_audience: Functional Safety Engineer
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - hazard identification
inputs:
  - path: inputs/template.md
    role: template
    title: Local Template
""",
        encoding="utf-8",
    )
    return task_path


def test_outline_run_creates_phase_2_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)

    assert (run_dir / "plans" / "template_structure.json").exists()
    assert (run_dir / "plans" / "outline_l1.md").exists()
    read_json(run_dir / "plans" / "template_structure.json")
    assert (run_dir / "plans" / "outline_l1.md").read_text(encoding="utf-8").startswith("# Outline L1")


def test_outline_run_updates_manifest_to_phase_2(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]

    assert manifest["phase"] == "phase_2"
    assert manifest["status"] == "outlined"
    assert set(artifact_paths) == PHASE_2_ARTIFACTS
    assert len(artifact_paths) == len(set(artifact_paths))


def test_template_structure_uses_template_from_input_inventory(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)
    records = inventory_by_path(run_dir)
    template_structure = read_json(run_dir / "plans" / "template_structure.json")

    assert template_structure["template_source"]["file_id"] == records["inputs/hara_template.md"]["file_id"]
    assert records["inputs/hara_template.md"]["role"] == "template"
    assert template_structure["template_source"]["path"] == "inputs/hara_template.md"
    assert template_structure["fallback_used"] is False
    assert template_structure["status"] == "parsed"
    assert not any("sample" in warning.lower() and "template" in warning.lower() for warning in template_structure["warnings"])


def test_template_structure_contains_template_nodes(tmp_path: Path) -> None:
    template_structure = read_json(run_phase_2_fixture(tmp_path) / "plans" / "template_structure.json")
    nodes = template_structure["nodes"]
    required_fields = {
        "node_id",
        "title",
        "level",
        "order",
        "parent_id",
        "children",
        "required",
        "optional",
        "intent",
        "source_line",
        "anchor",
    }

    assert nodes
    for node in nodes:
        assert set(node) == required_fields
        assert node["node_id"].startswith("TPL-")
        assert isinstance(node["level"], int)
        assert node["level"] > 0
        assert node["required"] is not node["optional"]
        assert node["anchor"].startswith("#")


def test_outline_l1_contains_sections_from_template(tmp_path: Path) -> None:
    outline = (run_phase_2_fixture(tmp_path) / "plans" / "outline_l1.md").read_text(encoding="utf-8")

    assert "# Outline L1" in outline
    assert "SEC-001" in outline
    assert "Document Purpose and Scope" in outline
    assert "Item Definition Summary" in outline
    assert "Intent:" in outline
    assert "Template anchor:" in outline
    assert "Phase boundary note" in outline
    assert "Evidence mapping is deferred to Phase 3." in outline
    assert "Draft generation is not performed in Phase 2." in outline
    assert "evidence_map.json" not in outline
    assert "full_draft.md" not in outline


def test_outline_run_does_not_use_sample_as_template(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)
    records = inventory_by_path(run_dir)
    source_index = read_json(run_dir / "knowledge" / "source_index.json")
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    outline = (run_dir / "plans" / "outline_l1.md").read_text(encoding="utf-8")
    indexed_file_ids = {source["file_id"] for source in source_index["sources"]}

    assert template_structure["template_source"]["file_id"] != records["inputs/sample_hara.md"]["file_id"]
    assert template_structure["template_source"]["path"] != "inputs/sample_hara.md"
    assert "Sample HARA" not in outline
    assert records["inputs/sample_hara.md"]["file_id"] not in indexed_file_ids


def test_outline_run_does_not_generate_phase_3_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)

    for relative_path in PHASE_3_ARTIFACTS:
        assert not (run_dir / relative_path).exists()

    assert generated_professional_artifacts(run_dir) == PHASE_2_ARTIFACTS
    assert generated_files(run_dir) == PHASE_2_ARTIFACTS | RUNTIME_CONTROL_ARTIFACTS


def test_init_run_still_only_generates_phase_0_artifacts(tmp_path: Path) -> None:
    run_dir = init_run(FIXTURE_TASK, tmp_path / "runs")

    assert generated_files(run_dir) == PHASE_0_ARTIFACTS


def test_ingest_run_still_only_generates_phase_0_and_1_artifacts(tmp_path: Path) -> None:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")

    assert generated_professional_artifacts(run_dir) == PHASE_1_ARTIFACTS
    assert generated_files(run_dir) == PHASE_1_ARTIFACTS | RUNTIME_CONTROL_ARTIFACTS


def test_outline_run_requires_existing_phase_1_run(tmp_path: Path) -> None:
    with pytest.raises(Exception) as missing_exc:
        outline_run(tmp_path / "missing-run")
    assert "Run directory not found" in str(missing_exc.value)

    empty_run = tmp_path / "empty-run"
    empty_run.mkdir()
    with pytest.raises(Exception) as empty_exc:
        outline_run(empty_run)
    assert "manifest.json" in str(empty_exc.value)
    assert not (empty_run / "plans").exists()

    phase_0_run = init_run(FIXTURE_TASK, tmp_path / "runs")
    with pytest.raises(Exception) as phase_exc:
        outline_run(phase_0_run)
    assert "phase" in str(phase_exc.value) or "input_inventory" in str(phase_exc.value)
    assert not (phase_0_run / "plans").exists()


def test_outline_run_falls_back_when_template_missing(tmp_path: Path) -> None:
    task_path = make_task_fixture(tmp_path, template_content=None)
    run_dir = outline_run(ingest_run(task_path, tmp_path / "runs"))
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    outline = (run_dir / "plans" / "outline_l1.md").read_text(encoding="utf-8")

    assert template_structure["status"] == "fallback"
    assert template_structure["fallback_used"] is True
    assert "missing" in template_structure["fallback_reason"].lower()
    assert template_structure["template_source"]["file_id"] is None
    assert "Fallback note:" in outline
    assert "文档目的和范围" in outline
    assert "安全目标候选" in outline


def test_outline_run_falls_back_when_template_has_no_headings(tmp_path: Path) -> None:
    task_path = make_task_fixture(tmp_path, template_content="This template has text but no Markdown headings.\n")
    run_dir = outline_run(ingest_run(task_path, tmp_path / "runs"))
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    outline = (run_dir / "plans" / "outline_l1.md").read_text(encoding="utf-8")

    assert template_structure["status"] == "fallback"
    assert template_structure["fallback_used"] is True
    assert "heading" in template_structure["fallback_reason"].lower()
    assert "文档目的和范围" in outline


def test_outline_run_is_repeatable_without_duplicate_manifest_artifacts(tmp_path: Path) -> None:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")

    outline_run(run_dir)
    outline_run(run_dir)

    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]

    assert len(artifact_paths) == len(set(artifact_paths))
    assert (run_dir / "plans" / "template_structure.json").exists()
    assert (run_dir / "plans" / "outline_l1.md").exists()


def test_outline_sections_mark_hara_confirmation_sensitive_sections(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    outline = (run_dir / "plans" / "outline_l1.md").read_text(encoding="utf-8")
    sections = {section["title"]: section for section in template_structure["outline_sections"]}

    assert sections["Document Purpose and Scope"]["needs_human_confirmation"] is False
    assert sections["Hazard Identification"]["needs_human_confirmation"] is True
    assert sections["Hazardous Event Analysis"]["needs_human_confirmation"] is True
    assert sections["S/E/C Rating Table"]["needs_human_confirmation"] is True
    assert sections["Safety Goals Candidate"]["needs_human_confirmation"] is True
    assert "Human confirmation: required before final professional conclusion" in outline


def test_outline_command_cli_success(tmp_path: Path) -> None:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "outline-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Outlined run:" in result.stdout
    assert "plans/template_structure.json" in result.stdout
    assert "plans/outline_l1.md" in result.stdout
    assert (run_dir / "plans" / "template_structure.json").exists()
    assert (run_dir / "plans" / "outline_l1.md").exists()
