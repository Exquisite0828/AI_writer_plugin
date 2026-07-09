import hashlib
import json
from pathlib import Path

import pytest

from ai_writing_plugin.input_refs import (
    InputRefsError,
    build_input_refs,
    input_refs_path,
    validate_input_refs,
    write_input_refs,
)


BODY_KEYS = ("body", "content", "text", "excerpt", "full_text", "raw")


def write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_config(inputs=None):
    payload = {
        "task_type": "hara",
        "task_title": "Demo",
    }
    if inputs is not None:
        payload["inputs"] = inputs
    return payload


def create_repo_task(tmp_path: Path):
    repo_root = tmp_path / "repo"
    task_path = repo_root / "examples" / "hara_minimal" / "task.yaml"
    source_path = repo_root / "examples" / "hara_minimal" / "inputs" / "source.md"
    write(task_path, "task_type: hara\n")
    write(source_path, "fact source body that must not be copied")
    return repo_root, task_path, source_path


def assert_no_body_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in BODY_KEYS
            assert_no_body_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_no_body_keys(nested)


def assert_no_dynamic_time_keys(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            assert key not in {"timestamp", "created_at", "updated_at"}
            assert_no_dynamic_time_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            assert_no_dynamic_time_keys(nested)


def test_build_input_refs_records_paths_hashes_sizes_without_bodies(tmp_path):
    repo_root, task_path, source_path = create_repo_task(tmp_path)

    payload = build_input_refs(
        run_id="demo-run",
        task_path=task_path,
        task=task_config(
            inputs=[
                {
                    "path": "inputs/source.md",
                    "role": "source",
                }
            ]
        ),
        repo_root=repo_root,
    )

    assert payload["schema_version"] == "input_refs.v1"
    assert payload["run_id"] == "demo-run"
    assert payload["constraints"]["paths_and_hashes_only"] is True
    assert payload["constraints"]["no_inline_body"] is True
    assert payload["task_ref"] == {
        "path": "examples/hara_minimal/task.yaml",
        "path_kind": "repo_relative",
        "sha256": sha256_file(task_path),
        "size_bytes": task_path.stat().st_size,
        "role": "task",
        "read_policy": "metadata_only",
        "fact_source_allowed": False,
    }
    assert payload["input_materials"] == [
        {
            "material_id": "input-001",
            "role": "source",
            "path": "examples/hara_minimal/inputs/source.md",
            "path_kind": "repo_relative",
            "sha256": sha256_file(source_path),
            "size_bytes": source_path.stat().st_size,
            "mime_type": "text/markdown",
            "read_policy": "summary_only",
            "fact_source_allowed": False,
            "selected_by": "task",
        }
    ]
    assert "fact source body" not in json.dumps(payload, ensure_ascii=False)
    assert_no_body_keys(payload)
    assert validate_input_refs(payload, repo_root=repo_root) == payload


def test_write_input_refs_uses_stable_path_and_deterministic_json(tmp_path):
    repo_root, task_path, _ = create_repo_task(tmp_path)
    run_dir = tmp_path / "runs" / "demo-run"
    payload = build_input_refs(
        run_id="demo-run",
        task_path=task_path,
        task=task_config(inputs=[]),
        repo_root=repo_root,
    )

    first = write_input_refs(run_dir, payload)
    first_text = first.read_text(encoding="utf-8")
    second = write_input_refs(run_dir, payload, overwrite=True)
    second_text = second.read_text(encoding="utf-8")

    assert first == input_refs_path(run_dir)
    assert second == first
    assert first_text == second_text
    assert_no_dynamic_time_keys(payload)


def test_validate_input_refs_fails_on_hash_mismatch(tmp_path):
    repo_root, task_path, _ = create_repo_task(tmp_path)
    payload = build_input_refs(
        run_id="demo-run",
        task_path=task_path,
        task=task_config(inputs=[]),
        repo_root=repo_root,
    )
    payload["task_ref"]["sha256"] = "0" * 64

    with pytest.raises(InputRefsError, match="sha256 mismatch"):
        validate_input_refs(payload, repo_root=repo_root)


def test_build_input_refs_fails_on_missing_input_file(tmp_path):
    repo_root, task_path, _ = create_repo_task(tmp_path)

    with pytest.raises(InputRefsError, match="input material does not exist"):
        build_input_refs(
            run_id="demo-run",
            task_path=task_path,
            task=task_config(inputs=[{"path": "inputs/missing.md", "role": "source"}]),
            repo_root=repo_root,
        )


def test_sample_and_expected_output_paths_cannot_be_fact_sources(tmp_path):
    repo_root = tmp_path / "repo"
    task_path = repo_root / "task.yaml"
    expected_path = repo_root / "expected_outputs" / "sample.md"
    write(task_path, "task_type: hara\n")
    write(expected_path, "sample output")

    payload = build_input_refs(
        run_id="demo-run",
        task_path=task_path,
        task=task_config(
            inputs=[
                {
                    "path": "expected_outputs/sample.md",
                    "role": "sample",
                    "fact_source_allowed": True,
                }
            ]
        ),
        repo_root=repo_root,
    )

    material = payload["input_materials"][0]
    assert material["role"] == "sample"
    assert material["fact_source_allowed"] is False
    assert material["read_policy"] == "summary_only"

    material["fact_source_allowed"] = True
    with pytest.raises(InputRefsError, match="sample/example/expected-output"):
        validate_input_refs(payload, repo_root=repo_root)


def test_examples_are_not_bulk_read_when_no_inputs_declared(tmp_path):
    repo_root = tmp_path / "repo"
    task_path = repo_root / "task.yaml"
    unselected = repo_root / "examples" / "unselected" / "large.md"
    write(task_path, "task_type: hara\n")
    write(unselected, "SECRET_EXAMPLE_BODY_SHOULD_NOT_APPEAR")

    payload = build_input_refs(
        run_id="demo-run",
        task_path=task_path,
        task=task_config(),
        repo_root=repo_root,
    )

    assert payload["input_materials"] == []
    assert payload["warnings"] == [
        "no explicit input materials declared; input_materials is empty"
    ]
    assert "SECRET_EXAMPLE_BODY_SHOULD_NOT_APPEAR" not in json.dumps(
        payload,
        ensure_ascii=False,
    )


def test_glob_material_paths_are_invalid(tmp_path):
    repo_root, task_path, _ = create_repo_task(tmp_path)

    with pytest.raises(InputRefsError, match="glob patterns are not allowed"):
        build_input_refs(
            run_id="demo-run",
            task_path=task_path,
            task=task_config(inputs=[{"path": "examples/**/*.md", "role": "source"}]),
            repo_root=repo_root,
        )


def test_missing_role_is_conservative_and_warns(tmp_path):
    repo_root, task_path, source_path = create_repo_task(tmp_path)

    payload = build_input_refs(
        run_id="demo-run",
        task_path=task_path,
        task=task_config(inputs=[{"path": "inputs/source.md"}]),
        repo_root=repo_root,
    )

    assert payload["input_materials"][0]["path"] == (
        source_path.relative_to(repo_root).as_posix()
    )
    assert payload["input_materials"][0]["role"] == "other"
    assert payload["input_materials"][0]["read_policy"] == "summary_only"
    assert payload["input_materials"][0]["fact_source_allowed"] is False
    assert payload["warnings"] == [
        "input material inputs/source.md has no role; using role=other and summary_only"
    ]
