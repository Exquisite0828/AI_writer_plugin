import json
from pathlib import Path

from ai_writing_plugin.context_telemetry import build_context_telemetry


ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_context_telemetry_schema_contains_required_top_level_fields():
    report = build_context_telemetry(
        ROOT,
        task_type="hara",
        step="step-evidence-map",
        largest_limit=5,
    )

    assert set(report) >= {
        "schema_version",
        "root",
        "measurement_status",
        "measurements",
        "budgets",
        "largest_runtime_files",
        "runtime_boundary",
        "cache_metrics",
        "overall_status",
    }
    assert report["schema_version"] == "context_telemetry.v1"
    assert report["measurement_status"] == "estimated_static_analysis"
    assert report["root"] == "."
    assert report["overall_status"] == "pass"


def test_context_telemetry_reports_required_measurement_scopes():
    report = build_context_telemetry(ROOT, task_type="hara", step="step-evidence-map")

    measurements = report["measurements"]
    assert measurements["total_runtime_surface"]["estimated_tokens"] > 0
    assert measurements["total_runtime_surface"]["file_count"] > 0
    assert measurements["active_workflow"]["task_type"] == "hara"
    assert measurements["active_workflow"]["estimated_tokens"] > 0
    assert measurements["active_step"]["task_type"] == "hara"
    assert measurements["active_step"]["step"] == "step-evidence-map"
    assert measurements["active_step"]["estimated_tokens"] > 0


def test_context_telemetry_cache_metrics_are_explicitly_not_measured():
    report = build_context_telemetry(ROOT, task_type="hara", step="step-evidence-map")

    assert report["cache_metrics"] == {
        "api_cache_read_ratio": None,
        "measurement_status": "not_measured",
        "reason": "No API-level cache telemetry is available in this deterministic test harness.",
    }


def test_context_telemetry_populates_largest_runtime_files_with_relative_paths():
    report = build_context_telemetry(
        ROOT,
        task_type="hara",
        step="step-evidence-map",
        largest_limit=3,
    )

    largest = report["largest_runtime_files"]
    assert largest
    assert len(largest) == 3
    assert all(not Path(item["path"]).is_absolute() for item in largest)
    assert all(item["estimated_tokens"] > 0 for item in largest)
    assert all(item["word_count"] > 0 for item in largest)


def test_context_telemetry_records_runtime_boundary_globs():
    report = build_context_telemetry(ROOT, task_type="hara", step="step-evidence-map")

    boundary = report["runtime_boundary"]
    assert boundary["runtime_globs"] == ["commands/**/*.md", "skills/**/*.md"]
    assert boundary["forbidden_default_context_globs"] == [
        "docs/maintainers/**",
        "examples/**",
        "runs/**",
    ]
    assert boundary["artifact_body_replay_measured"] is False
    assert boundary["artifact_body_replay_status"] == "covered_by_tests"
    assert boundary["sibling_document_type_reads_measured"] is False
    assert boundary["sibling_document_type_status"] == "structurally_guarded"


def test_context_telemetry_does_not_embed_artifact_body(tmp_path):
    sentinel = "SECRET_ARTIFACT_BODY_SHOULD_NOT_APPEAR"
    write(tmp_path / "commands" / "write.md", "stable command prompt")
    write(tmp_path / "skills" / "workflow-orchestrator" / "SKILL.md", "orchestrator")
    write(tmp_path / "skills" / "writing-core" / "SKILL.md", "core")
    write(tmp_path / "skills" / "step-evidence-map" / "SKILL.md", "wrapper")
    write(tmp_path / "skills" / "workflow-steps" / "step-evidence-map" / "SKILL.md", "canonical")
    write(tmp_path / "skills" / "document-types" / "hara" / "SKILL.md", "hara")
    write(
        tmp_path / "skills" / "document-types" / "hara" / "steps" / "step-evidence-map.md",
        "overlay",
    )
    write(tmp_path / "runs" / "demo" / "artifact.md", sentinel)

    report = build_context_telemetry(
        tmp_path,
        task_type="hara",
        step="step-evidence-map",
    )

    encoded = json.dumps(report, ensure_ascii=False)
    assert sentinel not in encoded
    assert str(tmp_path) not in encoded


def test_context_telemetry_supports_software_architecture_active_step():
    report = build_context_telemetry(
        ROOT,
        task_type="SoftwareArchitecture",
        step="step-evidence-map",
    )

    active_step = report["measurements"]["active_step"]
    assert active_step["task_type"] == "SoftwareArchitecture"
    assert active_step["step"] == "step-evidence-map"
    assert active_step["estimated_tokens"] > 0
    assert report["overall_status"] == "pass"
