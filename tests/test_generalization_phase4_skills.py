from pathlib import Path

from ai_writing_plugin.document_types.hara import HARA_RULES
from ai_writing_plugin.document_types.technical_solution import TECHNICAL_SOLUTION_RULES


ROOT = Path(__file__).resolve().parents[1]

SKILL_PATHS = {
    "writing_core": ROOT / "skills" / "writing-core" / "SKILL.md",
    "hara": ROOT / "skills" / "document-types" / "hara" / "SKILL.md",
    "technical_solution": ROOT / "skills" / "document-types" / "technical_solution" / "SKILL.md",
}


def read_skill(name: str) -> str:
    return SKILL_PATHS[name].read_text(encoding="utf-8").lower()


def assert_contains_all(text: str, terms: list[str]) -> None:
    missing = [term for term in terms if term.lower() not in text]
    assert not missing, f"Missing terms: {missing}"


def test_phase4_skill_files_exist() -> None:
    expected_paths = set(SKILL_PATHS.values())
    all_skill_paths = {path for path in (ROOT / "skills").rglob("SKILL.md")}
    assert expected_paths <= all_skill_paths


def test_writing_core_skill_describes_generic_workflow_and_entrypoints() -> None:
    text = read_skill("writing_core")

    assert_contains_all(
        text,
        [
            "/ai-writing-plugin:write",
            ".venv/bin/python -m ai_writing_plugin write-run",
            "examples/hara_demo_fixture/task.yaml",
            "examples/technical_solution_demo_fixture/task.yaml",
            "init run",
            "ingest",
            "source index",
            "template outline",
            "research questions",
            "evidence map",
            "citation plan",
            "section tasks",
            "draft",
            "review",
            "verify",
            "finalize",
            "trace",
            "learning",
        ],
    )


def test_writing_core_skill_covers_artifact_contract_and_material_roles() -> None:
    text = read_skill("writing_core")

    assert_contains_all(
        text,
        [
            "artifact contract",
            "python engine",
            "manifest",
            "task_brief",
            "input_inventory",
            "source_index",
            "knowledge_gaps",
            "outline",
            "evidence_map",
            "citation_plan",
            "section_tasks",
            "full_draft",
            "review_report",
            "verify_report",
            "final_report",
            "delivery_summary",
            "hitl_decisions",
            "candidate_profile_update",
            "candidate_skill_patch",
            "source",
            "template",
            "checklist",
            "sample",
            "reference",
            "fact source",
            "sample must not be used as a fact source",
            "reference must not be used as project-specific fact support",
        ],
    )


def test_writing_core_skill_preserves_engine_hitl_and_candidate_boundaries() -> None:
    text = read_skill("writing_core")

    assert_contains_all(
        text,
        [
            "must call python engine",
            "must not replace",
            "must use plugin workflow",
            "schema",
            "critical claim",
            "hitl",
            "needs_user_confirmation",
            "evidence",
            "candidate_profile_update",
            "candidate_skill_patch",
            "proposed",
            "inactive",
            "stable skill",
            "must not automatically",
            "prompt-only",
        ],
    )


def test_hara_skill_aligns_with_hara_rules_and_boundaries() -> None:
    text = read_skill("hara")

    assert_contains_all(text, ["hara", HARA_RULES.confirmation_marker, "final report is not approval"])
    assert_contains_all(text, list(HARA_RULES.critical_claims))
    assert_contains_all(text, ["final asil is approved", "risk is acceptable", "safety goal is approved"])
    assert_contains_all(
        text,
        [
            "document purpose and scope",
            "input materials and assumptions",
            "hazard identification",
            "hazardous event analysis",
            "s/e/c rating table",
            "asil candidate",
            "safety goals candidate",
            "sample",
            "reference",
            "must not be used as fact source",
            "must not prove project-specific facts",
        ],
    )


def test_technical_solution_skill_aligns_with_rules_and_boundaries() -> None:
    text = read_skill("technical_solution")

    assert_contains_all(text, ["technical_solution", "技术方案", TECHNICAL_SOLUTION_RULES.confirmation_marker])
    assert_contains_all(text, list(TECHNICAL_SOLUTION_RULES.critical_claims))
    assert_contains_all(text, list(TECHNICAL_SOLUTION_RULES.requires_human_confirmation))
    assert_contains_all(text, list(TECHNICAL_SOLUTION_RULES.forbidden_final_claims))
    assert_contains_all(
        text,
        [
            "system_context.md",
            "requirements.md",
            "solution_template.md",
            "checklist.md",
            "architecture_reference.md",
            "sample_solution.md",
            "background",
            "goals and non-goals",
            "architecture overview",
            "risks and trade-offs",
            "review focus",
            "ready_for_human_review",
            "not automatically approve",
            "must not be used as fact source",
            "must not prove project-specific",
        ],
    )
