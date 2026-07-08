import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.context_metrics import collect_context_metrics


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_context_metrics_scans_only_runtime_prompt_surfaces(tmp_path):
    write(tmp_path / "commands" / "write.md", "command prompt\n")
    write(tmp_path / "skills" / "workflow-orchestrator" / "SKILL.md", "orchestrator\n")
    write(tmp_path / "skills" / "workflow-steps" / "step-source-index" / "SKILL.md", "step\n")
    write(tmp_path / "examples" / "demo.md", "example should not be scanned\n")
    write(tmp_path / "runs" / "demo-run" / "artifact.md", "run output should not be scanned\n")
    write(tmp_path / "docs" / "maintainers" / "context.md", "maintainer docs should not be scanned\n")
    write(tmp_path / "contracts" / "CURRENT_ARTIFACT_CONTRACTS.md", "contract should not be scanned\n")

    metrics = collect_context_metrics(tmp_path, generated_at="2026-07-08T00:00:00+00:00")

    assert metrics["total_files"] == 3
    scanned_paths = {item["path"] for item in metrics["files"]}
    assert scanned_paths == {
        "commands/write.md",
        "skills/workflow-orchestrator/SKILL.md",
        "skills/workflow-steps/step-source-index/SKILL.md",
    }
    assert all(not path.startswith("examples/") for path in scanned_paths)
    assert all(not path.startswith("runs/") for path in scanned_paths)
    assert all(not path.startswith("docs/maintainers/") for path in scanned_paths)
    assert all(not path.startswith("contracts/") for path in scanned_paths)


def test_context_metrics_schema_categories_and_estimated_tokens(tmp_path):
    write(tmp_path / "commands" / "write.md", "abcd")
    write(tmp_path / "skills" / "workflow-orchestrator" / "SKILL.md", "abcdefgh")
    write(tmp_path / "skills" / "workflow-steps" / "step-review" / "SKILL.md", "abcde")
    write(tmp_path / "skills" / "document-types" / "hara" / "SKILL.md", "abcdefghi")
    write(tmp_path / "skills" / "step-review" / "SKILL.md", "abc")

    metrics = collect_context_metrics(tmp_path, generated_at="2026-07-08T00:00:00+00:00")

    assert set(metrics) >= {
        "generated_at",
        "root",
        "total_files",
        "total_bytes",
        "estimated_tokens",
        "by_category",
        "largest_files",
        "hotspot_patterns",
        "files",
    }
    assert metrics["estimated_tokens"] == 9
    assert metrics["by_category"]["command"]["file_count"] == 1
    assert metrics["by_category"]["workflow_orchestrator"]["file_count"] == 1
    assert metrics["by_category"]["workflow_step"]["file_count"] == 1
    assert metrics["by_category"]["document_type"]["file_count"] == 1
    assert metrics["by_category"]["step_wrapper"]["file_count"] == 1
    assert metrics["largest_files"][0]["path"] == "skills/document-types/hara/SKILL.md"
    assert all(len(item["sha256"]) == 64 for item in metrics["files"])


def test_context_metrics_cli_outputs_json(tmp_path):
    write(tmp_path / "commands" / "write.md", "command prompt\n")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin.context_metrics",
            "--root",
            str(tmp_path),
            "--json",
        ],
        text=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["total_files"] == 1
    assert payload["files"][0]["path"] == "commands/write.md"


def test_active_workflow_metrics_only_count_selected_task_type(tmp_path):
    write(tmp_path / "commands" / "write.md", "command\n")
    write(tmp_path / "skills" / "workflow-orchestrator" / "SKILL.md", "orchestrator\n")
    write(tmp_path / "skills" / "writing-core" / "SKILL.md", "core\n")
    write(tmp_path / "skills" / "step-input-materials" / "SKILL.md", "wrapper\n")
    write(tmp_path / "skills" / "step-final-report" / "SKILL.md", "wrapper\n")
    write(
        tmp_path / "skills" / "workflow-steps" / "step-input-materials" / "SKILL.md",
        "canonical\n",
    )
    write(
        tmp_path / "skills" / "workflow-steps" / "step-final-report" / "SKILL.md",
        "canonical\n",
    )
    write(tmp_path / "skills" / "document-types" / "hara" / "SKILL.md", "hara root\n")
    write(
        tmp_path
        / "skills"
        / "document-types"
        / "hara"
        / "steps"
        / "step-input-materials.md",
        "hara overlay\n",
    )
    write(
        tmp_path
        / "skills"
        / "document-types"
        / "SoftwareArchitecture"
        / "SKILL.md",
        "sibling root should be excluded\n",
    )

    metrics = collect_context_metrics(
        tmp_path,
        generated_at="2026-07-08T00:00:00+00:00",
        mode="active-workflow",
        task_type="hara",
    )

    scanned_paths = {item["path"] for item in metrics["files"]}
    assert metrics["mode"] == "active-workflow"
    assert metrics["task_type"] == "hara"
    assert metrics["step"] is None
    assert "skills/document-types/hara/SKILL.md" in scanned_paths
    assert "skills/document-types/hara/steps/step-input-materials.md" in scanned_paths
    assert "skills/document-types/SoftwareArchitecture/SKILL.md" not in scanned_paths
    assert metrics["total_runtime_estimated_tokens"] > metrics["estimated_tokens"]
    assert metrics["active_reduction_vs_total"] > 0
    assert metrics["excluded_document_type_files"] == 1
    assert metrics["excluded_document_type_bytes"] == len(
        "sibling root should be excluded\n".encode("utf-8")
    )


def test_active_step_metrics_count_only_selected_step_and_task_type(tmp_path):
    write(tmp_path / "commands" / "write.md", "command\n")
    write(tmp_path / "skills" / "workflow-orchestrator" / "SKILL.md", "orchestrator\n")
    write(tmp_path / "skills" / "writing-core" / "SKILL.md", "core\n")
    write(tmp_path / "skills" / "step-input-materials" / "SKILL.md", "active wrapper\n")
    write(tmp_path / "skills" / "step-final-report" / "SKILL.md", "other wrapper\n")
    write(
        tmp_path / "skills" / "workflow-steps" / "step-input-materials" / "SKILL.md",
        "active canonical\n",
    )
    write(
        tmp_path / "skills" / "workflow-steps" / "step-final-report" / "SKILL.md",
        "other canonical\n",
    )
    write(tmp_path / "skills" / "document-types" / "hara" / "SKILL.md", "hara root\n")
    write(
        tmp_path
        / "skills"
        / "document-types"
        / "hara"
        / "steps"
        / "step-input-materials.md",
        "active overlay\n",
    )
    write(
        tmp_path
        / "skills"
        / "document-types"
        / "hara"
        / "steps"
        / "step-final-report.md",
        "other overlay\n",
    )

    metrics = collect_context_metrics(
        tmp_path,
        generated_at="2026-07-08T00:00:00+00:00",
        mode="active-step",
        task_type="hara",
        step="step-input-materials",
    )

    scanned_paths = {item["path"] for item in metrics["files"]}
    assert metrics["mode"] == "active-step"
    assert metrics["task_type"] == "hara"
    assert metrics["step"] == "step-input-materials"
    assert "skills/step-input-materials/SKILL.md" in scanned_paths
    assert "skills/workflow-steps/step-input-materials/SKILL.md" in scanned_paths
    assert "skills/document-types/hara/steps/step-input-materials.md" in scanned_paths
    assert "skills/step-final-report/SKILL.md" not in scanned_paths
    assert "skills/workflow-steps/step-final-report/SKILL.md" not in scanned_paths
    assert "skills/document-types/hara/steps/step-final-report.md" not in scanned_paths


def test_active_metrics_require_task_type_and_step_when_needed(tmp_path):
    with pytest.raises(ValueError, match="task_type is required"):
        collect_context_metrics(tmp_path, mode="active-workflow")

    with pytest.raises(ValueError, match="step is required"):
        collect_context_metrics(tmp_path, mode="active-step", task_type="hara")


def test_context_metrics_cli_supports_active_step_json(tmp_path):
    write(tmp_path / "commands" / "write.md", "command\n")
    write(tmp_path / "skills" / "workflow-orchestrator" / "SKILL.md", "orchestrator\n")
    write(tmp_path / "skills" / "writing-core" / "SKILL.md", "core\n")
    write(tmp_path / "skills" / "step-input-materials" / "SKILL.md", "wrapper\n")
    write(
        tmp_path / "skills" / "workflow-steps" / "step-input-materials" / "SKILL.md",
        "canonical\n",
    )
    write(tmp_path / "skills" / "document-types" / "hara" / "SKILL.md", "hara root\n")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin.context_metrics",
            "--root",
            str(tmp_path),
            "--mode",
            "active-step",
            "--task-type",
            "hara",
            "--step",
            "step-input-materials",
            "--json",
        ],
        text=True,
        capture_output=True,
        cwd=Path(__file__).resolve().parents[1],
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "active-step"
    assert payload["task_type"] == "hara"
    assert payload["step"] == "step-input-materials"
