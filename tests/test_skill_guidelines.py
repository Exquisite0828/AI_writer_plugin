from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_SKILLS = {
    "writing_core": ROOT / "skills" / "writing-core" / "SKILL.md",
    "hara": ROOT / "skills" / "document-types" / "hara" / "SKILL.md",
    "technical_solution": ROOT / "skills" / "document-types" / "technical_solution" / "SKILL.md",
    "test_report": ROOT / "skills" / "document-types" / "test_report" / "SKILL.md",
    "fsr": ROOT / "skills" / "document-types" / "fsr" / "SKILL.md",
    "generic_document": ROOT / "skills" / "document-types" / "generic_document" / "SKILL.md",
}


def read_skill(name: str) -> str:
    return REQUIRED_SKILLS[name].read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return " ".join(text.lower().replace("_", "_").split())


def assert_contains_all(text: str, terms: list[str]) -> None:
    lowered = normalized(text)
    missing = [term for term in terms if normalized(term) not in lowered]
    assert not missing, f"Missing terms: {missing}"


def test_required_skill_files_exist_and_are_not_empty() -> None:
    for name, path in REQUIRED_SKILLS.items():
        assert path.exists(), f"{name} skill is missing at {path}"
        text = path.read_text(encoding="utf-8")
        assert len(text) > 800, f"{name} skill looks too small"
        assert text.count("## ") >= 5, f"{name} skill lacks section structure"
        assert "todo" not in normalized(text), f"{name} skill still contains TODO wording"
        assert "placeholder" not in normalized(text), f"{name} skill looks placeholder-only"


def test_writing_core_skill_documents_engine_and_boundaries() -> None:
    text = read_skill("writing_core")

    assert_contains_all(
        text,
        [
            "python deterministic engine",
            "write-run",
            "/ai-writing-plugin:write",
            "artifact",
            "source index",
            "provenance",
            "source tier",
            "sample",
            "reference",
            "critical claim",
            "HITL",
            "NEEDS_USER_CONFIRMATION",
            "candidate_profile_update",
            "candidate_skill_patch",
            "profile-from-spec",
        ],
    )


def test_skill_docs_preserve_source_and_sample_boundaries() -> None:
    combined = "\n".join(read_skill(name) for name in REQUIRED_SKILLS)

    assert_contains_all(
        combined,
        [
            "sample is not a fact source",
            "sample is not fact source",
            "reference cannot prove project facts",
            "critical claim",
            "source or HITL",
            "final report is not approval",
            "candidate update",
            "proposed / inactive",
        ],
    )


def test_skill_docs_explain_n4_source_tiers() -> None:
    text = read_skill("writing_core")

    assert_contains_all(
        text,
        [
            "T0",
            "T1",
            "T2",
            "T3",
            "T4",
            "T5",
            "HITL",
            "project source",
            "template",
            "checklist",
            "reference",
            "sample",
            "generated / unknown",
            "T3/T4/T5 cannot support critical claim",
        ],
    )


def test_document_domain_skills_have_required_sections() -> None:
    required_terms = [
        "purpose",
        "inputs",
        "sections",
        "critical claims",
        "requires human confirmation",
        "forbidden final claims",
        "sample",
        "reference",
        "provenance",
        "review focus",
        "verification focus",
        "final report",
        "demo",
        "command",
    ]

    for name in ["hara", "technical_solution", "test_report", "fsr", "generic_document"]:
        text = read_skill(name)
        assert_contains_all(text, required_terms)
        assert_contains_all(text, [name])


def test_hara_skill_preserves_hara_boundaries() -> None:
    assert_contains_all(
        read_skill("hara"),
        [
            "HARA",
            "L3",
            "hazard identification",
            "hazardous event",
            "severity",
            "exposure",
            "controllability",
            "ASIL",
            "safety goal",
            "NEEDS_USER_CONFIRMATION",
            "risk is acceptable",
            "safety goal is approved",
            "final ASIL is approved",
        ],
    )


def test_technical_solution_skill_warns_against_hara_leakage() -> None:
    assert_contains_all(
        read_skill("technical_solution"),
        [
            "technical_solution",
            "L3",
            "architecture decision",
            "performance target",
            "security boundary",
            "cost estimate",
            "rollout risk acceptance",
            "HARA leakage",
            "ASIL",
            "S/E/C",
            "hazardous event",
            "safety goal",
        ],
    )


def test_test_report_skill_prevents_invented_results() -> None:
    assert_contains_all(
        read_skill("test_report"),
        [
            "test_report",
            "L3",
            "pass/fail",
            "coverage",
            "defect",
            "release readiness",
            "cannot be invented",
            "source or HITL",
            "sample",
            "reference",
        ],
    )


def test_fsr_skill_preserves_fsr_and_tsc_boundaries() -> None:
    assert_contains_all(
        read_skill("fsr"),
        [
            "fsr",
            "L3",
            "Functional Safety Requirements",
            "Safety Goals",
            "ASIL",
            "verification method",
            "requirement completeness",
            "TSC deferred",
            "NEEDS_USER_CONFIRMATION",
            "final report is not approval",
        ],
    )


def test_generic_document_skill_explains_l1_and_external_profile_boundary() -> None:
    assert_contains_all(
        read_skill("generic_document"),
        [
            "generic_document",
            "L1",
            "external profile",
            "document_profile.yaml",
            "Markdown Spec",
            "candidate profile",
            "profile-from-spec",
            "custom_technical_note",
            "not L3",
        ],
    )


def test_skill_docs_do_not_contain_unsafe_positive_instructions() -> None:
    combined = normalized("\n".join(read_skill(name) for name in REQUIRED_SKILLS))

    unsafe_positive_phrases = [
        "sample may be used as a fact source",
        "sample can prove project facts",
        "reference proves project facts",
        "final report is approved",
        "automatically apply candidate_skill_patch",
        "automatically promote profile",
        "create a pipeline per document type",
        "use langchain to run the workflow",
        "use vector db as the source of truth",
    ]

    present = [phrase for phrase in unsafe_positive_phrases if normalized(phrase) in combined]
    assert not present, f"Unsafe positive Skill instructions found: {present}"
