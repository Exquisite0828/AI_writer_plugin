import json
import subprocess
import sys
from pathlib import Path


def write_task(path: Path, *, include_task_type: bool = True) -> None:
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
    assert task_brief["task_type"] == "generic_document"
    assert task_brief["task_title"] == "Demo task"
    assert task_brief["target_audience"] == "Reviewers"
    assert task_brief["output_format"] == "markdown"
    assert task_brief["strict_template"] is True
    assert task_brief["allow_inference"] is False
    assert task_brief["requires_human_confirmation"] == ["final recommendation"]
    assert "inputs" not in task_brief


def test_invalid_task_fails_without_run_dir(tmp_path):
    task_path = tmp_path / "task.yaml"
    output_root = tmp_path / "runs"
    write_task(task_path, include_task_type=False)

    result = run_init(task_path, output_root)

    assert result.returncode != 0
    assert "task_type" in result.stderr
    assert not (output_root / "demo-run").exists()


def test_prompt_does_not_claim_manual_run_creation():
    root = Path(__file__).resolve().parents[1]
    prompt_text = "\n".join(
        [
            (root / "commands/write.md").read_text(encoding="utf-8"),
            (root / "skills/workflow-steps/step-input-materials/SKILL.md").read_text(
                encoding="utf-8"
            ),
        ]
    )

    forbidden_phrases = [
        "手动创建 run 目录",
        "预创建完整 artifact tree",
        "pre-create every possible run subdirectory",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in prompt_text
