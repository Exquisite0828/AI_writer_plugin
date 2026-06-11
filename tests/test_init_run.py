import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]

VALID_TASK_YAML = """\
task_type: hara
task_title: 生成 HARA 危害分析报告
target_audience: 功能安全工程师
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - hazard identification
  - severity/exposure/controllability rating
  - ASIL or risk level conclusion
"""

PHASE_1_ARTIFACTS = [
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/provenance_index.json",
    "knowledge/knowledge_gaps.md",
    "knowledge/document_wiki.md",
    "knowledge/glossary.md",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/outline_final.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/citation_plan.json",
    "plans/claim_support_matrix.json",
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


def write_task(tmp_path: Path, content: str = VALID_TASK_YAML) -> Path:
    task_path = tmp_path / "task.yaml"
    task_path.write_text(content, encoding="utf-8")
    return task_path


def init_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import init_run

    return init_run(task_file=task_path, runs_dir=runs_dir)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task_config_inputs_uses_default_factory() -> None:
    from ai_writing_plugin.models import TaskConfig

    assert TaskConfig.model_fields["inputs"].default_factory is list


def test_create_unique_run_dir_uses_suffix_when_base_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import ai_writing_plugin.run_manager as run_manager

    class FixedDateTime:
        @classmethod
        def now(cls, tz: object) -> "FixedDateTime":
            return cls()

        def strftime(self, fmt: str) -> str:
            return "20260602-131035"

    monkeypatch.setattr(run_manager, "datetime", FixedDateTime)

    first_run_id, first_run_dir = run_manager.create_unique_run_dir(tmp_path / "runs", "hara")
    second_run_id, second_run_dir = run_manager.create_unique_run_dir(tmp_path / "runs", "hara")

    assert first_run_id == "20260602-131035-hara"
    assert second_run_id == "20260602-131035-hara-2"
    assert first_run_dir.exists()
    assert second_run_dir.exists()
    assert first_run_dir != second_run_dir


def test_consecutive_init_runs_do_not_overwrite(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    runs_dir = tmp_path / "runs"

    first_run_dir = init_run(task_path, runs_dir)
    second_run_dir = init_run(task_path, runs_dir)

    assert first_run_dir != second_run_dir
    assert first_run_dir.name != second_run_dir.name
    assert (first_run_dir / "manifest.json").exists()
    assert (second_run_dir / "manifest.json").exists()


def test_init_run_creates_run_directory(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    runs_dir = tmp_path / "runs"

    run_dir = init_run(task_path, runs_dir)

    assert run_dir.exists()
    assert run_dir.is_dir()
    assert run_dir.parent == runs_dir


def test_init_run_writes_manifest(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    run_dir = init_run(task_path, tmp_path / "runs")

    manifest_path = run_dir / "manifest.json"

    assert manifest_path.exists()
    assert read_json(manifest_path)["run_id"]


def test_init_run_writes_task_brief(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    run_dir = init_run(task_path, tmp_path / "runs")

    task_brief_path = run_dir / "task_brief.json"

    assert task_brief_path.exists()
    assert read_json(task_brief_path)["run_id"]


def test_manifest_contains_required_phase_0_fields(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    run_dir = init_run(task_path, tmp_path / "runs")

    manifest = read_json(run_dir / "manifest.json")

    assert set(manifest) == {
        "run_id",
        "task_file",
        "created_at",
        "status",
        "phase",
        "artifacts",
    }
    assert manifest["run_id"]
    assert manifest["task_file"]
    assert manifest["created_at"].endswith("Z")
    assert manifest["status"] == "initialized"
    assert manifest["phase"] == "phase_0"
    assert isinstance(manifest["artifacts"], list)

    artifacts_by_path = {item["path"]: item for item in manifest["artifacts"]}
    assert set(artifacts_by_path) == {"manifest.json", "task_brief.json"}
    for artifact in artifacts_by_path.values():
        assert set(artifact) == {"path", "kind", "created_at"}
        assert artifact["path"]
        assert artifact["kind"]
        assert artifact["created_at"].endswith("Z")


def test_task_brief_contains_required_fields(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    run_dir = init_run(task_path, tmp_path / "runs")

    task_brief = read_json(run_dir / "task_brief.json")

    assert set(task_brief) == {
        "run_id",
        "task_type",
        "task_title",
        "target_audience",
        "output_format",
        "strict_template",
        "allow_inference",
        "requires_human_confirmation",
    }
    assert task_brief["run_id"]
    assert task_brief["task_type"] == "hara"
    assert task_brief["task_title"] == "生成 HARA 危害分析报告"
    assert task_brief["target_audience"] == "功能安全工程师"
    assert task_brief["output_format"] == "markdown"
    assert task_brief["strict_template"] is True
    assert task_brief["allow_inference"] is False
    assert task_brief["requires_human_confirmation"] == [
        "hazard identification",
        "severity/exposure/controllability rating",
        "ASIL or risk level conclusion",
    ]


def test_invalid_task_config_fails_with_clear_error(tmp_path: Path) -> None:
    invalid_task = write_task(
        tmp_path,
        """\
task_type: hara
task_title: " "
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - ""
""",
    )
    runs_dir = tmp_path / "runs"

    with pytest.raises(Exception) as exc_info:
        init_run(invalid_task, runs_dir)

    message = str(exc_info.value)
    assert "Invalid task config" in message or "validation" in message.lower()
    assert not runs_dir.exists() or not any(runs_dir.iterdir())

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "init-run",
            "--task",
            str(invalid_task),
            "--runs-dir",
            str(runs_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "Invalid task config" in result.stderr or "validation" in result.stderr.lower()


def test_requires_human_confirmation_wrong_type_fails_without_run(tmp_path: Path) -> None:
    invalid_task = write_task(
        tmp_path,
        """\
task_type: hara
task_title: 生成 HARA 危害分析报告
target_audience: 功能安全工程师
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation: hazard identification
""",
    )
    runs_dir = tmp_path / "runs"

    with pytest.raises(Exception) as exc_info:
        init_run(invalid_task, runs_dir)

    message = str(exc_info.value)
    assert "Invalid task config" in message
    assert "requires_human_confirmation" in message
    assert "list" in message
    assert not runs_dir.exists() or not any(runs_dir.iterdir())


@pytest.mark.parametrize(
    ("yaml_content", "expected_message"),
    [
        ("task_type: [unterminated\n", "Invalid YAML"),
        ("- task_type: hara\n", "YAML root must be a mapping"),
    ],
)
def test_invalid_yaml_or_non_mapping_yaml_fails_without_run(
    tmp_path: Path, yaml_content: str, expected_message: str
) -> None:
    invalid_task = write_task(tmp_path, yaml_content)
    runs_dir = tmp_path / "runs"

    with pytest.raises(Exception) as exc_info:
        init_run(invalid_task, runs_dir)

    message = str(exc_info.value)
    assert expected_message in message
    assert not runs_dir.exists() or not any(runs_dir.iterdir())


def test_run_outputs_are_created_under_runs_dir(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    runs_dir = tmp_path / "custom-runs"

    run_dir = init_run(task_path, runs_dir)

    assert run_dir.parent == runs_dir
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "task_brief.json").exists()
    assert not (tmp_path / "manifest.json").exists()
    assert not (tmp_path / "task_brief.json").exists()


def test_phase_0_does_not_create_phase_1_artifacts(tmp_path: Path) -> None:
    task_path = write_task(tmp_path)
    run_dir = init_run(task_path, tmp_path / "runs")

    for relative_path in PHASE_1_ARTIFACTS:
        assert not (run_dir / relative_path).exists()

    generated_files = {path.relative_to(run_dir).as_posix() for path in run_dir.rglob("*") if path.is_file()}
    assert generated_files == {"manifest.json", "task_brief.json"}


def test_cli_init_run_with_minimal_fixture(tmp_path: Path) -> None:
    fixture_task = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"
    runs_dir = tmp_path / "runs"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "init-run",
            "--task",
            str(fixture_task),
            "--runs-dir",
            str(runs_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Created run:" in result.stdout
    run_dir = Path(result.stdout.strip().split("Created run:", 1)[1].strip())
    assert run_dir.exists()
    assert run_dir.parent == runs_dir
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "task_brief.json").exists()
