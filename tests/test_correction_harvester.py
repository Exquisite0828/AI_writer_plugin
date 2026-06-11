import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.corrections.harvester import CorrectionHarvestError, harvest_corrections


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "corrections"


def test_harvester_reads_yaml_json_and_jsonl_and_writes_run_artifacts(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    yaml_input = FIXTURES / "valid_add_critical_claim.yaml"
    json_input = tmp_path / "correction.json"
    jsonl_input = tmp_path / "corrections.jsonl"
    event = yaml.safe_load(yaml_input.read_text(encoding="utf-8"))
    json_input.write_text(json.dumps(event, indent=2), encoding="utf-8")
    jsonl_input.write_text(json.dumps(event) + "\n", encoding="utf-8")

    outputs = []
    for input_path in [yaml_input, json_input, jsonl_input]:
        run_dir = tmp_path / f"run-{input_path.suffix.strip('.') or 'yaml'}"
        outputs.append(harvest_corrections(run_dir=run_dir, corrections_path=input_path, profile_path=profile_path))
        events_path = run_dir / "trace" / "correction_events.jsonl"
        assert events_path == outputs[-1]["correction_events_path"]
        records = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        assert len(records) == 1
        assert records[0]["profile_id"] == "customer_demo.custom_technical_note"
        assert (run_dir / "learning" / "candidate_profile_patch.yaml").exists()
        assert (run_dir / "learning" / "candidate_eval_case.json").exists()
        assert (run_dir / "learning" / "profile_promotion_report.json").exists()
        assert (run_dir / "learning" / "profile_promotion_report.md").exists()

    assert [outputs[0]["events"][0]] == [outputs[1]["events"][0]] == [outputs[2]["events"][0]]


def test_harvester_fails_explicitly_on_parse_failure(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("corrections: [", encoding="utf-8")

    with pytest.raises(CorrectionHarvestError, match="parse"):
        harvest_corrections(run_dir=tmp_path / "run", corrections_path=invalid, profile_path=profile_path)


def test_harvester_does_not_silently_skip_invalid_events(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    mixed = tmp_path / "mixed.yaml"
    valid = yaml.safe_load((FIXTURES / "valid_add_critical_claim.yaml").read_text(encoding="utf-8"))
    invalid = yaml.safe_load((FIXTURES / "invalid_missing_value.yaml").read_text(encoding="utf-8"))
    mixed.write_text(yaml.safe_dump([valid, invalid], sort_keys=False), encoding="utf-8")

    with pytest.raises(CorrectionHarvestError, match="value"):
        harvest_corrections(run_dir=tmp_path / "run", corrections_path=mixed, profile_path=profile_path)

    assert not (tmp_path / "run" / "trace" / "correction_events.jsonl").exists()


def test_correction_harvest_cli_smoke(tmp_path: Path) -> None:
    profile_path = copy_profile(tmp_path)
    run_dir = tmp_path / "cli-run"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "correction-harvest",
            "--run-dir",
            str(run_dir),
            "--corrections",
            str(FIXTURES / "valid_add_critical_claim.yaml"),
            "--profile",
            str(profile_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (run_dir / "trace" / "correction_events.jsonl").exists()
    report = json.loads((run_dir / "learning" / "profile_promotion_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "blocked_pending_eval_or_approval"


def copy_profile(tmp_path: Path) -> Path:
    profile_path = tmp_path / "document_profile.yaml"
    shutil.copyfile(FIXTURES / "external_profile_base.yaml", profile_path)
    return profile_path

