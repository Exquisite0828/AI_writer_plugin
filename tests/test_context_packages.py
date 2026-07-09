import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_writing_plugin.context_packages import (
    ContextPackageError,
    build_step_context_package,
    validate_step_context_package,
)
from ai_writing_plugin.input_refs import build_input_refs, write_input_refs


ROOT = Path(__file__).resolve().parents[1]
VALID_HASH = "0" * 64


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ref(path: str, digest: str = VALID_HASH) -> dict:
    return {"path": path, "sha256": digest}


def create_repo_and_run(tmp_path: Path, *, include_doc_type: bool = True):
    repo_root = tmp_path / "repo"
    run_dir = tmp_path / "runs" / "demo-run"

    write(repo_root / "skills" / "step-input-materials" / "SKILL.md", "wrapper")
    write(
        repo_root / "skills" / "workflow-steps" / "step-input-materials" / "SKILL.md",
        "canonical",
    )
    if include_doc_type:
        write(repo_root / "skills" / "document-types" / "hara" / "SKILL.md", "doctype")
        write(
            repo_root
            / "skills"
            / "document-types"
            / "hara"
            / "steps"
            / "step-input-materials.md",
            "overlay",
        )

    write(run_dir / "task_brief.json", '{"task_type":"hara"}')
    task_path = repo_root / "examples" / "hara_minimal" / "task.yaml"
    source_path = repo_root / "examples" / "hara_minimal" / "inputs" / "source.md"
    write(task_path, "task_type: hara\n")
    write(source_path, "source")
    write_input_refs(
        run_dir,
        build_input_refs(
            run_id="demo-run",
            task_path=task_path,
            task={"task_type": "hara", "inputs": [{"path": "inputs/source.md", "role": "source"}]},
            repo_root=repo_root,
        ),
    )
    write(run_dir / "inputs" / "upstream.json", '{"ok":true}')
    return repo_root, run_dir


def valid_package(**overrides):
    payload = {
        "kind": "step_context_package",
        "schema_version": 1,
        "run_id": "demo-run",
        "stage": "ingest",
        "step": "step-input-materials",
        "task_type": "hara",
        "created_at": "2026-07-08T00:00:00+00:00",
        "instruction_refs": [
            ref("skills/step-input-materials/SKILL.md"),
            ref("skills/workflow-steps/step-input-materials/SKILL.md"),
        ],
        "input_refs_ref": ref("input_refs.json"),
        "run_refs": [ref("task_brief.json")],
        "result_paths": {
            "step_result": "orchestration/step_results/step-input-materials.json",
            "review_result": "orchestration/review_results/ingest/step-input-materials.json",
        },
        "constraints": {
            "paths_and_hashes_only": True,
            "no_artifact_body": True,
            "no_input_body": True,
            "no_inline_instructions": True,
        },
    }
    payload.update(overrides)
    return payload


def assert_invalid(payload, expected_message: str, **kwargs):
    with pytest.raises(ContextPackageError, match=expected_message):
        validate_step_context_package(payload, **kwargs)


def test_build_step_context_package_writes_canonical_package_with_hashes(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)

    payload = build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        task_type="hara",
        input_refs=["inputs/upstream.json"],
    )

    package_path = (
        run_dir
        / "orchestration"
        / "context_packages"
        / "ingest"
        / "step-input-materials.json"
    )
    assert package_path.is_file()
    assert read_json(package_path) == payload
    assert payload["run_id"] == "demo-run"
    assert [item["path"] for item in payload["instruction_refs"]] == [
        "skills/step-input-materials/SKILL.md",
        "skills/workflow-steps/step-input-materials/SKILL.md",
        "skills/document-types/hara/SKILL.md",
        "skills/document-types/hara/steps/step-input-materials.md",
    ]
    assert [item["path"] for item in payload["run_refs"]] == [
        "task_brief.json",
        "inputs/upstream.json",
    ]
    assert payload["input_refs_ref"] == {
        "path": "input_refs.json",
        "sha256": hashlib.sha256((run_dir / "input_refs.json").read_bytes()).hexdigest(),
    }
    assert all(len(item["sha256"]) == 64 for item in payload["instruction_refs"])
    assert all(len(item["sha256"]) == 64 for item in payload["run_refs"])
    assert validate_step_context_package(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload


def test_build_step_context_package_keeps_document_type_refs_lazy_and_task_scoped(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)
    write(
        repo_root / "skills" / "document-types" / "SoftwareArchitecture" / "SKILL.md",
        "sibling root",
    )
    write(
        repo_root
        / "skills"
        / "document-types"
        / "SoftwareArchitecture"
        / "steps"
        / "step-input-materials.md",
        "sibling overlay",
    )

    payload = build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        task_type="hara",
    )

    instruction_paths = {item["path"] for item in payload["instruction_refs"]}
    assert "skills/document-types/hara/SKILL.md" in instruction_paths
    assert "skills/document-types/hara/steps/step-input-materials.md" in instruction_paths
    assert all(
        not path.startswith("skills/document-types/SoftwareArchitecture/")
        for path in instruction_paths
    )


def test_missing_document_type_skill_or_overlay_does_not_fail(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path, include_doc_type=False)

    payload = build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        task_type="hara",
    )

    assert [item["path"] for item in payload["instruction_refs"]] == [
        "skills/step-input-materials/SKILL.md",
        "skills/workflow-steps/step-input-materials/SKILL.md",
    ]


@pytest.mark.parametrize(
    "field",
    ["content", "text", "artifact_body", "instructions", "canonical_text", "extra"],
)
def test_rejects_unknown_or_body_like_fields(field):
    payload = valid_package()
    payload[field] = "large changing body"

    assert_invalid(payload, "unexpected fields")


@pytest.mark.parametrize(
    "override, message",
    [
        ({"stage": "unknown"}, "invalid stage"),
        ({"step": "step-not-real"}, "invalid step"),
        ({"task_type": ""}, "task_type"),
        ({"constraints": {"paths_and_hashes_only": True}}, "constraints"),
        ({"result_paths": {"step_result": "x.json"}}, "result_paths"),
    ],
)
def test_rejects_invalid_scalar_or_fixed_fields(override, message):
    assert_invalid(valid_package(**override), message)


@pytest.mark.parametrize(
    "bad_ref, message",
    [
        (ref("/absolute.md"), "relative POSIX path"),
        (ref("../outside.md"), "must not contain '..'"),
        (ref("docs/maintainers/PLAN.md"), "instruction_refs path is not allowed"),
        (ref("examples/demo/task.yaml"), "instruction_refs path is not allowed"),
        (ref("contracts/CURRENT_ARTIFACT_CONTRACTS.md"), "instruction_refs path is not allowed"),
        (ref("commands/write.md"), "instruction_refs path is not allowed"),
    ],
)
def test_rejects_instruction_refs_outside_runtime_instruction_boundary(bad_ref, message):
    payload = valid_package(instruction_refs=[bad_ref])

    assert_invalid(payload, message)


@pytest.mark.parametrize(
    "bad_ref, message",
    [
        (ref("/absolute.json"), "relative POSIX path"),
        (ref("../outside.json"), "must not contain '..'"),
        (ref("plans\\outline.json"), "must use POSIX separators"),
        (ref("runs/demo-run/task_brief.json"), "must not start with runs/"),
        (ref("examples/demo/task.yaml"), "outside runtime result boundary"),
        (ref("docs/maintainers/PLAN.md"), "outside runtime result boundary"),
        (ref("contracts/CURRENT_ARTIFACT_CONTRACTS.md"), "outside runtime result boundary"),
    ],
)
def test_rejects_run_refs_outside_run_boundary(bad_ref, message):
    payload = valid_package(run_refs=[bad_ref])

    assert_invalid(payload, message)


def test_repo_and_run_validation_require_existing_files_and_matching_hashes(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path, include_doc_type=False)

    payload = valid_package(
        instruction_refs=[
            ref(
                "skills/step-input-materials/SKILL.md",
                sha256_text("wrapper"),
            ),
            ref(
                "skills/workflow-steps/step-input-materials/SKILL.md",
                sha256_text("canonical"),
            ),
        ],
        input_refs_ref=ref("input_refs.json", sha256_file(run_dir / "input_refs.json")),
        run_refs=[ref("task_brief.json", sha256_text('{"task_type":"hara"}'))],
    )

    assert validate_step_context_package(
        payload,
        repo_root=repo_root,
        run_dir=run_dir,
    ) == payload

    missing = valid_package(
        instruction_refs=[
            ref("skills/step-input-materials/SKILL.md", sha256_text("wrapper"))
        ],
        input_refs_ref=ref("input_refs.json", sha256_file(run_dir / "input_refs.json")),
        run_refs=[ref("missing.json")],
    )
    assert_invalid(missing, "run ref does not exist", repo_root=repo_root, run_dir=run_dir)

    wrong_hash = valid_package(
        instruction_refs=[ref("skills/step-input-materials/SKILL.md", VALID_HASH)],
        input_refs_ref=ref("input_refs.json", sha256_file(run_dir / "input_refs.json")),
        run_refs=[ref("task_brief.json", sha256_text('{"task_type":"hara"}'))],
    )
    assert_invalid(wrong_hash, "instruction ref sha256 mismatch", repo_root=repo_root)

    missing_input_refs = valid_package(
        instruction_refs=[
            ref("skills/step-input-materials/SKILL.md", sha256_text("wrapper"))
        ],
        input_refs_ref=ref("missing.json"),
        run_refs=[ref("task_brief.json", sha256_text('{"task_type":"hara"}'))],
    )
    assert_invalid(
        missing_input_refs,
        "run ref does not exist",
        repo_root=repo_root,
        run_dir=run_dir,
    )


def test_build_cli_writes_package_and_respects_overwrite(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path)

    command = [
        sys.executable,
        "-m",
        "ai_writing_plugin",
        "build-step-context-package",
        "--repo-root",
        str(repo_root),
        "--run-dir",
        str(run_dir),
        "--stage",
        "ingest",
        "--step",
        "step-input-materials",
        "--task-type",
        "hara",
        "--input-ref",
        "inputs/upstream.json",
    ]

    first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert first.returncode == 0, first.stderr
    package_path = run_dir / "orchestration/context_packages/ingest/step-input-materials.json"
    assert first.stdout.strip() == str(package_path)
    assert package_path.is_file()

    second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    assert second.returncode == 2
    assert "context package already exists" in second.stderr

    overwrite = subprocess.run(
        command + ["--overwrite"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert overwrite.returncode == 0, overwrite.stderr


def test_validate_cli_accepts_valid_package_and_rejects_invalid_package(tmp_path):
    repo_root, run_dir = create_repo_and_run(tmp_path, include_doc_type=False)
    payload = build_step_context_package(
        repo_root=repo_root,
        run_dir=run_dir,
        stage="ingest",
        step="step-input-materials",
        task_type="hara",
    )
    package_path = run_dir / "orchestration/context_packages/ingest/step-input-materials.json"

    valid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-step-context-package",
            "--path",
            str(package_path),
            "--repo-root",
            str(repo_root),
            "--run-dir",
            str(run_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert valid.returncode == 0, valid.stderr
    assert valid.stdout.strip() == "step context package valid"

    payload["stage"] = "unknown"
    package_path.write_text(json.dumps(payload), encoding="utf-8")
    invalid = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "validate-step-context-package",
            "--path",
            str(package_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert invalid.returncode == 2
    assert "invalid stage" in invalid.stderr
