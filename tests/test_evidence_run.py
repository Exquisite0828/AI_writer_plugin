import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_3_ARTIFACTS = {
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
}

LATER_PHASE_PATHS = [
    "plans/citation_plan.json",
    "plans/claim_support_matrix.json",
    "plans/outline_final.md",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
    "draft",
    "review",
    "verify",
    "final",
    "trace",
    "learning",
]

FORBIDDEN_ROOT_ENTRIES = [
    "schemas",
    "scripts",
    "agents",
    "plugin.json",
]

ALLOWED_QUESTION_TYPES = {
    "scope",
    "input_summary",
    "hazard",
    "hazardous_event",
    "rating",
    "safety_goal",
    "open_issue",
    "general",
}

ALLOWED_STATUSES = {"supported", "weak", "unsupported"}
ALLOWED_SUPPORT_TYPES = {"direct", "methodology", "context", "weak_keyword"}
SENSITIVE_TITLE_MARKERS = ("hazard", "hazardous", "rating", "s/e/c", "asil", "safety goal", "risk")


def ingest_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import ingest_run

    return ingest_run(task_file=task_path, runs_dir=runs_dir)


def init_run(task_path: Path, runs_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import init_run

    return init_run(task_file=task_path, runs_dir=runs_dir)


def outline_run(run_dir: Path) -> Path:
    from ai_writing_plugin.run_manager import outline_run

    return outline_run(run_dir=run_dir)


def evidence_run(run_dir: Path) -> Path:
    import ai_writing_plugin.run_manager as run_manager

    runner = getattr(run_manager, "evidence_run", None)
    assert runner is not None, "evidence_run is not implemented"
    return runner(run_dir=run_dir)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_phase_2_fixture(tmp_path: Path) -> Path:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    return outline_run(run_dir)


def run_phase_3_fixture(tmp_path: Path) -> Path:
    run_dir = run_phase_2_fixture(tmp_path)
    return evidence_run(run_dir)


def make_template_only_task(tmp_path: Path, template_content: str | None) -> Path:
    fixture_dir = tmp_path / "fixture"
    input_dir = fixture_dir / "inputs"
    input_dir.mkdir(parents=True)
    if template_content is not None:
        (input_dir / "template.md").write_text(template_content, encoding="utf-8")
    task_path = fixture_dir / "task.yaml"
    task_path.write_text(
        """\
task_type: hara
task_title: Fallback HARA
target_audience: Functional Safety Engineer
output_format: markdown
strict_template: true
allow_inference: false
requires_human_confirmation:
  - hazard identification
inputs:
  - path: inputs/template.md
    role: template
    title: Local Template
""",
        encoding="utf-8",
    )
    return task_path


def inventory_by_path(run_dir: Path) -> dict[str, dict]:
    inventory = read_json(run_dir / "inputs" / "input_inventory.json")
    return {record["path"]: record for record in inventory["files"]}


def source_by_id(run_dir: Path) -> dict[str, dict]:
    source_index = read_json(run_dir / "knowledge" / "source_index.json")
    return {source["source_id"]: source for source in source_index["sources"]}


def questions_by_id(run_dir: Path) -> dict[str, dict]:
    questions = read_json(run_dir / "plans" / "research_questions.json")["questions"]
    return {question["question_id"]: question for question in questions}


def evidence_questions_by_id(run_dir: Path) -> dict[str, dict]:
    questions = read_json(run_dir / "plans" / "evidence_map.json")["questions"]
    return {question["question_id"]: question for question in questions}


def all_candidates(run_dir: Path) -> list[dict]:
    evidence_map = read_json(run_dir / "plans" / "evidence_map.json")
    return [
        candidate
        for question in evidence_map["questions"]
        for candidate in question["evidence_candidates"]
    ]


def test_evidence_run_creates_phase_3_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    assert (run_dir / "plans" / "research_questions.json").exists()
    assert (run_dir / "plans" / "evidence_map.json").exists()
    assert (run_dir / "plans" / "unresolved_questions.md").exists()


def test_evidence_run_updates_manifest_to_phase_3(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]

    assert manifest["phase"] == "phase_3"
    assert manifest["status"] == "evidence_mapped"
    assert PHASE_3_ARTIFACTS <= set(artifact_paths)
    assert "manifest.json" in artifact_paths
    assert "task_brief.json" in artifact_paths
    assert "inputs/input_inventory.json" in artifact_paths
    assert "knowledge/source_index.json" in artifact_paths
    assert "knowledge/knowledge_gaps.md" in artifact_paths
    assert "plans/template_structure.json" in artifact_paths
    assert "plans/outline_l1.md" in artifact_paths
    assert len(artifact_paths) == len(set(artifact_paths))


def test_research_questions_cover_all_outline_sections(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    research_questions = read_json(run_dir / "plans" / "research_questions.json")

    outline_section_ids = {section["section_id"] for section in template_structure["outline_sections"]}
    question_section_ids = {question["section_id"] for question in research_questions["questions"]}

    assert outline_section_ids <= question_section_ids
    assert question_section_ids <= outline_section_ids


def test_research_question_schema_fields_are_complete(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    research_questions = read_json(run_dir / "plans" / "research_questions.json")
    required_fields = {
        "question_id",
        "section_id",
        "section_title",
        "question",
        "question_type",
        "requires_human_confirmation",
        "priority",
        "expected_evidence_role",
        "status",
    }

    assert set(research_questions) == {"run_id", "generated_at", "questions", "summary", "warnings"}
    assert research_questions["questions"]
    for question in research_questions["questions"]:
        assert set(question) == required_fields
        assert question["question_id"]
        assert question["section_id"]
        assert question["section_title"]
        assert question["question"]
        assert question["question_type"] in ALLOWED_QUESTION_TYPES
        assert question["status"] in ALLOWED_STATUSES


def test_evidence_map_questions_trace_to_research_questions(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    research_questions = questions_by_id(run_dir)
    evidence_questions = evidence_questions_by_id(run_dir)

    assert set(evidence_questions) == set(research_questions)
    for question_id, evidence_question in evidence_questions.items():
        research_question = research_questions[question_id]
        assert evidence_question["section_id"] == research_question["section_id"]
        assert evidence_question["status"] == research_question["status"]
        assert evidence_question["requires_human_confirmation"] == research_question["requires_human_confirmation"]


def test_evidence_candidates_reference_existing_source_ids(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    sources = source_by_id(run_dir)

    for candidate in all_candidates(run_dir):
        source = sources[candidate["source_id"]]
        assert candidate["file_id"] == source["file_id"]
        assert candidate["source_role"] == source["source_role"]
        assert candidate["is_fact_source"] == source["is_fact_source"]


def test_sample_and_expected_output_shape_are_not_used_as_evidence(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    records = inventory_by_path(run_dir)
    forbidden_file_ids = {
        records["inputs/sample_hara.md"]["file_id"],
        records["inputs/expected_output_shape.md"]["file_id"],
    }

    for candidate in all_candidates(run_dir):
        assert candidate["file_id"] not in forbidden_file_ids
        assert candidate["source_role"] not in {"sample", "expected_output_shape"}


def test_reference_evidence_is_non_fact_source_and_not_direct_project_fact(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    for candidate in all_candidates(run_dir):
        if candidate["source_role"] == "reference":
            assert candidate["is_fact_source"] is False
            assert candidate["support_type"] in {"methodology", "context", "weak_keyword"}
            assert candidate["support_type"] != "direct"


def test_hara_confirmation_sensitive_sections_require_human_confirmation(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    evidence_questions = evidence_questions_by_id(run_dir)
    sensitive_questions = [
        question
        for question in questions_by_id(run_dir).values()
        if any(marker in question["section_title"].lower() for marker in SENSITIVE_TITLE_MARKERS)
    ]

    assert sensitive_questions
    assert {"Hazard Identification", "Hazardous Event Analysis", "S/E/C Rating Table", "Safety Goals Candidate"} <= {
        question["section_title"] for question in sensitive_questions
    }
    for question in sensitive_questions:
        assert question["requires_human_confirmation"] is True
        assert evidence_questions[question["question_id"]]["requires_human_confirmation"] is True


def test_unsupported_questions_are_written_to_unresolved_questions(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    unresolved = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")
    unsupported_questions = [
        question for question in questions_by_id(run_dir).values() if question["status"] == "unsupported"
    ]

    assert "Unsupported 问题" in unresolved
    assert unsupported_questions
    for question in unsupported_questions:
        assert question["question_id"] in unresolved


def test_weak_questions_are_written_to_unresolved_questions(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    unresolved = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")
    weak_questions = [question for question in questions_by_id(run_dir).values() if question["status"] == "weak"]

    assert "Weak evidence 问题" in unresolved
    assert weak_questions
    for question in weak_questions:
        assert question["question_id"] in unresolved


def test_human_confirmation_questions_are_written_to_unresolved_questions(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    unresolved = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")
    confirmation_questions = [
        question for question in questions_by_id(run_dir).values() if question["requires_human_confirmation"]
    ]

    assert "需要人工确认" in unresolved
    assert confirmation_questions
    for question in confirmation_questions:
        assert question["question_id"] in unresolved


def test_knowledge_gaps_are_carried_into_unresolved_questions(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    unresolved = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")

    assert "从 knowledge gaps 带入的 missing / unsupported 材料" in unresolved
    assert "missing_item_definition.md" in unresolved
    assert "unsupported_reference.pdf" in unresolved


def test_evidence_run_does_not_generate_later_phase_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    for relative_path in LATER_PHASE_PATHS:
        assert not (run_dir / relative_path).exists()


def test_evidence_run_requires_phase_2_run(tmp_path: Path) -> None:
    phase_1_run = ingest_run(FIXTURE_TASK, tmp_path / "runs")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "evidence-run",
            "--run",
            str(phase_1_run),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "evidence-run requires an outlined Phase 2 run" in result.stderr
    for relative_path in PHASE_3_ARTIFACTS:
        assert not (phase_1_run / relative_path).exists()


def test_repeated_evidence_run_does_not_duplicate_manifest_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)

    evidence_run(run_dir)
    evidence_run(run_dir)

    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]

    for artifact_path in PHASE_3_ARTIFACTS:
        assert artifact_paths.count(artifact_path) == 1


def test_evidence_run_cli_success(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "evidence-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "证据映射已完成" in result.stdout
    assert "plans/research_questions.json" in result.stdout
    assert "plans/evidence_map.json" in result.stdout
    assert "plans/unresolved_questions.md" in result.stdout


def test_evidence_run_works_with_fallback_outline(tmp_path: Path) -> None:
    task_path = make_template_only_task(tmp_path, template_content=None)
    run_dir = outline_run(ingest_run(task_path, tmp_path / "runs"))

    evidence_run(run_dir)

    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    research_questions = read_json(run_dir / "plans" / "research_questions.json")
    outline_section_ids = {section["section_id"] for section in template_structure["outline_sections"]}
    question_section_ids = {question["section_id"] for question in research_questions["questions"]}

    assert research_questions["questions"]
    assert outline_section_ids <= question_section_ids
    assert any("fallback" in warning.lower() for warning in research_questions["warnings"])


def test_evidence_run_marks_questions_unsupported_when_source_index_is_empty(tmp_path: Path) -> None:
    run_dir = run_phase_2_fixture(tmp_path)
    source_index_path = run_dir / "knowledge" / "source_index.json"
    source_index = read_json(source_index_path)
    source_index["sources"] = []
    source_index["summary"]["total_sources"] = 0
    source_index["summary"]["fact_sources"] = 0
    source_index["summary"]["reference_sources"] = 0
    source_index_path.write_text(f"{json.dumps(source_index, ensure_ascii=False, indent=2)}\n", encoding="utf-8")

    evidence_run(run_dir)

    research_questions = read_json(run_dir / "plans" / "research_questions.json")
    evidence_map = read_json(run_dir / "plans" / "evidence_map.json")
    unresolved = (run_dir / "plans" / "unresolved_questions.md").read_text(encoding="utf-8")

    assert {question["status"] for question in research_questions["questions"]} == {"unsupported"}
    assert all(not question["evidence_candidates"] for question in evidence_map["questions"])
    assert "empty_source_index" in unresolved or "no_matching_source_evidence" in unresolved


def test_evidence_candidate_confidence_and_support_type_are_valid(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    for candidate in all_candidates(run_dir):
        assert 0 <= candidate["confidence"] <= 1
        assert candidate["support_type"] in ALLOWED_SUPPORT_TYPES


def test_evidence_candidate_snippet_comes_from_source_text(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    sources = source_by_id(run_dir)

    for candidate in all_candidates(run_dir):
        source_text = sources[candidate["source_id"]]["text"]
        assert candidate["snippet"]
        assert candidate["snippet"] in source_text


def test_evidence_run_does_not_create_forbidden_root_directories() -> None:
    for entry in FORBIDDEN_ROOT_ENTRIES:
        assert not (REPO_ROOT / entry).exists()
