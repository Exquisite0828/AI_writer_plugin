import json
import subprocess
import sys
from pathlib import Path

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
