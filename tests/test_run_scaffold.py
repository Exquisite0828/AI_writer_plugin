import json
import subprocess
import sys
from pathlib import Path


def write_task(path: Path, *, include_task_type: bool = True) -> None:
    (path.parent / "inputs").mkdir(parents=True, exist_ok=True)
    (path.parent / "inputs" / "source.md").write_text(
        "Input source body that must not be copied into run metadata.\n",
        encoding="utf-8",
    )
    lines = []
    if include_task_type:
        lines.append("task_type: generic_document")
    lines.extend(
        [
            "task_title: Demo task",
            "target_audience: Reviewers",
            "output_format: markdown",
            "strict_template: true",
            "allow_inference: false",
            "requires_human_confirmation:",
            "  - final recommendation",
            "inputs:",
            "  - path: inputs/source.md",
            "    role: source",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_init(task_path: Path, output_root: Path, run_id: str = "demo-run"):
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "init-run",
            "--task",
            str(task_path),
            "--output-root",
            str(output_root),
            "--run-id",
            run_id,
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )


def test_init_run_creates_only_phase0_artifacts(tmp_path):
    task_path = tmp_path / "task.yaml"
    output_root = tmp_path / "runs"
    write_task(task_path)

    result = run_init(task_path, output_root)

    assert result.returncode == 0, result.stderr
    run_dir = output_root / "demo-run"
    assert sorted(p.relative_to(run_dir).as_posix() for p in run_dir.rglob("*")) == [
        "input_refs.json",
        "manifest.json",
        "task_brief.json",
    ]
    for unexpected_dir in [
        "inputs",
        "knowledge",
        "plans",
        "draft",
        "review",
        "verify",
        "final",
        "learning",
        "stage_reviews",
        "subagent",
    ]:
        assert not (run_dir / unexpected_dir).exists()


def test_manifest_records_phase0_contract(tmp_path):
    task_path = tmp_path / "task.yaml"
    output_root = tmp_path / "runs"
    write_task(task_path)

    result = run_init(task_path, output_root)

    assert result.returncode == 0, result.stderr
    manifest = json.loads((output_root / "demo-run" / "manifest.json").read_text())
    assert manifest["status"] == "initialized"
    assert manifest["phase"] == "phase_0"
    assert [item["path"] for item in manifest["artifacts"]] == [
        "input_refs.json",
        "manifest.json",
        "task_brief.json",
    ]


def test_task_brief_excludes_inputs(tmp_path):
    task_path = tmp_path / "task.yaml"
    output_root = tmp_path / "runs"
    write_task(task_path)

    result = run_init(task_path, output_root)

    assert result.returncode == 0, result.stderr
    task_brief = json.loads((output_root / "demo-run" / "task_brief.json").read_text())
    input_refs = json.loads((output_root / "demo-run" / "input_refs.json").read_text())
    assert task_brief["task_type"] == "generic_document"
    assert task_brief["task_title"] == "Demo task"
    assert task_brief["target_audience"] == "Reviewers"
    assert task_brief["output_format"] == "markdown"
    assert task_brief["strict_template"] is True
    assert task_brief["allow_inference"] is False
    assert task_brief["requires_human_confirmation"] == ["final recommendation"]
    assert "inputs" not in task_brief
    assert input_refs["task_ref"]["role"] == "task"
    assert input_refs["input_materials"][0]["path"].endswith("inputs/source.md")
    assert "Input source body" not in json.dumps(input_refs, ensure_ascii=False)


def test_input_refs_generated_and_validated_during_init(tmp_path):
    task_path = tmp_path / "task.yaml"
    output_root = tmp_path / "runs"
    write_task(task_path)

    result = run_init(task_path, output_root)

    assert result.returncode == 0, result.stderr
    input_refs = json.loads((output_root / "demo-run" / "input_refs.json").read_text())
    assert input_refs["schema_version"] == "input_refs.v1"
    assert input_refs["task_ref"]["path"] == str(task_path.resolve())
    assert input_refs["task_ref"]["path_kind"] == "external"
    assert input_refs["task_ref"]["read_policy"] == "metadata_only"
    assert input_refs["task_ref"]["fact_source_allowed"] is False
    assert input_refs["input_materials"][0]["path"] == str(
        (tmp_path / "inputs" / "source.md").resolve()
    )
    assert input_refs["input_materials"][0]["path_kind"] == "external"
    assert input_refs["input_materials"][0]["role"] == "source"


def test_committed_hara_minimal_fixture_init_run_succeeds(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    task_path = repo_root / "examples" / "hara_minimal_fixture" / "task.yaml"
    output_root = tmp_path / "runs"

    result = run_init(task_path, output_root, run_id="hara-minimal")

    assert result.returncode == 0, result.stderr
    input_refs = json.loads(
        (output_root / "hara-minimal" / "input_refs.json").read_text()
    )
    materials_by_role = {
        material["role"]: material for material in input_refs["input_materials"]
    }
    assert materials_by_role["checklist"]["read_policy"] == "summary_only"
    assert materials_by_role["checklist"]["fact_source_allowed"] is False
    assert materials_by_role["expected_output_shape"]["read_policy"] == "summary_only"
    assert materials_by_role["expected_output_shape"]["fact_source_allowed"] is False
    assert "Item Definition" not in json.dumps(input_refs, ensure_ascii=False)


def test_invalid_task_fails_without_run_dir(tmp_path):
    task_path = tmp_path / "task.yaml"
    output_root = tmp_path / "runs"
    write_task(task_path, include_task_type=False)

    result = run_init(task_path, output_root)

    assert result.returncode != 0
    assert "task_type" in result.stderr
    assert not (output_root / "demo-run").exists()
