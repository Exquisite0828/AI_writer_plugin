import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_TASK = REPO_ROOT / "examples" / "hara_minimal_fixture" / "task.yaml"

PHASE_4_ARTIFACTS = {
    "plans/citation_plan.json",
    "plans/claim_support_matrix.json",
    "plans/outline_final.md",
    "plans/section_tasks.json",
    "plans/writing_plan.md",
}

PREVIOUS_ARTIFACTS = {
    "manifest.json",
    "task_brief.json",
    "inputs/input_inventory.json",
    "knowledge/source_index.json",
    "knowledge/provenance_index.json",
    "knowledge/knowledge_gaps.md",
    "plans/template_structure.json",
    "plans/outline_l1.md",
    "plans/research_questions.json",
    "plans/evidence_map.json",
    "plans/unresolved_questions.md",
}

LATER_PHASE_PATHS = [
    "draft",
    "draft/full_draft.md",
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

ALLOWED_SECTION_STATUSES = {"supported", "mixed", "weak", "unsupported"}
ALLOWED_SLOT_STATUSES = {"filled", "weak", "unsupported", "requires_human_confirmation"}
ALLOWED_UNSUPPORTED_REASONS = {
    "no_evidence",
    "weak_evidence",
    "requires_human_confirmation",
    "methodology_only",
    "missing_material",
}
ALLOWED_EVIDENCE_USAGES = {
    "fact_support",
    "methodology_support",
    "context_support",
    "weak_support",
    "human_confirmation_context",
}
ALLOWED_TASK_TYPES = {"prose", "table", "issue_list", "summary"}
ALLOWED_WRITING_MODES = {
    "evidence_grounded_summary",
    "conservative_candidate",
    "confirmation_required",
    "unsupported_stub",
    "open_issue_list",
}
SENSITIVE_TITLE_MARKERS = ("hazard", "hazardous", "rating", "s/e/c", "asil", "risk", "safety goal")
FORBIDDEN_SOURCES = {"sample", "expected_output_shape", "template", "checklist"}


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
    import ai_writing_plugin.run_manager as run_manager

    runner = getattr(run_manager, "plan_run", None)
    assert runner is not None, "plan_run is not implemented"
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
    return plan_run(run_dir)


def citation_plan(run_dir: Path) -> dict:
    return read_json(run_dir / "plans" / "citation_plan.json")


def section_tasks(run_dir: Path) -> dict:
    return read_json(run_dir / "plans" / "section_tasks.json")


def citation_sections_by_id(run_dir: Path) -> dict[str, dict]:
    return {section["section_id"]: section for section in citation_plan(run_dir)["sections"]}


def tasks_by_section_id(run_dir: Path) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for task in section_tasks(run_dir)["tasks"]:
        grouped.setdefault(task["section_id"], []).append(task)
    return grouped


def evidence_candidates_by_id(run_dir: Path) -> dict[str, dict]:
    evidence_map = read_json(run_dir / "plans" / "evidence_map.json")
    candidates: dict[str, dict] = {}
    for question in evidence_map["questions"]:
        for candidate in question["evidence_candidates"]:
            candidates[candidate["evidence_id"]] = candidate
    return candidates


def source_by_id(run_dir: Path) -> dict[str, dict]:
    source_index = read_json(run_dir / "knowledge" / "source_index.json")
    return {source["source_id"]: source for source in source_index["sources"]}


def research_question_ids(run_dir: Path) -> set[str]:
    research_questions = read_json(run_dir / "plans" / "research_questions.json")
    return {question["question_id"] for question in research_questions["questions"]}


def evidence_questions_by_id(run_dir: Path) -> dict[str, dict]:
    evidence_map = read_json(run_dir / "plans" / "evidence_map.json")
    return {question["question_id"]: question for question in evidence_map["questions"]}


def all_evidence_details(run_dir: Path) -> list[dict]:
    return [detail for section in citation_plan(run_dir)["sections"] for detail in section["evidence_details"]]


def all_citation_slots(run_dir: Path) -> list[dict]:
    return [slot for section in citation_plan(run_dir)["sections"] for slot in section["citation_slots"]]


def all_unsupported_claims(run_dir: Path) -> list[dict]:
    return [claim for section in citation_plan(run_dir)["sections"] for claim in section["unsupported_claims"]]


def all_weak_notes(run_dir: Path) -> list[dict]:
    return [note for section in citation_plan(run_dir)["sections"] for note in section["weak_evidence_notes"]]


def test_plan_run_creates_phase_4_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    assert (run_dir / "plans" / "citation_plan.json").exists()
    assert (run_dir / "plans" / "outline_final.md").exists()
    assert (run_dir / "plans" / "section_tasks.json").exists()
    assert (run_dir / "plans" / "writing_plan.md").exists()


def test_plan_run_updates_manifest_to_phase_4(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    manifest = read_json(run_dir / "manifest.json")
    artifact_paths = [artifact["path"] for artifact in manifest["artifacts"]]

    assert manifest["phase"] == "phase_4"
    assert manifest["status"] == "writing_planned"
    assert PREVIOUS_ARTIFACTS <= set(artifact_paths)
    assert PHASE_4_ARTIFACTS <= set(artifact_paths)
    assert len(artifact_paths) == len(set(artifact_paths))


def test_citation_plan_covers_all_outline_sections(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    template_structure = read_json(run_dir / "plans" / "template_structure.json")
    outline_section_ids = {section["section_id"] for section in template_structure["outline_sections"]}
    citation_section_ids = {section["section_id"] for section in citation_plan(run_dir)["sections"]}

    assert outline_section_ids == citation_section_ids


def test_citation_plan_section_schema_fields_are_complete(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    required_fields = {
        "section_id",
        "section_title",
        "order",
        "question_ids",
        "allowed_evidence",
        "evidence_details",
        "citation_slots",
        "unsupported_claims",
        "weak_evidence_notes",
        "requires_human_confirmation",
        "evidence_status",
        "unresolved_question_ids",
        "notes",
    }

    for section in citation_plan(run_dir)["sections"]:
        assert set(section) == required_fields
        assert section["section_id"]
        assert section["section_title"]
        assert section["evidence_status"] in ALLOWED_SECTION_STATUSES
        assert isinstance(section["allowed_evidence"], list)
        assert isinstance(section["citation_slots"], list)
        assert isinstance(section["unsupported_claims"], list)


def test_allowed_evidence_ids_come_from_evidence_map(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    candidate_ids = set(evidence_candidates_by_id(run_dir))

    for section in citation_plan(run_dir)["sections"]:
        assert set(section["allowed_evidence"]) <= candidate_ids


def test_citation_evidence_details_trace_to_evidence_map_and_source_index(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    candidates = evidence_candidates_by_id(run_dir)
    sources = source_by_id(run_dir)

    for detail in all_evidence_details(run_dir):
        candidate = candidates[detail["evidence_id"]]
        source = sources[detail["source_id"]]
        assert detail["source_id"] == candidate["source_id"]
        assert detail["file_id"] == source["file_id"]
        assert detail["source_role"] == source["source_role"]
        assert detail["is_fact_source"] == source["is_fact_source"]
        assert detail["source_tier"] == source["source_tier"]
        assert "provenance_support_type" in detail
        assert "human_confirmation_status" in detail


def test_sample_and_expected_output_shape_are_not_in_citation_plan(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    inventory = read_json(run_dir / "inputs" / "input_inventory.json")
    forbidden_file_ids = {
        file["file_id"] for file in inventory["files"] if file["role"] in {"sample", "expected_output_shape"}
    }

    for detail in all_evidence_details(run_dir):
        assert detail["file_id"] not in forbidden_file_ids
        assert detail["source_role"] not in {"sample", "expected_output_shape"}


def test_reference_evidence_is_not_fact_support(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    for detail in all_evidence_details(run_dir):
        if detail["source_role"] == "reference":
            assert detail["is_fact_source"] is False
            assert detail["usage"] in {
                "methodology_support",
                "context_support",
                "weak_support",
                "human_confirmation_context",
            }
            assert detail["usage"] != "fact_support"


def test_citation_slots_cover_research_questions(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    slot_question_ids = {slot["question_id"] for slot in all_citation_slots(run_dir)}

    assert research_question_ids(run_dir) <= slot_question_ids
    assert slot_question_ids <= research_question_ids(run_dir)


def test_citation_slot_status_and_human_confirmation_propagation(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    evidence_questions = evidence_questions_by_id(run_dir)

    for slot in all_citation_slots(run_dir):
        assert slot["status"] in ALLOWED_SLOT_STATUSES
        if evidence_questions[slot["question_id"]]["requires_human_confirmation"]:
            assert slot["status"] == "requires_human_confirmation"


def test_unsupported_questions_generate_unsupported_claims(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    unsupported_question_ids = {
        question["question_id"]
        for question in evidence_questions_by_id(run_dir).values()
        if question["status"] == "unsupported"
    }
    unsupported_claims = all_unsupported_claims(run_dir)

    assert unsupported_question_ids
    assert unsupported_question_ids <= {claim["question_id"] for claim in unsupported_claims}
    for claim in unsupported_claims:
        assert claim["reason"] in ALLOWED_UNSUPPORTED_REASONS


def test_weak_questions_generate_weak_evidence_notes(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    weak_question_ids = {
        question["question_id"] for question in evidence_questions_by_id(run_dir).values() if question["status"] == "weak"
    }
    weak_note_question_ids = {note["question_id"] for note in all_weak_notes(run_dir)}
    weak_slot_question_ids = {slot["question_id"] for slot in all_citation_slots(run_dir) if slot["status"] == "weak"}

    assert weak_question_ids
    assert weak_question_ids <= weak_note_question_ids | weak_slot_question_ids


def test_hara_sensitive_sections_create_confirmation_required_tasks(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    citation_sections = citation_sections_by_id(run_dir)
    tasks_by_section = tasks_by_section_id(run_dir)
    sensitive_sections = [
        section
        for section in citation_sections.values()
        if any(marker in section["section_title"].lower() for marker in SENSITIVE_TITLE_MARKERS)
    ]

    assert {"Hazard Identification", "Hazardous Event Analysis", "S/E/C Rating Table", "Safety Goals Candidate"} <= {
        section["section_title"] for section in sensitive_sections
    }
    for section in sensitive_sections:
        assert section["requires_human_confirmation"] is True
        for task in tasks_by_section[section["section_id"]]:
            assert task["requires_human_confirmation"] is True
            assert "NEEDS_USER_CONFIRMATION" in task["confirmation_markers"]
            assert any(
                phrase in task["must_not_include"]
                for phrase in ["final professional conclusion", "unconfirmed ASIL or risk conclusion"]
            )


def test_section_tasks_cover_all_citation_plan_sections(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    citation_section_ids = set(citation_sections_by_id(run_dir))
    task_section_ids = set(tasks_by_section_id(run_dir))

    assert citation_section_ids == task_section_ids


def test_section_task_schema_fields_are_complete(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    required_fields = {
        "task_id",
        "section_id",
        "section_title",
        "order",
        "task_title",
        "task_type",
        "writing_goal",
        "writing_mode",
        "allowed_evidence",
        "required_citation_slots",
        "evidence_status",
        "requires_human_confirmation",
        "unresolved_question_ids",
        "forbidden_sources",
        "word_limit",
        "must_include",
        "must_not_include",
        "confirmation_markers",
        "future_output_path",
        "source_support_requirements",
        "source_support",
        "provenance_summary",
        "notes",
    }

    for task in section_tasks(run_dir)["tasks"]:
        assert set(task) == required_fields
        assert task["task_id"]
        assert task["section_id"]
        assert task["task_type"] in ALLOWED_TASK_TYPES
        assert task["writing_mode"] in ALLOWED_WRITING_MODES
        assert 200 <= task["word_limit"] <= 500
        assert "claim_status" in task["provenance_summary"]


def test_section_tasks_forbid_non_fact_sources(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    for task in section_tasks(run_dir)["tasks"]:
        assert FORBIDDEN_SOURCES <= set(task["forbidden_sources"])


def test_section_task_allowed_evidence_matches_citation_plan(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    citation_sections = citation_sections_by_id(run_dir)

    for task in section_tasks(run_dir)["tasks"]:
        citation_section = citation_sections[task["section_id"]]
        section_slot_ids = {slot["slot_id"] for slot in citation_section["citation_slots"]}
        assert set(task["allowed_evidence"]) <= set(citation_section["allowed_evidence"])
        assert set(task["required_citation_slots"]) <= section_slot_ids


def test_outline_final_is_plan_not_draft(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    outline_final = (run_dir / "plans" / "outline_final.md").read_text(encoding="utf-8")

    assert "# 最终写作大纲" in outline_final
    assert "Run id:" in outline_final
    assert "最终写作大纲" in outline_final
    assert "阶段边界说明" in outline_final
    assert "TASK-001" in outline_final
    assert "草稿生成推迟到 Phase 5" in outline_final
    assert "## Draft" not in outline_final


def test_writing_plan_contains_order_and_boundary_notes(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)
    writing_plan = (run_dir / "plans" / "writing_plan.md").read_text(encoding="utf-8")

    assert "# 写作计划" in writing_plan
    assert "写作顺序" in writing_plan
    assert "TASK-001" in writing_plan
    assert "Phase 5 引用规则" in writing_plan
    assert "Phase 4 不生成草稿文件" in writing_plan
    assert "草稿生成从 Phase 5 开始" in writing_plan


def test_plan_run_does_not_generate_later_phase_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_4_fixture(tmp_path)

    for relative_path in LATER_PHASE_PATHS:
        assert not (run_dir / relative_path).exists()


def test_plan_run_requires_phase_3_run(tmp_path: Path) -> None:
    run_dir = ingest_run(FIXTURE_TASK, tmp_path / "runs")
    outline_run(run_dir)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "plan-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "plan-run requires an evidence-mapped Phase 3 run" in result.stderr
    for relative_path in PHASE_4_ARTIFACTS:
        assert not (run_dir / relative_path).exists()


def test_repeated_plan_run_does_not_duplicate_manifest_artifacts(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    plan_run(run_dir)
    plan_run(run_dir)

    artifact_paths = [artifact["path"] for artifact in read_json(run_dir / "manifest.json")["artifacts"]]
    for artifact_path in PHASE_4_ARTIFACTS:
        assert artifact_paths.count(artifact_path) == 1


def test_plan_run_cli_success(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "plan-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "写作计划已完成" in result.stdout
    assert "plans/citation_plan.json" in result.stdout
    assert "plans/outline_final.md" in result.stdout
    assert "plans/section_tasks.json" in result.stdout
    assert "plans/writing_plan.md" in result.stdout


def test_plan_run_creates_conservative_plan_when_evidence_map_has_no_candidates(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    evidence_map_path = run_dir / "plans" / "evidence_map.json"
    evidence_map = read_json(evidence_map_path)
    for question in evidence_map["questions"]:
        question["evidence_candidates"] = []
        question["status"] = "unsupported"
        question["unresolved_reason"] = "no_matching_source_evidence"
    write_json(evidence_map_path, evidence_map)

    plan_run(run_dir)

    citation_statuses = {section["evidence_status"] for section in citation_plan(run_dir)["sections"]}
    writing_modes = {task["writing_mode"] for task in section_tasks(run_dir)["tasks"]}

    assert citation_statuses <= {"unsupported", "weak", "mixed"}
    assert writing_modes <= {"unsupported_stub", "conservative_candidate", "confirmation_required", "open_issue_list"}
    assert all(not section["allowed_evidence"] for section in citation_plan(run_dir)["sections"])


def test_plan_run_fails_when_source_index_missing(tmp_path: Path) -> None:
    run_dir = run_phase_3_fixture(tmp_path)
    (run_dir / "knowledge" / "source_index.json").unlink()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_writing_plugin",
            "plan-run",
            "--run",
            str(run_dir),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "source_index is required for citation traceability" in result.stderr
    for relative_path in PHASE_4_ARTIFACTS:
        assert not (run_dir / relative_path).exists()


def test_plan_run_does_not_create_forbidden_root_directories() -> None:
    for entry in FORBIDDEN_ROOT_ENTRIES:
        assert not (REPO_ROOT / entry).exists()
