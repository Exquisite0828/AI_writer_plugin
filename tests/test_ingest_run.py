import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_1_ARTIFACTS = {
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/provenance_index.json",
    "knowledge/knowledge_gaps.md",
}
RUNTIME_CONTROL_ARTIFACTS = {"run_state.json"}

PHASE_2_ARTIFACTS = [
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/outline_final.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/citation_plan.json",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
    "draft/full_draft.md",
    "review/final_review.md",
    "verify/verify_report.json",
    "revised/full_draft.md",
    "final/final_report.md",
    "trace/session_trace.jsonl",
    "trace/hitl_decisions.jsonl",
    "learning/run_summary.md",
    "learning/candidate_profile_update.yaml",
]


def ingest_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import ingest_run

    return ingest_run(task_file=task_path, runs_dir=runs_dir)


def init_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import init_run

    return init_run(task_file=task_path, runs_dir=runs_dir)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generated_files(run_dir: Path) -> set[str]:
    return {path.relative_to(run_dir).as_posix() for path in run_dir.rglob("*") if path.is_file()}


def generated_professional_artifacts(run_dir: Path) -> set[str]:
    return generated_files(run_dir) - RUNTIME_CONTROL_ARTIFACTS


def run_fixture(tmp_path: Path) -> Path:
    return ingest_run(FIXTURE_TASK, tmp_path / "runs")


def inventory_by_path(run_dir: Path) -> dict[str, dict]:
    inventory = read_json(run_dir / "inputs" / "input_inventory.json")
    return {record["path"]: record for record in inventory["files"]}


def source_index(run_dir: Path) -> dict:
    return read_json(run_dir / "knowledge" / "source_index.json")


def test_ingest_run_creates_phase_1_artifacts(tmp_path: Path) -> None:
    run_dir = run_fixture(tmp_path)

    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "task_brief.json").exists()
    assert (run_dir / "inputs" / "input_inventory.json").exists()
    assert (run_dir / "knowledge" / "source_index.json").exists()
    assert (run_dir / "knowledge" / "knowledge_gaps.md").exists()
    read_json(run_dir / "manifest.json")
    read_json(run_dir / "task_brief.json")
    read_json(run_dir / "inputs" / "input_inventory.json")
    read_json(run_dir / "knowledge" / "source_index.json")


def test_input_inventory_contains_all_declared_inputs(tmp_path: Path) -> None:
    run_dir = run_fixture(tmp_path)
    task_config = yaml.safe_load(FIXTURE_TASK.read_text(encoding="utf-8"))
    inventory = read_json(run_dir / "inputs" / "input_inventory.json")

    assert set(inventory) == {"run_id", "generated_at", "files", "summary"}
    assert len(inventory["files"]) == len(task_config["inputs"]) == 10
    assert [record["file_id"] for record in inventory["files"][:3]] == ["FILE-001", "FILE-002", "FILE-003"]

    required_fields = {
        "file_id",
        "path",
        "role",
        "format",
        "parse_status",
        "is_fact_source",
        "title",
        "notes",
        "error_message",
    }
    for record in inventory["files"]:
        assert set(record) == required_fields

    assert inventory["summary"]["total_files"] == 10


def test_inventory_summary_distinguishes_declared_and_parsed_fact_sources(tmp_path: Path) -> None:
    inventory = read_json(run_fixture(tmp_path) / "inputs" / "input_inventory.json")
    summary = inventory["summary"]

    assert summary["fact_source_files"] == 4
    assert summary["parsed_fact_source_files"] == 3
    assert summary["non_fact_source_files"] == 6
    assert summary["parsed_non_fact_source_files"] == 5


def test_input_inventory_sets_fact_source_flags_correctly(tmp_path: Path) -> None:
    records = inventory_by_path(run_fixture(tmp_path))

    assert records["inputs/item_definition.md"]["is_fact_source"] is True
    assert records["inputs/system_notes.txt"]["is_fact_source"] is True
    assert records["inputs/safety_requirements.csv"]["is_fact_source"] is True
    assert records["inputs/method_reference.json"]["is_fact_source"] is False
    assert records["inputs/hara_template.md"]["is_fact_source"] is False
    assert records["inputs/checklist.txt"]["is_fact_source"] is False
    assert records["inputs/sample_hara.md"]["is_fact_source"] is False
    assert records["inputs/expected_output_shape.md"]["is_fact_source"] is False


def test_sample_and_expected_output_shape_are_not_fact_sources(tmp_path: Path) -> None:
    records = inventory_by_path(run_fixture(tmp_path))

    sample = records["inputs/sample_hara.md"]
    expected_shape = records["inputs/expected_output_shape.md"]

    assert sample["role"] == "sample"
    assert sample["parse_status"] == "parsed"
    assert sample["is_fact_source"] is False
    assert expected_shape["role"] == "expected_output_shape"
    assert expected_shape["parse_status"] == "parsed"
    assert expected_shape["is_fact_source"] is False


def test_sample_and_expected_output_shape_do_not_enter_source_index(tmp_path: Path) -> None:
    run_dir = run_fixture(tmp_path)
    records = inventory_by_path(run_dir)
    sources = source_index(run_dir)["sources"]
    indexed_file_ids = {source["file_id"] for source in sources}

    assert records["inputs/sample_hara.md"]["file_id"] not in indexed_file_ids
    assert records["inputs/expected_output_shape.md"]["file_id"] not in indexed_file_ids
    assert all(source["source_role"] not in {"sample", "expected_output_shape"} for source in sources)


def test_source_and_reference_enter_source_index(tmp_path: Path) -> None:
    sources = source_index(run_fixture(tmp_path))["sources"]

    assert any(source["source_role"] == "source" for source in sources)
    assert any(source["source_role"] == "reference" for source in sources)

    required_fields = {
        "source_id",
        "file_id",
        "path",
        "title",
        "section",
        "anchor",
        "text",
        "keywords",
        "source_role",
        "is_fact_source",
        "source_tier",
        "can_support_project_fact",
        "can_support_methodology",
        "can_support_style",
        "can_support_critical_claim",
        "source_date",
        "owner",
        "char_start",
        "char_end",
    }
    for source in sources:
        assert set(source) == required_fields
        assert source["source_id"].startswith("SRC-")
        assert source["file_id"].startswith("FILE-")
        assert source["text"]
        assert source["char_end"] >= source["char_start"]
        assert source["source_tier"] in {"T1_PROJECT_SOURCE", "T3_REFERENCE_METHODOLOGY"}


def test_source_index_does_not_include_heading_only_chunks(tmp_path: Path) -> None:
    sources = source_index(run_fixture(tmp_path))["sources"]
    heading_only = re.compile(r"^#{1,6}\s+.+$")

    assert not [source["source_id"] for source in sources if heading_only.fullmatch(source["text"].strip())]


def test_reference_source_index_records_are_not_fact_sources(tmp_path: Path) -> None:
    sources = source_index(run_fixture(tmp_path))["sources"]

    for source in sources:
        if source["source_role"] == "reference":
            assert source["is_fact_source"] is False
        if source["source_role"] == "source":
            assert source["is_fact_source"] is True


def test_missing_and_unsupported_files_are_recorded_in_inventory_and_gaps(tmp_path: Path) -> None:
    run_dir = run_fixture(tmp_path)
    records = inventory_by_path(run_dir)
    gaps = (run_dir / "knowledge" / "knowledge_gaps.md").read_text(encoding="utf-8")
    sources = source_index(run_dir)["sources"]
    indexed_file_ids = {source["file_id"] for source in sources}

    missing = records["inputs/missing_item_definition.md"]
    unsupported = records["inputs/unsupported_reference.pdf"]

    assert missing["parse_status"] == "missing"
    assert unsupported["parse_status"] == "unsupported"
    assert "inputs/missing_item_definition.md" in gaps
    assert "inputs/unsupported_reference.pdf" in gaps
    assert missing["file_id"] not in indexed_file_ids
    assert unsupported["file_id"] not in indexed_file_ids


def test_md_txt_json_csv_supported_files_are_parsed(tmp_path: Path) -> None:
    records = inventory_by_path(run_fixture(tmp_path))

    assert records["inputs/item_definition.md"]["parse_status"] == "parsed"
    assert records["inputs/system_notes.txt"]["parse_status"] == "parsed"
    assert records["inputs/method_reference.json"]["parse_status"] == "parsed"
    assert records["inputs/safety_requirements.csv"]["parse_status"] == "parsed"


def test_manifest_updated_to_phase_1_for_ingest_run(tmp_path: Path) -> None:
    run_dir = run_fixture(tmp_path)
    manifest = read_json(run_dir / "manifest.json")

    assert manifest["phase"] == "phase_1"
    assert manifest["status"] == "ingested"
    artifact_paths = {artifact["path"] for artifact in manifest["artifacts"]}
    assert artifact_paths == PHASE_1_ARTIFACTS


def test_init_run_still_does_not_generate_phase_1_artifacts(tmp_path: Path) -> None:
    run_dir = init_run(FIXTURE_TASK, tmp_path / "runs")

    assert not (run_dir / "inputs" / "input_inventory.json").exists()
    assert not (run_dir / "knowledge" / "source_index.json").exists()
    assert not (run_dir / "knowledge" / "provenance_index.json").exists()
    assert not (run_dir / "knowledge" / "knowledge_gaps.md").exists()
    generated_files = {path.relative_to(run_dir).as_posix() for path in run_dir.rglob("*") if path.is_file()}
    assert generated_files == {"manifest.json", "task_brief.json"}


def test_ingest_run_does_not_generate_phase_2_artifacts(tmp_path: Path) -> None:
    run_dir = run_fixture(tmp_path)

    for relative_path in PHASE_2_ARTIFACTS:
        assert not (run_dir / relative_path).exists()

    assert generated_professional_artifacts(run_dir) == PHASE_1_ARTIFACTS
    assert generated_files(run_dir) == PHASE_1_ARTIFACTS | RUNTIME_CONTROL_ARTIFACTS


def test_invalid_input_role_fails_task_validation(tmp_path: Path) -> None:
    task_path = tmp_path / "task.yaml"
    task_path.write_text(
        """\
task_type: hara
task_title: 生成 HARA 危害分析报告
target_audience: 功能安全工程师
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - hazard identification
inputs:
  - path: inputs/item_definition.md
    role: factual_example
""",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    with pytest.raises(Exception) as exc_info:
        ingest_run(task_path, runs_dir)

    message = str(exc_info.value)
    assert "Invalid task config" in message
    assert "role" in message
    assert not runs_dir.exists() or not any(runs_dir.iterdir())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "ingest-run",
            "--task",
            str(task_path),
            "--runs-dir",
            str(runs_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "role" in result.stderr or "Invalid task config" in result.stderr


def test_input_paths_are_resolved_relative_to_task_yaml(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixture"
    input_dir = fixture_dir / "inputs"
    input_dir.mkdir(parents=True)
    (input_dir / "item_definition.md").write_text(
        "# Local Item\n\nRelative input path should be parsed from the task directory.",
        encoding="utf-8",
    )
    task_path = fixture_dir / "task.yaml"
    task_path.write_text(
        """\
task_type: hara
task_title: Relative Fixture
target_audience: Functional Safety Engineer
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - hazard identification
inputs:
  - path: inputs/item_definition.md
    role: source
    title: Local Item
""",
        encoding="utf-8",
    )

    run_dir = ingest_run(task_path, tmp_path / "runs")
    records = inventory_by_path(run_dir)
    sources = source_index(run_dir)["sources"]

    assert records["inputs/item_definition.md"]["parse_status"] == "parsed"
    assert records["inputs/item_definition.md"]["path"] == "inputs/item_definition.md"
    assert any(source["path"] == "inputs/item_definition.md" for source in sources)
