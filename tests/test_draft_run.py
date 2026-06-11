import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_5_ARTIFACTS = {
    "draft/full_draft.md",
}

LATER_PHASE_PATHS = [
    "review",
    "verify",
    "revised",
    "final",
    "trace",
    "learning",
    "revision_plan.json",
]

FORBIDDEN_ROOT_ENTRIES = [
    "schemas",
    "scripts",
    "agents",
    "plugin.json",
]

FORBIDDEN_FINAL_PHRASES = [
    "ASIL A",
    "ASIL B",
    "ASIL C",
    "ASIL D",
    "final ASIL",
    "final rating",
    "risk is acceptable",
    "final HARA conclusion",
    "final professional conclusion is made",
]


def ingest_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import ingest_run

    return ingest_run(task_file=task_path, runs_dir=runs_dir)


def outline_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import outline_run

    return outline_run(run_dir=run_dir)


def evidence_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import evidence_run

    return evidence_run(run_dir=run_dir)


def plan_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import plan_run

    return plan_run(run_dir=run_dir)


def draft_run(run_dir: Path) -> Path:
    import ai_writing_plugin.run_manager as run_manager

    runner = getattr(run_manager, "draft_run", None)
    assert runner is not None, "draft_run is not implemented"
    return runner(run_dir=run_dir)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(f"{json.dumps(data, ensure_ascii=False, indent=2)}\n", encoding="utf-8")


def run_phase_3_fixture(tmp_path: Path) -> Path:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    outline_run(run_dir)
    evidence_run(run_dir)
    return run_dir


def run_phase_4_fixture(tmp_path: Path) -> Path:
    run_dir = run_phase_3_fixture(tmp_path)
    plan_run(run_dir)
    return run_dir


def run_phase_5_fixture(tmp_path: Path) -> Path:
    run_dir = run_phase_4_fixture(tmp_path)
    draft_run(run_dir)
    return run_dir


def citation_plan(run_dir: Path) -> dict:
    return read_json(run_dir / "plans" / "citation_plan.json")


def section_tasks(run_dir: Path) -> dict:
    return read_json(run_dir / "plans" / "section_tasks.json")


def citation_sections_by_id(run_dir: Path) -> dict[str, dict]:
    return {section["section_id"]: section for section in citation_plan(run_dir)["sections"]}


def task_draft_path(run_dir: Path, task: dict) -> Path:
    return run_dir / task["future_output_path"]


def all_draft_text(run_dir: Path) -> str:
    texts = [(run_dir / "draft" / "full_draft.md").read_text(encoding="utf-8")]
    for task in section_tasks(run_dir)["tasks"]:
        texts.append(task_draft_path(run_dir, task).read_text(encoding="utf-8"))
    return "\n".join(texts)


def extract_evidence_ids(text: str) -> set[str]:
    return set(re.findall(r"\bEVD-\d{3}\b", text))


def test_draft_run_creates_phase_5_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    tasks = section_tasks(run_dir)["tasks"]

    assert (run_dir / "draft" / "full_draft.md").exists()
    for task in tasks:
        assert task_draft_path(run_dir, task).exists()


def test_draft_run_updates_manifest_to_phase_5(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]
    task_paths = {task["future_output_path"] for task in section_tasks(run_dir)["tasks"]}

    assert manifest["phase"] == "phase_5"
    assert manifest["status"] == "drafted"
    assert task_paths <= set(artifact_paths)
    assert PHASE_5_ARTIFACTS <= set(artifact_paths)
    assert len(artifact_paths) == len(set(artifact_paths))


def test_every_section_task_has_required_markdown_sections(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)

    for task in section_tasks(run_dir)["tasks"]:
        draft_text = task_draft_path(run_dir, task).read_text(encoding="utf-8")
        assert draft_text.startswith(f"# {task['section_title']}\n")
        assert f"Task id: {task['task_id']}" in draft_text
        assert f"Section id: {task['section_id']}" in draft_text
        assert "Draft status: conservative_draft" in draft_text
        assert "Future review required: true" in draft_text
        assert "## 来源支持" in draft_text
        assert "## 草稿正文" in draft_text
        assert "## NEEDS_USER_CONFIRMATION" in draft_text
        assert "## 限制和开放问题" in draft_text
        assert "## 草稿边界说明" in draft_text


def test_full_draft_contains_sections_in_task_order_and_boundary_note(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    full_draft = (run_dir / "draft" / "full_draft.md").read_text(encoding="utf-8")
    tasks = section_tasks(run_dir)["tasks"]

    assert full_draft.startswith("# HARA 危害分析报告保守草稿\n")
    assert "Draft status: conservative_draft" in full_draft
    assert "Source: section_tasks.json + citation_plan.json" in full_draft
    assert "Not final: true" in full_draft
    assert "## 全局草稿边界说明" in full_draft
    assert "这是保守草稿。" in full_draft
    assert "仅使用 citation_plan.json 和 section_tasks.json 中允许的证据" in full_draft
    assert "不会形成最终 HARA professional judgments" in full_draft
    assert "sample 和 expected-output-shape 材料不是事实证据" in full_draft
    assert "## 目录" in full_draft
    assert "## 全局开放问题和必需确认" in full_draft
    assert "## 阶段边界说明" in full_draft

    positions = [full_draft.index(f"# {task['section_title']}") for task in tasks]
    assert positions == sorted(positions)


def test_draft_run_requires_phase_4_run(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "draft-run requires a writing-planned Phase 4 run" in result.stderr
    assert not (run_dir / "draft").exists()


def test_draft_run_fails_when_section_tasks_missing(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    (run_dir / "plans" / "section_tasks.json").unlink()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "section_tasks is required" in result.stderr
    assert not (run_dir / "draft").exists()


def test_draft_run_fails_when_citation_plan_missing(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    (run_dir / "plans" / "citation_plan.json").unlink()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "citation_plan is required for conservative drafting" in result.stderr
    assert not (run_dir / "draft").exists()


def test_draft_run_fails_when_source_index_missing(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    (run_dir / "knowledge" / "source_index.json").unlink()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "source_index is required for source support traceability" in result.stderr
    assert not (run_dir / "draft").exists()


def test_draft_only_uses_allowed_evidence_ids(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)

    for task in section_tasks(run_dir)["tasks"]:
        draft_text = task_draft_path(run_dir, task).read_text(encoding="utf-8")
        assert extract_evidence_ids(draft_text) <= set(task["allowed_evidence"])


def test_allowed_evidence_is_listed_in_source_support(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)

    for task in section_tasks(run_dir)["tasks"]:
        draft_text = task_draft_path(run_dir, task).read_text(encoding="utf-8")
        source_support = draft_text.split("## 来源支持", maxsplit=1)[1].split("## 草稿正文", maxsplit=1)[0]
        if task["allowed_evidence"]:
            for evidence_id in task["allowed_evidence"]:
                assert evidence_id in source_support
        else:
            assert "本章节没有可用的 allowed evidence。" in source_support


def test_sample_and_expected_output_shape_are_not_used_as_factual_support(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    draft_text = all_draft_text(run_dir)

    assert "sample |" not in draft_text
    assert "expected_output_shape |" not in draft_text
    assert "facts from sample" not in draft_text
    assert "facts from expected_output_shape" not in draft_text


def test_reference_evidence_is_marked_as_methodology_or_context(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    citation_sections = citation_sections_by_id(run_dir)
    reference_ids = {
        detail["evidence_id"]
        for section in citation_sections.values()
        for detail in section["evidence_details"]
        if detail["source_role"] == "reference"
    }

    assert reference_ids
    draft_text = all_draft_text(run_dir)
    for evidence_id in reference_ids:
        assert f"{evidence_id}" in draft_text
    assert "reference evidence 仅用于方法、背景或弱支持，不能作为项目事实。" in draft_text


def test_hara_sensitive_sections_include_confirmation_markers(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    sensitive_tasks = [
        task
        for task in section_tasks(run_dir)["tasks"]
        if any(marker in task["section_title"].lower() for marker in ["hazard", "hazardous", "rating", "s/e/c", "asil", "safety goal"])
    ]

    assert sensitive_tasks
    for task in sensitive_tasks:
        draft_text = task_draft_path(run_dir, task).read_text(encoding="utf-8")
        assert "NEEDS_USER_CONFIRMATION" in draft_text
        assert "pending" in draft_text
        assert "不会形成最终 HARA professional judgment" in draft_text


def test_sec_rating_table_uses_pending_rating_markers(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    rating_task = next(task for task in section_tasks(run_dir)["tasks"] if "S/E/C" in task["section_title"])
    draft_text = task_draft_path(run_dir, rating_task).read_text(encoding="utf-8")

    assert "S?" in draft_text
    assert "E?" in draft_text
    assert "C?" in draft_text
    assert "TBD" in draft_text
    assert "NEEDS_USER_CONFIRMATION" in draft_text


def test_unsupported_task_generates_conservative_stub(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    tasks_path = run_dir / "plans" / "section_tasks.json"
    tasks_artifact = section_tasks(run_dir)
    tasks_artifact["tasks"][0]["allowed_evidence"] = []
    tasks_artifact["tasks"][0]["evidence_status"] = "unsupported"
    tasks_artifact["tasks"][0]["writing_mode"] = "unsupported_stub"
    tasks_artifact["tasks"][0]["requires_human_confirmation"] = True
    tasks_artifact["tasks"][0]["confirmation_markers"] = ["NEEDS_USER_CONFIRMATION"]
    write_json(tasks_path, tasks_artifact)

    draft_run(run_dir)

    draft_text = task_draft_path(run_dir, tasks_artifact["tasks"][0]).read_text(encoding="utf-8")
    assert "本章节没有可用的 allowed evidence。" in draft_text
    assert "NEEDS_USER_CONFIRMATION" in draft_text
    assert "不足以将本章节写成事实结论" in draft_text
    assert "不会输出缺少支持的专业结论" in draft_text


def test_weak_task_uses_conservative_candidate_language(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    tasks_path = run_dir / "plans" / "section_tasks.json"
    tasks_artifact = section_tasks(run_dir)
    task = next(task for task in tasks_artifact["tasks"] if task["allowed_evidence"])
    task["evidence_status"] = "weak"
    task["writing_mode"] = "conservative_candidate"
    task["requires_human_confirmation"] = True
    task["confirmation_markers"] = ["NEEDS_USER_CONFIRMATION"]
    write_json(tasks_path, tasks_artifact)

    draft_run(run_dir)

    draft_text = task_draft_path(run_dir, task).read_text(encoding="utf-8")
    assert "候选" in draft_text
    assert "有限支持" in draft_text
    assert "NEEDS_USER_CONFIRMATION" in draft_text


def test_open_issues_carry_unresolved_and_gap_notes(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    full_draft = (run_dir / "draft" / "full_draft.md").read_text(encoding="utf-8")

    assert "## 全局开放问题和必需确认" in full_draft
    assert "继续带入的知识缺口" in full_draft
    assert "继续带入的未解决问题" in full_draft
    assert "UNS-" in full_draft or "weak evidence" in full_draft


def test_full_draft_summarizes_required_confirmations(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    full_draft = (run_dir / "draft" / "full_draft.md").read_text(encoding="utf-8")
    confirmation_tasks = [task for task in section_tasks(run_dir)["tasks"] if task["requires_human_confirmation"]]

    assert confirmation_tasks
    for task in confirmation_tasks:
        assert f"{task['task_id']} | {task['section_id']} | {task['section_title']} | pending" in full_draft


def test_draft_run_does_not_generate_phase_6_plus_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)

    for relative_path in LATER_PHASE_PATHS:
        assert not (run_dir / relative_path).exists()


def test_repeated_draft_run_does_not_duplicate_manifest_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    draft_run(run_dir)
    draft_run(run_dir)

    artifact_paths = [artifact["path"] for artifact in read_json(run_dir / "manifest.json")["artifacts"]]
    for task in section_tasks(run_dir)["tasks"]:
        assert artifact_paths.count(task["future_output_path"]) == 1
    assert artifact_paths.count("draft/full_draft.md") == 1


def test_draft_run_cli_success(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "保守草稿已完成" in result.stdout
    assert "draft/full_draft.md" in result.stdout


def test_empty_allowed_evidence_does_not_fabricate_evidence(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    tasks_path = run_dir / "plans" / "section_tasks.json"
    tasks_artifact = section_tasks(run_dir)
    tasks_artifact["tasks"][0]["allowed_evidence"] = []
    write_json(tasks_path, tasks_artifact)

    draft_run(run_dir)

    draft_text = task_draft_path(run_dir, tasks_artifact["tasks"][0]).read_text(encoding="utf-8")
    assert "本章节没有可用的 allowed evidence。" in draft_text
    assert not extract_evidence_ids(draft_text)


def test_invalid_output_path_outside_draft_fails(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    tasks_path = run_dir / "plans" / "section_tasks.json"
    tasks_artifact = section_tasks(run_dir)
    tasks_artifact["tasks"][0]["future_output_path"] = "../outside.md"
    write_json(tasks_path, tasks_artifact)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "invalid draft output path" in result.stderr
    assert not (run_dir / "outside.md").exists()
    assert not (run_dir.parent / "outside.md").exists()


def test_empty_section_tasks_fails_without_empty_draft(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    tasks_path = run_dir / "plans" / "section_tasks.json"
    tasks_artifact = section_tasks(run_dir)
    tasks_artifact["tasks"] = []
    tasks_artifact["summary"]["total_tasks"] = 0
    write_json(tasks_path, tasks_artifact)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "draft-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "no section tasks available for drafting" in result.stderr
    assert not (run_dir / "draft").exists()


def test_draft_run_does_not_create_forbidden_root_directories() -> None:
    for entry in FORBIDDEN_ROOT_ENTRIES:
        assert not (REPO_ROOT / entry).exists()


def test_draft_body_avoids_final_hara_conclusion_phrases(tmp_path: Path) -> None:
    run_dir = run_phase_5_fixture(tmp_path)
    draft_text = all_draft_text(run_dir)

    for phrase in FORBIDDEN_FINAL_PHRASES:
        assert phrase not in draft_text
