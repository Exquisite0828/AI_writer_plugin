from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FSR_SKILL = REPO_ROOT / "skills" / "document-types" / "fsr" / "SKILL.md"


def normalized(text: str) -> str:
    return " ".join(text.lower().split())


def assert_contains_all(text: str, terms: list[str]) -> None:
    lowered = normalized(text)
    missing = [term for term in terms if normalized(term) not in lowered]
    assert not missing, f"Missing terms: {missing}"


def test_fsr_skill_exists_and_has_guideline_structure() -> None:
    assert FSR_SKILL.exists()
    text = FSR_SKILL.read_text(encoding="utf-8")

    assert len(text) > 800
    assert text.count("## ") >= 5
    assert "todo" not in normalized(text)
    assert "placeholder" not in normalized(text)


def test_fsr_skill_documents_engine_boundaries_and_domain_rules() -> None:
    text = FSR_SKILL.read_text(encoding="utf-8")

    assert_contains_all(
        text,
        [
            "FSR",
            "Functional Safety Requirements",
            "L3",
            "HARA",
            "Safety Goals",
            "ASIL",
            "TSC deferred",
            "source tier",
            "provenance",
            "sample is not a fact source",
            "reference cannot prove project facts",
            "critical claim",
            "requires human confirmation",
            "NEEDS_USER_CONFIRMATION",
            "forbidden final claims",
            "final report is not approval",
            "candidate update",
            "proposed / inactive",
            "Python deterministic engine",
            "write-run",
            "not prompt-only",
        ],
    )


def test_fsr_skill_warns_against_tsc_promotion_and_special_pipeline() -> None:
    text = FSR_SKILL.read_text(encoding="utf-8")

    assert_contains_all(
        text,
        [
            "do not create a TSC document",
            "do not create technical safety requirements",
            "do not create an FSR-specific pipeline",
            "one plugin, one pipeline",
            "no automatic professional approval",
            "no RAG",
            "no LangChain",
            "no vector DB",
        ],
    )


def test_fsr_skill_does_not_contain_unsafe_positive_instructions() -> None:
    text = normalized(FSR_SKILL.read_text(encoding="utf-8"))
    unsafe_positive_phrases = [
        "sample may be used as a fact source",
        "sample can prove project facts",
        "reference proves project facts",
        "final report is approved",
        "automatically promote profile",
        "create a pipeline per document type",
        "use langchain to run the workflow",
        "use vector db as the source of truth",
    ]

    for phrase in unsafe_positive_phrases:
        assert phrase not in text
