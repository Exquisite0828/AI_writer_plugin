import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ai_writing_plugin.document_types.profile_loader import load_document_profile_file


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "profile_specs"
VALID_SPEC = FIXTURE_DIR / "valid_generic_document_SPEC.md"

EXPECTED_PROFILE_FIELDS = {
    "profile_id",
    "profile_version",
    "task_type",
    "display_name",
    "description",
    "default_sections",
    "required_sections",
    "optional_sections",
    "critical_claims",
    "requires_human_confirmation",
    "forbidden_final_claims",
    "confirmation_marker",
    "fact_source_roles",
    "non_fact_source_roles",
    "reference_policy",
    "sample_policy",
    "default_final_status",
    "allowed_final_statuses",
    "review_focus",
    "verification_focus",
    "candidate_learning_policy",
    "terminology",
    "output_labels",
}


def generate(spec: Path, output_dir: Path, *, force: bool = False, no_skeletons: bool = False):
    from ai_writing_plugin.document_types.spec_profile_generator import generate_profile_from_spec

    return generate_profile_from_spec(
        spec_path=spec,
        output_dir=output_dir,
        force=force,
        no_skeletons=no_skeletons,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_failed(result, expected: str) -> None:
    assert not result.success
    assert any(expected in blocker for blocker in result.promotion_blockers), result.promotion_blockers
    manifest_path = result.output_dir / "candidate_manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        assert manifest["validation_status"] == "failed"
        assert manifest["status"] == "candidate"
        assert manifest["activation_status"] == "inactive"


def test_profile_from_spec_generates_candidate_profile(tmp_path: Path) -> None:
    result = generate(VALID_SPEC, tmp_path)

    assert result.success
    assert (tmp_path / "document_profile.yaml").exists()
    assert (tmp_path / "candidate_manifest.json").exists()
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "fixture_skeleton" / "task.yaml").exists()
    assert (tmp_path / "eval_skeleton" / "smoke_test_plan.md").exists()

    manifest = read_json(tmp_path / "candidate_manifest.json")
    assert manifest["phase"] == "N3"
    assert manifest["status"] == "candidate"
    assert manifest["activation_status"] == "inactive"
    assert manifest["validation_status"] == "passed"
    assert manifest["profile_task_type"] == "generic_document"
    assert manifest["profile_id"] == "candidate.generic_document"
    assert manifest["profile_version"] == "0.1.0-candidate"
    assert manifest["promotion_blockers"] == []
    assert manifest["human_review_required"] is True
    assert manifest["may_overwrite_active_profile"] is False
    assert manifest["may_modify_stable_skill"] is False


def test_generated_profile_passes_existing_profile_validation(tmp_path: Path) -> None:
    generate(VALID_SPEC, tmp_path)

    loaded = load_document_profile_file(
        tmp_path / "document_profile.yaml",
        profile_path="tests/generated/document_profile.yaml",
        expected_task_type="generic_document",
    )
    rules = loaded.to_rules()

    assert rules.task_type == "generic_document"
    assert rules.display_name == "Generic Document"
    assert "final decision recommendation" in rules.critical_claims
    assert "Sample documents may guide structure" in rules.sample_policy
    assert "Reference materials may support structure" in rules.reference_policy
    assert rules.default_final_status == "ready_for_human_review"


def test_profile_from_spec_maps_required_fields(tmp_path: Path) -> None:
    generate(VALID_SPEC, tmp_path)

    generated = yaml.safe_load((tmp_path / "document_profile.yaml").read_text(encoding="utf-8"))

    assert set(generated) == EXPECTED_PROFILE_FIELDS
    assert generated["task_type"] == "generic_document"
    assert generated["default_sections"] == [
        "Background and Scope",
        "Confirmed Source Facts",
        "Proposed Approach",
        "Risks and Open Questions",
        "Human Confirmations",
    ]
    assert generated["non_fact_source_roles"] == ["sample", "template", "checklist", "reference"]
    assert generated["terminology"]["professional_judgment"] == "generic document critical claim"


@pytest.mark.parametrize(
    ("fixture_name", "expected"),
    [
        ("missing_critical_claims_SPEC.md", "critical_claims"),
        ("missing_requires_human_confirmation_SPEC.md", "requires_human_confirmation"),
        ("missing_forbidden_final_claims_SPEC.md", "forbidden_final_claims"),
        ("missing_sample_policy_SPEC.md", "sample_policy"),
        ("missing_reference_policy_SPEC.md", "reference_policy"),
        ("missing_final_status_policy_SPEC.md", "default_final_status"),
        ("sample_as_fact_source_SPEC.md", "fact_source_roles"),
        ("unsafe_reference_policy_SPEC.md", "reference_policy"),
        ("approval_status_SPEC.md", "final status"),
        ("no_profile_block_SPEC.md", "document_profile"),
        ("multiple_profile_blocks_SPEC.md", "multiple document_profile"),
    ],
)
def test_profile_from_spec_blocks_invalid_specs(tmp_path: Path, fixture_name: str, expected: str) -> None:
    result = generate(FIXTURE_DIR / fixture_name, tmp_path / fixture_name.removesuffix(".md"))

    assert_failed(result, expected)
    assert not (result.output_dir / "document_profile.yaml").exists()


def test_profile_from_spec_refuses_active_profile_overwrite() -> None:
    result = generate(VALID_SPEC, REPO_ROOT / "profiles" / "document_types" / "generic_document.yaml")

    assert_failed(result, "active profile")


def test_profile_from_spec_does_not_write_skills_or_pipeline_files(tmp_path: Path) -> None:
    generate(VALID_SPEC, tmp_path)

    generated_paths = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")}
    assert not any(path.startswith("skills/") for path in generated_paths)
    assert not any(path.endswith("_pipeline.py") for path in generated_paths)
    assert not any(path.startswith("ai_writing_plugin/") for path in generated_paths)


def test_fixture_skeleton_contains_no_project_fact_claims(tmp_path: Path) -> None:
    generate(VALID_SPEC, tmp_path)

    task = yaml.safe_load((tmp_path / "fixture_skeleton" / "task.yaml").read_text(encoding="utf-8"))
    assert task["task_type"] == "generic_document"
    assert task["document_profile_path"] == "../document_profile.yaml"
    assert task["allow_inference"] is False
    assert {item["role"] for item in task["inputs"]} == {"source", "template", "checklist", "reference", "sample"}

    for filename in ["source.md", "template.md", "checklist.md", "reference.md", "sample.md"]:
        assert (tmp_path / "fixture_skeleton" / "inputs" / filename).exists()
    sample_text = (tmp_path / "fixture_skeleton" / "inputs" / "sample.md").read_text(encoding="utf-8").lower()
    reference_text = (tmp_path / "fixture_skeleton" / "inputs" / "reference.md").read_text(encoding="utf-8").lower()
    assert "not a fact source" in sample_text
    assert "does not prove project facts" in reference_text


def test_eval_skeleton_is_guidance_not_eval_harness(tmp_path: Path) -> None:
    generate(VALID_SPEC, tmp_path)

    assert (tmp_path / "eval_skeleton" / "README.md").exists()
    smoke_plan = tmp_path / "eval_skeleton" / "smoke_test_plan.md"
    assert smoke_plan.exists()
    assert "guidance" in smoke_plan.read_text(encoding="utf-8").lower()
    assert not (tmp_path / "ai_writing_plugin" / "eval").exists()


def test_profile_from_spec_cli_generates_candidate_profile(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "profile-from-spec",
            "--spec",
            str(VALID_SPEC),
            "--output-dir",
            str(tmp_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "document_profile.yaml").exists()
    assert (tmp_path / "candidate_manifest.json").exists()


def test_profile_from_spec_no_skeletons_option(tmp_path: Path) -> None:
    result = generate(VALID_SPEC, tmp_path, no_skeletons=True)

    assert result.success
    assert (tmp_path / "document_profile.yaml").exists()
    assert (tmp_path / "candidate_manifest.json").exists()
    assert not (tmp_path / "fixture_skeleton").exists()
    assert not (tmp_path / "eval_skeleton").exists()


def test_profile_spec_docs_exist_and_state_boundaries() -> None:
    template = REPO_ROOT / "docs" / "DOCUMENT_PROFILE_SPEC_TEMPLATE.md"
    generic_spec = REPO_ROOT / "docs" / "document_types" / "generic_document_SPEC.md"

    assert template.exists()
    assert generic_spec.exists()
    template_text = template.read_text(encoding="utf-8")
    generic_text = generic_spec.read_text(encoding="utf-8")

    for required in [
        "```yaml document_profile",
        "Markdown Spec is an upstream explanation layer",
        "sample must not be used as a fact source",
        "reference must not prove project-specific facts",
        "candidate profile must not be automatically promoted",
        "stable Skill must not be automatically overwritten",
        "human review is required",
    ]:
        assert required in template_text
    assert "```yaml document_profile" in generic_text
    assert "task_type: generic_document" in generic_text
    assert "generic_document is a general-purpose mode, not a new official L3 document type" in generic_text
